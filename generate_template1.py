
import os
import zipfile

# Folder structure
base_dir = "medu-netcher-template"
css_dir = os.path.join(base_dir, "css")
fonts_dir = os.path.join(base_dir, "fonts")

# Create directories
os.makedirs(css_dir, exist_ok=True)
os.makedirs(fonts_dir, exist_ok=True)

# HTML content with Kemety and Medu Netcher references
html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kemety & Medu Netcher Demo</title>

    <!-- Google Fonts for Noto Sans -->
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans&display=swap" rel="stylesheet">

    <!-- Example CDN for Kemety Fonts (replace with your hosted URLs) -->
    <link href="https://cdn.jsdelivr.net/gh/yourusername/kemety-fonts/aegyptus.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/gh/yourusername/kemety-fonts/gardiner.css" rel="stylesheet">

    <link rel="stylesheet" href="css/styles.css">
</head>
<body>
    <div class="container">
        <h1>𓂀 Kemety Heading</h1>
        <h2>𓆣 Medu Netcher Subheading</h2>
        <p>
            This template uses Kemety fonts for headings and Unicode Medu Netcher glyphs for demonstration.
            If fonts are loaded correctly, these glyphs will render beautifully.
        </p>

        <div class="glyph-sample">
            <!-- Unicode Medu Netcher Glyph Examples -->
            𓀀 𓂋 𓏏 𓊖 𓆣 𓉐 𓎛 𓋴 𓏠 𓍿
        </div>

        <p>
            These characters are Unicode-based (U+13000–U+1342F). Insert them manually in your content.
            Fonts like Kemety or Noto Sans Egyptian Hieroglyphs will render them correctly.
        </p>
    </div>
</body>
</html>
"""

# CSS content
css_content = """/* Headings: Kemety + Medu Netcher fonts */
h1, h2, h3 {
    font-family:
        "Kemety",
        "Medu Netcher",
        "New Gardiner Medium",
        "New GardinerNon Core Medium",
        "Unifont Upper Helper",
        "Segoe UI",
        "Helvetica Neue",
        "Arial",
        sans-serif;
    font-weight: normal;
    margin-bottom: 0.5em;
}

/* Body text: readable fonts */
body, p, li {
    font-family:
        "Noto Sans", /* Google Fonts */
        "Segoe UI",
        "Helvetica Neue",
        "Arial",
        sans-serif;
    font-size: 16px;
    line-height: 1.6;
    color: #333;
    margin: 0;
    padding: 0;
}

body {
    background-color: #f9f9f9;
    padding: 20px;
}

.container {
    max-width: 800px;
    margin: auto;
    background: #fff;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

h1 {
    font-size: 2.5em;
    color: #222;
}

h2 {
    font-size: 1.8em;
    color: #444;
}

.glyph-sample {
    font-size: 2em;
    margin: 20px 0;
    color: #222;
}
"""

# Write files
with open(os.path.join(base_dir, "index.html"), "w", encoding="utf-8") as f:
    f.write(html_content)

with open(os.path.join(css_dir, "styles.css"), "w", encoding="utf-8") as f:
    f.write(css_content)

# Create ZIP
zip_filename = "medu-netcher-template.zip"
with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
    for folder, _, files in os.walk(base_dir):
        for file in files:
            file_path = os.path.join(folder, file)
            zipf.write(file_path, os.path.relpath(file_path, base_dir))

print(f"✅ Deployment ZIP created: {zip_filename}")
