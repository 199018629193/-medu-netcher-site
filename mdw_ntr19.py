
import os
import sys
import json
import csv
import zipfile
import re
import logging
import time
from tqdm import tqdm
from datasets import load_dataset
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import argparse

# --- Configuration ---
INPUT_FOLDER = r"C:\learnpython\medu_neTcher"
OUTPUT_FOLDER = r"C:\learnpython\output"
LOG_PATH = os.path.join(OUTPUT_FOLDER, "process_log.txt")
GLYPH_IMAGE_FOLDER = os.path.join(INPUT_FOLDER, "glyph_images")
JSON_FOLDER = os.path.join(INPUT_FOLDER, "signs_by_category_json")
CSV_FOLDER = os.path.join(INPUT_FOLDER, "signs_by_category_csv")
PDF_FILENAME = "glyph_output.pdf"
PDF_PATH = os.path.join(OUTPUT_FOLDER, PDF_FILENAME)
SUMMARY_PATH = os.path.join(INPUT_FOLDER, "Summary_Report.txt")
ZIP_PATH = os.path.join(INPUT_FOLDER, "Signs_Archive.zip")
DEFAULT_ORIENTATION = "portrait"
DEFAULT_FONT_SIZE = 10
DEFAULT_IMAGE_SIZE = 50
DEFAULT_COLUMNS = 4
DEFAULT_ACK = (
    "Unicode Consortium, Gardiner List, "
    "Aegyptus.otf, AegyptusBold.otf, NewGardiner.ttf, NewGardinerNonCore.ttf, "
    "Noto_Sans, Noto_Sans_Egyptian_Hieroglyphs.zip, "
    "rn-i DjeHuty imn DjedkAra"
)

# --- Idle Time Tracking ---
last_activity_time = time.time()
def log_idle_time(task_name):
    global last_activity_time
    current_time = time.time()
    idle_seconds = current_time - last_activity_time
    logging.info(f"Idle before '{task_name}': {idle_seconds:.2f} seconds")
    last_activity_time = current_time

# --- Logging Setup ---
def setup_logging(log_path):
    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

# --- Command-line arguments ---
parser = argparse.ArgumentParser(description="Per medut kheper: Generate glyph images and scrolls")
parser.add_argument("--input_folder", type=str, default=INPUT_FOLDER, help="Per medut in (input folder)")
parser.add_argument("--output_folder", type=str, default=OUTPUT_FOLDER, help="Per medut out (output folder)")
parser.add_argument("--overwrite", action="store_true", help="Overwrite existing scrolls if they exist")
parser.add_argument("--orientation", type=str, choices=["portrait", "landscape"], default=DEFAULT_ORIENTATION, help="Scroll orientation")
args = parser.parse_args()
per_medut_in = args.input_folder
per_medut_out = args.output_folder
overwrite = args.overwrite
orientation_choice = args.orientation

os.makedirs(per_medut_in, exist_ok=True)
os.makedirs(per_medut_out, exist_ok=True)

# Setup logging
setup_logging(LOG_PATH)

pdf_orientation = "landscape" if orientation_choice == "landscape" else "portrait"
print(f"Per medut in: {per_medut_in}")
print(f"Per medut out: {per_medut_out}")
print(f"Scroll orientation: {orientation_choice}")
print(f"Overwrite enabled: {overwrite}")
logging.info("Opening the Scroll: Initial configuration complete.")

# --- Helper Functions ---
def show_progress_sesh(current, total, task_name):
    percent = int((current / total) * 100)
    sys.stdout.write(f"\r{task_name}: {percent}% n medu neTcher ({current}/{total})")
    sys.stdout.flush()
    if current == total:
        print(" ✅")
        logging.info(f"Ma’at Kheper: {task_name} completed.")

def per_sesh_medut(glyph, img_path):
    try:
        img = Image.new("RGB", (100, 100), color="white")
        draw = ImageDraw.Draw(img)
        em_sizes = [0.25, 0.50, 0.75, 1.0]
        y_offset = 10
        for em in em_sizes:
            size = int(40 * em)
            # Try all custom fonts, fallback to default
            font_loaded = False
            for font_name in [
                "Aegyptus.otf", "AegyptusBold.otf", "NewGardiner.ttf",
                "NewGardinerNonCore.ttf", "Noto_Sans", "Noto_Sans_Egyptian_Hieroglyphs.ttf"
            ]:
                try:
                    font_scaled = ImageFont.truetype(font_name, size)
                    font_loaded = True
                    break
                except:
                    continue
            if not font_loaded:
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
                    zipf.write(path, os.path.relpath(path, INPUT_FOLDER))
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

# --- Main Processing ---

log_idle_time("Parsing glyph papyri")
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

# --- Generate placeholder images with progress ---
log_idle_time("Inscribing glyph images")
os.makedirs(GLYPH_IMAGE_FOLDER, exist_ok=True)
print(f"Inscribing glyph images for {len(structured_signs_medut)} signs...")
logging.info(f"Opening the Scroll: Generating {len(structured_signs_medut)} glyph images.")
for entry in tqdm(structured_signs_medut, desc="Inscribing glyph images"):
    img_path = os.path.join(GLYPH_IMAGE_FOLDER, f"{entry['code']}.png")
    if not os.path.exists(img_path):
        per_sesh_medut(entry["glyph"], img_path)

# --- Export JSON and CSV ---
log_idle_time("Export JSON and CSV")
os.makedirs(JSON_FOLDER, exist_ok=True)
os.makedirs(CSV_FOLDER, exist_ok=True)
master_output = os.path.join(per_medut_in, "Signs_Master.json")
seal_medut_json(master_output, structured_signs_medut)
categories = {}
for entry in structured_signs_medut:
    categories.setdefault(entry["category"], []).append(entry)
all_json_paths = [master_output]
all_csv_paths = []
for cat, items in categories.items():
    safe_cat = cat.replace(" ", "_").replace("-", "_")
    cat_json_file = os.path.join(JSON_FOLDER, f"{safe_cat}.json")
    seal_medut_json(cat_json_file, items)
    all_json_paths.append(cat_json_file)
    cat_csv_file = os.path.join(CSV_FOLDER, f"{safe_cat}.csv")
    rows = [["Category", "Code", "Glyph", "Unicode Escape", "Unicode Hex", "Description"]]
    for entry in items:
        rows.append([entry["category"], entry["code"], entry["glyph"], entry["unicode_escape"], entry["unicode_hex"], entry["description"]])
    seal_medut_csv(cat_csv_file, rows)
    all_csv_paths.append(cat_csv_file)

# --- ZIP Archive ---
log_idle_time("ZIP Archive")
zip_output = ZIP_PATH
files_to_zip = [master_output] + all_json_paths + all_csv_paths
seal_kheper_archive(zip_output, files_to_zip)

# --- Summary Report ---
log_idle_time("Summary Report")
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
summary_path = SUMMARY_PATH
with open(summary_path, 'w', encoding='utf-8') as f:
    f.write(rekh_summary_medut)
logging.info(f"Sesh medu: Summary sealed at {summary_path}")
