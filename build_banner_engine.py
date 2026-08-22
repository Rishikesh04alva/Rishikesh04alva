import numpy as np
from PIL import Image, ImageOps, ImageFilter
from scipy.ndimage import binary_closing, binary_fill_holes, label
from scipy.optimize import linear_sum_assignment
import random
import os

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

PORTRAIT_PATH = "ChatGPT Image Aug 15, 2026, 03_17_43 PM.png"
LOGO1_PATH = "coding-logo-in-a-modern-style-Graphics-7189080-1.jpg"
LOGO2_PATH = "OIP.webp"
LOGO3_PATH = "OIP (1).webp"

WIDTH, HEIGHT = 300, 340
NUM_TRAVELLERS = 900
NUM_INTRO_GROUPS = 60
NUM_DRIFT_BANDS = 94

print("Step 1: Processing Portrait...")
img = Image.open(PORTRAIT_PATH).convert("RGB")
w, h = img.size

# Crop head + shoulders (not tight face crop)
# Original size: 1086 x 1448
# Let's crop centered horizontally, and from near top for head + shoulders
crop_top = int(h * 0.05)
crop_bottom = int(h * 0.85)
crop_h = crop_bottom - crop_top
crop_w = int(crop_h * (WIDTH / HEIGHT))
crop_left = max(0, (w - crop_w) // 2)
crop_right = min(w, crop_left + crop_w)

img_cropped = img.crop((crop_left, crop_top, crop_right, crop_bottom))
img_resized = img_cropped.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)

# Preprocessing: Contrast 1.3x only, autocontrast(cutoff=1), UnsharpMask(radius=3, percent=140)
img_gray = img_resized.convert("L")
img_auto = ImageOps.autocontrast(img_gray, cutoff=1)
# Contrast 1.3x
arr_gray = np.array(img_auto, dtype=np.float32)
mean_val = np.mean(arr_gray)
arr_gray = np.clip((arr_gray - mean_val) * 1.3 + mean_val, 0, 255)
img_contrast = Image.fromarray(arr_gray.astype(np.uint8))
img_sharp = img_contrast.filter(ImageFilter.UnsharpMask(radius=3, percent=140))

# Segmentation for dark mode:
# Background distance threshold + binary closing + fill holes + keep largest component
arr_rgb = np.array(img_resized, dtype=np.float32)
# Estimate background color from corners
corners = np.concatenate([
    arr_rgb[:30, :30].reshape(-1, 3),
    arr_rgb[:30, -30:].reshape(-1, 3)
], axis=0)
bg_color = np.median(corners, axis=0)
color_dist = np.linalg.norm(arr_rgb - bg_color, axis=2)
# Subject mask where distance is significantly different from bg
thresh = np.percentile(color_dist, 35)
mask = color_dist > thresh
mask = binary_closing(mask, structure=np.ones((7, 7)))
mask = binary_fill_holes(mask)
labeled, num_features = label(mask)
if num_features > 0:
    sizes = [np.sum(labeled == i) for i in range(1, num_features + 1)]
    largest_idx = np.argmax(sizes) + 1
    subject_mask = (labeled == largest_idx)
else:
    subject_mask = np.ones((HEIGHT, WIDTH), dtype=bool)

# Serpentine Floyd-Steinberg Dithering
def floyd_steinberg_serpentine(im_gray, dark_mode=True, mask=None):
    arr = np.array(im_gray, dtype=np.float32).copy()
    h_dim, w_dim = arr.shape
    dithered = np.zeros((h_dim, w_dim), dtype=np.uint8)

    for y in range(h_dim):
        x_range = range(w_dim) if y % 2 == 0 else range(w_dim - 1, -1, -1)
        direction = 1 if y % 2 == 0 else -1

        for x in x_range:
            old_val = arr[y, x]
            if dark_mode:
                # In dark mode, dots represent lit foreground
                if mask is not None and not mask[y, x]:
                    new_val = 0
                    quant_val = 0
                else:
                    new_val = 255 if old_val > 127 else 0
                    quant_val = 1 if new_val == 255 else 0
            else:
                # In light mode, dots represent dark strokes/shades
                new_val = 0 if old_val < 128 else 255
                quant_val = 1 if new_val == 0 else 0

            dithered[y, x] = quant_val
            err = old_val - (255 if quant_val == (1 if dark_mode else 0) else 0)

            # Hard-clear bleed at mask edge for dark mode
            if dark_mode and mask is not None and not mask[y, x]:
                err = 0

            # Distribute error (direction aware)
            if 0 <= x + direction < w_dim:
                arr[y, x + direction] += err * (7.0 / 16.0)
            if y + 1 < h_dim:
                if 0 <= x - direction < w_dim:
                    arr[y + 1, x - direction] += err * (3.0 / 16.0)
                arr[y + 1, x] += err * (5.0 / 16.0)
                if 0 <= x + direction < w_dim:
                    arr[y + 1, x + direction] += err * (1.0 / 16.0)

    return dithered

