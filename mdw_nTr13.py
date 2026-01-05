import os
import sys 
import json
import csv
import zipfile
import re
import logging
import time
import pandas as pd
from reportlab.lib.pagesizes import letter, landscape, portrait
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from datetime import datetime
from tqdm import tqdm
from datasets import load_dataset
from PIL import Image, ImageDraw, ImageFont

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
DEFAULT_ACK = "Unicode Consortium, Gardiner List"

# --- Logging Setup ---
def setup_logging(log_path):
    logging.basicConfig( 
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

def log_progress(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_PATH, "a") as log:
        log.write(f"{timestamp} - {message}\n")
    logging.info(message)

# --- Idle Time Tracking ---
last_activity_time = time.time()

def log_idle_time(step_name):
    global last_activity_time
    current_time = time.time()
    idle_seconds = current_time - last_activity_time
    log_progress(f"Idle before '{step_name}': {idle_seconds:.2f} seconds")
    last_activity_time = current_time

# --- Prepare Folders ---
os.makedirs(INPUT_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(GLYPH_IMAGE_FOLDER, exist_ok=True)
os.makedirs(JSON_FOLDER, exist_ok=True)
os.makedirs(CSV_FOLDER, exist_ok=True)

setup_logging(LOG_PATH)
log_progress("Script started.")
log_progress(f"Input folder: {INPUT_FOLDER}")
log_progress(f"Output folder: {OUTPUT_FOLDER}")

# --- Discover TXT Files ---
log_idle_time("Discover TXT Files")
txt_files = [f for f in os.listdir(INPUT_FOLDER) if f.lower().endswith(".txt")]
log_progress(f"Found {len(txt_files)} .txt files in input folder.")

# --- Parse TXT Files into Structured Signs ---
log_idle_time("Parse TXT Files")
structured_signs = []
seen_codes = set()
for idx, filename in enumerate(txt_files, start=1):
    file_path = os.path.join(INPUT_FOLDER, filename)
    try:
        dataset = load_dataset('text', data_files=file_path)
        lines = [row['text'].strip() for row in dataset['train'] if row['text'].strip()]
    except Exception as e:
        log_progress(f"Error reading {file_path}: {e}")
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

log_progress("Parsing complete.")

# --- Generate Glyph Images ---
log_idle_time("Generate Glyph Images")
def create_glyph_image(glyph, img_path):
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
        log_progress(f"Glyph '{glyph}' image saved at {img_path}")
    except Exception as e:
        log_progress(f"Error creating glyph image '{glyph}': {e}")

log_progress(f"Generating glyph images for {len(structured_signs)} signs.")
for entry in tqdm(structured_signs, desc="Inscribing glyph images"):
    img_path = os.path.join(GLYPH_IMAGE_FOLDER, f"{entry['code']}.png")
    if not os.path.exists(img_path):
        create_glyph_image(entry["glyph"], img_path)

# --- Export JSON and CSV ---
log_idle_time("Export JSON and CSV")
def save_json(path, data):
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        log_progress(f"JSON saved: {path}")
    except Exception as e:
        log_progress(f"Error saving JSON {path}: {e}")

def save_csv(path, rows):
    try:
        with open(path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            for row in rows:
                writer.writerow(row)
        log_progress(f"CSV saved: {path}")
    except Exception as e:
        log_progress(f"Error saving CSV {path}: {e}")

master_json = os.path.join(INPUT_FOLDER, "Signs_Master.json")
save_json(master_json, structured_signs)

categories = {}
for entry in structured_signs:
    categories.setdefault(entry["category"], []).append(entry)

json_paths = [master_json]
csv_paths = []
for cat, items in categories.items():
    safe_cat = cat.replace(" ", "_").replace("-", "_")
    cat_json_file = os.path.join(JSON_FOLDER, f"{safe_cat}.json")
    save_json(cat_json_file, items)
    json_paths.append(cat_json_file)
    cat_csv_file = os.path.join(CSV_FOLDER, f"{safe_cat}.csv")
    rows = [["Category", "Code", "Glyph", "Unicode Escape", "Unicode Hex", "Description"]]
    for entry in items:
        rows.append([entry["category"], entry["code"], entry["glyph"], entry["unicode_escape"], entry["unicode_hex"], entry["description"]])
    save_csv(cat_csv_file, rows)
    csv_paths.append(cat_csv_file)

# --- ZIP Archive ---
log_idle_time("ZIP Archive")
def create_zip(zip_path, files):
    try:
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for path in files:
                if os.path.exists(path):
                    zipf.write(path, os.path.relpath(path, INPUT_FOLDER))
                    log_progress(f"Archived: {path}")
                else:
                    log_progress(f"Missing file skipped: {path}")
        log_progress(f"Archive created at {zip_path}")
    except Exception as e:
        log_progress(f"Error creating archive {zip_path}: {e}")

files_to_zip = [master_json] + json_paths + csv_paths
create_zip(ZIP_PATH, files_to_zip)

# --- Summary Report ---
log_idle_time("Summary Report")
archive_size = os.path.getsize(ZIP_PATH) / (1024 * 1024) if os.path.exists(ZIP_PATH) else 0
summary = (
    "\n=== Medu neTcher Rekh ===\n"
    f"Papyri sesh: {len(txt_files)}\n"
    f"Medu neTcher inscribed: {len(structured_signs)}\n"
    f"Seshu kheper: {len(structured_signs)}\n"
    f"Per medu scrolls: 1\n"
    f"Kheper archive: {archive_size:.2f} MB\n"
    "========================\n"
)
print(summary)
log_progress("Summary:\n" + summary)
with open(SUMMARY_PATH, 'w', encoding='utf-8') as f:
    f.write(summary)
log_progress(f"Summary report saved at {SUMMARY_PATH}")
