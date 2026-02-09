"""
Payment View for Horsepower Gym Management System
Phone Number Fee Verification & Payment Display
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime, date
import sys
import os
from PIL import Image, ImageDraw

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import database as db
from utils import (
    format_date, format_currency, get_remaining_days, is_membership_valid,
    validate_phone, FEE_MAP, calculate_pending_fee, get_membership_status,
    calculate_new_end_date, MEMBERSHIP_TYPES, PAYMENT_TYPES,
    load_member_photo_with_badge, create_default_avatar, get_data_path
)


def create_status_pil_image(status="paid", size=48):
    """
    Create payment status PIL Image (PyInstaller-safe, no external files)
    
    Args:
        status: "paid" for green check, "pending" for orange/red warning, "expired" for red X
        size: Icon size in pixels
    
    Returns:
        PIL Image object (RGBA)
    """
    # Create transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Circle padding
    padding = 4
    circle_bbox = [padding, padding, size - padding, size - padding]
    
    if status == "paid":
        # Green circle with white checkmark
        draw.ellipse(circle_bbox, fill=(46, 204, 113, 255))  # #2ecc71
        
        # Draw checkmark
        check_color = (255, 255, 255, 255)
        line_width = max(3, size // 12)
        
        # Checkmark points (scaled to size)
        x1 = size * 0.25
        y1 = size * 0.50
        x2 = size * 0.42
        y2 = size * 0.68
        x3 = size * 0.75
        y3 = size * 0.32
        
        draw.line([(x1, y1), (x2, y2)], fill=check_color, width=line_width)
        draw.line([(x2, y2), (x3, y3)], fill=check_color, width=line_width)
        
    elif status == "pending":
        # Orange circle with exclamation mark
        draw.ellipse(circle_bbox, fill=(243, 156, 18, 255))  # #f39c12 (Orange)
        
        # Draw exclamation mark
        mark_color = (255, 255, 255, 255)
        center_x = size // 2
        
        # Exclamation line
        line_top = size * 0.22
        line_bottom = size * 0.58
        line_width = max(4, size // 10)
        draw.line([(center_x, line_top), (center_x, line_bottom)], 
                  fill=mark_color, width=line_width)
        
        # Exclamation dot
        dot_y = size * 0.72
        dot_radius = max(3, size // 14)
        draw.ellipse([center_x - dot_radius, dot_y - dot_radius,
                      center_x + dot_radius, dot_y + dot_radius], 
                     fill=mark_color)
        
    elif status == "expired":
        # Red circle with X mark
        draw.ellipse(circle_bbox, fill=(231, 76, 60, 255))  # #e74c3c (Red)
        
        # Draw X mark
        x_color = (255, 255, 255, 255)
        line_width = max(3, size // 12)
        margin = size * 0.28
        
        draw.line([(margin, margin), (size - margin, size - margin)], 
                  fill=x_color, width=line_width)
        draw.line([(size - margin, margin), (margin, size - margin)], 
                  fill=x_color, width=line_width)
    
    return img


class PaymentView(ctk.CTkFrame):
    """Payment Screen with Phone Verification"""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.verified_member = None
        
        # === CRITICAL: Store PIL images to prevent garbage collection ===
        # PIL images MUST be stored as instance variables
        self._pil_images = {
            "paid": create_status_pil_image("paid", 40),
            "pending": create_status_pil_image("pending", 40),
            "expired": create_status_pil_image("expired", 40),
            "paid_large": create_status_pil_image("paid", 56),
            "pending_large": create_status_pil_image("pending", 56),
            "expired_large": create_status_pil_image("expired", 56),
        }
        
        # Create CTkImage objects from PIL images (also stored as instance vars)
        self._status_icons = {
            key: ctk.CTkImage(
                light_image=pil_img, 
                dark_image=pil_img, 
                size=(pil_img.width, pil_img.height)
            )
            for key, pil_img in self._pil_images.items()
        }
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main container with two panels
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_columnconfigure(1, weight=2)
        main_container.grid_rowconfigure(0, weight=1)
        
        # Left Panel - Phone Verification & Payment
        self.create_verification_panel(main_container)
        
        # Right Panel - Payment History
        self.create_history_panel(main_container)
        
    def create_verification_panel(self, parent):
        """Create the phone verification and payment panel with scrollable content"""
        # Outer container frame (non-scrollable, holds the structure)
        verify_frame = ctk.CTkFrame(parent, fg_color="#1a1a1a", corner_radius=10)
        verify_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Header (fixed at top, outside scroll area)
        header_container = ctk.CTkFrame(verify_frame, fg_color="transparent")
        header_container.pack(fill="x", padx=0, pady=0)
        
        ctk.CTkLabel(
            header_container,
            text="💳 Fee Verification & Payment",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#FFD700"
        ).pack(anchor="w", padx=20, pady=(20, 10))
        
        # Phone Input Section (fixed at top, outside scroll area for quick access)
        phone_frame = ctk.CTkFrame(header_container, fg_color="#2d2d2d", corner_radius=8)
        phone_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        ctk.CTkLabel(
            phone_frame,
            text="📱 Enter Phone Number",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#ffffff"
        ).pack(anchor="w", padx=15, pady=(15, 5))
        
        input_row = ctk.CTkFrame(phone_frame, fg_color="transparent")
        input_row.pack(fill="x", padx=15, pady=(0, 15))
        
        self.phone_var = ctk.StringVar()
        self.phone_entry = ctk.CTkEntry(
            input_row,
            textvariable=self.phone_var,
            placeholder_text="Enter 10-digit phone number...",
            height=45,
            font=ctk.CTkFont(size=16),
            fg_color="#3d3d3d",
            border_color="#444444"
        )
        self.phone_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.phone_entry.bind("<Return>", lambda e: self.verify_phone())
        
        ctk.CTkButton(
            input_row,
            text="🔍 Check",
            command=self.verify_phone,
            fg_color="#FFD700",
            text_color="#000000",
            hover_color="#FFC000",
            height=45,
            width=100,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="right")
        
        # SCROLLABLE CONTENT AREA - This is the key fix
        # Contains: Member Details + Payment Section
        self.scroll_container = ctk.CTkScrollableFrame(
            verify_frame, 
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color="#444444",
            scrollbar_button_hover_color="#666666"
        )
        self.scroll_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Member Details Display (inside scrollable area)
        self.details_frame = ctk.CTkFrame(self.scroll_container, fg_color="#2d2d2d", corner_radius=8)
        self.details_frame.pack(fill="x", padx=10, pady=5)
        
        self.show_empty_state()
        
        # Payment Section (inside scrollable area - always visible when scrolled)
        self.payment_section = ctk.CTkFrame(self.scroll_container, fg_color="#2d2d2d", corner_radius=8)
        self.payment_section.pack(fill="x", padx=10, pady=(5, 10))
        self.payment_section.pack_forget()  # Hide initially
        
    def show_empty_state(self):
        """Show empty state before verification"""
        for widget in self.details_frame.winfo_children():
            widget.destroy()
        
        # Center content in details frame
        content = ctk.CTkFrame(self.details_frame, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=10, pady=20)
            
        ctk.CTkLabel(
            content,
            text="📲",
            font=ctk.CTkFont(size=50)
        ).pack(pady=(30, 10))
        
        ctk.CTkLabel(
            content,
            text="Enter phone number to verify member",
            font=ctk.CTkFont(size=14),
            text_color="#888888"
        ).pack(pady=(0, 30))
        
    def verify_phone(self):
        """Verify phone number and fetch member details"""
        phone = self.phone_var.get().strip().replace(" ", "").replace("-", "")
        
        if not validate_phone(phone):
            messagebox.showerror("Invalid Phone", "Please enter a valid 10-digit phone number")
            return
        
        # Fetch member by phone
        member = db.get_member_fee_details(phone)
        
        if not member:
            self.show_not_found()
            return
        
        self.verified_member = member
        self.display_member_details(member)
        
    def show_not_found(self):
        """Show member not found state"""
        for widget in self.details_frame.winfo_children():
            widget.destroy()
        
        self.payment_section.pack_forget()
        self.verified_member = None
        
        # Center content in details frame
        content = ctk.CTkFrame(self.details_frame, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=10, pady=20)
        
        ctk.CTkLabel(
            content,
            text="❌",
            font=ctk.CTkFont(size=50)
        ).pack(pady=(20, 10))
        
        ctk.CTkLabel(
            content,
            text="Member Not Found!",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#e74c3c"
        ).pack()
        
        ctk.CTkLabel(
            content,
            text="No member registered with this phone number.\nPlease check the number or register as new member.",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        ).pack(pady=(5, 20))
        
    def display_member_details(self, member):
        """Display verified member details with prominent photo status"""
        for widget in self.details_frame.winfo_children():
            widget.destroy()
        
        # Content container (no nested scroll - parent scroll_container handles it)
        content = ctk.CTkFrame(self.details_frame, fg_color="transparent")
        content.pack(fill="x", expand=True, padx=10, pady=10)
        
        # ========== MEMBER PHOTO WITH PAYMENT STATUS ==========
        # This is the PRIMARY visual indicator of payment status
        amount_paid = member['amount_paid'] or 0
        total_fee = FEE_MAP.get(member['membership_type'], 0)
        pending_fee = calculate_pending_fee(member['membership_type'], amount_paid)
        
        photo_frame = ctk.CTkFrame(content, fg_color="#2d2d2d", corner_radius=10)
        photo_frame.pack(fill="x", pady=(0, 10))
        
        # Center the photo container
        photo_container = ctk.CTkFrame(photo_frame, fg_color="transparent")
        photo_container.pack(pady=15)
        
        # Get member photo path
        photo_path = member['photo_path'] if 'photo_path' in member.keys() else None
        
        # Load photo with status badge overlay
        # This applies:
        # - Dark overlay + "FEE PENDING" badge if pending_fee > 0
        # - Clean photo + "PAID ✓" badge if pending_fee == 0
        self._member_photo_pil = load_member_photo_with_badge(photo_path, pending_fee, (180, 180))
        self._member_photo_ctk = ctk.CTkImage(
            light_image=self._member_photo_pil,
            dark_image=self._member_photo_pil,
            size=(180, 180)
        )
        
        self._photo_label = ctk.CTkLabel(
            photo_container,
            image=self._member_photo_ctk,
            text=""
        )
        self._photo_label.pack()
        
        # Member name under photo
        ctk.CTkLabel(
            photo_container,
            text=member['name'],
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#ffffff"
        ).pack(pady=(10, 2))
        
        ctk.CTkLabel(
            photo_container,
            text=f"📞 {member['phone']}",
            font=ctk.CTkFont(size=13),
            text_color="#aaaaaa"
        ).pack()
        
        # ========== END PHOTO SECTION ==========
        
        # Member Info Header (compact)
        header = ctk.CTkFrame(content, fg_color="#3d3d3d", corner_radius=8)
        header.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            header,
            text="✓ Member Verified",
            font=ctk.CTkFont(size=12),
            text_color="#2ecc71"
        ).pack(anchor="w", padx=15, pady=10)
        
        # Membership Status Card
        status = get_membership_status(member['end_date'])
        is_expired = status == "Expired"
        remaining = get_remaining_days(member['end_date'])
        
        status_frame = ctk.CTkFrame(content, fg_color="#4a1a1a" if is_expired else "#1a3d1a", corner_radius=8)
        status_frame.pack(fill="x", pady=5)
        
        status_color = "#e74c3c" if is_expired else "#FFD700"
        status_text = "⚠️ EXPIRED" if is_expired else f"✓ ACTIVE ({remaining} days left)"
        
        ctk.CTkLabel(
            status_frame,
            text="Membership Status",
            font=ctk.CTkFont(size=11),
            text_color="#aaaaaa"
        ).pack(anchor="w", padx=15, pady=(10, 0))
        
        ctk.CTkLabel(
            status_frame,
            text=status_text,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=status_color
        ).pack(anchor="w", padx=15, pady=(0, 10))
        
        # Membership Details
        details_grid = ctk.CTkFrame(content, fg_color="#3d3d3d", corner_radius=8)
        details_grid.pack(fill="x", pady=5)
        
        details = [
            ("Membership Type", member['membership_type'], "#FFD700"),
            ("Start Date", format_date(member['start_date']), "#ffffff"),
            ("End Date", format_date(member['end_date']), "#e74c3c" if is_expired else "#2ecc71"),
            ("Total Fee", format_currency(FEE_MAP.get(member['membership_type'], 0)), "#ffffff"),
        ]
        
        for label, value, color in details:
            row = ctk.CTkFrame(details_grid, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=3)
            
            ctk.CTkLabel(
                row,
                text=label,
                font=ctk.CTkFont(size=12),
                text_color="#888888",
                width=120,
                anchor="w"
            ).pack(side="left")
            
            ctk.CTkLabel(
                row,
                text=value,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=color
            ).pack(side="right")
        
        # Payment Info with Status Indicator
        payment_frame = ctk.CTkFrame(content, fg_color="#3d3d3d", corner_radius=8)
        payment_frame.pack(fill="x", pady=5)
        
        amount_paid = member['amount_paid'] or 0
        total_fee = FEE_MAP.get(member['membership_type'], 0)
        pending_fee = calculate_pending_fee(member['membership_type'], amount_paid)
        
        # Payment header with status icon
        payment_header = ctk.CTkFrame(payment_frame, fg_color="transparent")
        payment_header.pack(fill="x", padx=15, pady=(10, 5))
        
        ctk.CTkLabel(
            payment_header,
            text="💰 Payment Details",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#ffffff"
        ).pack(side="left")
        
        # === PAYMENT STATUS INDICATOR (IMAGE) ===
        # Determine which icon to show based on payment status
        if is_expired:
            status_icon_key = "expired"
            status_tooltip = "Membership Expired"
        elif pending_fee > 0:
            status_icon_key = "pending"
            status_tooltip = "Pending Fee"
        else:
            status_icon_key = "paid"
            status_tooltip = "Fully Paid"
        
        # Status indicator container (right side of header)
        status_indicator = ctk.CTkFrame(payment_header, fg_color="transparent")
        status_indicator.pack(side="right")
        
        # Status icon image label - MUST store reference to prevent GC
        self._current_status_icon_label = ctk.CTkLabel(
            status_indicator,
            image=self._status_icons[status_icon_key],
            text="",
            width=40,
            height=40
        )
        self._current_status_icon_label.pack(side="left", padx=(0, 5))
        
        # Status text label
        status_label_color = "#e74c3c" if is_expired else ("#f39c12" if pending_fee > 0 else "#2ecc71")
        ctk.CTkLabel(
            status_indicator,
            text=status_tooltip,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=status_label_color
        ).pack(side="left")
        
        pay_details = [
            ("Amount Paid", format_currency(amount_paid), "#2ecc71"),
            ("Pending Amount", format_currency(pending_fee), "#f39c12" if pending_fee > 0 else "#2ecc71"),
            ("Last Payment", format_date(member['last_payment_date']) if member['last_payment_date'] else "N/A", "#aaaaaa"),
        ]
        
        for label, value, color in pay_details:
            row = ctk.CTkFrame(payment_frame, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=2)
            
            ctk.CTkLabel(
                row,
                text=label,
                font=ctk.CTkFont(size=12),
                text_color="#888888",
                width=120,
                anchor="w"
            ).pack(side="left")
            
            ctk.CTkLabel(
                row,
                text=value,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=color
            ).pack(side="right")
        
        # Pending Fee Highlight with Visual Indicator
        if pending_fee > 0 or is_expired:
            # Determine banner color and icon
            if is_expired:
                banner_bg = "#4a1a1a"  # Dark red
                banner_icon_key = "expired_large"
                msg = f"Membership expired!\nRenewal fee: {format_currency(total_fee)}"
                text_color = "#e74c3c"
            else:
                banner_bg = "#4a3000"  # Dark orange
                banner_icon_key = "pending_large"
                msg = f"Pending fee:\n{format_currency(pending_fee)}"
                text_color = "#f39c12"
            
            highlight = ctk.CTkFrame(payment_frame, fg_color=banner_bg, corner_radius=8)
            highlight.pack(fill="x", padx=15, pady=(8, 10))
            
            # Banner content with icon
            banner_content = ctk.CTkFrame(highlight, fg_color="transparent")
            banner_content.pack(fill="x", padx=10, pady=10)
            
            # Large status icon on the left - store reference
            self._banner_icon_label = ctk.CTkLabel(
                banner_content,
                image=self._status_icons[banner_icon_key],
                text="",
                width=56,
                height=56
            )
            self._banner_icon_label.pack(side="left", padx=(5, 15))
            
            # Text on the right
            ctk.CTkLabel(
                banner_content,
                text=msg,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=text_color,
                justify="left"
            ).pack(side="left", anchor="w")
            
        else:
            # Fully paid - show green success banner
            success_banner = ctk.CTkFrame(payment_frame, fg_color="#1a3d1a", corner_radius=8)
            success_banner.pack(fill="x", padx=15, pady=(8, 10))
            
            success_content = ctk.CTkFrame(success_banner, fg_color="transparent")
            success_content.pack(fill="x", padx=10, pady=10)
            
            # Green check icon - store reference
            self._banner_icon_label = ctk.CTkLabel(
                success_content,
                image=self._status_icons["paid_large"],
                text="",
                width=56,
                height=56
            )
            self._banner_icon_label.pack(side="left", padx=(5, 15))
            
            ctk.CTkLabel(
                success_content,
                text="All Fees Paid\nMembership Active",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#2ecc71",
                justify="left"
            ).pack(side="left", anchor="w")
        
        # Personal Training Info (if any)
        if member['current_trainer']:
            pt_frame = ctk.CTkFrame(content, fg_color="#1a2d4a", corner_radius=8)
            pt_frame.pack(fill="x", pady=5)
            
            pt_remaining = get_remaining_days(member['pt_end_date']) if member['pt_end_date'] else 0
            pt_status = "Active" if pt_remaining > 0 else "Expired"
            
            ctk.CTkLabel(
                pt_frame,
                text="🏃 Personal Training",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#3498db"
            ).pack(anchor="w", padx=15, pady=(10, 5))
            
            ctk.CTkLabel(
                pt_frame,
                text=f"Trainer: {member['current_trainer']}",
                font=ctk.CTkFont(size=13),
                text_color="#ffffff"
            ).pack(anchor="w", padx=15)
            
            ctk.CTkLabel(
                pt_frame,
                text=f"Status: {pt_status} | {pt_remaining} days left",
                font=ctk.CTkFont(size=12),
                text_color="#2ecc71" if pt_remaining > 0 else "#e74c3c"
            ).pack(anchor="w", padx=15)
            
            if member['pt_fee']:
                ctk.CTkLabel(
                    pt_frame,
                    text=f"PT Fee: {format_currency(member['pt_fee'])}",
                    font=ctk.CTkFont(size=12),
                    text_color="#aaaaaa"
                ).pack(anchor="w", padx=15, pady=(0, 10))
        
        # Show payment section
        self.show_payment_section(member, is_expired, pending_fee)
        
    def show_payment_section(self, member, is_expired, pending_fee):
        """Show the payment confirmation section"""
        # Clear and show payment section
        for widget in self.payment_section.winfo_children():
            widget.destroy()
        
        # Re-pack payment section in scroll container (after details_frame)
        self.payment_section.pack(fill="x", padx=10, pady=(5, 10))
        
        # Header
        ctk.CTkLabel(
            self.payment_section,
            text="💵 Record Payment",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#FFD700"
        ).pack(anchor="w", padx=15, pady=(12, 8))
        
        # Payment Type
        type_frame = ctk.CTkFrame(self.payment_section, fg_color="transparent")
        type_frame.pack(fill="x", padx=15, pady=4)
        
        ctk.CTkLabel(
            type_frame,
            text="Payment Type",
            font=ctk.CTkFont(size=12),
            text_color="#aaaaaa"
        ).pack(anchor="w")
        
        self.payment_type_var = ctk.StringVar(value="Membership")
        ctk.CTkComboBox(
            type_frame,
            variable=self.payment_type_var,
            values=PAYMENT_TYPES,
            height=32,
            fg_color="#3d3d3d",
            border_color="#444444",
            button_color="#FFD700",
            button_hover_color="#FFC000",
            dropdown_fg_color="#3d3d3d",
            command=self.on_payment_type_change
        ).pack(fill="x", pady=(2, 0))
        
        # Amount
        amount_frame = ctk.CTkFrame(self.payment_section, fg_color="transparent")
        amount_frame.pack(fill="x", padx=15, pady=4)
        
        ctk.CTkLabel(
            amount_frame,
            text="Amount (₹)",
            font=ctk.CTkFont(size=12),
            text_color="#aaaaaa"
        ).pack(anchor="w")
        
        # Calculate suggested amount
        if is_expired:
            suggested_amount = FEE_MAP.get(member['membership_type'], 1200)
        else:
            suggested_amount = pending_fee if pending_fee > 0 else FEE_MAP.get(member['membership_type'], 1200)
        
        self.amount_var = ctk.StringVar(value=str(int(suggested_amount)))
        ctk.CTkEntry(
            amount_frame,
            textvariable=self.amount_var,
            height=36,
            font=ctk.CTkFont(size=14),
            fg_color="#3d3d3d",
            border_color="#444444"
        ).pack(fill="x", pady=(2, 0))
        
        # Renewal option for expired members
        self.extend_var = ctk.BooleanVar(value=is_expired)
        self.extend_check = ctk.CTkCheckBox(
            self.payment_section,
            text="Extend/Renew membership",
            variable=self.extend_var,
            font=ctk.CTkFont(size=12),
            fg_color="#FFD700",
            hover_color="#FFC000",
            text_color="#ffffff",
            checkbox_height=18,
            checkbox_width=18
        )
        self.extend_check.pack(anchor="w", padx=15, pady=4)
        
        # Notes
        notes_frame = ctk.CTkFrame(self.payment_section, fg_color="transparent")
        notes_frame.pack(fill="x", padx=15, pady=4)
        
        ctk.CTkLabel(
            notes_frame,
            text="Notes (Optional)",
            font=ctk.CTkFont(size=12),
            text_color="#aaaaaa"
        ).pack(anchor="w")
        
        self.notes_var = ctk.StringVar()
        ctk.CTkEntry(
            notes_frame,
            textvariable=self.notes_var,
            height=32,
            placeholder_text="Add payment notes...",
            fg_color="#3d3d3d",
            border_color="#444444"
        ).pack(fill="x", pady=(2, 0))
        
        # Confirm Button - ALWAYS VISIBLE
        ctk.CTkButton(
            self.payment_section,
            text="✓ CONFIRM PAYMENT",
            command=self.confirm_payment,
            fg_color="#2ecc71",
            hover_color="#27ae60",
            height=42,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(fill="x", padx=15, pady=(10, 15))
        
    def on_payment_type_change(self, value):
        """Handle payment type change"""
        if not self.verified_member:
            return
            
        member = self.verified_member
        
        if value == "Membership" or value == "Renewal":
            amount_paid = member['amount_paid'] or 0
            pending = calculate_pending_fee(member['membership_type'], amount_paid)
            
            if get_membership_status(member['end_date']) == "Expired":
                suggested = FEE_MAP.get(member['membership_type'], 1200)
            else:
                suggested = pending if pending > 0 else FEE_MAP.get(member['membership_type'], 1200)
            
            self.amount_var.set(str(int(suggested)))
            self.extend_var.set(True)
        elif value == "PT":
            # Suggest PT fee if available
            if member['pt_fee']:
                self.amount_var.set(str(int(member['pt_fee'])))
            self.extend_var.set(False)
        
    def confirm_payment(self):
        """Confirm and process the payment"""
        if not self.verified_member:
            messagebox.showerror("Error", "Please verify a member first")
            return
        
        member = self.verified_member
        
        try:
            amount = float(self.amount_var.get())
            if amount <= 0:
                raise ValueError
        except:
            messagebox.showerror("Invalid Amount", "Please enter a valid payment amount")
            return
        
        payment_type = self.payment_type_var.get()
        notes = self.notes_var.get().strip()
        extend_membership = self.extend_var.get()
        
        # Confirm with user
        confirm_msg = f"""Confirm Payment Details:

