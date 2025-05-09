import json
import re
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

    # finds and tags speech and thoughts in the text through regex
    def _find_and_tag_speech_and_thoughts(self, chunk: Chunk) -> Chunk:
        chunk_content = chunk.get_content()
        
        speech_pattern = r'(?<!<[^>]*)([„“"‚‘‚‘»«›‹])([^„“"‚‘‚‘»«›‹]+?)\1'
'
        speech_matches = list(re.finditer(speech_pattern, chunk_content))
        
        thought_pattern = r'<em>([^<]+)</em>'
        thought_matches = list(re.finditer(thought_pattern, chunk_content))
        
        modified_text = chunk_content
        replacements = []
        
        # tag thoughts with incremental indexes
        for i, match in enumerate(thought_matches, 1):
            original = match.group(0)
            replacement = f'<em index="{i}">{match.group(1)}</em>'
            start_pos = match.start()
            replacements.append((start_pos, original, replacement))
        
        # tag speech segments with incremental indexes
        for i, match in enumerate(speech_matches, 1):
            original = match.group(0)
            replacement = f'<speech index="{i}">»{match.group(1)}«</speech>'
            start_pos = match.start()
            replacements.append((start_pos, original, replacement))
        
        # sort replacements backwards to prevent position shifting
        replacements.sort(key=lambda x: x[0], reverse=True)
        
        # apply replacements to the text
        for _, original, replacement in replacements:
            modified_text = modified_text.replace(original, replacement, 1)
        
        chunk.set_content(modified_text)
        return chunk

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
    