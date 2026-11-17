import os
from PIL import Image, ImageDraw, ImageFont

FONTS_DIR = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts')

def get_font(name="georgiab.ttf", size=18):
    p = os.path.join(FONTS_DIR, name)
    if os.path.exists(p):
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            pass
    return ImageFont.load_default()

FONT_BANNER = get_font("georgiab.ttf", 26)
FONT_SUBBANNER = get_font("arial.ttf", 15)
FONT_CARD_TITLE = get_font("georgiab.ttf", 15)
FONT_CARD_SUB = get_font("arial.ttf", 12)

BG_GALLERY = (250, 248, 245, 255)      # #FAF8F5
DEEP_NAVY = (27, 43, 72, 255)         # #1B2B48
PRIMARY_GOLD = (245, 184, 23, 255)    # #F5B817
WARM_BORDER = (239, 236, 230, 255)    # #EFECE6
WHITE = (255, 255, 255, 255)
SECONDARY_TEXT = (130, 125, 115, 255)

OUT_DIR = "docs/design-reference/galleries"
os.makedirs(OUT_DIR, exist_ok=True)

def create_gallery(group_title, group_subtitle, screens_info, cols, out_filename):
    """
    screens_info: list of tuples: (image_path, screen_num, screen_title, status_text)
    cols: number of columns
    """
    target_w = 320
    target_h = int(target_w * (844 / 390)) # ~692
    
    pad_x = 24
    pad_y = 24
    card_gap = 20
    card_header_h = 44
    banner_h = 90
    
    num_screens = len(screens_info)
    rows = (num_screens + cols - 1) // cols
    
    total_w = pad_x * 2 + cols * target_w + (cols - 1) * card_gap
    total_h = banner_h + pad_y + rows * (target_h + card_header_h) + (rows - 1) * card_gap + pad_y
    
    canvas = Image.new("RGBA", (total_w, total_h), BG_GALLERY)
    draw = ImageDraw.Draw(canvas)
    
    # Top Banner
    draw.rectangle([0, 0, total_w, banner_h], fill=DEEP_NAVY)
    draw.rectangle([0, banner_h - 4, total_w, banner_h], fill=PRIMARY_GOLD)
    draw.text((pad_x + 10, 20), group_title, fill=PRIMARY_GOLD, font=FONT_BANNER)
    draw.text((pad_x + 10, 54), group_subtitle, fill=WHITE, font=FONT_SUBBANNER)
    
    for idx, (img_rel_path, s_num, s_title, s_status) in enumerate(screens_info):
        r = idx // cols
        c = idx % cols
        
        # Center last row if fewer items
        items_in_this_row = min(cols, num_screens - r * cols)
        row_start_x = pad_x
        if items_in_this_row < cols:
            row_w = items_in_this_row * target_w + (items_in_this_row - 1) * card_gap
            row_start_x = (total_w - row_w) // 2
            
        x = row_start_x + c * (target_w + card_gap)
        y = banner_h + pad_y + r * (target_h + card_header_h + card_gap)
        
        # Card header pill
        draw.rounded_rectangle([x, y, x + target_w, y + card_header_h - 6], radius=8, fill=WHITE, outline=WARM_BORDER)
        draw.text((x + 10, y + 6), f"{s_num}. {s_title}", fill=DEEP_NAVY, font=FONT_CARD_TITLE)
        draw.text((x + 10, y + 24), s_status, fill=PRIMARY_GOLD if "Mentor" in s_status else SECONDARY_TEXT, font=FONT_CARD_SUB)
        
        # Screen image
        full_img_path = os.path.join("docs", "design-reference", img_rel_path)
        if os.path.exists(full_img_path):
            s_img = Image.open(full_img_path).convert("RGBA")
            s_resized = s_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
            canvas.paste(s_resized, (x, y + card_header_h), s_resized)
            draw.rectangle([x, y + card_header_h, x + target_w, y + card_header_h + target_h], outline=WARM_BORDER, width=1)
        else:
            draw.rectangle([x, y + card_header_h, x + target_w, y + card_header_h + target_h], fill=WHITE, outline=WARM_BORDER)
            draw.text((x + 20, y + card_header_h + 100), "Image Missing", fill=DEEP_NAVY, font=FONT_CARD_TITLE)
            
    out_path = os.path.join(OUT_DIR, out_filename)
    canvas.convert("RGB").save(out_path, quality=95)
    print(f"Generated Gallery Contact Sheet: {out_path} ({total_w}x{total_h})")

# Gallery 1: Authentication (4 screens, 4 cols)
g1 = [
    ("01-authentication/welcome_splash.png", "01", "Welcome / Splash", "Approved Mentor Ref 01 • Live Route /welcome"),
    ("01-authentication/login.png", "02", "Login", "Verified UI Reference • Live Route /login"),
    ("01-authentication/forgot_password.png", "03", "Forgot Password", "Verified UI Reference • Live Route /forgot-password"),
    ("01-authentication/reset_password.png", "04", "Reset Password", "Verified UI Reference • Live Route /reset-password"),
]
create_gallery("Group 1: App Entry & Authentication", "4 Dedicated High-Resolution Screens • Locked Global Design System v1.0", g1, cols=4, out_filename="gallery_01_authentication.png")

