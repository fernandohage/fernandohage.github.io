#!/bin/bash

path_to_rename=$1
files_txt="suggested_names.txt"

for file in ${path_to_rename}/*.md; do

    file_basename=$(basename "$file")
    if ! grep -q "${file_basename}" ${files_txt}; then
        echo "ERR: $file is not in files.txt, suggesting a name... Skipping..."
        continue
    fi
    
    suggested_file_name=$(grep "${file_basename}" ${files_txt}| cut -d';' -f2)
    if [ -z "$suggested_file_name" ]; then
        echo "ERR: No suggested name found for $file, skipping..."
        continue
    fi

    suggested_image_preffix="${suggested_file_name%.*}"
    # Filter out URLs and only get actual image paths
    images=$(cat "$file" | grep -E "assets/images/[^)]*\.(jpg|jpeg|png|gif|webp)" | sed 's/.*(\([^)]*assets\/images\/[^)]*\)).*/\1/' | grep -v "http" | sort -u)

    # Make a backup of the file
    echo "Backing up $file to ${file}.bak"
    cp "$file" "${file}.bak"

    # Rename all the assets to the right name
    # Example:
    #   Old name: /assets/images/novos-projetos-do-site-02.png
    #   New name: /assets/images/${suggested_name}-02.png
    # We have to replace the whole name, but keep the numeral suffix in the end and the path in the beginning
    for image in $images; do
        # Skip if image variable is empty or contains newlines
        if [ -z "$image" ] || [[ "$image" == *$'\n'* ]]; then
            echo "Skipping invalid image path: '$image'"
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
            new_image="${image_dirname}/${suggested_image_preffix}.${image_filename##*.}"
        else
            new_image="${image_dirname}/${suggested_image_preffix}-${suffix}"
        fi

        if [ "$image" == "$new_image" ]; then
            echo "No change needed for $image"
            continue
        fi

        # Check if source file exists before attempting to rename
        if [ ! -f "./$image" ]; then
            echo "Source file does not exist: ./$image, skipping..."
            continue
        fi

        echo "Backing up $image to ${image}.bak"
        cp "./$image" "./${image}.bak"
        echo "Renaming $image to $new_image"

        mv "./$image" "./$new_image"

        echo "Replacing references in $file"
        # Replace all the references to image in the file with the new name 
        # Use a more careful sed approach to avoid issues with special characters
        sed -i '' "s|$(echo "$image" | sed 's/[[\.*^$()+?{|]/\\&/g')|$(echo "$new_image" | sed 's/[[\.*^$()+?{|]/\\&/g')|g" "$file"
    done

    # Rename the file itself
    echo "Renaming $file to ${file%/*}/${suggested_file_name}"
    mv "$file" "${file%/*}/${suggested_file_name}"

done