from PIL import Image, ImageOps, ImageFilter
import numpy as np

# Load user photo
img = Image.open('ChatGPT Image Aug 15, 2026, 03_17_43 PM.png').convert('RGB')
w, h = img.size

# Target portrait dimensions in SVG: width=322, height=340
WIDTH, HEIGHT = 322, 340

# Crop head + upper torso centered
crop_top = int(h * 0.04)
crop_bottom = int(h * 0.90)
crop_h = crop_bottom - crop_top
crop_w = int(crop_h * (WIDTH / HEIGHT))
crop_left = max(0, (w - crop_w) // 2)
crop_right = min(w, crop_left + crop_w)

img_cropped = img.crop((crop_left, crop_top, crop_right, crop_bottom))
img_resized = img_cropped.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)

# Preprocessing: contrast + autocontrast + unsharp mask
img_gray = img_resized.convert('L')
img_auto = ImageOps.autocontrast(img_gray, cutoff=1)
arr_gray = np.array(img_auto, dtype=np.float32)
mean_val = np.mean(arr_gray)
arr_gray = np.clip((arr_gray - mean_val) * 1.35 + mean_val, 0, 255)
img_contrast = Image.fromarray(arr_gray.astype(np.uint8))
img_sharp = img_contrast.filter(ImageFilter.UnsharpMask(radius=3, percent=140))

# Serpentine Floyd-Steinberg Dithering
def dither_serpentine(im_gray, dark_mode=True):
    arr = np.array(im_gray, dtype=np.float32).copy()
    h_dim, w_dim = arr.shape
    dithered = np.zeros((h_dim, w_dim), dtype=np.uint8)

    for y in range(h_dim):
        x_range = range(w_dim) if y % 2 == 0 else range(w_dim - 1, -1, -1)
        direction = 1 if y % 2 == 0 else -1

        for x in x_range:
            old_val = arr[y, x]
            if dark_mode:
                quant_val = 1 if old_val > 115 else 0
                target_val = 255 if quant_val == 1 else 0
            else:
                quant_val = 1 if old_val < 140 else 0
                target_val = 0 if quant_val == 1 else 255

            dithered[y, x] = quant_val
            err = old_val - target_val

            if 0 <= x + direction < w_dim:
                arr[y, x + direction] += err * (7.0 / 16.0)
            if y + 1 < h_dim:
                if 0 <= x - direction < w_dim:
                    arr[y + 1, x - direction] += err * (3.0 / 16.0)
                arr[y + 1, x] += err * (5.0 / 16.0)
                if 0 <= x + direction < w_dim:
                    arr[y + 1, x + direction] += err * (1.0 / 16.0)

    return dithered

dither_dark = dither_serpentine(img_sharp, dark_mode=True)
dither_light = dither_serpentine(img_sharp, dark_mode=False)

def grid_to_runs(binary_grid):
    h_dim, w_dim = binary_grid.shape
    runs = []
    for y in range(h_dim):
        in_run = False
        start_x = 0
        for x in range(w_dim):
            if binary_grid[y, x] == 1:
                if not in_run:
                    in_run = True
                    start_x = x
            else:
                if in_run:
                    length = x - start_x
                    if length == 1:
                        runs.append(f"M{start_x} {y}h1v1h-1z")
                    else:
                        runs.append(f"M{start_x} {y}h{length}v1h-{length}z")
                    in_run = False
        if in_run:
            length = w_dim - start_x
            if length == 1:
                runs.append(f"M{start_x} {y}h1v1h-1z")
            else:
                runs.append(f"M{start_x} {y}h{length}v1h-{length}z")
    return "".join(runs)

dark_path_data = grid_to_runs(dither_dark)
light_path_data = grid_to_runs(dither_light)

# Build SVG
def render_full_banner(is_dark=True):
    path_d = dark_path_data if is_dark else light_path_data
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

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="610" viewBox="0 0 1180 610" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace" role="img" aria-label="Rishikesh R Alva — profile.sh --live">
<defs>
<linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#7C3AED"/>
  <stop offset="0.5" stop-color="#22D3EE"/>
  <stop offset="1" stop-color="#10B981"/>
