import os
import math
from PIL import Image, ImageDraw, ImageFont

FONTS_DIR = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts')

# Colors
BG_COLOR = (250, 248, 245, 255)       # #FAF8F5
PRIMARY_GOLD = (245, 184, 23, 255)    # #F5B817
DEEP_NAVY = (27, 43, 72, 255)         # #1B2B48
WHITE = (255, 255, 255, 255)          # #FFFFFF
WARM_BORDER = (239, 236, 230, 255)    # #EFECE6
SECONDARY_TEXT = (130, 125, 115, 255) # #827D73
CARD_SHADOW = (0, 0, 0, 12)
SUCCESS_GREEN = (22, 163, 74, 255)    # #16A34A
ACCENT_BLUE = (37, 99, 235, 255)      # #2563EB
ACCENT_PURPLE = (124, 58, 237, 255)   # #7C3AED
ACCENT_AMBER = (217, 119, 6, 255)     # #D97706
LIGHT_GOLD = (254, 243, 199, 255)     # #FEF3C7
LIGHT_GREEN = (220, 252, 231, 255)    # #DCFCE7
LIGHT_BLUE = (219, 234, 254, 255)     # #DBEAFE
LIGHT_RED = (254, 226, 226, 255)      # #FEE2E2
CRITICAL_RED = (220, 38, 38, 255)     # #DC2626

def get_font(name="arial.ttf", size=14):
    path = os.path.join(FONTS_DIR, name)
    if os.path.exists(path):
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()

FONT_TITLE_LG = get_font("georgiab.ttf", 26)
FONT_TITLE_MD = get_font("georgiab.ttf", 20)
FONT_TITLE_SM = get_font("georgiab.ttf", 16)
FONT_HEAD_BOLD = get_font("georgiab.ttf", 14)
FONT_BODY_LG = get_font("arial.ttf", 15)
FONT_BODY_MD = get_font("arial.ttf", 13)
FONT_BODY_BOLD = get_font("arialbd.ttf", 13)
FONT_BODY_SM = get_font("arial.ttf", 11)
FONT_BODY_SM_BOLD = get_font("arialbd.ttf", 11)
FONT_CAPTION = get_font("arial.ttf", 10)
FONT_CAPTION_BOLD = get_font("arialbd.ttf", 10)

def create_base_canvas(width=390, height=844):
    img = Image.new("RGBA", (width, height), BG_COLOR)
    draw = ImageDraw.Draw(img)
    return img, draw

def draw_status_bar(draw, width=390):
    draw.text((32, 14), "9:41", fill=DEEP_NAVY, font=FONT_BODY_SM_BOLD)
    # Signal bars
    for i in range(4):
        h = 4 + i * 2.5
        x = width - 75 + i * 4
        draw.rounded_rectangle([x, 22 - h, x + 2.5, 22], radius=1, fill=DEEP_NAVY)
    # Wifi arc / symbol representation
    draw.arc([width - 55, 12, width - 42, 24], start=210, end=330, fill=DEEP_NAVY, width=2)
    draw.arc([width - 52, 15, width - 45, 24], start=210, end=330, fill=DEEP_NAVY, width=2)
    # Battery icon
    draw.rounded_rectangle([width - 36, 13, width - 16, 23], radius=3, outline=DEEP_NAVY, width=1)
    draw.rectangle([width - 15, 16, width - 14, 20], fill=DEEP_NAVY)
    draw.rounded_rectangle([width - 34, 15, width - 20, 21], radius=2, fill=DEEP_NAVY)

def draw_header_brand(img, draw, width=390):
    # Logo
    logo_path = "mobile/assets/images/logo.png"
    if os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path).convert("RGBA")
            aspect = logo.width / logo.height
            logo_h = 38
            logo_w = int(logo_h * aspect)
            logo_resized = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
            img.paste(logo_resized, (16, 38), logo_resized)
        except Exception:
            draw.text((16, 44), "Maatram", fill=DEEP_NAVY, font=FONT_TITLE_MD)
    else:
        draw.text((16, 44), "Maatram", fill=DEEP_NAVY, font=FONT_TITLE_MD)
    
    # Notification Bell
    bell_x = width - 68
    draw.rounded_rectangle([bell_x, 42, bell_x + 28, 70], radius=14, fill=WHITE, outline=WARM_BORDER)
    # Bell icon representation
    draw.arc([bell_x + 8, 48, bell_x + 20, 60], start=180, end=360, fill=DEEP_NAVY, width=2)
    draw.line([bell_x + 6, 60, bell_x + 22, 60], fill=DEEP_NAVY, width=2)
    draw.ellipse([bell_x + 12, 62, bell_x + 16, 64], fill=DEEP_NAVY)
    # Red badge (3)
    draw.ellipse([bell_x + 18, 40, bell_x + 28, 50], fill=(220, 38, 38, 255))
    draw.text((bell_x + 21, 40), "3", fill=WHITE, font=FONT_CAPTION_BOLD)

    # Avatar
    avatar_x = width - 36
    draw.ellipse([avatar_x, 42, avatar_x + 28, 70], fill=(229, 231, 235, 255), outline=PRIMARY_GOLD, width=2)
    draw.ellipse([avatar_x + 8, 48, avatar_x + 20, 60], fill=(156, 163, 175, 255))
    draw.chord([avatar_x + 3, 56, avatar_x + 25, 75], start=180, end=360, fill=(156, 163, 175, 255))

