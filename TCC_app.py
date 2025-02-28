import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import io
import os
import tempfile
from fpdf import FPDF

st.title("TCC_QD EC5 Verification")

st.markdown(
    """
This app calculates the stresses in a Timber-Concrete Composite (TCC) element using the formulas from EN 1995-1-1 Annex B.
Below, you can adjust the input parameters from the sidebar.
"""
)

# Sidebar input parameters
st.sidebar.header("Input Parameters")

E_timber_g = st.sidebar.number_input(
    "Elastic Modulus of Timber (GPa)", value=11.0, format="%.1f", step=0.1
)
E_timber = E_timber_g*1000000000
E_concrete_g = st.sidebar.number_input(
    "Elastic Modulus of Concrete (GPa)", value=33.0, format="%.1f", step=0.1
)
E_concrete = E_concrete_g*1000000000
h_timber = st.sidebar.number_input("Height of Timber Section (m)", value=0.16)
b_timber = st.sidebar.number_input("Width of Timber Section (m)", value=0.12)
h_concrete = st.sidebar.number_input("Height of Concrete Section (m)", value=0.1)
b_concrete = st.sidebar.number_input("Width of Concrete Section (m)", value=0.4)

# Connector and load parameters
s = st.sidebar.number_input("Spacing between connectors (m)", value=0.8)
k_ser = st.sidebar.slider("Slip Modulus per connector (N/m)", min_value=100, max_value=2500000000, value=330000000, step=1000, format=None, key=None, help="165000000 N/m is the Value for 20 cm TiComTec", on_change=None, args=None, kwargs=None, disabled=False, label_visibility="visible")
# k_ser = st.sidebar.number_input("Slip Modulus per connector (N/m)", value=330000000, format="%.2e")

P = st.sidebar.number_input("Point Load (N)", value=80e3, format="%.2e")
L = st.sidebar.number_input("Span Length (m)", value=1.6)

# --- Calculated Section Properties ---
# Cross-sectional areas
A_timber = b_timber * h_timber
A_concrete = b_concrete * h_concrete

# Moments of inertia
I_timber = (b_timber * h_timber**3) / 12
I_concrete = (b_concrete * h_concrete**3) / 12

# Calculate bending moment at mid-span
M_mid = (P * L) / 4
V_max = P*L/2

# Compute gamma factor
gamma_concrete = 1 / (1 + (np.pi**2 * E_concrete * A_concrete * s) / (k_ser * L**2))

# Compute neutral axis distances
a_timber = (gamma_concrete * E_concrete * A_concrete * (h_concrete + h_timber)) / (2*(gamma_concrete * E_concrete * A_concrete) + (E_timber * A_timber))
a_concrete = (h_timber / 2) - a_timber + (h_concrete / 2)

# Elevation view
plt.figure(figsize=(8, 2))
plt.plot([0, L], [0, 0], color='black', linewidth=2, label='Beam')
plt.scatter([L/2], [0], color='blue', s=100, label='Point Load')
plt.scatter([0, L], [0, 0], color='black', marker='^', s=100, label='Supports')
plt.scatter(np.linspace(s/2, L - s/2, int(L/s)), np.zeros(int(L/s)), color='red', label='Connectors')
plt.xlabel("Beam Length (m)")
plt.ylabel("Elevation")
plt.title("Elevation View of TCC Element")
plt.legend()
plt.grid()
st.pyplot(plt)

# Cross-section plot
plt.figure(figsize=(8, 6))
plt.fill_between([-b_concrete/2, b_concrete/2], 0, h_concrete, color='gray', alpha=0.7, label='Concrete Slab')
plt.fill_between([-b_timber/2, b_timber/2], -h_timber, 0, color='saddlebrown', alpha=0.7, label='Timber Beam')
plt.scatter([0], [0], color='red', label='Connectors')
plt.axhline(0, color='black', linestyle='--', linewidth=0.8)
plt.axhline(-h_timber/2 + a_timber, color='blue', linestyle='-', linewidth=2, label='Neutral Axis')
plt.xlabel("Width (m)")
plt.ylabel("Height (m)")
plt.title("Cross-section of TCC Element")
plt.legend()
plt.grid()
st.pyplot(plt)

