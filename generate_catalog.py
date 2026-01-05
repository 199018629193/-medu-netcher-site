
import json

# Path to your master sign file
json_path = r"C:\learnpython\medu_neTcher\Signs_Master.json"
output_path = r"C:\learnpython\medu_neTcher\complete_catalog.txt"

# Load all signs
with open(json_path, "r", encoding="utf-8") as f:
    signs = json.load(f)

# Group signs by category
categories = {}
for entry in signs:
    cat = entry.get("category", "Uncategorized")
    categories.setdefault(cat, []).append(entry)

# Write catalog to file
with open(output_path, "w", encoding="utf-8") as out:
    for cat, entries in categories.items():
        out.write(f"=== {cat} ===\n")
        for entry in entries:
            # Each line: code, glyph, description
            out.write(f"{entry['code']}\t{entry['glyph']}\t{entry.get('description','')}\n")
        out.write("\n")

print(f"Complete catalog written to {output_path}")
