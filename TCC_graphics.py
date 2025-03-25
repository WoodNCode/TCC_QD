import drawsvg as draw

def draw_elevation_view(L, s):
    """
    Returns an SVG string showing the elevation view of a TCC element.

    - The beam runs horizontally at y=150, from x=100 to x=100+L.
    - Supports (triangles) have their tip at the beam line, base below.
    - Connectors (red circles) are spaced along the beam.
    - A downward arrow is attached at the midspan, from y=130 to y=150.
    - Font sizes are small (~3) to avoid oversized text.
    """
    # 1) Define canvas size
    canvas_width = L + 300  # some extra space
    canvas_height = 300
    d = draw.Drawing(canvas_width, canvas_height, origin=(0, 0), displayInline=False)
    
    # 2) Beam coordinates
    beam_y = 150
    beam_left = 100
    beam_right = beam_left + L
    
    # 3) Draw the beam (horizontal line)
    d.append(draw.Line(beam_left, beam_y, beam_right, beam_y,
                       stroke='black', stroke_width=2))
    
    # 4) Supports with tip at the beam
    #    Tip at (cx, cy), base at (cx±size, cy+size)
    def support_triangle_tip(cx, cy, size):
        return draw.Lines(
            cx,   cy,         # tip at the beam
            cx - size, cy + size,  # left base
            cx + size, cy + size,  # right base
            close=True, fill='black'
        )
    support_size = 6
    d.append(support_triangle_tip(beam_left,  beam_y, support_size))
    d.append(support_triangle_tip(beam_right, beam_y, support_size))
    
    # 5) Connectors (red circles) along the beam
    n_conn = int(L // s)
    for i in range(n_conn):
        x = beam_left + s/2 + i*s
        d.append(draw.Circle(x, beam_y, 3, fill='red'))
    
    # 6) Downward arrow using the user’s snippet
    arrow = draw.Marker(-0.1, -0.51, 0.9, 0.5, scale=4, orient='auto')
    arrow.append(draw.Lines(-0.1, 0.5, -0.1, -0.5, 0.9, 0, fill='blue', close=True))
    d.append(arrow)
    
    # Create a vertical path from y=130 down to y=150 so the arrow points downward
    p = draw.Path(stroke='blue', stroke_width=2, fill='none', marker_end=arrow)
    p.M(beam_left + L/2, beam_y - 20).L(beam_left + L/2, beam_y)
    d.append(p)
    
    # 7) Small text (font size ~3)
    d.append(draw.Text("Elevation View of TCC Element", 3, 10, 20, fill='black'))
    d.append(draw.Text("Beam Length (m)", 3, canvas_width/2, canvas_height - 5, fill='black'))
    # Rotate the Y-axis label
    d.append(draw.Text("Elevation", 3, 20, canvas_height/2,
                       fill='black',
                       transform=f"rotate(-90,20,{canvas_height/2})"))
    
    return d.as_svg()

def draw_cross_section(b_concrete, h_concrete, b_timber, h_timber, a_timber=None):
    """
    Returns an SVG string for the cross-section of a TCC element.

    - Concrete slab: x from (cx - b_concrete/2) to (cx + b_concrete/2),
                     y from top_sl to top_sl + h_concrete.
    - Timber beam:   x from (cx - b_timber/2) to (cx + b_timber/2),
                     y from top_sl + h_concrete to top_sl + h_concrete + h_timber.
    - Connector (red circle) at the slab/beam interface (center).
    - Neutral axis if 'a_timber' is given, at y= interface + ( -h_timber/2 + a_timber ).
    - Font sizes are small (~3).
    """
    canvas_width = max(b_concrete, b_timber) + 200
    canvas_height = h_concrete + h_timber + 150
    d = draw.Drawing(canvas_width, canvas_height, origin=(0, 0), displayInline=False)
    
    # We'll center x=0 at the midpoint
    cx = canvas_width / 2
    # Let the slab top start at y=50
    slab_top = 50
    
    # Concrete slab
    slab_left = cx - b_concrete/2
    slab_width = b_concrete
    d.append(draw.Rectangle(slab_left, slab_top, slab_width, h_concrete,
                            fill='gray', fill_opacity=0.7))
    
    # Timber beam just below
    beam_top = slab_top + h_concrete
    beam_left = cx - b_timber/2
    d.append(draw.Rectangle(beam_left, beam_top, b_timber, h_timber,
                            fill='saddlebrown', fill_opacity=0.7))
    
    # Connector at interface
    interface_y = slab_top + h_concrete
    d.append(draw.Circle(cx, interface_y, 4, fill='red'))
    
    # Dashed line at interface
    d.append(draw.Line(slab_left, interface_y, slab_left + slab_width, interface_y,
                       stroke='black', stroke_width=2, stroke_dasharray="5,5"))
    
    # Neutral axis if provided
    if a_timber is not None:
        na_y = interface_y + (-h_timber/2 + a_timber)
        d.append(draw.Line(slab_left, na_y, slab_left + slab_width, na_y,
                           stroke='blue', stroke_width=2))
    
    # Text (small fonts)
    d.append(draw.Text("Cross-section of TCC Element", 3, 10, 20, fill='black'))
    d.append(draw.Text("Width (m)", 3, canvas_width/2, canvas_height - 10, fill='black'))
    d.append(draw.Text("Height (m)", 3, 20, canvas_height/2,
                       fill='black',
                       transform=f"rotate(-90,20,{canvas_height/2})"))
    
    return d.as_svg()
