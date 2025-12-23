
import json
import os
import csv
import zipfile
import re
from datasets import load_dataset
import pandas as pd
from reportlab.lib.pagesizes import letter, landscape, portrait
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from PIL import Image, ImageDraw, ImageFont
import argparse
import sys

# -------------------------------
# Validation Helpers
# -------------------------------
def get_int_input(prompt, default=None):
    while True:
        value = input(prompt).strip()
        if value == "":
            if default is not None:
                print(f"No input provided. Using default: {default}")
                return default
            print("Please enter a number.")
        else:
            try:
                return int(value)
            except ValueError:
                print("Invalid input. Please enter a valid number.")

def get_valid_directory(prompt, default=None):
    while True:
        path = input(prompt).strip()
        if path == "":
            if default:
                path = default
                print(f"No input provided. Using default directory: {default}")
            else:
                print("Please enter a directory path.")
                continue
        path = os.path.expanduser(path)
        if not os.path.exists(path):
            try:
                os.makedirs(path)
                print(f"Directory '{path}' created successfully.")
            except OSError as e:
                print(f"Error creating directory: {e}")
                continue
        return path

def get_valid_filename(prompt, directory, default=None, overwrite=False):
    while True:
        filename = input(prompt).strip()
        if filename == "":
            if default:
                filename = default
                print(f"No input provided. Using default filename: {default}")
            else:
                print("Please enter a filename.")
                continue
        invalid_chars = '<>:"/\\|?*'
        for ch in invalid_chars:
            filename = filename.replace(ch, "_")
        filepath = os.path.join(directory, filename)
        if os.path.exists(filepath) and not overwrite:
            confirm = input(f"File '{filepath}' already exists. Overwrite? (y/n): ").strip().lower()
            if confirm != "y":
                print("Please enter a different filename.")
                continue
        return filepath

# -------------------------------
# Progress Helper
# -------------------------------
def show_progress(current, total, task_name):
    percent = int((current / total) * 100)
    sys.stdout.write(f"\r{task_name}: {percent}% completed ({current}/{total})")
    sys.stdout.flush()
    if current == total:
        print(" ✅")

# -------------------------------
# Command-line arguments
# -------------------------------
parser = argparse.ArgumentParser(description="Generate glyph images and PDFs")
parser.add_argument("--input_folder", type=str, default="C:\\learnpython\\input", help="Path to the input folder")
parser.add_argument("--output_folder", type=str, default="C:\\learnpython\\output", help="Path to the output folder")
parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files if they exist")
parser.add_argument("--orientation", type=str, choices=["portrait", "landscape"], default="portrait", help="PDF orientation")
args = parser.parse_args()

input_folder = args.input_folder
output_folder = args.output_folder
overwrite = args.overwrite
orientation_choice = args.orientation

os.makedirs(input_folder, exist_ok=True)
os.makedirs(output_folder, exist_ok=True)

pdf_orientation = landscape(letter) if orientation_choice == "landscape" else portrait(letter)

print(f"Using input folder: {input_folder}")
print(f"Using output folder: {output_folder}")
print(f"PDF orientation: {orientation_choice}")
print(f"Overwrite enabled: {overwrite}")

# -------------------------------
# User Input with Validation
# -------------------------------
DEFAULT_FOLDER = r"C:\Users\calmc\OneDrive\medu_neTcher"
folder_path = get_valid_directory(f"Enter the folder path containing .txt files [default: {DEFAULT_FOLDER}]: ", default=DEFAULT_FOLDER)

orientation = input(f"Choose PDF orientation (portrait/landscape) [default: {orientation_choice}]: ").strip() or orientation_choice
pdf_orientation = landscape(letter) if orientation == "landscape" else portrait(letter)

pdf_font_size = get_int_input("Enter font size for PDF (e.g., 10): ", default=10)
image_size = get_int_input("Enter image size in pixels (e.g., 50): ", default=50)
grid_columns = get_int_input("Enter number of columns for grid layout (e.g., 4): ", default=4)
ack_text = input("Enter acknowledgements (e.g., Unicode Consortium, Gardiner List, Your Name): ").strip() or "Unicode Consortium, Gardiner List"

pdf_path = get_valid_filename("Enter output PDF filename (e.g., glyph_output.pdf): ", output_folder, default="glyph_output.pdf", overwrite=overwrite)

# -------------------------------
# Prepare folders
# -------------------------------
image_folder = os.path.join(input_folder, "glyph_images")
os.makedirs(image_folder, exist_ok=True)
output_folder_json = os.path.join(input_folder, "signs_by_category_json")
output_folder_csv = os.path.join(input_folder, "signs_by_category_csv")
os.makedirs(output_folder_json, exist_ok=True)
os.makedirs(output_folder_csv, exist_ok=True)

# -------------------------------
# Helper Functions
# -------------------------------
def create_placeholder_image(glyph, img_path):
    img = Image.new("RGB", (image_size, image_size), color="white")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", int(image_size / 2))
    except:
        font = ImageFont.load_default()
    w, h = draw.textsize(glyph, font=font)
    draw.text(((image_size - w) / 2, (image_size - h) / 2), glyph, fill="black", font=font)
    img.save(img_path)

