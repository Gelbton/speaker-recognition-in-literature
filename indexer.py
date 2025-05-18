import json
import re

from bs4 import BeautifulSoup
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
            )
        }
        # initializes the messages array with the base prompt
        self.messages = [self.base_message]
        self.blocks = []

    def _update_messages(self):
        recent_blocks = self.blocks[-5:] # only the last 5 messages get resend in the messages object of the api
        self.messages = [self.base_message] + [msg for block in recent_blocks for msg in block]

    # processes the text by first prescanning it, then tagging speech and thoughts, and finally assigning speakers
    def process_chunk(self, chunk: Chunk) -> Chunk:
        current_block = []
        chunk_content = chunk.get_content()

        # prescan the current chunk
        prescan_summary = self.api_client.prescan(chunk_content)
        new_msg = {"role": "assistant", "content": f"Occurring speakers in the text: {prescan_summary}"}
        self.messages.append(new_msg)
        current_block.append(new_msg)

        # tag speech and thoughts
        tagged_chunk = self._find_and_tag_speech_and_thoughts(chunk)
        tagged_text = tagged_chunk.get_content()
        
        speech_indexes = self._extract_indexes(tagged_text, 'speech')
        thought_indexes = self._extract_indexes(tagged_text, 'em')
        
        new_msg = {"role": "user", "content": (
            f"Text for speaker detection:\n{tagged_text}\n\n"
            f"Please identify the speaker for each of the following numbered segments:\n"
            f"Speech segments: {', '.join([str(idx) for idx in speech_indexes])}\n"
            f"Thought segments: {', '.join([str(idx) for idx in thought_indexes])}\n"
            "Return only a JSON object with speaker names for each index."
        )}
        self.messages.append(new_msg)
        current_block.append(new_msg)

        # get the speakers from the API response
        speakers_response = self.api_client.get_speakers(self.messages)
        try:
            cleaned_response = self._extract_json(speakers_response)
            speakers_dict = json.loads(cleaned_response)
            
            speakers_dict.setdefault("speech", {})
            speakers_dict.setdefault("thought", {})
            
            self._validate_speaker_names(speakers_dict)
            
            AllSpeakers.enrich_speaker_set(speakers_dict["speech"].values())
            AllSpeakers.enrich_speaker_set(speakers_dict["thought"].values())
            
            processed_chunk = self._replace_all_indexes(tagged_chunk, speakers_dict, speech_indexes, thought_indexes)
            processed_chunk_text = processed_chunk.get_content()
            
            # summarize the context for the next chunk
            summary = self.api_client.summarize_context(processed_chunk_text)
            new_msg = {"role": "assistant", "content": f"Context-Summary: {summary}"}
            self.messages.append(new_msg)
            current_block.append(new_msg)
            
            self.blocks.append(current_block)
            self._update_messages()
            return processed_chunk

        except json.JSONDecodeError as e:
            print(f"Could not parse the API answer: {str(e)}")
            print(f"Original response: {speakers_response}")
            print(f"Cleaned response: {self._extract_json(speakers_response)}")
            self.blocks.append(current_block)
            self._update_messages()
            return tagged_chunk

    def _extract_indexes(self, text, tag_type):
        pattern = fr'<{tag_type} index="(\d+)">'
        return [int(match.group(1)) for match in re.finditer(pattern, text)]


    def _find_and_tag_speech_and_thoughts(self, chunk):
        chunk_content = chunk.get_content()
        soup = BeautifulSoup(chunk_content, "html.parser")

        # Tag thoughts first
        soup = self._tag_thoughts_in_html(soup)

        # Tag speech across text nodes
        soup = self._tag_speech_across_text_nodes(soup)

        chunk.set_content(str(soup))
        return chunk

    def _tag_thoughts_in_html(self, soup):
        """
        Tags <em>thoughts</em> with an incremental index attribute.
        """
        thought_pattern = r'<em>([^<]+)</em>'
        def thought_repl(m, c=iter(range(1, 10000))):
            return f'<em index="{next(c)}">{m.group(1)}</em>'
        # Apply replacement on the string representation, then re-parse
        modified_html = re.sub(thought_pattern, thought_repl, str(soup))
        return BeautifulSoup(modified_html, "html.parser")

    def _get_visible_text_nodes(self, soup):
        """
        Returns all visible text nodes (excluding script/style and whitespace).
        """
        return [
            node for node in soup.find_all(string=True)
            if node.parent.name not in ['script', 'style'] and node.strip()
        ]

    def _tag_speech_across_text_nodes(self, soup):
        """
        Tags speech segments that may span across multiple text nodes.
        """
        speech_pattern = r'([„“"‚‘»«›‹])([^„“"‚‘»«›‹]+?)([“"‘’»«›‹])'
        text_nodes = self._get_visible_text_nodes(soup)
        speech_index = 1
        i = 0

        while i < len(text_nodes):
            node = text_nodes[i]
            text = str(node)
            open_pos = self._find_opening_quote(text)
            if open_pos is not None:
                # Check for closing quote after opening
                after_open = text[open_pos+1:]
                close_pos = self._find_closing_quote(after_open)
                if close_pos is not None:
                    # Opening and closing in same node
                    new_text, speech_index = self._replace_speech_in_text(
                        text, speech_pattern, speech_index
                    )
                    node.replace_with(new_text)
                    i += 1
                else:
                    # Speech spans multiple nodes
                    combined, nodes_to_replace, j, closing_found = self._gather_until_closing_quote(
                        text_nodes, i, open_pos
                    )
                    if closing_found:
                        new_combined, speech_index = self._replace_speech_in_text(
                            combined, speech_pattern, speech_index
                        )
                        nodes_to_replace[0].replace_with(new_combined)
                        for n in nodes_to_replace[1:]:
                            n.extract()
                        i = j + 1
                    else:
                        i += 1
            else:
                i += 1
        return soup

    def _find_opening_quote(self, text):
        """
        Returns the position of the first opening quote or None.
        """
        match = re.search(r'[„“"‚‘»«›‹]', text)
        return match.start() if match else None

    def _find_closing_quote(self, text):
        """
        Returns the position of the first closing quote or None.
        """
        match = re.search(r'[“"‘’»«›‹]', text)
        return match.start() if match else None

    def _gather_until_closing_quote(self, text_nodes, start_idx, open_pos):
        """
        Gathers text nodes from start_idx onwards until a closing quote is found.
        Returns the combined text, the involved nodes, the index of the last node, and a flag.
        """
        combined = str(text_nodes[start_idx])
        nodes_to_replace = [text_nodes[start_idx]]
        j = start_idx + 1
        closing_found = False
        while j < len(text_nodes):
            next_text = str(text_nodes[j])
            if self._find_closing_quote(next_text) is not None:
                closing_found = True
                combined += next_text
                nodes_to_replace.append(text_nodes[j])
                break
            else:
                combined += next_text
                nodes_to_replace.append(text_nodes[j])
            j += 1
        return combined, nodes_to_replace, j, closing_found

    def _replace_speech_in_text(self, text, speech_pattern, speech_index):
        """
        Replaces speech in the given text with <speech> tags, incrementing the index.
        Returns a BeautifulSoup fragment (not a string!).
        """
        def repl(m):
            nonlocal speech_index
            tag = f'<speech index="{speech_index}">{m.group(1)}{m.group(2)}{m.group(3)}</speech>'
            speech_index += 1
            return tag

        new_text = re.sub(speech_pattern, repl, text)
        # Parse the result as HTML fragment
        fragment = BeautifulSoup(new_text, "html.parser")
        return fragment, speech_index


    def _extract_json(self, response: str) -> str:
        # extract first JSON object from API response
        start_idx = response.find('{')
        end_idx = response.rfind('}')
        
        # return cleaned JSON if valid boundaries found
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            return response[start_idx:end_idx+1]
        
        # fallback for invalid responses
        return '{"speech":{}, "thought":{}}'

    def _validate_speaker_names(self, speakers_dict: dict) -> None:
        # clean speaker names and convert string indexes to integers
        for category in ["speech", "thought"]:
            for idx in list(speakers_dict[category].keys()):
                speaker_name = speakers_dict[category][idx]
                
                # handle numeric string indexes (e.g., "1" → 1)
                if isinstance(idx, str) and idx.isdigit():
                    numeric_idx = int(idx)
                    speakers_dict[category][numeric_idx] = speaker_name
                    if numeric_idx != idx: 
                        del speakers_dict[category][idx]
                
                # remove residual markup and sanitize names
                if isinstance(speaker_name, str):
                    speaker_name = re.sub(r'index=["\']\d+["\']', '', speaker_name)
                    speaker_name = re.sub(r'<[^>]+>', '', speaker_name)
                    speaker_name = speaker_name.strip('" \t\n').strip()
                    
                    # enforce default name for empty values
                    if not speaker_name:
                        speaker_name = "Unknown"
                    
                    # use converted index if available
                    idx_to_use = numeric_idx if 'numeric_idx' in locals() else idx
                    speakers_dict[category][idx_to_use] = speaker_name

    def _replace_all_indexes(self, chunk: Chunk, speakers_dict, speech_indexes, thought_indexes):
        text = chunk.get_content()
        
        # replace speech indexes with detected speaker names
        for idx in speech_indexes:
            if idx in speakers_dict["speech"]:
                speaker = speakers_dict["speech"][idx]
                text = text.replace(f'<speech index="{idx}">', f'<speech speaker="{speaker}">')
            else:
                # fallback for unassigned indexes
                text = text.replace(f'<speech index="{idx}">', '<speech speaker="Unknown">')
        
        # replace thought indexes with detected speaker names
        for idx in thought_indexes:
            if idx in speakers_dict["thought"]:
                speaker = speakers_dict["thought"][idx]
                text = text.replace(f'<em index="{idx}">', f'<em speaker="{speaker}">')
            else:
                # fallback for unassigned indexes
                text = text.replace(f'<em index="{idx}">', '<em speaker="Unknown">')
        
        chunk.set_content(text)
        return chunk
    