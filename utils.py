"""
Utility functions for Horsepower Gym Management System
"""

from datetime import datetime, date, timedelta
import os
import sys


def get_resource_path(relative_path):
    """
    Get absolute path to BUNDLED resources (read-only), works for dev and PyInstaller.
    PyInstaller extracts bundled files to _MEIPASS temp folder.
    Use this for assets that are bundled WITH the app and don't change.
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


def get_app_directory():
    """
    Get the directory where the application EXE or main.py is located.
    This is for PERSISTENT data (database, photos) that must survive restarts.
    
    PyInstaller bundles files to a temp _MEIPASS folder that gets deleted.
    User data must be stored in the same folder as the .exe, not _MEIPASS.
    """
    if getattr(sys, 'frozen', False):
        # Running as compiled .exe - use the folder containing the .exe
        return os.path.dirname(sys.executable)
    else:
        # Running as script - use the script directory
        return os.path.dirname(os.path.abspath(__file__))


def get_data_path(relative_path=""):
    """
    Get path to user data directory (PERSISTENT - survives app restarts).
    For photos and database that must survive PyInstaller builds.
    
    IMPORTANT: This returns paths in the .exe folder, NOT the _MEIPASS temp folder.
    """
    base_path = get_app_directory()
    if relative_path:
        return os.path.join(base_path, relative_path)
    return base_path


def get_member_photos_dir():
    """Get the member photos directory, creating it if it doesn't exist."""
    photos_dir = os.path.join(get_app_directory(), "assets", "member_photos")
    if not os.path.exists(photos_dir):
        os.makedirs(photos_dir, exist_ok=True)
    return photos_dir


def get_member_photo_path(phone):
    """Get the full path for a member's photo based on phone number."""
    photos_dir = get_member_photos_dir()
    # Clean phone number for filename
    clean_phone = phone.strip().replace(" ", "").replace("-", "")
    return os.path.join(photos_dir, f"member_{clean_phone}.jpg")


def calculate_end_date(start_date, membership_type):
    """Calculate membership end date based on type"""
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    
    if membership_type == "Monthly":
        end_date = start_date + timedelta(days=30)
    elif membership_type == "Quarterly":
        end_date = start_date + timedelta(days=90)
    elif membership_type == "Yearly":
        end_date = start_date + timedelta(days=365)
    else:
        end_date = start_date + timedelta(days=30)
    
    return end_date.strftime('%Y-%m-%d')


def calculate_training_end_date(start_date, duration_months):
    """Calculate personal training end date"""
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    
    end_date = start_date + timedelta(days=duration_months * 30)
    return end_date.strftime('%Y-%m-%d')


def get_remaining_days(end_date):
    """Get remaining days until expiry"""
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    today = date.today()
    remaining = (end_date - today).days
    return max(0, remaining)


def is_membership_valid(end_date):
    """Check if membership is still valid"""
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    return end_date >= date.today()


def format_date(date_str):
    """Format date string for display"""
    if not date_str:
        return ""
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        return dt.strftime('%d-%b-%Y')
    except:
        return date_str


def format_currency(amount):
    """Format amount as currency"""
    try:
        return f"₹{float(amount):,.2f}"
    except:
        return f"₹{amount}"


def get_membership_fee(membership_type):
    """Get default fee based on membership type"""
    fees = {
        "Monthly": 1200,
        "Quarterly": 3200,
        "Yearly": 12000
    }
    return fees.get(membership_type, 1200)


# Fee Map - Official pricing
FEE_MAP = {
    "Monthly": 1200,
    "Quarterly": 3200,
    "Yearly": 12000
}

# Membership duration in days
MEMBERSHIP_DURATION = {
    "Monthly": 30,
    "Quarterly": 90,
    "Yearly": 365
}


def calculate_pending_fee(membership_type, amount_paid):
    """Calculate pending fee for a member"""
    total_fee = FEE_MAP.get(membership_type, 1200)
    pending = max(0, total_fee - amount_paid)
    return pending


def get_membership_status(end_date):
    """Get membership status (Active/Expired) based on end date"""
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    if end_date >= date.today():
        return "Active"
    else:
        return "Expired"


def calculate_new_end_date(current_end_date, membership_type):
    """Calculate new end date after payment (extends from current end or today)"""
    if isinstance(current_end_date, str):
        current_end_date = datetime.strptime(current_end_date, '%Y-%m-%d').date()
    
    today = date.today()
    # If membership is expired, start from today; otherwise extend from end date
    start_from = max(current_end_date, today)
    
    days = MEMBERSHIP_DURATION.get(membership_type, 30)
    new_end = start_from + timedelta(days=days)
    return new_end.strftime('%Y-%m-%d')


