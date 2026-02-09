"""
Personal Training View for Horsepower Gym Management System
Handles trainer assignments and tracking
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import date
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import database as db
from utils import (
    calculate_training_end_date, format_date, format_currency, 
    get_remaining_days, is_membership_valid, TRAINERS
)
from ui_theme import (
    BG_PRIMARY, BG_SECONDARY, BG_TERTIARY, BG_HOVER,
    ACCENT_GOLD, ACCENT_GOLD_HOVER, TEXT_PRIMARY, TEXT_MUTED,
    SUCCESS, SUCCESS_DARK, ERROR, ERROR_DARK, WARNING, INFO, INFO_DARK,
    BORDER_COLOR, TABLE_ROW_ODD, TABLE_ROW_EVEN
)


class TrainingView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=BG_PRIMARY)
        self.selected_training_id = None
        self.selected_member_id = None
        self.create_widgets()
        
    def create_widgets(self):
        # Main container
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_columnconfigure(1, weight=2)
        main_container.grid_rowconfigure(0, weight=1)
        
        # Left Panel - Training Form
        self.create_form_panel(main_container)
        
        # Right Panel - Training List
        self.create_list_panel(main_container)
        
    def create_form_panel(self, parent):
        """Create the training assignment form"""
        form_frame = ctk.CTkFrame(parent, fg_color=BG_SECONDARY, corner_radius=10)
        form_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Header
        ctk.CTkLabel(
            form_frame,
            text="🏃 Assign Personal Training",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=ACCENT_GOLD
        ).pack(anchor="w", padx=20, pady=(20, 15))
        
        # Form content
        form_scroll = ctk.CTkScrollableFrame(form_frame, fg_color="transparent")
        form_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        # Member selection
        member_frame = ctk.CTkFrame(form_scroll, fg_color="transparent")
        member_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            member_frame,
            text="Select Member *",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_MUTED
        ).pack(anchor="w")
        
        # Member search
        self.member_search_var = ctk.StringVar()
        self.member_search_var.trace_add("write", self.on_member_search)
        
        ctk.CTkEntry(
            member_frame,
            textvariable=self.member_search_var,
            placeholder_text="🔍 Search member by name or phone...",
            height=35,
            fg_color=BG_TERTIARY,
            border_color=BORDER_COLOR
        ).pack(fill="x", pady=(2, 5))
        
        # Member results list
        self.member_results = ctk.CTkScrollableFrame(member_frame, fg_color=BG_TERTIARY, height=100)
        self.member_results.pack(fill="x", pady=(0, 5))
        
        # Selected member display
        self.selected_member_label = ctk.CTkLabel(
            member_frame,
            text="No member selected",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_MUTED
        )
        self.selected_member_label.pack(anchor="w", pady=5)
        
        # Form fields
        self.trainer_var = ctk.StringVar(value=TRAINERS[0])
        self.duration_var = ctk.StringVar(value="1")
        self.fee_var = ctk.StringVar(value="2000")
        self.start_date_var = ctk.StringVar(value=date.today().strftime('%Y-%m-%d'))
        self.end_date_var = ctk.StringVar()
        self.status_var = ctk.StringVar(value="Active")
        
        fields = [
            ("Trainer *", self.trainer_var, "combo", TRAINERS),
            ("Duration (Months) *", self.duration_var, "combo", ["1", "2", "3", "6", "12"]),
            ("Fee (₹) *", self.fee_var, "entry"),
            ("Start Date (YYYY-MM-DD) *", self.start_date_var, "entry"),
            ("End Date", self.end_date_var, "readonly"),
            ("Status", self.status_var, "combo", ["Active", "Completed", "Cancelled"]),
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
                ctk.CTkEntry(
                    field_frame,
                    textvariable=var,
                    height=35,
                    fg_color=BG_TERTIARY,
                    border_color=BORDER_COLOR,
                    state="readonly"
                ).pack(fill="x", pady=(2, 0))
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
        
        # Bind changes
        self.duration_var.trace_add("write", self.on_duration_change)
        self.start_date_var.trace_add("write", self.on_date_change)
        self.calculate_end_date()
        
        # Buttons
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkButton(
            btn_frame,
            text="💾 Save Training",
            command=self.save_training,
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
            text="🗑️ Delete Training",
            command=self.delete_training,
            fg_color=ERROR,
            hover_color=ERROR_DARK,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(fill="x", pady=2)
        
    def create_list_panel(self, parent):
        """Create the training list panel"""
        list_frame = ctk.CTkFrame(parent, fg_color=BG_SECONDARY, corner_radius=10)
        list_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        # Header
        header_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(
            header_frame,
            text="📋 Personal Training Records",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=ACCENT_GOLD
        ).pack(side="left")
        
        ctk.CTkButton(
            header_frame,
            text="🔄 Refresh",
            width=100,
            height=35,
            command=self.load_training,
            fg_color=INFO,
            hover_color=INFO_DARK
        ).pack(side="right")
        
        # Column headers
        headers_frame = ctk.CTkFrame(list_frame, fg_color=BG_TERTIARY, corner_radius=5)
        headers_frame.pack(fill="x", padx=20, pady=(10, 5))
        
        headers = ["Member", "Trainer", "Duration", "End Date", "Days Left", "Status"]
        widths = [140, 80, 70, 90, 70, 80]
        
        for header, width in zip(headers, widths):
            ctk.CTkLabel(
                headers_frame,
                text=header,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=ACCENT_GOLD,
                width=width
            ).pack(side="left", padx=5, pady=8)
        
        # Training list
        self.training_list = ctk.CTkScrollableFrame(list_frame, fg_color=BG_TERTIARY, corner_radius=8)
        self.training_list.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.load_training()
        
    def load_training(self):
        """Load training records"""
        for widget in self.training_list.winfo_children():
            widget.destroy()
            
        training_records = db.get_all_training()
        
        if not training_records:
            ctk.CTkLabel(
                self.training_list,
                text="No personal training records found",
                font=ctk.CTkFont(size=14),
                text_color=TEXT_MUTED
            ).pack(pady=50)
            return
            
        for i, record in enumerate(training_records):
            is_valid = is_membership_valid(record['end_date'])
            remaining = get_remaining_days(record['end_date'])
            
            row_bg = TABLE_ROW_ODD if i % 2 == 0 else TABLE_ROW_EVEN
            if not is_valid and record['status'] == 'Active':
                row_bg = "#4a1a1a"  # Dark red for expired
            
            row = ctk.CTkFrame(self.training_list, fg_color=row_bg, corner_radius=5)
            row.pack(fill="x", pady=2)
            row.bind("<Button-1>", lambda e, r=record: self.select_training(r))
            
            def make_clickable(widget, record):
                widget.bind("<Button-1>", lambda e, r=record: self.select_training(r))
            
            # Member name
            name_label = ctk.CTkLabel(
                row,
                text=record['member_name'][:15] + "..." if len(record['member_name']) > 15 else record['member_name'],
                font=ctk.CTkFont(size=12),
                text_color=TEXT_PRIMARY,
                width=140,
                anchor="w"
            )
            name_label.pack(side="left", padx=5, pady=10)
            make_clickable(name_label, record)
            
            # Trainer
            trainer_label = ctk.CTkLabel(
                row,
                text=record['trainer_name'],
                font=ctk.CTkFont(size=12),
                text_color=TEXT_MUTED,
                width=80,
                anchor="w"
            )
            trainer_label.pack(side="left", padx=5, pady=10)
            make_clickable(trainer_label, record)
            
            # Duration
            duration_label = ctk.CTkLabel(
                row,
                text=f"{record['plan_duration']} month(s)",
                font=ctk.CTkFont(size=12),
                text_color=TEXT_MUTED,
                width=70,
                anchor="w"
            )
            duration_label.pack(side="left", padx=5, pady=10)
            make_clickable(duration_label, record)
            
            # End Date
            end_label = ctk.CTkLabel(
                row,
                text=format_date(record['end_date']),
                font=ctk.CTkFont(size=12),
                text_color=TEXT_MUTED,
                width=90,
                anchor="w"
            )
            end_label.pack(side="left", padx=5, pady=10)
            make_clickable(end_label, record)
            
            # Days Left
            if record['status'] == 'Active':
                days_color = SUCCESS if remaining > 7 else WARNING if remaining > 0 else ERROR
                days_text = f"{remaining} days" if is_valid else "EXPIRED"
            else:
                days_color = TEXT_MUTED
                days_text = "-"
            
            days_label = ctk.CTkLabel(
                row,
                text=days_text,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=days_color,
                width=70,
                anchor="w"
            )
            days_label.pack(side="left", padx=5, pady=10)
            make_clickable(days_label, record)
            
            # Status
            status_colors = {"Active": SUCCESS, "Completed": INFO, "Cancelled": ERROR}
            status_label = ctk.CTkLabel(
                row,
                text=record['status'],
                font=ctk.CTkFont(size=12),
                text_color=status_colors.get(record['status'], TEXT_MUTED),
                width=80,
                anchor="w"
            )
            status_label.pack(side="left", padx=5, pady=10)
            make_clickable(status_label, record)
    
    def on_member_search(self, *args):
        """Search members"""
        for widget in self.member_results.winfo_children():
            widget.destroy()
            
        query = self.member_search_var.get().strip()
        if not query:
            return
            
        members = db.search_members(query)
        
        for member in members[:5]:  # Show max 5 results
            btn = ctk.CTkButton(
                self.member_results,
                text=f"{member['name']} - {member['phone']}",
                fg_color="transparent",
                text_color=TEXT_PRIMARY,
                hover_color=BG_HOVER,
                anchor="w",
                command=lambda m=member: self.select_member(m)
            )
            btn.pack(fill="x", pady=1)
    
    def select_member(self, member):
        """Select a member for training"""
        self.selected_member_id = member['id']
        self.selected_member_label.configure(
            text=f"✓ {member['name']} ({member['phone']})",
            text_color=SUCCESS
        )
        self.member_search_var.set("")
        for widget in self.member_results.winfo_children():
            widget.destroy()
    
    def select_training(self, record):
        """Select a training record"""
        self.selected_training_id = record['id']
        self.selected_member_id = record['member_id']
        self.selected_member_label.configure(
            text=f"✓ {record['member_name']} ({record['member_phone']})",
            text_color=SUCCESS
        )
        self.trainer_var.set(record['trainer_name'])
        self.duration_var.set(str(record['plan_duration']))
        self.fee_var.set(str(record['fee']))
        self.start_date_var.set(record['start_date'])
        self.end_date_var.set(record['end_date'])
        self.status_var.set(record['status'])
    
    def save_training(self):
        """Save or update training record"""
        if not self.selected_member_id:
            messagebox.showerror("Error", "Please select a member")
            return
        
        try:
            fee = float(self.fee_var.get())
            duration = int(self.duration_var.get())
        except:
            messagebox.showerror("Error", "Please enter valid fee and duration")
            return
        
        start_date = self.start_date_var.get()
        end_date = calculate_training_end_date(start_date, duration)
        
        if self.selected_training_id:
            db.update_personal_training(
                self.selected_training_id,
                self.trainer_var.get(),
                duration,
                fee,
                start_date,
                end_date,
                self.status_var.get()
            )
            messagebox.showinfo("Success", "Training record updated!")
        else:
            db.add_personal_training(
                self.selected_member_id,
                self.trainer_var.get(),
                duration,
                fee,
                start_date,
                end_date
            )
            messagebox.showinfo("Success", "Training assigned successfully!")
        
        self.clear_form()
        self.load_training()
    
    def delete_training(self):
        """Delete selected training record"""
        if not self.selected_training_id:
            messagebox.showwarning("Warning", "Please select a training record to delete")
            return
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this training record?"):
            db.delete_personal_training(self.selected_training_id)
            messagebox.showinfo("Success", "Training record deleted!")
            self.clear_form()
            self.load_training()
    
    def clear_form(self):
        """Clear form"""
        self.selected_training_id = None
        self.selected_member_id = None
        self.selected_member_label.configure(text="No member selected", text_color=TEXT_MUTED)
        self.member_search_var.set("")
        self.trainer_var.set(TRAINERS[0])
        self.duration_var.set("1")
        self.fee_var.set("2000")
        self.start_date_var.set(date.today().strftime('%Y-%m-%d'))
        self.status_var.set("Active")
        self.calculate_end_date()
    
    def on_duration_change(self, *args):
        self.calculate_end_date()
    
    def on_date_change(self, *args):
        self.calculate_end_date()
    
    def calculate_end_date(self):
        try:
            duration = int(self.duration_var.get())
            end = calculate_training_end_date(self.start_date_var.get(), duration)
            self.end_date_var.set(end)
        except:
            pass
    
    def refresh(self):
        self.load_training()