# --- Effective Bending Stiffness ---
EI_eff = (E_timber * I_timber + 
          E_concrete * I_concrete + 
          E_timber * A_timber * a_timber**2 + 
          gamma_concrete * E_concrete * A_concrete * a_concrete**2)

# Deflection curve computation
x_left = np.linspace(0, L/2, 50)
x_right = np.linspace(L/2, L, 50)
delta_x_left = (P * x_left**3 / 12 - P * L**2 * x_left / 16) / EI_eff
delta_x_right = delta_x_left[::-1]  # Symmetric about mid-span

# Plot deflection shape
plt.figure(figsize=(8, 4))
plt.plot(x_left, delta_x_left * 1e3, label='Deflection (mm)', color='blue')
plt.plot(x_right, delta_x_right * 1e3, color='blue')
plt.axhline(0, color='black', linestyle='--', linewidth=0.8)
plt.xlabel("Beam Length (m)")
plt.ylabel("Deflection (mm)")
plt.title("Deflection of TCC Element using Gamma Method")
plt.legend()
plt.grid()
st.pyplot(plt)

# --- Output the Calculated Properties and Stresses ---
st.header("Calculated Section Properties")
st.markdown(f"- **A_timber**: {A_timber:.4f} m²")
st.markdown(f"- **I_timber**: {I_timber:.4e} m⁴")
st.markdown(f"- **A_concrete**: {A_concrete:.4f} m²")
st.markdown(f"- **I_concrete**: {I_concrete:.4e} m⁴")
st.markdown(f"- **Neutral Axis Distances**: a_timber = {a_timber:.4f} m, a_concrete = {a_concrete:.4f} m")
st.markdown(f"- **Effective Bending Stiffness (EI_eff)**: {EI_eff:.4e} Nm²")
st.markdown(f"- **Gamma_concrete**: {gamma_concrete:.4f}")

# Calculate normal and bending stresses
sigma_timber = (E_timber * a_timber * M_mid) / EI_eff
sigma_m_timber = (0.5 * E_timber * h_timber * M_mid) / EI_eff

sigma_concrete = (gamma_concrete * E_timber * a_timber * M_mid) / EI_eff
sigma_m_concrete = (0.5 * E_timber * h_timber * M_mid) / EI_eff

N_concrete = sigma_concrete * A_concrete
M_concrete = (E_concrete*I_concrete * M_mid) / EI_eff

# Calculate shear stress in Timber
# Note: This formula is taken from your script, but verify it since it appears non-standard.
tau_timber_max = (0.5 * E_timber * b_timber * h_timber**2) *V_max / (b_timber*EI_eff)

# Calculate the Force in the Connector
F_connector = (gamma_concrete*E_concrete*A_concrete*a_concrete*s) / (EI_eff) * V_max

st.title("TCC Element Stress Verification Results")

st.markdown("## Timber")
st.write(f"**Normal Stress in Timber:** {sigma_timber / 1e6:.2f} MPa")
st.write(f"**Bending Stress in Timber:** {sigma_m_timber / 1e6:.2f} MPa")

st.markdown("## Concrete")
st.write(f"**Normal Stress in Concrete:** {sigma_concrete / 1e6:.2f} MPa")
st.write(f"**Bending Stress in Concrete:** {sigma_m_concrete / 1e6:.2f} MPa")
st.write(f"**Bending Moment in Concrete:** {M_concrete / 1e3:.2f} kNm")
st.write(f"**Normal Force in Concrete:** {N_concrete / 1e3:.2f} kN")

st.markdown("## Timber Shear")
st.write(f"**Maximum Shear Stress in Timber:** {tau_timber_max / 1e6:.2f} MPa")

st.markdown("## Connectors")
st.write(f"**Force in Connector:** {F_connector / 1e3:.2f} kN")

