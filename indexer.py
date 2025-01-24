import json
import os
import re
from openai import OpenAI

class SpeechIndexer:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)
        self.context = ""

    def process_text(self, text):
        tagged_text = self._find_and_tag_speech_and_thoughts(text)
        speakers_response = self._get_speakers_from_openai(tagged_text)

        try:
            speakers_dict = json.loads(speakers_response)
            
            if "speech" not in speakers_dict:
                speakers_dict["speech"] = {}
            if "thought" not in speakers_dict:
                speakers_dict["thought"] = {}
                
            processed_text = self._apply_speakers_to_text(tagged_text, speakers_dict)
            
            #self._update_context(processed_text)
            print("--------------------------------" + self.context + "--------------------------")
            
            return processed_text
            
        except json.JSONDecodeError as e:
            print(f"\nFehler beim Parsen der OpenAI-Antwort:")
            print(f"Original Response: {speakers_response}")
            print(f"Error: {str(e)}")
            return tagged_text
        
    def _find_and_tag_speech_and_thoughts(self, text):
        speech_pattern = r'»([^»«]+)«'
        speech_matches = re.finditer(speech_pattern, text)
        
        thought_pattern = r'<em>([^<]+)</em>'
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
            replacement = f'<em index="{i}">{content}</em>'
            thought_replacements.append((original, replacement))
        
        for original, replacement in reversed(speech_replacements + thought_replacements):
            modified_text = modified_text.replace(original, replacement)
        
        return modified_text

    def _get_speakers_from_openai(self, tagged_text):
        prompt = f"""
        Analyze the following text and identify the speaker for each indexed speech and thought.
        - Text enclosed in <speech index="X"> tags is direct speech. Assign the correct speaker to each index.
        - Text enclosed in <em index="X"> tags is internal thought. Assign the correct speaker to each index.
        - Each index (e.g., "1", "2", "3") must be mapped to a specific speaker based on the context.
        - If a speaker cannot be identified, use "Unknown" as the speaker name.

        Use the following context to help identify speakers:
        {self.context}

        Return ONLY a JSON-like list of speaker assignments in this format:
        {{
            "speech": {{"1": "speaker_name", "2": "speaker_name", ...}},
            "thought": {{"1": "speaker_name", "2": "speaker_name", ...}}
        }}
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
        
        print(response.choices[0].message.content)
        return response.choices[0].message.content

    def _apply_speakers_to_text(self, text, speakers_json):
        for idx, speaker in speakers_json["speech"].items():
            pattern = f'<speech index="{idx}">'
            replacement = f'<speech speaker="{speaker}">'
            text = text.replace(pattern, replacement)
        
        for idx, speaker in speakers_json["thought"].items():
            pattern = f'<em index="{idx}">'
            replacement = f'<em speaker="{speaker}">'
            text = text.replace(pattern, replacement)
        
        return text

    def _update_context(self, processed_text):
        summary_prompt = f"""
        Summarize the following text in one or two very short sentences to provide context for the next chunk.
        Do it in the language of the provided text.
        The context should contain all speakers in the text and the main events.
        {processed_text}
        """
        
        response = self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": summary_prompt
                },
                {
                    "role": "user",
                    "content": processed_text
                }
            ],
            model="gpt-3.5-turbo",
            temperature=0.7
        )
        
        self.context = response.choices[0].message.content