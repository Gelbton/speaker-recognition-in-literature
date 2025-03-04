import json
import re
from api import OpenAIClient, DeepSeekClient
from item_chunk import Chunk

class SpeechIndexer:
    def __init__(self, api_client="openai"):
        match api_client:
            case "openai":
                self.api_client = OpenAIClient()
            case "deepseek":
                self.api_client = DeepSeekClient()
            case _:
                raise ValueError("Invalid API client specified.")
        # messages are used to store the conversation history for the API
        # the first message is a system message to explain the purpose of the assistant (base prompt)
        self.messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant for detecting the speakers of direct speech and internal thoughts. "
                    "Use the provided context to assign the correct speaker to each indexed speech and thought. "
                )
            }
        ]

<<<<<<< HEAD
    def process_chunk(self, chunk: Chunk) -> Chunk:
        tagged_chunk = self._find_and_tag_speech_and_thoughts(chunk)
        tagged_text = tagged_chunk.get_content() # extract the content from the chunk
        speakers_response = self.api_client.get_speakers(tagged_text, self.context) # identify speakers in json format
=======
    # processes the text by first prescanning it, then tagging speech and thoughts, and finally assigning speakers
    def process_chunk(self, chunk: Chunk) -> Chunk:
        chunk_content = chunk.get_content()
        # prescan the current chunk to extract all speakers and the content
        prescan_summary = self.api_client.prescan(chunk_content)
        self.messages.append({"role": "assistant", "content": f"Occurring speakers in the text: {prescan_summary}"})
>>>>>>> context-propagation

        # tag speech and thoughts
        tagged_chunk = self._find_and_tag_speech_and_thoughts(chunk)
        tagged_text = tagged_chunk.get_content()
        self.messages.append({"role": "user", "content": f"Text for speaker detection:\n{tagged_text}"})

        # get the speakers from the API response and apply them to the text
        speakers_response = self.api_client.get_speakers(self.messages) # identify speakers in json format
        try:
            speakers_dict = json.loads(speakers_response)
            speakers_dict.setdefault("speech", {})
            speakers_dict.setdefault("thought", {})

<<<<<<< HEAD
            processed_chunk = self._apply_speakers_to_text(tagged_chunk, speakers_dict) # add annotated text to chunk
            self._update_context(processed_chunk)
            return processed_chunk
            
        except json.JSONDecodeError as e:
            print(f"Fehler beim Parsen der Api-Antwort: {str(e)}")
            return tagged_chunk

=======
            processed_chunk = self._apply_speakers_to_text(tagged_chunk, speakers_dict)
            processed_chunk_text = processed_chunk.get_content()
            
            # summarize the context to provide a brief overview of the text for the next chunk
            summary = self.api_client.summarize_context(processed_chunk_text)
            self.messages.append({"role": "assistant", "content": f"Kontext-Zusammenfassung: {summary}"})
            return processed_chunk

        except json.JSONDecodeError as e:
            print(f"Could not parse the API answer: {str(e)}")
            return tagged_chunk

    # finds and tags speech and thoughts in the text through regex
>>>>>>> context-propagation
    def _find_and_tag_speech_and_thoughts(self, chunk: Chunk) -> Chunk:
        chunk_content = chunk.get_content()
        speech_pattern = r'»([^»«]+)«'
        speech_matches = re.finditer(speech_pattern, chunk_content)

        thought_pattern = r'<em>([^<]+)</em>'
        thought_matches = re.finditer(thought_pattern, chunk_content)

        modified_text = chunk_content
        for i, match in enumerate(speech_matches, 1):
            modified_text = modified_text.replace(match.group(0), f'<speech index="{i}">»{match.group(1)}«</speech>')

        for i, match in enumerate(thought_matches, 1):
            modified_text = modified_text.replace(match.group(0), f'<em index="{i}">{match.group(1)}</em>')
        
        chunk.set_content(modified_text)
        return chunk

<<<<<<< HEAD
=======
    # gets the speakers from the API response and apply them to the text
>>>>>>> context-propagation
    def _apply_speakers_to_text(self, chunk: Chunk, speakers_json) -> Chunk:
        text = chunk.get_content()
        for idx, speaker in speakers_json["speech"].items():
            text = text.replace(f'<speech index="{idx}">', f'<speech speaker="{speaker}">')

        for idx, speaker in speakers_json["thought"].items():
            text = text.replace(f'<em index="{idx}">', f'<em speaker="{speaker}">')

        chunk.set_content(text)
        return chunk
<<<<<<< HEAD

    def _update_context(self, processed_chunk: Chunk):
        """Holt eine kurze Zusammenfassung von der API, um den Kontext zu aktualisieren."""
        processed_text = processed_chunk.get_content()
        self.context = self.api_client.summarize_context(processed_text)
=======
>>>>>>> context-propagation