# Gallery 2: Registration (6 screens, 3 cols x 2 rows)
g2 = [
    ("02-registration/registration_basic_details.png", "05", "Step 1: Basic Details", "6-Step Wizard • Live Route /register"),
    ("02-registration/registration_category.png", "06", "Step 2: Category Select", "Role-Based Cards (Student/Alumni/Panelist)"),
    ("02-registration/registration_category_details.png", "07", "Step 3: Category Details", "Institution & Program Specifics"),
    ("02-registration/registration_skills_availability.png", "08", "Step 4: Skills & Availability", "Multi-Select Chips & Availability Slots"),
    ("02-registration/registration_privacy_consent.png", "09", "Step 5: Privacy & Consent", "Granular Privacy Consents"),
    ("02-registration/registration_review_submit.png", "10", "Step 6: Review & Submit", "Verified Summary Cards & Final Submission"),
]
create_gallery("Group 2: Volunteer Registration (6-Step Guided Flow)", "6 Dedicated High-Resolution Screens • Sequential Onboarding Architecture", g2, cols=3, out_filename="gallery_02_registration.png")

# Gallery 3: Verification (5 screens, 5 cols)
g3 = [
    ("03-verification/email_verification.png", "11", "Email Verification", "6-Digit Code / Token Submission"),
    ("03-verification/pending_verification.png", "12", "Pending Verification", "Email Delivery Guidance & Resend"),
    ("03-verification/pending_approval.png", "13", "Pending Approval", "Admin Review Status & Timeline"),
    ("03-verification/application_rejected.png", "14", "Application Update", "Respectful Update & Support Channel"),
    ("03-verification/post_approval_welcome.png", "15", "Post-Approval Welcome", "Celebratory Onboarding Gateway"),
]
create_gallery("Group 3: Verification & Application Status", "5 Dedicated High-Resolution Screens • 4-State Lifecycle Management", g3, cols=5, out_filename="gallery_03_verification.png")

# Gallery 4: Main Application (8 screens, 4 cols x 2 rows)
g4 = [
    ("04-main-application/home.png", "16", "Volunteer Home", "Approved Mentor Ref 02 • Live Route /home"),
    ("04-main-application/events.png", "17", "Events Discovery", "Category Filter Chips & Event Feed"),
    ("04-main-application/event_details.png", "18", "Event Details", "Hero Banner, Description & Prerequisites"),
    ("04-main-application/event_registration.png", "19", "Event Registration", "Commitment Checklist & Confirmation"),
    ("04-main-application/my_activity.png", "20", "My Activity", "Approved Mentor Ref 03 • Live Route /activity"),
    ("04-main-application/activity_details.png", "21", "Activity Record Details", "Verified Attendance & Credited Hours"),
    ("04-main-application/leaderboard.png", "22", "Leaderboard", "Podium Hierarchy & Category Filters"),
    ("04-main-application/more.png", "23", "More Hub", "Profile Preview & Feature Navigation"),
]
create_gallery("Group 4: Main Volunteer Application", "8 Dedicated High-Resolution Screens • Core Volunteering & Event Discovery Hub", g4, cols=4, out_filename="gallery_04_main_application.png")

# Gallery 5: Volunteer Account & Gamification (7 screens, 4 cols)
g5 = [
    ("05-volunteer-account/profile.png", "24", "Volunteer Profile", "Summary Stats & Contact Details"),
    ("05-volunteer-account/edit_profile.png", "25", "Edit Profile", "Self-Service Information Management"),
    ("05-volunteer-account/profile_photo.png", "26", "Profile Photo", "Photo Guidelines & Avatar Upload"),
    ("05-volunteer-account/points.png", "27", "My Points Balance", "Tier Progression & Category Breakdown"),
    ("05-volunteer-account/points_history.png", "28", "Points History", "Itemized Immutable Audit Ledger"),
    ("05-volunteer-account/achievements.png", "29", "Achievements Gallery", "Unlocked & Locked Badge Medals"),
    ("05-volunteer-account/achievement_details.png", "30", "Achievement Details", "Criteria Breakdown & Social Sharing"),
]
create_gallery("Group 5: Volunteer Account & Gamification", "7 Dedicated High-Resolution Screens • Recognition, Points & Credential Management", g5, cols=4, out_filename="gallery_05_volunteer_account.png")

# Gallery 6: Notifications & Settings (8 screens, 4 cols x 2 rows)
g6 = [
    ("06-notifications-settings/notifications.png", "31", "Notifications Feed", "Chronological & Unread Grouping"),
    ("06-notifications-settings/notification_details.png", "32", "Notification Details", "Rich Announcement & Action Deep-Link"),
    ("06-notifications-settings/notification_settings.png", "33", "Notification Settings", "Push & Channel Alert Preferences"),
    ("06-notifications-settings/privacy_consent.png", "34", "Privacy & Consents", "Granular Directory & Ranking Controls"),
    ("06-notifications-settings/settings.png", "35", "App Settings", "Language, Biometrics & Cache Management"),
    ("06-notifications-settings/help_support.png", "36", "Help & Support", "FAQ Accordion & Coordinator Helpline"),
    ("06-notifications-settings/about_maatram.png", "37", "About Maatram", "Foundation Mission, Impact & Vision"),
    ("06-notifications-settings/logout_confirmation.png", "38", "Logout Confirmation", "Safe Sign-Out Confirmation Sheet"),
]
create_gallery("Group 6: Notifications & Preferences", "8 Dedicated High-Resolution Screens • Utility, Support & Account Governance", g6, cols=4, out_filename="gallery_06_notifications_settings.png")

print("\n✓ ALL SIX CONTACT SHEET GALLERIES GENERATED SUCCESSFULLY!")
