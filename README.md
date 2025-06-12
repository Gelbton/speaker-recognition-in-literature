# Speaker Recognition in Literature

This repository provides a tool and code for identifying and recognizing speakers in literary texts using modern OpenAI LLMs. The project is written entirely in Python and is designed to analyze works of literature, extract dialogue, and 
attribute spoken lines to specific characters.

## Features

- Automated extraction of dialogues from literary texts in the EPUB format
- Attribution of speech to characters based on context and linguistic features
- Reparsing and color highliting in the output EPUB with annotated speakers

# How to run it
1\. **Clone and Install**
   \- `git clone https://github.com/Gelbton/speaker-recognition-in-literature`
   \- `cd <your-repo-folder>`
   \- `pip install -r requirements.txt`

2\. **Set API Key**
   \- Set your OpenAI or DeepSeek API key as an environment variable:
     \- Linux/macOS: `export OPENAI_API_KEY=your-key`
     \- Windows: `set OPENAI_API_KEY=your-key`

3\. **Edit Script**
   \- Set `epub_file_path` to your EPUB file location in `main.py`.

4\. **Run**
   \- `python main.py`

5\. **Use the GUI**
   \- Create a group for each speaker (even without aliases).
   \- Map aliases as needed.
   \- Close the GUI when done.

6\. **Output**
   \- Find your highlighted EPUB as `output.epub` (or as specified).

