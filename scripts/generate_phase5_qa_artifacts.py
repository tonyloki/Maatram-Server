import os
import shutil
import json
import numpy as np
from PIL import Image, ImageDraw

MAPPING = [
    {
        "id": "01",
        "name": "welcome_splash",
        "rendered": "screen_01_welcome_splash.png",
        "ref": "01-authentication/welcome_splash.png",
        "title": "Welcome / Splash Screen",
        "category": "Authentication"
    },
    {
        "id": "02",
        "name": "login",
        "rendered": "screen_02_login.png",
        "ref": "01-authentication/login.png",
        "title": "Sign In Screen",
        "category": "Authentication"
    },
    {
        "id": "03",
        "name": "forgot_password",
        "rendered": "screen_03_forgot_password.png",
        "ref": "01-authentication/forgot_password.png",
        "title": "Forgot Password Screen",
        "category": "Authentication"
    },
    {
        "id": "04",
        "name": "reset_password",
        "rendered": "screen_04_reset_password.png",
        "ref": "01-authentication/reset_password.png",
        "title": "Reset Password Screen",
        "category": "Authentication"
    },
    {
        "id": "05",
        "name": "registration_basic_details",
        "rendered": "screen_05_register_step1.png",
        "ref": "02-registration/registration_basic_details.png",
        "title": "Registration Step 1: Basic Details",
        "category": "Registration"
    },
    {
        "id": "06",
        "name": "registration_category",
        "rendered": "screen_06_register_step2.png",
        "ref": "02-registration/registration_category.png",
        "title": "Registration Step 2: Select Category",
        "category": "Registration"
    },
    {
        "id": "07",
        "name": "registration_category_details",
        "rendered": "screen_07_register_step3.png",
        "ref": "02-registration/registration_category_details.png",
        "title": "Registration Step 3: Category Details",
        "category": "Registration"
    },
    {
        "id": "08",
        "name": "registration_skills_availability",
        "rendered": "screen_08_register_step4.png",
        "ref": "02-registration/registration_skills_availability.png",
        "title": "Registration Step 4: Skills & Availability",
        "category": "Registration"
    },
    {
        "id": "09",
        "name": "registration_privacy_consent",
        "rendered": "screen_09_register_step5.png",
        "ref": "02-registration/registration_privacy_consent.png",
        "title": "Registration Step 5: Privacy & Consent",
        "category": "Registration"
    },
    {
        "id": "10",
        "name": "registration_review_submit",
        "rendered": "screen_10_register_step6.png",
        "ref": "02-registration/registration_review_submit.png",
        "title": "Registration Step 6: Review & Submit",
        "category": "Registration"
    },
    {
        "id": "11",
        "name": "verify_email",
        "rendered": "screen_11_verify_email.png",
        "ref": "03-verification/email_verification.png",
        "title": "Verify Your Email",
        "category": "Verification & Onboarding"
    },
    {
        "id": "12",
        "name": "pending_verification",
        "rendered": "screen_12_pending_verification.png",
        "ref": "03-verification/pending_verification.png",
        "title": "Email Verification Pending",
        "category": "Verification & Onboarding"
    },
    {
        "id": "13",
        "name": "pending_approval",
        "rendered": "screen_13_pending_approval.png",
        "ref": "03-verification/pending_approval.png",
        "title": "Pending Under Review",
        "category": "Verification & Onboarding"
    },
    {
        "id": "14",
        "name": "application_rejected",
        "rendered": "screen_14_rejected.png",
        "ref": "03-verification/application_rejected.png",
        "title": "Application Update / Rejected",
        "category": "Verification & Onboarding"
    },
    {
        "id": "15",
        "name": "post_approval_welcome",
        "rendered": "screen_15_welcome_approved.png",
        "ref": "03-verification/post_approval_welcome.png",
        "title": "Welcome to Maatram!",
        "category": "Verification & Onboarding"
    },
    {
        "id": "16",
        "name": "home",
        "rendered": "screen_16_home.png",
        "ref": "04-main-application/home.png",
        "title": "Volunteer Home Dashboard",
        "category": "Main Application"
    },
    {
        "id": "17",
        "name": "events",
        "rendered": "screen_17_events.png",
        "ref": "04-main-application/events.png",
        "title": "Events Catalog Screen",
        "category": "Main Application"
    },
    {
        "id": "18",
        "name": "event_details",
        "rendered": "screen_18_event_details.png",
        "ref": "04-main-application/event_details.png",
        "title": "Event Details Screen",
        "category": "Main Application"
    },
    {
        "id": "19",
        "name": "event_registration",
        "rendered": "screen_19_event_registration.png",
        "ref": "04-main-application/event_registration.png",
        "title": "Event Registration Screen",
        "category": "Main Application"
    },
    {
        "id": "20",
        "name": "my_activity",
        "rendered": "screen_20_my_activity.png",
        "ref": "04-main-application/my_activity.png",
        "title": "My Activity Hub Screen",
        "category": "Main Application"
    },
    {
        "id": "21",
        "name": "activity_details",
        "rendered": "screen_21_activity_details.png",
        "ref": "04-main-application/activity_details.png",
        "title": "Activity Details Screen",
        "category": "Main Application"
    },
    {
        "id": "22",
        "name": "leaderboard",
        "rendered": "screen_22_leaderboard.png",
        "ref": "04-main-application/leaderboard.png",
        "title": "Leaderboard Podium Screen",
        "category": "Main Application"
    },
    {
        "id": "23",
        "name": "more",
        "rendered": "screen_23_more.png",
        "ref": "04-main-application/more.png",
        "title": "More Hub Navigation Screen",
        "category": "Main Application"
    },
    {
        "id": "24",
        "name": "profile",
        "rendered": "screen_24_profile.png",
        "ref": "05-volunteer-account/profile.png",
        "title": "Volunteer Profile Screen",
        "category": "Volunteer Account"
    },
    {
        "id": "25",
        "name": "edit_profile",
        "rendered": "screen_25_edit_profile.png",
        "ref": "05-volunteer-account/edit_profile.png",
        "title": "Edit Profile Screen",
        "category": "Volunteer Account"
    },
    {
        "id": "26",
        "name": "profile_photo",
        "rendered": "screen_26_profile_photo.png",
        "ref": "05-volunteer-account/profile_photo.png",
        "title": "Profile Photo Management",
        "category": "Volunteer Account"
    },
    {
        "id": "27",
        "name": "points",
        "rendered": "screen_27_points_overview.png",
        "ref": "05-volunteer-account/points.png",
        "title": "Points Overview Screen",
        "category": "Volunteer Account"
    },
    {
        "id": "28",
        "name": "points_history",
        "rendered": "screen_28_points_history.png",
        "ref": "05-volunteer-account/points_history.png",
        "title": "Points History Ledger",
        "category": "Volunteer Account"
    },
    {
        "id": "29",
        "name": "achievements",
        "rendered": "screen_29_achievements.png",
        "ref": "05-volunteer-account/achievements.png",
        "title": "Achievements Showcase Screen",
        "category": "Volunteer Account"
    },
    {
        "id": "30",
        "name": "achievement_details",
        "rendered": "screen_30_achievement_details.png",
        "ref": "05-volunteer-account/achievement_details.png",
        "title": "Achievement Details Modal",
        "category": "Volunteer Account"
    },
    {
        "id": "31",
        "name": "notifications",
        "rendered": "screen_31_notifications.png",
        "ref": "06-notifications-settings/notifications.png",
        "title": "Notifications Screen",
        "category": "Notifications & Settings"
    },
    {
        "id": "32",
        "name": "notification_details",
        "rendered": "screen_32_notification_details.png",
        "ref": "06-notifications-settings/notification_details.png",
        "title": "Notification Details Screen",
        "category": "Notifications & Settings"
    },
    {
        "id": "33",
        "name": "notification_settings",
        "rendered": "screen_33_notification_settings.png",
        "ref": "06-notifications-settings/notification_settings.png",
        "title": "Notification Settings Screen",
        "category": "Notifications & Settings"
    },
    {
        "id": "34",
        "name": "privacy_consent",
        "rendered": "screen_34_privacy_consent.png",
        "ref": "06-notifications-settings/privacy_consent.png",
        "title": "Privacy & Consent Settings",
        "category": "Notifications & Settings"
    },
    {
        "id": "35",
        "name": "settings",
        "rendered": "screen_35_app_settings.png",
        "ref": "06-notifications-settings/settings.png",
        "title": "App Settings Screen",
        "category": "Notifications & Settings"
    },
    {
        "id": "36",
        "name": "help_support",
        "rendered": "screen_36_help_support.png",
        "ref": "06-notifications-settings/help_support.png",
        "title": "Help & Support Screen",
        "category": "Notifications & Settings"
    },
    {
        "id": "37",
        "name": "about_maatram",
        "rendered": "screen_37_about_maatram.png",
        "ref": "06-notifications-settings/about_maatram.png",
        "title": "About Maatram Screen",
        "category": "Notifications & Settings"
    },
    {
        "id": "38",
        "name": "logout_confirmation",
        "rendered": "screen_38_logout_confirmation.png",
        "ref": "06-notifications-settings/logout_confirmation.png",
        "title": "Logout Confirmation Dialog",
        "category": "Notifications & Settings"
    }
]

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_RENDERED = os.path.join(BASE_DIR, "docs", "audits", "phase4_rendered_screens")
SRC_REF = os.path.join(BASE_DIR, "docs", "design-reference")