def validate_phone(phone):
    """Validate phone number"""
    phone = phone.strip().replace(" ", "").replace("-", "")
    return len(phone) >= 10 and phone.isdigit()


def validate_age(age):
    """Validate age"""
    try:
        age = int(age)
        return 10 <= age <= 100
    except:
        return False


TRAINERS = ["Suriya", "Ganesh"]
MEMBERSHIP_TYPES = ["Monthly", "Quarterly", "Yearly"]
PAYMENT_STATUS = ["Paid", "Pending"]
PAYMENT_TYPES = ["Membership", "PT", "Renewal"]
GENDERS = ["Male", "Female", "Other"]

GYM_INFO = {
    "name": "Horsepower Gym",
    "location": "Koodapakkam Road, near Lakshmi Narayana Medical College, Pondicherry",
    "owner": "Manikandan",
    "trainers": TRAINERS
}


# ============ IMAGE UTILITIES ============

def resize_image_pil(pil_image, target_size=(200, 200)):
    """
    Resize PIL image maintaining aspect ratio.
    Returns a PIL Image object.
    """
    from PIL import Image
    
    # Get original size
    original_width, original_height = pil_image.size
    target_width, target_height = target_size
    
    # Calculate aspect ratios
    ratio = min(target_width / original_width, target_height / original_height)
    new_width = int(original_width * ratio)
    new_height = int(original_height * ratio)
    
    # Resize with high quality
    resized = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # Create a new image with target size and paste resized image centered
    new_image = Image.new("RGB", target_size, (45, 45, 45))  # Dark gray background
    paste_x = (target_width - new_width) // 2
    paste_y = (target_height - new_height) // 2
    new_image.paste(resized, (paste_x, paste_y))
    
    return new_image


