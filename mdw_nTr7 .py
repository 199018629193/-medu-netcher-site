
import os 
from tqdm import tqdm 
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

# ------------------------------
# Logging Setup
# ------------------------------
def setup_logging(log_path): 
    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
input_folder = "medu_neTcher"
os.makedirs(input_folder, exist_ok=True)
files = os.listdir(input_folder)
print("Files in input folder:", files)
# If filtering for PDFs:
pdf_files = [f for f in files if f.lower().endswith('.pdf')]
print("PDF files found:", pdf_files)
logging.info("Opening the Scroll: Per medut kheper (Process initiated).")
input_files = os.listdir(input_folder)
print("Files found in input folder:", input_files)

# ------------------------------
# Validation Helpers
# ------------------------------
def get_int_input(prompt, default=None):
    while True:
        value = input(prompt).strip()
        if value == "":
            if default is not None:
                print(f"No input provided. Using default: {default}")
                logging.info(f"Sesh medu: Default numeric value accepted ({default})")
                return default
            print("Please enter a number.")
        else:
            try:
                val = int(value)
                logging.info(f"Sesh medu: Numeric input recorded ({val})")
                return val
            except ValueError:
                print("Invalid input. Please enter a valid number.")
                logging.warning("Isfet Kheper: Invalid numeric input.")

def get_valid_directory(prompt, default=None):
    while True:
        path = input(prompt).strip()
        if path == "":
            if default:
                path = default
                print(f"No input provided. Using default directory: {default}")
                logging.info(f"Sesh medu: Default directory accepted ({default})")
            else:
                print("Please enter a directory path.")
                continue
        path = os.path.expanduser(path)
        if not os.path.exists(path):
            try:
                os.makedirs(path)
                print(f"Directory '{path}' created successfully.")
                logging.info(f"Ma’at Kheper: Directory created ({path})")
            except OSError as e:
                print(f"Error creating directory: {e}")
                logging.error(f"Isfet Kheper: Failed to create directory ({path}) - {e}")
                continue
        return path

def get_valid_filename(prompt, directory, default=None, overwrite=False):
    while True:
        filename = input(prompt).strip()
        if filename == "":
            if default:
                filename = default
                print(f"No input provided. Using default filename: {default}")
                logging.info(f"Sesh medu: Default filename accepted ({default})")
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
                logging.warning(f"Isfet Kheper: Overwrite declined for {filepath}")
                continue
        logging.info(f"Sesh medu: Filename recorded ({filepath})")
        return filepath

# ------------------------------
# Progress Helper
# ------------------------------
def show_progress_sesh(current, total, task_name):
    percent = int((current / total) * 100)
    sys.stdout.write(f"\r{task_name}: {percent}% n medu neTcher ({current}/{total})")
    sys.stdout.flush()
    if current == total:
        print(" ✅")
        logging.info(f"Ma’at Kheper: {task_name} completed.")

# ------------------------------
# Command-line arguments
# ------------------------------
parser = argparse.ArgumentParser(description="Per medut kheper: Generate glyph images and scrolls")
parser.add_argument("--input_folder", type=str, default="C:\\learnpython\\input", help="Per medut in (input folder)")
parser.add_argument("--output_folder", type=str, default="C:\\learnpython\\output", help="Per medut out (output folder)")
parser.add_argument("--overwrite", action="store_true", help="Overwrite existing scrolls if they exist")
parser.add_argument("--orientation", type=str, choices=["portrait", "landscape"], default="portrait", help="Scroll orientation")
args = parser.parse_args()
per_medut_in = args.input_folder
per_medut_out = args.output_folder
overwrite = args.overwrite
orientation_choice = args.orientation
os.makedirs(per_medut_in, exist_ok=True)
os.makedirs(per_medut_out, exist_ok=True)

# Setup logging
log_path = os.path.join(per_medut_out, "process_log.txt")
setup_logging(log_path)
pdf_orientation = landscape(letter) if orientation_choice == "landscape" else portrait(letter)
print(f"Per medut in: {per_medut_in}")
print(f"Per medut out: {per_medut_out}")
print(f"Scroll orientation: {orientation_choice}")
print(f"Overwrite enabled: {overwrite}")
logging.info("Opening the Scroll: Initial configuration complete.")

