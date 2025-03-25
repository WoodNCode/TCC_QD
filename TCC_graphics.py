import math

import drawsvg as draw

def draw_elevation_view(L, s):
    """
    Returns an SVG string for the elevation view of a TCC element.
    Model coordinates:
      • The beam runs from x=0 to x=L at y=0.
      • Supports (upward-pointing triangles) are drawn at the beam ends.
      • Connectors (red circles) are spaced along the beam.
      • A downward-pointing load arrow is drawn from (L/2,5) to (L/2,0).
    """
    # Define drawing parameters (model in meters/units)
    margin = 20              # extra space around the drawing
    # Define model vertical extents: let’s show from y = -10 to y = +10.
    model_y_min = -10
    model_y_max = 10
    canvas_width = L + 2 * margin
    canvas_height = (model_y_max - model_y_min) + 2 * margin  # (20 + 40 = 60)
    
    # We want our model's y=0 (beam level) to be raised by (margin - model_y_min)
    y_offset = margin - model_y_min  # =20 - (-10) = 30
    
    # Create drawing with origin at bottom left (no flip!)
    d = draw.Drawing(canvas_width, canvas_height, origin=(0,0))
    
    # Draw the beam: a horizontal line from (margin, y_offset) to (margin+L, y_offset)
    d.append(draw.Line(margin, y_offset, margin + L, y_offset,
                       stroke='black', stroke_width=2))
    
    # Helper: draw an upward-pointing support triangle centered at (x, y).
    # Here we design an isosceles triangle whose centroid is (x,0).
    # We'll choose vertices so that the triangle’s tip is at (x, 2/3*size)
    # and the base vertices at (x - size, -1/3*size) and (x + size, -1/3*size).
    def support_triangle(x, y, size):
        return draw.Lines(
            x, y + (2/3)*size,
            x - size, y - (1/3)*size,
            x + size, y - (1/3)*size,
            close=True,
            fill='black'
        )
    
    support_size = 6
    # Draw supports at the left and right ends of the beam.
    d.append(support_triangle(margin, y_offset, support_size))
    d.append(support_triangle(margin + L, y_offset, support_size))
    
    # Draw connectors as red circles along the beam.
    n_connectors = int(L / s)
    for i in range(n_connectors):
        x = margin + s/2 + i * s
        d.append(draw.Circle(x, y_offset, 2.5, fill='red'))
    
    # Create a downward-pointing arrow marker.
    # For a downward arrow (in our upward-positive system), we want the marker’s tip at (0,0).
    # We define a marker with a bounding box and a simple triangular shape.
    arrow = draw.Marker(-0.5, -1, 0.5, 0, scale=3, orient='auto', id='load_arrow')
    # The arrow shape: vertices at (0,0) (the tip), (0.4,-0.8) and (-0.4,-0.8).
    arrow.append(draw.Lines(0, 0, 0.4, -0.8, -0.4, -0.8, close=True, fill='blue'))
    d.append(arrow)
    
    # Draw the load: a vertical line from (L/2, y_offset+5) down to (L/2, y_offset)
    load_x = margin + L/2
    load_line = draw.Line(load_x, y_offset + 5, load_x, y_offset,
                          stroke='blue', stroke_width=2,
                          marker_end=arrow)
    d.append(load_line)
    
    # Add title and axis labels (positions chosen for clarity)
    d.append(draw.Text("Elevation View of TCC Element", 10, margin, canvas_height - margin + 5))
    d.append(draw.Text("Beam Length (m)", 10, canvas_width/2 - 30, 5))
    d.append(draw.Text("Elevation", 10, 5, canvas_height/2,
                       transform=f"rotate(-90,5,{canvas_height/2})"))
    
    # Optionally, gridlines can be added (commented out for now)
    # for y in range(int(model_y_min), int(model_y_max)+1, 5):
    #     d.append(draw.Line(margin, y + (margin - model_y_min),
    #                        margin + L, y + (margin - model_y_min),
    #                        stroke='lightgray', stroke_width=0.5))
    # for x in range(margin, int(margin+L)+1, 10):
    #     d.append(draw.Line(x, margin, x, canvas_height - margin,
    #                        stroke='lightgray', stroke_width=0.5))
    
    return d.as_svg()

