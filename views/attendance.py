"""
Attendance View for Horsepower Gym Management System
Handles member check-ins with phone verification and validation
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import database as db
from utils import (
    format_date, format_currency, get_remaining_days, is_membership_valid, 
    validate_phone, get_membership_status, FEE_MAP, calculate_pending_fee, TRAINERS,
    load_member_photo_with_badge, create_default_avatar
)
from ui_theme import (
    BG_PRIMARY, BG_SECONDARY, BG_TERTIARY, BG_HOVER,
    ACCENT_GOLD, ACCENT_GOLD_HOVER, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    SUCCESS, SUCCESS_DARK, ERROR, ERROR_DARK, WARNING, INFO, INFO_DARK,
    BORDER_COLOR, TABLE_ROW_ODD, TABLE_ROW_EVEN
)


class AttendanceView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=BG_PRIMARY)
        # Store image references to prevent garbage collection
        self._photo_images = {}
        self.create_widgets()
        
    def create_widgets(self):
        # Main container
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_columnconfigure(1, weight=2)
        main_container.grid_rowconfigure(0, weight=1)
        
        # Left Panel - Check-in
        self.create_checkin_panel(main_container)
        
        # Right Panel - Today's Attendance
        self.create_attendance_panel(main_container)
        
    def create_checkin_panel(self, parent):
        """Create the check-in panel with phone verification"""
        checkin_frame = ctk.CTkFrame(parent, fg_color=BG_SECONDARY, corner_radius=10)
        checkin_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Header
        ctk.CTkLabel(
            checkin_frame,
            text="✓ Member Check-In",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=ACCENT_GOLD
        ).pack(anchor="w", padx=20, pady=(20, 15))
        
        # Current time
        time_frame = ctk.CTkFrame(checkin_frame, fg_color=BG_TERTIARY, corner_radius=8)
        time_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            time_frame,
            text="📅 " + datetime.now().strftime('%d-%b-%Y'),
            font=ctk.CTkFont(size=16),
            text_color=TEXT_PRIMARY
        ).pack(side="left", padx=15, pady=10)
        
        self.time_label = ctk.CTkLabel(
            time_frame,
            text="⏰ " + datetime.now().strftime('%I:%M:%S %p'),
            font=ctk.CTkFont(size=16),
            text_color=ACCENT_GOLD
        )
        self.time_label.pack(side="right", padx=15, pady=10)
        self.update_time()
        
        # Phone verification section
        phone_frame = ctk.CTkFrame(checkin_frame, fg_color=BG_TERTIARY, corner_radius=8)
        phone_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            phone_frame,
            text="📱 Quick Check-In by Phone",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=ACCENT_GOLD
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        phone_input_row = ctk.CTkFrame(phone_frame, fg_color="transparent")
        phone_input_row.pack(fill="x", padx=15, pady=(0, 10))
        
        self.phone_checkin_var = ctk.StringVar()
        phone_entry = ctk.CTkEntry(
            phone_input_row,
            textvariable=self.phone_checkin_var,
            placeholder_text="Enter phone number...",
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color=BG_HOVER,
            border_color=BORDER_COLOR
        )
        phone_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        phone_entry.bind("<Return>", lambda e: self.verify_and_checkin())
        
        ctk.CTkButton(
            phone_input_row,
            text="✓ Verify & Check-In",
            command=self.verify_and_checkin,
            fg_color=SUCCESS,
            hover_color=SUCCESS_DARK,
            height=40,
            width=140,
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="right")
        
        # Divider
        ctk.CTkLabel(
            checkin_frame,
            text="─── OR Search by Name ───",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_MUTED
        ).pack(pady=5)
        
        # Search member
        search_frame = ctk.CTkFrame(checkin_frame, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(
            search_frame,
            text="Search Member",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_MUTED
        ).pack(anchor="w")
        
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self.on_search)
        
        ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            placeholder_text="🔍 Enter name or phone number...",
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color=BG_TERTIARY,
            border_color=BORDER_COLOR
        ).pack(fill="x", pady=(5, 0))
        
        # Search results
        self.search_results = ctk.CTkScrollableFrame(checkin_frame, fg_color=BG_TERTIARY, corner_radius=8, height=250)
        self.search_results.pack(fill="x", padx=20, pady=10)
        
        # Selected member info
        self.member_info_frame = ctk.CTkFrame(checkin_frame, fg_color=BG_TERTIARY, corner_radius=8)
        self.member_info_frame.pack(fill="x", padx=20, pady=10)
        
        self.member_info_label = ctk.CTkLabel(
            self.member_info_frame,
            text="Select a member to check in",
            font=ctk.CTkFont(size=14),
            text_color=TEXT_MUTED
        )
        self.member_info_label.pack(pady=20)
        
        # Trainer selection (optional)
        trainer_frame = ctk.CTkFrame(checkin_frame, fg_color="transparent")
        trainer_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            trainer_frame,
            text="With Trainer (Optional)",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_MUTED
        ).pack(anchor="w")
        
        self.trainer_var = ctk.StringVar(value="None")
        ctk.CTkComboBox(
            trainer_frame,
            variable=self.trainer_var,
            values=["None"] + TRAINERS,
            height=40,
            fg_color=BG_TERTIARY,
            border_color=BORDER_COLOR,
            button_color=ACCENT_GOLD,
            button_hover_color=ACCENT_GOLD_HOVER,
            dropdown_fg_color=BG_TERTIARY
        ).pack(fill="x", pady=(5, 0))
        
        # Check-in button
        self.checkin_btn = ctk.CTkButton(
            checkin_frame,
            text="✓ CHECK IN",
            command=self.do_checkin,
            fg_color=SUCCESS,
            hover_color=SUCCESS_DARK,
            height=50,
            font=ctk.CTkFont(size=18, weight="bold"),
            state="disabled"
        )
        self.checkin_btn.pack(fill="x", padx=20, pady=20)
        
        self.selected_member = None
        
    def create_attendance_panel(self, parent):
        """Create today's attendance panel"""
        attendance_frame = ctk.CTkFrame(parent, fg_color=BG_SECONDARY, corner_radius=10)
        attendance_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        # Header with filters
        header_frame = ctk.CTkFrame(attendance_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(
            header_frame,
            text="📋 Today's Attendance",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=ACCENT_GOLD
        ).pack(side="left")
        
        # Trainer filter
        filter_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        filter_frame.pack(side="right")
        
        ctk.CTkLabel(
            filter_frame,
            text="Filter by Trainer:",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_MUTED
        ).pack(side="left", padx=5)
        
        self.filter_var = ctk.StringVar(value="All")
        filter_combo = ctk.CTkComboBox(
            filter_frame,
            variable=self.filter_var,
            values=["All"] + TRAINERS,
            width=120,
            height=30,
            fg_color=BG_TERTIARY,
            border_color=BORDER_COLOR,
            button_color=ACCENT_GOLD,
            button_hover_color=ACCENT_GOLD_HOVER,
            dropdown_fg_color=BG_TERTIARY,
            command=self.on_filter_change
        )
        filter_combo.pack(side="left", padx=5)
        
        ctk.CTkButton(
            filter_frame,
            text="🔄",
            width=35,
            height=30,
            command=self.load_attendance,
            fg_color=INFO,
            hover_color=INFO_DARK
        ).pack(side="left", padx=5)
        
        # Stats
        stats_frame = ctk.CTkFrame(attendance_frame, fg_color=BG_TERTIARY, corner_radius=8)
        stats_frame.pack(fill="x", padx=20, pady=10)
        
        self.stats_label = ctk.CTkLabel(
            stats_frame,
            text=f"Total Check-ins Today: {db.get_today_attendance_count()}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=SUCCESS
        )
        self.stats_label.pack(pady=10)
        
        # Column headers
        headers_frame = ctk.CTkFrame(attendance_frame, fg_color=BG_TERTIARY, corner_radius=5)
        headers_frame.pack(fill="x", padx=20, pady=(10, 5))
        
        headers = ["#", "Member Name", "Phone", "Time", "Trainer"]
        widths = [40, 180, 120, 100, 100]
        
        for header, width in zip(headers, widths):
            ctk.CTkLabel(
                headers_frame,
                text=header,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=ACCENT_GOLD,
                width=width
            ).pack(side="left", padx=5, pady=8)
        
        # Attendance list
        self.attendance_list = ctk.CTkScrollableFrame(attendance_frame, fg_color=BG_TERTIARY, corner_radius=8)
        self.attendance_list.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.load_attendance()
    
    def update_time(self):
        """Update the time display"""
        self.time_label.configure(text="⏰ " + datetime.now().strftime('%I:%M:%S %p'))
        self.after(1000, self.update_time)
    
    def verify_and_checkin(self):
        """Verify phone number and perform check-in"""
        phone = self.phone_checkin_var.get().strip().replace(" ", "").replace("-", "")
        
        if not validate_phone(phone):
            messagebox.showerror("Invalid Phone", "Please enter a valid 10-digit phone number")
            return
        
        # Get member by phone
        member = db.get_member_by_phone(phone)
        
        if not member:
            messagebox.showerror("Member Not Found", 
                "No member found with this phone number.\n"
                "Please check the number or register as new member.")
            return
        
        # Check if already checked in today
        if db.check_already_checked_in(member['id']):
            messagebox.showwarning("Already Checked In", 
                f"{member['name']} has already checked in today!")
            self.phone_checkin_var.set("")
            return
        
        # Validate membership
        if not is_membership_valid(member['end_date']):
            # Calculate pending fee for display
            amount_paid = member['amount_paid'] or 0 if 'amount_paid' in member.keys() else 0
            pending = FEE_MAP.get(member['membership_type'], 1200)
            
            messagebox.showerror("Membership Expired", 
                f"⚠️ Cannot Check In!\n\n"
                f"Member: {member['name']}\n"
                f"Phone: {member['phone']}\n"
                f"Membership Expired: {format_date(member['end_date'])}\n\n"
                f"Renewal Fee: {format_currency(pending)}\n\n"
                f"Please renew membership before check-in.")
            self.phone_checkin_var.set("")
            return
        
        # Check for pending payments (warning only, still allow check-in)
        if member['payment_status'] == 'Pending':
            amount_paid = member['amount_paid'] or 0 if 'amount_paid' in member.keys() else 0
            pending = calculate_pending_fee(member['membership_type'], amount_paid)
            
            if pending > 0:
                if not messagebox.askyesno("Pending Payment", 
                    f"⚠️ Pending Fee Alert!\n\n"
                    f"Member: {member['name']}\n"
                    f"Pending Amount: {format_currency(pending)}\n\n"
                    f"Continue with check-in anyway?"):
                    self.phone_checkin_var.set("")
                    return
        
        # Perform check-in
        remaining = get_remaining_days(member['end_date'])
        db.add_attendance(member['id'], None)
        
        messagebox.showinfo("Check-In Success", 
            f"✓ Check-in Successful!\n\n"
            f"Member: {member['name']}\n"
            f"Time: {datetime.now().strftime('%I:%M %p')}\n"
            f"Membership: {remaining} days remaining")
        
        self.phone_checkin_var.set("")
        self.load_attendance()
    
    def on_search(self, *args):
        """Search for members"""
        for widget in self.search_results.winfo_children():
            widget.destroy()
            
        query = self.search_var.get().strip()
        if not query:
            return
            
        members = db.search_members(query)
        
        for member in members[:8]:  # Show max 8 results
            is_valid = is_membership_valid(member['end_date'])
            remaining = get_remaining_days(member['end_date'])
            already_checked = db.check_already_checked_in(member['id'])
            has_pending = member['payment_status'] == 'Pending'
            
            result_frame = ctk.CTkFrame(self.search_results, fg_color=BG_HOVER, corner_radius=5)
            result_frame.pack(fill="x", pady=2)
            
            # Status indicator
            if already_checked:
                status_color = INFO
                status_text = "✓ Already checked in"
            elif not is_valid:
                status_color = ERROR
                status_text = "⚠️ EXPIRED"
            elif has_pending:
                status_color = WARNING
                status_text = f"⚠️ {remaining} days | PENDING FEE"
            else:
                status_color = SUCCESS
                status_text = f"✓ {remaining} days left"
            
            info_frame = ctk.CTkFrame(result_frame, fg_color="transparent")
            info_frame.pack(side="left", fill="x", expand=True, padx=10, pady=8)
            
            ctk.CTkLabel(
                info_frame,
                text=member['name'],
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=TEXT_PRIMARY
            ).pack(anchor="w")
            
            ctk.CTkLabel(
                info_frame,
                text=f"{member['phone']} | {status_text}",
                font=ctk.CTkFont(size=11),
                text_color=status_color
            ).pack(anchor="w")
            
            # Select button - disabled for already checked in or expired
            btn_state = "disabled" if already_checked or not is_valid else "normal"
            btn_color = BORDER_COLOR if already_checked or not is_valid else SUCCESS
            
            ctk.CTkButton(
                result_frame,
                text="Select",
                width=70,
                height=30,
                fg_color=btn_color,
                hover_color=SUCCESS_DARK if btn_state == "normal" else BORDER_COLOR,
                state=btn_state,
                command=lambda m=member: self.select_member(m)
            ).pack(side="right", padx=10, pady=8)
    
    def select_member(self, member):
        """Select a member for check-in with photo status display"""
        self.selected_member = member
        
        # Update member info display
        for widget in self.member_info_frame.winfo_children():
            widget.destroy()
        
        # Calculate pending fee for badge
        amount_paid = member['amount_paid'] or 0 if 'amount_paid' in member.keys() else 0
        pending_fee = calculate_pending_fee(member['membership_type'], amount_paid)
        
        info_container = ctk.CTkFrame(self.member_info_frame, fg_color="transparent")
        info_container.pack(fill="x", padx=15, pady=15)
        
        # ========== MEMBER PHOTO WITH STATUS ==========
        photo_path = member['photo_path'] if 'photo_path' in member.keys() else None
        
        # Load photo with badge (dark overlay + PENDING if fee > 0, clean + PAID if 0)
        self._photo_images['selected'] = load_member_photo_with_badge(photo_path, pending_fee, (120, 120))
        self._photo_images['selected_ctk'] = ctk.CTkImage(
            light_image=self._photo_images['selected'],
            dark_image=self._photo_images['selected'],
            size=(120, 120)
        )
        
        ctk.CTkLabel(
            info_container,
            image=self._photo_images['selected_ctk'],
            text=""
        ).pack(pady=(0, 10))
        # ========== END PHOTO ==========
        
        ctk.CTkLabel(
            info_container,
            text="Selected Member:",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_MUTED
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            info_container,
            text=member['name'],
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w", pady=(5, 0))
        
        ctk.CTkLabel(
            info_container,
            text=f"📞 {member['phone']}",
            font=ctk.CTkFont(size=13),
            text_color=TEXT_MUTED
        ).pack(anchor="w")
        
        remaining = get_remaining_days(member['end_date'])
        ctk.CTkLabel(
            info_container,
            text=f"📅 Membership: {remaining} days remaining",
            font=ctk.CTkFont(size=13),
            text_color=SUCCESS
        ).pack(anchor="w")
        
        # Check for active personal training
        training = db.get_active_training(member['id'])
        if training:
            training_remaining = get_remaining_days(training['end_date'])
            ctk.CTkLabel(
                info_container,
                text=f"🏃 Training with {training['trainer_name']}: {training_remaining} days",
                font=ctk.CTkFont(size=13),
                text_color=WARNING
            ).pack(anchor="w")
        
        self.checkin_btn.configure(state="normal")
        self.search_var.set("")
        
        for widget in self.search_results.winfo_children():
            widget.destroy()
    
    def do_checkin(self):
        """Perform check-in"""
        if not self.selected_member:
            messagebox.showerror("Error", "Please select a member")
            return
        
        # Final validation - membership expiry
        if not is_membership_valid(self.selected_member['end_date']):
            pending = FEE_MAP.get(self.selected_member['membership_type'], 1200)
            messagebox.showerror("Membership Expired", 
                f"⚠️ Cannot Check In!\n\n"
                f"Member: {self.selected_member['name']}\n"
                f"Membership Expired: {format_date(self.selected_member['end_date'])}\n\n"
                f"Renewal Fee: {format_currency(pending)}\n\n"
                f"Please renew membership before check-in.")
            return
        
        if db.check_already_checked_in(self.selected_member['id']):
            messagebox.showwarning("Warning", "Member has already checked in today!")
            return
        
        # Check for pending payments (warning, still allow)
        if self.selected_member['payment_status'] == 'Pending':
            amount_paid = self.selected_member['amount_paid'] or 0 if 'amount_paid' in self.selected_member.keys() else 0
            pending = calculate_pending_fee(self.selected_member['membership_type'], amount_paid)
            
            if pending > 0:
                if not messagebox.askyesno("Pending Payment", 
                    f"⚠️ Pending Fee Alert!\n\n"
                    f"Member: {self.selected_member['name']}\n"
                    f"Pending Amount: {format_currency(pending)}\n\n"
                    f"Continue with check-in anyway?"):
                    return
        
        # Check personal training validity if with trainer
        trainer = self.trainer_var.get()
        if trainer != "None":
            training = db.get_active_training(self.selected_member['id'])
            if not training:
                if not messagebox.askyesno("Warning", 
                    f"No active personal training found for this member.\n"
                    f"Continue check-in without trainer?"):
                    return
                trainer = None
            elif not is_membership_valid(training['end_date']):
                if not messagebox.askyesno("Warning",
                    f"Personal training has expired!\n"
                    f"Continue check-in without trainer?"):
                    return
                trainer = None
        else:
            trainer = None
        
        # Do check-in
        db.add_attendance(self.selected_member['id'], trainer)
        
        remaining = get_remaining_days(self.selected_member['end_date'])
        messagebox.showinfo("Success", 
            f"✓ Check-in successful!\n\n"
            f"Member: {self.selected_member['name']}\n"
            f"Time: {datetime.now().strftime('%I:%M %p')}\n"
            f"Membership: {remaining} days remaining"
        )
        
        # Reset form
        self.selected_member = None
        self.checkin_btn.configure(state="disabled")
        self.trainer_var.set("None")
        
        for widget in self.member_info_frame.winfo_children():
            widget.destroy()
        self.member_info_label = ctk.CTkLabel(
            self.member_info_frame,
            text="Select a member to check in",
            font=ctk.CTkFont(size=14),
            text_color=TEXT_MUTED
        )
        self.member_info_label.pack(pady=20)
        
        self.load_attendance()
    
    def on_filter_change(self, value):
        """Handle trainer filter change"""
        self.load_attendance()
    
    def load_attendance(self):
        """Load today's attendance"""
        for widget in self.attendance_list.winfo_children():
            widget.destroy()
        
        filter_trainer = self.filter_var.get()
        
        if filter_trainer == "All":
            attendance = db.get_today_attendance()
        else:
            attendance = db.get_attendance_by_trainer(filter_trainer)
            # Filter to today only
            from datetime import date
            today = date.today().strftime('%Y-%m-%d')
            attendance = [a for a in attendance if a['date'] == today]
        
        self.stats_label.configure(text=f"Total Check-ins Today: {len(attendance)}")
        
        if not attendance:
            ctk.CTkLabel(
                self.attendance_list,
                text="No check-ins yet today",
                font=ctk.CTkFont(size=14),
                text_color=TEXT_MUTED
            ).pack(pady=50)
            return
        
        for i, record in enumerate(attendance):
            row_bg = TABLE_ROW_ODD if i % 2 == 0 else TABLE_ROW_EVEN
            row = ctk.CTkFrame(self.attendance_list, fg_color=row_bg, corner_radius=5)
            row.pack(fill="x", pady=2)
            
            # Number
            ctk.CTkLabel(
                row,
                text=str(i + 1),
                font=ctk.CTkFont(size=12),
                text_color=TEXT_MUTED,
                width=40
            ).pack(side="left", padx=5, pady=10)
            
            # Name
            ctk.CTkLabel(
                row,
                text=record['member_name'],
                font=ctk.CTkFont(size=12),
                text_color=TEXT_PRIMARY,
                width=180,
                anchor="w"
            ).pack(side="left", padx=5, pady=10)
            
            # Phone
            ctk.CTkLabel(
                row,
                text=record['member_phone'],
                font=ctk.CTkFont(size=12),
                text_color=TEXT_MUTED,
                width=120,
                anchor="w"
            ).pack(side="left", padx=5, pady=10)
            
            # Time
            ctk.CTkLabel(
                row,
                text=record['check_in_time'],
                font=ctk.CTkFont(size=12),
                text_color=SUCCESS,
                width=100,
                anchor="w"
            ).pack(side="left", padx=5, pady=10)
            
            # Trainer
            ctk.CTkLabel(
                row,
                text=record['trainer_name'] or "-",
                font=ctk.CTkFont(size=12),
                text_color=WARNING if record['trainer_name'] else TEXT_MUTED,
                width=100,
                anchor="w"
            ).pack(side="left", padx=5, pady=10)
    
    def refresh(self):
        """Refresh the view"""
        self.load_attendance()
