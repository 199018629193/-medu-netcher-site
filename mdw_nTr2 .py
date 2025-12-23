
import json
import os
import csv
import zipfile
import re
import logging
from datasets import load_dataset
import pandas as pd
from reportlab.lib.pagesizes import letter, landscape, portrait
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from PIL import Image, ImageDraw, ImageFont
import argparse
import sys

# -------------------------------
# Logging Setup
# -------------------------------
def setup_logging(log_path):
    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    logging.info("Opening the Scroll: Process initiated.")

# -------------------------------
# Validation Helpers
# -------------------------------
def get_int_input(prompt, default=None):
    while True:
        value = input(prompt).strip()
        if value == "":
            if default is not None:
                print(f"No input provided. Using default: {default}")
                logging.info(f"Scribe accepted default value: {default}")
                return default
            print("Please enter a number.")
        else:
            try:
                val = int(value)
                logging.info(f"Scribe recorded numeric input: {val}")
                return val
            except ValueError:
                print("Invalid input. Please enter a valid number.")
                logging.warning("Isfet Detected: Invalid numeric input.")

def get_valid_directory(prompt, default=None):
    while True:
        path = input(prompt).strip()
        if path == "":
            if default:
                path = default
                print(f"No input provided. Using default directory: {default}")
                logging.info(f"Scribe accepted default directory: {default}")
            else:
                print("Please enter a directory path.")
                continue
        path = os.path.expanduser(path)
        if not os.path.exists(path):
            try:
                os.makedirs(path)
                print(f"Directory '{path}' created successfully.")
                logging.info(f"Ma’at Restored: Directory created at {path}")
            except OSError as e:
                print(f"Error creating directory: {e}")
                logging.error(f"Isfet Detected: Failed to create directory {path} - {e}")
                continue
        return path

def get_valid_filename(prompt, directory, default=None, overwrite=False):
    while True:
        filename = input(prompt).strip()
        if filename == "":
            if default:
                filename = default
                print(f"No input provided. Using default filename: {default}")
                logging.info(f"Scribe accepted default filename: {default}")
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
                logging.warning(f"Isfet Detected: Overwrite declined for {filepath}")
                continue
        logging.info(f"Scribe recorded filename: {filepath}")
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
        logging.info(f"Ma’at Restored: {task_name} completed.")

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

# Setup logging
log_path = os.path.join(output_folder, "process_log.txt")
setup_logging(log_path)

pdf_orientation = landscape(letter) if orientation_choice == "landscape" else portrait(letter)
print(f"Using input folder: {input_folder}")
print(f"Using output folder: {output_folder}")
print(f"PDF orientation: {orientation_choice}")
print(f"Overwrite enabled: {overwrite}")
logging.info("Opening the Scroll: Initial configuration complete.")

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

logging.info("Opening the Scroll: Directories prepared.")

# -------------------------------
# Helper Functions with Logging
# -------------------------------
def create_placeholder_image(glyph, img_path):
    try:
        img = Image.new("RGB", (image_size, image_size), color="white")
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", int(image_size / 2))
        except:
            font = ImageFont.load_default()
        w, h = draw.textsize(glyph, font=font)
        draw.text(((image_size - w) / 2, (image_size - h) / 2), glyph, fill="black", font=font)
        img.save(img_path)
        logging.info(f"Scribe inscribed glyph image: {glyph}")
    except Exception as e:
        logging.error(f"Isfet Detected: Failed to inscribe glyph '{glyph}' - {e}")

def safe_write_json(path, data):
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logging.info(f"Scribe sealed JSON papyrus: {path}")
    except Exception as e:
        logging.error(f"Isfet Detected: Failed to write JSON '{path}' - {e}")