def create_badge_overlay(pil_image, pending_amount, badge_position="bottom"):
    """
    Overlay a PROMINENT payment status indicator on a PIL image.
    
    VISUAL RULES:
    - If pending_amount > 0: 
      * Apply semi-transparent DARK overlay
      * Show ORANGE/RED "FEE PENDING" badge
    - If pending_amount == 0:
      * NO dark overlay (normal photo)
      * Show GREEN "PAID" badge
    
    Args:
        pil_image: PIL Image object
        pending_amount: Amount pending (0 = paid, >0 = pending)
        badge_position: 'top', 'bottom', 'top-right', 'bottom-right'
    
    Returns:
        PIL Image with status overlay
    """
    from PIL import Image, ImageDraw, ImageFont, ImageEnhance
    
    # Make a copy to avoid modifying original
    img = pil_image.copy().convert("RGBA")
    img_width, img_height = img.size
    
    if pending_amount > 0:
        # ========== PENDING STATUS ==========
        # Apply semi-transparent dark overlay
        dark_overlay = Image.new("RGBA", (img_width, img_height), (0, 0, 0, 120))  # 47% opacity black
        img = Image.alpha_composite(img, dark_overlay)
        
        # Badge configuration for PENDING
        badge_bg_color = (231, 76, 60, 240)  # Red with slight transparency
        badge_border_color = (255, 255, 255, 255)
        badge_text = "FEE PENDING"
        text_color = (255, 255, 255, 255)
        icon_text = "⚠"
        
    else:
        # ========== PAID STATUS ==========
        # No dark overlay - keep photo bright
        
        # Badge configuration for PAID
        badge_bg_color = (46, 204, 113, 240)  # Green with slight transparency
        badge_border_color = (255, 255, 255, 255)
        badge_text = "PAID ✓"
        text_color = (255, 255, 255, 255)
        icon_text = None
    
    # Create drawing context
    draw = ImageDraw.Draw(img)
    
    # Calculate badge dimensions
    badge_height = max(36, img_height // 5)
    badge_padding = 8
    corner_radius = badge_height // 3
    
    # Calculate badge position (full width banner at bottom)
    if badge_position in ["bottom", "bottom-right"]:
        badge_y = img_height - badge_height - 8
    else:
        badge_y = 8
    
    badge_x = 8
    badge_width = img_width - 16
    
    # Draw rounded rectangle badge background
    _draw_rounded_rectangle(
        draw,
        (badge_x, badge_y, badge_x + badge_width, badge_y + badge_height),
        corner_radius,
        fill=badge_bg_color,
        outline=badge_border_color,
        width=2
    )
    
    # Load font
    try:
        font_size = max(14, badge_height // 2)
        font = ImageFont.truetype("arial.ttf", font_size)
        font_bold = ImageFont.truetype("arialbd.ttf", font_size)
    except:
        font = ImageFont.load_default()
        font_bold = font
    
    # Calculate text position (centered in badge)
    text_bbox = draw.textbbox((0, 0), badge_text, font=font_bold)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    text_x = badge_x + (badge_width - text_width) // 2
    text_y = badge_y + (badge_height - text_height) // 2 - 2
    
    # Draw text
    draw.text((text_x, text_y), badge_text, fill=text_color, font=font_bold)
    
    # For pending: add warning triangles on sides
    if pending_amount > 0:
        # Draw warning indicators on left and right
        warn_size = badge_height - 12
        _draw_warning_triangle(draw, badge_x + 10, badge_y + 6, warn_size)
        _draw_warning_triangle(draw, badge_x + badge_width - warn_size - 10, badge_y + 6, warn_size)
    
    # Convert back to RGB
    img = img.convert("RGB")
    
    return img


def _draw_rounded_rectangle(draw, coords, radius, fill=None, outline=None, width=1):
    """Draw a rounded rectangle on a PIL ImageDraw object."""
    x1, y1, x2, y2 = coords
    
    # Draw the main rectangle body
    draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
    draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)
    
    # Draw the four corners
    draw.pieslice([x1, y1, x1 + 2*radius, y1 + 2*radius], 180, 270, fill=fill)
    draw.pieslice([x2 - 2*radius, y1, x2, y1 + 2*radius], 270, 360, fill=fill)
    draw.pieslice([x1, y2 - 2*radius, x1 + 2*radius, y2], 90, 180, fill=fill)
    draw.pieslice([x2 - 2*radius, y2 - 2*radius, x2, y2], 0, 90, fill=fill)
    
    # Draw outline if specified
    if outline:
        draw.arc([x1, y1, x1 + 2*radius, y1 + 2*radius], 180, 270, fill=outline, width=width)
        draw.arc([x2 - 2*radius, y1, x2, y1 + 2*radius], 270, 360, fill=outline, width=width)
        draw.arc([x1, y2 - 2*radius, x1 + 2*radius, y2], 90, 180, fill=outline, width=width)
        draw.arc([x2 - 2*radius, y2 - 2*radius, x2, y2], 0, 90, fill=outline, width=width)
        draw.line([x1 + radius, y1, x2 - radius, y1], fill=outline, width=width)
        draw.line([x1 + radius, y2, x2 - radius, y2], fill=outline, width=width)
        draw.line([x1, y1 + radius, x1, y2 - radius], fill=outline, width=width)
        draw.line([x2, y1 + radius, x2, y2 - radius], fill=outline, width=width)


def _draw_warning_triangle(draw, x, y, size):
    """Draw a warning triangle icon."""
    # Yellow/orange warning triangle
    triangle_color = (241, 196, 15, 255)  # Yellow
    outline_color = (243, 156, 18, 255)  # Orange outline
    
    # Triangle points (pointing up)
    points = [
        (x + size // 2, y),           # Top
        (x, y + size),                 # Bottom left
        (x + size, y + size)           # Bottom right
    ]
    
    draw.polygon(points, fill=triangle_color, outline=outline_color)
    
    # Draw exclamation mark inside
    exc_x = x + size // 2
    exc_top = y + size // 4
    exc_bottom = y + size * 3 // 4
    
    draw.line([(exc_x, exc_top), (exc_x, exc_bottom - 4)], fill=(0, 0, 0, 255), width=2)
    draw.ellipse([exc_x - 2, exc_bottom - 2, exc_x + 2, exc_bottom + 2], fill=(0, 0, 0, 255))


def create_mini_badge_overlay(pil_image, pending_amount):
    """
    Create a small payment status badge overlay for thumbnail images.
    Used in the members list to show PENDING/PAID status at a glance.
    
    Args:
        pil_image: PIL Image object (small thumbnail, e.g., 40x40)
        pending_amount: Amount pending (0 = paid, >0 = pending)
    
    Returns:
        PIL Image with mini status badge in top-right corner
    """
    from PIL import Image, ImageDraw
    
    # Make a copy to avoid modifying original
    img = pil_image.copy().convert("RGBA")
    img_width, img_height = img.size
    
    # Badge size - proportional to image (for 40x40 image, badge is about 14x14)
    badge_size = max(12, img_width // 3)
    badge_padding = 2
    
    # Badge position: top-right corner
    badge_x = img_width - badge_size - badge_padding
    badge_y = badge_padding
    
    # Create badge
    draw = ImageDraw.Draw(img)
    
    if pending_amount > 0:
        # PENDING - Orange/Red circle with exclamation
        badge_color = (231, 76, 60, 255)  # Red
        draw.ellipse(
            [badge_x, badge_y, badge_x + badge_size, badge_y + badge_size],
            fill=badge_color,
            outline=(255, 255, 255, 255),
            width=1
        )
        # Draw exclamation mark
        exc_x = badge_x + badge_size // 2
        exc_top = badge_y + badge_size // 4
        exc_bottom = badge_y + badge_size * 3 // 4
        draw.line([(exc_x, exc_top), (exc_x, exc_bottom - 2)], fill=(255, 255, 255, 255), width=2)
        draw.ellipse([exc_x - 1, exc_bottom, exc_x + 1, exc_bottom + 2], fill=(255, 255, 255, 255))
    else:
        # PAID - Green circle with checkmark
        badge_color = (46, 204, 113, 255)  # Green
        draw.ellipse(
            [badge_x, badge_y, badge_x + badge_size, badge_y + badge_size],
            fill=badge_color,
            outline=(255, 255, 255, 255),
            width=1
        )
        # Draw checkmark
        check_start_x = badge_x + badge_size // 4
        check_mid_x = badge_x + badge_size * 2 // 5
        check_end_x = badge_x + badge_size * 3 // 4
        check_y1 = badge_y + badge_size // 2
        check_y2 = badge_y + badge_size * 2 // 3
        check_y3 = badge_y + badge_size // 3
        
        draw.line([(check_start_x, check_y1), (check_mid_x, check_y2)], fill=(255, 255, 255, 255), width=2)
        draw.line([(check_mid_x, check_y2), (check_end_x, check_y3)], fill=(255, 255, 255, 255), width=2)
    
    # Convert back to RGB
    img = img.convert("RGB")
    return img


def create_default_avatar(size=(200, 200), pending_amount=None):
    """
    Create a default avatar image when no photo is available.
    Optionally applies payment status badge.
    
    Args:
        size: Tuple of (width, height)
        pending_amount: If provided, applies badge overlay
    
    Returns:
        PIL Image object.
    """
    from PIL import Image, ImageDraw, ImageFont
    
    # Create image with dark gray background
    img = Image.new("RGB", size, (60, 60, 60))
    draw = ImageDraw.Draw(img)
    
    # Draw a circle for avatar background
    center_x, center_y = size[0] // 2, size[1] // 2
    radius = min(size) // 2 - 10
    draw.ellipse(
        [center_x - radius, center_y - radius,
         center_x + radius, center_y + radius],
        fill=(80, 80, 80),
        outline=(100, 100, 100),
        width=2
    )
    
    # Draw person icon (simplified)
    icon_color = (150, 150, 150)
    
    # Head
    head_radius = radius // 3
    draw.ellipse(
        [center_x - head_radius, center_y - radius // 2 - head_radius,
         center_x + head_radius, center_y - radius // 2 + head_radius],
        fill=icon_color
    )
    
    # Body (semicircle at bottom)
    body_top = center_y - radius // 2 + head_radius + 5
    body_radius = radius // 2
    draw.ellipse(
        [center_x - body_radius, body_top,
         center_x + body_radius, body_top + body_radius * 2],
        fill=icon_color
    )
    
    # Apply badge if pending_amount is provided
    if pending_amount is not None:
        img = create_badge_overlay(img, pending_amount)
    
    return img


def save_member_photo(pil_image, phone, resize=True):
    """
    Save a member's photo to disk.
    
    Args:
        pil_image: PIL Image object (captured from webcam or file)
        phone: Member's phone number (used for filename)
        resize: Whether to resize the image
    
    Returns:
        Saved file path (relative to app directory)
    """
    from PIL import Image
    
    # Resize if requested
    if resize:
        pil_image = resize_image_pil(pil_image, (200, 200))
    
    # Get save path
    full_path = get_member_photo_path(phone)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    
    # Save with good quality
    pil_image.save(full_path, "JPEG", quality=90)
    
    # Return relative path for database storage
    clean_phone = phone.strip().replace(" ", "").replace("-", "")
    return f"assets/member_photos/member_{clean_phone}.jpg"


def load_member_photo_with_badge(photo_path, pending_amount, size=(200, 200)):
    """
    Load a member's photo and apply payment badge.
    
    Args:
        photo_path: Relative path to photo (from database)
        pending_amount: Amount pending (0 = paid, >0 = pending)
        size: Target display size
    
    Returns:
        PIL Image with badge overlay, or default avatar if photo not found
    """
    from PIL import Image
    
    try:
        if photo_path:
            # Build full path
            full_path = os.path.join(get_data_path(), photo_path)
            if os.path.exists(full_path):
                img = Image.open(full_path)
                img = resize_image_pil(img, size)
            else:
                img = create_default_avatar(size)
        else:
            img = create_default_avatar(size)
    except Exception:
        img = create_default_avatar(size)
    
    # Apply badge overlay
    img = create_badge_overlay(img, pending_amount)
    
    return img
