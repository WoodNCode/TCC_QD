import io
import matplotlib.pyplot as plt
import numpy as np

def create_formula_plot():
    """
    Create a Matplotlib figure that renders the formulas using mathtext,
    then return a BytesIO buffer containing the PNG image.
    """
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.axis("off")
    
    # Define each formula as a separate line
    formula_lines = [
        r"$\gamma_1 = \frac{1}{1 + \frac{\pi^2\,E_{timber}\,A_{timber}\,s}{k_{ser}\,L^2}}$",
        r"$a_2 = \frac{\gamma_1\,E_{concrete}\,A_{concrete}\,(h_{concrete}+h_{timber})}{2\left(\gamma_1\,E_{concrete}\,A_{concrete}+E_{timber}\,A_{timber}\right)}$",
        r"$a_1 = \frac{h_{timber}}{2} - a_2 + \frac{h_{concrete}}{2}$",
        r"$EI_{eff} = E_{timber}\,I_{timber} + E_{concrete}\,I_{concrete} + E_{timber}\,A_{timber}\,a_1^2 + \gamma_1\,E_{concrete}\,A_{concrete}\,a_2^2$"
    ]
    
    # Define vertical positions (in fraction of the Axes height)
    y_positions = [0.8, 0.65, 0.5, 0.35]
    
    # Render each formula on its own line
    for line, y in zip(formula_lines, y_positions):
        ax.text(0.5, y, line, ha="center", va="center", fontsize=14, transform=ax.transAxes)
    
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=150)
    plt.close(fig)
    buf.seek(0)
    return buf


def plot_elevation_view(L, s, P, show_plot=True):
    """
    Plots the elevation view of the TCC element with:
      - Beam line from x=0 to x=L
      - A point load at mid-span
      - Two supports at ends
      - Connectors spaced at 's'
    If show_plot=True, will call plt.show() at the end (useful if needed).
    """
    fig, ax = plt.subplots(figsize=(8, 2))
    ax.plot([0, L], [0, 0], linewidth=2, label='Beam')
    ax.scatter([L/2], [0], s=100, label='Point Load')
    ax.scatter([0, L], [0, 0], marker='^', s=100, label='Supports')

    # Plot the connector positions
    n_connectors = int(L / s)
    connector_positions = np.linspace(s/2, L - s/2, n_connectors)
    ax.scatter(connector_positions, np.zeros(n_connectors), color='red', label='Connectors')

    ax.set_xlabel("Beam Length (m)")
    ax.set_ylabel("Elevation")
    ax.set_title("Elevation View of TCC Element")
    ax.legend()
    ax.grid()

    if show_plot:
        plt.show()

    return fig

def plot_cross_section(b_concrete, h_concrete, b_timber, h_timber, a_timber, show_plot=True):
    """
    Plots a cross-section with:
      - Concrete slab
      - Timber beam
      - Approx. connector location
      - Neutral axis drawn
    """
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.fill_between([-b_concrete/2, b_concrete/2], 0, h_concrete, alpha=0.7, label='Concrete Slab')
    ax.fill_between([-b_timber/2, b_timber/2], -h_timber, 0, alpha=0.7, label='Timber Beam')
    
    # Connectors at the interface
    ax.scatter([0], [0], color='red', label='Connectors')
    ax.axhline(0, linestyle='--', linewidth=0.8, color='black')
    
    # Plot the NA in timber
    na_position = -h_timber/2 + a_timber
    ax.axhline(na_position, linestyle='-', linewidth=2, color='blue', label='Neutral Axis')

    ax.set_xlabel("Width (m)")
    ax.set_ylabel("Height (m)")
    ax.set_title("Cross-Section of TCC Element")
    ax.legend()
    ax.grid()

    if show_plot:
        plt.show()
    
    return fig

def plot_deflection_shape(x_left, delta_left, x_right, delta_right, show_plot=True):
    """
    Plots the beam deflection (in mm) vs x (in m).
    """
    fig, ax = plt.subplots(figsize=(8, 4))
    x_total = np.concatenate((x_left, x_right))
    delta_total = np.concatenate((delta_left, delta_right))
    ax.plot(x_total, delta_total*1e3, label='Deflection in mm')
    
    ax.axhline(0, color='black', linestyle='--', linewidth=0.8)
    ax.set_xlabel("Beam Length (m)")
    ax.set_ylabel("Deflection (mm)")
    ax.set_title("Deflection of TCC Element (Gamma Method)")
    ax.legend()
    ax.grid()

    if show_plot:
        plt.show()
    
    return fig