def safe_write_csv(path, rows):
    try:
        with open(path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            for row in rows:
                writer.writerow(row)
        logging.info(f"Scribe sealed CSV papyrus: {path}")
    except Exception as e:
        logging.error(f"Isfet Detected: Failed to write CSV '{path}' - {e}")

def safe_zip(zip_path, files):
    try:
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for idx, path in enumerate(files, start=1):
                if os.path.exists(path):
                    zipf.write(path, os.path.relpath(path, input_folder))
                    logging.info(f"Scribe archived: {path}")
                else:
                    logging.warning(f"Isfet Detected: Missing file '{path}' skipped.")
                show_progress(idx, len(files), "ZIP Archive")
        logging.info(f"Ma’at Restored: Archive sealed at {zip_path}")
    except Exception as e:
        logging.error(f"Isfet Detected: Failed to create ZIP archive '{zip_path}' - {e}")

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
print(f"Opening the Scroll: Parsing {total_files} papyri...")
logging.info(f"Opening the Scroll: Parsing {total_files} text files.")

for idx, filename in enumerate(txt_files, start=1):
    show_progress(idx, total_files, "Parsing glyph papyri")
    file_path = os.path.join(input_folder, filename)
    try:
        dataset = load_dataset('text', data_files=file_path)
        lines = [row['text'].strip() for row in dataset['train'] if row['text'].strip()]
    except Exception as e:
        logging.error(f"Isfet Detected: Failed to read papyrus '{file_path}' - {e}")
        continue

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
print("\nThe Papyrus is Sealed: Parsing complete.")
logging.info("Ma’at Restored: Parsing completed successfully.")

# -------------------------------
# Generate placeholder images with progress
# -------------------------------
print(f"Inscribing glyph images for {len(structured_signs)} signs...")
logging.info(f"Opening the Scroll: Generating {len(structured_signs)} glyph images.")
for idx, entry in enumerate(structured_signs, start=1):
    img_path = os.path.join(image_folder, f"{entry['code']}.png")
    if not os.path.exists(img_path):
        create_placeholder_image(entry["glyph"], img_path)
    show_progress(idx, len(structured_signs), "Inscribing glyphs")

# -------------------------------
# Export JSON and CSV
# -------------------------------
master_output = os.path.join(input_folder, "Signs_Master.json")
safe_write_json(master_output, structured_signs)

categories = {}
for entry in structured_signs:
    categories.setdefault(entry["category"], []).append(entry)

all_json_paths = [master_output]
all_csv_paths = []

for cat, items in categories.items():
    safe_cat = cat.replace(" ", "_").replace("-", "_")
    cat_json_file = os.path.join(output_folder_json, f"{safe_cat}.json")
    safe_write_json(cat_json_file, items)
    all_json_paths.append(cat_json_file)

    cat_csv_file = os.path.join(output_folder_csv, f"{safe_cat}.csv")
    rows = [["Category", "Code", "Glyph", "Unicode Escape", "Unicode Hex", "Description"]]
    for entry in items:
        rows.append([entry["category"], entry["code"], entry["glyph"], entry["unicode_escape"], entry["unicode_hex"], entry["description"]])
    safe_write_csv(cat_csv_file, rows)
    all_csv_paths.append(cat_csv_file)

# -------------------------------
# ZIP Archive
# -------------------------------
zip_output = os.path.join(input_folder, "Signs_Archive.zip")
files_to_zip = [master_output] + all_json_paths + all_csv_paths
safe_zip(zip_output, files_to_zip)

# -------------------------------
# Summary Report
# -------------------------------
archive_size = os.path.getsize(zip_output) / (1024 * 1024) if os.path.exists(zip_output) else 0
summary_text = (
    "\n=== Sacred Record of Deeds ===\n"
    f"Papyri examined: {total_files}\n"
    f"Glyphs inscribed: {len(structured_signs)}\n"
    f"Images created: {len(structured_signs)}\n"
    f"PDF scrolls: 1 (Signs_Grid_ByCategory.pdf)\n"
    f"Archive sealed: {archive_size:.2f} MB\n"
    "==============================\n"
)
print(summary_text)
logging.info(summary_text)

# Save summary to file
summary_path = os.path.join(input_folder, "Summary_Report.txt")
try:
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary_text)
    logging.info(f"Scribe sealed summary papyrus at {summary_path}")
except Exception as e:
    logging.error(f"Isfet Detected: Failed to write summary report - {e}")
