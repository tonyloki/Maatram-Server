"""Analyze exact text, typography, colors, and visual components in reference hero banners."""

from PIL import Image
import numpy as np

def inspect_details(img_path):
    img = Image.open(img_path).convert("RGB")
    arr = np.array(img)
    w, h = img.size
    print(f"\n--- Detailed Inspection: {img_path} ({w}x{h}) ---")

    # Sample top badge
    # Sample greeting text
    # Sample button / link
    # Find bounding box of non-background content
    bg = arr[0, 0] # top left pixel of the slice
    print(f"Top-Left Pixel: RGB={bg.tolist()}")

    # Find unique colors
    # Get histogram of prominent colors
    unique_colors, counts = np.unique(arr.reshape(-1, 3), axis=0, return_counts=True)
    idx = np.argsort(-counts)
    print("Top 5 Colors:")
    for i in range(min(5, len(idx))):
        c = unique_colors[idx[i]]
        print(f"   RGB({c[0]}, {c[1]}, {c[2]}) : {counts[idx[i]]} px")

inspect_details("docs/design/recreation/crops/ref_dash_hero_slice_left.png")
inspect_details("docs/design/recreation/crops/ref_dash_hero_slice_right.png")
inspect_details("docs/design/recreation/crops/ref_events_hero_slice_left.png")
inspect_details("docs/design/recreation/crops/ref_events_hero_slice_right.png")
inspect_details("docs/design/recreation/crops/ref_activity_hero_slice_left.png")
inspect_details("docs/design/recreation/crops/ref_activity_hero_slice_right.png")

