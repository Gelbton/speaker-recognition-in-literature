import json
import re
from api import OpenAIClient, DeepSeekClient

class SpeechIndexer:
    def __init__(self, api_client="openai"):
        match api_client:
            case "openai":
                self.api_client = OpenAIClient()
            case "deepseek":
                self.api_client = DeepSeekClient()
            case _:
                raise ValueError("Invalid API client specified.")
        self.context = ""

    def process_text(self, text):
        tagged_text = self._find_and_tag_speech_and_thoughts(text)
        speakers_response = self.api_client.get_speakers(tagged_text, self.context)

        try:
            speakers_dict = json.loads(speakers_response)
            if "speech" not in speakers_dict:
                speakers_dict["speech"] = {}
            if "thought" not in speakers_dict:
                speakers_dict["thought"] = {}

            processed_text = self._apply_speakers_to_text(tagged_text, speakers_dict)
            self._update_context(processed_text)
            return processed_text
            
        except json.JSONDecodeError as e:
            print(f"Fehler beim Parsen der Api-Antwort: {str(e)}")
            return tagged_text

    def _find_and_tag_speech_and_thoughts(self, text):
        speech_pattern = r'»([^»«]+)«'
        speech_matches = re.finditer(speech_pattern, text)

        thought_pattern = r'<em>([^<]+)</em>'
        thought_matches = re.finditer(thought_pattern, text)

        modified_text = text
        for i, match in enumerate(speech_matches, 1):
            modified_text = modified_text.replace(match.group(0), f'<speech index="{i}">»{match.group(1)}«</speech>')

        for i, match in enumerate(thought_matches, 1):
            modified_text = modified_text.replace(match.group(0), f'<em index="{i}">{match.group(1)}</em>')

        return modified_text

    def _apply_speakers_to_text(self, text, speakers_json):
        for idx, speaker in speakers_json["speech"].items():
            text = text.replace(f'<speech index="{idx}">', f'<speech speaker="{speaker}">')

        for idx, speaker in speakers_json["thought"].items():
            text = text.replace(f'<em index="{idx}">', f'<em speaker="{speaker}">')

        return text

    def _update_context(self, processed_text):
        """Holt eine kurze Zusammenfassung von der API, um den Kontext zu aktualisieren."""
        self.context = self.api_client.summarize_context(processed_text)