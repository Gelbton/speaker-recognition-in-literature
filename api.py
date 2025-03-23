import os
from openai import OpenAI

class OpenAIClient:
    def __init__(self):
        openai_api_key = os.environ.get("OPENAI_API_KEY")
        self.client = OpenAI(api_key=openai_api_key)

    # prescan the text to get the speakers mentioned in it for each chunk
    def prescan(self, text):
        prescan_prompt = """
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
    def get_speakers(self, conversation_history):
        speakers_prompt = """
        Analyze the text and identify the speaker for EACH numbered speech and thought segment.
        
        IMPORTANT INSTRUCTIONS:
        - Return a valid JSON object with speech and thought categories
        - For each index, provide ONLY the name of the speaker or thinker
        - DO NOT include the word "index" or any other formatting in your response
        - If you're unsure about a speaker, use "Unknown"
        
        Example of CORRECT response format:
        {
            "speech": {
                "1": "John",
                "2": "Mary",
                "3": "James"
            },
            "thought": {
                "1": "Sarah"
            }
        }
        
        Make sure to identify a speaker for EVERY indexed segment mentioned in the user's message.
        """
        
        # Füge den speakers_prompt hinzu und erzwinge JSON-Format
        conversation = list(conversation_history)  # Erstelle eine Kopie
        conversation.append({"role": "system", "content": speakers_prompt})
        
        response = self.client.chat.completions.create(
            messages=conversation,
            model="gpt-3.5-turbo",
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        result = response.choices[0].message.content
        print("Get Speakers:", result)
        return result

    # summarize the context to provide a brief overview of the text for the next chunk
    def summarize_context(self, text):
        summary_prompt = """
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
    
# DeepSeek API client
class DeepSeekClient:
    def __init__(self):
        deepseek_api_key = os.environ.get("DEEPSEEK_API_KEY")
        self.client = OpenAI(api_key=deepseek_api_key, base_url="https://api.deepseek.com")

    # prescan the text to get the speakers mentioned in it for each chunk
    def prescan(self, text):
        prescan_prompt = """
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

    # get the speakers from the API response
    def get_speakers(self, conversation_history):
        # In dieser verbesserten Version fragen wir explizit nach jedem gefundenen Index
        
        # Extrahiere alle vorhandenen Indizes aus dem letzten Benutzer-Prompt
        user_content = ""
        for msg in reversed(conversation_history):
            if msg["role"] == "user":
                user_content = msg["content"]
                break
        
        # Extrahiere die Indizes aus dem Text (einfache Implementation)
        speech_indices = []
        thought_indices = []
        
        speech_pattern = r'<speech index="(\d+)">'
        for match in re.finditer(speech_pattern, user_content):
            speech_indices.append(match.group(1))
            
        thought_pattern = r'<em index="(\d+)">'
        for match in re.finditer(thought_pattern, user_content):
            thought_indices.append(match.group(1))
        
        # Erstelle einen angepassten Prompt, der explizit nach jedem Index fragt
        speakers_prompt = f"""
        Analyze the text and identify the speaker for each of these specific speech and thought segments.
        
        Speech indices to identify: {', '.join(speech_indices)}
        Thought indices to identify: {', '.join(thought_indices)}
        
        IMPORTANT INSTRUCTIONS:
        - Return a valid JSON object with the following structure:
        {{
            "speech": {{
                "1": "Speaker Name",
                "2": "Another Speaker"
            }},
            "thought": {{
                "1": "Thinker Name"
            }}
        }}
        
        - For each index, provide ONLY the name of the speaker or thinker
        - DO NOT include the word "index" or any tags in your response
        - If you're unsure about a speaker, use "Unknown"
        - Include an entry for EVERY index mentioned above
        """
        
        # Füge den angepassten Prompt zur Konversation hinzu
        conversation = list(conversation_history)
        conversation.append({"role": "system", "content": speakers_prompt})
        
        # Füge eine zusätzliche direkte Anweisung hinzu (da DeepSeek möglicherweise kein response_format unterstützt)
        conversation.append({
            "role": "user", 
            "content": "Provide your response as a valid JSON object ONLY, with no additional text. Include entries for ALL indices."
        })
        
        response = self.client.chat.completions.create(
            messages=conversation,
            model="deepseek-chat",
            temperature=0.7
        )
        result = response.choices[0].message.content
        print("Get Speakers:", result)
        return result

    # summarize the context to provide a brief overview of the text for the next chunk
    def summarize_context(self, text):
        summary_prompt = """
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