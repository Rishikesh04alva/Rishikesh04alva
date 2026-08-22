import numpy as np

dark_pts = np.load("processed_dark_pts.npy")
light_pts = np.load("processed_light_pts.npy")
intro_groups = np.load("processed_intro_groups.npy")
drift_bands = np.load("processed_drift_bands.npy")
traveller_paths = np.load("traveller_paths.npy")

def points_to_runs(pts):
    if len(pts) == 0:
        return ""
    pts_sorted = sorted(list(pts), key=lambda p: (p[1], p[0]))
    runs = []
    cur_x, cur_y = pts_sorted[0]
    cur_len = 1
    for x, y in pts_sorted[1:]:
        if y == cur_y and x == cur_x + cur_len:
            cur_len += 1
        else:
            if cur_len == 1:
                runs.append(f"M{int(cur_x)} {int(cur_y)}h1v1h-1z")
            else:
                runs.append(f"M{int(cur_x)} {int(cur_y)}h{cur_len}v1h-{cur_len}z")
            cur_x, cur_y = x, y
            cur_len = 1
    if cur_len == 1:
        runs.append(f"M{int(cur_x)} {int(cur_y)}h1v1h-1z")
    else:
        runs.append(f"M{int(cur_x)} {int(cur_y)}h{cur_len}v1h-{cur_len}z")
    return "".join(runs)

def build_svg(is_dark=True):
    portrait_color = "#A78BFA" if is_dark else "#7C3AED"
    bg_start = "#0A101F" if is_dark else "#F8FAFC"
    bg_end = "#0C1426" if is_dark else "#F1F5F9"
    window_border = "#070B16" if is_dark else "#E2E8F0"
    header_bg = "#0B1222" if is_dark else "#FFFFFF"
    header_line = "rgba(255,255,255,0.10)" if is_dark else "rgba(0,0,0,0.08)"
    header_title = "#94A3B8" if is_dark else "#64748B"
    frame_stroke = "rgba(34,211,238,0.35)" if is_dark else "rgba(8,145,178,0.30)"
    panel_bg = "#0A101F" if is_dark else "#FFFFFF"
    system_info_title = "#22D3EE" if is_dark else "#0891B2"
    dot_leader_color = "rgba(148,163,184,0.35)" if is_dark else "rgba(15,23,42,0.25)"
    label_color = "#22D3EE" if is_dark else "#0891B2"
    val_color = "#F8FAFC" if is_dark else "#0F172A"
    live_badge_color = "#F87171" if is_dark else "#EF4444"
    footer_text = "#94A3B8" if is_dark else "#64748B"
    cursor_color = "#22D3EE" if is_dark else "#06B6D4"
    
    header = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="610" viewBox="0 0 1180 610" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace" role="img" aria-label="Rishikesh R Alva — profile.sh --live">
<defs>
<linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#7C3AED"><animate attributeName="stop-color" values="#7C3AED;#22D3EE;#10B981;#7C3AED" dur="10s" repeatCount="indefinite"/></stop>
  <stop offset="0.5" stop-color="#22D3EE"><animate attributeName="stop-color" values="#22D3EE;#10B981;#7C3AED;#22D3EE" dur="10s" repeatCount="indefinite"/></stop>
  <stop offset="1" stop-color="#10B981"><animate attributeName="stop-color" values="#10B981;#7C3AED;#22D3EE;#10B981" dur="10s" repeatCount="indefinite"/></stop>
