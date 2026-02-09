"""
UI Theme Configuration for Horsepower Gym Management System
Gray-based theme inspired by gym interior with gold accents
Applied to all post-login views (Dashboard, Members, Training, Attendance)
"""

# ============================================================
# GRAY THEME COLORS (Post-Login Views)
# ============================================================

# Background colors
BG_PRIMARY = "#6B6F73"        # Main app background (professional gym gray)
BG_SECONDARY = "#5A5E62"      # Cards, panels, sidebar (darker gray)
BG_TERTIARY = "#4A4E52"       # Darker elements, headers, inputs
BG_HOVER = "#7B7F83"          # Hover state background

# Accent colors
ACCENT_GOLD = "#FFD700"       # Primary brand accent
ACCENT_GOLD_HOVER = "#FFC000" # Gold hover state
ACCENT_GOLD_DARK = "#D4AF00"  # Darker gold

# Text colors
TEXT_PRIMARY = "#FFFFFF"      # Main text
TEXT_SECONDARY = "#E0E0E0"    # Secondary text
TEXT_MUTED = "#C0C0C0"        # Labels, hints
TEXT_DARK = "#000000"         # Text on gold buttons

# Status colors
SUCCESS = "#2ECC71"           # Active, paid, success
SUCCESS_DARK = "#27AE60"
ERROR = "#E74C3C"             # Expired, error, danger
ERROR_DARK = "#C0392B"
WARNING = "#F39C12"           # Warning, pending
WARNING_DARK = "#D68910"
INFO = "#3498DB"              # Info, links
INFO_DARK = "#2980B9"
PURPLE = "#9B59B6"            # Photo capture, special actions
PURPLE_DARK = "#8E44AD"

# Border colors
BORDER_COLOR = "#6B7075"      # Default border
BORDER_LIGHT = "#8A8D91"      # Light border
BORDER_GOLD = "#FFD700"       # Gold accent border

# ============================================================
# COMPONENT STYLES
# ============================================================

# Corner radius
RADIUS_SM = 8
RADIUS_MD = 10
RADIUS_LG = 14

# Padding values
PAD_XS = 5
PAD_SM = 8
PAD_MD = 12
PAD_LG = 16
PAD_XL = 20

# Font sizes
FONT_HEADING_XL = 28
FONT_HEADING_LG = 24
FONT_HEADING_MD = 20
FONT_HEADING_SM = 16
FONT_BODY = 14
FONT_SMALL = 12
FONT_TINY = 11

# ============================================================
# BUTTON STYLES
# ============================================================

BTN_PRIMARY = {
    "fg_color": ACCENT_GOLD,
    "hover_color": ACCENT_GOLD_HOVER,
    "text_color": TEXT_DARK,
    "corner_radius": RADIUS_SM
}

BTN_SECONDARY = {
    "fg_color": BG_TERTIARY,
    "hover_color": BG_HOVER,
    "text_color": TEXT_PRIMARY,
    "corner_radius": RADIUS_SM
}

BTN_SUCCESS = {
    "fg_color": SUCCESS,
    "hover_color": SUCCESS_DARK,
    "text_color": TEXT_PRIMARY,
    "corner_radius": RADIUS_SM
}

BTN_DANGER = {
    "fg_color": ERROR,
    "hover_color": ERROR_DARK,
    "text_color": TEXT_PRIMARY,
    "corner_radius": RADIUS_SM
}

BTN_INFO = {
    "fg_color": INFO,
    "hover_color": INFO_DARK,
    "text_color": TEXT_PRIMARY,
    "corner_radius": RADIUS_SM
}

# ============================================================
# INPUT STYLES
# ============================================================

INPUT_STYLE = {
    "fg_color": BG_TERTIARY,
    "border_color": BORDER_COLOR,
    "border_width": 1,
    "corner_radius": RADIUS_SM,
    "text_color": TEXT_PRIMARY
}

COMBOBOX_STYLE = {
    "fg_color": BG_TERTIARY,
    "border_color": BORDER_COLOR,
    "border_width": 1,
    "button_color": ACCENT_GOLD,
    "button_hover_color": ACCENT_GOLD_HOVER,
    "dropdown_fg_color": BG_TERTIARY,
    "corner_radius": RADIUS_SM
}

# ============================================================
# TABLE/LIST STYLES
# ============================================================

TABLE_HEADER_BG = BG_TERTIARY
TABLE_ROW_ODD = BG_SECONDARY
TABLE_ROW_EVEN = "#424649"
TABLE_ROW_EXPIRED = "#5C3030"  # Dark red tint for expired
TABLE_ROW_HOVER = BG_HOVER
