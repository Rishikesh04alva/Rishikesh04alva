import numpy as np
from PIL import Image, ImageOps, ImageFilter, ImageEnhance
from scipy.ndimage import binary_closing, binary_fill_holes, binary_opening
import xml.etree.ElementTree as ET

PORTRAIT_PATH = "ChatGPT Image Aug 15, 2026, 03_17_43 PM.png"
WIDTH, HEIGHT = 320, 394 # 320 x 394 scaled 1.25x = 400 x 492.5 (exact fit for 400x492 card)

print("Step 1: Loading & Cropping user photo...")
img = Image.open(PORTRAIT_PATH).convert("RGB")
w, h = img.size

# Frame head + upper torso
crop_top = int(h * 0.05)
crop_bottom = int(h * 0.85)
crop_h = crop_bottom - crop_top
crop_w = int(crop_h * (WIDTH / HEIGHT))
crop_left = max(0, (w - crop_w) // 2)
crop_right = min(w, crop_left + crop_w)

img_cropped = img.crop((crop_left, crop_top, crop_right, crop_bottom))
img_resized = img_cropped.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)

print("Step 2: Clean background segmentation mask...")
arr_rgb = np.array(img_resized, dtype=np.float32)
r, g, b = arr_rgb[:, :, 0], arr_rgb[:, :, 1], arr_rgb[:, :, 2]
max_c = np.maximum(np.maximum(r, g), b)
min_c = np.minimum(np.minimum(r, g), b)
sat = max_c - min_c
gray = 0.299 * r + 0.587 * g + 0.114 * b

# Background studio backdrop: low saturation AND mid-gray
is_bg = (sat < 14) & (gray > 65) & (gray < 175)
is_subject = ~is_bg
mask = binary_closing(is_subject, structure=np.ones((7, 7)))
mask = binary_opening(mask, structure=np.ones((5, 5)))
mask = binary_fill_holes(mask)

print("Step 3: Detail enhancement...")
img_gray = img_resized.convert("L")
enhancer = ImageEnhance.Contrast(img_gray)
img_contrast = enhancer.enhance(1.45)
img_sharp = img_contrast.filter(ImageFilter.UnsharpMask(radius=2.2, percent=170))
arr_gray = np.array(img_sharp, dtype=np.float32)

print("Step 4: Serpentine Floyd-Steinberg Dithering...")
def dither_fs(arr, is_dark=True, mask=None):
    a = arr.copy()
    h_dim, w_dim = a.shape
    out = np.zeros((h_dim, w_dim), dtype=np.uint8)
    
    for y in range(h_dim):
        x_range = range(w_dim) if y % 2 == 0 else range(w_dim - 1, -1, -1)
        direction = 1 if y % 2 == 0 else -1
        
        for x in x_range:
            if mask is not None and not mask[y, x]:
                out[y, x] = 0
                continue
                
            old = a[y, x]
            if is_dark:
                thresh = 112
                quant = 1 if old > thresh else 0
                new = 255 if quant == 1 else 0
            else:
                thresh = 138
                quant = 1 if old < thresh else 0
                new = 0 if quant == 1 else 255
                
            out[y, x] = quant
            err = (old - new)
            
            if 0 <= x + direction < w_dim: a[y, x + direction] += err * (7.0 / 16.0)
            if y + 1 < h_dim:
                if 0 <= x - direction < w_dim: a[y + 1, x - direction] += err * (3.0 / 16.0)
                a[y + 1, x] += err * (5.0 / 16.0)
                if 0 <= x + direction < w_dim: a[y + 1, x + direction] += err * (1.0 / 16.0)
    return out

d_dark = dither_fs(arr_gray, is_dark=True, mask=mask)
d_light = dither_fs(arr_gray, is_dark=False, mask=mask)

dark_points = np.argwhere(d_dark == 1)
light_points = np.argwhere(d_light == 1)

dark_pts = np.stack([dark_points[:, 1], dark_points[:, 0]], axis=1)
light_pts = np.stack([light_points[:, 1], light_points[:, 0]], axis=1)