def generate_formula_image():
    """
    Create a Matplotlib figure that renders the formulas in LaTeX and return
    a BytesIO buffer containing the PNG image.
    """
    # Create a figure without axes
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.axis("off")
    
    # Define the formulas using LaTeX
    formulas = r"""
    \begin{align*}
    \gamma_1 &= \frac{1}{1 + \frac{\pi^2 \, E_{\text{timber}} \, A_{\text{timber}} \, s}{k_{\text{ser}} \, L^2}} \\[8pt]
    a_2 &= \frac{\gamma_1 \, E_{\text{concrete}} \, A_{\text{concrete}} \, (h_{\text{concrete}} + h_{\text{timber}})}
           {2\Bigl(\gamma_1 \, E_{\text{concrete}} \, A_{\text{concrete}} + E_{\text{timber}} \, A_{\text{timber}}\Bigr)} \\[8pt]
    a_1 &= \frac{h_{\text{timber}}}{2} - a_2 + \frac{h_{\text{concrete}}}{2} \\[8pt]
    EI_{\text{eff}} &= E_{\text{timber}} \, I_{\text{timber}} + E_{\text{concrete}} \, I_{\text{concrete}} + 
           E_{\text{timber}} \, A_{\text{timber}} \, a_1^2 + \gamma_1 \, E_{\text{concrete}} \, A_{\text{concrete}} \, a_2^2
    \end{align*}
    """
    # Display the formulas centered in the figure
    ax.text(0.5, 0.5, formulas, horizontalalignment="center", verticalalignment="center",
            fontsize=12, transform=ax.transAxes)
    
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=150)
    plt.close(fig)
    buf.seek(0)
    return buf

def generate_formula_image():
    """
    Create a Matplotlib figure that renders the formulas using mathtext,
    then return a BytesIO buffer containing the PNG image.
    """
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.axis("off")
    
    # Define the formulas using mathtext. Note that mathtext does not support 
    # full LaTeX environments such as align, so we create a multi-line string.
    formulas = (
        r"$\gamma_1 = \frac{1}{1 + \frac{\pi^2\, E_{\mathrm{timber}}\, A_{\mathrm{timber}}\, s}{k_{\mathrm{ser}}\, L^2}}$" "\n\n" +
        r"$a_2 = \frac{\gamma_1\, E_{\mathrm{concrete}}\, A_{\mathrm{concrete}}\, (h_{\mathrm{concrete}}+h_{\mathrm{timber}})}{2\Bigl(\gamma_1\, E_{\mathrm{concrete}}\, A_{\mathrm{concrete}}+E_{\mathrm{timber}}\, A_{\mathrm{timber}}\Bigr)}$" "\n\n" +
        r"$a_1 = \frac{h_{\mathrm{timber}}}{2} - a_2 + \frac{h_{\mathrm{concrete}}}{2}$" "\n\n" +
        r"$EI_{\mathrm{eff}} = E_{\mathrm{timber}}\, I_{\mathrm{timber}} + E_{\mathrm{concrete}}\, I_{\mathrm{concrete}} + E_{\mathrm{timber}}\, A_{\mathrm{timber}}\, a_1^2 + \gamma_1\, E_{\mathrm{concrete}}\, A_{\mathrm{concrete}}\, a_2^2$"
    )
    
    # Place the formulas in the center of the figure.
    ax.text(0.5, 0.5, formulas, ha="center", va="center", fontsize=12, wrap=True, transform=ax.transAxes)
    
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=150)
    plt.close(fig)
    buf.seek(0)
    return buf

