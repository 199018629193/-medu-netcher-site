
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

# === INTERACTIVE CONFIGURATION ===
input_folder = input("Enter the folder path containing .txt files: ").strip()
image_folder = os.path.join(input_folder, "glyph_images")
os.makedirs(image_folder, exist_ok=True)

output_folder_json = os.path.join(input_folder, "signs_by_category_json")
output_folder_csv = os.path.join(input_folder, "signs_by_category_csv")
os.makedirs(output_folder_json, exist_ok=True)
os.makedirs(output_folder_csv, exist_ok=True)

# PDF options
pdf_orientation_choice = input("Choose PDF orientation (portrait/landscape): ").strip().lower()
pdf_orientation = landscape(letter) if pdf_orientation_choice == "landscape" else portrait(letter)
pdf_font_size = int(input("Enter font size for PDF (e.g., 10): ").strip())
image_size = int(input("Enter image size in pixels (e.g., 50): ").strip())
grid_columns = int(input("Enter number of columns for grid layout (e.g., 4): ").strip())

# Acknowledgements
ack_text = input("Enter acknowledgements (e.g., Unicode Consortium, Gardiner List, Your Name): ").strip()

structured_signs = []
seen_codes = set()

# === Helper: Create placeholder image ===
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

# === Helper: Sort by Gardiner code ===
def gardiner_sort_key(code):
    match = re.match(r"([A-Z]+)(\d+)?", code)
    if match:
        letter = match.group(1)
        number = int(match.group(2)) if match.group(2) else 0
        return (letter, number)
    return (code, 0)

# === PARSE FILES ===
for filename in os.listdir(input_folder):
    if filename.lower().endswith(".txt"):
        file_path = os.path.join(input_folder, filename)
        print(f"[Debug] Processing file: {file_path}")

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

print(f"[Debug] Parsed {len(structured_signs)} unique structured signs")

# === EXPORT MASTER JSON ===
master_output = os.path.join(input_folder, "Signs_Master.json")
with open(master_output, 'w', encoding='utf-8') as f:
    json.dump(structured_signs, f, ensure_ascii=False, indent=2)

# === SPLIT BY CATEGORY ===
categories = {}
for entry in structured_signs:
    cat = entry["category"] or "Unknown"
    categories.setdefault(cat, []).append(entry)

all_csv_paths = []
all_json_paths = [master_output]