print(f"Total dots: Dark={len(dark_pts)}, Light={len(light_pts)}")

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

# Compute 40 shimmer groups
NUM_GROUPS = 40
np.random.seed(42)
group_idx_dark = np.random.randint(0, NUM_GROUPS, size=len(dark_pts))
group_idx_light = np.random.randint(0, NUM_GROUPS, size=len(light_pts))

def render_banner(is_dark=True):
    pts = dark_pts if is_dark else light_pts
    group_idx = group_idx_dark if is_dark else group_idx_light
    
    portrait_color = "#22D3EE" if is_dark else "#0891B2"
    bg_start = "#0A101F" if is_dark else "#F8FAFC"
    bg_end = "#0C1426" if is_dark else "#F1F5F9"
    window_border = "#070B16" if is_dark else "#E2E8F0"
    header_bg = "#0B1222" if is_dark else "#FFFFFF"
    header_line = "rgba(255,255,255,0.12)" if is_dark else "rgba(0,0,0,0.08)"
    header_title = "#94A3B8" if is_dark else "#64748B"
    frame_stroke = "rgba(34,211,238,0.5)" if is_dark else "rgba(8,145,178,0.4)"
    panel_bg = "#0A101F" if is_dark else "#FFFFFF"
    system_info_title = "#22D3EE" if is_dark else "#0891B2"
    dot_leader_color = "rgba(148,163,184,0.35)" if is_dark else "rgba(15,23,42,0.25)"
    label_color = "#22D3EE" if is_dark else "#0891B2"
    val_color = "#F8FAFC" if is_dark else "#0F172A"
    live_badge_color = "#F87171" if is_dark else "#EF4444"
    footer_text = "#94A3B8" if is_dark else "#64748B"
    cursor_color = "#22D3EE" if is_dark else "#06B6D4"

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="610" viewBox="0 0 1180 610" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" role="img" aria-label="Rishikesh R Alva - Developer Profile">
<defs>
<linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0%" stop-color="#7C3AED"/>
  <stop offset="50%" stop-color="#22D3EE"/>
  <stop offset="100%" stop-color="#10B981"/>
</linearGradient>
<linearGradient id="panelGrad" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{bg_start}"/>
  <stop offset="1" stop-color="{bg_end}"/>
</linearGradient>
<clipPath id="winClip">
  <rect x="2" y="2" width="1176" height="606" rx="18"/>
</clipPath>
<clipPath id="portraitClip">
  <rect x="36" y="84" width="400" height="492" rx="12"/>
</clipPath>
</defs>

<!-- Window Frame -->
<rect x="2" y="2" width="1176" height="606" rx="18" fill="{window_border}"/>
<g clip-path="url(#winClip)">
<rect x="2" y="2" width="1176" height="606" fill="url(#panelGrad)"/>
<rect x="2" y="2" width="1176" height="46" fill="{header_bg}"/>
<line x1="2" y1="48" x2="1178" y2="48" stroke="{header_line}"/>

<!-- Mac Window Controls -->
<circle cx="30" cy="25.0" r="5.5" fill="#ff5f56"/>
<circle cx="50" cy="25.0" r="5.5" fill="#ffbd2e"/>
<circle cx="70" cy="25.0" r="5.5" fill="#27c93f"/>
<text x="590.0" y="29.0" text-anchor="middle" font-size="12" fill="{header_title}">rishikeshalvahere@gmail.com - % ./profile.sh --live</text>

<!-- Left Photo Frame (Visual Map) -->
<text x="38" y="74" font-size="10" letter-spacing="3" fill="#475569">VISUAL.MAP</text>
<rect x="36" y="84" width="400" height="492" rx="12" fill="{panel_bg}" stroke="{frame_stroke}" stroke-width="1.5"/>

<!-- Face Portrait Dither Artwork with Shimmer Reveal (100% Native SVG Path) -->
<g clip-path="url(#portraitClip)">
  <g transform="translate(36, 84) scale(1.25, 1.25)" fill="{portrait_color}" shape-rendering="crispEdges">
