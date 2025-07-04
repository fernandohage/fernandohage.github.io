#!/bin/bash

path_to_rename=$1
files_txt="${2:-suggested_names.txt}"

for file in ${path_to_rename}/*.md; do

    file_basename=$(basename "$file")
    if ! grep -q "${file_basename}" ${files_txt}; then
        echo "ERR: $file is not in files.txt, suggesting a name... Skipping..."
        continue
    fi
    
    suggested_file_name=$(grep "^${file_basename};" ${files_txt} | cut -d';' -f2 | head -1)
    if [ -z "$suggested_file_name" ]; then
        echo "ERR: No suggested name found for $file, skipping..."
        continue
    fi

    suggested_image_prefix="${suggested_file_name%.*}"
    # Extract image paths more carefully to avoid newlines
    images=$(grep -oE '/assets/images/[^)]*\.(jpg|jpeg|png|gif|webp)' "$file" | grep -v "http" | sort -u)

    # Make a backup of the file
    echo "Backing up $file to ${file}.bak"
    cp "$file" "${file}.bak"

    # Rename all the assets to the right name
    # Example:
    #   Old name: /assets/images/novos-projetos-do-site-02.png
    #   New name: /assets/images/${suggested_name}-02.png
    # We have to replace the whole name, but keep the numeral suffix in the end and the path in the beginning
    for image in $images; do
        # Clean the image path and remove any potential newlines or whitespace
        image=$(echo "$image" | tr -d '\n\r' | xargs)
        
        # Skip if image variable is empty
        if [ -z "$image" ]; then
            echo "Skipping empty image path"
            continue
        fi
        
        # Skip URLs
        if [[ "$image" == http* ]]; then
            echo "Skipping URL: $image"
            continue
        fi
        
        image_dirname=$(dirname "$image")
        image_filename=$(basename "$image")
        
        # Extract the suffix (number and extension) from the filename
        suffix=$(echo "$image_filename" | sed -E 's/.*-([0-9]+\.[a-zA-Z]+)$/\1/')
        
        # If no numeric suffix found, use the original filename
        if [ "$suffix" = "$image_filename" ]; then
            new_image="${image_dirname}/${suggested_image_prefix}.${image_filename##*.}"
        else
            new_image="${image_dirname}/${suggested_image_prefix}-${suffix}"
        fi

        # Clean the new_image path as well
        new_image=$(echo "$new_image" | tr -d '\n\r' | xargs)

        if [ "$image" == "$new_image" ]; then
            echo "No change needed for $image"
            continue
        fi

        # Check if source file exists before attempting to rename
        if [ ! -f "./$image" ]; then
            echo "Source file does not exist: ./$image, skipping..."
            if [ -f "./${image}.bak" ] && [ -f "${new_image}" ]; then
                echo "Image was already renamed."
            fi
        else
            echo "Backing up $image to ${image}.bak"
            cp "./$image" "./${image}.bak"
            echo "Renaming $image to $new_image"
            mv "./$image" "./$new_image"
        fi

        echo "Replacing references in $file"
        # Use a safer approach for sed replacement to avoid newline issues
        temp_file=$(mktemp)
        if sed "s|$(printf '%s\n' "$image" | sed 's/[[\.*^$()+?{|]/\\&/g')|$(printf '%s\n' "$new_image" | sed 's/[[\.*^$()+?{|]/\\&/g')|g" "$file" > "$temp_file"; then
            mv "$temp_file" "$file"
            echo "Successfully replaced references to $image with $new_image"
        else
            echo "Error replacing references in $file for $image" 1>&2
            rm -f "$temp_file"
            continue
        fi
    done

    # Rename the file itself
    echo "Renaming $file to ${file%/*}/${suggested_file_name}"
    mv "$file" "${file%/*}/${suggested_file_name}"

done