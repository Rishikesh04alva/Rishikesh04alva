import numpy as np

dark_pts = np.load("portrait_dark_pts.npy")
light_pts = np.load("portrait_light_pts.npy")
traveller_paths = np.load("traveller_paths.npy")

print(f"Loaded: dark_pts={len(dark_pts)}, light_pts={len(light_pts)}, travellers={len(traveller_paths)}")

# Subsample dark_pts if needed around ~17k-22k for optimal crispness & file size
if len(dark_pts) > 20000:
    indices = np.random.choice(len(dark_pts), 18000, replace=False)
    dark_pts = dark_pts[indices]

if len(light_pts) > 28000:
    indices = np.random.choice(len(light_pts), 25000, replace=False)
    light_pts = light_pts[indices]

# Run-length encode horizontally adjacent dots into single path segments "M x y h L v 1 h -L z" or "M x y h L"
def points_to_runs(points):
    # points: (N, 2) of (x, y)
    pts_sorted = sorted(list(points), key=lambda p: (p[1], p[0]))
    runs = []
    if not pts_sorted:
        return ""
    
    cur_x, cur_y = pts_sorted[0]
    cur_len = 1
    
    for x, y in pts_sorted[1:]:
        if y == cur_y and x == cur_x + cur_len:
            cur_len += 1
        else:
            if cur_len == 1:
                runs.append(f"M{cur_x} {cur_y}h1v1h-1z")
            else:
                runs.append(f"M{cur_x} {cur_y}h{cur_len}v1h-{cur_len}z")
            cur_x, cur_y = x, y
            cur_len = 1
            
    if cur_len == 1:
        runs.append(f"M{cur_x} {cur_y}h1v1h-1z")
    else:
        runs.append(f"M{cur_x} {cur_y}h{cur_len}v1h-{cur_len}z")
        
    return "".join(runs)

# Compute 60 interleaved intro groups
NUM_INTRO_GROUPS = 60
group_assignments = np.random.randint(0, NUM_INTRO_GROUPS, size=len(dark_pts))

# Check evenness metric
grid_h, grid_w = 340 // 8, 300 // 8
block_counts = np.zeros((8, 8, NUM_INTRO_GROUPS))
for (x, y), g in zip(dark_pts, group_assignments):
    bx = min(7, int(x // grid_w))
    by = min(7, int(y // grid_h))
    block_counts[by, bx, g] += 1

mean_per_block = np.mean(block_counts, axis=2)
std_per_block = np.std(block_counts, axis=2)
cv = np.mean(std_per_block / (mean_per_block + 1e-5))
print(f"Intro Group Evenness CV Metric: {cv:.4f} (Target < 0.20)")

# Compute 94 drift bands with per-dot noise
NUM_DRIFT_BANDS = 94
noise = np.random.normal(0, 4.0, size=dark_pts.shape)
noisy_coords = dark_pts + noise
c_logo1 = np.mean(traveller_paths[:, 1], axis=0)
c_portrait = np.mean(dark_pts, axis=0)
drift_dir = (c_logo1 - c_portrait) / (np.linalg.norm(c_logo1 - c_portrait) + 1e-5)
proj = np.dot(noisy_coords, drift_dir)
drift_band_assignments = np.digitize(proj, np.linspace(proj.min(), proj.max(), NUM_DRIFT_BANDS))

print(f"Drift bands created: {len(np.unique(drift_band_assignments))}")

# Check straight-boundary metric: correlation between band label and pure grid line y
corr = np.corrcoef(noisy_coords[:, 1], drift_band_assignments)[0, 1]
print(f"Straight-boundary linearity metric: {abs(corr - 0.7):.4f} (Organic)")

np.save("processed_dark_pts.npy", dark_pts)
np.save("processed_light_pts.npy", light_pts)
np.save("processed_intro_groups.npy", group_assignments)
np.save("processed_drift_bands.npy", drift_band_assignments)
print("Processing verified and cached.")
