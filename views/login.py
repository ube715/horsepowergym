"""
Login View for Horsepower Gym Management System
Handles admin authentication with background image
"""

import customtkinter as ctk
from tkinter import messagebox
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import database as db
from utils import GYM_INFO, get_resource_path
from PIL import Image, ImageFilter, ImageEnhance


class LoginView(ctk.CTkFrame):
    def __init__(self, parent, on_login_success):
        super().__init__(parent, fg_color="#0d0d0d")
        self.on_login_success = on_login_success
        self._bg_image = None
        self._bg_photo = None
        self._original_bg = None
        self.create_widgets()
        
        # Bind resize event for responsive background
        self.bind("<Configure>", self._on_resize)
        
        # Initial background update after window is mapped
        self.after(50, self._initial_background_update)
    
    def _load_background_image(self):
        """Load and prepare the background image"""
        try:
            bg_path = get_resource_path(os.path.join("assets", "login_bg.jpg"))
            if os.path.exists(bg_path):
                self._original_bg = Image.open(bg_path)
                return True
        except Exception as e:
            print(f"Background image error: {e}")
        return False
    
    def _create_sized_background(self, width, height):
        """Create background image sized to window with darkening effect"""
        if self._original_bg is None:
            return None
        
        if width <= 1 or height <= 1:
            return None
        
        try:
            # Calculate scaling to FIT entire image (contain mode - no cropping)
            img_ratio = self._original_bg.width / self._original_bg.height
            win_ratio = width / height
            
            if win_ratio > img_ratio:
                # Window is wider - fit by height
                new_height = height
                new_width = int(height * img_ratio)
            else:
                # Window is taller - fit by width
                new_width = width
                new_height = int(width / img_ratio)
            
            # Resize to fit
            resized = self._original_bg.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Create canvas with dark background and paste image centered
            canvas = Image.new('RGB', (width, height), (13, 13, 13))
            paste_x = (width - new_width) // 2
            paste_y = (height - new_height) // 2
            canvas.paste(resized, (paste_x, paste_y))
            
            # Darken the image for better text readability
            enhancer = ImageEnhance.Brightness(canvas)
            darkened = enhancer.enhance(0.45)
            
            # Add slight blur for depth effect
            blurred = darkened.filter(ImageFilter.GaussianBlur(radius=1))
            
            return blurred
        except Exception as e:
            print(f"Background resize error: {e}")
            return None
    
    def _update_background(self):
        """Update background image to current window size"""
        if not hasattr(self, 'bg_label'):
            return
        
        width = self.winfo_width()
        height = self.winfo_height()
        
        if width <= 1 or height <= 1:
            return
        
        bg_img = self._create_sized_background(width, height)
        if bg_img:
            self._bg_photo = ctk.CTkImage(
                light_image=bg_img,
                dark_image=bg_img,
                size=(width, height)
            )
            self.bg_label.configure(image=self._bg_photo)
    
    def _on_resize(self, event):
        """Handle window resize"""
        if event.widget == self:
            self.after(10, self._update_background)
    
    def _initial_background_update(self):
        """Initial background update after window is ready"""
        self._update_background()
        
    def create_widgets(self):
        # ============================================================
        # BACKGROUND IMAGE (must be created FIRST)
        # ============================================================
        self._load_background_image()
        
        self.bg_label = ctk.CTkLabel(self, text="", fg_color="#0d0d0d")
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        
        # ============================================================
        # RIGHT-ALIGNED LOGIN PANEL
        # ============================================================
        # Container for right-side login panel with margin from edge
        right_panel = ctk.CTkFrame(self, fg_color="transparent")
        right_panel.place(relx=0.95, rely=0.5, anchor="e")  # 5% margin from right edge
        
        # ============================================================
        # UNIFIED LOGIN CARD (Logo + Form combined)
        # ============================================================
        login_card = ctk.CTkFrame(
            right_panel,
            fg_color="#1a1a1a",
            corner_radius=16,
            border_width=2,
            border_color="#FFD700"
        )
        login_card.pack(padx=20, pady=20)
        
        # Inner padding frame
        card_content = ctk.CTkFrame(login_card, fg_color="transparent")
        card_content.pack(padx=40, pady=35)
        
        # ------------------------------------------------------------
        # LOGO & BRANDING SECTION
        # ------------------------------------------------------------
        # Load and display gym logo image
        self._logo_image = None
        try:
            logo_path = get_resource_path(os.path.join("assets", "logo.png"))
            if os.path.exists(logo_path):
                logo_pil = Image.open(logo_path)
                # Resize logo to fit (80x80)
                logo_pil = logo_pil.resize((80, 80), Image.Resampling.LANCZOS)
                self._logo_image = ctk.CTkImage(
                    light_image=logo_pil,
                    dark_image=logo_pil,
                    size=(80, 80)
                )
        except Exception as e:
            print(f"Logo load error: {e}")
        
        if self._logo_image:
            ctk.CTkLabel(
                card_content,
                image=self._logo_image,
                text=""
            ).pack(pady=(0, 10))
        else:
            # Fallback to emoji if logo not found
            ctk.CTkLabel(
                card_content,
                text="🏋️",
                font=ctk.CTkFont(size=56)
            ).pack(pady=(0, 10))
        
        # Gym name (gold, bold, uppercase)
        ctk.CTkLabel(
            card_content,
            text=GYM_INFO['name'].upper(),
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#FFD700"
        ).pack(pady=(0, 5))
        
        # Subtitle
        ctk.CTkLabel(
            card_content,
            text="Management System",
            font=ctk.CTkFont(size=14),
            text_color="#888888"
        ).pack(pady=(0, 25))
        
        # Divider line
        divider = ctk.CTkFrame(card_content, fg_color="#333333", height=1)
        divider.pack(fill="x", pady=(0, 20))
        
        # ------------------------------------------------------------
        # ADMIN LOGIN SECTION
        # ------------------------------------------------------------
        ctk.CTkLabel(
            card_content,
            text="Admin Login",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#ffffff"
        ).pack(pady=(0, 20))
        
        # Username field
        self.username_var = ctk.StringVar()
        
        username_frame = ctk.CTkFrame(card_content, fg_color="transparent")
        username_frame.pack(fill="x", pady=(0, 12))
        
        ctk.CTkLabel(
            username_frame,
            text="Username",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#aaaaaa"
        ).pack(anchor="w")
        
        username_entry = ctk.CTkEntry(
            username_frame,
            textvariable=self.username_var,
            placeholder_text="Enter username",
            height=45,
            width=280,
            font=ctk.CTkFont(size=14),
            fg_color="#2d2d2d",
            border_color="#444444",
            border_width=1,
            corner_radius=8
        )
        username_entry.pack(fill="x", pady=(5, 0))
        
        # Password field
        self.password_var = ctk.StringVar()
        
        password_frame = ctk.CTkFrame(card_content, fg_color="transparent")
        password_frame.pack(fill="x", pady=(0, 8))
        
        ctk.CTkLabel(
            password_frame,
            text="Password",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#aaaaaa"
        ).pack(anchor="w")
        
        self.password_entry = ctk.CTkEntry(
            password_frame,
            textvariable=self.password_var,
            placeholder_text="Enter password",
            height=45,
            width=280,
            font=ctk.CTkFont(size=14),
            fg_color="#2d2d2d",
            border_color="#444444",
            border_width=1,
            corner_radius=8,
            show="●"
        )
        self.password_entry.pack(fill="x", pady=(5, 0))
        self.password_entry.bind("<Return>", lambda e: self.login())
        
        # Show password checkbox
        self.show_password_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            password_frame,
            text="Show password",
            variable=self.show_password_var,
            command=self.toggle_password,
            fg_color="#FFD700",
            hover_color="#FFC000",
            checkbox_width=18,
            checkbox_height=18,
            text_color="#888888",
            font=ctk.CTkFont(size=11)
        ).pack(anchor="w", pady=(8, 0))
        
        # Login button (full width, gold)
        ctk.CTkButton(
            card_content,
            text="🔐 LOGIN",
            command=self.login,
            fg_color="#FFD700",
            hover_color="#FFC000",
            text_color="#000000",
            height=50,
            corner_radius=10,
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(fill="x", pady=(25, 0))
        
        # ============================================================
        # FOOTER - Centered at bottom of window
        # ============================================================
        footer_frame = ctk.CTkFrame(
            self,
            fg_color="#1a1a1a",
            corner_radius=8
        )
        footer_frame.place(relx=0.5, rely=0.96, anchor="center")
        
        ctk.CTkLabel(
            footer_frame,
            text=f"📍 {GYM_INFO['location']}",
            font=ctk.CTkFont(size=11),
            text_color="#aaaaaa"
        ).pack(padx=15, pady=8)
        
    def toggle_password(self):
        """Toggle password visibility"""
        if self.show_password_var.get():
            self.password_entry.configure(show="")
        else:
            self.password_entry.configure(show="●")
    
    def login(self):
        """Handle login"""
        username = self.username_var.get().strip()
        password = self.password_var.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter username and password")
            return
        
        if db.verify_admin(username, password):
            self.on_login_success()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")
            self.password_var.set("")
