#!/bin/bash

# The directory containing your Portuguese Markdown files
SOURCE_DIR="pt"

# The directory where the translated English files will be saved
DEST_DIR="en"

# Check if the source directory exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo "Error: Source directory '${SOURCE_DIR}' not found."
    exit 1
fi

# Create the destination directory if it doesn't exist
# The -p flag ensures it doesn't error if the directory already exists
mkdir -p "$DEST_DIR"

export GOOGLE_API_KEY=${GEMINI_API_KEY}

# Find all Markdown files in the source directory and its subdirectories
# The -print0 and xargs -0 combo handles filenames with spaces or special characters
find "$SOURCE_DIR" -type f -name "*.md" -print0 | while IFS= read -r -d '' file; do
    # Define the full path for the destination file
    # This preserves the subdirectory structure
    relative_path="${file#$SOURCE_DIR/}"
    dest_file="$DEST_DIR/$relative_path"

    # Create the subdirectory in the destination if it doesn't exist
    mkdir -p "$(dirname "$dest_file")"

    echo "Processing: $file -> $dest_file"

    # Call the Python script to perform the intelligent translation
    /Users/jonatas.teixeira/weebly_scrapping/new_website/_pages/venv/bin/python translate_markdown.py "$file" "$dest_file"

    if [ $? -ne 0 ]; then
        echo "Stop!!, an error occurred while processing $file"
        exit 1
    fi
    sleep 5
done

echo "
Translation complete. All files have been processed.
"