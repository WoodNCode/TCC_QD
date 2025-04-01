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
        - A horizontal beam line from x=0 to x=L (scaled and offset via a group).
        - A pinned support at the left end and a roller support at the right end.
        - A downward load arrow at mid-span (with its reference on the beam line).
        - Connector markers along the beam at spacing s.
        - A dimension line below the beam indicating its length.
        
        Parameters:
        L : float
            Total beam length.
        s : float
            Spacing for connectors.
        P : number
            Load value to display (e.g., in kN or N).
        
        Returns:
        A string containing the SVG markup.
    """

    # Scale factor applied only to x-coordinates.
    scale = 600 / L

    # Define canvas size.
    # We add 50 for the left offset and extra margin on the right.
    canvas_width = L * scale + 50 + 50  
    canvas_height = 150       
    beam_y = 100  # y-coordinate of the beam (the beam line)
    offset_x = (canvas_width - L * scale) / 2
    offset_y = 0

    # Create the drawing.
    d = draw.Drawing(canvas_width, canvas_height, origin=(0, 0))
    # Create a group with a translation for centering.
    g = draw.Group(transform=f"translate({offset_x},{offset_y})")

    # Draw the beam as a horizontal solid line from x=0 to x=L*scale.
    beam_line = draw.Line(0, beam_y, L * scale, beam_y, stroke='black', stroke_width=2)
    g.append(beam_line)
    # Draw a dashed line 3 units below the beam.
    dashed_line = draw.Line(0, beam_y + 3, L * scale, beam_y + 3,
                            stroke='black', stroke_width=0.5,
                            stroke_dasharray="6,3")
    g.append(dashed_line)

    # Draw connector markers along the beam.
    n_connectors = int(L / s)
    if n_connectors < 1:
        n_connectors = 1
    connector_positions = np.linspace(s * scale / 2, L * scale - s * scale / 2, n_connectors)
    for x in connector_positions:
        connector = draw.Circle(x, beam_y, 3, fill='red', stroke='none')
        g.append(connector)

    # Draw supports.
    # Left support (Pinned): triangle with its top vertex on the beam.
    left_support = draw.Lines(
        0, beam_y,           # top vertex on the beam
        -10, beam_y + 20,    # left bottom
        10, beam_y + 20,     # right bottom
        close=True,
        fill='gray',
        stroke='black',
        stroke_width=1
    )
    g.append(left_support)

    # Right support (Roller): triangle with its top vertex on the beam.
    right_support = draw.Lines(
        L * scale, beam_y,              # top vertex on the beam
        L * scale - 10, beam_y + 20,      # left bottom
        L * scale + 10, beam_y + 20,      # right bottom
        close=True,
        fill='gray',
        stroke='black',
        stroke_width=1
    )
    g.append(right_support)
    # Draw a line below the right support to depict the roller.
    roller = draw.Line(L * scale - 10, beam_y + 25, L * scale + 10, beam_y + 25,
                       stroke='black', stroke_width=1)
    g.append(roller)

    # Create a downward arrow marker for the load.
    arrow_down = draw.Marker(0, 0, 6, 8, id='arrow_down', markerUnits='strokeWidth',
                             markerWidth=6, markerHeight=8, refX=3, refY=8, orient="down")
    arrow_down_path = draw.Path("M 0 0 L 6 0 L 3 8 Z", fill='black')
    arrow_down.append(arrow_down_path)
    d.append(arrow_down)

    # Draw the load arrow at mid-span.
    load_arrow = draw.Line(L * scale / 2, beam_y - P, L * scale / 2, beam_y,
                           stroke='black', stroke_width=2, marker_end='url(#arrow_down)')
    g.append(load_arrow)

    # Add a load label near the arrow (positioned at mid-span).
    load_label = draw.Text(f"{P} kN", 12, L * scale / 2, beam_y - P, text_anchor="middle")
    g.append(load_label)

    # Add a dimension line below the beam.
    # Using the helper function from graphics_defs to draw a horizontal dimension line.
    # Here, x1=0 and x2=L*scale are the beam endpoints and offset=20 places the line below.
    add_horizontal_dimension_line(g, 0, beam_y, L * scale, 50, f"{L:.2f} m")

    # Append the group (with all elevation elements) to the drawing.
    d.append(g)
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
    # box = draw.Rectangle(-400, -250, 800, 500, fill='none', stroke='black', stroke_width=1)
    # d.append(box)
    return d.as_svg()
