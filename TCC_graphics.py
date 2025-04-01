import drawsvg as draw
import math
import streamlit as st
import numpy as np
from graphics_defs import get_timber_pattern, get_concrete_hatch, add_horizontal_dimension_line, add_vertical_dimension_line,  add_legend

def render_svg(svg):
    """Renders the given svg string."""
    b64 = base64.b64encode(svg.encode('utf-8')).decode("utf-8")
    html = r'<img src="data:image/svg+xml;base64,%s"/>' % b64
    st.write(html, unsafe_allow_html=True)

def create_elevation_view(L, s, P):
    """
    Creates an elevation view of a beam with:
      - A horizontal beam line from x=0 to x=L at a fixed y level.
      - A pinned support at the left end and a roller support at the right end.
      - A downward load arrow at mid-span (with its reference on the beam line).
      - Connector markers along the beam at spacing s.
      
    Parameters:
      L : float
          Total beam length.
      s : float
          Spacing for connectors.
      P : number
          Load value to display (e.g., in kN or N).
    
    Returns:
      A drawsvg.Drawing object.
    scale = at the moment fixed scale to make the elevation view fit the width.
    """
    scale = 1000/3
    # Define canvas size and beam level.
    canvas_width = L*scale + 100    # extra margin on right
    canvas_height = 150       # enough space above and below the beam
    beam_y = 100              # y-coordinate of the beam (the beam line)
    
    d = draw.Drawing(canvas_width, canvas_height, origin=(0,0))
    
    # Draw the beam: horizontal line from x=0 to x=L.
    beam_line = draw.Line(50, beam_y, 50+ L*scale, beam_y, stroke='black', stroke_width=2)
    d.append(beam_line)
    
    # Draw connector markers along the beam.
    n_connectors = int(L / s)
    if n_connectors < 1:
        n_connectors = 1
    connector_positions = np.linspace(s*scale/2, L*scale - s*scale/2, n_connectors)
    for x in connector_positions:
        connector = draw.Circle(50+x, beam_y, 3, fill='red', stroke='none')
        d.append(connector)
    
    # Draw supports.
    # Left support (Pinned): Draw a triangle with its top vertex on the beam.
    left_support = draw.Lines(
        50, beam_y,
        50-10, beam_y + 20,
        50+10, beam_y + 20,
        close=True,
        fill='gray',
        stroke='black',
        stroke_width=1
    )
    d.append(left_support)
    
    # Right support (Roller): Triangle with its top vertex on the beam.
    right_support = draw.Lines(
        50+L*scale, beam_y,
        50+L*scale - 10, beam_y + 20,
        50+L*scale + 10, beam_y + 20,
        close=True,
        fill='gray',
        stroke='black',
        stroke_width=1
    )
    d.append(right_support)
    # Add a Line below the right support to depict the roller.
    roller = draw.Line(50+L*scale-10, beam_y + 25, 50+L*scale+10, beam_y + 25, fill='gray', stroke='black', stroke_width=1)
    d.append(roller)
    
    # Create a downward arrow marker for the load.
    arrow_down = draw.Marker(0, 0, 10, 10, id='arrow_down', markerUnits='strokeWidth',
                             markerWidth=10, markerHeight=10, refX=5, refY=8, orient="down")
    arrow_down_path = draw.Path("M 0 0 L 10 0 L 5 8 Z", fill='black')
    arrow_down.append(arrow_down_path)
    d.append(arrow_down)
    
    # Draw the load arrow at mid-span.
    # The arrow starts on the beam and points downward.
    load_arrow = draw.Line(50+L*scale/2, beam_y - P, 50+L*scale/2, beam_y, stroke='black', stroke_width=2,
                           marker_end='url(#arrow_down)')
    d.append(load_arrow)
    
    # Add a load label near the arrow.
    # The label is drawn just below the beam (adjust as needed).
    load_label = draw.Text(f"{P} kN", 12, 50+L*scale/2, beam_y - P, text_anchor="middle")
    d.append(load_label)
    
    return d.as_svg()

def draw_cross_section(b_concrete, h_concrete, b_timber, h_timber, a_timber=None):

    # Create the drawing canvas.
    d = draw.Drawing(800, 500, origin='center')

    # Add the timber pattern to the drawing definitions.
    timber_pattern = get_timber_pattern()
    d.append(timber_pattern)

    # Wood element (Holzbalken) using the timber pattern.
    wood_element = draw.Rectangle(-b_timber*1000/2, 0, b_timber*1000, h_timber*1000, stroke='black', stroke_width=2, fill='url(#timber_lines)')
    wood_element.append_title("Holzbalken")
    d.append(wood_element)

    # Add the concrete hatch pattern to the drawing definitions.
    concrete_hatch = get_concrete_hatch()
    d.append(concrete_hatch)

    # Concrete element (Betonplatte) using the hatch pattern for fill.
    concrete_element = draw.Rectangle(-b_concrete*1000/2, -h_concrete*1000, b_concrete*1000, h_concrete*1000, stroke='black', stroke_width=2, fill='url(#concrete_hatch)')
    concrete_element.append_title("Betonplatte")
    d.append(concrete_element)

    if a_timber:
        neutral_y = h_timber/2*1000-a_timber*1000
        neutral_line = draw.Line(-100, neutral_y, 100, neutral_y, 
                           stroke='red', stroke_width=1, stroke_dasharray="5,2,1,2")
        d.append(neutral_line)
        neutral_label = draw.Text("Neutralachse", 12, 0, neutral_y - 5,
                              text_anchor="middle", fill="red")
        d.append(neutral_label)

    # Add dimension lines.
    add_horizontal_dimension_line(d, -b_concrete/2*1000, -h_concrete*1000, b_concrete/2*1000, -20, f"{b_concrete * 1000:.0f} mm")
    add_horizontal_dimension_line(d, -b_timber/2*1000, h_timber*1000, b_timber/2*1000, 20, f"{b_timber * 1000:.0f} mm")
    add_vertical_dimension_line(d, -b_timber/2*1000, -0, h_timber*1000, -20, f"{h_timber * 1000:.0f} mm")
    add_vertical_dimension_line(d, -b_concrete/2*1000, -h_concrete*1000, 0, -20, f"{h_concrete * 1000:.0f} mm")
    
    add_legend(d)   

    return d.as_svg()
