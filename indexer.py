import json
import os
import re
from openai import OpenAI

class SpeechIndexer:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)

    def process_text(self, text):
        tagged_text = self._find_and_tag_speech_and_thoughts(text)
        speakers_response = self._get_speakers_from_openai(tagged_text)

        # test response printing
        #print("\nOpenAI Response:")
        #print("=" * 50)
        #print(speakers_response)
        #print("=" * 50)
        #print("\nContinuing with text processing...\n")


        try:
            speakers_dict = json.loads(speakers_response)
            
            if "speech" not in speakers_dict:
                speakers_dict["speech"] = {}
            if "thought" not in speakers_dict:
                speakers_dict["thought"] = {}
                
            processed_text = self._apply_speakers_to_text(tagged_text, speakers_dict)
            return processed_text
            
        except json.JSONDecodeError as e:
            print(f"\nFehler beim Parsen der OpenAI-Antwort:")
            print(f"Original Response: {speakers_response}")
            print(f"Error: {str(e)}")
            return tagged_text
        
        
    def _find_and_tag_speech_and_thoughts(self, text):
        speech_pattern = r'»([^»«]+)«'
        speech_matches = re.finditer(speech_pattern, text)
        
        thought_pattern = r'<em class="calibre7">([^<]+)</em>'
        thought_matches = re.finditer(thought_pattern, text)
        
        modified_text = text
        
        speech_replacements = []
        for i, match in enumerate(speech_matches, 1):
            original = match.group(0)
            content = match.group(1)
            replacement = f'<speech index="{i}">»{content}«</speech>'
            speech_replacements.append((original, replacement))

        thought_replacements = []
        for i, match in enumerate(thought_matches, 1):
            original = match.group(0)
            content = match.group(1)
            replacement = f'<em class="calibre7" index="{i}">{content}</em>'
            thought_replacements.append((original, replacement))
        
        for original, replacement in reversed(speech_replacements + thought_replacements):
            modified_text = modified_text.replace(original, replacement)
        
        return modified_text

    def _get_speakers_from_openai(self, tagged_text):
        prompt = """
        Analyze the following text and identify the speaker for each indexed speech and thought.
        Return only a JSON-like list of speaker assignments in this format:
        {
            "speech": {"1": "speaker_name", "2": "speaker_name", ...},
            "thought": {"1": "speaker_name", "2": "speaker_name", ...}
        }
        Note: If no speech or thoughts are found, return empty objects.
        """
        
        response = self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": prompt
                },
                {
                    "role": "user",
                    "content": tagged_text
                }
            ],
            model="gpt-3.5-turbo",
            temperature=0.7
        )
        
        return response.choices[0].message.content

    def _apply_speakers_to_text(self, text, speakers_json):
        for idx, speaker in speakers_json["speech"].items():
            pattern = f'<speech index="{idx}">'
            replacement = f'<speech speaker="{speaker}">'
            text = text.replace(pattern, replacement)
        
        for idx, speaker in speakers_json["thought"].items():
            pattern = f'<em class="calibre7" index="{idx}">'
            replacement = f'<em class="calibre7" speaker="{speaker}">'
            text = text.replace(pattern, replacement)
        
        return text