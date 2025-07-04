#!/bin/bash


path_to_rename=$1

files_txt="suggested_names.txt"

for file in ${path_to_rename}/*.md; do

    file_basename=$(basename "$file")
    if ! grep -q "${file_basename}" ${files_txt}; then
        echo "ERR: $file is not in files.txt, suggesting a name... Skiping..."
        continue
    fi
    
    suggested_file_name=$(grep "${file_basename}" ${files_txt}| cut -d';' -f2)
    if [ -z "$suggested_file_name" ]; then
        echo "ERR: No suggested name found for $file, skipping..."
        continue
    fi
    suggested_image_preffix=$(echo "$suggested_file_name" | sed 's/.*-\([^.]*\).*/\1/')
    images=$(cat "$file" | grep assets/images |  sed 's/.*(\(.*\)).*/\1/')

    # Make a backup of the file
    echo "Backing up $file to ${file}.bak"
    #cp "$file" "${file}.bak"

    # Rename all the assets to the write name
    # Example:
    #   Old name: /assets/images/novos-projetos-do-site-02.png
    #   New name: /assets/images/${suggested_name}-02.png
    # We have to replace the whole name, but keep the numeral suffix in the end and the path in the beginning
    for image in $images; do
        image_dirname=$(dirname "$image")
        image_filename=$(basename "$image")
        
        new_image="${image_dirname}/${suggested_image_preffix}-${image_filename##*-}"

        if [ "$image" == "$new_image" ]; then
            echo "No change needed for $image"
            continue
        fi

        echo "Backing up $image to ${image}.bak"
        #cp "$image" "${image}.bak"
        echo "Renaming $image to $new_image"

        #mv "$image" "$new_image"

        echo "Replacing references in $file"
        # Replace all the references to image in the file with the new name 
        # sed -i '' "s|$image|$new_image|g" "$file"
    done

    echo "Exiting script after processing $file"
    exit 0
done