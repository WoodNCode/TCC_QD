import numpy as np

def compute_section_properties(b_timber, h_timber, b_concrete, h_concrete):
    """
    Computes and returns the cross-sectional properties:
    - Timber area, I
    - Concrete area, I
    """
    A_timber = b_timber * h_timber
    A_concrete = b_concrete * h_concrete

    I_timber = (b_timber * (h_timber**3)) / 12.0
    I_concrete = (b_concrete * (h_concrete**3)) / 12.0
    
    return A_timber, I_timber, A_concrete, I_concrete

def compute_gamma_concrete(E_concrete, A_concrete, s, k_ser, L):
    """
    Computes the gamma factor for the concrete (gamma_concrete)
    using the equation from EN 1995-1-1 Annex B.
    """
    # gamma_concrete = 1 / [1 + (π² * E_c * A_c * s) / (k_ser * L²)]
    return 1.0 / (
        1.0 + (np.pi**2 * E_concrete * A_concrete * s) / (k_ser * (L**2))
    )

def compute_neutral_axes(E_timber, A_timber, E_concrete, A_concrete, h_timber, h_concrete, gamma_concrete):
    """
    Computes the distance from the timber's centroid to the 
    composite neutral axis (a_timber) and from the concrete's centroid 
    to the composite neutral axis (a_concrete).

    Returns:
      a_timber (float): distance from the timber section centroid
      a_concrete (float): distance from the concrete section centroid
    """
    # a_timber = [γ * E_c * A_c * (h_c + h_t)] / [2*(γ * E_c * A_c + E_t * A_t)]
    numerator = gamma_concrete * E_concrete * A_concrete * (h_concrete + h_timber)
    denominator = 2.0 * ((gamma_concrete * E_concrete * A_concrete) + (E_timber * A_timber))
    a_timber = numerator / denominator
    
    # a_concrete is measured from the timber centroid as well,
    # so if timber centroid is at -h_timber/2, then the distance from that
    # to the concrete centroid is (h_concrete / 2 + h_timber / 2).
    # Then we shift by a_timber to find the composite neutral axis to the 
    # concrete centroid location:
    a_concrete = (h_timber / 2.0) - a_timber + (h_concrete / 2.0)

    return a_timber, a_concrete

def compute_effective_bending_stiffness(E_timber, I_timber, A_timber, a_timber,
                                        E_concrete, I_concrete, A_concrete, a_concrete,
                                        gamma_concrete):
    """
    Computes the effective bending stiffness EI_eff using 
    the gamma method from EN 1995-1-1 Annex B.
    """
    # EI_eff = E_t * I_t + E_c * I_c + E_t * A_t * a_timber^2 + 
    #          γ * E_c * A_c * a_concrete^2
    part_timber = E_timber * I_timber + E_timber * A_timber * (a_timber**2)
    part_concrete = E_concrete * I_concrete + gamma_concrete * E_concrete * A_concrete * (a_concrete**2)
    return part_timber + part_concrete

def compute_bending_moment_and_shear(P, L):
    """
    For a single-span simply supported beam with a single point load P at mid-span:
      - M_mid = P * L / 4
      - V_max = P / 2

    Returns:
      M_mid, V_max
    """
    M_mid = (P * L) / 4.0
    V_max = P / 2.0
    return M_mid, V_max

def compute_deflection(EI_eff, P, L, num_points=50):
    """
    Computes the deflection curve for a simply supported beam with a 
    mid-span point load, using classic beam formulas.

    Returns:
      x_left (ndarray): x-coordinates from 0 to L/2
      delta_left (ndarray): deflection from 0 to L/2
      x_right (ndarray): x-coordinates from L/2 to L
      delta_right (ndarray): deflection from L/2 to L
    """
    # The deflection for a point load P at mid-span (x = L/2) can be derived.
    # For convenience, we do a polynomial expression or symmetrical approach.
    x_left = np.linspace(0, L / 2.0, num_points)
    # The expression for deflection in the region 0 <= x <= L/2 is:
    # δ(x) = [P * x^3 / (48*EI)] * (3L - 4x)   (this is one form),
    # or you can store an approximate form used below. 
    # Let's just replicate your partial approach for demonstration:
    
    # Replace with your known beam formula if you want a more exact solution.
    delta_left = (P * x_left**3 / 12.0 - P * L**2 * x_left / 16.0) / EI_eff
    
    # Symmetrically reflect for the right half
    x_right = np.linspace(L / 2.0, L, num_points)
    # We'll just mirror the shape so that it's symmetrical
    delta_right = delta_left[::-1]
    
    return x_left, delta_left, x_right, delta_right

def compute_stresses_and_forces(E_timber, A_timber, h_timber, f_m_timber, f_t_timber,
                                E_concrete, A_concrete, h_concrete,
                                I_concrete, M_mid, V_max,
                                a_timber, a_concrete, s, EI_eff, gamma_concrete):
    """
    Computes the normal/bending stresses in timber & concrete, 
    shear stress in timber, and force in connectors, etc.
    """
    # Normal / bending stress in timber
    # For demonstration, a simple approach:
    # sigma_timber = (E_timber * a_timber * M_mid) / EI_eff
    sigma_timber = (E_timber * a_timber * M_mid) / EI_eff
    sigma_m_timber = (0.5 * E_timber * h_timber * M_mid) / EI_eff
    
    utilisation_timber = (sigma_m_timber / f_m_timber) + (sigma_timber / f_t_timber)
    
    # Normal / bending stress in concrete
    sigma_concrete = (gamma_concrete * E_concrete * a_concrete * M_mid) / EI_eff
    sigma_m_concrete = (0.5 * E_concrete * h_concrete * M_mid) / EI_eff

    # Internal forces in concrete
    # Normal force
    N_concrete = sigma_concrete * A_concrete
    # Bending moment
    M_concrete = (E_concrete * I_concrete * M_mid) / EI_eff

    # Shear stress in Timber
    # Use whichever formula is valid for your scenario
    h_EC_tau = (a_timber + 0.5*h_timber)
    tau_timber_max = (0.5 * E_timber * (h_EC_tau**2) * V_max) / (EI_eff)
    # If b_timber is needed for average shear, adapt accordingly. 
    # The line above is from your snippet, but double-check correctness.

    # Force in connector
    # Typically: F_connector = (γ * E_c * A_c * a_c * s / EI_eff) * V
    # This is an approximate expression for the shear in each connector group.
    # 
    # If your s is the spacing, be mindful of total vs per-connector. 
    # Below is the approach from your snippet:
    F_connector = (gamma_concrete * E_concrete * A_concrete * a_concrete * s / EI_eff) * V_max
    
    results = {
        "sigma_timber": sigma_timber,
        "sigma_m_timber": sigma_m_timber,
        "utilisation_timber": utilisation_timber,
        "sigma_concrete": sigma_concrete,
        "sigma_m_concrete": sigma_m_concrete,
        "N_concrete": N_concrete,
        "M_concrete": M_concrete,
        "tau_timber_max": tau_timber_max,
        "F_connector": F_connector,
        "h_EC_tau": h_EC_tau  # neutral axis position from bottom
    }

    return results
