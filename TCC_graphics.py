import drawsvg as draw

def draw_elevation_view(L, s, show_legend=False):
    """
    Returns an SVG string for the Elevation View of a TCC element,
    matching the geometry from the Matplotlib example:
      • Beam from x=0 to x=L at y=0
      • A downward arrow at x=L/2, y=0 (instead of a blue dot)
      • Supports at x=0 and x=L, with the tip exactly at y=0
      • Red connectors spaced along the beam
      • Axes labels, title, grid lines
      • (Optional) a simple text-based 'legend' if show_legend=True
    """
    # ----------------------
    # 1) Define the drawing’s coordinate range
    #    We’ll allow a small margin on left/right, plus room above/below for arrow, grid, etc.
    x_min = -10
    x_max = L + 10
    y_min = -10
    y_max = 30  # Enough space for the arrow above the beam

    width = x_max - x_min
    height = y_max - y_min

    # Create the drawing; origin=(x_min, y_min) so we can place items at their real coordinates
    d = draw.Drawing(width, height, origin=(x_min, y_min), displayInline=False)
    # Make it larger on screen so it’s readable
    d.set_render_size(800, 200)  

    # ----------------------
    # 2) Draw a grid (like plt.grid())
    #    Step size is arbitrary; adjust as you wish.
    grid_step = 5
    for gx in range(int(x_min), int(x_max+1), grid_step):
        d.append(draw.Line(gx, y_min, gx, y_max, stroke='lightgray', stroke_width=0.5))
    for gy in range(int(y_min), int(y_max+1), grid_step):
        d.append(draw.Line(x_min, gy, x_max, gy, stroke='lightgray', stroke_width=0.5))

    # ----------------------
    # 3) Draw the beam: a black line from (0,0) to (L,0)
    d.append(draw.Line(0, 0, L, 0, stroke='black', stroke_width=2))

    # ----------------------
    # 4) Supports as triangles with tip at the beam coordinate
    #    Tip at (x,0), base at (x ± size, size)
    def support_triangle_tip(x, size=3):
        return draw.Lines(
            x, 0,            # tip
            x - size, size,  # left base
            x + size, size,  # right base
            close=True,
            fill='black'
        )
    d.append(support_triangle_tip(0))     # left support at x=0
    d.append(support_triangle_tip(L))     # right support at x=L

    # ----------------------
    # 5) Connectors: red circles spaced from s/2 to L - s/2
    import math
    n_conn = int(math.floor(L / s))
    for i in range(n_conn):
        cx = s/2 + i*s
        d.append(draw.Circle(cx, 0, 1.5, fill='red'))

    # ----------------------
    # 6) Downward arrow at midspan using your snippet
    #    Instead of a blue dot, we show an arrow from y=10 down to y=0 at x=L/2
    arrow_marker = draw.Marker(-0.1, -0.51, 0.9, 0.5, scale=4, orient='auto')
    arrow_marker.append(draw.Lines(-0.1, 0.5, -0.1, -0.5, 0.9, 0, fill='red', close=True))
    d.append(arrow_marker)

    arrow_path = draw.Path(stroke='red', stroke_width=2, fill='none', marker_end=arrow_marker)
    arrow_path.M(L/2, 10).L(L/2, 0)  # vertical line
    d.append(arrow_path)

    # ----------------------
    # 7) Labels: Title, x-label, y-label, all at small font size ~3
    #    (like your “figsize=(8,2)” but scaled to an SVG coordinate space)
    d.append(draw.Text("Elevation View of TCC Element", 3, x_min+2, y_max-3, fill='black'))
    # X-axis label near the bottom center
    d.append(draw.Text("Beam Length (m)", 3, (x_min + x_max)/2 - 20, y_min+3, fill='black'))
    # Y-axis label, rotated
    d.append(draw.Text("Elevation", 3, x_min+5, (y_min+y_max)/2, fill='black',
                       transform=f"rotate(-90,{x_min+5},{(y_min+y_max)/2})"))

    # ----------------------
    # 8) (Optional) “Legend”
    if show_legend:
        # A quick textual legend example, near top-left
        lx, ly = x_min+5, y_max-10
        d.append(draw.Text("Legend:", 3, lx, ly, fill='black'))
        # Next line: "Beam" with black line
        d.append(draw.Line(lx, ly-5, lx+10, ly-5, stroke='black', stroke_width=2))
        d.append(draw.Text("Beam", 3, lx+15, ly-2, fill='black'))
        # Next line: "Support" with black triangle
        tri = support_triangle_tip(lx+5, size=3)
        d.append(tri)
        d.append(draw.Text("Support", 3, lx+15, ly-8, fill='black'))
        # etc. You can add arrow/connectors similarly

    return d.as_svg()
    
