"""
Horsepower Gym Management System
Main Application Entry Point

A professional desktop application for managing gym operations including:
- Member Management
- Personal Training
- Attendance Tracking
- Dashboard Analytics

Gym: Horsepower Gym
Location: Koodapakkam Road, near Lakshmi Narayana Medical College, Pondicherry
Owner: Manikandan
Trainers: Suriya, Ganesh
"""

import customtkinter as ctk
from tkinter import messagebox
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import views
from views.login import LoginView
from views.dashboard import DashboardView
from views.members import MembersView
from views.training import TrainingView
from views.attendance import AttendanceView
from views.payment import PaymentView
from utils import GYM_INFO

# Configure CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class HorsepowerGymApp(ctk.CTk):
    """Main Application Class"""
    
    def __init__(self):
        super().__init__()
        
        # Window configuration
        self.title(f"{GYM_INFO['name']} - Management System")
        self.geometry("1400x800")
        self.minsize(1200, 700)
        
        # Center window
        self.center_window()
        
        # Configure colors - Gray theme for post-login
        self.colors = {
            "bg_dark": "#0d0d0d",       # Login screen only
            "bg_main": "#6B6F73",       # Main content background (professional gym gray)
            "bg_sidebar": "#5A5E62",    # Sidebar (darker gray)
            "accent": "#FFD700",        # Gold accent
            "accent_hover": "#FFC000",
            "text": "#ffffff",
            "text_muted": "#C0C0C0"
        }
        
        # Configure window
        self.configure(fg_color=self.colors["bg_dark"])
        
        # Initialize logged in state
        self.is_logged_in = False
        self.current_view = None
        self.views = {}
        self.nav_buttons = {}
        
        # Show login first
        self.show_login()
        
        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def center_window(self):
        """Center the window on screen"""
        self.update_idletasks()
        width = 1400
        height = 800
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def show_login(self):
        """Show the login screen"""
        # Clear any existing widgets
        for widget in self.winfo_children():
            widget.destroy()
        
        # Create login view
        self.login_view = LoginView(self, self.on_login_success)
        self.login_view.pack(fill="both", expand=True)
    
    def on_login_success(self):
        """Handle successful login"""
        self.is_logged_in = True
        self.login_view.destroy()
        self.create_main_interface()
    
    def create_main_interface(self):
        """Create the main application interface with gray theme"""
        # Main container with gray theme
        self.main_container = ctk.CTkFrame(self, fg_color=self.colors["bg_main"])
        self.main_container.pack(fill="both", expand=True)
        
        # Configure grid layout for main container
        self.main_container.grid_columnconfigure(1, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)
        
        # Create sidebar
        self.create_sidebar()
        
        # Create content area frame (container for views)
        self.content_frame = ctk.CTkFrame(
            self.main_container, 
            fg_color=self.colors["bg_main"],
            corner_radius=0
        )
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        
        # Configure content frame to expand
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        # Track current view instance
        self.current_view_widget = None
        self.current_view = None
        
        # Show dashboard by default
        self.show_view("dashboard")
    
    def create_sidebar(self):
        """Create the navigation sidebar"""
        sidebar = ctk.CTkFrame(self.main_container, fg_color=self.colors["bg_sidebar"], width=250, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.grid_propagate(False)
        
        # Logo/Header
        header_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(20, 10))
        
        ctk.CTkLabel(
            header_frame,
            text="🏋️",
            font=ctk.CTkFont(size=40)
        ).pack(pady=(0, 5))
        
        ctk.CTkLabel(
            header_frame,
            text=GYM_INFO['name'].upper(),
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors["accent"]
        ).pack()
        
        ctk.CTkLabel(
            header_frame,
            text="Management System",
            font=ctk.CTkFont(size=11),
            text_color=self.colors["text_muted"]
        ).pack()
        
        # Separator
        ctk.CTkFrame(sidebar, fg_color="#333333", height=1).pack(fill="x", padx=15, pady=15)
        
        # Navigation buttons
        nav_items = [
            ("dashboard", "📊", "Dashboard"),
            ("members", "👥", "Members"),
            ("payment", "💳", "Payments"),
            ("training", "🏃", "Personal Training"),
            ("attendance", "✓", "Attendance"),
        ]
        
        self.nav_buttons = {}
        
        for view_name, icon, label in nav_items:
            btn = ctk.CTkButton(
                sidebar,
                text=f"  {icon}  {label}",
                anchor="w",
                height=45,
                font=ctk.CTkFont(size=14),
                fg_color="transparent",
                text_color=self.colors["text"],
                hover_color="#6B7075",
                command=lambda v=view_name: self.show_view(v)
            )
            btn.pack(fill="x", padx=10, pady=3)
            self.nav_buttons[view_name] = btn
        
        # Spacer
        ctk.CTkFrame(sidebar, fg_color="transparent").pack(fill="both", expand=True)
        
        # Bottom section
        bottom_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        bottom_frame.pack(fill="x", padx=15, pady=15)
        
        # Refresh button
        ctk.CTkButton(
            bottom_frame,
            text="🔄 Refresh",
            height=35,
            fg_color="#3498db",
            hover_color="#2980b9",
            command=self.refresh_current_view
        ).pack(fill="x", pady=3)
        
        # Logout button
        ctk.CTkButton(
            bottom_frame,
            text="🚪 Logout",
            height=35,
            fg_color="#e74c3c",
            hover_color="#c0392b",
            command=self.logout
        ).pack(fill="x", pady=3)
        
        # Owner info
        ctk.CTkLabel(
            bottom_frame,
            text=f"Owner: {GYM_INFO['owner']}",
            font=ctk.CTkFont(size=10),
            text_color=self.colors["text_muted"]
        ).pack(pady=(10, 0))
        
        ctk.CTkLabel(
            bottom_frame,
            text=f"Trainers: {', '.join(GYM_INFO['trainers'])}",
            font=ctk.CTkFont(size=10),
            text_color=self.colors["text_muted"]
        ).pack()
    
    def show_view(self, view_name):
        """Show a specific view using clear-and-load pattern"""
        # Update navigation button styles
        for name, btn in self.nav_buttons.items():
            if name == view_name:
                btn.configure(fg_color=self.colors["accent"], text_color="#000000")
            else:
                btn.configure(fg_color="transparent", text_color=self.colors["text"])
        
        # Clear current view from content frame
        if self.current_view_widget is not None:
            self.current_view_widget.destroy()
            self.current_view_widget = None
        
        # Create new view instance
        try:
            if view_name == "dashboard":
                self.current_view_widget = DashboardView(self.content_frame)
            elif view_name == "members":
                self.current_view_widget = MembersView(self.content_frame)
            elif view_name == "payment":
                self.current_view_widget = PaymentView(self.content_frame)
            elif view_name == "training":
                self.current_view_widget = TrainingView(self.content_frame)
            elif view_name == "attendance":
                self.current_view_widget = AttendanceView(self.content_frame)
            else:
                # Fallback - show error label
                self.current_view_widget = ctk.CTkLabel(
                    self.content_frame,
                    text=f"View '{view_name}' not found",
                    font=ctk.CTkFont(size=20),
                    text_color="#e74c3c"
                )
            
            # Pack the view to fill content frame
            if self.current_view_widget:
                self.current_view_widget.grid(row=0, column=0, sticky="nsew")
                self.current_view = view_name
                
        except Exception as e:
            # Show error message if view fails to load
            error_frame = ctk.CTkFrame(self.content_frame, fg_color=self.colors["bg_main"])
            error_frame.grid(row=0, column=0, sticky="nsew")
            
            ctk.CTkLabel(
                error_frame,
                text=f"⚠️ Error loading {view_name}",
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color="#e74c3c"
            ).pack(pady=(100, 10))
            
            ctk.CTkLabel(
                error_frame,
                text=str(e),
                font=ctk.CTkFont(size=14),
                text_color="#ffffff"
            ).pack(pady=10)
            
            self.current_view_widget = error_frame
            print(f"Error loading view {view_name}: {e}")
    
    def refresh_current_view(self):
        """Refresh the current view by reloading it"""
        if self.current_view:
            # Re-show the current view (will destroy and recreate)
            self.show_view(self.current_view)
    
    def logout(self):
        """Handle logout"""
        if messagebox.askyesno("Confirm Logout", "Are you sure you want to logout?"):
            self.is_logged_in = False
            
            # Clear current view
            if self.current_view_widget:
                self.current_view_widget.destroy()
                self.current_view_widget = None
            
            self.current_view = None
            
            # Clear main container
            if hasattr(self, 'main_container'):
                self.main_container.destroy()
            
            # Show login
            self.show_login()
    
    def on_close(self):
        """Handle window close"""
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.destroy()


def main():
    """Main entry point"""
    app = HorsepowerGymApp()
    app.mainloop()


if __name__ == "__main__":
    main()
