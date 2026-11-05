"""Deep dive into hero sections across Dashboard, Discover Events, and My Activities."""

import numpy as np
from PIL import Image

def analyze_hero(ref_path, live_path, name):
    ref = Image.open(ref_path).convert("RGB")
    live = Image.open(live_path).convert("RGB")

    # Crop hero region x: 270..1500, y: 70..320
    box = (270, 70, 1500, 320)
    c_ref = ref.crop(box)
    c_live = live.crop(box)

    c_ref.save(f"docs/design/recreation/crops/{name}_ref_hero_exact.png")
    c_live.save(f"docs/design/recreation/crops/{name}_live_hero_exact.png")

    arr_ref = np.array(c_ref)
    arr_live = np.array(c_live)

    # Let's find background color profile along a vertical line where there's no text (e.g. x = 100 within crop)
    print(f"\n--- Hero Analysis for {name} ---")
    print(f"Ref Crop Size: {c_ref.size} | Live Crop Size: {c_live.size}")

    # Sample top-left, center, bottom-right of hero banner inside crop
    # Find bounding box of the rounded hero card in ref vs live
    # Detect where hero card starts (y) by scanning from y=0 down at x=100
    y_start_ref = -1
    y_start_live = -1
    for y in range(c_ref.size[1]):
        px_ref = c_ref.getpixel((100, y))
        px_live = c_live.getpixel((100, y))
        # If warmer / different from canvas (250, 248, 245)
        if px_ref[0] > 240 and px_ref[1] > 220 and px_ref[2] < 220:
            if y_start_ref == -1:
                y_start_ref = y
        if px_live[0] > 240 and px_live[1] > 220 and px_live[2] < 220:
            if y_start_live == -1:
                y_start_live = y

    print(f"Hero Banner top offset: Ref={y_start_ref}px | Live={y_start_live}px")

    # Measure mean RGB in the center of the hero banner
    center_ref = arr_ref[60:120, 200:400]
    center_live = arr_live[60:120, 200:400]
    print(f"Ref Hero Center Mean RGB: {center_ref.mean(axis=(0,1)).astype(int)}")
    print(f"Live Hero Center Mean RGB: {center_live.mean(axis=(0,1)).astype(int)}")

    # Check right side photo area (x: 800..1200 within crop)
    right_ref = arr_ref[:, 800:]
    right_live = arr_live[:, 800:]
    print(f"Ref Right Area Mean RGB: {right_ref.mean(axis=(0,1)).astype(int)}")
    print(f"Live Right Area Mean RGB: {right_live.mean(axis=(0,1)).astype(int)}")

analyze_hero("ui-Reference/Dashboard.jpeg", "docs/design/recreation/live_dashboard_1536x1024.png", "dashboard")
analyze_hero("ui-Reference/Discover_Events.jpeg", "docs/design/recreation/live_discover_events_1536x1024.png", "events")
analyze_hero("ui-Reference/MyActivities.jpeg", "docs/design/recreation/live_my_activity_1536x1024.png", "activity")
analyze_hero("ui-Reference/Leaderboard.jpeg", "docs/design/recreation/live_leaderboard_1536x1024.png", "leaderboard")