def draw_cross_section(b_concrete, h_concrete, b_timber, h_timber, a_timber=None, show_legend=False):
    """
    Returns an SVG string for the Cross-section view of a TCC element,
    matching the geometry from the Matplotlib example:
      • Concrete slab from x in [-b_concrete/2, +b_concrete/2], y in [0, h_concrete]
      • Timber beam from x in [-b_timber/2, +b_timber/2], y in [-h_timber, 0]
      • Red connector at (0,0)
      • Dashed line at y=0
      • If a_timber is given, a line at y=-h_timber/2 + a_timber
      • Axes labels, title, grid
      • (Optional) a simple text-based 'legend'
    """
    # ----------------------
    # 1) Define coordinate extents
    x_min = -max(b_concrete/2, b_timber/2) - 10
    x_max = +max(b_concrete/2, b_timber/2) + 10
    y_min = -h_timber - 10
    y_max = h_concrete + 10

    width = x_max - x_min
    height = y_max - y_min

    d = draw.Drawing(width, height, origin=(x_min, y_min), displayInline=False)
    # Make it larger on screen so it’s readable
    d.set_render_size(600, 400)

    # ----------------------
    # 2) Grid lines
    grid_step_x = 5
    grid_step_y = 5
    import math
    for gx in range(int(math.floor(x_min)), int(math.ceil(x_max))+1, grid_step_x):
        d.append(draw.Line(gx, y_min, gx, y_max, stroke='lightgray', stroke_width=0.5))
    for gy in range(int(math.floor(y_min)), int(math.ceil(y_max))+1, grid_step_y):
        d.append(draw.Line(x_min, gy, x_max, gy, stroke='lightgray', stroke_width=0.5))

    # ----------------------
    # 3) Concrete slab
    #    x from [-b_concrete/2, +b_concrete/2], y from [0, h_concrete]
    slab_left = -b_concrete/2
    slab_right = +b_concrete/2
    # We'll create a rectangle shape via fill_between approach:
    # Using draw.Path or draw.Rectangle is simpler:
    # rectangle at (slab_left, 0) with width=b_concrete, height=h_concrete
    d.append(draw.Rectangle(slab_left, 0, b_concrete, h_concrete,
                            fill='gray', fill_opacity=0.7))

    # ----------------------
    # 4) Timber beam
    #    x from [-b_timber/2, +b_timber/2], y from [-h_timber, 0]
    beam_left = -b_timber/2
    d.append(draw.Rectangle(beam_left, -h_timber, b_timber, h_timber,
                            fill='saddlebrown', fill_opacity=0.7))

    # ----------------------
    # 5) Red connector at (0,0)
    d.append(draw.Circle(0, 0, 3, fill='red'))

    # ----------------------
    # 6) Dashed line at y=0
    d.append(draw.Line(x_min, 0, x_max, 0, stroke='black', stroke_width=1, stroke_dasharray="4,2"))

    # ----------------------
    # 7) Neutral axis if a_timber is provided
    if a_timber is not None:
        na_y = -h_timber/2 + a_timber
        d.append(draw.Line(x_min, na_y, x_max, na_y, stroke='blue', stroke_width=2))

    # ----------------------
    # 8) Labels: Title, x-label, y-label
    d.append(draw.Text("Cross-section of TCC Element", 3, x_min+2, y_max-3, fill='black'))
    # x-label near bottom center
    d.append(draw.Text("Width (m)", 3, (x_min + x_max)/2 - 15, y_min+5, fill='black'))
    # y-label, rotated
    d.append(draw.Text("Height (m)", 3, x_min+5, (y_min + y_max)/2, fill='black',
                       transform=f"rotate(-90,{x_min+5},{(y_min+y_max)/2})"))

    # ----------------------
    # 9) (Optional) "Legend"
    if show_legend:
        lx, ly = x_min+5, y_max-10
        d.append(draw.Text("Legend:", 3, lx, ly, fill='black'))
        # Concrete example
        d.append(draw.Rectangle(lx, ly-7, 5, 5, fill='gray', fill_opacity=0.7))
        d.append(draw.Text("Concrete Slab", 3, lx+8, ly-3, fill='black'))
        # Timber example
        d.append(draw.Rectangle(lx, ly-17, 5, 5, fill='saddlebrown', fill_opacity=0.7))
        d.append(draw.Text("Timber Beam", 3, lx+8, ly-13, fill='black'))
        # etc.

    return d.as_svg()
