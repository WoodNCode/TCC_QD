import drawsvg as draw
import base64 as base64
import streamlit as st

def render_svg(svg):
    """Renders the given svg string."""
    b64 = base64.b64encode(svg.encode('utf-8')).decode("utf-8")
    html = r'<img src="data:image/svg+xml;base64,%s"/>' % b64
    st.write(html, unsafe_allow_html=True)
    
def draw_elevation_view(L, s):
    """
    Draws the Elevation view for a TCC element.
    
    • The beam is a horizontal line from x=0 to x=L at y=0.
    • Supports are drawn at the beam ends (with their tip exactly at the coordinate).
    • Connectors (red circles) are evenly spaced along the beam.
    • A downward-pointing load is drawn as an arrow (using your snippet) at midspan.
    • Text labels (title, x/y axis) are scaled down.
    
    Coordinates are defined in a “model space” then shifted so nothing overlaps.
    """
    # Define canvas/model parameters (in model units)
    margin = 100       # left/right margin in model units
    canvas_width = L + 2 * margin  # extra space on left and right
    canvas_height = 300            # fixed canvas height
    beam_y = 100                   # y-coordinate for the beam
    beam_left = margin             # beam starts at x = margin
    beam_right = beam_left + L*100     
    
    d = draw.Drawing(canvas_width, canvas_height, origin=(0,0), displayInline=False)
    
    # Draw the beam (black horizontal line)
    d.append(draw.Line(beam_left, beam_y, beam_right, beam_y,
                       stroke='black', stroke_width=2))
    
    # Draw supports as triangles.
    # The triangle’s tip is exactly at the support coordinate.
    # For a support at (x, beam_y), we draw a triangle with tip at (x,beam_y)
    # and base corners at (x - size, beam_y + size) and (x + size, beam_y + size)
    def support_triangle_tip(x, y, size):
        return draw.Lines(
            x, y,                    # tip at (x,y)
            x - size, y + size,      # left base
            x + size, y + size,      # right base
            close=True,
            fill='black'
        )
    support_size = 10
    d.append(support_triangle_tip(beam_left, beam_y, support_size))
    d.append(support_triangle_tip(beam_right, beam_y, support_size))
    
    # Draw connectors as red circles along the beam.
    n_conn = int(L // s)
    for i in range(n_conn):
        cx = beam_left + s/2 + i*s
        d.append(draw.Circle(cx, beam_y, 4, fill='red'))
    
    # Draw the downward-pointing load arrow.
    # Use the snippet you provided:
    arrow = draw.Marker(-0.1, -0.51, 0.9, 0.5, scale=4, orient='auto')
    arrow.append(draw.Lines(-0.1, 0.5, -0.1, -0.5, 0.9, 0, fill='red', close=True))
    d.append(arrow)
    # Draw a vertical line from (beam_mid, 20) to (beam_mid, beam_y)
    beam_mid = beam_left + L/2
    # Here the marker_end parameter accepts a Marker directly.
    load_line = draw.Path(stroke='red', stroke_width=2, fill='none', marker_end=arrow)
    load_line.M(beam_mid, beam_y - 20).L(beam_mid, beam_y)
    d.append(load_line)
    
    # Add text labels (font size reduced to ~1/5th typical; here using size 3)
    d.append(draw.Text("Elevation View of TCC Element", 3, 10, 20, fill='black'))
    d.append(draw.Text("Beam Length (m)", 3, canvas_width/2 - 30, canvas_height - 10, fill='black'))
    d.append(draw.Text("Elevation", 3, 10, canvas_height/2, fill='black',
                        transform=f"rotate(-90,10,{canvas_height/2})"))
    
    # (Grid lines omitted; you can add them later if needed)
    return d.as_svg()

def draw_cross_section(b_concrete, h_concrete, b_timber, h_timber, a_timber=None):
    """
    Draws the Cross-section view for a TCC element.
    
    • The concrete slab is drawn from x = -b_concrete/2 to b_concrete/2,
      and from y = 0 to y = h_concrete.
    • The timber beam is drawn from x = -b_timber/2 to b_timber/2,
      and from y = -h_timber to y = 0.
    • A red connector is drawn at (0,0).
    • A dashed line is drawn at y=0 (the interface).
    • If provided, the neutral axis is drawn at y = -h_timber/2 + a_timber.
    • All text is scaled down (font size ~3).
    
    The drawing is shifted so that the interface is centered horizontally.
    """
    # Canvas/model parameters
    margin = 100
    # Let the drawing's x-axis run from -max_width/2 to max_width/2.
    max_width = max(b_concrete, b_timber)
    canvas_width = max_width + 2 * margin
    canvas_height = h_concrete + h_timber + 200  # extra vertical margin
    
    d = draw.Drawing(canvas_width, canvas_height, origin=(0,0), displayInline=False)
    
    # Center the cross-section horizontally.
    cx = canvas_width / 2
    # Let the interface (y=0 in the model) be drawn at y = 150.
    interface_y = 150
    
    # Draw concrete slab (from y=0 to y=h_concrete, above the interface)
    slab_left = cx - b_concrete/2
    slab_top = interface_y  # interface is at y=interface_y
    d.append(draw.Rectangle(slab_left, slab_top, b_concrete, h_concrete,
                            fill='gray', fill_opacity=0.7))
    
    # Draw timber beam (from y=-h_timber to y=0, below the interface)
    beam_left = cx - b_timber/2
    beam_top = interface_y - h_timber  # timber extends upward to the interface
    d.append(draw.Rectangle(beam_left, beam_top, b_timber, h_timber,
                            fill='saddlebrown', fill_opacity=0.7))
    
    # Draw a red connector at the interface (0,0 in model → (cx, interface_y))
    d.append(draw.Circle(cx, interface_y, 4, fill='red'))
    
    # Draw dashed line at the interface (x from slab_left to slab_left+b_concrete)
    d.append(draw.Line(slab_left, interface_y, slab_left + b_concrete, interface_y,
                       stroke='black', stroke_width=1, stroke_dasharray="5,5"))
    
    # Draw neutral axis if provided.
    if a_timber is not None:
        # Neutral axis is at y = -h_timber/2 + a_timber (model), so its screen y = interface_y - h_timber/2 + a_timber.
        na_y = interface_y - h_timber/2 + a_timber
        d.append(draw.Line(slab_left, na_y, slab_left + b_concrete, na_y,
                           stroke='blue', stroke_width=2))
    
    # Add text labels (small font size ~3)
    d.append(draw.Text("Cross-section of TCC Element", 3, 10, 20, fill='black'))
    d.append(draw.Text("Width (m)", 3, canvas_width/2 - 30, canvas_height - 10, fill='black'))
    d.append(draw.Text("Height (m)", 3, 10, canvas_height/2,
                       fill='black',
                       transform=f"rotate(-90,10,{canvas_height/2})"))
    return d.as_svg()
