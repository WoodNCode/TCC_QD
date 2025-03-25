import drawsvg as draw
import math

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

def draw_cross_section_scaled(b_concrete, h_concrete, b_timber, h_timber, a_timber=None):
    """
    Returns an SVG string for the Cross-section view of a TCC element,
    automatically scaled to ~800×400 px.

    Model geometry:
      - Concrete slab: x in [-b_concrete/2, +b_concrete/2], y in [0, h_concrete]
      - Timber beam:   x in [-b_timber/2,   +b_timber/2],   y in [-h_timber, 0]
      - Connector at (0,0)
      - Dashed line at y=0
      - If a_timber: neutral axis at y=(-h_timber/2 + a_timber)
      - We add ~10 m of margin in model coords around x & y.
    """
    import math

    # 1) Model bounding box
    x_left  = -max(b_concrete/2, b_timber/2) - 10
    x_right = +max(b_concrete/2, b_timber/2) + 10
    y_bottom = -h_timber - 10
    y_top    = h_concrete + 10

    # 2) SVG size, margins
    svg_width_px = 800
    svg_height_px = 400
    margin_px = 50

    model_width = x_right - x_left
    model_height = y_top - y_bottom

    usable_w = svg_width_px - 2*margin_px
    usable_h = svg_height_px - 2*margin_px

    scale_x = usable_w / model_width   if model_width>0   else 1
    scale_y = usable_h / model_height if model_height>0   else 1
    # If you want uniform scale, do scale = min(scale_x, scale_y).

    def sx(x):
        """Map model x to SVG x (y-up)."""
        return margin_px + scale_x*(x - x_left)
    def sy(y):
        """Map model y to SVG y (y-up)."""
        return svg_height_px - margin_px - scale_y*(y - y_bottom)

    d = draw.Drawing(svg_width_px, svg_height_px, origin=(0,0), displayInline=False)

    # 3) Grid lines
    step = 5
    for gx in range(int(math.floor(x_left)), int(math.ceil(x_right))+1, step):
        d.append(draw.Line(sx(gx), sy(y_bottom),
                           sx(gx), sy(y_top),
                           stroke='lightgray', stroke_width=0.5))
    for gy in range(int(math.floor(y_bottom)), int(math.ceil(y_top))+1, step):
        d.append(draw.Line(sx(x_left), sy(gy),
                           sx(x_right), sy(gy),
                           stroke='lightgray', stroke_width=0.5))

    # 4) Concrete slab
    #    x from [-b_concrete/2, +b_concrete/2], y from [0, h_concrete]
    slab_left = -b_concrete/2
    slab_bottom = 0
    d.append(draw.Rectangle(sx(slab_left), sy(slab_bottom),
                            scale_x*b_concrete, scale_y*h_concrete,
                            fill='gray', fill_opacity=0.7))

    # 5) Timber beam
    #    x from [-b_timber/2, +b_timber/2], y from [-h_timber, 0]
    beam_left = -b_timber/2
    beam_bottom = -h_timber
    d.append(draw.Rectangle(sx(beam_left), sy(beam_bottom),
                            scale_x*b_timber, scale_y*h_timber,
                            fill='saddlebrown', fill_opacity=0.7))

    # 6) Connector at (0,0)
    d.append(draw.Circle(sx(0), sy(0), 4, fill='red'))

    # 7) Dashed line at y=0
    d.append(draw.Line(sx(x_left), sy(0),
                       sx(x_right), sy(0),
                       stroke='black', stroke_width=2, stroke_dasharray="4,2"))

    # 8) Neutral axis if provided
    if a_timber is not None:
        na_y = -h_timber/2 + a_timber
        d.append(draw.Line(sx(x_left), sy(na_y),
                           sx(x_right), sy(na_y),
                           stroke='blue', stroke_width=2))

    # 9) Text
    d.append(draw.Text("Cross-section of TCC Element", 10,
                       sx(x_left)+5, sy(y_top)-5, fill='black'))
    # x-label near the bottom
    d.append(draw.Text("Width (m)", 8,
                       (sx(x_left)+sx(x_right))/2 - 30,
                       sy(y_bottom)+15,
                       fill='black'))
    # y-label, rotated
    lx = sx(x_left)+15
    ly = (sy(y_bottom)+sy(y_top))/2
    d.append(draw.Text("Height (m)", 8, lx, ly, fill='black',
                       transform=f"rotate(-90,{lx},{ly})"))

    return d.as_svg()
