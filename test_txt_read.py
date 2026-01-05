
import os

input_folder = r"C:\learnpython\medu_neTcher"
txt_files = [f for f in os.listdir(input_folder) if f.lower().endswith(".txt")]

print("TXT files found:", txt_files)

for fname in txt_files:
    path = os.path.join(input_folder, fname)
    print(f"\n--- {fname} ---")
    try:
        with open(path, encoding="utf-8") as f:
            for i, line in enumerate(f):
                print(line.rstrip())
                if i >= 4:
                    break
    except Exception as e:
        print(f"Error reading {fname}: {e}")