def gardiner_sort_key(code):
    match = re.match(r"([A-Z]+)(\d+)?", code)
    if match:
        letter = match.group(1)
        number = int(match.group(2)) if match.group(2) else 0
        return (letter, number)
    return (code, 0)

# -------------------------------
# Parse .txt files into structured signs
# -------------------------------
structured_signs = []
seen_codes = set()

txt_files = [f for f in os.listdir(input_folder) if f.lower().endswith(".txt")]
total_files = len(txt_files)
print(f"Parsing {total_files} text files...")

for idx, filename in enumerate(txt_files, start=1):
    show_progress(idx, total_files, "Parsing files")
    file_path = os.path.join(input_folder, filename)
    dataset = load_dataset('text', data_files=file_path)
    lines = [row['text'].strip() for row in dataset['train'] if row['text'].strip()]

    current_category = None
    i = 0
    while i < len(lines):
        line = lines[i]
        if "-" in line and not any(ch.isdigit() for ch in line):
            current_category = line
            i += 1
            continue
        if i + 1 < len(lines):
            code = line
            glyph_line = lines[i + 1]
            description = ""
            glyph_parts = glyph_line.split(maxsplit=1)
            glyph = glyph_parts[0]
            if len(glyph_parts) > 1:
                description = glyph_parts[1]
            unicode_escape = glyph.encode('unicode_escape').decode('utf-8')
            hex_points = " ".join([f"U+{ord(ch):04X}" for ch in glyph])
            entry = {
                "category": current_category or filename.replace(".txt", ""),
                "code": code,
                "glyph": glyph,
                "unicode_escape": unicode_escape,
                "unicode_hex": hex_points,
                "description": description
            }
            if code not in seen_codes:
                structured_signs.append(entry)
                seen_codes.add(code)
        i += 2
print("\n✅ Parsing completed.")

# -------------------------------
# Generate placeholder images with progress
# -------------------------------
print(f"Generating placeholder images for {len(structured_signs)} signs...")
for idx, entry in enumerate(structured_signs, start=1):
    img_path = os.path.join(image_folder, f"{entry['code']}.png")
    if not os.path.exists(img_path):
        create_placeholder_image(entry["glyph"], img_path)
    show_progress(idx, len(structured_signs), "Image generation")

# -------------------------------
# PDF Generation with progress
# -------------------------------
print("\nCreating PDFs...")
grid_pdf_output = os.path.join(input_folder, "Signs_Grid_ByCategory.pdf")
c = canvas.Canvas(grid_pdf_output, pagesize=pdf_orientation)
width, height = pdf_orientation
x_positions = [inch + i * (width - 2 * inch) / grid_columns for i in range(grid_columns)]
y = height - inch

c.setFont("Helvetica-Bold", pdf_font_size + 4)
c.drawString(inch, y, "Egyptian Signs Index")
y -= 40
c.setFont("Helvetica", pdf_font_size + 2)
for cat in categories.keys():
    c.bookmarkPage(cat)
    c.addOutlineEntry(cat, cat, level=0)
    c.drawString(inch, y, f"{cat}")
    c.linkRect("", cat, (inch, y - 5, inch + 200, y + 10))
    y -= 20
y -= 40
c.setFont("Helvetica-Oblique", pdf_font_size)
c.drawString(inch, y, f"Acknowledgements: {ack_text}")
c.showPage()

total_cats = len(categories)
for idx, (cat, items) in enumerate(categories.items(), start=1):
    show_progress(idx, total_cats, "PDF (By Category)")
    c.bookmarkPage(cat)
    c.setFont("Helvetica-Bold", pdf_font_size + 2)
    c.drawString(inch, height - inch, f"Category: {cat}")
    y = height - inch - 40
    col_index = 0
    for entry in items:
        img_path = os.path.join(image_folder, f"{entry['code']}.png")
        x = x_positions[col_index]
        c.drawImage(img_path, x, y - image_size, width=image_size, height=image_size)
        c.drawString(x, y - image_size - 15, f"{entry['code']} ({entry['description']})")
        col_index += 1
        if col_index >= grid_columns:
            col_index = 0
            y -= 80
            if y < inch + 80:
                c.showPage()
                y = height - inch
c.save()
print("\n✅ PDF (By Category) completed.")

# -------------------------------
# ZIP Archive with progress
# -------------------------------
zip_output = os.path.join(input_folder, "Signs_Archive.zip")
files_to_zip = [master_output, excel_output, grid_pdf_output, html_output, readme_path] + all_json_paths + all_csv_paths
print(f"Creating ZIP archive with {len(files_to_zip)} files...")
with zipfile.ZipFile(zip_output, 'w') as zipf:
    for idx, path in enumerate(files_to_zip, start=1):
        zipf.write(path, os.path.relpath(path, input_folder))
        show_progress(idx, len(files_to_zip), "ZIP Archive")
print("\n✅ ZIP archive created successfully.")

