import drawsvg as draw

def draw_elevation_view(L, s):
    """
    Returns an SVG string for the elevation view of a TCC element, drawn 'right-side up'
    and scaled larger for visibility.
    
    Parameters:
      L (float): Beam length in "model units" (e.g., meters).
      s (float): Connector spacing (same units as L).
    """
    # 1) Define the canvas size and margins so things aren't cramped.
    margin = 50
    canvas_height = 250
    canvas_width = L + 2 * margin

    # 2) Create the drawing with origin at (0,0). We'll place the beam around y=100.
    d = draw.Drawing(canvas_width, canvas_height, origin=(0,0), displayInline=False)

    # 3) Increase the rendered size so it appears bigger.
    #    (You can tweak this scale factor as needed.)
    d.set_pixel_scale(2)

    # We'll place the beam at y=100, from x=margin to x=margin+L
    beam_y = 100

    # Draw the beam (a horizontal line)
    d.append(draw.Line(margin, beam_y, margin + L, beam_y,
                       stroke='black', stroke_width=3))

    # Upward-pointing support triangles at beam ends
    def support_triangle(cx, cy, size):
        """
        An upward triangle with centroid near (cx,cy).
        Tip is above (cx,cy); base is below.
        """
        return draw.Lines(
            cx,     cy + 2*size/3,    # tip (top)
            cx - size, cy - size/3,   # left base
            cx + size, cy - size/3,   # right base
            close=True,
            fill='black'
        )

    support_size = 8
    d.append(support_triangle(margin,     beam_y, support_size))
    d.append(support_triangle(margin + L, beam_y, support_size))

    # Connectors (red circles) spaced along the beam
    n_connectors = int(L // s)
    for i in range(n_connectors):
        x_pos = margin + s/2 + i*s
        d.append(draw.Circle(x_pos, beam_y, 4, fill='red'))

    # Draw the downward load arrow in BLUE.
    # We'll create a marker for the arrow tip.
    arrow_marker = draw.Marker(-0.5, -1, 0.5, 0, scale=4, orient='auto', id='down_arrow')
    # A simple triangular arrow shape with tip at (0,0) and base around (±0.4, -0.8).
    arrow_marker.append(draw.Lines(0,0, 0.4,-0.8, -0.4,-0.8, close=True, fill='blue'))
    d.append(arrow_marker)

    # Vertical line for the load from y=beam_y+30 down to y=beam_y
    load_x = margin + L/2
    load_line = draw.Line(load_x, beam_y + 30, load_x, beam_y,
                          stroke='blue', stroke_width=3,
                          marker_end=arrow_marker)
    d.append(load_line)

    # Some text
    d.append(draw.Text("Elevation View of TCC Element", 14,
                       margin, canvas_height - 20,
                       fill='black'))
    d.append(draw.Text("Beam Length (m)", 12,
                       canvas_width/2 - 40, 30,
                       fill='black'))
    # Rotate the Y-axis label 90° around its anchor
    d.append(draw.Text("Elevation", 12,
                       20, canvas_height/2,
                       fill='black',
                       transform=f"rotate(-90,20,{canvas_height/2})"))

    # (No grid lines, as requested — if you want them, add them later.)

    return d.as_svg()
def draw_cross_section(b_concrete, h_concrete, b_timber, h_timber, a_timber=None):
    """
    Returns an SVG string for the cross-section view of a TCC element.
    
    Model coordinates:
      - Concrete slab from x in [-b_concrete/2, b_concrete/2], y in [0, h_concrete].
      - Timber beam from x in [-b_timber/2, b_timber/2], y in [-h_timber, 0].
      - A connector (red circle) at (0, 0).
      - Neutral axis (if a_timber) at y = -h_timber/2 + a_timber.
    """
    # 1) Canvas size and margins
    margin = 50
    canvas_width = b_concrete + 2*margin
    canvas_height = h_concrete + h_timber + 2*margin

    d = draw.Drawing(canvas_width, canvas_height, origin=(0,0), displayInline=False)
    d.set_pixel_scale(2)  # Make the rendering bigger

    # 2) We want the "interface" (y=0) somewhere in the middle. We'll define an offset:
    #    offset_x = margin - ( -b_concrete/2 ) = margin + b_concrete/2
    #    offset_y = margin - ( -h_timber ) = margin + h_timber
    offset_x = margin + b_concrete/2
    offset_y = margin + h_timber

    # Draw the concrete slab
    #  bottom-left at ( -b_concrete/2, 0 )
    #  top-right   at ( +b_concrete/2, h_concrete )
    # in the final drawing, that means:
    slab_x = offset_x - b_concrete/2
    slab_y = offset_y + 0
    d.append(draw.Rectangle(slab_x, slab_y,
                            b_concrete, h_concrete,
                            fill='gray', fill_opacity=0.7))

    # Draw the timber beam
    #  bottom-left at ( -b_timber/2, -h_timber )
    #  top-right   at ( +b_timber/2, 0 )
    beam_x = offset_x - b_timber/2
    beam_y = offset_y - h_timber
    d.append(draw.Rectangle(beam_x, beam_y,
                            b_timber, h_timber,
                            fill='saddlebrown', fill_opacity=0.7))

    # Connector at (0,0)
    d.append(draw.Circle(offset_x + 0, offset_y + 0, 5, fill='red'))

    # Dashed line at y=0
    d.append(draw.Line(offset_x - b_concrete/2, offset_y,
                       offset_x + b_concrete/2, offset_y,
                       stroke='black', stroke_width=2,
                       stroke_dasharray="5,5"))

    # Neutral axis if provided
    if a_timber is not None:
        na_y = -h_timber/2 + a_timber
        d.append(draw.Line(offset_x - b_concrete/2, offset_y + na_y,
                           offset_x + b_concrete/2, offset_y + na_y,
                           stroke='blue', stroke_width=3))

    # Some text
    d.append(draw.Text("Cross-section of TCC Element", 14,
                       slab_x, slab_y + h_concrete + 30,
                       fill='black'))
    d.append(draw.Text("Width (m)", 12,
                       canvas_width/2 - 40, margin - 20,
                       fill='black'))
    d.append(draw.Text("Height (m)", 12,
                       slab_x - 40, (beam_y + h_concrete)/2,
                       fill='black',
                       transform=f"rotate(-90,{slab_x - 40},{(beam_y + h_concrete)/2})"))

    # No grid lines (commented out)
    # ...

    return d.as_svg()
