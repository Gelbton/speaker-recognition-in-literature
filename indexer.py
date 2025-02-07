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

    # processes the text by first prescanning it, then tagging speech and thoughts, and finally assigning speakers
    def process_text(self, text):
        # prescan the text to get the speakers mentioned in it
        prescan_summary = self.api_client.prescan(text)
        self.messages.append({"role": "assistant", "content": f"Occuring speakers in the text: {prescan_summary}"})

        # tag the speech and thoughts in the text and prepare it for the speaker detection by adding it to the messages
        tagged_text = self._find_and_tag_speech_and_thoughts(text)
        self.messages.append({"role": "user", "content": f"Text for the speaker detection:\n{tagged_text}"})

        # get the speakers from the API response and apply them to the text
        speakers_response = self.api_client.get_speakers(self.messages)
        try:
            speakers_dict = json.loads(speakers_response)
            speakers_dict.setdefault("speech", {})
            speakers_dict.setdefault("thought", {})

            processed_text = self._apply_speakers_to_text(tagged_text, speakers_dict)
            
            # summarize the context to provide a brief overview of the text for the next chunk
            summary = self.api_client.summarize_context(processed_text)
            self.messages.append({"role": "assistant", "content": f"Kontext-Zusammenfassung: {summary}"})
            return processed_text

        except json.JSONDecodeError as e:
            print(f"Could not parse the API answer: {str(e)}")
            return tagged_text

    # finds and tags speech and thoughts in the text through regex
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

    # gets the speakers from the API response and apply them to the text
    def _apply_speakers_to_text(self, text, speakers_json):
        for idx, speaker in speakers_json.get("speech", {}).items():
            text = text.replace(f'<speech index="{idx}">', f'<speech speaker="{speaker}">')
        for idx, speaker in speakers_json.get("thought", {}).items():
            text = text.replace(f'<em index="{idx}">', f'<em speaker="{speaker}">')
        return text
