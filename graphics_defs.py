# graphics_defs.py
import drawsvg as draw

def get_timber_pattern():
    """Return the timber (wood) pattern with horizontal lines."""
    timber_pattern = draw.Pattern(100, 30, id='timber_lines', patternUnits='userSpaceOnUse')
    # Background fill matching the original wood colour.
    bg_timber = draw.Rectangle(0, 0, 100, 30, fill='#ffc000ff', fill_opacity=0.25, stroke='none')
    timber_pattern.append(bg_timber)
    # Horizontal line across the tile.
    line = draw.Line(0, 0, 100, 0, stroke='#997d2a40', stroke_width=3)
    timber_pattern.append(line)
    return timber_pattern

def get_concrete_hatch():
    """Return the concrete hatch pattern with a rotated grid."""
    concrete_hatch = draw.Pattern(100, 100, id='concrete_hatch', patternUnits='userSpaceOnUse',
                                  patternTransform='rotate(45) scale(0.2, 0.2)')
    # Background for the concrete hatch pattern.
    bg = draw.Rectangle(0, 0, 100, 100, fill='#a3a3a3ff', fill_opacity=0.25, stroke='none')
    concrete_hatch.append(bg)
    # Grid lines for the hatch pattern.
    line1 = draw.Line(0, 0, 100, 0, stroke='#a3a3a3ff', stroke_width=10)
    line2 = draw.Line(0, 0, 0, 100, stroke='#a3a3a3ff', stroke_width=10)
    concrete_hatch.append(line1)
    concrete_hatch.append(line2)
    return concrete_hatch