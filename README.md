# 🏋️ Horsepower Gym Management System

A professional Windows desktop application for comprehensive gym management.

## 📋 About

**Gym Name:** Horsepower Gym  
**Location:** Koodapakkam Road, near Lakshmi Narayana Medical College, Pondicherry  
**Owner:** Manikandan  
**Trainers:** Suriya, Ganesh

## ✨ Features

### 1. Member Management
- Add, edit, and delete gym members
- Track membership details (Monthly/Quarterly/Yearly)
- Automatic end date calculation
- Payment status tracking (Paid/Pending)
- Expired members highlighted in red
- Search by name or phone number

### 2. Personal Training Management
- Assign trainers (Suriya or Ganesh) to members
- Set training duration and fees
- Track validity period
- Alert when training expires

### 3. Attendance System
- Daily member check-in
- Validates membership before allowing entry
- Validates personal training if checking in with trainer
- Real-time clock display
- Filter attendance by trainer
- Complete attendance history

### 4. Dashboard
- Total members count
- Active vs expired memberships
- Today's attendance
- Monthly revenue summary
- Gym information display

### 5. Security
- Admin login system
- Default credentials: `admin` / `admin123`

## 🎨 Design
- Professional dark theme (black & gold)
- Modern, clean interface
- Fitness-style icons
- Responsive layout

## 🚀 Quick Start

### Option 1: Run from Source (Development)

1. **Install Python 3.8+** from https://python.org

2. **Install dependencies:**
   ```powershell
   cd C:\Users\kalai\horsepower_gym
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```powershell
   python main.py
   ```

### Option 2: Build Executable (.exe)

1. **Install dependencies:**
   ```powershell
   cd C:\Users\kalai\horsepower_gym
   pip install -r requirements.txt
   ```

2. **Build the .exe:**
   ```powershell
   python build.py
   ```

3. **Run the executable:**
   - Navigate to: `dist\HorsepowerGym\`
   - Double-click: `HorsepowerGym.exe`

## 📁 Project Structure

```
horsepower_gym/
├── main.py              # Application entry point
├── database.py          # SQLite database operations
├── utils.py             # Utility functions & constants
├── requirements.txt     # Python dependencies
├── build.py             # PyInstaller build script
├── README.md            # This file
├── views/
│   ├── __init__.py
│   ├── login.py         # Admin login screen
│   ├── dashboard.py     # Dashboard with stats
│   ├── members.py       # Member management
│   ├── training.py      # Personal training
│   └── attendance.py    # Attendance system
└── assets/              # Images & icons (optional)
```

## 🗄️ Database

The application uses SQLite, stored locally as `horsepower_gym.db`. No external database server required.

### Tables:
- **members** - Member information and membership details
- **personal_training** - Training assignments
- **attendance** - Daily check-in records
- **admin** - Admin credentials

## 🔐 Default Login

- **Username:** admin
- **Password:** admin123

⚠️ Please change the password after first login for security.

## 📋 Requirements

- Windows 10/11
- Python 3.8 or higher
- 100MB disk space
- 4GB RAM (recommended)

## 🛠️ Dependencies

- customtkinter >= 5.2.0
- pillow >= 10.0.0
- pyinstaller >= 6.0.0 (for building .exe)

## 📞 Support

For issues or feature requests, contact the gym management.

---

**Horsepower Gym** - *Power Your Fitness Journey* 🏋️