</linearGradient>
<linearGradient id="panelGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{bg_start}"/><stop offset="1" stop-color="{bg_end}"/></linearGradient>
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
<rect x="36" y="84" width="400" height="492" rx="10" fill="{panel_bg}" stroke="{frame_stroke}"/>

<!-- Portrait Group: Centered inside 400x492 frame (x=36..436, y=84..576) -->
<g transform="translate(40, 100) scale(1.220, 1.340)" fill="{portrait_color}" shape-rendering="crispEdges">
  <path d="{path_d}"/>
</g>

<!-- Right Info Panel -->
<g transform="translate(0, 0)">
<text x="470" y="106" font-size="13" letter-spacing="2" fill="{system_info_title}">SYSTEM.INFO</text>
<line x1="566" y1="102" x2="1061" y2="102" stroke="{header_line}"/>
<text x="1125" y="106" text-anchor="end" font-size="12" fill="{live_badge_color}" font-weight="700">&#9679; LIVE</text>

<rect x="470" y="122" width="245" height="20" rx="4" fill="{("#4C1D95" if is_dark else "#E0E7FF")}"/>
<text x="479" y="136" font-size="14" font-weight="700" fill="{("#E9D5FF" if is_dark else "#4338CA")}">rishikeshalvahere@gmail.com</text>
<line x1="725" y1="130" x2="1125" y2="130" stroke="{header_line}"/>
'''

    rows_data = [
        ("Subject", "Rishikesh R Alva"),
        ("Role", "AI Engineer | Full-Stack Dev"),
        ("Origin", "Mangalore, Karnataka, India"),
        ("Education", "B Tech CSE (AI)"),
        ("Status", "Building + Learning + Shipping"),
        ("ToolChain", "VS Code, All AI tools, Git, Figma"),
        ("Core.Lang", "Python, JavaScript, TypeScript, C++"),
        ("Core.Frontend", "HTML, CSS, Javascript, React.js"),
        ("Core.Backend", "Python, Node.js, REST APIs"),
        ("Core.Database", "MongoDB, MySQL"),
        ("Core.Infra", "Vercel, Netlify, Git, Docker"),
        ("Grid.Mail", "rishikeshalvahere@gmail.com"),
        ("Grid.Portfolio", "rishikeshportfolioforpc.netlify.app"),
        ("Grid.LinkedIn", "rishikesh-r-alva-78543a426"),
        ("Grid.GitHub", "@Rishikesh04alva"),
        ("Grid.Instagram", "@rishixalva"),
        ("Grid.Twitter/X", "@AlvaRishihere"),
    ]

    y_pos = 160
    for label, val in rows_data:
        dots_count = max(4, 75 - len(label) - len(val))
        dots_str = "." * dots_count
        
        if label == "Grid.Mail":
            svg += f'''<text x="470" y="{y_pos}" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve"><tspan fill="{footer_text}">- Contact </tspan><tspan fill="{dot_leader_color}">---------------------------------------------------------------------</tspan></text>\n'''
            y_pos += 22

        svg += f'''<text x="470" y="{y_pos}" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve"><tspan fill="{label_color}">{label} </tspan><tspan fill="{dot_leader_color}"> {dots_str} </tspan><tspan fill="{val_color}" font-weight="600"> {val}</tspan></text>\n'''
        y_pos += 22

    svg += f'''<text x="470" y="577" font-size="14" fill="{footer_text}">&#9656; More about me &amp; projects below in README &#8595; <tspan fill="{cursor_color}">&#9608;</tspan></text>
</g>

<rect x="3" y="3" width="1174" height="604" rx="17" fill="none" stroke="url(#accent)" stroke-width="2"/>
</g>
</svg>'''

    return svg

with open('dark.svg', 'w', encoding='utf-8') as f:
    f.write(render_full_banner(is_dark=True))

with open('light.svg', 'w', encoding='utf-8') as f:
    f.write(render_full_banner(is_dark=False))

print("Rendered and wrote guaranteed 100% visible dark.svg and light.svg!")