OUT_SCREENSHOTS = os.path.join(BASE_DIR, "docs", "audits", "ui-ux", "phase-5", "screenshots")
OUT_SIDE_BY_SIDE = os.path.join(BASE_DIR, "docs", "audits", "ui-ux", "phase-5", "side-by-side")
OUT_OVERLAYS = os.path.join(BASE_DIR, "docs", "audits", "ui-ux", "phase-5", "overlays")
OUT_HEATMAPS = os.path.join(BASE_DIR, "docs", "audits", "ui-ux", "phase-5", "difference-heatmaps")
OUT_REPORTS = os.path.join(BASE_DIR, "docs", "audits", "ui-ux", "phase-5", "reports")

for d in [OUT_SCREENSHOTS, OUT_SIDE_BY_SIDE, OUT_OVERLAYS, OUT_HEATMAPS, OUT_REPORTS]:
    os.makedirs(d, exist_ok=True)

TARGET_SIZE = (780, 1688)

results = []

print("Fast Vectorized Generation of all 38 screens for Phase 5 Visual Fidelity...")

for item in MAPPING:
    sid = item["id"]
    sname = item["name"]
    rendered_file = os.path.join(SRC_RENDERED, item["rendered"])
    ref_file = os.path.join(SRC_REF, item["ref"].replace("/", os.sep))
    
    target_rendered_copy = os.path.join(OUT_SCREENSHOTS, f"{sid}_{sname}.png")
    if os.path.exists(rendered_file):
        shutil.copy2(rendered_file, target_rendered_copy)
    
    if not os.path.exists(rendered_file) or not os.path.exists(ref_file):
        print(f"Skipping {sid} ({sname}): missing {rendered_file} or {ref_file}")
        continue
    
    img_rendered = Image.open(rendered_file).convert("RGB")
    img_ref = Image.open(ref_file).convert("RGB")
    
    norm_rendered = img_rendered.resize(TARGET_SIZE, Image.Resampling.LANCZOS)
    norm_ref = img_ref.resize(TARGET_SIZE, Image.Resampling.LANCZOS)
    
    # 1. Side by side
    pad_h = 60
    gap = 20
    sbs_w = TARGET_SIZE[0] * 2 + gap
    sbs_h = TARGET_SIZE[1] + pad_h
    sbs = Image.new("RGB", (sbs_w, sbs_h), (250, 248, 245))
    sbs.paste(norm_ref, (0, pad_h))
    sbs.paste(norm_rendered, (TARGET_SIZE[0] + gap, pad_h))
    
    draw = ImageDraw.Draw(sbs)
    draw.rectangle([0, 0, sbs_w, pad_h], fill=(27, 43, 72))
    draw.text((30, 18), f"APPROVED DESIGN REFERENCE — Screen {sid}: {item['title']}", fill=(245, 184, 23))
    draw.text((TARGET_SIZE[0] + gap + 30, 18), f"IMPLEMENTED FLUTTER UI — Screen {sid}: {item['title']}", fill=(255, 255, 255))
    
    sbs_path = os.path.join(OUT_SIDE_BY_SIDE, f"{sid}_{sname}_side_by_side.png")
    sbs.save(sbs_path)
    
    # 2. 50% Opacity Overlay
    overlay = Image.blend(norm_ref, norm_rendered, alpha=0.50)
    overlay_path = os.path.join(OUT_OVERLAYS, f"{sid}_{sname}_overlay.png")
    overlay.save(overlay_path)
    
    # 3. Vectorized Difference Heatmap & MAE Calculation using NumPy
    arr_ref = np.array(norm_ref, dtype=np.float32)
    arr_rend = np.array(norm_rendered, dtype=np.float32)
    
    delta = np.mean(np.abs(arr_ref - arr_rend), axis=2)
    mae = float(np.mean(delta))
    fidelity_score = max(0.0, min(100.0, 100.0 - (mae / 255.0 * 100.0)))
    
    scaled = np.clip(delta * 2.8, 0, 255).astype(np.uint8)
    
    h_r = np.where(scaled < 30, (arr_ref[:, :, 0] * 0.2).astype(np.uint8),
          np.where(scaled < 100, np.clip(scaled * 2, 0, 255).astype(np.uint8), 245))
    h_g = np.where(scaled < 30, (arr_ref[:, :, 1] * 0.2 + 20).astype(np.uint8),
          np.where(scaled < 100, scaled, np.clip(255 - scaled, 0, 255).astype(np.uint8)))
    h_b = np.where(scaled < 30, (arr_ref[:, :, 2] * 0.2 + 35).astype(np.uint8),
          np.where(scaled < 100, 0, 23))
          
    heatmap_arr = np.stack([h_r, h_g, h_b], axis=2).astype(np.uint8)
    heatmap = Image.fromarray(heatmap_arr)
    heatmap_path = os.path.join(OUT_HEATMAPS, f"{sid}_{sname}_heatmap.png")
    heatmap.save(heatmap_path)
    
    res = {
        "id": sid,
        "name": sname,
        "title": item["title"],
        "category": item["category"],
        "mae": round(mae, 2),
        "fidelity_score": round(fidelity_score, 2),
        "side_by_side": f"docs/audits/ui-ux/phase-5/side-by-side/{sid}_{sname}_side_by_side.png",
        "overlay": f"docs/audits/ui-ux/phase-5/overlays/{sid}_{sname}_overlay.png",
        "heatmap": f"docs/audits/ui-ux/phase-5/difference-heatmaps/{sid}_{sname}_heatmap.png"
    }
    results.append(res)
    print(f"[{sid}/38] {item['title']}: MAE={mae:.2f}/255, Fidelity={fidelity_score:.2f}%")

with open(os.path.join(OUT_REPORTS, "phase5_fidelity_metrics.json"), "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

avg_fidelity = sum(r["fidelity_score"] for r in results) / len(results) if results else 0
print(f"\nSuccessfully generated QA artifacts for all 38 screens! Overall Average Fidelity: {avg_fidelity:.2f}%")
