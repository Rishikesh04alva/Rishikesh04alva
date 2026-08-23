import base64
import io
from PIL import Image, ImageOps, ImageEnhance

# Load original user photo
img = Image.open('ChatGPT Image Aug 15, 2026, 03_17_43 PM.png').convert('RGB')
w, h = img.size
WIDTH, HEIGHT = 400, 492

# Crop head + upper body centered
crop_top = int(h * 0.04)
crop_bottom = int(h * 0.90)
crop_h = crop_bottom - crop_top
crop_w = int(crop_h * (WIDTH / HEIGHT))
crop_left = max(0, (w - crop_w) // 2)
crop_right = min(w, crop_left + crop_w)

img_cropped = img.crop((crop_left, crop_top, crop_right, crop_bottom))
img_resized = img_cropped.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)

# Dark mode version: slightly higher contrast and rich tone
enhancer = ImageEnhance.Contrast(img_resized)
img_dark = enhancer.enhance(1.15)
buf_dark = io.BytesIO()
img_dark.save(buf_dark, format='JPEG', quality=88, optimize=True)
b64_dark = base64.b64encode(buf_dark.getvalue()).decode('ascii')

# Light mode version: crisp clean tone
enhancer_light = ImageEnhance.Contrast(img_resized)
img_light = enhancer_light.enhance(1.08)
buf_light = io.BytesIO()
img_light.save(buf_light, format='JPEG', quality=88, optimize=True)
b64_light = base64.b64encode(buf_light.getvalue()).decode('ascii')

def render_svg(is_dark=True):
    b64_img = b64_dark if is_dark else b64_light
    bg_start = "#0A101F" if is_dark else "#F8FAFC"
    bg_end = "#0C1426" if is_dark else "#F1F5F9"
    window_border = "#070B16" if is_dark else "#E2E8F0"
    header_bg = "#0B1222" if is_dark else "#FFFFFF"
    header_line = "rgba(255,255,255,0.12)" if is_dark else "rgba(0,0,0,0.08)"
    header_title = "#94A3B8" if is_dark else "#64748B"
    frame_stroke = "#22D3EE" if is_dark else "#0891B2"
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
  <stop offset="0" stop-color="#7C3AED"/>
  <stop offset="0.5" stop-color="#22D3EE"/>
  <stop offset="1" stop-color="#10B981"/>
</linearGradient>
<linearGradient id="panelGrad" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{bg_start}"/>
  <stop offset="1" stop-color="{bg_end}"/>
</linearGradient>
<clipPath id="winClip">
  <rect x="2" y="2" width="1176" height="606" rx="18"/>
</clipPath>
<clipPath id="photoClip">
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
<image href="data:image/jpeg;base64,{b64_img}" x="36" y="84" width="400" height="492" preserveAspectRatio="xMidYMid slice" clip-path="url(#photoClip)"/>
<rect x="36" y="84" width="400" height="492" rx="12" fill="none" stroke="{frame_stroke}" stroke-width="2" opacity="0.6"/>

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

<!-- Accent Border Glow -->
<rect x="3" y="3" width="1174" height="604" rx="17" fill="none" stroke="url(#accent)" stroke-width="2"/>
</g>
</svg>'''

    return svg

with open('dark.svg', 'w', encoding='utf-8') as f:
    f.write(render_svg(is_dark=True))

with open('light.svg', 'w', encoding='utf-8') as f:
    f.write(render_svg(is_dark=False))

print("Rendered HD photo facecard dark.svg and light.svg!")
