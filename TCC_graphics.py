import math
import drawsvg as draw

def draw_elevation_view(L, s):
    """
    Returns an SVG string for the elevation view of a TCC element.
    
    Parameters:
      L : float
          Total beam length (m).
      s : float
          Connector spacing (m). Connectors are placed at mid‐points of segments.
          
    The elevation view shows:
      - A horizontal beam (black line)
      - Supports at both ends (upward triangles)
      - Connectors (red circles) evenly spaced along the beam
      - A point load represented as a downward pointing arrow (blue)
      - Basic text labels (title, axes)
    """
    # Set up drawing parameters
    margin = 10  # margin around drawing (arbitrary units)
    canvas_width = L + 2 * margin
    canvas_height = 40  # total canvas height
    beam_y = canvas_height / 2  # place beam at mid-height

    d = draw.Drawing(canvas_width, canvas_height, origin=(0, 0))
    
    # Draw the beam as a horizontal line
    d.append(draw.Line(margin, beam_y, margin + L, beam_y, stroke='black', stroke_width=2))
    
    # Function to create an upward-pointing triangle (support marker)
    def support_triangle(x, y, size):
        # Triangle with tip at (x, y+size) and base corners at (x-size, y-size) and (x+size, y-size)
        return draw.Polygon([x, y + size, x - size, y - size, x + size, y - size], fill='black')
    
    support_size = 4
    # Supports at both ends
    d.append(support_triangle(margin, beam_y, support_size))
    d.append(support_triangle(margin + L, beam_y, support_size))
    
    # Draw connectors: red circles along the beam.
    n_connectors = int(L / s)
    for i in range(n_connectors):
        x = margin + s/2 + i * s
        d.append(draw.Circle(x, beam_y, 1.5, fill='red'))
    
    # Draw the load as a downward arrow.
    # We create an arrow marker (using the snippet you referenced).
    # Here the marker is defined so that its “tip” (at the top of the arrow) is attached to the end of a vertical line.
    arrow = draw.Marker(-0.1, -0.51, 0.9, 0.5, scale=4, orient='auto')
    arrow.append(draw.Lines(-0.1, 0.5, -0.1, -0.5, 0.9, 0, fill='blue', close=True))
    # Draw a vertical line from above the beam down to the beam.
    load_x = margin + L / 2
    load_line = draw.Line(load_x, beam_y + 10, load_x, beam_y, stroke='blue', stroke_width=2,
                           marker_end=arrow)
    d.append(load_line)
    
    # Add title and axis labels as text
    d.append(draw.Text("Elevation View of TCC Element", 8, margin, canvas_height - 2))
    d.append(draw.Text("Beam Length (m)", 8, canvas_width / 2 - 30, 2))
    # For the Y label, we rotate the text (rotate around the text’s anchor point)
    d.append(draw.Text("Elevation", 8, 2, beam_y, transform=f"rotate(-90,2,{beam_y})"))
    
    # Add a simple grid (light gray lines)
    # Horizontal grid lines every 10 units
    for y in range(0, canvas_height + 1, 10):
        d.append(draw.Line(margin, y, margin + L, y, stroke='lightgray', stroke_width=0.5))
    # Vertical grid lines every 10 units
    for x in range(margin, int(margin + L) + 1, 10):
        d.append(draw.Line(x, 0, x, canvas_height, stroke='lightgray', stroke_width=0.5))
    
    return d.as_svg()

def draw_cross_section(b_concrete, h_concrete, b_timber, h_timber, a_timber=None):
    """
    Returns an SVG string for the cross-section view of a TCC element.
    
    Parameters:
      b_concrete : float
          Width of the concrete slab.
      h_concrete : float
          Height of the concrete slab.
      b_timber : float
          Width of the timber beam.
      h_timber : float
          Height of the timber beam.
      a_timber : float or None, optional
          Vertical offset for the neutral axis (if provided, drawn as a blue line).
    
    The cross-section view shows:
      - A concrete slab (gray rectangle) above the interface (y = 0)
      - A timber beam (saddlebrown rectangle) below y = 0
      - A red connector (circle) at the interface (0,0)
      - A dashed line at y = 0 (the interface)
      - Optionally, a neutral axis line drawn at y = (-h_timber/2 + a_timber)
      - Text labels (title and axis labels)
    """
    margin = 10  # margin in drawing units
    # The drawing canvas:
    # x goes from -b_concrete/2 - margin to b_concrete/2 + margin.
    # y goes from -h_timber - margin to h_concrete + margin.
    canvas_width = b_concrete + 2 * margin
    canvas_height = h_concrete + h_timber + 2 * margin
    d = draw.Drawing(canvas_width, canvas_height, origin=(0, 0))
    
    # To work in a coordinate system where:
    # x = 0 is at the center and y = 0 is the interface between timber and concrete,
    # we create a group and translate coordinates accordingly.
    # We'll set the translation so that (0,0) in our "model" is at (canvas_width/2, margin + h_timber)
    tx = canvas_width / 2
    ty = margin + h_timber
    grp = draw.Group(transform=f"translate({tx},{ty})")
    
    # Draw the concrete slab as a rectangle from (-b_concrete/2, 0) to (b_concrete/2, h_concrete)
    grp.append(draw.Rectangle(-b_concrete / 2, 0, b_concrete, h_concrete, fill='gray', fill_opacity=0.7))
    
    # Draw the timber beam as a rectangle from (-b_timber/2, -h_timber) to (b_timber/2, 0)
    grp.append(draw.Rectangle(-b_timber / 2, -h_timber, b_timber, h_timber, fill='saddlebrown', fill_opacity=0.7))
    
    # Draw a connector as a red circle at the interface (0,0)
    grp.append(draw.Circle(0, 0, 1.5, fill='red'))
    
    # Draw a dashed line at the interface (y = 0)
    grp.append(draw.Line(-b_concrete / 2, 0, b_concrete / 2, 0, stroke='black', stroke_width=0.8,
                           stroke_dasharray="4,2"))
    
    # If a neutral axis is provided, draw it at y = -h_timber/2 + a_timber.
    if a_timber is not None:
        na_y = -h_timber / 2 + a_timber
        grp.append(draw.Line(-b_concrete / 2, na_y, b_concrete / 2, na_y, stroke='blue', stroke_width=2))
    
    # Add title and axis labels (these are drawn in the group coordinates)
    # Title at the top of the concrete slab
    grp.append(draw.Text("Cross-section of TCC Element", 8, -b_concrete / 2, h_concrete + 5))
    # X label below the timber beam
    grp.append(draw.Text("Width (m)", 8, -b_concrete / 2, -h_timber - 8))
    # Y label: rotated and placed along the left
    grp.append(draw.Text("Height (m)", 8, -b_concrete / 2 - 12, h_concrete / 2, transform=f"rotate(-90, {-b_concrete / 2 - 12},{h_concrete / 2})"))
    
    # Optionally add simple grid lines (here vertical grid lines every ~10 units)
    for x in range(int(-b_concrete // 2), int(b_concrete // 2) + 1, 10):
        grp.append(draw.Line(x, -h_timber, x, h_concrete, stroke='lightgray', stroke_width=0.5))
    for y in range(int(-h_timber), int(h_concrete) + 1, 10):
        grp.append(draw.Line(-b_concrete / 2, y, b_concrete / 2, y, stroke='lightgray', stroke_width=0.5))
    
    d.append(grp)
    return d.as_svg()
