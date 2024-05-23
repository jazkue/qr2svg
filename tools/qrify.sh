#!/bin/bash

# Set the directory containing SVG files
input_dir="$1"

# Loop through each SVG file in the directory
for svg_file in "$input_dir"/*.svg; do
    # Get the filename without the extension
    filename=$(basename -- "$svg_file")
    filename_no_ext="${filename%.*}"

    # Define the output PNG file path
    png_file="${input_dir}/${filename_no_ext}.png"

    # Apply the code to generate the QR code PNG
    cat "$svg_file" | qrencode --8bit -v 40 --size=5 --margin=0 --output "$png_file"
    
    echo "QR code generated for $filename"
done