Member: {member['name']}
Phone: {member['phone']}
Amount: {format_currency(amount)}
Type: {payment_type}
{"Membership will be extended" if extend_membership else ""}

Proceed with payment?"""
        
        if not messagebox.askyesno("Confirm Payment", confirm_msg):
            return
        
        # Process payment
        try:
            # Add payment record
            db.add_payment(
                member['id'],
                member['phone'],
                amount,
                payment_type,
                notes
            )
            
            # Calculate new values
            total_fee = FEE_MAP.get(member['membership_type'], 1200)
            current_paid = (member['amount_paid'] or 0) + amount
            new_pending = max(0, total_fee - current_paid)
            
            # Calculate new end date if extending
            new_end_date = None
            if extend_membership and (payment_type == "Membership" or payment_type == "Renewal"):
                new_end_date = calculate_new_end_date(member['end_date'], member['membership_type'])
                # Reset amount tracking for renewal
                if get_membership_status(member['end_date']) == "Expired":
                    current_paid = amount
                    new_pending = max(0, total_fee - amount)
            
            # Update member payment info
            db.update_member_payment(
                member['id'],
                amount,
                new_pending,
                new_end_date
            )
            
            # Update member status
            db.update_member_status()
            
            # Success message
            success_msg = f"""✓ Payment Recorded Successfully!

