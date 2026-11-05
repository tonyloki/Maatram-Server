"""Exhaustive visual reference analyzer.

Compares mentor reference images (in ui-Reference/) against live screenshots
(in docs/design/recreation/) down to exact pixels, layout boxes, color palettes,
and font hierarchies.
"""

import os
from PIL import Image, ImageChops, ImageStat

PAGES = [
    {
        "name": "Dashboard",
        "ref": "ui-Reference/Dashboard.jpeg",
        "live": "docs/design/recreation/live_dashboard_1536x1024.png",
        "width": 1536,
        "height": 1024,
    },
    {
        "name": "Discover Events",
        "ref": "ui-Reference/Discover_Events.jpeg",
        "live": "docs/design/recreation/live_discover_events_1536x1024.png",
        "width": 1536,
        "height": 1024,
    },
    {
        "name": "My Activities",
        "ref": "ui-Reference/MyActivities.jpeg",
        "live": "docs/design/recreation/live_my_activity_1536x1024.png",
        "width": 1536,
        "height": 1024,
    },
    {
        "name": "Leaderboard",
        "ref": "ui-Reference/Leaderboard.jpeg",
        "live": "docs/design/recreation/live_leaderboard_1536x1024.png",
        "width": 1536,
        "height": 1024,
    },
    {
        "name": "Profile Page",
        "ref": "ui-Reference/Profile_page.jpeg",
        "live": "docs/design/recreation/live_profile_1600x900.png",
        "width": 1600,
        "height": 900,
    },
]


def analyze_image_regions(ref_img, live_img, name):
    print(f"\n=======================================================")
    print(f"PAGE: {name}")
    print(f"Ref Size: {ref_img.size} | Live Size: {live_img.size}")
    print(f"=======================================================")

    # 1. Overall Difference
    diff = ImageChops.difference(ref_img.convert("RGB"), live_img.convert("RGB"))
    stat = ImageStat.Stat(diff)
    avg_diff = sum(stat.mean) / (3.0 * 255.0)
    similarity = (1.0 - avg_diff) * 100.0
    print(f"Global Color & Layout Similarity: {similarity:.2f}%")

    # 2. Key Regions Analysis
    w, h = ref_img.size

    # Region A: Sidebar (x: 0..270, y: 0..h)
    sb_box = (0, 0, min(270, w), h)
    sb_ref = ref_img.crop(sb_box)
    sb_live = live_img.crop(sb_box)
    sb_diff = ImageChops.difference(sb_ref.convert("RGB"), sb_live.convert("RGB"))
    sb_stat = ImageStat.Stat(sb_diff)
    sb_sim = (1.0 - (sum(sb_stat.mean) / (3.0 * 255.0))) * 100.0
    print(f"  - Sidebar Area (0..270px): {sb_sim:.2f}% similarity")

    # Region B: Top Header (x: 270..w, y: 0..80)
    th_box = (270, 0, w, min(80, h))
    th_ref = ref_img.crop(th_box)
    th_live = live_img.crop(th_box)
    th_diff = ImageChops.difference(th_ref.convert("RGB"), th_live.convert("RGB"))
    th_stat = ImageStat.Stat(th_diff)
    th_sim = (1.0 - (sum(th_stat.mean) / (3.0 * 255.0))) * 100.0
    print(f"  - Top Header (y: 0..80px): {th_sim:.2f}% similarity")

    # Region C: Hero / Top Main (x: 270..w, y: 80..300)
    hero_box = (270, 80, w, min(300, h))
    hero_ref = ref_img.crop(hero_box)
    hero_live = live_img.crop(hero_box)
    hero_diff = ImageChops.difference(hero_ref.convert("RGB"), hero_live.convert("RGB"))
    hero_stat = ImageStat.Stat(hero_diff)
    hero_sim = (1.0 - (sum(hero_stat.mean) / (3.0 * 255.0))) * 100.0
    print(f"  - Hero Section (y: 80..300px): {hero_sim:.2f}% similarity")

    # Region D: Mid Content (x: 270..w, y: 300..600)
    mid_box = (270, 300, w, min(600, h))
    mid_ref = ref_img.crop(mid_box)
    mid_live = live_img.crop(mid_box)
    mid_diff = ImageChops.difference(mid_ref.convert("RGB"), mid_live.convert("RGB"))
    mid_stat = ImageStat.Stat(mid_diff)
    mid_sim = (1.0 - (sum(mid_stat.mean) / (3.0 * 255.0))) * 100.0
    print(f"  - Mid Content (y: 300..600px): {mid_sim:.2f}% similarity")

    # Region E: Bottom Content (x: 270..w, y: 600..h)
    bot_box = (270, 600, w, h)
    bot_ref = ref_img.crop(bot_box)
    bot_live = live_img.crop(bot_box)
    bot_diff = ImageChops.difference(bot_ref.convert("RGB"), bot_live.convert("RGB"))
    bot_stat = ImageStat.Stat(bot_diff)
    bot_sim = (1.0 - (sum(bot_stat.mean) / (3.0 * 255.0))) * 100.0
    print(f"  - Bottom Content (y: 600..end): {bot_sim:.2f}% similarity")


def main():
    for page in PAGES:
        if not os.path.exists(page["ref"]) or not os.path.exists(page["live"]):
            print(f"Missing file for {page['name']}")
            continue
        ref_img = Image.open(page["ref"])
        live_img = Image.open(page["live"])
        analyze_image_regions(ref_img, live_img, page["name"])


if __name__ == "__main__":
    main()

