# indexer.py
import json
import re
from bs4 import BeautifulSoup
from bs4.element import NavigableString  

from api import OpenAIClient, DeepSeekClient
from item_chunk import Chunk
from all_speakers import AllSpeakers


class SpeechIndexer:
    def __init__(self, api_client="openai"):
        match api_client:
            case "openai":
                self.api_client = OpenAIClient()
            case "deepseek":
                self.api_client = DeepSeekClient()
            case _:
                raise ValueError("Invalid API client specified.")

        # base prompt
        self.base_message = {
            "role": "system",
            "content": (
                "You are a helpful assistant for detecting the speakers of direct speech and internal thoughts. "
                "Your task is to identify who is speaking or thinking based on the context. "
                "Always respond with a clear, simple JSON object containing only speaker names."
            ),
        }

        # initializes the messages array with the base prompt
        self.messages = [self.base_message]
        self.blocks: list[list[dict]] = []

    # --------------------------------------------------------------------- #
    # -------------------------- public interface ------------------------- #
    # --------------------------------------------------------------------- #
    def process_chunk(self, chunk: Chunk) -> Chunk:
        """
        Tags speech (<speech>) and thoughts (<em>) within the chunk,
        retrieves speaker names via LLM and replaces the index attributes
        by speaker attributes.
        """
        current_block: list[dict] = []
        # ----------------------------------------------------------------- #
        # 0. prescan for obvious speaker names
        chunk_content = chunk.get_content()
        try:
            prescan_summary = self.api_client.prescan(chunk_content)
        except Exception as err:
            prescan_summary = "n/a"
            print(f"[Prescan] {err}")

        prescan_msg = {
            "role": "assistant",
            "content": f"Occurring speakers in the text: {prescan_summary}",
        }
        self.messages.append(prescan_msg)
        current_block.append(prescan_msg)
        # ----------------------------------------------------------------- #
        # 1. tag speech & thoughts
        tagged_chunk = self._find_and_tag_speech_and_thoughts(chunk)

        # (EARLY RETURN – for debugging only)
        # return tagged_chunk

        # ----------------------------------------------------------------- #
        # 2. ask the model for speakers
        tagged_text = tagged_chunk.get_content()
        speech_indexes = self._extract_indexes(tagged_text, "speech")
        thought_indexes = self._extract_indexes(tagged_text, "em")

        user_msg = {
            "role": "user",
            "content": (
                f"Text for speaker detection:\n{tagged_text}\n\n"
                f"Please identify the speaker for each of the following numbered segments:\n"
                f"Speech segments: {', '.join(map(str, speech_indexes))}\n"
                f"Thought segments: {', '.join(map(str, thought_indexes))}\n"
                "Return only a JSON object with speaker names for each index."
            ),
        }

        self.messages.append(user_msg)
        current_block.append(user_msg)

        # ----------------------------------------------------------------- #
        # 3. parse model response
        speakers_response = self.api_client.get_speakers(self.messages)
        try:
            cleaned_response = self._extract_json(speakers_response)
            speakers_dict = json.loads(cleaned_response)

            # ensure both keys exist
            speakers_dict.setdefault("speech", {})
            speakers_dict.setdefault("thought", {})

            self._validate_speaker_names(speakers_dict)
            AllSpeakers.enrich_speaker_set(speakers_dict["speech"].values())
            AllSpeakers.enrich_speaker_set(speakers_dict["thought"].values())

            processed_chunk = self._replace_all_indexes(
                tagged_chunk, speakers_dict, speech_indexes, thought_indexes
            )

            # ----------------------------------------------------------------- #
            # 4. summarise context for next chunk
            summary = self.api_client.summarize_context(processed_chunk.get_content())
            assistant_msg = {
                "role": "assistant",
                "content": f"Context-Summary: {summary}",
            }
            self.messages.append(assistant_msg)
            current_block.append(assistant_msg)

            # update rolling context
            self.blocks.append(current_block)
            self._update_messages()

            return processed_chunk

        except json.JSONDecodeError as exc:
            print(f"[SpeechIndexer] JSON decode error: {exc}")
            print(f"Model raw response:\n{speakers_response}\n")
            print(f"After attempted extract:\n{self._extract_json(speakers_response)}\n")

            # still keep conversation context
            self.blocks.append(current_block)
            self._update_messages()
            return tagged_chunk

    # --------------------------------------------------------------------- #
    # ---------------- tagging speech & thoughts -------------------------- #
    # --------------------------------------------------------------------- #
    def _find_and_tag_speech_and_thoughts(self, chunk: Chunk) -> Chunk:
        soup = BeautifulSoup(chunk.get_content(), "html.parser")

        # 1) tag thoughts first
        soup = self._tag_thoughts_in_html(soup)

        # 2) tag speech
        soup = self._tag_speech_across_text_nodes(soup)

        chunk.set_content(str(soup))
        return chunk

    # ---------------- thoughts ---------------- #
    def _tag_thoughts_in_html(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Adds a running index attribute to each <em>…</em> (thought)."""
        thought_pattern = r"<em>([^<]+)</em>"

        def thought_repl(match, counter=iter(range(1, 10_000))):
            return f'<em index="{next(counter)}">{match.group(1)}</em>'

        modified_html = re.sub(thought_pattern, thought_repl, str(soup))
        return BeautifulSoup(modified_html, "html.parser")

    # ---------------- speech ---------------- #
    def _tag_speech_across_text_nodes(self, soup: BeautifulSoup) -> BeautifulSoup:
        """
        Detects quoted speech that may span several adjacent siblings
        (including inline tags) and wraps it in <speech index="…">…</speech>.
        Already tagged speech is skipped, preventing endless loops.
        """
        speech_index = 1
        text_nodes = self._get_visible_text_nodes(soup)
        i = 0

        while i < len(text_nodes):
            node = text_nodes[i]

            # node might have been removed/changed
            if node.parent is None:
                text_nodes = self._get_visible_text_nodes(soup)
                continue

            text = str(node)
            open_pos = self._find_opening_quote(text)
            if open_pos is None:
                i += 1
                continue

            # closing quote in same node?
            if self._find_closing_quote(text[open_pos + 1 :]) is not None:
                new_html, speech_index = self._replace_speech_in_text(text, speech_index)
                node.replace_with(BeautifulSoup(new_html, "html.parser"))

                # refresh list, continue after current index
                text_nodes = self._get_visible_text_nodes(soup)
                continue

            # speech spans multiple nodes
            combined, nodes_to_replace, closing_found = self._collect_until_closing_quote(
                node, open_pos
            )
            if not closing_found:
                i += 1
                continue

            new_html, speech_index = self._replace_speech_in_text(combined, speech_index)
            fragment = BeautifulSoup(new_html, "html.parser")
            nodes_to_replace[0].replace_with(fragment)
            for n in nodes_to_replace[1:]:
                n.extract()

            # refresh list, resume scanning
            text_nodes = self._get_visible_text_nodes(soup)
            continue

        return soup

    # ---------------- helpers for speech ---------------- #
    @staticmethod
    def _find_opening_quote(text: str) -> int | None:
        m = re.search(r'[„“"‚‘»«›‹]', text)
        return m.start() if m else None

    @staticmethod
    def _find_closing_quote(text: str) -> int | None:
        m = re.search(r'[“"‘’»«›‹]', text)
        return m.start() if m else None

    def _collect_until_closing_quote(
        self, start_node: NavigableString, open_pos: int
    ) -> tuple[str, list, bool]:
        """Collects siblings until a closing quote is found."""
        combined = str(start_node)
        nodes_to_replace = [start_node]
        closing_found = False

        # check remainder of start node first
        if self._find_closing_quote(combined[open_pos + 1 :]) is not None:
            return combined, nodes_to_replace, True

        node = start_node.next_sibling
        while node:
            combined += str(node)
            nodes_to_replace.append(node)
            if self._find_closing_quote(str(node)):
                closing_found = True
                break
            node = node.next_sibling

        return combined, nodes_to_replace, closing_found

    def _replace_speech_in_text(self, text: str, speech_index: int) -> tuple[str, int]:
        """
        Wraps any quoted segment – even with inline HTML – in a
        <speech index="…">…</speech> tag. Empty/whitespace-only segments
        are ignored.
        """
        speech_pattern = re.compile(
            r'([„“"‚‘»«›‹])([\s\S]*?)([“"‘’»«›‹])',  # allow anything between quotes
            re.DOTALL | re.MULTILINE,
        )

        def repl(m: re.Match) -> str:
            nonlocal speech_index
            inner_plain = re.sub(r"<[^>]+>", "", m.group(2)).strip()
            if not inner_plain:
                return m.group(0)  # skip empty quotes
            wrapped = (
                f'<speech index="{speech_index}">'
                f'{m.group(1)}{m.group(2)}{m.group(3)}</speech>'
            )
            speech_index += 1
            return wrapped

        new_text = speech_pattern.sub(repl, text)
        return new_text, speech_index
    
    def _update_messages(self) -> None:
        """Keep only the last 5 blocks for the next API call."""
        recent_blocks = self.blocks[-5:]
        # base_message always first, then flatten the last blocks
        self.messages = [self.base_message] + [
            msg for block in recent_blocks for msg in block
        ]

    # ---------------- utilities ---------------- #
    def _get_visible_text_nodes(self, soup: BeautifulSoup) -> list:
        """
        Returns all visible text nodes that are not inside <script>/<style>
        and not already wrapped in a <speech> tag.
        """
        return [
            n
            for n in soup.find_all(string=True)
            if n.parent.name not in {"script", "style"}
            and n.strip()
            and n.find_parent("speech") is None
        ]

    # ---------------- JSON & speaker replacement ---------------- #
    def _extract_json(self, response: str) -> str:
        start = response.find("{")
        end = response.rfind("}")
        if start != -1 and end != -1 and end > start:
            return response[start : end + 1]
        return '{"speech": {}, "thought": {}}'

    def _validate_speaker_names(self, speakers_dict: dict) -> None:
        """
        • converts index strings to int
        • strips markup/whitespace from speaker names
        • ensures empty names become "Unknown"
        """
        for category in ("speech", "thought"):
            cleaned = {}
            for idx, name in speakers_dict[category].items():
                numeric_idx = int(idx) if isinstance(idx, str) and idx.isdigit() else idx
                if isinstance(name, str):
                    name = re.sub(r'index=["\']\d+["\']', "", name)
                    name = re.sub(r"<[^>]+>", "", name).strip('"\t\n ').strip()
                if not name:
                    name = "Unknown"
                cleaned[numeric_idx] = name
            speakers_dict[category] = cleaned

    def _replace_all_indexes(
        self, chunk: Chunk, speakers_dict, speech_indexes, thought_indexes
    ) -> Chunk:
        text = chunk.get_content()
        for idx in speech_indexes:
            speaker = speakers_dict["speech"].get(idx, "Unknown")
            text = text.replace(f'<speech index="{idx}">', f'<speech speaker="{speaker}">')
        for idx in thought_indexes:
            speaker = speakers_dict["thought"].get(idx, "Unknown")
            text = text.replace(f'<em index="{idx}">', f'<em speaker="{speaker}">')
        chunk.set_content(text)
        return chunk

    # ---------------- misc ---------------- #
    def _extract_indexes(self, text: str, tag_type: str) -> list[int]:
        pattern = fr'<{tag_type} index="(\d+)">'
        return [int(m.group(1)) for m in re.finditer(pattern, text)]
