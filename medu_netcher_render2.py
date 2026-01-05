
import json
import svgwrite
import argparse
import os

def load_sign_map(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        signs = json.load(f)
    return {entry['code']: entry['glyph'] for entry in signs}

def medu_netcher_render(signs, sign_map, font_size=48, font_family="Agyptus Noto Sans Egyptian Hieroglyphs", as_svg=False):
    unicode_chars = []
    for code in signs:
        glyph = sign_map.get(code)
        if glyph:
            unicode_chars.append(glyph)
        else:
            unicode_chars.append('?')  # Unknown code
    unicode_string = ''.join(unicode_chars)

    if as_svg:
        dwg = svgwrite.Drawing(size=(len(unicode_string)*font_size, int(font_size*1.5)))
        dwg.add(dwg.text(
            unicode_string,
            insert=(0, font_size),
            font_size=font_size,
            font_family=font_family
        ))
        return dwg.tostring()
    else:
        return unicode_string

def main():
    parser = argparse.ArgumentParser(description="Render Medu Neṭer signs as Unicode or SVG.")
    parser.add_argument('--json', type=str, required=True, help="Path to Signs_Master.json")
    parser.add_argument('--codes', type=str, required=True, help="Comma-separated list of sign codes (e.g., A1,G17,HIER001)")
    parser.add_argument('--svg', action='store_true', help="Output SVG instead of Unicode text")
    parser.add_argument('--font_size', type=int, default=48, help="Font size for SVG output")
    parser.add_argument('--font_family', type=str, default="Noto Sans Egyptian Hieroglyphs", help="Font family for SVG output")
    parser.add_argument('--output', type=str, help="Output file (SVG or TXT). If not set, prints to console.")
    args = parser.parse_args()

    sign_map = load_sign_map(args.json)
    signs = [code.strip() for code in args.codes.split(',')]
    result = medu_netcher_render(
        signs, sign_map,
        font_size=args.font_size,
        font_family=args.font_family,
        as_svg=args.svg
    )

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"Output written to {args.output}")
    else:
        print(result)

if __name__ == "__main__":
    main()
