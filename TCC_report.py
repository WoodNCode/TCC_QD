import os
import io
import tempfile
%from fpdf import FPDF
from TCC_plots import create_formula_plot

def generate_pdf_report(
    E_timber_g, E_concrete_g, h_timber, b_timber,
    h_concrete, b_concrete, s, k_ser, P, L,
    sigma_timber, sigma_m_timber, sigma_concrete, sigma_m_concrete,
    M_concrete, N_concrete, tau_timber_max, F_connector
):
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
    # Here we assume a_timber is computed as 0.05 (or pass as a parameter if computed)
    a_timber = 0.05
    pdf.multi_cell(0, 8, 
        "The cross-section consists of a concrete slab over a timber beam.\n"
        " - Concrete slab: width = {:.3f} m, height = {:.3f} m.\n"
        " - Timber beam: width = {:.3f} m, height = {:.3f} m.\n"
        "Neutral axis (a_timber): {:.3f} m.".format(b_concrete, h_concrete, b_timber, h_timber, a_timber))
    pdf.ln(8)
    
    # --- Insert Formula Graphic ---
    #formula_buf = create_formula_plot()
    #with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
    #    tmp_file.write(formula_buf.getvalue())
    #    tmp_formula_filename = tmp_file.name
    #pdf.set_font("Arial", "B", 14)
    #pdf.cell(0, 10, "Gamma Method Formulas", ln=True)
    # Let FPDF auto-place the image (without specifying y)
    #pdf.image(tmp_formula_filename, x=10, w=pdf.w - 20)
    #os.remove(tmp_formula_filename)
    #pdf.ln(10)
    
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
    
    pdf_bytes = pdf.output(dest="S").encode("latin1")
    return pdf_bytes
