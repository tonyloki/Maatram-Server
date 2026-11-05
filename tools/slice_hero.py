"""Inspect exact visual elements of reference hero banners."""

from PIL import Image

def examine_crop(crop_path, name):
    img = Image.open(crop_path)
    w, h = img.size
    print(f"\n=== Inspecting {name} ({w}x{h}) ===")
    
    # Save 4 horizontal slices to see left text vs right artwork
    # slice 1: Left column (0..600)
    # slice 2: Right artwork (600..1200)
    left = img.crop((0, 0, min(650, w), h))
    right = img.crop((min(650, w), 0, w, h))
    
    left.save(f"docs/design/recreation/crops/{name}_slice_left.png")
    right.save(f"docs/design/recreation/crops/{name}_slice_right.png")
    print(f"Saved {name}_slice_left.png and {name}_slice_right.png")

examine_crop("docs/design/recreation/crops/dashboard_ref_hero_exact.png", "ref_dash_hero")
examine_crop("docs/design/recreation/crops/dashboard_live_hero_exact.png", "live_dash_hero")
examine_crop("docs/design/recreation/crops/events_ref_hero_exact.png", "ref_events_hero")
examine_crop("docs/design/recreation/crops/events_live_hero_exact.png", "live_events_hero")
examine_crop("docs/design/recreation/crops/activity_ref_hero_exact.png", "ref_activity_hero")
examine_crop("docs/design/recreation/crops/activity_live_hero_exact.png", "live_activity_hero")