for cat, items in categories.items():
    safe_cat = cat.replace(" ", "_").replace("-", "_")

    # JSON export
    cat_json_file = os.path.join(output_folder_json, f"{safe_cat}.json")
    with open(cat_json_file, 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    all_json_paths.append(cat_json_file)

    # CSV export
    cat_csv_file = os.path.join(output_folder_csv, f"{safe_cat}.csv")
    with open(cat_csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Category", "Code", "Glyph", "Unicode Escape", "Unicode Hex", "Description"])
        for entry in items:
            writer.writerow([entry["category"], entry["code"], entry["glyph"], entry["unicode_escape"], entry["unicode_hex"], entry["description"]])
    all_csv_paths.append(cat_csv_file)

# === EXCEL EXPORT ===
excel_output = os.path.join(input_folder, "Signs_All.xlsx")
excel_writer = pd.ExcelWriter(excel_output, engine='openpyxl')

for csv_path in all_csv_paths:
    sheet_name = os.path.splitext(os.path.basename(csv_path))[0][:31]
    df = pd.read_csv(csv_path)
    df.to_excel(excel_writer, sheet_name=sheet_name, index=False)

summary_data = [{"Category": cat, "Sign Count": len(items)} for cat, items in categories.items()]
summary_df = pd.DataFrame(summary_data)
summary_df.loc[len(summary_df)] = ["TOTAL", summary_df["Sign Count"].sum()]
summary_df.to_excel(excel_writer, sheet_name="Summary", index=False)

excel_writer.close()
print(f"[Debug] Excel file created: {excel_output}")

# === HTML INDEX EXPORT ===
html_output = os.path.join(input_folder, "Signs_Index.html")
with open(html_output, 'w', encoding='utf-8') as f:
    f.write("<!DOCTYPE html><html><head><meta charset='UTF-8'><title>Egyptian Signs Index</title>")
    f.write("<style>body{font-family:Arial;margin:20px;}h1{color:#333;}a{display:block;margin:5px 0;text-decoration:none;color:#007BFF;}a:hover{color:#0056b3;}</style></head><body>")
    f.write("<h1>Egyptian Hieroglyphs Index</h1><p>Click a category to view its section in the PDF:</p>")
    for cat in categories.keys():
        f.write(f"<a href='Signs_Grid_ByCategory.pdf#{cat}'>{cat}</a>")
    f.write("<hr><h2>Downloads</h2>")
    f.write("<a href='Signs_Grid_ByCategory.pdf'>Download Grid PDF (By Category)</a>")
    f.write("<a href='Signs_Grid_Sorted.pdf'>Download Grid PDF (Sorted)</a>")
    f.write("<a href='Signs_All.xlsx'>Download Excel Workbook</a>")
    f.write("<a href='Signs_Master.json'>Download Master JSON</a>")
    f.write("<hr><p><strong>Acknowledgements:</strong> " + ack_text + "</p>")
    f.write("</body></html>")
print(f"[Debug] HTML index created: {html_output}")

# === PDF GRID WITH CLICKABLE INDEX ===
grid_pdf_output = os.path.join(input_folder, "Signs_Grid_ByCategory.pdf")
c = canvas.Canvas(grid_pdf_output, pagesize=pdf_orientation)
width, height = pdf_orientation
x_positions = [inch + i * (width - 2 * inch) / grid_columns for i in range(grid_columns)]
y = height - inch

# Create clickable index page
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

# Draw categories with bookmarks
for cat, items in categories.items():
    c.bookmarkPage(cat)
    c.setFont("Helvetica-Bold", pdf_font_size + 2)
    c.drawString(inch, height - inch, f"Category: {cat}")
    y = height - inch - 40
    col_index = 0

    for entry in items:
        img_path = os.path.join(image_folder, f"{entry['code']}.png")
        if not os.path.exists(img_path):
            create_placeholder_image(entry["glyph"], img_path)

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
print(f"[Debug] Grid PDF with clickable index created: {grid_pdf_output}")

# === PDF GRID SORTED BY GARDINER CODE ===
sorted_signs = sorted(structured_signs, key=lambda e: gardiner_sort_key(e["code"]))
sorted_pdf_output = os.path.join(input_folder, "Signs_Grid_Sorted.pdf")
c = canvas.Canvas(sorted_pdf_output, pagesize=pdf_orientation)
width, height = pdf_orientation
x_positions = [inch + i * (width - 2 * inch) / grid_columns for i in range(grid_columns)]
y = height - inch

c.setFont("Helvetica-Bold", pdf_font_size + 2)
c.drawString(inch, y, "Egyptian Signs Grid (Sorted by Gardiner Code)")
y -= 80

col_index = 0
for entry in sorted_signs:
    img_path = os.path.join(image_folder, f"{entry['code']}.png")
    if not os.path.exists(img_path):
        create_placeholder_image(entry["glyph"], img_path)

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
print(f"[Debug] Grid PDF sorted by Gardiner code created: {sorted_pdf_output}")

# === README ===
readme_path = os.path.join(input_folder, "README.txt")
with open(readme_path, 'w', encoding='utf-8') as f:
    f.write("Egyptian Hieroglyphs Dataset\n")
    f.write("=============================\n\n")
    f.write("Contents:\n")
    f.write("- Signs_Master.json: All signs combined in JSON format.\n")
    f.write("- signs_by_category_json/: JSON files split by category.\n")
    f.write("- signs_by_category_csv/: CSV files split by category.\n")
    f.write("- Signs_All.xlsx: Excel workbook with all signs and summary sheet.\n")
    f.write("- Signs_Grid_ByCategory.pdf: Grid layout with clickable index.\n")
    f.write("- Signs_Grid_Sorted.pdf: Grid layout sorted by Gardiner code.\n")
    f.write("- Signs_Index.html: HTML index for web viewing.\n")
    f.write("- glyph_images/: Folder for PNG images (placeholders auto-generated).\n\n")
    f.write("Acknowledgements:\n")
    f.write(f"{ack_text}\n")

# === ZIP ARCHIVE ===
zip_output = os.path.join(input_folder, "Signs_Archive.zip")

with zipfile.ZipFile(zip_output,withzipfile.ZipFile(zip_output, 'w') aszipf:
    zipf.write(master_output, os.path.basename(master_output))
    zipf.write(excel_output, os.path.basename(excel_output))
    zipf.write(grid_pdf_output, os.path.basename(grid_pdf_output))
    zipf.write(ed_pdf_output, os.path.basename(ed_pdf_output))
    zipf.write(sorted_pdf_output, os.path.basename(sorted_pdf_output))
    zipf.write(html_output, os.path.basename(html_output))
    zipf.write(readme_path, os.path.basename(readme_path))

    
# Add all JSON and CSV files
    for path in all_json_paths + all_csv_paths:


