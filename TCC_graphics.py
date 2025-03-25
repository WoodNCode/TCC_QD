import drawsvg as draw

def draw_elevation_view(L, s):
    """
    Returns an SVG string for the elevation view of a TCC element,
    with everything placed at clear coordinates (no flipping).
    
    Parameters:
      L (float): Beam length (e.g., meters).
      s (float): Connector spacing.
    """
    # Canvas size: a bit wider than L, and tall enough for text/arrow.
    canvas_width = L + 100
    canvas_height = 200

    d = draw.Drawing(canvas_width, canvas_height, origin=(0,0), displayInline=False)
    # Force a larger rendered size so it appears bigger in Streamlit.
    d.set_render_size(1200, 300)

    # We'll place the beam horizontally at y=100, from x=50 to x=50+L.
    beam_y = 100
    beam_left = 50
    beam_right = beam_left + L

    # 1) Beam line
    d.append(draw.Line(beam_left, beam_y, beam_right, beam_y,
                       stroke='black', stroke_width=3))

    # 2) Supports as upward-pointing triangles at the beam ends
    def support_triangle(cx, cy, size):
        # Tip at (cx, cy+size), base corners at (cx±size, cy-size)
        return draw.Lines(cx,   cy + size,
                          cx - size, cy - size,
                          cx + size, cy - size,
                          close=True, fill='black')
    support_size = 8
    d.append(support_triangle(beam_left,  beam_y, support_size))
    d.append(support_triangle(beam_right, beam_y, support_size))

    # 3) Connectors (red circles) spaced along the beam
    n_conn = int(L // s)
    for i in range(n_conn):
        x = beam_left + s/2 + i*s
        d.append(draw.Circle(x, beam_y, 4, fill='red'))

    # 4) Downward-pointing load arrow
    arrow_marker = draw.Marker(-0.5, -1, 0.5, 0, scale=4, orient='auto', id='down_arrow')
    # Tip at (0,0); base around (±0.4, -0.8).
    arrow_marker.append(draw.Lines(0,0, 0.4,-0.8, -0.4,-0.8, close=True, fill='blue'))
    d.append(arrow_marker)

    # A vertical line from y=beam_y+30 down to y=beam_y
    load_x = beam_left + L/2
    arrow_line = draw.Line(load_x, beam_y+30, load_x, beam_y,
                           stroke='blue', stroke_width=3,
                           marker_end=arrow_marker)
    d.append(arrow_line)

    # 5) Text
    d.append(draw.Text("Elevation View of TCC Element", 14,
                       10, canvas_height-10, fill='black'))
    d.append(draw.Text("Beam Length (m)", 12,
                       canvas_width/2, 20, fill='black'))
    d.append(draw.Text("Elevation", 12,
                       10, canvas_height/2, fill='black',
                       transform=f"rotate(-90,10,{canvas_height/2})"))

    return d.as_svg()
def draw_cross_section(b_concrete, h_concrete, b_timber, h_timber, a_timber=None):
    """
    Returns an SVG string for the cross-section of a TCC element,
    with all parts placed at explicit coordinates (no flipping).
    
    Model:
      - Concrete slab: x in [ -b_concrete/2, +b_concrete/2 ],
                       y in [ 0, h_concrete ].
      - Timber beam:   x in [ -b_timber/2,   +b_timber/2   ],
                       y in [ -h_timber, 0 ].
      - Connector: red circle at (0,0).
      - Neutral axis (if a_timber): at y = -h_timber/2 + a_timber.
    """
    # Canvas wide enough for the concrete width, tall enough for total height.
    canvas_width = max(b_concrete, b_timber) + 100
    canvas_height = h_concrete + h_timber + 100

    d = draw.Drawing(canvas_width, canvas_height, origin=(0,0), displayInline=False)
    # Make it larger so it displays clearly in Streamlit.
    d.set_render_size(800, 600)

    # We'll place the interface y=0 at y= h_timber+50 (some offset).
    interface_y = h_timber + 50
    # We'll center x=0 in the middle of the canvas.
    center_x = canvas_width/2

    # 1) Concrete slab: from (center_x - b_concrete/2, interface_y)
    #                   up to   (center_x + b_concrete/2, interface_y + h_concrete)
    slab_x = center_x - b_concrete/2
    slab_y = interface_y
    d.append(draw.Rectangle(slab_x, slab_y,
                            b_concrete, h_concrete,
                            fill='gray', fill_opacity=0.7))

    # 2) Timber beam: from (center_x - b_timber/2, interface_y - h_timber)
    #                 up to   (center_x + b_timber/2, interface_y)
    beam_x = center_x - b_timber/2
    beam_y = interface_y - h_timber
    d.append(draw.Rectangle(beam_x, beam_y,
                            b_timber, h_timber,
                            fill='saddlebrown', fill_opacity=0.7))

    # 3) Connector at (0,0) → (center_x, interface_y)
    d.append(draw.Circle(center_x, interface_y, 5, fill='red'))

    # 4) Dashed line at y=0
    d.append(draw.Line(center_x - b_concrete/2, interface_y,
                       center_x + b_concrete/2, interface_y,
                       stroke='black', stroke_width=2,
                       stroke_dasharray="5,5"))

    # 5) Neutral axis (if given)
    if a_timber is not None:
        na_y = interface_y - h_timber/2 + a_timber
        d.append(draw.Line(center_x - b_concrete/2, na_y,
                           center_x + b_concrete/2, na_y,
                           stroke='blue', stroke_width=3))

    # 6) Text
    d.append(draw.Text("Cross-section of TCC Element", 14,
                       10, canvas_height-10, fill='black'))
    d.append(draw.Text("Width (m)", 12,
                       canvas_width/2, 30, fill='black'))
    d.append(draw.Text("Height (m)", 12,
                       30, canvas_height/2, fill='black',
                       transform=f"rotate(-90,30,{canvas_height/2})"))

    return d.as_svg()
