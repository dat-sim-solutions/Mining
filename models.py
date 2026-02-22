import numpy as np

def calculate_slope_stability(xc, yc, R, dam_x, dam_y, water_x=None, water_y=None, gamma=18, gamma_w=9.81, c=15, phi=25):
    # 1. FIND INTERSECTIONS
    x_scan = np.linspace(xc - R + 0.01, xc + R - 0.01, 1000)
    y_dam_scan = np.interp(x_scan, dam_x, dam_y)
    y_circ_scan = yc - np.sqrt(R**2 - (x_scan - xc)**2)
    
    diff = y_dam_scan - y_circ_scan
    sign_changes = np.where(np.diff(np.sign(diff)))[0]
    
    if len(sign_changes) < 2:
        return None, []
    
    x_start, x_end = x_scan[sign_changes[0]], x_scan[sign_changes[-1]]
    
    # 2. DISCRETIZE INTO SLICES
    num_slices = 30
    slice_edges = np.linspace(x_start, x_end, num_slices + 1)
    b = (x_end - x_start) / num_slices
    phi_rad = np.radians(phi)
    
    slices = []
    for i in range(num_slices):
        x_mid = (slice_edges[i] + slice_edges[i+1]) / 2
        y_top = np.interp(x_mid, dam_x, dam_y)
        y_bot = yc - np.sqrt(R**2 - (x_mid - xc)**2)
        h = max(0, y_top - y_bot)
        
        # Pore pressure u
        u = 0
        if water_x is not None and water_y is not None:
            y_water = np.interp(x_mid, water_x, water_y)
            u = max(0, (y_water - y_bot) * gamma_w)

        W = h * b * gamma
        alpha_rad = np.arcsin((xc - x_mid) / R)
        
        slices.append({
            'W': W, 'alpha_deg': np.degrees(alpha_rad), 'b': b, 
            'u': u, 'x_mid': x_mid, 'h': h, 'y_bot': y_bot
        })

    # 3. BISHOP SOLVER
    fs = 1.2 # Initial guess
    for _ in range(20):
        num, den = 0, 0
        for s in slices:
            a_rad = np.radians(s['alpha_deg'])
            den += s['W'] * np.sin(a_rad)
            m_alpha = np.cos(a_rad) + (np.sin(a_rad) * np.tan(phi_rad) / fs)
            resisting = (c * s['b'] + (s['W'] - s['u'] * s['b']) * np.tan(phi_rad)) / m_alpha
            num += resisting
        
        if den == 0: return 0, slices
        new_fs = num / den
        if abs(new_fs - fs) < 0.001: break
        fs = new_fs
        
    return round(fs, 3), slices