# ------------------------------
# User Input with Validation
# ------------------------------
DEFAULT_FOLDER = r"C:\Users\calmc\OneDrive\medu_neTcher"
folder_path = get_valid_directory(f"Enter papyri path [default: {DEFAULT_FOLDER}]: ", default=DEFAULT_FOLDER)
orientation = input(f"Choose scroll orientation (portrait/landscape) [default: {orientation_choice}]: ").strip() or orientation_choice
maat_font_size = get_int_input("Enter font size for scroll (e.g., 10): ", default=10)
image_size = get_int_input("Enter glyph image size in pixels (e.g., 50): ", default=50)
sesh_columns = get_int_input("Enter number of columns for scroll layout (e.g., 4): ", default=4)
djed_medut_ack = input("Enter acknowledgements (e.g., Unicode Consortium, Gardiner List): ").strip() or "Unicode Consortium, Gardiner List"
pdf_path = get_valid_filename("C:\\learnpython\\output (e.g., glyph_output.pdf): ", per_medut_out, default="glyph_output.pdf", overwrite=overwrite)

# ------------------------------
# Prepare folders
# ------------------------------
per_sesh_seshu = os.path.join(per_medut_in, "glyph_images")
os.makedirs(per_sesh_seshu, exist_ok=True)
output_folder_json = os.path.join(per_medut_in, "signs_by_category_json")
output_folder_csv = os.path.join(per_medut_in, "signs_by_category_csv")
os.makedirs(output_folder_json, exist_ok=True)
os.makedirs(output_folder_csv, exist_ok=True)
logging.info("Opening the Scroll: Houses prepared for medut.")

# ------------------------------
# Helper Functions with Kemety Names
# ------------------------------
def per_sesh_medut(glyph, img_path):
    try:
        img = Image.new("RGB", (100, 100), color="white")
        draw = ImageDraw.Draw(img)
        em_sizes = [0.25, 0.50, 0.75, 1.0]
        y_offset = 10
        for em in em_sizes:
            size = int(40 * em)
            try:
                font_scaled = ImageFont.truetype("arial.ttf", size)
            except:
                font_scaled = ImageFont.load_default()
            w, h = draw.textsize(glyph, font=font_scaled)
            draw.text(((100 - w) / 2, y_offset), glyph, fill="black", font=font_scaled)
            y_offset += h + 5
        img.save(img_path)
        logging.info(f"Sesh medu: Glyph '{glyph}' inscribed with em sizes at {img_path}")
    except Exception as e:
        logging.error(f"Isfet Kheper: Failed to inscribe glyph '{glyph}' - {e}")

def seal_medut_json(path, data):
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logging.info(f"Sesh medu: Papyrus sealed in JSON ({path})")
    except Exception as e:
        logging.error(f"Isfet Kheper: Failed to seal JSON papyrus ({path}) - {e}")

