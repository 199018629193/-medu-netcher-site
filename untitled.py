
import os

input_folder = r"C:\learnpython\medu_neTcher"
txt_files = [f for f in os.listdir(input_folder) if f.lower().endswith(".txt")]

print("All files in folder:", os.listdir(input_folder))
print("TXT files found:", txt_files)
print("TXT files found:", txt_files)