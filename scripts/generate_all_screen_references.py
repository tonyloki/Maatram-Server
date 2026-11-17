import os
import sys
from PIL import Image, ImageDraw, ImageFont

sys.path.append(os.path.dirname(__file__))
from design_reference_builder import (
    BG_COLOR, PRIMARY_GOLD, DEEP_NAVY, WHITE, WARM_BORDER, SECONDARY_TEXT,
    SUCCESS_GREEN, ACCENT_BLUE, ACCENT_PURPLE, ACCENT_AMBER, LIGHT_GOLD,
    LIGHT_GREEN, LIGHT_BLUE, LIGHT_RED, CRITICAL_RED,
    FONT_TITLE_LG, FONT_TITLE_MD, FONT_TITLE_SM, FONT_HEAD_BOLD,
    FONT_BODY_LG, FONT_BODY_MD, FONT_BODY_BOLD, FONT_BODY_SM,
    FONT_BODY_SM_BOLD, FONT_CAPTION, FONT_CAPTION_BOLD,
    create_base_canvas, draw_status_bar, draw_header_brand, draw_header_nav,
    draw_bottom_nav, draw_card, draw_button, draw_input, draw_pill, get_font
)

W = 390
H = 844

def save_screen(img, relative_path):
    out_path = os.path.join("docs", "design-reference", relative_path)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path, quality=95)
    print(f"Generated: {out_path} ({img.size[0]}x{img.size[1]})")

# ==============================================================================
# GROUP 1: AUTHENTICATION
# ==============================================================================