</linearGradient>
<linearGradient id="panelGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{bg_start}"/><stop offset="1" stop-color="{bg_end}"/></linearGradient>
<filter id="glow8" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="8"/></filter>
<filter id="glow3" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="3"/></filter>
<filter id="txtGlow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="0.9" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<clipPath id="winClip"><rect x="2" y="2" width="1176" height="606" rx="18"/></clipPath>
</defs>
<rect x="2" y="2" width="1176" height="606" rx="18" fill="{window_border}"/>
<g clip-path="url(#winClip)">
<rect x="2" y="2" width="1176" height="606" fill="url(#panelGrad)"/>
<rect x="2" y="2" width="1176" height="46" fill="{header_bg}"/>
<line x1="2" y1="48" x2="1178" y2="48" stroke="{header_line}"/>
<circle cx="30" cy="25.0" r="5.5" fill="#ff5f56"/>
<circle cx="50" cy="25.0" r="5.5" fill="#ffbd2e"/>
<circle cx="70" cy="25.0" r="5.5" fill="#27c93f"/>
<text x="590.0" y="29.0" text-anchor="middle" font-size="12" fill="{header_title}">rishikeshalvahere@gmail.com - % ./profile.sh --live</text>
<text x="38" y="74" font-size="10" letter-spacing="3" fill="#475569">VISUAL.MAP</text>
<rect x="36" y="84" width="400" height="492" rx="10" fill="none" stroke="{label_color}" stroke-width="2" opacity="0.45" filter="url(#glow3)"/>
<rect x="36" y="84" width="400" height="492" rx="10" fill="{panel_bg}" stroke="{frame_stroke}"/>
'''

    # Portrait Layer 1: Intro (~3.2s) - 60 interleaved random groups
    portrait_intro = ['<g transform="translate(50,86) scale(1.2400,1.4471)" fill="' + portrait_color + '" shape-rendering="crispEdges">\n<set attributeName="opacity" to="0" begin="3.2s"/>\n']
    
    for g_id in range(60):
        g_mask = (intro_groups == g_id)
        g_pts = dark_pts[g_mask]
        path_d = points_to_runs(g_pts)
        if path_d:
            begin_t = 0.20 + (g_id * 0.033)
            portrait_intro.append(f'<g opacity="0"><animate attributeName="opacity" values="0;1" dur="0.9s" begin="{begin_t:.2f}s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines=".4 0 .2 1"/><path d="{path_d}"/></g>\n')
    portrait_intro.append('</g>\n')

    # Portrait Layer 2: 94 Drift Bands
    c_logo1 = np.mean(traveller_paths[:, 1], axis=0)
    c_port = np.mean(dark_pts, axis=0)
    drift_vec = (c_logo1 - c_port) * 0.42

    portrait_loop = ['<g transform="translate(50,86) scale(1.2400,1.4471)" fill="' + portrait_color + '" shape-rendering="crispEdges" opacity="0">\n']
    portrait_loop.append('<animate attributeName="opacity" values="0;1" dur="0.1s" begin="3.2s" fill="freeze"/>\n')
    
    unique_bands = np.unique(drift_bands)
    for b_id in unique_bands:
        b_mask = (drift_bands == b_id)
        b_pts = dark_pts[b_mask]
        path_d = points_to_runs(b_pts)
        if path_d:
            dx = drift_vec[0] * (0.8 + 0.4 * (b_id / len(unique_bands)))
            dy = drift_vec[1] * (0.8 + 0.4 * (b_id / len(unique_bands)))
            portrait_loop.append(f'''<g>
<animateTransform attributeName="transform" type="translate" values="0 0; 0 0; {dx:.1f} {dy:.1f}; {dx:.1f} {dy:.1f}; 0 0; 0 0" keyTimes="0; 0.21; 0.30; 0.88; 0.96; 1" dur="14.2s" begin="3.2s" repeatCount="indefinite"/>
<animate attributeName="opacity" values="1; 1; 0; 0; 0; 1; 1" keyTimes="0; 0.21; 0.30; 0.88; 0.94; 0.98; 1" dur="14.2s" begin="3.2s" repeatCount="indefinite"/>
<path d="{path_d}"/>
</g>\n''')
    portrait_loop.append('</g>\n')

    # Travellers Layer (Optimal Transport morphing across 3 logos)
    travellers_svg = ['<g transform="translate(50,86) scale(1.2400,1.4471)" fill="' + portrait_color + '" shape-rendering="crispEdges">\n']
    
    for i in range(len(traveller_paths)):
        p0 = traveller_paths[i, 0]
        p1 = traveller_paths[i, 1]
        p2 = traveller_paths[i, 2]
        p3 = traveller_paths[i, 3]
        pr = traveller_paths[i, 4]
        
        vals = f"{p0[0]:.1f} {p0[1]:.1f}; {p0[0]:.1f} {p0[1]:.1f}; {p1[0]:.1f} {p1[1]:.1f}; {p1[0]:.1f} {p1[1]:.1f}; {p2[0]:.1f} {p2[1]:.1f}; {p2[0]:.1f} {p2[1]:.1f}; {p3[0]:.1f} {p3[1]:.1f}; {p3[0]:.1f} {p3[1]:.1f}; {pr[0]:.1f} {pr[1]:.1f}; {p0[0]:.1f} {p0[1]:.1f}"
        
        travellers_svg.append(f'''<g opacity="0">