def draw_header_nav(img, draw, title, width=390, show_back=True, action_text=None):
    if show_back:
        # Back arrow
        draw.line([24, 52, 17, 58], fill=DEEP_NAVY, width=2)
        draw.line([17, 58, 24, 64], fill=DEEP_NAVY, width=2)
    
    draw.text((44 if show_back else 20, 48), title, fill=DEEP_NAVY, font=FONT_TITLE_MD)
    
    if action_text:
        draw.text((width - 80, 52), action_text, fill=PRIMARY_GOLD, font=FONT_BODY_SM_BOLD)

def draw_bottom_nav(draw, width=390, height=844, active_index=0):
    nav_h = 64
    y = height - nav_h - 10
    draw.rectangle([0, y, width, height], fill=WHITE)
    draw.line([0, y, width, y], fill=WARM_BORDER, width=1)
    
    tabs = [
        ("Home", "H"),
        ("Events", "E"),
        ("Leaderboard", "L"),
        ("More", "M")
    ]
    
    tab_w = width / len(tabs)
    for i, (name, icon_c) in enumerate(tabs):
        tx = int(i * tab_w + tab_w / 2)
        is_active = (i == active_index)
        if is_active:
            pill_w = 48
            draw.rounded_rectangle([tx - pill_w//2, y + 6, tx + pill_w//2, y + 32], radius=13, fill=PRIMARY_GOLD)
            draw.text((tx - 5, y + 10), icon_c, fill=DEEP_NAVY, font=FONT_BODY_SM_BOLD)
            draw.text((tx - len(name)*3, y + 36), name, fill=DEEP_NAVY, font=FONT_CAPTION_BOLD)
        else:
            draw.text((tx - 5, y + 12), icon_c, fill=SECONDARY_TEXT, font=FONT_BODY_SM_BOLD)
            draw.text((tx - len(name)*3, y + 36), name, fill=SECONDARY_TEXT, font=FONT_CAPTION)

def draw_card(draw, x, y, w, h, radius=16, fill=WHITE, border=WARM_BORDER, shadow=True):
    # Shadow
    if shadow:
        draw.rounded_rectangle([x, y + 2, x + w, y + h + 2], radius=radius, fill=(0, 0, 0, 8))
    draw.rounded_rectangle([x, y, x + w, y + h], radius=radius, fill=fill, outline=border, width=1)

def draw_button(draw, x, y, w, h, label, is_primary=True, radius=16):
    bg = PRIMARY_GOLD if is_primary else WHITE
    border = PRIMARY_GOLD if is_primary else WARM_BORDER
    fg = DEEP_NAVY if is_primary else DEEP_NAVY
    draw.rounded_rectangle([x, y, x + w, y + h], radius=radius, fill=bg, outline=border, width=1)
    # Center text
    font = FONT_BODY_BOLD
    bbox = draw.textbbox((0, 0), label, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text((x + (w - tw) / 2, y + (h - th) / 2 - 2), label, fill=fg, font=font)

def draw_input(draw, x, y, w, h, label, value="", placeholder="", radius=12, is_password=False):
    draw.text((x, y - 18), label, fill=DEEP_NAVY, font=FONT_BODY_SM_BOLD)
    draw.rounded_rectangle([x, y, x + w, y + h], radius=radius, fill=WHITE, outline=WARM_BORDER, width=1)
    display_text = ("••••••••" if is_password and value else (value if value else placeholder))
    text_color = DEEP_NAVY if value else SECONDARY_TEXT
    draw.text((x + 14, y + (h - 14) / 2), display_text, fill=text_color, font=FONT_BODY_MD)

def draw_pill(draw, x, y, label, bg=LIGHT_GOLD, fg=DEEP_NAVY, radius=12):
    font = FONT_CAPTION_BOLD
    bbox = draw.textbbox((0, 0), label, font=font)
    tw = bbox[2] - bbox[0]
    w = tw + 18
    h = 24
    draw.rounded_rectangle([x, y, x + w, y + h], radius=radius, fill=bg)
    draw.text((x + 9, y + 4), label, fill=fg, font=font)
    return w
