import sys
import os
import re
import google.generativeai as genai

# --- Gemini API Configuration ---
if 'GEMINI_API_KEY' not in os.environ:

    print("Error: The GEMINI_API_KEY environment variable is not set.", file=sys.stderr)
    print("Please obtain an API key from Google AI Studio and set it as an environment variable.", file=sys.stderr)
    sys.exit(1)

try:
    genai.configure(api_key=os.environ['GEMINI_API_KEY'])
except Exception as e:
    print(f"Error configuring Gemini API: {e}", file=sys.stderr)
    sys.exit(1)


# DO NOT REMOVE THESE COMMENTS, THEY ARE USED TO IGNORE THE LINES IN THE TRANSLATION
#genai_model="gemini-2.0-flash"                     # Exceed the limit
#genai_model="gemini-2.0-flash-lite"                 # Exceed the limit
#genai_model="gemini-2.5-flash"                     # Exceed the limit
#genai_model="gemini-2.5-flash-lite-preview-06-17"  # Exceed the limit
genai_model = "gemini-2.5-pro"  # Exceed the limit
######################

def translate_markdown_file(content, source_lang, target_lang):
    """
    Translates the entire Markdown file in a single Gemini API call using a detailed prompt.
    """
    prompt = (
        f"You are a professional translator with experience in software engineering. "
        f"Translate the following Markdown file from {source_lang} to {target_lang}.\n\n"
        "Instructions:\n"
        "- The file contains a YAML front matter section at the top (between '---' lines) in the first 7 lines.\n"
        "  - Only translate the values of the fields, not the keys.\n"
        "  - Do NOT translate the values for the keys: date, slug, permalink.\n"
        "  - Update the 'lang' field from 'pt' to 'en'.\n"
        "- For the rest of the file, translate all user-facing text (headings, paragraphs, etc.).\n"
        "- Do NOT translate code blocks, inline code, URLs, HTML tags, or markdown formatting.\n"
        "- Preserve all formatting, structure, and non-translatable elements exactly as in the original.\n"
        "- Do not add any extra text or explanation.\n"
        "- Keep the result well formatted as the original file, it must be used in a Jekyll website.\n\n"
        "Here is the file:\n"
        "-----\n"
        f"{content}\n"
        "-----"
    )
    
    try:
        model = genai.GenerativeModel(genai_model)
        response = model.generate_content(prompt)
        if response.parts:
            return response.text.strip()
        else:
            print("Warning: Gemini API returned an empty response.", file=sys.stderr)
            return content
    except Exception as e:
        print(f"Error during Gemini API call: {e}", file=sys.stderr)
        return content

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: python3 {sys.argv[0]} <input_file> <output_file>")
        sys.exit(1)

    input_file_path = sys.argv[1]
    output_file_path = sys.argv[2]
    
    SOURCE_LANG = 'pt'
    TARGET_LANG = 'en'

    try:
        with open(input_file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()

        translated_content = translate_markdown_file(original_content, SOURCE_LANG, TARGET_LANG)

        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write(translated_content)
            
        # A quieter success message is better for batch processing
        # print(f"Successfully translated {input_file_path} to {output_file_path}")

    except FileNotFoundError:
        print(f"Error: Input file not found at {input_file_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)