def draw_cross_section(b_concrete, h_concrete, b_timber, h_timber, a_timber=None):
    """
    Returns an SVG string for the cross-section view of a TCC element.
    Model coordinates (y increases upward):
      • Concrete slab: x from -b_concrete/2 to b_concrete/2, y from 0 to h_concrete.
      • Timber beam: x from -b_timber/2 to b_timber/2, y from -h_timber to 0.
      • Connector: red circle at (0,0).
      • Neutral axis (if a_timber is provided): horizontal line at y = -h_timber/2 + a_timber.
    """
    margin = 30
    # Define model extents.
    model_x_min = -b_concrete/2
    model_x_max = b_concrete/2
    model_y_min = -h_timber
    model_y_max = h_concrete
    canvas_width = (model_x_max - model_x_min) + 2*margin
    canvas_height = (model_y_max - model_y_min) + 2*margin
    
    # Create drawing with origin at bottom left.
    d = draw.Drawing(canvas_width, canvas_height, origin=(0,0))
    # Offset for model coordinates so that (0,0) is shifted by (margin - model_x_min, margin - model_y_min)
    offset_x = margin - model_x_min
    offset_y = margin - model_y_min
    
    # Draw the concrete slab as a rectangle: lower left at (-b_concrete/2, 0).
    d.append(draw.Rectangle(offset_x - b_concrete/2, offset_y + 0, b_concrete, h_concrete,
                            fill='gray', fill_opacity=0.7))
    
    # Draw the timber beam: rectangle from (-b_timber/2, -h_timber) with height h_timber.
    d.append(draw.Rectangle(offset_x - b_timber/2, offset_y - h_timber, b_timber, h_timber,
                            fill='saddlebrown', fill_opacity=0.7))
    
    # Draw a connector: red circle at (0,0)
    d.append(draw.Circle(offset_x + 0, offset_y + 0, 3, fill='red'))
    
    # Draw a dashed line at the interface y = 0.
    d.append(draw.Line(offset_x - b_concrete/2, offset_y + 0,
                       offset_x + b_concrete/2, offset_y + 0,
                       stroke='black', stroke_width=1, stroke_dasharray="4,2"))
    
    # Draw the neutral axis if provided.
    if a_timber is not None:
        na_y = -h_timber/2 + a_timber
        d.append(draw.Line(offset_x - b_concrete/2, offset_y + na_y,
                           offset_x + b_concrete/2, offset_y + na_y,
                           stroke='blue', stroke_width=2))
    
    # Add title and axis labels.
    d.append(draw.Text("Cross-section of TCC Element", 12,
                       offset_x - b_concrete/2, offset_y + h_concrete + 15))
    d.append(draw.Text("Width (m)", 12,
                       canvas_width/2 - 30, offset_y - 15))
    d.append(draw.Text("Height (m)", 12,
                       offset_x - b_concrete/2 - 20, canvas_height/2,
                       transform=f"rotate(-90,{offset_x - b_concrete/2 - 20},{canvas_height/2})"))
    
    # Optionally, gridlines can be added (commented out for now)
    # for x in range(int(model_x_min), int(model_x_max)+1, 10):
    #     d.append(draw.Line(offset_x + x, offset_y + model_y_min,
    #                        offset_x + x, offset_y + model_y_max,
    #                        stroke='lightgray', stroke_width=0.5))
    # for y in range(int(model_y_min), int(model_y_max)+1, 5):
    #     d.append(draw.Line(offset_x + model_x_min, offset_y + y,
    #                        offset_x + model_x_max, offset_y + y,
    #                        stroke='lightgray', stroke_width=0.5))
    
    return d.as_svg()
