import os
from openai import OpenAI

class OpenAIClient:
    def __init__(self):
        openai_api_key = os.environ.get("OPENAI_API_KEY")
        self.client = OpenAI(api_key=openai_api_key)

    # prescan the text to get the speakers mentioned in it for each chunk
    # the messages contain only the "system" message with the base prompt when prescanning
    def prescan(self, text):
        prescan_prompt = f"""
        Analyze the following text and identify all mentioned speakers and scenes.
        Return ONLY all the speakers in the text in following format:
        - Speaker 1 (e.g. John Doe)
        - Speaker 2 (e.g. Jane)
        """
        messages = [
            {"role": "system", "content": prescan_prompt},
            {"role": "user", "content": text}
        ]
        response = self.client.chat.completions.create(
            messages=messages,
            model="gpt-3.5-turbo",
            temperature=0.7
        )

        result = response.choices[0].message.content
        print("Prescan:", result)
        return result

    # get the speakers from the API response
    # the conversation history contains the base prompt, the prescan message and the text with tagged speech and thoughts for the current chunk with the speakers prompt
    def get_speakers(self, conversation_history):
        speakers_prompt = f"""
        Analyze the following text and identify the speaker for each indexed speech and thought.
        Use the context to assign the correct speaker to each index, the context contains all speakers in the text.
        - ONLY the text enclosed in <speech index="X">»...«</speech> tags is direct speech. Assign the correct speaker to each index.
        - Text enclosed in <em index="X">...</em> tags is internal thought. Assign the correct speaker to each index.
        - Each index must be mapped to a specific speaker based on the context.
        - If a speaker cannot be identified, use "Unknown".
        Important: If there are no <speech index="X">»...«</speech> return an empty JS Object for 'speech'.
        If there are no <em index="X">...</em> return an empty JS Object for 'thought'.

        Return JSON:
        {{
            "speech": {{"1": "speaker_name", "2": "speaker_name"}},
            "thought": {{"1": "speaker_name", "2": "speaker_name"}}
        }}
        """
        conversation = conversation_history + [{"role": "system", "content": speakers_prompt}]
        response = self.client.chat.completions.create(
            messages=conversation,
            model="gpt-3.5-turbo",
            temperature=0.7
        )
        result = response.choices[0].message.content
        print("Get Speakers:", result)
        return result

    # summarize the context to provide a brief overview of the text for the next chunk
    def summarize_context(self, text):
        summary_prompt = f"""
        Summarize the following text in one or two very short sentences to provide context for the next chunk.
        Do it in the language of the provided text.
        The context should contain all speakers in the text and the main events.
        """

        messages = [
            {"role": "system", "content": summary_prompt},
            {"role": "user", "content": text}
        ]
        response = self.client.chat.completions.create(
            messages=messages,
            model="gpt-3.5-turbo",
            temperature=0.7
        )
        result = response.choices[0].message.content
        print("Summarize Context:", result)
        return result
    
# DeepSeek API client has the same methods as the OpenAI client
class DeepSeekClient:
    def __init__(self):
        deepseek_api_key = os.environ.get("DEEPSEEK_API_KEY")
        self.client = OpenAI(api_key=deepseek_api_key, base_url="https://api.deepseek.com")

    def prescan(self, text):
        prescan_prompt = f"""
        Analyze the following text and identify all mentioned speakers and scenes.
        Return ONLY all the speakers in the text in following format:
        - Speaker 1 (e.g. John Doe)
        - Speaker 2 (e.g. Jane)
        """
        messages = [
            {"role": "system", "content": prescan_prompt},
            {"role": "user", "content": text}
        ]
        response = self.client.chat.completions.create(
            messages=messages,
            model="deepseek-chat",
            temperature=0.7
        )

        result = response.choices[0].message.content
        print("Prescan:", result)
        return result

    def get_speakers(self, conversation_history):
        speakers_prompt = f"""
        Analyze the following text and identify the speaker for each indexed speech and thought.
        Use the context to assign the correct speaker to each index, the context contains all speakers in the text.
        - ONLY the text enclosed in <speech index="X">»...«</speech> tags is direct speech. Assign the correct speaker to each index.
        - Text enclosed in <em index="X">...</em> tags is internal thought. Assign the correct speaker to each index.
        - Each index must be mapped to a specific speaker based on the context.
        - If a speaker cannot be identified, use "Unknown".
        Important: If there are no <speech index="X">»...«</speech> return an empty JS Object for 'speech'.
        If there are no <em index="X">...</em> return an empty JS Object for 'thought'.

        Return JSON:
        {{
            "speech": {{"1": "speaker_name", "2": "speaker_name"}},
            "thought": {{"1": "speaker_name", "2": "speaker_name"}}
        }}
        """
        conversation = conversation_history + [{"role": "system", "content": speakers_prompt}]
        response = self.client.chat.completions.create(
            messages=conversation,
            model="deepseek-chat",
            temperature=0.7
        )
        result = response.choices[0].message.content
        print("Get Speakers:", result)
        return result

    def summarize_context(self, text):
        summary_prompt = f"""
        Summarize the following text in one or two very short sentences to provide context for the next chunk.
        Do it in the language of the provided text.
        The context should contain all speakers in the text and the main events.
        """

        messages = [
            {"role": "system", "content": summary_prompt},
            {"role": "user", "content": text}
        ]
        response = self.client.chat.completions.create(
            messages=messages,
            model="deepseek-chat",
            temperature=0.7
        )
        result = response.choices[0].message.content
        print("Summarize Context:", result)
        return result
    
