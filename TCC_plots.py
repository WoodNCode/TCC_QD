import io
import matplotlib.pyplot as plt

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
