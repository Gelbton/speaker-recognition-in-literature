import re
import os
from openai import OpenAI

def find_and_tag_speech_and_thoughts(text):
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

def load_text(input_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        input_text = file.read()
        return input_text



def get_speakers_from_openai(tagged_text):
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    prompt = """
    Analyze the following text and identify the speaker for each indexed speech and thought.
    Return only a JSON-like list of speaker assignments in this format:
    {
        "speech": {"1": "speaker_name", "2": "speaker_name", ...},
        "thought": {"1": "speaker_name", "2": "speaker_name", ...}
    }
    """
    
    response = client.chat.completions.create(
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
    print(response)
    return response.choices[0].message.content



def apply_speakers_to_text(text, speakers_json):
    for idx, speaker in speakers_json["speech"].items():
        pattern = f'<speech index="{idx}">'
        replacement = f'<speech speaker="{speaker}">'
        text = text.replace(pattern, replacement)
    
    for idx, speaker in speakers_json["thought"].items():
        pattern = f'<em class="calibre7" index="{idx}">'
        replacement = f'<em class="calibre7" speaker="{speaker}">'
        text = text.replace(pattern, replacement)
    
    return text

def process_text(input_text):
    tagged_text = find_and_tag_speech_and_thoughts(input_text)
    
    speakers_response = get_speakers_from_openai(tagged_text)
    
    speakers_dict = eval(speakers_response)
    final_text = apply_speakers_to_text(tagged_text, speakers_dict)
    
    return final_text

html_text = load_text('heavy_dialogue.txt')
processed_text = process_text(html_text)
print(processed_text)