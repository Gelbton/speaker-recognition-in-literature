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
        self.messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant for detecting the speakers of direct speech and internal thoughts. "
                    "Use the provided context to assign the correct speaker to each indexed speech and thought. "
                )
            }
        ]

    def process_text(self, text):
        prescan_summary = self.api_client.prescan(text)
        self.messages.append({"role": "assistant", "content": f"Occuring speakers in the text: {prescan_summary}"})

        tagged_text = self._find_and_tag_speech_and_thoughts(text)
        self.messages.append({"role": "user", "content": f"Text for the speaker detection:\n{tagged_text}"})

        speakers_response = self.api_client.get_speakers(self.messages)
        try:
            speakers_dict = json.loads(speakers_response)
            speakers_dict.setdefault("speech", {})
            speakers_dict.setdefault("thought", {})

            processed_text = self._apply_speakers_to_text(tagged_text, speakers_dict)

            summary = self.api_client.summarize_context(processed_text)
            self.messages.append({"role": "assistant", "content": f"Kontext-Zusammenfassung: {summary}"})
            return processed_text

        except json.JSONDecodeError as e:
            print(f"Fehler beim Parsen der API-Antwort: {str(e)}")
            return tagged_text

    def _find_and_tag_speech_and_thoughts(self, text):
        speech_counter = 0
        def speech_repl(match):
            nonlocal speech_counter
            speech_counter += 1
            return f'<speech index="{speech_counter}">»{match.group(1)}«</speech>'

        thought_counter = 0
        def thought_repl(match):
            nonlocal thought_counter
            thought_counter += 1
            return f'<em index="{thought_counter}">{match.group(1)}</em>'

        text = re.sub(r'»([^»«]+)«', speech_repl, text)
        text = re.sub(r'<em>([^<]+)</em>', thought_repl, text)
        return text

    def _apply_speakers_to_text(self, text, speakers_json):
        for idx, speaker in speakers_json.get("speech", {}).items():
            text = text.replace(f'<speech index="{idx}">', f'<speech speaker="{speaker}">')
        for idx, speaker in speakers_json.get("thought", {}).items():
            text = text.replace(f'<em index="{idx}">', f'<em speaker="{speaker}">')
        return text
