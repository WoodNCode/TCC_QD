from pylatex import Document, Section, Command, Math, Package
from pylatex.utils import NoEscape
import os

def generate_latex_pdf(
    E_timber_g, E_concrete_g, h_timber, b_timber,
    h_concrete, b_concrete, s, k_ser, P, L,
    sigma_timber, sigma_m_timber, sigma_concrete, sigma_m_concrete,
    M_concrete, N_concrete, tau_timber_max, F_connector
):
    # Create a new LaTeX document
    doc = Document(documentclass='article')
    
    # Include necessary packages
    doc.packages.append(Package('amsmath'))
    doc.packages.append(Package('graphicx'))
    
    # Preamble: title, author, and date
    doc.preamble.append(Command('title', 'TCC Element Stress Verification Report'))
    doc.preamble.append(Command('author', 'Your Name'))
    doc.preamble.append(Command('date', NoEscape(r'\today')))
    doc.append(NoEscape(r'\maketitle'))
    
    # Input Parameters Section
    with doc.create(Section('Input Parameters')):
        doc.append(f'Elastic Modulus of Timber: {E_timber_g:.1f} GPa\\\\')
        doc.append(f'Elastic Modulus of Concrete: {E_concrete_g:.1f} GPa\\\\')
        doc.append(f'Timber Section (h x b): {h_timber:.3f} m x {b_timber:.3f} m\\\\')
        doc.append(f'Concrete Section (h x b): {h_concrete:.3f} m x {b_concrete:.3f} m\\\\')
        doc.append(f'Connector Spacing (s): {s:.3f} m\\\\')
        doc.append(f'Slip Modulus per Connector (k_ser): {k_ser:.0f} N/m\\\\')
        doc.append(f'Point Load (P): {P:.0f} N\\\\')
        doc.append(f'Span Length (L): {L:.3f} m\\\\')
    
    # Formulas Section (rendered as LaTeX math)
    with doc.create(Section('Formulas')):
        doc.append(Math(data=r'\gamma_1 = \frac{1}{1+\frac{\pi^2\,E_{timber}\,A_{timber}\,s}{k_{ser}\,L^2}}'))
        doc.append('\n')
        doc.append(Math(data=r'a_2 = \frac{\gamma_1\,E_{concrete}\,A_{concrete}\,(h_{concrete}+h_{timber})}{2\left(\gamma_1\,E_{concrete}\,A_{concrete}+E_{timber}\,A_{timber}\right)}'))
        doc.append('\n')
        doc.append(Math(data=r'a_1 = \frac{h_{timber}}{2} - a_2 + \frac{h_{concrete}}{2}'))
        doc.append('\n')
        doc.append(Math(data=r'EI_{eff} = E_{timber}\,I_{timber} + E_{concrete}\,I_{concrete} + E_{timber}\,A_{timber}\,a_1^2 + \gamma_1\,E_{concrete}\,A_{concrete}\,a_2^2'))
    
    # Results Section
    with doc.create(Section('Results')):
        doc.append(f'Normal Stress in Timber: {sigma_timber/1e6:.2f} MPa\\\\')
        doc.append(f'Bending Stress in Timber: {sigma_m_timber/1e6:.2f} MPa\\\\')
        doc.append(f'Normal Stress in Concrete: {sigma_concrete/1e6:.2f} MPa\\\\')
        doc.append(f'Bending Stress in Concrete: {sigma_m_concrete/1e6:.2f} MPa\\\\')
        doc.append(f'Bending Moment in Concrete: {M_concrete/1e3:.2f} kNm\\\\')
        doc.append(f'Normal Force in Concrete: {N_concrete/1e3:.2f} kN\\\\')
        doc.append(f'Maximum Shear Stress in Timber: {tau_timber_max/1e6:.2f} MPa\\\\')
        doc.append(f'Force in Connector: {F_connector/1e3:.2f} kN\\\\')
    
    # Generate the PDF into a temporary file
    pdf_filename = "TCC_Stress_Verification_Report.pdf"
    doc.generate_pdf(pdf_filename, clean_tex=False, silent=True)
    
    # Read the PDF file as bytes
    with open(pdf_filename + ".pdf", "rb") as f:
        pdf_bytes = f.read()
    
    # Optionally, remove the generated files if you don't need them anymore
    os.remove(pdf_filename + ".pdf")
    os.remove(pdf_filename + ".tex")
    
    return pdf_bytes