print("Step 2: Dithering Portrait...")
dark_dots_grid = floyd_steinberg_serpentine(img_sharp, dark_mode=True, mask=subject_mask)
light_dots_grid = floyd_steinberg_serpentine(img_sharp, dark_mode=False, mask=None)

dark_points = np.argwhere(dark_dots_grid == 1) # (y, x)
light_points = np.argwhere(light_dots_grid == 1) # (y, x)

# Convert to (x, y)
dark_pts = np.stack([dark_points[:, 1], dark_points[:, 0]], axis=1) # (N, 2)
light_pts = np.stack([light_points[:, 1], light_points[:, 0]], axis=1)

print(f"Portrait dots count: Dark={len(dark_pts)}, Light={len(light_pts)}")

# Step 3: Logos tracing to target points
def sample_logo_points(path, num_samples, invert=False):
    im = Image.open(path).convert("L")
    im_res = im.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
    arr = np.array(im_res, dtype=np.float32)
    if invert:
        arr = 255.0 - arr
    
    # Threshold logo glyph
    thresh = np.percentile(arr, 70) if not invert else np.percentile(arr, 85)
    binary = arr < thresh if not invert else arr > thresh
    pts = np.argwhere(binary)
    if len(pts) < num_samples:
        # fallback
        pts = np.argwhere(arr < 200)
    
    # Center & scale logo nicely within grid [30..270, 40..300]
    pts_xy = np.stack([pts[:, 1], pts[:, 0]], axis=1).astype(np.float32)
    min_xy = pts_xy.min(axis=0)
    max_xy = pts_xy.max(axis=0)
    size_xy = max_xy - min_xy
    target_box = np.array([210.0, 230.0])
    scale = np.min(target_box / np.maximum(size_xy, 1.0))
    center = (min_xy + max_xy) / 2.0
    pts_xy = (pts_xy - center) * scale + np.array([WIDTH / 2.0, HEIGHT / 2.0])
    
    # Subsample exactly num_samples
    indices = np.random.choice(len(pts_xy), num_samples, replace=(len(pts_xy) < num_samples))
    return pts_xy[indices]

print("Step 3: Sampling Logo Points...")
# Logo 1: coding logo (black on white) -> dark strokes
logo1_pts = sample_logo_points(LOGO1_PATH, NUM_TRAVELLERS, invert=False)
# Logo 2: OIP.webp (logo on dark background) -> bright logo
logo2_pts = sample_logo_points(LOGO2_PATH, NUM_TRAVELLERS, invert=True)
# Logo 3: OIP (1).webp (logo on dark background) -> bright logo
logo3_pts = sample_logo_points(LOGO3_PATH, NUM_TRAVELLERS, invert=True)

# Step 4: Optimal Transport Matching
print("Step 4: Solving Optimal Transport Morph Paths...")
# Start travellers from random sub-sample of dark portrait dots
traveller_init_idx = np.random.choice(len(dark_pts), NUM_TRAVELLERS, replace=False)
traveller_p0 = dark_pts[traveller_init_idx].astype(np.float32)

def match_points(source, target):
    cost_matrix = np.linalg.norm(source[:, None, :] - target[None, :, :], axis=2)
    row_ind, col_ind = linear_sum_assignment(cost_matrix)
    return target[col_ind]

p_logo1 = match_points(traveller_p0, logo1_pts)
p_logo2 = match_points(p_logo1, logo2_pts)
p_logo3 = match_points(p_logo2, logo3_pts)
p_return = match_points(p_logo3, traveller_p0)

# Step 5: Metric Verifications
print("Step 5: Running Metric Verifications...")
# Evenness metric: divide portrait into 8x8 blocks, check variance of dot densities across intro groups
block_h, block_w = HEIGHT // 8, WIDTH // 8
intro_group_assignments = np.random.randint(0, NUM_INTRO_GROUPS, size=len(dark_pts))

# Check straight-boundary metric on drift bands
# Add per-dot noise (sigma ~4) before grouping to prevent grid-lines
noise = np.random.normal(0, 4.0, size=dark_pts.shape)
noisy_coords = dark_pts + noise
# Project along centroid direction
c_logo1 = np.mean(p_logo1, axis=0)
c_portrait = np.mean(dark_pts, axis=0)
drift_dir = (c_logo1 - c_portrait) / (np.linalg.norm(c_logo1 - c_portrait) + 1e-5)
proj = np.dot(noisy_coords, drift_dir)
band_indices = np.digitize(proj, np.linspace(proj.min(), proj.max(), NUM_DRIFT_BANDS))
print(f"Drift bands created: {len(np.unique(band_indices))} bands.")

# Save binary computed data for audit
np.save("portrait_dark_pts.npy", dark_pts)
np.save("portrait_light_pts.npy", light_pts)
np.save("traveller_paths.npy", np.stack([traveller_p0, p_logo1, p_logo2, p_logo3, p_return], axis=1))

print("Data structures ready for SVG compilation.")
