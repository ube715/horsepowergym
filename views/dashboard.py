"""
Dashboard View for Horsepower Gym Management System
Displays key metrics and summaries
Gray theme applied for professional gym look
"""

import customtkinter as ctk
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import database as db
from utils import format_currency, GYM_INFO
from ui_theme import *


class DashboardView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=BG_PRIMARY)
        self.create_widgets()
        
    def create_widgets(self):
        # Header with gray theme
        header_frame = ctk.CTkFrame(self, fg_color=BG_SECONDARY, corner_radius=RADIUS_MD)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(
            header_frame,
            text="📊 Dashboard",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=ACCENT_GOLD
        ).pack(side="left", padx=20, pady=15)
        
        # Welcome message
        ctk.CTkLabel(
            header_frame,
            text=f"Welcome to {GYM_INFO['name']}",
            font=ctk.CTkFont(size=16),
            text_color=TEXT_MUTED
        ).pack(side="right", padx=20, pady=15)
        
        # Stats Cards Container
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.pack(fill="x", padx=20, pady=10)
        
        # Configure grid
        cards_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Create stat cards
        self.create_stat_card(cards_frame, 0, "👥", "Total Members", 
                             str(db.get_total_members_count()), "#3498db")
        self.create_stat_card(cards_frame, 1, "✅", "Active Members", 
                             str(db.get_active_members_count()), "#2ecc71")
        self.create_stat_card(cards_frame, 2, "⚠️", "Expired Members", 
                             str(db.get_expired_members_count()), "#e74c3c")
        self.create_stat_card(cards_frame, 3, "📅", "Today's Attendance", 
                             str(db.get_today_attendance_count()), "#9b59b6")
        
        # Second row of cards
        cards_frame2 = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame2.pack(fill="x", padx=20, pady=10)
        cards_frame2.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.create_stat_card(cards_frame2, 0, "💰", "Monthly Revenue", 
                             format_currency(db.get_monthly_revenue()), "#f39c12")
        
        # Pending Payments card - shows members with outstanding dues
        pending_members = db.get_pending_payments()
        pending_count = len(pending_members) if pending_members else 0
        self.create_stat_card(cards_frame2, 1, "💳", "Pending Payments", 
                             str(pending_count), "#e74c3c")
        
        # Today's Collections
        self.create_stat_card(cards_frame2, 2, "📈", "Today's Collections", 
                             format_currency(db.get_today_collections()), "#2ecc71")
        
        # Quick Actions - Gray theme
        actions_frame = ctk.CTkFrame(self, fg_color=BG_SECONDARY, corner_radius=RADIUS_MD)
        actions_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            actions_frame,
            text="📋 Quick Information",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=ACCENT_GOLD
        ).pack(anchor="w", padx=20, pady=(15, 10))
        
        info_grid = ctk.CTkFrame(actions_frame, fg_color="transparent")
        info_grid.pack(fill="x", padx=20, pady=(0, 15))
        
        # Gym info
        info_items = [
            ("🏋️ Gym Name:", GYM_INFO['name']),
            ("📍 Location:", GYM_INFO['location']),
            ("👤 Owner:", GYM_INFO['owner']),
            ("🏃 Trainers:", ", ".join(GYM_INFO['trainers'])),
            ("📆 Date:", datetime.now().strftime('%d-%b-%Y')),
            ("⏰ Time:", datetime.now().strftime('%I:%M %p'))
        ]
        
        for i, (label, value) in enumerate(info_items):
            row = i // 2
            col = i % 2
            
            item_frame = ctk.CTkFrame(info_grid, fg_color=BG_TERTIARY, corner_radius=RADIUS_SM)
            item_frame.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            info_grid.grid_columnconfigure(col, weight=1)
            
            ctk.CTkLabel(
                item_frame,
                text=label,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=ACCENT_GOLD
            ).pack(anchor="w", padx=10, pady=(8, 2))
            
            ctk.CTkLabel(
                item_frame,
                text=value,
                font=ctk.CTkFont(size=12),
                text_color=TEXT_PRIMARY
            ).pack(anchor="w", padx=10, pady=(0, 8))
        
        # Today's Attendance Preview - Gray theme
        attendance_frame = ctk.CTkFrame(self, fg_color=BG_SECONDARY, corner_radius=RADIUS_MD)
        attendance_frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))
        
        ctk.CTkLabel(
            attendance_frame,
            text="📝 Recent Check-ins Today",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=ACCENT_GOLD
        ).pack(anchor="w", padx=20, pady=(15, 10))
        
        # Attendance list
        attendance_list = ctk.CTkScrollableFrame(attendance_frame, fg_color=BG_TERTIARY, corner_radius=RADIUS_SM)
        attendance_list.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        today_attendance = db.get_today_attendance()
        
        if today_attendance:
            for i, record in enumerate(today_attendance[:10]):  # Show last 10
                item_frame = ctk.CTkFrame(attendance_list, fg_color=TABLE_ROW_ODD if i % 2 == 0 else TABLE_ROW_EVEN, corner_radius=5)
                item_frame.pack(fill="x", padx=5, pady=2)
                
                ctk.CTkLabel(
                    item_frame,
                    text=f"✓ {record['member_name']}",
                    font=ctk.CTkFont(size=13, weight="bold"),
                    text_color=SUCCESS
                ).pack(side="left", padx=10, pady=8)
                
                ctk.CTkLabel(
                    item_frame,
                    text=record['check_in_time'],
                    font=ctk.CTkFont(size=12),
                    text_color=TEXT_MUTED
                ).pack(side="right", padx=10, pady=8)
        else:
            ctk.CTkLabel(
                attendance_list,
                text="No check-ins yet today",
                font=ctk.CTkFont(size=14),
                text_color=TEXT_MUTED
            ).pack(pady=30)
    
    def create_stat_card(self, parent, col, icon, title, value, color, wide=False):
        """Create a statistics card with gray theme"""
        card = ctk.CTkFrame(parent, fg_color=BG_SECONDARY, corner_radius=RADIUS_MD)
        card.grid(row=0, column=col, padx=5, pady=5, sticky="ew", columnspan=2 if wide else 1)
        
        # Icon
        ctk.CTkLabel(
            card,
            text=icon,
            font=ctk.CTkFont(size=36)
        ).pack(pady=(20, 5))
        
        # Value
        ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=color
        ).pack(pady=5)
        
        # Title
        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=14),
            text_color=TEXT_MUTED
        ).pack(pady=(0, 20))
        
    def refresh(self):
        """Refresh dashboard data"""
        # Destroy and recreate widgets
        for widget in self.winfo_children():
            widget.destroy()
        self.create_widgets()