Member: {member['name']}
Amount: {format_currency(amount)}
{"New End Date: " + format_date(new_end_date) if new_end_date else ""}

Receipt ID: #{db.get_member_payments(member['id'])[0]['id']}"""
            
            messagebox.showinfo("Payment Success", success_msg)
            
            # Reset form
            self.phone_var.set("")
            self.verified_member = None
            self.show_empty_state()
            self.payment_section.pack_forget()
            self.load_payment_history()
            
        except Exception as e:
            messagebox.showerror("Payment Error", f"Failed to process payment: {str(e)}")
            
    def create_history_panel(self, parent):
        """Create the payment history panel"""
        history_frame = ctk.CTkFrame(parent, fg_color="#1a1a1a", corner_radius=10)
        history_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        # Header
        header_frame = ctk.CTkFrame(history_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(
            header_frame,
            text="📋 Payment History",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#FFD700"
        ).pack(side="left")
        
        ctk.CTkButton(
            header_frame,
            text="🔄 Refresh",
            width=80,
            height=30,
            command=self.load_payment_history,
            fg_color="#3498db",
            hover_color="#2980b9"
        ).pack(side="right")
        
        # Stats
        stats_frame = ctk.CTkFrame(history_frame, fg_color="#2d2d2d", corner_radius=8)
        stats_frame.pack(fill="x", padx=20, pady=10)
        
        self.today_collection_label = ctk.CTkLabel(
            stats_frame,
            text="Today's Collection: ₹0",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#2ecc71"
        )
        self.today_collection_label.pack(side="left", padx=15, pady=10)
        
        self.month_collection_label = ctk.CTkLabel(
            stats_frame,
            text="This Month: ₹0",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#FFD700"
        )
        self.month_collection_label.pack(side="right", padx=15, pady=10)
        
        # Column headers
        headers_frame = ctk.CTkFrame(history_frame, fg_color="#2d2d2d", corner_radius=5)
        headers_frame.pack(fill="x", padx=20, pady=(10, 5))
        
        headers = ["Date", "Member", "Phone", "Type", "Amount"]
        widths = [90, 150, 100, 90, 100]
        
        for header, width in zip(headers, widths):
            ctk.CTkLabel(
                headers_frame,
                text=header,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#FFD700",
                width=width
            ).pack(side="left", padx=5, pady=8)
        
        # Payment list
        self.payment_list = ctk.CTkScrollableFrame(history_frame, fg_color="#2d2d2d", corner_radius=8)
        self.payment_list.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.load_payment_history()
        
    def load_payment_history(self):
        """Load payment history"""
        for widget in self.payment_list.winfo_children():
            widget.destroy()
        
        # Update stats
        today_total = db.get_today_collections()
        month_total = db.get_monthly_collections()
        
        self.today_collection_label.configure(text=f"Today's Collection: {format_currency(today_total)}")
        self.month_collection_label.configure(text=f"This Month: {format_currency(month_total)}")
        
        # Load payments
        payments = db.get_all_payments()
        
        if not payments:
            ctk.CTkLabel(
                self.payment_list,
                text="No payment records yet",
                font=ctk.CTkFont(size=14),
                text_color="#888888"
            ).pack(pady=50)
            return
        
        for i, payment in enumerate(payments[:50]):  # Show last 50
            row_bg = "#3d3d3d" if i % 2 == 0 else "#2d2d2d"
            row = ctk.CTkFrame(self.payment_list, fg_color=row_bg, corner_radius=5)
            row.pack(fill="x", pady=2)
            
            # Date
            ctk.CTkLabel(
                row,
                text=format_date(payment['payment_date']),
                font=ctk.CTkFont(size=11),
                text_color="#aaaaaa",
                width=90,
                anchor="w"
            ).pack(side="left", padx=5, pady=10)
            
            # Member Name
            ctk.CTkLabel(
                row,
                text=payment['member_name'][:18] + "..." if len(payment['member_name']) > 18 else payment['member_name'],
                font=ctk.CTkFont(size=11),
                text_color="#ffffff",
                width=150,
                anchor="w"
            ).pack(side="left", padx=5, pady=10)
            
            # Phone
            ctk.CTkLabel(
                row,
                text=payment['phone'],
                font=ctk.CTkFont(size=11),
                text_color="#aaaaaa",
                width=100,
                anchor="w"
            ).pack(side="left", padx=5, pady=10)
            
            # Type
            type_color = "#3498db" if payment['payment_type'] == "PT" else "#2ecc71"
            ctk.CTkLabel(
                row,
                text=payment['payment_type'],
                font=ctk.CTkFont(size=11),
                text_color=type_color,
                width=90,
                anchor="w"
            ).pack(side="left", padx=5, pady=10)
            
            # Amount
            ctk.CTkLabel(
                row,
                text=format_currency(payment['amount']),
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#2ecc71",
                width=100,
                anchor="w"
            ).pack(side="left", padx=5, pady=10)
    
    def refresh(self):
        """Refresh the view"""
        self.load_payment_history()
        if self.verified_member:
            # Re-verify member to get updated data
            member = db.get_member_fee_details(self.verified_member['phone'])
            if member:
                self.verified_member = member
                self.display_member_details(member)
