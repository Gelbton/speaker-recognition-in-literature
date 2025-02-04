import os
from openai import OpenAI

class OpenAIClient:
    def __init__(self):
        openai_api_key = os.environ.get("OPENAI_API_KEY")
        self.client = OpenAI(api_key=openai_api_key)

    def get_speakers(self, tagged_text, context):
        """Analysiert den Text und identifiziert Sprecher für direkte Rede und Gedanken."""
        prompt = f"""
        Analyze the following text and identify the speaker for each indexed speech and thought.
        - Text enclosed in <speech index="X"> tags is direct speech. Assign the correct speaker to each index.
        - Text enclosed in <em index="X"> tags is internal thought. Assign the correct speaker to each index.
        - Each index must be mapped to a specific speaker based on the context.
        - If a speaker cannot be identified, try making a sophisticated guess based on context or if you have no clue, use "Unknown".

        Context:
        {context}

        Return JSON:
        {{
            "speech": {{"1": "speaker_name", "2": "speaker_name"}},
            "thought": {{"1": "speaker_name", "2": "speaker_name"}}
        }}
        """
        
        response = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": tagged_text}
            ],
            model="gpt-3.5-turbo",
            temperature=0.7
        )

        print(response.choices[0].message.content)
        return response.choices[0].message.content

    def summarize_context(self, text):
        summary_prompt = f"""
        Summarize the following text in one or two short sentences to provide context for the next chunk.
        Do it in the language of the provided text.
        The context should contain all speakers in the text and the main events.
        If you detect a significant change in context such as a new scenery or a major timeskip you
        should only summarize the new setting.
        If you see a ___CHAPTER_START___ treat this as a context change.
        {text}
        """

        response = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": summary_prompt},
                {"role": "user", "content": text}
            ],
            model="gpt-3.5-turbo",
            temperature=0.7
        )

        print(response.choices[0].message.content)
        return response.choices[0].message.content
    
class DeepSeekClient:
    def __init__(self):
        deepseek_api_key = os.environ.get("DEEPSEEK_API_KEY")
        self.client = OpenAI(api_key=deepseek_api_key, base_url="https://api.deepseek.com")

    def get_speakers(self, tagged_text, context):
        """Analysiert den Text und identifiziert Sprecher für direkte Rede und Gedanken."""
        prompt = f"""
        Analyze the following text and identify the speaker for each indexed speech and thought.
        - Text enclosed in <speech index="X"> tags is direct speech. Assign the correct speaker to each index.
        - Text enclosed in <em index="X"> tags is internal thought. Assign the correct speaker to each index.
        - Each index must be mapped to a specific speaker based on the context.
        - If a speaker is intentionally mystified, assign a fitting name like "disembodied voice" or "voice from the recording"
        - If a speaker cannot be identified, use "Unknown".

        Context:
        {context}

        Return JSON:
        {{
            "speech": {{"1": "speaker_name", "2": "speaker_name"}},
            "thought": {{"1": "speaker_name", "2": "speaker_name"}}
        }}
        """
        
        response = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": tagged_text}
            ],
            model="deepseek-chat",
            temperature=0.7
        )

        return response.choices[0].message.content

    def summarize_context(self, text):
        summary_prompt = f"""
        Summarize the following text in one or two very short sentences to provide context for the next chunk.
        Do it in the language of the provided text.
        The context should contain all speakers in the text and the main events. If you assigned your own name to a mystified
        speaker without official name, make sure to pass on that name.
        {text}    
        """

        response = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": summary_prompt},
                {"role": "user", "content": text}
            ],
            model="deepseek-chat",
            temperature=0.7
        )

        return response.choices[0].message.content