'''

    # Interleaved shimmer fade-in
    for g in range(NUM_GROUPS):
        sub_pts = pts[group_idx == g]
        path_d = points_to_runs(sub_pts)
        if path_d:
            t_begin = 0.10 + (g * 0.025)
            svg += f'''    <g opacity="0"><animate attributeName="opacity" values="0;1" dur="0.6s" begin="{t_begin:.2f}s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines=".4 0 .2 1"/><path d="{path_d}"/></g>\n'''

    svg += f'''  </g>
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
        ("Subject", "Rishikesh R Alva", 0.75),
        ("Role", "AI Engineer | Full-Stack Dev", 0.85),
        ("Origin", "Mangalore, Karnataka, India", 0.95),
        ("Education", "B Tech CSE (AI)", 1.05),
        ("Status", "Building + Learning + Shipping", 1.15),
        ("ToolChain", "VS Code, All AI tools, Git, Figma", 1.25),
        ("Core.Lang", "Python, JavaScript, TypeScript, C++", 1.45),
        ("Core.Frontend", "HTML, CSS, Javascript, React.js", 1.55),
        ("Core.Backend", "Python, Node.js, REST APIs", 1.65),
        ("Core.Database", "MongoDB, MySQL", 1.75),
        ("Core.Infra", "Vercel, Netlify, Git, Docker", 1.85),
        ("Grid.Mail", "rishikeshalvahere@gmail.com", 2.05),
        ("Grid.Portfolio", "rishikeshportfolioforpc.netlify.app", 2.15),
        ("Grid.LinkedIn", "rishikesh-r-alva-78543a426", 2.25),
        ("Grid.GitHub", "@Rishikesh04alva", 2.35),
        ("Grid.Instagram", "@rishixalva", 2.45),
        ("Grid.Twitter/X", "@AlvaRishihere", 2.55),
    ]

    y_pos = 160
    for label, val, begin_t in rows_data:
        dots_count = max(4, 75 - len(label) - len(val))
        dots_str = "." * dots_count
        
        if label == "Grid.Mail":
            svg += f'''<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.3s" begin="1.95s" fill="freeze"/><text x="470" y="{y_pos}" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve"><tspan fill="{footer_text}">- Contact </tspan><tspan fill="{dot_leader_color}">---------------------------------------------------------------------</tspan></text></g>\n'''
            y_pos += 22

        svg += f'''<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.3s" begin="{begin_t:.2f}s" fill="freeze"/><animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.3s" begin="{begin_t:.2f}s" fill="freeze"/><text x="470" y="{y_pos}" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve"><tspan fill="{label_color}">{label} </tspan><tspan fill="{dot_leader_color}"> {dots_str} </tspan><tspan fill="{val_color}" font-weight="600"> {val}</tspan></text></g>\n'''
        y_pos += 22

    svg += f'''<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="2.75s" fill="freeze"/><text x="470" y="577" font-size="14" fill="{footer_text}">&#9656; More about me &amp; projects below in README &#8595; <tspan fill="{cursor_color}">&#9608;</tspan></text></g>
</g>

<!-- Accent Border Glow -->
<rect x="3" y="3" width="1174" height="604" rx="17" fill="none" stroke="url(#accent)" stroke-width="2"/>
</g>
</svg>'''

    return svg

print("Step 5: Writing dark.svg & light.svg...")
dark_content = render_banner(is_dark=True)
with open('dark.svg', 'w', encoding='utf-8') as f:
    f.write(dark_content)

light_content = render_banner(is_dark=False)
with open('light.svg', 'w', encoding='utf-8') as f:
    f.write(light_content)

# Validate XML
ET.fromstring(dark_content)
ET.fromstring(light_content)
print("SUCCESS: Both dark.svg and light.svg are 100% VALID XML!")
print(f"Generated clean dark.svg ({len(dark_content)} bytes) and light.svg ({len(light_content)} bytes)!")
