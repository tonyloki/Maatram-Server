import os
from PIL import Image, ImageDraw, ImageFont

def make_side_by_side(ref_path, runtime_path, out_path, ref_label="Approved Design Reference", runtime_label="Live Flutter Web Runtime"):
    if not os.path.exists(ref_path) or not os.path.exists(runtime_path):
        print(f"Skipping {out_path}: {ref_path} or {runtime_path} not found")
        return

    ref_img = Image.open(ref_path).convert("RGBA")
    run_img = Image.open(runtime_path).convert("RGBA")

    target_h = 844
    ref_w = int(ref_img.width * (target_h / ref_img.height))
    ref_resized = ref_img.resize((ref_w, target_h), Image.Resampling.LANCZOS)

    run_w = int(run_img.width * (target_h / run_img.height))
    run_resized = run_img.resize((run_w, target_h), Image.Resampling.LANCZOS)

    header_h = 50
    gap = 20
    border = 20
    total_w = border * 2 + ref_w + run_w + gap
    total_h = border * 2 + header_h + target_h

    canvas = Image.new("RGBA", (total_w, total_h), (250, 248, 245, 255))
    draw = ImageDraw.Draw(canvas)

    # Paste images
    ref_x = border
    ref_y = border + header_h
    canvas.paste(ref_resized, (ref_x, ref_y), ref_resized)

    run_x = border + ref_w + gap
    run_y = border + header_h
    canvas.paste(run_resized, (run_x, run_y), run_resized)

    # Draw headers
    try:
        font = ImageFont.truetype("arial.ttf", 20)
        subfont = ImageFont.truetype("arial.ttf", 14)
    except:
        font = ImageFont.load_default()
        subfont = ImageFont.load_default()

    draw.rectangle([ref_x, border, ref_x + ref_w, border + header_h - 10], fill=(27, 43, 72, 255))
    draw.text((ref_x + 15, border + 10), ref_label, fill=(245, 184, 23, 255), font=font)

    draw.rectangle([run_x, border, run_x + run_w, border + header_h - 10], fill=(27, 43, 72, 255))
    draw.text((run_x + 15, border + 10), runtime_label, fill=(245, 184, 23, 255), font=font)

    # Border around images
    draw.rectangle([ref_x, ref_y, ref_x + ref_w, ref_y + target_h], outline=(239, 236, 230, 255), width=2)
    draw.rectangle([run_x, run_y, run_x + run_w, run_y + target_h], outline=(239, 236, 230, 255), width=2)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    canvas.convert("RGB").save(out_path, quality=95)
    print(f"Generated comparison: {out_path} ({total_w}x{total_h})")

if __name__ == "__main__":
    base_ref = "docs/audits/ui-ux/references"
    base_shot = "docs/audits/ui-ux/screenshots"

    # WP1 Welcome Splash
    make_side_by_side(
        f"{base_ref}/ref_01_welcome_splash.jpg",
        f"{base_shot}/wp1_welcome_splash_runtime.png",
        f"{base_shot}/wp1_comparison_side_by_side.png",
        "Mentor Reference: Welcome Splash",
        "Live Flutter Web Runtime (390x844)"
    )

    # WP4 Home Screen
    make_side_by_side(
        f"{base_ref}/ref_02_home_screen.jpg",
        f"{base_shot}/03_home_screen_runtime.png",
        f"{base_shot}/wp4_home_screen_comparison.png",
        "Mentor Reference: Home Screen",
        "Live Flutter Web Runtime (390x844)"
    )

    # WP2 My Activity
    make_side_by_side(
        f"{base_ref}/ref_03_my_activity.jpg",
        f"{base_shot}/07_my_activity_runtime.png",
        f"{base_shot}/wp2_my_activity_comparison.png",
        "Mentor Reference: My Activity",
        "Live Flutter Web Runtime (390x844)"
    )