def seal_medut_csv(path, rows):
    try:
        with open(path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            for row in rows:
                writer.writerow(row)
        logging.info(f"Sesh medu: Papyrus sealed in CSV ({path})")
    except Exception as e:
        logging.error(f"Isfet Kheper: Failed to seal CSV papyrus ({path}) - {e}")

def seal_kheper_archive(zip_path, files):
    try:
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for idx, path in enumerate(files, start=1):
                if os.path.exists(path):
                    zipf.write(path, os.path.relpath(path, per_medut_in))
                    logging.info(f"Sesh medu: Archived papyrus ({path})")
                else:
                    logging.warning(f"Isfet Kheper: Missing papyrus '{path}' skipped.")
                show_progress_sesh(idx, len(files), "Per kheper archive")
        logging.info(f"Ma’at Kheper: Archive sealed at {zip_path}")
    except Exception as e:
        logging.error(f"Isfet Kheper: Failed to seal archive ({zip_path}) - {e}")

def gardiner_sort_key(code):
    match = re.match(r"([A-Z]+)(\d+)?", code)
    if match:
        letter = match.group(1)
        number = int(match.group(2)) if match.group(2) else 0
        return (letter, number)
    return (code, 0)

# ------------------------------
# Parse .txt files into structured signs
# ------------------------------
structured_signs_medut = []
seen_codes = set()
txt_files = [f for f in os.listdir(per_medut_in) if f.lower().endswith(".txt")]
total_files = len(txt_files)
print(f"Opening the Scroll: Parsing {total_files} papyri...")
logging.info(f"Opening the Scroll: Parsing {total_files} text files.")
for idx, filename in enumerate(txt_files, start=1):
    show_progress_sesh(idx, total_files, "Parsing glyph papyri")
    file_path = os.path.join(per_medut_in, filename)
    try:
        dataset = load_dataset('text', data_files=file_path)
        lines = [row['text'].strip() for row in dataset['train'] if row['text'].strip()]
    except Exception as e:
        logging.error(f"Isfet Kheper: Failed to read papyrus '{file_path}' - {e}")
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
                structured_signs_medut.append(entry)
                seen_codes.add(code)
            i += 2
print("\nThe Papyrus is Sealed: Parsing complete.")
logging.info("Ma’at Kheper: Parsing completed successfully.")

# ------------------------------
# Generate placeholder images with progress
# ------------------------------
print(f"Inscribing glyph images for {len(structured_signs_medut)} signs...")
logging.info(f"Opening the Scroll: Generating {len(structured_signs_medut)} glyph images.")
for entry in tqdm(structured_signs_medut, desc="Inscribing glyph images"):
    img_path = os.path.join(per_sesh_seshu, f"{entry['code']}.png")
    if not os.path.exists(img_path):
        per_sesh_medut(entry["glyph"], img_path)

# ------------------------------
# Export JSON and CSV
# ------------------------------
master_output = os.path.join(per_medut_in, "Signs_Master.json")
seal_medut_json(master_output, structured_signs_medut)
categories = {}
for entry in structured_signs_medut:
    categories.setdefault(entry["category"], []).append(entry)
all_json_paths = [master_output]
all_csv_paths = []
for cat, items in categories.items():
    safe_cat = cat.replace(" ", "_").replace("-", "_")
    cat_json_file = os.path.join(output_folder_json, f"{safe_cat}.json")
    seal_medut_json(cat_json_file, items)
    all_json_paths.append(cat_json_file)
    cat_csv_file = os.path.join(output_folder_csv, f"{safe_cat}.csv")
    rows = [["Category", "Code", "Glyph", "Unicode Escape", "Unicode Hex", "Description"]]
    for entry in items:
        rows.append([entry["category"], entry["code"], entry["glyph"], entry["unicode_escape"], entry["unicode_hex"], entry["description"]])
    seal_medut_csv(cat_csv_file, rows)
    all_csv_paths.append(cat_csv_file)

# ------------------------------
# ZIP Archive
# ------------------------------
zip_output = os.path.join(per_medut_in, "Signs_Archive.zip")
files_to_zip = [master_output] + all_json_paths + all_csv_paths
seal_kheper_archive(zip_output, files_to_zip)

# ------------------------------
# Summary Report
# ------------------------------
archive_size = os.path.getsize(zip_output) / (1024 * 1024) if os.path.exists(zip_output) else 0
rekh_summary_medut = (
    "\n=== Medu neTcher Rekh ===\n"
    f"Papyri sesh: {total_files}\n"
    f"Medu neTcher inscribed: {len(structured_signs_medut)}\n"
    f"Seshu kheper: {len(structured_signs_medut)}\n"
    f"Per medu scrolls: 1\n"
    f"Kheper archive: {archive_size:.2f} MB\n"
    "========================\n"
)
print(rekh_summary_medut)
logging.info(rekh_summary_medut)
summary_path = os.path.join(per_medut_in, "Summary_Report.txt")
with open(summary_path, 'w', encoding='utf-8') as f:
    f.write(rekh_summary_medut)
logging.info(f"Sesh medu: Summary sealed at {summary_path}")