def gen_login():
    img, draw = create_base_canvas(W, H)
    draw_status_bar(draw, W)
    
    # Top hero photo background with organic swoop
    hero_path = "mobile/assets/images/volunteers-team-hero.jpg"
    if os.path.exists(hero_path):
        hero = Image.open(hero_path).convert("RGBA")
        hero_resized = hero.resize((W, 220), Image.Resampling.LANCZOS)
        img.paste(hero_resized, (0, 36), hero_resized)
        # Golden gradient overlay
        overlay = Image.new("RGBA", (W, 220), (250, 248, 245, 120))
        img.paste(overlay, (0, 36), overlay)
    
    # Logo
    logo_path = "mobile/assets/images/logo.png"
    if os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        logo_h = 44
        logo_w = int(logo_h * (logo.width / logo.height))
        logo_resized = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
        img.paste(logo_resized, ((W - logo_w) // 2, 50), logo_resized)
    
    # White Auth Card (Sheet)
    card_y = 190
    card_h = 600
    draw.rounded_rectangle([16, card_y, W - 16, card_y + card_h], radius=24, fill=WHITE, outline=WARM_BORDER)
    
    # Title & Subtitle
    draw.text((36, card_y + 32), "Together, We Make\na Difference.", fill=DEEP_NAVY, font=FONT_TITLE_MD)
    draw.text((36, card_y + 88), "Welcome back! Sign in to continue your\nvolunteering journey.", fill=SECONDARY_TEXT, font=FONT_BODY_MD)
    
    # Form fields
    field_y = card_y + 140
    draw_input(draw, 36, field_y, W - 72, 48, "Email Address", "priya.s@maatram.org")
    draw_input(draw, 36, field_y + 76, W - 72, 48, "Password", "••••••••", is_password=True)
    
    # Remember me & Forgot Password
    draw.rounded_rectangle([36, field_y + 144, 48, field_y + 156], radius=3, fill=PRIMARY_GOLD)
    draw.text((54, field_y + 144), "Remember me", fill=DEEP_NAVY, font=FONT_BODY_SM)
    draw.text((W - 146, field_y + 144), "Forgot Password?", fill=DEEP_NAVY, font=FONT_BODY_SM_BOLD)
    
    # Sign In Button
    draw_button(draw, 36, field_y + 180, W - 72, 50, "Sign In", is_primary=True)
    
    # Register Link
    draw.text((W//2 - 96, field_y + 256), "New volunteer?", fill=SECONDARY_TEXT, font=FONT_BODY_MD)
    draw.text((W//2 + 4, field_y + 256), "Register Here", fill=DEEP_NAVY, font=FONT_BODY_BOLD)
    
    save_screen(img, "01-authentication/login.png")

def gen_forgot_password():
    img, draw = create_base_canvas(W, H)
    draw_status_bar(draw, W)
    draw_header_nav(img, draw, "Reset Password", W, show_back=True)
    
    # Center Card
    draw_card(draw, 20, 120, W - 40, 460, radius=24)
    
    # Envelope Icon Illustration
    draw.ellipse([W//2 - 40, 160, W//2 + 40, 240], fill=LIGHT_GOLD)
    draw.rectangle([W//2 - 24, 186, W//2 + 24, 216], outline=PRIMARY_GOLD, width=3, fill=WHITE)
    draw.line([W//2 - 24, 186, W//2, 202], fill=PRIMARY_GOLD, width=2)
    draw.line([W//2 + 24, 186, W//2, 202], fill=PRIMARY_GOLD, width=2)
    
    draw.text((W//2 - 80, 260), "Forgot Password?", fill=DEEP_NAVY, font=FONT_TITLE_MD)
    draw.text((44, 300), "No worries! Enter your registered email address\nand we'll send you a password reset link.", fill=SECONDARY_TEXT, font=FONT_BODY_MD, align="center")
    
    draw_input(draw, 44, 380, W - 88, 48, "Email Address", "priya.s@maatram.org")
    draw_button(draw, 44, 450, W - 88, 48, "Send Reset Link", is_primary=True)
    
    draw.text((W//2 - 50, 520), "Back to Sign In", fill=DEEP_NAVY, font=FONT_BODY_SM_BOLD)
    
    save_screen(img, "01-authentication/forgot_password.png")

def gen_reset_password():
    img, draw = create_base_canvas(W, H)
    draw_status_bar(draw, W)
    draw_header_nav(img, draw, "New Password", W, show_back=True)
    
    draw_card(draw, 20, 110, W - 40, 520, radius=24)
    
    # Lock Icon
    draw.ellipse([W//2 - 36, 140, W//2 + 36, 212], fill=LIGHT_GOLD)
    draw.rounded_rectangle([W//2 - 18, 172, W//2 + 18, 198], radius=3, fill=PRIMARY_GOLD)
    draw.arc([W//2 - 12, 154, W//2 + 12, 182], start=180, end=360, fill=PRIMARY_GOLD, width=4)
    
    draw.text((W//2 - 84, 226), "Reset Your Password", fill=DEEP_NAVY, font=FONT_TITLE_MD)
    draw.text((54, 262), "Create a strong new password for your account.", fill=SECONDARY_TEXT, font=FONT_BODY_MD)
    
    draw_input(draw, 44, 320, W - 88, 46, "New Password", "••••••••", is_password=True)
    draw_input(draw, 44, 396, W - 88, 46, "Confirm Password", "••••••••", is_password=True)
    
    # Checklist
    checks = ["At least 8 characters", "One uppercase letter", "One number or symbol"]
    for i, item in enumerate(checks):
        cy = 460 + i * 22
        draw.ellipse([46, cy, 56, cy + 10], fill=SUCCESS_GREEN)
        draw.text((64, cy - 2), item, fill=DEEP_NAVY, font=FONT_CAPTION)
    
    draw_button(draw, 44, 540, W - 88, 48, "Reset Password", is_primary=True)
    
    save_screen(img, "01-authentication/reset_password.png")

# ==============================================================================
# GROUP 2: REGISTRATION (6-STEP FLOW)
# ==============================================================================

def draw_reg_stepper(draw, current_step, title, subtitle):
    # Header bar
    draw.text((20, 48), f"Step {current_step} of 6", fill=PRIMARY_GOLD, font=FONT_BODY_SM_BOLD)
    # Progress track
    total_steps = 6
    track_w = W - 40
    step_w = (track_w - (total_steps - 1) * 6) / total_steps
    for i in range(total_steps):
        x = 20 + i * (step_w + 6)
        color = PRIMARY_GOLD if i < current_step else WARM_BORDER
        draw.rounded_rectangle([x, 72, x + step_w, 77], radius=2, fill=color)
    
    # Headline
    draw.text((20, 96), title, fill=DEEP_NAVY, font=FONT_TITLE_MD)
    draw.text((20, 126), subtitle, fill=SECONDARY_TEXT, font=FONT_BODY_MD)

def gen_reg_step1():
    img, draw = create_base_canvas(W, H)
    draw_status_bar(draw, W)
    draw_reg_stepper(draw, 1, "Basic Details", "Let's start with your personal information.")
    
    draw_card(draw, 20, 160, W - 40, 360, radius=20)
    draw_input(draw, 40, 200, W - 80, 46, "Full Name", "Priya Sharma")
    draw_input(draw, 40, 276, W - 80, 46, "Email Address", "priya.s@maatram.org")
    draw_input(draw, 40, 352, W - 80, 46, "Mobile Number", "+91 98765 43210")
    
    draw_button(draw, 20, 740, W - 40, 50, "Next →", is_primary=True)
    save_screen(img, "02-registration/registration_basic_details.png")

def gen_reg_step2():
    img, draw = create_base_canvas(W, H)
    draw_status_bar(draw, W)
    draw_reg_stepper(draw, 2, "Select Category", "Choose the volunteer category that best describes you.")
    
    categories = [
        ("Student Volunteer", "Enrolled in college/university seeking mentorship & engagement", ACCENT_BLUE, True),
        ("Alumni Volunteer", "Graduated professional providing leadership and career guidance", ACCENT_PURPLE, False),
        ("Corporate Panelist", "Industry expert conducting mock interviews and soft skills workshops", ACCENT_AMBER, False),
    ]
    
    y = 170
    for title, desc, color, selected in categories:
        draw_card(draw, 20, y, W - 40, 96, radius=18, fill=WHITE, border=PRIMARY_GOLD if selected else WARM_BORDER)
        # Radio circle
        draw.ellipse([36, y + 24, 52, y + 40], outline=color if selected else WARM_BORDER, width=2)
        if selected:
            draw.ellipse([40, y + 28, 48, y + 36], fill=color)
        draw.text((64, y + 20), title, fill=DEEP_NAVY, font=FONT_HEAD_BOLD)
        draw.text((64, y + 44), desc[:48] + "...", fill=SECONDARY_TEXT, font=FONT_BODY_SM)
        y += 112
        
    draw_button(draw, 20, 740, W - 40, 50, "Next →", is_primary=True)
    save_screen(img, "02-registration/registration_category.png")

def gen_reg_step3():
    img, draw = create_base_canvas(W, H)
    draw_status_bar(draw, W)
    draw_reg_stepper(draw, 3, "Category Details", "Tell us more about your educational background.")
    
    draw_card(draw, 20, 160, W - 40, 360, radius=20)
    draw_input(draw, 40, 200, W - 80, 46, "College / University Name", "Sathyabama Institute of Science and Tech")
    draw_input(draw, 40, 276, W - 80, 46, "Degree / Program", "B.Tech Computer Science")
    draw_input(draw, 40, 352, W - 80, 46, "Year of Study", "Final Year (4th Year)")
    
    draw_button(draw, 20, 740, W - 40, 50, "Next →", is_primary=True)
    save_screen(img, "02-registration/registration_category_details.png")

def gen_reg_step4():
    img, draw = create_base_canvas(W, H)
    draw_status_bar(draw, W)
    draw_reg_stepper(draw, 4, "Skills & Availability", "Help us match you with the right opportunities.")
    
    draw_card(draw, 20, 160, W - 40, 380, radius=20)
    draw.text((40, 180), "Select Your Skills & Interests", fill=DEEP_NAVY, font=FONT_HEAD_BOLD)
    
    chips = ["Mentoring", "Public Speaking", "Event Support", "Career Guidance", "Content Writing", "Coordination"]
    cx, cy = 40, 210
    for chip in chips:
        pill_w = draw_pill(draw, cx, cy, chip, bg=LIGHT_GOLD, fg=DEEP_NAVY)
        cx += pill_w + 8
        if cx > W - 120:
            cx = 40
            cy += 36
            
    draw_input(draw, 40, cy + 60, W - 80, 46, "Preferred Availability", "Weekends (Saturday & Sunday)")
    draw_input(draw, 40, cy + 136, W - 80, 46, "City / Location", "Chennai, Tamil Nadu")
    
    draw_button(draw, 20, 740, W - 40, 50, "Next →", is_primary=True)
    save_screen(img, "02-registration/registration_skills_availability.png")

def gen_reg_step5():
    img, draw = create_base_canvas(W, H)
    draw_status_bar(draw, W)
    draw_reg_stepper(draw, 5, "Privacy & Consent", "Your privacy matters. Please review and provide consents.")
    
    draw_card(draw, 20, 160, W - 40, 460, radius=20)
    
    toggles = [
        ("Show my name on Leaderboard", "Celebrate impact with peers", True),
        ("Show profile in Volunteer Directory", "Connect with fellow volunteers", True),
        ("Receive Event Notifications via Push", "Get reminders for registered events", True),
        ("Allow Activity Sharing in Stories", "Feature your service in impact reports", True),
        ("Anonymized Research & Analytics", "Help improve foundation programs", True),
    ]
    
    ty = 180
    for title, desc, on in toggles:
        draw.text((40, ty), title, fill=DEEP_NAVY, font=FONT_BODY_SM_BOLD)
        draw.text((40, ty + 18), desc, fill=SECONDARY_TEXT, font=FONT_CAPTION)
        # Toggle switch
        sw_x = W - 80
        draw.rounded_rectangle([sw_x, ty + 4, sw_x + 36, ty + 22], radius=9, fill=PRIMARY_GOLD if on else WARM_BORDER)
        draw.ellipse([sw_x + (18 if on else 2), ty + 6, sw_x + (34 if on else 18), ty + 20], fill=WHITE)
        ty += 56
        
    draw_button(draw, 20, 740, W - 40, 50, "Next →", is_primary=True)
    save_screen(img, "02-registration/registration_privacy_consent.png")

def gen_reg_step6():
    img, draw = create_base_canvas(W, H)
    draw_status_bar(draw, W)
    draw_reg_stepper(draw, 6, "Review & Submit", "Please review your details before submitting.")
    
    draw_card(draw, 20, 160, W - 40, 440, radius=20)
    
    sections = [
        ("Personal Information", "Priya Sharma • priya.s@maatram.org\n+91 98765 43210"),
        ("Category & Institution", "Student Volunteer\nSathyabama Institute of Science and Tech"),
        ("Skills & Availability", "Mentoring, Event Support, Career Guidance\nWeekends • Chennai"),
        ("Privacy & Consents", "5 of 5 optional consents accepted"),
    ]
    
    sy = 180
    for stitle, sdesc in sections:
        draw.ellipse([40, sy + 4, 52, sy + 16], fill=SUCCESS_GREEN)
        draw.text((60, sy), stitle, fill=DEEP_NAVY, font=FONT_HEAD_BOLD)
        draw.text((60, sy + 20), sdesc, fill=SECONDARY_TEXT, font=FONT_BODY_SM)
        sy += 64
        
    draw_button(draw, 20, 740, W - 40, 50, "Submit Application ✓", is_primary=True)
    save_screen(img, "02-registration/registration_review_submit.png")

# ==============================================================================
# GROUP 3: VERIFICATION & STATUS
# ==============================================================================

def gen_email_verification():
    img, draw = create_base_canvas(W, H)
    draw_status_bar(draw, W)
    draw_header_nav(img, draw, "Verify Email", W, show_back=True)
    
    draw_card(draw, 20, 120, W - 40, 460, radius=24)
    
    draw.ellipse([W//2 - 40, 160, W//2 + 40, 240], fill=LIGHT_GOLD)
    draw.rectangle([W//2 - 24, 186, W//2 + 24, 216], outline=PRIMARY_GOLD, width=3, fill=WHITE)
    
    draw.text((W//2 - 70, 260), "Verify Your Email", fill=DEEP_NAVY, font=FONT_TITLE_MD)
    draw.text((44, 300), "We've sent a 6-digit verification code to:\npriya.s@maatram.org", fill=SECONDARY_TEXT, font=FONT_BODY_MD, align="center")
    
    # 6 OTP boxes
    box_w = 40
    gap = 8
    start_x = (W - (6 * box_w + 5 * gap)) // 2
    for i in range(6):
        bx = start_x + i * (box_w + gap)
        draw.rounded_rectangle([bx, 360, bx + box_w, 410], radius=10, fill=WHITE, outline=PRIMARY_GOLD if i == 2 else WARM_BORDER, width=2 if i == 2 else 1)
        if i < 2:
            draw.text((bx + 14, 374), str(i + 4), fill=DEEP_NAVY, font=FONT_TITLE_MD)
            
    draw.text((W//2 - 60, 440), "Resend code in 00:45", fill=SECONDARY_TEXT, font=FONT_BODY_SM)
    draw_button(draw, 44, 490, W - 88, 48, "Verify Email", is_primary=True)
    
    save_screen(img, "03-verification/email_verification.png")

def gen_pending_verification():
    img, draw = create_base_canvas(W, H)
    draw_status_bar(draw, W)
    draw_header_brand(img, draw, W)
    
    draw_card(draw, 20, 140, W - 40, 480, radius=24)
    
    # Hourglass motif
    draw.ellipse([W//2 - 40, 180, W//2 + 40, 260], fill=LIGHT_GOLD)
    draw.polygon([(W//2 - 16, 200), (W//2 + 16, 200), (W//2, 220)], fill=PRIMARY_GOLD)
    draw.polygon([(W//2 - 16, 240), (W//2 + 16, 240), (W//2, 220)], fill=PRIMARY_GOLD)
    
    draw.text((W//2 - 110, 280), "Email Verification Pending", fill=DEEP_NAVY, font=FONT_TITLE_MD)
    draw.text((44, 320), "Please verify your email address to continue your\nregistration. We sent a link to priya.s@maatram.org", fill=SECONDARY_TEXT, font=FONT_BODY_MD, align="center")
    
    items = [
        "Check your inbox and spam folder",
        "Use the 6-digit code or link we sent",
        "Verification links expire in 10 minutes"
    ]
    for i, it in enumerate(items):
        iy = 390 + i * 30
        draw.ellipse([46, iy, 56, iy + 10], fill=PRIMARY_GOLD)
        draw.text((66, iy - 2), it, fill=DEEP_NAVY, font=FONT_BODY_SM)
        
    draw_button(draw, 44, 520, W - 88, 48, "Resend Email", is_primary=False)
    save_screen(img, "03-verification/pending_verification.png")

def gen_pending_approval():
    img, draw = create_base_canvas(W, H)
    draw_status_bar(draw, W)
    draw_header_brand(img, draw, W)
    
    draw_card(draw, 20, 140, W - 40, 460, radius=24)
    
    # Clipboard motif
    draw.ellipse([W//2 - 40, 180, W//2 + 40, 260], fill=LIGHT_GOLD)
    draw.rounded_rectangle([W//2 - 18, 200, W//2 + 18, 240], radius=4, fill=WHITE, outline=PRIMARY_GOLD, width=2)
    draw.rounded_rectangle([W//2 - 10, 194, W//2 + 10, 204], radius=2, fill=PRIMARY_GOLD)
    
    draw.text((W//2 - 94, 280), "Pending Under Review", fill=DEEP_NAVY, font=FONT_TITLE_MD)
    draw.text((44, 320), "Your volunteer application is currently being reviewed\nby the Maatram team. You will be notified once\nyour profile is approved.", fill=SECONDARY_TEXT, font=FONT_BODY_MD, align="center")
    
    # Timeline
    draw.line([60, 400, 60, 470], fill=PRIMARY_GOLD, width=2)
    draw.ellipse([54, 396, 66, 408], fill=SUCCESS_GREEN)
    draw.text((76, 396), "Application Submitted", fill=DEEP_NAVY, font=FONT_BODY_SM_BOLD)
    draw.text((76, 412), "Completed on 15 Nov 2026", fill=SECONDARY_TEXT, font=FONT_CAPTION)
    
    draw.ellipse([54, 460, 66, 472], fill=PRIMARY_GOLD)
    draw.text((76, 460), "Coordinator Review", fill=DEEP_NAVY, font=FONT_BODY_SM_BOLD)
    draw.text((76, 476), "In Progress (Typically 24-48 hrs)", fill=SECONDARY_TEXT, font=FONT_CAPTION)
    
    save_screen(img, "03-verification/pending_approval.png")

def gen_rejected():
    img, draw = create_base_canvas(W, H)
    draw_status_bar(draw, W)
    draw_header_brand(img, draw, W)
    
    draw_card(draw, 20, 140, W - 40, 440, radius=24)
    
    # Clipboard with cross
    draw.ellipse([W//2 - 40, 180, W//2 + 40, 260], fill=LIGHT_RED)
    draw.rounded_rectangle([W//2 - 18, 200, W//2 + 18, 240], radius=4, fill=WHITE, outline=CRITICAL_RED, width=2)
    draw.line([W//2 - 10, 212, W//2 + 10, 228], fill=CRITICAL_RED, width=2)
    draw.line([W//2 + 10, 212, W//2 - 10, 228], fill=CRITICAL_RED, width=2)
    
    draw.text((W//2 - 82, 280), "Application Update", fill=DEEP_NAVY, font=FONT_TITLE_MD)
    draw.text((44, 320), "We are unable to approve your volunteer application\nat this time. Please contact our support team if\nyou believe this is in error.", fill=SECONDARY_TEXT, font=FONT_BODY_MD, align="center")
    
    draw_button(draw, 44, 440, W - 88, 48, "Contact Support", is_primary=True)
    save_screen(img, "03-verification/application_rejected.png")

def gen_post_approval_welcome():
    # Copy from existing runtime screenshot if available or regenerate
    src = "docs/audits/ui-ux/screenshots/02_post_approval_welcome_runtime.png"
    if os.path.exists(src):
        img = Image.open(src)
        save_screen(img, "03-verification/post_approval_welcome.png")
    else:
        img, draw = create_base_canvas(W, H)
        draw_status_bar(draw, W)
        draw_card(draw, 20, 160, W - 40, 420, radius=24)
        draw.text((W//2 - 90, 260), "Welcome to Maatram!", fill=DEEP_NAVY, font=FONT_TITLE_MD)
        draw.text((44, 310), "You're now a verified volunteer. Let's create\na better tomorrow together!", fill=SECONDARY_TEXT, font=FONT_BODY_MD, align="center")
        draw_button(draw, 44, 460, W - 88, 48, "Go to Home", is_primary=True)
        save_screen(img, "03-verification/post_approval_welcome.png")

# ==============================================================================
# GROUP 4: MAIN APPLICATION
# ==============================================================================

def gen_events_screen():
    src = "docs/audits/ui-ux/screenshots/04_events_screen_runtime.png"
    if os.path.exists(src):
        img = Image.open(src)
        save_screen(img, "04-main-application/events.png")
    else:
        img, draw = create_base_canvas(W, H)
        draw_status_bar(draw, W)
        draw_header_brand(img, draw, W)
        draw_bottom_nav(draw, W, H, active_index=1)
        save_screen(img, "04-main-application/events.png")

def gen_event_details():
    img, draw = create_base_canvas(W, H)
    draw_status_bar(draw, W)
    
    # Event Hero Image
    hero_path = "mobile/assets/images/school-visit.jpg"
    if os.path.exists(hero_path):
        hero = Image.open(hero_path).convert("RGBA")
        hero_resized = hero.resize((W, 220), Image.Resampling.LANCZOS)
        img.paste(hero_resized, (0, 0), hero_resized)
    
    # Floating Back button on hero
    draw.ellipse([20, 48, 56, 84], fill=(255, 255, 255, 200))
    draw.line([40, 60, 34, 66], fill=DEEP_NAVY, width=2)
    draw.line([34, 66, 40, 72], fill=DEEP_NAVY, width=2)
    
    # Content Body Card
    card_y = 200
    card_h = 560
    draw.rounded_rectangle([0, card_y, W, card_y + card_h], radius=24, fill=WHITE)
    
    # Category Pill
    draw_pill(draw, 20, card_y + 20, "School Visit", bg=LIGHT_BLUE, fg=ACCENT_BLUE)
    draw_pill(draw, 110, card_y + 20, "15 / 20 Registered", bg=LIGHT_GREEN, fg=SUCCESS_GREEN)
    
    # Title
    draw.text((20, card_y + 54), "School Visit – Government\nHigh School", fill=DEEP_NAVY, font=FONT_TITLE_MD)
    
    # Date, Time, Venue Chips
    chips = [
        ("📅 26 Nov 2026", "🕒 2:30 PM – 6:30 PM (4.0 hrs)"),
        ("📍 Government High School, Chennai", "👥 Coordinator: Priya K.")
    ]
    cy = card_y + 116
    for c1, c2 in chips:
        draw.text((20, cy), c1, fill=DEEP_NAVY, font=FONT_BODY_SM_BOLD)
        draw.text((20, cy + 20), c2, fill=SECONDARY_TEXT, font=FONT_BODY_SM)
        cy += 44
        
    draw.line([20, cy, W - 20, cy], fill=WARM_BORDER, width=1)
    
    # Description
    draw.text((20, cy + 16), "About This Event", fill=DEEP_NAVY, font=FONT_HEAD_BOLD)
    desc = (
        "Join fellow volunteers for an interactive career guidance\n"
        "and science literacy mentoring session for high school\n"
        "students. Volunteers will facilitate group discussions,\n"
        "mentor 3-4 students, and inspire higher education."
    )
    draw.text((20, cy + 38), desc, fill=SECONDARY_TEXT, font=FONT_BODY_MD)
    
    # Volunteer Prerequisites
    draw.text((20, cy + 118), "Prerequisites", fill=DEEP_NAVY, font=FONT_HEAD_BOLD)
    draw.text((20, cy + 140), "• Maatram black volunteer t-shirt\n• Arrive 15 minutes before reporting time\n• High school mentoring orientation completed", fill=SECONDARY_TEXT, font=FONT_BODY_SM)
    
    # Fixed bottom action bar
    draw.rectangle([0, H - 76, W, H], fill=WHITE, outline=WARM_BORDER)
    draw_button(draw, 20, H - 64, W - 40, 48, "Register as Volunteer", is_primary=True)
    
    save_screen(img, "04-main-application/event_details.png")

def gen_event_registration():
    img, draw = create_base_canvas(W, H)
    draw_status_bar(draw, W)
    draw_header_nav(img, draw, "Confirm Registration", W, show_back=True)
    
    draw_card(draw, 20, 110, W - 40, 620, radius=24)
    
    # Event summary banner
    draw.text((40, 136), "School Visit – Government High School", fill=DEEP_NAVY, font=FONT_HEAD_BOLD)
    draw.text((40, 158), "26 Nov 2026 • 2:30 PM – 6:30 PM • 4.0 Hours", fill=SECONDARY_TEXT, font=FONT_BODY_SM)
    draw.line([40, 186, W - 40, 186], fill=WARM_BORDER)
    
    # Commitment checklist
    draw.text((40, 204), "Volunteer Commitments", fill=DEEP_NAVY, font=FONT_HEAD_BOLD)
    commitments = [
        "I will arrive on time and stay for the full duration",
        "I will wear the official Maatram volunteer t-shirt",
        "I agree to follow the student safeguarding guidelines",
        "I will notify coordinators 24 hours prior if unable to attend"
    ]
    for i, c in enumerate(commitments):
        cy = 232 + i * 36
        draw.rectangle([40, cy + 2, 54, cy + 16], outline=PRIMARY_GOLD, width=2, fill=LIGHT_GOLD)
        draw.text((44, cy), "✓", fill=DEEP_NAVY, font=FONT_CAPTION_BOLD)
        draw.text((62, cy), c[:42] + ("..." if len(c) > 42 else ""), fill=DEEP_NAVY, font=FONT_BODY_SM)
        
    draw.line([40, 386, W - 40, 386], fill=WARM_BORDER)
    
    # Inputs
    draw_input(draw, 40, 420, W - 80, 44, "Emergency Contact Number", "+91 98765 11223")
    draw_input(draw, 40, 492, W - 80, 44, "Special Accommodations / Notes", "None")
    
    draw_button(draw, 40, 560, W - 80, 48, "Confirm Registration ✓", is_primary=True)
    save_screen(img, "04-main-application/event_registration.png")

def gen_activity_details():
    img, draw = create_base_canvas(W, H)
    draw_status_bar(draw, W)
    draw_header_nav(img, draw, "Activity Record", W, show_back=True)
    
    draw_card(draw, 20, 110, W - 40, 580, radius=24)
    
    # Header badge
    draw_pill(draw, 40, 136, "Completed & Verified ✓", bg=LIGHT_GREEN, fg=SUCCESS_GREEN)
    draw.text((40, 172), "School Visit – Government High School", fill=DEEP_NAVY, font=FONT_TITLE_MD)
    
    # Metric cards
    draw_card(draw, 40, 226, 145, 76, radius=14, fill=LIGHT_GOLD, border=PRIMARY_GOLD)
    draw.text((54, 240), "Hours Credited", fill=DEEP_NAVY, font=FONT_CAPTION)
    draw.text((54, 258), "4.0 hrs", fill=DEEP_NAVY, font=FONT_TITLE_MD)
    
    draw_card(draw, 195, 226, 145, 76, radius=14, fill=LIGHT_GOLD, border=PRIMARY_GOLD)
    draw.text((209, 240), "Points Earned", fill=DEEP_NAVY, font=FONT_CAPTION)
    draw.text((209, 258), "+50 pts", fill=PRIMARY_GOLD, font=FONT_TITLE_MD)
    
    # Timeline details
    draw.text((40, 326), "Attendance Log", fill=DEEP_NAVY, font=FONT_HEAD_BOLD)
    logs = [
        ("Check-In Time", "26 Nov 2026, 2:24 PM • QR Code Verified"),
        ("Check-Out Time", "26 Nov 2026, 6:32 PM • Coordinator Signed"),
        ("Reporting Officer", "Priya K. (Lead Coordinator)"),
        ("Ledger Transaction", "TXN-2026-ATT-084920")
    ]
    ly = 356
    for ltitle, ldesc in logs:
        draw.text((40, ly), ltitle, fill=SECONDARY_TEXT, font=FONT_CAPTION)
        draw.text((40, ly + 14), ldesc, fill=DEEP_NAVY, font=FONT_BODY_SM_BOLD)
        ly += 38
        
    draw_button(draw, 40, 520, W - 80, 48, "Download Certificate 📄", is_primary=False)
    save_screen(img, "04-main-application/activity_details.png")

def gen_leaderboard_screen():
    src = "docs/audits/ui-ux/screenshots/05_leaderboard_screen_runtime.png"
    if os.path.exists(src):
        img = Image.open(src)
        save_screen(img, "04-main-application/leaderboard.png")
    else:
        img, draw = create_base_canvas(W, H)
        draw_status_bar(draw, W)
        draw_header_brand(img, draw, W)
        draw_bottom_nav(draw, W, H, active_index=2)
        save_screen(img, "04-main-application/leaderboard.png")

def gen_more_screen():
    src = "docs/audits/ui-ux/screenshots/06_more_screen_runtime.png"
    if os.path.exists(src):
        img = Image.open(src)
        save_screen(img, "04-main-application/more.png")
    else:
        img, draw = create_base_canvas(W, H)
        draw_status_bar(draw, W)
        draw_header_brand(img, draw, W)
        draw_bottom_nav(draw, W, H, active_index=3)
        save_screen(img, "04-main-application/more.png")

# ==============================================================================
# GROUP 5: VOLUNTEER ACCOUNT & PERSONAL INFO
# ==============================================================================

def gen_profile():
    img, draw = create_base_canvas(W, H)
    draw_status_bar(draw, W)
    draw_header_nav(img, draw, "My Profile", W, show_back=True, action_text="Edit")
    
    # Profile Card
    draw_card(draw, 20, 110, W - 40, 220, radius=24)
    # Large avatar with gold ring
    draw.ellipse([W//2 - 42, 130, W//2 + 42, 214], fill=(229, 231, 235, 255), outline=PRIMARY_GOLD, width=3)
    draw.text((W//2 - 40, 224), "Priya S.", fill=DEEP_NAVY, font=FONT_TITLE_MD)
    draw_pill(draw, W//2 - 42, 254, "Student Volunteer", bg=LIGHT_BLUE, fg=ACCENT_BLUE)
    draw.text((W//2 - 110, 286), "Sathyabama Institute of Science and Technology", fill=SECONDARY_TEXT, font=FONT_CAPTION)
    
    # 4 Stats Grid
    stats = [
        ("Points", "180", PRIMARY_GOLD),
        ("Hours", "24", DEEP_NAVY),
        ("Events", "5", DEEP_NAVY),
        ("Rank", "#1", PRIMARY_GOLD),
    ]
    sw = (W - 56) // 4
    for i, (label, val, col) in enumerate(stats):
        sx = 20 + i * (sw + 4)
        draw_card(draw, sx, 344, sw, 70, radius=14)
        draw.text((sx + 10, 354), label, fill=SECONDARY_TEXT, font=FONT_CAPTION)
        draw.text((sx + 10, 372), val, fill=col, font=FONT_TITLE_MD)
        
    # Volunteer Bio & Information Card
    draw_card(draw, 20, 430, W - 40, 220, radius=20)
    draw.text((36, 448), "About Volunteer", fill=DEEP_NAVY, font=FONT_HEAD_BOLD)
    draw.text((36, 472), "Passionate student mentor enthusiastic about youth\neducation, career counseling, and community literacy.\nActively volunteering with Maatram since 2025.", fill=SECONDARY_TEXT, font=FONT_BODY_SM)
    
    draw.line([36, 532, W - 36, 532], fill=WARM_BORDER)
    draw.text((36, 546), "Contact Information", fill=DEEP_NAVY, font=FONT_HEAD_BOLD)
    draw.text((36, 570), "Email: priya.s@maatram.org\nPhone: +91 98765 43210\nLocation: Chennai, Tamil Nadu", fill=SECONDARY_TEXT, font=FONT_BODY_SM)
    
    draw_button(draw, 20, 680, W - 40, 48, "Manage Account Settings", is_primary=False)
    draw_bottom_nav(draw, W, H, active_index=3)
    save_screen(img, "05-volunteer-account/profile.png")

def gen_edit_profile():
    img, draw = create_base_canvas(W, H)
    draw_status_bar(draw, W)
    draw_header_nav(img, draw, "Edit Profile", W, show_back=True)
    
    draw_card(draw, 20, 110, W - 40, 540, radius=24)
    draw_input(draw, 40, 150, W - 80, 44, "Full Name", "Priya Sharma")
    draw_input(draw, 40, 224, W - 80, 44, "Contact Number", "+91 98765 43210")
    draw_input(draw, 40, 298, W - 80, 44, "College / Institution", "Sathyabama Institute of Science and Tech")
    draw_input(draw, 40, 372, W - 80, 44, "Location / City", "Chennai, Tamil Nadu")
    draw_input(draw, 40, 446, W - 80, 44, "Bio & Motivation", "Passionate student mentor...")
    
    draw_button(draw, 40, 510, W - 80, 48, "Save Changes ✓", is_primary=True)
    save_screen(img, "05-volunteer-account/edit_profile.png")

def gen_profile_photo():
    img, draw = create_base_canvas(W, H)
    draw_status_bar(draw, W)
    draw_header_nav(img, draw, "Profile Photo", W, show_back=True)
    
    draw_card(draw, 20, 120, W - 40, 520, radius=24)
    
    # Large Photo Preview
    draw.ellipse([W//2 - 70, 160, W//2 + 70, 300], fill=(229, 231, 235, 255), outline=PRIMARY_GOLD, width=4)
    draw.text((W//2 - 40, 320), "Current Photo", fill=DEEP_NAVY, font=FONT_HEAD_BOLD)
    draw.text((50, 344), "Please provide a clear headshot with neutral lighting.\nOfficial photo helps coordinators identify you at events.", fill=SECONDARY_TEXT, font=FONT_BODY_SM, align="center")
    
    draw_button(draw, 44, 410, W - 88, 46, "📷 Take New Photo", is_primary=True)
    draw_button(draw, 44, 466, W - 88, 46, "🖼️ Choose from Gallery", is_primary=False)
    draw.text((W//2 - 38, 532), "Remove Photo", fill=CRITICAL_RED, font=FONT_BODY_SM_BOLD)
    
    save_screen(img, "05-volunteer-account/profile_photo.png")

def gen_points():
    img, draw = create_base_canvas(W, H)
    draw_status_bar(draw, W)
    draw_header_nav(img, draw, "My Points", W, show_back=True, action_text="History")
    
    # Hero points card
    draw_card(draw, 20, 110, W - 40, 220, radius=24, fill=LIGHT_GOLD, border=PRIMARY_GOLD)
    draw.text((40, 136), "Total Points Balance", fill=DEEP_NAVY, font=FONT_BODY_MD)
    draw.text((40, 160), "180", fill=PRIMARY_GOLD, font=FONT_TITLE_LG)
    draw.text((120, 178), "PTS", fill=DEEP_NAVY, font=FONT_TITLE_SM)
    
    draw_pill(draw, 40, 214, "★ Gold Tier Volunteer", bg=PRIMARY_GOLD, fg=DEEP_NAVY)
    
    # Progress to next tier
    draw.text((40, 254), "20 pts needed to reach Platinum Tier (200 pts)", fill=SECONDARY_TEXT, font=FONT_CAPTION)
    draw.rounded_rectangle([40, 274, W - 40, 282], radius=4, fill=WHITE)
    draw.rounded_rectangle([40, 274, 40 + int((W - 80) * 0.9), 282], radius=4, fill=PRIMARY_GOLD)
    
    # Breakdown Card
    draw_card(draw, 20, 350, W - 40, 280, radius=20)
    draw.text((36, 370), "Points Breakdown by Category", fill=DEEP_NAVY, font=FONT_HEAD_BOLD)
    
    breakdown = [
        ("School Visits", "80 pts", "2 events completed", ACCENT_BLUE),
        ("Mock Interview Panels", "60 pts", "2 sessions conducted", ACCENT_PURPLE),
        ("BGV Support Drives", "40 pts", "1 verification drive", ACCENT_AMBER),
    ]
    by = 404
    for btitle, bpts, bsub, col in breakdown:
        draw.ellipse([36, by + 4, 46, by + 14], fill=col)
        draw.text((54, by), btitle, fill=DEEP_NAVY, font=FONT_BODY_SM_BOLD)
        draw.text((54, by + 16), bsub, fill=SECONDARY_TEXT, font=FONT_CAPTION)
        draw.text((W - 90, by + 6), bpts, fill=DEEP_NAVY, font=FONT_BODY_BOLD)
        by += 48
        
    draw_button(draw, 20, 650, W - 40, 48, "View Full Points Ledger", is_primary=False)
    draw_bottom_nav(draw, W, H, active_index=3)
    save_screen(img, "05-volunteer-account/points.png")

def gen_points_history():
    img, draw = create_base_canvas(W, H)
    draw_status_bar(draw, W)
    draw_header_nav(img, draw, "Points History", W, show_back=True)
    
    draw_card(draw, 20, 110, W - 40, 620, radius=24)
    draw.text((36, 130), "Chronological Ledger", fill=DEEP_NAVY, font=FONT_HEAD_BOLD)
    
    txns = [
        ("+50 pts", "School Visit – Govt High School", "26 Nov 2026 • 4.0 hrs verified", SUCCESS_GREEN),
        ("+40 pts", "Mock Interview Session", "28 Oct 2026 • 2.0 hrs verified", SUCCESS_GREEN),
        ("+30 pts", "BGV Support Verification Drive", "30 Oct 2026 • 4.0 hrs verified", SUCCESS_GREEN),
        ("+40 pts", "Career Orientation Panel", "12 Oct 2026 • 2.5 hrs verified", SUCCESS_GREEN),
        ("+20 pts", "Volunteer Orientation Complete", "01 Sep 2026 • Onboarding bonus", SUCCESS_GREEN),
    ]
    ty = 166
    for pts, title, meta, pcol in txns:
        draw.rounded_rectangle([36, ty, W - 36, ty + 70], radius=14, fill=WHITE, outline=WARM_BORDER)
        draw.text((48, ty + 12), title[:30] + ("..." if len(title) > 30 else ""), fill=DEEP_NAVY, font=FONT_BODY_SM_BOLD)
        draw.text((48, ty + 32), meta, fill=SECONDARY_TEXT, font=FONT_CAPTION)
        draw.text((W - 96, ty + 20), pts, fill=pcol, font=FONT_BODY_BOLD)
        ty += 80
        
    save_screen(img, "05-volunteer-account/points_history.png")

def gen_achievements():
    img, draw = create_base_canvas(W, H)
    draw_status_bar(draw, W)
    draw_header_nav(img, draw, "Achievements", W, show_back=True)
    
    # Badges Grid
    draw_card(draw, 20, 110, W - 40, 600, radius=24)
    draw.text((36, 130), "Badges & Milestones (3 / 8 Unlocked)", fill=DEEP_NAVY, font=FONT_HEAD_BOLD)
    
    badges = [
        ("🏆 First Step", "Completed first event", True),
        ("⭐ Youth Mentor", "Mentored 10+ students", True),
        ("🌟 Century Club", "Earned 100+ points", True),
        ("🎯 Consistency Star", "Volunteer 3 months row", False),
        ("🚀 Master Interviewer", "Conduct 5 mock panels", False),
        ("🤝 Community Champion", "Completed 10 events", False),
    ]
    
    by = 166
    for i, (bname, bdesc, unlocked) in enumerate(badges):
        bx = 36 if i % 2 == 0 else 195
        card_w = 145
        draw_card(draw, bx, by, card_w, 110, radius=14, fill=LIGHT_GOLD if unlocked else WHITE, border=PRIMARY_GOLD if unlocked else WARM_BORDER)
        draw.text((bx + 12, by + 16), "🎖️" if unlocked else "🔒", font=FONT_TITLE_MD)
        draw.text((bx + 12, by + 48), bname, fill=DEEP_NAVY, font=FONT_BODY_SM_BOLD)
        draw.text((bx + 12, by + 68), bdesc[:22] + "...", fill=SECONDARY_TEXT, font=FONT_CAPTION)
        if i % 2 == 1:
            by += 124
            
    draw_bottom_nav(draw, W, H, active_index=3)
    save_screen(img, "05-volunteer-account/achievements.png")

def gen_achievement_details():
    img, draw = create_base_canvas(W, H)
    draw_status_bar(draw, W)
    draw_header_nav(img, draw, "Badge Details", W, show_back=True)
    
    draw_card(draw, 20, 120, W - 40, 520, radius=24)
    
    # Big Medal Icon
    draw.ellipse([W//2 - 50, 160, W//2 + 50, 260], fill=LIGHT_GOLD, outline=PRIMARY_GOLD, width=3)
    draw.text((W//2 - 18, 190), "⭐", fill=PRIMARY_GOLD, font=FONT_TITLE_LG)
    
    draw.text((W//2 - 64, 280), "Youth Mentor", fill=DEEP_NAVY, font=FONT_TITLE_MD)
    draw_pill(draw, W//2 - 38, 314, "Gold Tier Badge", bg=PRIMARY_GOLD, fg=DEEP_NAVY)
    
    draw.text((44, 356), "Unlocked on 28 October 2026", fill=SECONDARY_TEXT, font=FONT_CAPTION, align="center")
    draw.line([44, 380, W - 44, 380], fill=WARM_BORDER)
    
    draw.text((44, 396), "Criteria & Impact", fill=DEEP_NAVY, font=FONT_HEAD_BOLD)
    draw.text((44, 420), "Awarded to dedicated volunteers who complete at least\n5 high school mentorship sessions and guide 10+\nunderprivileged students toward higher education.", fill=SECONDARY_TEXT, font=FONT_BODY_SM)
    
    draw_button(draw, 44, 540, W - 88, 48, "Share Achievement 🌟", is_primary=True)
    save_screen(img, "05-volunteer-account/achievement_details.png")

# ==============================================================================
# GROUP 6: NOTIFICATIONS & SETTINGS
# ==============================================================================

def gen_notifications():
    img, draw = create_base_canvas(W, H)
    draw_status_bar(draw, W)
    draw_header_nav(img, draw, "Notifications", W, show_back=True, action_text="Clear All")
    
    draw_card(draw, 20, 110, W - 40, 600, radius=24)
    draw.text((36, 130), "Today", fill=SECONDARY_TEXT, font=FONT_BODY_SM_BOLD)
    
    notifs = [
        ("Event Reminder: School Visit", "Reporting tomorrow at 2:30 PM at Govt High School", "2 hrs ago", True),
        ("Points Awarded! (+50 pts)", "Attendance verified for Mock Interview Session", "5 hrs ago", True),
        ("New Opportunity Available", "Admissions Guidance Drive open for registration", "1 day ago", False),
        ("Application Approved", "Welcome to Maatram Volunteer Portal!", "3 days ago", False),
    ]
    ny = 156
    for title, desc, time_str, unread in notifs:
        draw.rounded_rectangle([36, ny, W - 36, ny + 72], radius=14, fill=LIGHT_GOLD if unread else WHITE, outline=WARM_BORDER)
        if unread:
            draw.ellipse([46, ny + 16, 54, ny + 24], fill=PRIMARY_GOLD)
        draw.text((62 if unread else 48, ny + 12), title, fill=DEEP_NAVY, font=FONT_BODY_SM_BOLD)
        draw.text((62 if unread else 48, ny + 32), desc[:36] + "...", fill=SECONDARY_TEXT, font=FONT_CAPTION)
        draw.text((62 if unread else 48, ny + 48), time_str, fill=SECONDARY_TEXT, font=FONT_CAPTION)
        ny += 82
        
    draw_bottom_nav(draw, W, H, active_index=3)
    save_screen(img, "06-notifications-settings/notifications.png")

def gen_notification_details():
    img, draw = create_base_canvas(W, H)
    draw_status_bar(draw, W)
    draw_header_nav(img, draw, "Notification", W, show_back=True)
    
    draw_card(draw, 20, 120, W - 40, 480, radius=24)
    draw_pill(draw, 40, 144, "Event Reminder", bg=LIGHT_BLUE, fg=ACCENT_BLUE)
    draw.text((40, 180), "School Visit – Govt High School\nReporting Tomorrow", fill=DEEP_NAVY, font=FONT_TITLE_MD)
    draw.text((40, 240), "26 November 2026 • 2:30 PM Reporting Time", fill=SECONDARY_TEXT, font=FONT_BODY_SM)
    draw.line([40, 268, W - 40, 268], fill=WARM_BORDER)
    
    body = (
        "Dear Priya,\n\n"
        "This is a friendly reminder for tomorrow's School Visit\n"
        "session at Government High School, Chennai.\n\n"
        "Please remember to wear your official black volunteer\n"
        "t-shirt and carry a valid student ID card. Your lead\n"
        "coordinator Priya K. will meet you at the main gate."
    )
    draw.text((40, 286), body, fill=DEEP_NAVY, font=FONT_BODY_SM)
    
    draw_button(draw, 40, 490, W - 80, 48, "View Event Details →", is_primary=True)
    save_screen(img, "06-notifications-settings/notification_details.png")

def gen_notification_settings():
    img, draw = create_base_canvas(W, H)
    draw_status_bar(draw, W)
    draw_header_nav(img, draw, "Notification Settings", W, show_back=True)
    
    draw_card(draw, 20, 110, W - 40, 460, radius=24)
    draw.text((36, 130), "Push & Email Notifications", fill=DEEP_NAVY, font=FONT_HEAD_BOLD)
    
    toggles = [
        ("Event Reminders & Updates", "24h and 2h alerts before registered events", True),
        ("Points & Badge Awards", "Notifications when points/badges are credited", True),
        ("New Event Announcements", "Alerts when events match your skills & city", True),
        ("Foundation Newsletter", "Monthly community impact stories", False),
        ("Direct Coordinator Messages", "Critical event day coordination alerts", True),
    ]
    ty = 166
    for title, desc, on in toggles:
        draw.text((36, ty), title, fill=DEEP_NAVY, font=FONT_BODY_SM_BOLD)
        draw.text((36, ty + 18), desc, fill=SECONDARY_TEXT, font=FONT_CAPTION)
        sw_x = W - 80
        draw.rounded_rectangle([sw_x, ty + 4, sw_x + 36, ty + 22], radius=9, fill=PRIMARY_GOLD if on else WARM_BORDER)
        draw.ellipse([sw_x + (18 if on else 2), ty + 6, sw_x + (34 if on else 18), ty + 20], fill=WHITE)
        ty += 56
        
    draw_button(draw, 20, 600, W - 40, 48, "Save Preferences", is_primary=True)
    save_screen(img, "06-notifications-settings/notification_settings.png")

def gen_privacy_consent():
    img, draw = create_base_canvas(W, H)
    draw_status_bar(draw, W)
    draw_header_nav(img, draw, "Privacy & Consents", W, show_back=True)
    
    draw_card(draw, 20, 110, W - 40, 520, radius=24)
    draw.text((36, 130), "Manage Your Privacy Preferences", fill=DEEP_NAVY, font=FONT_HEAD_BOLD)
    
    consents = [
        ("Public Leaderboard Visibility", "Display your name and points on rankings", True),
        ("Volunteer Directory Listing", "Allow other approved volunteers to view profile", True),
        ("Activity Photos in Stories", "Allow photos of you at events in impact media", True),
        ("Academic Progress Data", "Share volunteering hours with college coordinators", True),
        ("Anonymized Research Consent", "Include anonymized activity metrics in research", True),
    ]
    cy = 166
    for title, desc, on in consents:
        draw.text((36, cy), title, fill=DEEP_NAVY, font=FONT_BODY_SM_BOLD)
        draw.text((36, cy + 18), desc, fill=SECONDARY_TEXT, font=FONT_CAPTION)
        sw_x = W - 80
        draw.rounded_rectangle([sw_x, cy + 4, sw_x + 36, cy + 22], radius=9, fill=PRIMARY_GOLD if on else WARM_BORDER)
        draw.ellipse([sw_x + (18 if on else 2), cy + 6, sw_x + (34 if on else 18), cy + 20], fill=WHITE)
        cy += 60
        
    draw_button(draw, 20, 660, W - 40, 48, "Update Privacy Settings", is_primary=True)
    save_screen(img, "06-notifications-settings/privacy_consent.png")

def gen_settings():
    img, draw = create_base_canvas(W, H)
    draw_status_bar(draw, W)
    draw_header_nav(img, draw, "App Settings", W, show_back=True)
    
    draw_card(draw, 20, 110, W - 40, 460, radius=24)
    draw.text((36, 130), "Preferences & Security", fill=DEEP_NAVY, font=FONT_HEAD_BOLD)
    
    settings_items = [
        ("App Language", "English (தமிழ் Coming Soon)", False),
        ("Theme / Appearance", "Light Theme (Warm Cream)", False),
        ("Biometric App Lock", "Require Face ID / Fingerprint to open", True),
        ("Offline Data Caching", "Save registered event tickets offline", True),
        ("Clear Cached Media", "Free up 42 MB local storage", False),
    ]
    sy = 166
    for title, desc, is_toggle in settings_items:
        draw.text((36, sy), title, fill=DEEP_NAVY, font=FONT_BODY_SM_BOLD)
        draw.text((36, sy + 18), desc, fill=SECONDARY_TEXT, font=FONT_CAPTION)
        if is_toggle:
            sw_x = W - 80
            draw.rounded_rectangle([sw_x, sy + 4, sw_x + 36, sy + 22], radius=9, fill=PRIMARY_GOLD)
            draw.ellipse([sw_x + 18, sy + 6, sw_x + 34, sy + 20], fill=WHITE)
        else:
            draw.text((W - 60, sy + 6), "›", fill=SECONDARY_TEXT, font=FONT_TITLE_MD)
        sy += 56
        
    draw.text((W//2 - 50, 600), "Version 1.0.0 (Build 42)", fill=SECONDARY_TEXT, font=FONT_CAPTION)
    save_screen(img, "06-notifications-settings/settings.png")

def gen_help_support():
    img, draw = create_base_canvas(W, H)
    draw_status_bar(draw, W)
    draw_header_nav(img, draw, "Help & Support", W, show_back=True)
    
    draw_card(draw, 20, 110, W - 40, 520, radius=24)
    draw.text((36, 130), "Frequently Asked Questions", fill=DEEP_NAVY, font=FONT_HEAD_BOLD)
    
    faqs = [
        "How do I earn volunteering points?",
        "When will my attendance be verified?",
        "How do I cancel my registration?",
        "Can I download my service certificate?",
        "What should I wear to school visits?",
    ]
    fy = 166
    for q in faqs:
        draw.rounded_rectangle([36, fy, W - 36, fy + 46], radius=12, fill=WHITE, outline=WARM_BORDER)
        draw.text((48, fy + 14), q, fill=DEEP_NAVY, font=FONT_BODY_SM)
        draw.text((W - 64, fy + 12), "+", fill=PRIMARY_GOLD, font=FONT_TITLE_SM)
        fy += 54
        
    draw.line([36, fy + 10, W - 36, fy + 10], fill=WARM_BORDER)
    draw.text((36, fy + 24), "Need more assistance?", fill=DEEP_NAVY, font=FONT_HEAD_BOLD)
    draw.text((36, fy + 46), "Reach out to support@maatram.org or contact your\nassigned volunteer mentor.", fill=SECONDARY_TEXT, font=FONT_BODY_SM)
    
    draw_button(draw, 20, 660, W - 40, 48, "Chat with Coordinator", is_primary=True)
    save_screen(img, "06-notifications-settings/help_support.png")

def gen_about_maatram():
    img, draw = create_base_canvas(W, H)
    draw_status_bar(draw, W)
    draw_header_nav(img, draw, "About Maatram", W, show_back=True)
    
    draw_card(draw, 20, 110, W - 40, 580, radius=24)
    
    # Logo
    logo_path = "mobile/assets/images/logo.png"
    if os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        logo_h = 50
        logo_w = int(logo_h * (logo.width / logo.height))
        logo_resized = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
        img.paste(logo_resized, ((W - logo_w) // 2, 130), logo_resized)
        
    draw.text((W//2 - 64, 196), "Together for Tomorrow", fill=PRIMARY_GOLD, font=FONT_HEAD_BOLD)
    draw.line([40, 224, W - 40, 224], fill=WARM_BORDER)
    
    desc = (
        "Maatram Foundation is a non-profit organization\n"
        "committed to empowering underprivileged students\n"
        "through free higher education, mentorship, and\n"
        "skill-building opportunities across Tamil Nadu.\n\n"
        "Over the last decade, Maatram has transformed\n"
        "thousands of lives with the support of partner\n"
        "institutions and dedicated volunteers like you."
    )
    draw.text((40, 240), desc, fill=DEEP_NAVY, font=FONT_BODY_SM)
    
    # Impact Stats
    draw_card(draw, 40, 390, 145, 70, radius=12, fill=LIGHT_GOLD, border=PRIMARY_GOLD)
    draw.text((54, 402), "Students Placed", fill=DEEP_NAVY, font=FONT_CAPTION)
    draw.text((54, 420), "10,000+", fill=PRIMARY_GOLD, font=FONT_TITLE_MD)
    
    draw_card(draw, 195, 390, 145, 70, radius=12, fill=LIGHT_GOLD, border=PRIMARY_GOLD)
    draw.text((209, 402), "Volunteer Hours", fill=DEEP_NAVY, font=FONT_CAPTION)
    draw.text((209, 420), "50,000+", fill=PRIMARY_GOLD, font=FONT_TITLE_MD)
    
    draw.text((40, 480), "Founder & Visionary: Sujit Kumar", fill=DEEP_NAVY, font=FONT_BODY_SM_BOLD)
    draw.text((40, 500), "Website: www.maatramfoundation.com", fill=ACCENT_BLUE, font=FONT_CAPTION)
    
    draw_button(draw, 40, 560, W - 80, 48, "Visit Official Website 🌐", is_primary=False)
    save_screen(img, "06-notifications-settings/about_maatram.png")

def gen_logout_confirmation():
    img, draw = create_base_canvas(W, H)
    draw_status_bar(draw, W)
    draw_header_brand(img, draw, W)
    draw_bottom_nav(draw, W, H, active_index=3)
    
    # Dim background overlay
    dim = Image.new("RGBA", (W, H), (0, 0, 0, 110))
    img.paste(dim, (0, 0), dim)
    
    # Bottom Sheet Dialog
    sheet_h = 320
    draw.rounded_rectangle([0, H - sheet_h, W, H], radius=24, fill=WHITE)
    
    # Pull pill
    draw.rounded_rectangle([W//2 - 20, H - sheet_h + 12, W//2 + 20, H - sheet_h + 16], radius=2, fill=WARM_BORDER)
    
    draw.text((W//2 - 64, H - sheet_h + 40), "Sign Out Confirmation", fill=DEEP_NAVY, font=FONT_TITLE_SM)
    draw.text((40, H - sheet_h + 74), "Are you sure you want to sign out of your\nMaatram volunteer account?", fill=SECONDARY_TEXT, font=FONT_BODY_MD, align="center")
    
    draw_button(draw, 30, H - sheet_h + 140, W - 60, 48, "Sign Out", is_primary=True)
    draw_button(draw, 30, H - sheet_h + 200, W - 60, 48, "Cancel", is_primary=False)
    
    save_screen(img, "06-notifications-settings/logout_confirmation.png")

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

def main():
    print("Generating comprehensive Maatram individual design reference library...")
    
    # 01-authentication
    gen_login()
    gen_forgot_password()
    gen_reset_password()
    
    # 02-registration
    gen_reg_step1()
    gen_reg_step2()
    gen_reg_step3()
    gen_reg_step4()
    gen_reg_step5()
    gen_reg_step6()
    
    # 03-verification
    gen_email_verification()
    gen_pending_verification()
    gen_pending_approval()
    gen_rejected()
    gen_post_approval_welcome()
    
    # 04-main-application
    gen_events_screen()
    gen_event_details()
    gen_event_registration()
    gen_activity_details()
    gen_leaderboard_screen()
    gen_more_screen()
    
    # 05-volunteer-account
    gen_profile()
    gen_edit_profile()
    gen_profile_photo()
    gen_points()
    gen_points_history()
    gen_achievements()
    gen_achievement_details()
    
    # 06-notifications-settings
    gen_notifications()
    gen_notification_details()
    gen_notification_settings()
    gen_privacy_consent()
    gen_settings()
    gen_help_support()
    gen_about_maatram()
    gen_logout_confirmation()
    
    print("\n✓ ALL 38 INDIVIDUAL SCREENS GENERATED SUCCESSFULLY IN docs/design-reference/!")

if __name__ == "__main__":
    main()
