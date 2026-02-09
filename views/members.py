"""
Members View for Horsepower Gym Management System
Handles member registration, editing, and management with photo capture
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import date
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import database as db
from utils import (
    calculate_end_date, format_date, format_currency, get_remaining_days,
    is_membership_valid, validate_phone, validate_age, get_membership_fee,
    MEMBERSHIP_TYPES, PAYMENT_STATUS, GENDERS, FEE_MAP,
    load_member_photo_with_badge, save_member_photo, create_default_avatar,
    create_badge_overlay, get_member_photo_path
)
from ui_theme import (
    BG_PRIMARY, BG_SECONDARY, BG_TERTIARY, BG_HOVER,
    ACCENT_GOLD, ACCENT_GOLD_HOVER, TEXT_PRIMARY, TEXT_MUTED,
    SUCCESS, SUCCESS_DARK, ERROR, ERROR_DARK, WARNING, INFO, INFO_DARK,
    BORDER_COLOR, TABLE_ROW_ODD, TABLE_ROW_EVEN, PURPLE, PURPLE_DARK,
    RADIUS_SM, RADIUS_MD
)
from PIL import Image
import cv2
import threading


class MembersView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=BG_PRIMARY)
        self.selected_member_id = None
        self.captured_photo = None  # Store captured PIL image
        self._photo_image = None  # Store CTkImage reference to prevent GC
        self._photo_pil = None  # Store PIL image reference
        self.create_widgets()
        
    def create_widgets(self):
        # Main container with two panels
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_columnconfigure(1, weight=2)
        main_container.grid_rowconfigure(0, weight=1)
        
        # Left Panel - Member Form
        self.create_form_panel(main_container)
        
        # Right Panel - Members List
        self.create_list_panel(main_container)
        
    def create_form_panel(self, parent):
        """Create the member registration/edit form"""
        form_frame = ctk.CTkFrame(parent, fg_color=BG_SECONDARY, corner_radius=RADIUS_MD)
        form_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Header
        ctk.CTkLabel(
            form_frame,
            text="➕ Add / Edit Member",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=ACCENT_GOLD
        ).pack(anchor="w", padx=20, pady=(20, 15))
        
        # Photo Section
        self.create_photo_section(form_frame)
        
        # Scrollable form
        form_scroll = ctk.CTkScrollableFrame(form_frame, fg_color="transparent")
        form_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        # Form fields
        self.name_var = ctk.StringVar()
        self.phone_var = ctk.StringVar()
        self.address_var = ctk.StringVar()
        self.age_var = ctk.StringVar()
        self.gender_var = ctk.StringVar(value="Male")
        self.membership_var = ctk.StringVar(value="Monthly")
        self.start_date_var = ctk.StringVar(value=date.today().strftime('%Y-%m-%d'))
        self.end_date_var = ctk.StringVar()
        self.fees_var = ctk.StringVar(value="1000")
        self.payment_var = ctk.StringVar(value="Pending")
        
        fields = [
            ("Full Name *", self.name_var, "entry"),
            ("Phone Number *", self.phone_var, "entry"),
            ("Address", self.address_var, "entry"),
            ("Age *", self.age_var, "entry"),
            ("Gender", self.gender_var, "combo", GENDERS),
            ("Membership Type *", self.membership_var, "combo", MEMBERSHIP_TYPES),
            ("Start Date (YYYY-MM-DD) *", self.start_date_var, "entry"),
            ("End Date", self.end_date_var, "readonly"),
            ("Fees (₹) *", self.fees_var, "entry"),
            ("Payment Status", self.payment_var, "combo", PAYMENT_STATUS),
        ]
        
        for label, var, field_type, *options in fields:
            field_frame = ctk.CTkFrame(form_scroll, fg_color="transparent")
            field_frame.pack(fill="x", pady=5)
            
            ctk.CTkLabel(
                field_frame,
                text=label,
                font=ctk.CTkFont(size=12),
                text_color=TEXT_MUTED
            ).pack(anchor="w")
            
            if field_type == "entry":
                ctk.CTkEntry(
                    field_frame,
                    textvariable=var,
                    height=35,
                    fg_color=BG_TERTIARY,
                    border_color=BORDER_COLOR
                ).pack(fill="x", pady=(2, 0))
            elif field_type == "readonly":
                entry = ctk.CTkEntry(
                    field_frame,
                    textvariable=var,
                    height=35,
                    fg_color=BG_TERTIARY,
                    border_color=BORDER_COLOR,
                    state="readonly"
                )
                entry.pack(fill="x", pady=(2, 0))
            elif field_type == "combo":
                ctk.CTkComboBox(
                    field_frame,
                    variable=var,
                    values=options[0],
                    height=35,
                    fg_color=BG_TERTIARY,
                    border_color=BORDER_COLOR,
                    button_color=ACCENT_GOLD,
                    button_hover_color=ACCENT_GOLD_HOVER,
                    dropdown_fg_color=BG_TERTIARY
                ).pack(fill="x", pady=(2, 0))
        
        # Bind membership type change to update fee and end date
        self.membership_var.trace_add("write", self.on_membership_change)
        self.start_date_var.trace_add("write", self.on_date_change)
        
        # Calculate initial end date
        self.calculate_end_date()
        
        # Buttons
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkButton(
            btn_frame,
            text="💾 Save Member",
            command=self.save_member,
            fg_color=SUCCESS,
            hover_color=SUCCESS_DARK,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(fill="x", pady=2)
        
        ctk.CTkButton(
            btn_frame,
            text="🔄 Clear Form",
            command=self.clear_form,
            fg_color=INFO,
            hover_color=INFO_DARK,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(fill="x", pady=2)
        
        ctk.CTkButton(
            btn_frame,
            text="🗑️ Delete Member",
            command=self.delete_member,
            fg_color=ERROR,
            hover_color=ERROR_DARK,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(fill="x", pady=2)
    
    def create_photo_section(self, parent):
        """Create the photo capture/display section"""
        photo_frame = ctk.CTkFrame(parent, fg_color=BG_TERTIARY, corner_radius=8)
        photo_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        # Photo display container
        photo_container = ctk.CTkFrame(photo_frame, fg_color="transparent")
        photo_container.pack(pady=15)
        
        # Photo label (will display member photo or placeholder)
        self.photo_label = ctk.CTkLabel(
            photo_container,
            text="",
            width=150,
            height=150
        )
        self.photo_label.pack()
        
        # Set default avatar
        self.set_default_photo()
        
        # Capture button
        ctk.CTkButton(
            photo_frame,
            text="📷 Capture Photo",
            command=self.open_webcam_capture,
            fg_color=PURPLE,
            hover_color=PURPLE_DARK,
            height=35,
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(pady=(0, 15))
    
    def set_default_photo(self, pending_amount=0):
        """Set the default avatar with badge"""
        default_img = create_default_avatar((150, 150))
        default_img = create_badge_overlay(default_img, pending_amount)
        self._photo_pil = default_img
        self._photo_image = ctk.CTkImage(
            light_image=default_img,
            dark_image=default_img,
            size=(150, 150)
        )
        self.photo_label.configure(image=self._photo_image)
    
    def update_photo_display(self, photo_path=None, pending_amount=0):
        """Update the photo display with member photo and badge"""
        if photo_path or self.captured_photo:
            if self.captured_photo:
                # Use captured photo
                img = self.captured_photo.copy()
                from utils import resize_image_pil
                img = resize_image_pil(img, (150, 150))
                img = create_badge_overlay(img, pending_amount)
            else:
                # Load from file
                img = load_member_photo_with_badge(photo_path, pending_amount, (150, 150))
        else:
            img = create_default_avatar((150, 150))
            img = create_badge_overlay(img, pending_amount)
        
        self._photo_pil = img
        self._photo_image = ctk.CTkImage(
            light_image=img,
            dark_image=img,
            size=(150, 150)
        )
        self.photo_label.configure(image=self._photo_image)
    
    def open_webcam_capture(self):
        """Open webcam capture dialog"""
        WebcamCaptureDialog(self, self.on_photo_captured)
    
    def on_photo_captured(self, pil_image):
        """Callback when photo is captured from webcam"""
        self.captured_photo = pil_image
        self.update_photo_display(pending_amount=0)
        
    def create_list_panel(self, parent):
        """Create the members list panel"""
        list_frame = ctk.CTkFrame(parent, fg_color=BG_SECONDARY, corner_radius=10)
        list_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        # Header with search
        header_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(
            header_frame,
            text="👥 Members List",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=ACCENT_GOLD
        ).pack(side="left")
        
        # Search
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self.on_search)
        
        search_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        search_frame.pack(side="right")
        
        ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            placeholder_text="🔍 Search by name or phone...",
            width=250,
            height=35,
            fg_color=BG_TERTIARY,
            border_color=BORDER_COLOR
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            search_frame,
            text="🔄",
            width=40,
            height=35,
            command=self.load_members,
            fg_color=INFO,
            hover_color=INFO_DARK
        ).pack(side="left")
        
        # Column headers with Photo column
        headers_frame = ctk.CTkFrame(list_frame, fg_color=BG_TERTIARY, corner_radius=5)
        headers_frame.pack(fill="x", padx=20, pady=(10, 5))
        
        headers = ["Photo", "Name", "Phone", "Type", "End Date", "Days", "Status"]
        widths = [50, 130, 100, 75, 85, 60, 70]
        
        for header, width in zip(headers, widths):
            ctk.CTkLabel(
                headers_frame,
                text=header,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=ACCENT_GOLD,
                width=width
            ).pack(side="left", padx=3, pady=8)
        
        # Members list
        self.members_list = ctk.CTkScrollableFrame(list_frame, fg_color=BG_TERTIARY, corner_radius=8)
        self.members_list.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Store thumbnail image references to prevent garbage collection
        self._thumbnail_images = []
        
        self.load_members()
        
    def load_members(self, members=None):
        """Load members into the list with photo thumbnails and payment badges"""
        # Clear existing
        for widget in self.members_list.winfo_children():
            widget.destroy()
        
        # Clear thumbnail references
        self._thumbnail_images = []
            
        if members is None:
            members = db.get_all_members()
        
        if not members:
            ctk.CTkLabel(
                self.members_list,
                text="No members found",
                font=ctk.CTkFont(size=14),
                text_color=TEXT_MUTED
            ).pack(pady=50)
            return
            
        for i, member in enumerate(members):
            is_valid = is_membership_valid(member['end_date'])
            remaining = get_remaining_days(member['end_date'])
            
            # Row frame - highlight expired members in red
            row_bg = TABLE_ROW_ODD if i % 2 == 0 else TABLE_ROW_EVEN
            if not is_valid:
                row_bg = "#4a1a1a"  # Dark red for expired
            
            row = ctk.CTkFrame(self.members_list, fg_color=row_bg, corner_radius=5)
            row.pack(fill="x", pady=2)
            row.bind("<Button-1>", lambda e, m=member: self.select_member(m))
            
            # Make all children clickable
            def make_clickable(widget, member):
                widget.bind("<Button-1>", lambda e, m=member: self.select_member(m))
            
            # Photo thumbnail with badge
            photo_path = member['photo_path'] if 'photo_path' in member.keys() else None
            pending_amount = member['pending_amount'] if 'pending_amount' in member.keys() else 0
            
            # Load thumbnail with payment badge overlay
            thumb_img = self._create_list_thumbnail(photo_path, pending_amount or 0)
            thumb_ctk = ctk.CTkImage(light_image=thumb_img, dark_image=thumb_img, size=(40, 40))
            self._thumbnail_images.append(thumb_ctk)  # Prevent garbage collection
            
            photo_label = ctk.CTkLabel(row, image=thumb_ctk, text="", width=50)
            photo_label.pack(side="left", padx=3, pady=5)
            make_clickable(photo_label, member)
            
            # Name
            name_label = ctk.CTkLabel(
                row,
                text=member['name'][:16] + "..." if len(member['name']) > 16 else member['name'],
                font=ctk.CTkFont(size=12),
                text_color=TEXT_PRIMARY if is_valid else ERROR,
                width=130,
                anchor="w"
            )
            name_label.pack(side="left", padx=3, pady=10)
            make_clickable(name_label, member)
            
            # Phone
            phone_label = ctk.CTkLabel(
                row,
                text=member['phone'],
                font=ctk.CTkFont(size=12),
                text_color=TEXT_MUTED,
                width=100,
                anchor="w"
            )
            phone_label.pack(side="left", padx=3, pady=10)
            make_clickable(phone_label, member)
            
            # Type
            type_label = ctk.CTkLabel(
                row,
                text=member['membership_type'][:7],
                font=ctk.CTkFont(size=12),
                text_color=TEXT_MUTED,
                width=75,
                anchor="w"
            )
            type_label.pack(side="left", padx=3, pady=10)
            make_clickable(type_label, member)
            
            # End Date
            end_label = ctk.CTkLabel(
                row,
                text=format_date(member['end_date']),
                font=ctk.CTkFont(size=11),
                text_color=TEXT_MUTED,
                width=85,
                anchor="w"
            )
            end_label.pack(side="left", padx=3, pady=10)
            make_clickable(end_label, member)
            
            # Days Left
            days_color = SUCCESS if remaining > 7 else WARNING if remaining > 0 else ERROR
            days_label = ctk.CTkLabel(
                row,
                text=f"{remaining}d" if is_valid else "EXP",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=days_color,
                width=60,
                anchor="w"
            )
            days_label.pack(side="left", padx=3, pady=10)
            make_clickable(days_label, member)
            
            # Payment Status with icon
            status_color = SUCCESS if member['payment_status'] == "Paid" else ERROR
            status_text = "✓ Paid" if member['payment_status'] == "Paid" else "⚠ Due"
            status_label = ctk.CTkLabel(
                row,
                text=status_text,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=status_color,
                width=70,
                anchor="w"
            )
            status_label.pack(side="left", padx=3, pady=10)
            make_clickable(status_label, member)
    
    def _create_list_thumbnail(self, photo_path, pending_amount):
        """Create a small thumbnail with mini payment badge for the members list"""
        from utils import create_mini_badge_overlay
        
        # Load or create base image
        try:
            if photo_path:
                from utils import get_data_path, resize_image_pil
                full_path = os.path.join(get_data_path(), photo_path)
                if os.path.exists(full_path):
                    img = Image.open(full_path)
                    img = resize_image_pil(img, (40, 40))
                else:
                    img = self._create_mini_avatar((40, 40))
            else:
                img = self._create_mini_avatar((40, 40))
        except Exception:
            img = self._create_mini_avatar((40, 40))
        
        # Apply mini badge
        img = create_mini_badge_overlay(img, pending_amount)
        return img
    
    def _create_mini_avatar(self, size=(40, 40)):
        """Create a small default avatar"""
        from PIL import ImageDraw
        img = Image.new("RGB", size, (60, 60, 60))
        draw = ImageDraw.Draw(img)
        
        # Simple circle with person icon
        center_x, center_y = size[0] // 2, size[1] // 2
        radius = min(size) // 2 - 2
        draw.ellipse(
            [center_x - radius, center_y - radius,
             center_x + radius, center_y + radius],
            fill=(80, 80, 80),
            outline=(100, 100, 100)
        )
        
        # Head
        head_r = radius // 3
        draw.ellipse(
            [center_x - head_r, center_y - radius // 2,
             center_x + head_r, center_y - radius // 2 + head_r * 2],
            fill=(120, 120, 120)
        )
        
        # Body
        body_top = center_y
        draw.ellipse(
            [center_x - radius // 2, body_top,
             center_x + radius // 2, body_top + radius],
            fill=(120, 120, 120)
        )
        
        return img
    
    def select_member(self, member):
        """Select a member and populate the form"""
        self.selected_member_id = member['id']
        self.captured_photo = None  # Clear any captured photo
        self.name_var.set(member['name'])
        self.phone_var.set(member['phone'])
        self.address_var.set(member['address'] or "")
        self.age_var.set(str(member['age']) if member['age'] else "")
        self.gender_var.set(member['gender'] or "Male")
        self.membership_var.set(member['membership_type'])
        self.start_date_var.set(member['start_date'])
        self.end_date_var.set(member['end_date'])
        self.fees_var.set(str(member['fees']))
        self.payment_var.set(member['payment_status'])
        
        # Load member photo with badge
        photo_path = member['photo_path'] if 'photo_path' in member.keys() else None
        pending_amount = member['pending_amount'] if 'pending_amount' in member.keys() else 0
        self.update_photo_display(photo_path, pending_amount or 0)
    
    def save_member(self):
        """Save or update member"""
        # Validate required fields
        if not self.name_var.get().strip():
            messagebox.showerror("Error", "Please enter member name")
            return
        
        phone = self.phone_var.get().strip().replace(" ", "").replace("-", "")
        
        if not validate_phone(phone):
            messagebox.showerror("Error", "Please enter a valid phone number (10+ digits)")
            return
        
        # Check phone uniqueness
        if db.check_phone_exists(phone, self.selected_member_id):
            messagebox.showerror("Duplicate Phone", 
                "This phone number is already registered with another member.\n"
                "Phone numbers must be unique.")
            return
        
        if not validate_age(self.age_var.get()):
            messagebox.showerror("Error", "Please enter a valid age (10-100)")
            return
        
        try:
            fees = float(self.fees_var.get())
        except:
            messagebox.showerror("Error", "Please enter valid fees amount")
            return
        
        # Validate date format
        try:
            start_date = self.start_date_var.get()
            if len(start_date) != 10 or start_date[4] != '-' or start_date[7] != '-':
                raise ValueError
        except:
            messagebox.showerror("Error", "Please enter date in YYYY-MM-DD format")
            return
        
        # Calculate end date
        end_date = calculate_end_date(start_date, self.membership_var.get())
        
        # Calculate pending amount
        total_fee = FEE_MAP.get(self.membership_var.get(), 1200)
        payment_status = self.payment_var.get()
        amount_paid = fees if payment_status == "Paid" else 0
        pending_amount = total_fee - amount_paid if payment_status == "Pending" else 0
        
        if self.selected_member_id:
            # Update existing member
            db.update_member(
                self.selected_member_id,
                self.name_var.get().strip(),
                phone,
                self.address_var.get().strip(),
                int(self.age_var.get()),
                self.gender_var.get(),
                self.membership_var.get(),
                start_date,
                end_date,
                fees,
                payment_status
            )
            
            # Save photo if captured
            if self.captured_photo:
                photo_path = save_member_photo(self.captured_photo, phone)
                db.update_member_photo(self.selected_member_id, photo_path)
            
            messagebox.showinfo("Success", "Member updated successfully!")
        else:
            # Add new member
            member_id = db.add_member(
                self.name_var.get().strip(),
                phone,
                self.address_var.get().strip(),
                int(self.age_var.get()),
                self.gender_var.get(),
                self.membership_var.get(),
                start_date,
                end_date,
                fees,
                payment_status
            )
            
            # Save photo if captured
            if self.captured_photo:
                photo_path = save_member_photo(self.captured_photo, phone)
                db.update_member_photo(member_id, photo_path)
            
            # Update payment fields for new member
            db.update_member_payment(member_id, amount_paid, pending_amount)
            
            # Add payment record if paid
            if payment_status == "Paid":
                db.add_payment(member_id, phone, fees, "Membership", "Initial registration")
            
            messagebox.showinfo("Success", "Member added successfully!")
        
        # Update all member statuses
        db.update_member_status()
        
        self.clear_form()
        self.load_members()
    
    def delete_member(self):
        """Delete selected member"""
        if not self.selected_member_id:
            messagebox.showwarning("Warning", "Please select a member to delete")
            return
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this member?"):
            db.delete_member(self.selected_member_id)
            messagebox.showinfo("Success", "Member deleted successfully!")
            self.clear_form()
            self.load_members()
    
    def clear_form(self):
        """Clear the form"""
        self.selected_member_id = None
        self.captured_photo = None  # Clear captured photo
        self.name_var.set("")
        self.phone_var.set("")
        self.address_var.set("")
        self.age_var.set("")
        self.gender_var.set("Male")
        self.membership_var.set("Monthly")
        self.start_date_var.set(date.today().strftime('%Y-%m-%d'))
        self.fees_var.set(str(get_membership_fee("Monthly")))
        self.payment_var.set("Pending")
        self.calculate_end_date()
        self.set_default_photo()  # Reset to default avatar
    
    def on_membership_change(self, *args):
        """Handle membership type change"""
        self.fees_var.set(str(get_membership_fee(self.membership_var.get())))
        self.calculate_end_date()
    
    def on_date_change(self, *args):
        """Handle start date change"""
        self.calculate_end_date()
    
    def calculate_end_date(self):
        """Calculate and set end date"""
        try:
            end = calculate_end_date(self.start_date_var.get(), self.membership_var.get())
            self.end_date_var.set(end)
        except:
            pass
    
    def on_search(self, *args):
        """Handle search"""
        query = self.search_var.get().strip()
        if query:
            members = db.search_members(query)
        else:
            members = db.get_all_members()
        self.load_members(members)
    
    def refresh(self):
        """Refresh the view"""
        self.load_members()


class WebcamCaptureDialog(ctk.CTkToplevel):
    """Dialog for capturing photo from webcam"""
    
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback
        self.captured_image = None
        self.is_running = True
        self._preview_image = None  # Store CTkImage reference
        self._preview_pil = None  # Store PIL image reference
        
        # Window configuration
        self.title("📷 Capture Photo")
        self.geometry("500x500")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 250
        y = (self.winfo_screenheight() // 2) - 250
        self.geometry(f"+{x}+{y}")
        
        # Configure
        self.configure(fg_color=BG_SECONDARY)
        
        # Header
        ctk.CTkLabel(
            self,
            text="📷 Webcam Photo Capture",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=ACCENT_GOLD
        ).pack(pady=(15, 10))
        
        # Instructions
        ctk.CTkLabel(
            self,
            text="Position yourself in the frame and click 'Capture' or press SPACE",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_MUTED
        ).pack(pady=(0, 10))
        
        # Preview frame
        self.preview_frame = ctk.CTkFrame(self, fg_color=BG_TERTIARY, corner_radius=10)
        self.preview_frame.pack(padx=20, pady=10)
        
        # Preview label for webcam feed
        self.preview_label = ctk.CTkLabel(
            self.preview_frame,
            text="Starting camera...",
            width=400,
            height=300,
            font=ctk.CTkFont(size=14),
            text_color=TEXT_MUTED
        )
        self.preview_label.pack(padx=10, pady=10)
        
        # Buttons frame
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=15)
        
        ctk.CTkButton(
            btn_frame,
            text="📸 Capture",
            command=self.capture_photo,
            fg_color=SUCCESS,
            hover_color=SUCCESS_DARK,
            width=120,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            btn_frame,
            text="❌ Cancel",
            command=self.cancel,
            fg_color=ERROR,
            hover_color=ERROR_DARK,
            width=120,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=10)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=WARNING
        )
        self.status_label.pack(pady=(5, 15))
        
        # Bind keyboard shortcuts
        self.bind("<space>", lambda e: self.capture_photo())
        self.bind("<Return>", lambda e: self.capture_photo())
        self.bind("<Escape>", lambda e: self.cancel())
        
        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        
        # Start webcam feed
        self.cap = None
        self.start_webcam()
    
    def start_webcam(self):
        """Start the webcam feed"""
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                self.show_error("Could not open webcam. Please check if camera is connected.")
                return
            
            # Set resolution
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            # Start update loop
            self.update_preview()
            
        except Exception as e:
            self.show_error(f"Webcam error: {str(e)}")
    
    def update_preview(self):
        """Update the preview with webcam feed"""
        if not self.is_running or self.cap is None:
            return
        
        try:
            ret, frame = self.cap.read()
            if ret:
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Convert to PIL Image
                pil_image = Image.fromarray(frame_rgb)
                
                # Resize for preview (maintain aspect ratio)
                pil_image = pil_image.resize((400, 300), Image.Resampling.LANCZOS)
                
                # Store the full-resolution frame for capture
                self.current_frame = Image.fromarray(frame_rgb)
                
                # Create CTkImage and update preview
                self._preview_pil = pil_image
                self._preview_image = ctk.CTkImage(
                    light_image=pil_image,
                    dark_image=pil_image,
                    size=(400, 300)
                )
                self.preview_label.configure(image=self._preview_image, text="")
            
            # Schedule next update
            if self.is_running:
                self.after(30, self.update_preview)  # ~30 FPS
                
        except Exception as e:
            if self.is_running:
                self.after(100, self.update_preview)
    
    def capture_photo(self):
        """Capture the current frame"""
        if hasattr(self, 'current_frame') and self.current_frame:
            self.captured_image = self.current_frame.copy()
            self.status_label.configure(text="✅ Photo captured! Closing...", text_color=SUCCESS)
            
            # Stop webcam and close
            self.is_running = False
            if self.cap:
                self.cap.release()
            
            # Call callback with captured image
            if self.callback:
                self.callback(self.captured_image)
            
            # Close dialog after a short delay
            self.after(500, self.destroy)
        else:
            self.status_label.configure(text="⚠️ No frame available. Try again.", text_color=WARNING)
    
    def cancel(self):
        """Cancel and close the dialog"""
        self.is_running = False
        if self.cap:
            self.cap.release()
        self.destroy()
    
    def show_error(self, message):
        """Show error message"""
        self.preview_label.configure(text=f"❌ {message}", text_color=ERROR)
        self.status_label.configure(text="Camera unavailable", text_color=ERROR)