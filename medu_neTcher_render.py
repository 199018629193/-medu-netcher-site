import svgwrite
import argparse
import os
import json

def load_sign_map(json_path):
    """Load mapping of sign codes to glyphs from JSON."""
    with open(json_path, 'r', encoding='utf-8') as f:
        signs = json.load(f)
    return {entry['code']: entry['glyph'] for entry in signs}

def medu_netcher_render(signs, sign_map, title=None, font_size=48, font_family="Aegyptus", as_svg=False, vertical=False):
    """Render Medu NeTcher signs as Unicode or SVG."""
    unicode_chars = []
    for code in signs:
        glyph = sign_map.get(code)
        if glyph:
            unicode_chars.append(glyph)
        else:
            unicode_chars.append('?')  # Unknown code

    if as_svg:
        # SVG vertical stacking
        height = (len(unicode_chars) + (1 if title else 0)) * font_size + font_size
        width = font_size * 2
        dwg = svgwrite.Drawing(size=(width, height))
        y = font_size
        if title:
            dwg.add(dwg.text(
                title,
                insert=(0, y),
                font_size=int(font_size * 0.7),
                font_family=font_family,
                font_weight="bold"
            ))
            y += int(font_size * 0.8)
        for glyph in unicode_chars:
            dwg.add(dwg.text(
                glyph,
                insert=(font_size // 2, y),
                font_size=font_size,
                font_family=font_family
            ))
            y += font_size
        return dwg.tostring()
    else:
        # Unicode output
        output = ""
        if title:
            output += title + "\n"
        if vertical:
            output += "\n".join(unicode_chars)
        else:
            output += "".join(unicode_chars)
        return output

def main():
    parser = argparse.ArgumentParser(description="Render Medu Neṭer signs as Unicode or SVG.")
    parser.add_argument('--json', type=str, required=True, help="Path to Signs_Master.json")
    parser.add_argument('--codes', type=str, required=True, help="Comma-separated list of sign codes (e.g., A1,G17,HIER001)")
    parser.add_argument('--svg', action='store_true', help="Output SVG instead of Unicode text")
    parser.add_argument('--vertical', action='store_true', help="Stack signs vertically")
    parser.add_argument('--font_size', type=int, default=48, help="Font size for SVG output")
    parser.add_argument('--font_family', type=str, default="Noto Sans Egyptian Hieroglyphs", help="Font family for SVG output")
    parser.add_argument('--title', type=str, help="Title for the scroll")
    parser.add_argument('--output', type=str, help="Output file (SVG or TXT). If not set, prints to console.")
    args = parser.parse_args()

    # Load sign mapping
    sign_map = load_sign_map(args.json)
    # Parse codes
    signs = [code.strip() for code in args.codes.split(',')]
    # Render
    result = medu_netcher_render(
        signs,
        sign_map,
        title=args.title,
        font_size=args.font_size,
        font_family=args.font_family,
        as_svg=args.svg,
        vertical=args.vertical
    )
    

    # Output
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"Output written to {args.output}")
    else:
        print(result)

if __name__ == "__main__":
    main()
