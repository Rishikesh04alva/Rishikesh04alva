import random
import math

def generate_snake_svg(is_dark=True):
    bg_color = "#0A101F" if is_dark else "#FFFFFF"
    grid_empty = "#1E293B" if is_dark else "#E2E8F0"
    snake_head = "#10B981"
    snake_body = "#34D399"
    snake_eye = "#0A101F" if is_dark else "#FFFFFF"
    
    # Palette levels
    if is_dark:
        colors = ["#1E293B", "#0E7490", "#06B6D4", "#22D3EE", "#38BDF8"]
    else:
        colors = ["#E2E8F0", "#BAE6FD", "#7DD3FC", "#38BDF8", "#0284C7"]

    # 53 columns x 7 rows grid
    cols = 53
    rows = 7
    cell_size = 11
    cell_gap = 3
    pad_x = 25
    pad_y = 25
    
    width = pad_x * 2 + cols * (cell_size + cell_gap) - cell_gap
    height = pad_y * 2 + rows * (cell_size + cell_gap) - cell_gap + 15
    
    # Seed reproducible random pattern resembling real commit activity
    random.seed(42)
    grid_data = []
    for r in range(rows):
        row = []
        for c in range(cols):
            # Higher activity towards recent weeks
            prob = (c / cols) * 0.7 + 0.15
            if random.random() < prob:
                level = random.choices([1, 2, 3, 4], weights=[40, 30, 20, 10])[0]
            else:
                level = 0
            row.append(level)
        grid_data.append(row)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background: {bg_color}; border-radius: 12px;">
<style>
  @keyframes snakeMove {{
    0% {{ transform: translate(0px, 0px); }}
    25% {{ transform: translate({cols * 7}px, 0px); }}
    50% {{ transform: translate({cols * 10}px, 42px); }}
    75% {{ transform: translate({cols * 4}px, 70px); }}
    100% {{ transform: translate(0px, 0px); }}
  }}
  .snake-body {{
    animation: snakeMove 16s ease-in-out infinite alternate;
  }}
</style>
<rect width="{width}" height="{height}" fill="{bg_color}" rx="12" />
<g transform="translate({pad_x}, {pad_y})">
'''
    # Render contribution cells
    for r in range(rows):
        for c in range(cols):
            x = c * (cell_size + cell_gap)
            y = r * (cell_size + cell_gap)
            level = grid_data[r][c]
            fill = colors[level]
            svg += f'  <rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" rx="2" fill="{fill}" />\n'

    # Animated Snake
    # Initial head at (300, 42)
    svg += f'''
  <!-- Snake Animation -->
  <g class="snake-body">
    <!-- Tail & Body segments -->
    <rect x="238" y="42" width="{cell_size}" height="{cell_size}" rx="2" fill="{snake_body}" opacity="0.6"/>
    <rect x="252" y="42" width="{cell_size}" height="{cell_size}" rx="2" fill="{snake_body}" opacity="0.8"/>
    <rect x="266" y="42" width="{cell_size}" height="{cell_size}" rx="2" fill="{snake_body}"/>
    <rect x="280" y="42" width="{cell_size}" height="{cell_size}" rx="3" fill="{snake_head}"/>
    <!-- Snake eyes -->
    <circle cx="288" cy="45" r="1.5" fill="{snake_eye}"/>
    <circle cx="288" cy="50" r="1.5" fill="{snake_eye}"/>
  </g>
</g>
<text x="{width - 25}" y="{height - 10}" text-anchor="end" font-family="ui-monospace, monospace" font-size="10" fill="{('#64748B' if is_dark else '#94A3B8')}">Rishikesh04alva &bull; contribution snake</text>
</svg>'''
    return svg

# Generate all output targets
with open('snake-dark.svg', 'w', encoding='utf-8') as f:
    f.write(generate_snake_svg(is_dark=True))

with open('snake-light.svg', 'w', encoding='utf-8') as f:
    f.write(generate_snake_svg(is_dark=False))

with open('github-contribution-grid-snake-dark.svg', 'w', encoding='utf-8') as f:
    f.write(generate_snake_svg(is_dark=True))

with open('github-contribution-grid-snake.svg', 'w', encoding='utf-8') as f:
    f.write(generate_snake_svg(is_dark=False))

print("Generated all snake game SVGs successfully!")
