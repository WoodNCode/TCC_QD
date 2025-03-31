import drawsvg as draw
import math
import streamlit as st
from graphics_defs import get_timber_pattern, get_concrete_hatch

def render_svg(svg):
    """Renders the given svg string."""
    b64 = base64.b64encode(svg.encode('utf-8')).decode("utf-8")
    html = r'<img src="data:image/svg+xml;base64,%s"/>' % b64
    st.write(html, unsafe_allow_html=True)

def draw_elevation_view_scaled(L, s):
    """
    Returns an SVG string for the Elevation View of a TCC element,
    with an automatic scale from 'meters' to an ~800×300 px canvas.
    
    Model geometry (in meters):
      - x in [0, L], beam along y=0
      - We'll allow some vertical space for the arrow above (say y=+10) and a bit below (y=-5).
    
    Shapes:
      - Beam: black line from (0,0) to (L,0)
      - Supports: tip at (0,0) and (L,0)
      - Connectors: red circles spaced along the beam
      - Arrow snippet at midspan, from (L/2, 10) down to (L/2, 0)
      - Grid lines in model space
      - Small text for labels
    """

    # -----------------------
    # 1) Define the model bounding box in real units
    x_min_model = 0
    x_max_model = L
    y_min_model = -5
    y_max_model = 15  # Enough space for arrow at y=10

    # 2) Define the final SVG size (in px) and margins (in px)
    svg_width_px = 800
    svg_height_px = 300
    margin_px = 40  # margin on each side
    
    # 3) Compute scale factors so that the entire model bounding box fits into the canvas
    #    We map [x_min_model, x_max_model] -> [margin_px, svg_width_px - margin_px]
    #        [y_min_model, y_max_model] -> [margin_px, svg_height_px - margin_px]
    model_width = x_max_model - x_min_model
    model_height = y_max_model - y_min_model
    
    usable_width_px = svg_width_px - 2*margin_px
    usable_height_px = svg_height_px - 2*margin_px
    
    scale_x = usable_width_px / model_width  if model_width  > 0 else 1
    scale_y = usable_height_px / model_height if model_height > 0 else 1

    # If you want uniform scaling (same scale for x and y), use:
    # scale = min(scale_x, scale_y)
    # scale_x, scale_y = scale, scale
    # For this example, we allow separate scale_x, scale_y to avoid distortion.

    # 4) Helper functions to map model -> SVG coords
    def sx(x):
        """Scale an x-coordinate from model to SVG."""
        return margin_px + scale_x*(x - x_min_model)
    def sy(y):
        """Scale a y-coordinate from model to SVG (note: no y-flip, y increases upward)."""
        # If you prefer standard screen coords with y down, you could invert scale_y or do a flip.
        return svg_height_px - margin_px - scale_y*(y - y_min_model)
        # Explanation: We want y= y_min_model to map near the bottom of the drawing.
        # But often we prefer an upward-positive system, so we do (svg_height_px - ...).

    # Create the Drawing with the final pixel dimensions
    d = draw.Drawing(svg_width_px, svg_height_px, origin=(0,0), displayInline=False)

    # 5) Optionally add grid lines in model space
    grid_step = 5
    for gx in range(int(math.floor(x_min_model)), int(math.ceil(x_max_model))+1, grid_step):
        d.append(draw.Line(sx(gx), sy(y_min_model),
                           sx(gx), sy(y_max_model),
                           stroke='lightgray', stroke_width=0.5))
    for gy in range(int(math.floor(y_min_model)), int(math.ceil(y_max_model))+1, grid_step):
        d.append(draw.Line(sx(x_min_model), sy(gy),
                           sx(x_max_model), sy(gy),
                           stroke='lightgray', stroke_width=0.5))

    # 6) Draw the beam (black line)
    d.append(draw.Line(sx(0), sy(0), sx(L), sy(0),
                       stroke='black', stroke_width=2))

    # 7) Supports (triangles) with tip at (x,0)
    def support_triangle_tip(x, size_model=2):
        """
        Model-based triangle: tip at (x,0), base at (x±size, size)
        We'll scale them to screen coords in the path.
        """
        tipX, tipY = sx(x), sy(0)
        leftX, leftY = sx(x - size_model), sy(size_model)
        rightX, rightY = sx(x + size_model), sy(size_model)
        return draw.Lines(tipX, tipY, leftX, leftY, rightX, rightY,
                          close=True, fill='black')
    d.append(support_triangle_tip(0))
    d.append(support_triangle_tip(L))

    # 8) Connectors (red circles) spaced along the beam
    n_conn = int(math.floor(L / s)) if s>0 else 0
    for i in range(n_conn):
        x_c = s/2 + i*s
        d.append(draw.Circle(sx(x_c), sy(0), 3, fill='red'))

    # 9) Downward arrow at midspan, using your snippet
    arrow_marker = draw.Marker(-0.1, -0.51, 0.9, 0.5, scale=4, orient='auto')
    arrow_marker.append(draw.Lines(-0.1, 0.5, -0.1, -0.5, 0.9, 0, fill='red', close=True))
    d.append(arrow_marker)

    arrow_path = draw.Path(stroke='red', stroke_width=2, fill='none', marker_end=arrow_marker)
    arrow_path.M(sx(L/2), sy(10)).L(sx(L/2), sy(0))  # vertical line in model coords
    d.append(arrow_path)

    # 10) Text (small fonts). By default, y=0 is at the top if you do standard screen coords,
    #     so we used sy(...) to keep an upward-positive approach.
    d.append(draw.Text("Elevation View of TCC Element", 10,
                       sx(x_min_model)+5, sy(y_max_model)-5, fill='black'))
    # x-label near the bottom
    d.append(draw.Text("Beam Length (m)", 8,
                       (sx(x_min_model)+sx(x_max_model))/2 - 30,
                       sy(y_min_model)+10, fill='black'))
    # y-label, rotated
    # We'll place it near x_min_model, middle in y
    label_x = sx(x_min_model) + 15
    label_y = (sy(y_min_model)+sy(y_max_model))/2
    d.append(draw.Text("Elevation", 8,
                       label_x, label_y,
                       fill='black',
                       transform=f"rotate(-90,{label_x},{label_y})"))

    return d.as_svg()

def draw_cross_section(b_concrete, h_concrete, b_timber, h_timber, a_timber=None):

    # Create the drawing canvas.
    d = draw.Drawing(800, 500, origin='center')

    # Add the timber pattern to the drawing definitions.
    timber_pattern = get_timber_pattern()
    d.append(timber_pattern)

    # Wood element (Holzbalken) using the timber pattern.
    wood_element = draw.Rectangle(-60, 0, 120, 180, stroke='black', stroke_width=2, fill='url(#timber_lines)')
    wood_element.append_title("Holzbalken")
    d.append(wood_element)

    # Add the concrete hatch pattern to the drawing definitions.
    concrete_hatch = get_concrete_hatch()
    d.append(concrete_hatch)

    # Concrete element (Betonplatte) using the hatch pattern for fill.
    concrete_element = draw.Rectangle(-200, -100, 400, 100, stroke='black', stroke_width=2, fill='url(#concrete_hatch)')
    concrete_element.append_title("Betonplatte")
    d.append(concrete_element)

    d  # Display as SVG    

    return d.as_svg()
