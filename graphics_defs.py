# graphics_defs.py
import drawsvg as draw
import math

def get_timber_pattern():
    timber_pattern = draw.Pattern(100, 30, id='timber_lines', patternUnits='userSpaceOnUse')
    bg_timber = draw.Rectangle(0, 0, 100, 30, fill='#ffc000ff', fill_opacity=0.25, stroke='none')
    timber_pattern.append(bg_timber)
    line = draw.Line(0, 0, 100, 0, stroke='#997d2a40', stroke_width=3)
    timber_pattern.append(line)
    return timber_pattern

def get_concrete_hatch():
    concrete_hatch = draw.Pattern(100, 100, id='concrete_hatch', patternUnits='userSpaceOnUse',
                                  patternTransform='rotate(45) scale(0.2, 0.2)')
    bg_concrete = draw.Rectangle(0, 0, 100, 100, fill='#a3a3a3ff', fill_opacity=0.25, stroke='none')
    concrete_hatch.append(bg_concrete)
    line1 = draw.Line(0, 0, 100, 0, stroke='#a3a3a3ff', stroke_width=10)
    line2 = draw.Line(0, 0, 0, 100, stroke='#a3a3a3ff', stroke_width=10)
    concrete_hatch.append(line1)
    concrete_hatch.append(line2)
    return concrete_hatch

import drawsvg as draw

def add_horizontal_dimension_line(drawing, x1, y, x2, offset, text_value, tick_length=5):
    """
    Adds a horizontal dimension line with extension lines, 45° tick marks, and a text label.
    
    drawing: the draw.Drawing object
    x1, y: the left endpoint on the object edge
    x2, y: the right endpoint on the object edge
    offset: vertical offset from the object edge where the dimension line is drawn
    text_value: the dimension text label (e.g., "400")
    tick_length: the half-length of the tick mark (before rotation)
    """
    # Extension lines from the object edge to the dimension line.
    ext_line1 = draw.Line(x1, y, x1, y + offset, stroke='black', stroke_width=1)
    ext_line2 = draw.Line(x2, y, x2, y + offset, stroke='black', stroke_width=1)
    drawing.append(ext_line1)
    drawing.append(ext_line2)
    
    # The dimension line.
    dim_line = draw.Line(x1, y + offset, x2, y + offset, stroke='black', stroke_width=1)
    drawing.append(dim_line)
    
    # Compute the offset for the tick marks at a 45° angle.
    # For a tick of "half-length" tick_length, the horizontal and vertical offsets are:
    delta = tick_length * math.sqrt(2) / 2

    # Left tick (centered at (x1, y+offset)).
    tick_left = draw.Line(x1 + delta, y + offset - delta,
                          x1 - delta, y + offset + delta,
                          stroke='black', stroke_width=1)
    # Right tick (centered at (x2, y+offset)).
    tick_right = draw.Line(x2 + delta, y + offset - delta,
                           x2 - delta, y + offset + delta,
                           stroke='black', stroke_width=1)
    drawing.append(tick_left)
    drawing.append(tick_right)
    
    # Place the dimension text at the midpoint.
    mid_x = (x1 + x2) / 2
    # Position text slightly above the tick marks.
    mid_y = y + offset - tick_length - 2  
    dim_text = draw.Text(text_value, 12, mid_x, mid_y, text_anchor="middle")
    drawing.append(dim_text)

def add_vertical_dimension_line(drawing, x, y1, y2, offset, text_value, tick_length=5):
    """
    Adds a vertical dimension line with extension lines, 45° tick marks, and a text label.
    
    drawing: the draw.Drawing object
    x, y1: the bottom endpoint on the object edge
    x, y2: the top endpoint on the object edge
    offset: horizontal offset from the object edge where the dimension line is drawn
    text_value: the dimension text label (e.g., "180")
    tick_length: the half-length of the tick mark (before rotation)
    """
    # Extension lines from the object edge to the dimension line.
    ext_line1 = draw.Line(x, y1, x + offset, y1, stroke='black', stroke_width=1)
    ext_line2 = draw.Line(x, y2, x + offset, y2, stroke='black', stroke_width=1)
    drawing.append(ext_line1)
    drawing.append(ext_line2)
    
    # The dimension line.
    dim_line = draw.Line(x + offset, y1, x + offset, y2, stroke='black', stroke_width=1)
    drawing.append(dim_line)
    
    # Compute the delta for a 45° tick mark.
    delta = tick_length * math.sqrt(2) / 2

    # Bottom tick (centered at (x+offset, y1)).
    tick_bottom = draw.Line(x + offset + delta, y1 - delta,
                            x + offset - delta, y1 + delta,
                            stroke='black', stroke_width=1)
    # Top tick (centered at (x+offset, y2)).
    tick_top = draw.Line(x + offset + delta, y2 - delta,
                         x + offset - delta, y2 + delta,
                         stroke='black', stroke_width=1)
    drawing.append(tick_bottom)
    drawing.append(tick_top)
    
    # Place the dimension text at the midpoint.
    mid_x = x + offset + tick_length + 2  # Slightly to the right of the ticks.
    mid_y = (y1 + y2) / 2
    # Rotate the text so it reads vertically.
    dim_text = draw.Text(text_value, 12, mid_x, mid_y, text_anchor="middle",
                         transform="rotate(90, {}, {})".format(mid_x, mid_y))
    drawing.append(dim_text)

def add_legend(drawing):
    """
    Adds a legend to the drawing. The legend includes a background box,
    a title, and legend items for the timber element and the concrete element.
    """
    # Create a group to hold all legend elements.
    legend = draw.Group(id="legend")
    
    # Define the legend background (position and size may be adjusted).
    # Here it is placed at (-245, 85) with width 100 and height 85.
    legend_bg = draw.Rectangle(-245, 85, 100, 85, fill='white', stroke='black', stroke_width=1)
    legend.append(legend_bg)
    
    # Add a legend title.
    legend_title = draw.Text("Legende", 14, -240, 100, text_anchor="start")
    legend.append(legend_title)
    
    # Legend item 1: Timber element ("Holzbalken")
    # A small rectangle filled with the timber pattern.
    timber_icon = draw.Rectangle(-240, 140, 20, 20, fill='url(#timber_lines)', stroke='black', stroke_width=1)
    legend.append(timber_icon)
    timber_text = draw.Text("Holzbalken", 12, -215, 155, text_anchor="start")
    legend.append(timber_text)
    
    # Legend item 2: Concrete element ("Betonplatte")
    # A small rectangle filled with the concrete hatch pattern.
    concrete_icon = draw.Rectangle(-240, 110, 20, 20, fill='url(#concrete_hatch)', stroke='black', stroke_width=1)
    legend.append(concrete_icon)
    concrete_text = draw.Text("Betonplatte", 12, -215, 125, text_anchor="start")
    legend.append(concrete_text)
    
    # Append the legend group to the main drawing.
    drawing.append(legend)