<animate attributeName="opacity" values="0; 0; 1; 1; 1; 1; 1; 1; 0; 0" keyTimes="0; 0.21; 0.29; 0.44; 0.52; 0.67; 0.75; 0.89; 0.97; 1" dur="14.2s" begin="3.2s" repeatCount="indefinite"/>
<animateTransform attributeName="transform" type="translate" values="{vals}" keyTimes="0; 0.21; 0.30; 0.44; 0.53; 0.67; 0.76; 0.90; 0.98; 1" dur="14.2s" begin="3.2s" repeatCount="indefinite"/>
<rect width="1.6" height="1.6" rx="0.3"/>
</g>\n''')
    travellers_svg.append('</g>\n')

    # Info Panel
    rows_data = [
        ("Subject", "Rishikesh R Alva", 0.90),
        ("Role", "AI Engineer | Full-Stack Dev", 1.02),
        ("Origin", "Mangalore, Karnataka, India", 1.14),
        ("Education", "B Tech CSE (AI)", 1.26),
        ("Status", "Building + Learning + Shipping", 1.38),
        ("ToolChain", "VS Code, All AI tools, Git, Figma", 1.50),
        ("Core.Lang", "Python, JavaScript, TypeScript, C++", 1.72),
        ("Core.Frontend", "HTML, CSS, Javascript, React.js", 1.84),
        ("Core.Backend", "Python, Node.js, REST APIs", 1.96),
        ("Core.Database", "MongoDB, MySQL", 2.08),
        ("Core.Infra", "Vercel, Netlify, Git, Docker", 2.20),
        ("Grid.Mail", "rishikeshalvahere@gmail.com", 2.54),
        ("Grid.Portfolio", "rishikeshportfolioforpc.netlify.app", 2.66),
        ("Grid.LinkedIn", "rishikesh-r-alva-78543a426", 2.78),
        ("Grid.GitHub", "@Rishikesh04alva", 2.90),
        ("Grid.Instagram", "@rishixalva", 3.02),
    ]

    info_panel = f'''<g transform="translate(0, 0)">
<text x="470" y="106" font-size="13" letter-spacing="2" fill="{system_info_title}" filter="url(#txtGlow)">SYSTEM.INFO</text>
<line x1="566" y1="102" x2="1061" y2="102" stroke="{header_line}"/>
<text x="1125" y="106" text-anchor="end" font-size="12" fill="{live_badge_color}" font-weight="700"><tspan>&#9679;</tspan> LIVE<animate attributeName="opacity" values="1;0.25;1" dur="1.6s" repeatCount="indefinite"/></text>

<rect x="470" y="122" width="245" height="20" rx="4" fill="{("#4C1D95" if is_dark else "#E0E7FF")}"/>
<text x="479" y="136" font-size="14" font-weight="700" fill="{("#E9D5FF" if is_dark else "#4338CA")}">rishikeshalvahere@gmail.com</text>
<line x1="725" y1="130" x2="1125" y2="130" stroke="{header_line}"/>
'''

    y_pos = 162
    for label, val, begin_t in rows_data:
        dots_count = max(5, 75 - len(label) - len(val))
        dots_str = "." * dots_count
        
        if label == "Grid.Mail":
            info_panel += f'''<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="2.42s" fill="freeze"/><text x="470" y="{y_pos}" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve"><tspan fill="{footer_text}">- Contact </tspan><tspan fill="{dot_leader_color}">---------------------------------------------------------------------</tspan></text></g>\n'''
            y_pos += 23

        info_panel += f'''<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="{begin_t:.2f}s" fill="freeze"/><animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="{begin_t:.2f}s" fill="freeze"/><text x="470" y="{y_pos}" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve"><tspan fill="{label_color}">{label} </tspan><tspan fill="{dot_leader_color}">{dots_str}</tspan><tspan fill="{val_color}" font-weight="600"> {val}</tspan></text></g>\n'''
        y_pos += 23

    info_panel += f'''<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.5s" begin="3.34s" fill="freeze"/>
<text x="470" y="577" font-size="14" fill="{footer_text}">&#9656; More about me &amp; projects below in README &#8595; <tspan fill="{cursor_color}">&#9608;<animate attributeName="fill-opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></tspan></text>
</g>
</g>
'''

    footer = f'''<rect x="3" y="3" width="1174" height="604" rx="17" fill="none" stroke="url(#accent)" stroke-width="3" opacity="0.55" filter="url(#glow8)"/>
<rect x="3" y="3" width="1174" height="604" rx="17" fill="none" stroke="url(#accent)" stroke-width="1.6"/>
</g>
</svg>'''

    full_svg = header + "".join(portrait_intro) + "".join(portrait_loop) + "".join(travellers_svg) + info_panel + footer
    return full_svg

dark_svg = build_svg(is_dark=True)
with open("dark.svg", "w", encoding="utf-8") as f:
    f.write(dark_svg)

light_svg = build_svg(is_dark=False)
with open("light.svg", "w", encoding="utf-8") as f:
    f.write(light_svg)

print("Regenerated clean dark.svg and light.svg.")
