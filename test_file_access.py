
import os

# Paths to test
test_folder = r"C:\learnpython\medu_neTcher"
test_image_folder = os.path.join(test_folder, "glyph_images")
test_json_folder = os.path.join(test_folder, "signs_by_category_json")
test_csv_folder = os.path.join(test_folder, "signs_by_category_csv")

# Create folders if missing
for folder in [test_folder, test_image_folder, test_json_folder, test_csv_folder]:
    os.makedirs(folder, exist_ok=True)

# Test writing a file in each folder
try:
    with open(os.path.join(test_folder, "test.txt"), "w") as f:
        f.write("This is a test file in medu_neTcher.\n")
    with open(os.path.join(test_image_folder, "test_image.txt"), "w") as f:
        f.write("This is a test file in glyph_images.\n")
    with open(os.path.join(test_json_folder, "test_json.txt"), "w") as f:
        f.write("This is a test file in signs_by_category_json.\n")
    with open(os.path.join(test_csv_folder, "test_csv.txt"), "w") as f:
        f.write("This is a test file in signs_by_category_csv.\n")
    print("File access test succeeded: All files written successfully.")
except Exception as e:
    print(f"File access test failed: {e}")