def generate_pdf():
    pdf = FPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "TCC Element Stress Verification Report", ln=True, align="C")
    pdf.ln(10)
    
    # --- Input Parameters Section ---
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Input Parameters", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Elastic Modulus of Timber: {E_timber_g:.1f} GPa", ln=True)
    pdf.cell(0, 8, f"Elastic Modulus of Concrete: {E_concrete_g:.1f} GPa", ln=True)
    pdf.cell(0, 8, f"Timber Section (h x b): {h_timber:.3f} m x {b_timber:.3f} m", ln=True)
    pdf.cell(0, 8, f"Concrete Section (h x b): {h_concrete:.3f} m x {b_concrete:.3f} m", ln=True)
    pdf.cell(0, 8, f"Connector Spacing (s): {s:.3f} m", ln=True)
    pdf.cell(0, 8, f"Slip Modulus per Connector (k_ser): {k_ser:.0f} N/m", ln=True)
    pdf.cell(0, 8, f"Point Load (P): {P:.0f} N", ln=True)
    pdf.cell(0, 8, f"Span Length (L): {L:.3f} m", ln=True)
    pdf.ln(8)
    
    # --- Cross-Section Plan Description ---
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Cross-Section Plan", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 8,
        "The cross-section consists of a concrete slab over a timber beam.\n"
        " - Concrete slab: width = {:.3f} m, height = {:.3f} m.\n"
        " - Timber beam: width = {:.3f} m, height = {:.3f} m.\n"
        "A neutral axis is drawn based on the computed value a_timber = {:.3f} m.".format(
            b_concrete, h_concrete, b_timber, h_timber, a_timber))
    pdf.ln(8)
    
    # --- Insert Cross-Section Graphic (Plot) ---
    # Create the cross-section plot using Matplotlib.
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.fill_between([-b_concrete/2, b_concrete/2], 0, h_concrete, color="gray", alpha=0.7, label="Concrete Slab")
    ax.fill_between([-b_timber/2, b_timber/2], -h_timber, 0, color="saddlebrown", alpha=0.7, label="Timber Beam")
    ax.scatter([0], [0], color="red", label="Connectors")
    ax.axhline(0, color="black", linestyle="--", linewidth=0.8)
    ax.axhline(-h_timber/2 + a_timber, color="blue", linestyle="-", linewidth=2, label="Neutral Axis")
    ax.set_xlabel("Width (m)")
    ax.set_ylabel("Height (m)")
    ax.set_title("Cross-section of TCC Element")
    ax.legend()
    ax.grid(True)
    
    # Save the plot temporarily.
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
        fig.savefig(tmp_file.name, format="png", bbox_inches="tight")
        tmp_filename = tmp_file.name
    plt.close(fig)
    
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Cross-Section Graphic", ln=True)
    current_y = pdf.get_y()
    pdf.image(tmp_filename, x=10, y=current_y, w=pdf.w - 20)
    os.remove(tmp_filename)
    pdf.ln(10)
    
    # --- Insert Formulas Graphic ---
    # Generate a graphic of the formulas.
    formula_buf = generate_formula_image()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_formula:
        tmp_formula.write(formula_buf.getvalue())
        tmp_formula_filename = tmp_formula.name
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Gamma Method Formulas", ln=True)
    current_y = pdf.get_y()
    pdf.image(tmp_formula_filename, x=10, y=current_y, w=pdf.w - 20)
    os.remove(tmp_formula_filename)
    pdf.ln(10)
    
    # --- Results Section ---
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Calculated Results", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Normal Stress in Timber: {sigma_timber/1e6:.2f} MPa", ln=True)
    pdf.cell(0, 8, f"Bending Stress in Timber: {sigma_m_timber/1e6:.2f} MPa", ln=True)
    pdf.cell(0, 8, f"Normal Stress in Concrete: {sigma_concrete/1e6:.2f} MPa", ln=True)
    pdf.cell(0, 8, f"Bending Stress in Concrete: {sigma_m_concrete/1e6:.2f} MPa", ln=True)
    pdf.cell(0, 8, f"Bending Moment in Concrete: {M_concrete/1e3:.2f} kNm", ln=True)
    pdf.cell(0, 8, f"Normal Force in Concrete: {N_concrete/1e3:.2f} kN", ln=True)
    pdf.cell(0, 8, f"Maximum Shear Stress in Timber: {tau_timber_max/1e6:.2f} MPa", ln=True)
    pdf.cell(0, 8, f"Force in Connector: {F_connector/1e3:.2f} kN", ln=True)
    
    pdf_data = pdf.output(dest="S").encode("latin1")
    return pdf_data

# --- Generate PDF Button ---
if st.button("Generate PDF Report", key="generate_pdf_report"):
    pdf_data = generate_pdf()
    st.download_button(
        label="Download PDF Report",
        data=pdf_data,
        file_name="TCC_Stress_Verification_Report.pdf",
        mime="application/pdf",
        key="download_pdf_button"
    )

