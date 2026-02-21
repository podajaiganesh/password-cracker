# SECURENETRA - Offensive AI Simulator

A comprehensive cybersecurity education and awareness training platform built with Python and CustomTkinter.

## Features

### 🔐 Password Attack Simulator
- Dictionary, Brute Force, and Hybrid attacks
- Supports MD5, SHA1, SHA256, SHA512, bcrypt, PBKDF2
- Real-time speed metrics and progress tracking

### 🎣 Social Engineering Simulator
- Phishing email generator
- Email risk analyzer with 0-100 scoring
- Awareness training scenarios

### 🌐 Domain Spoof Detector
- SSL certificate validation
- DNS/IP lookup with response time
- Levenshtein distance matching against 50+ brands
- Homograph character detection
- High-risk TLD flagging

### 📚 Security Awareness Training
- 8 interactive lessons (Password Hygiene, Phishing, 2FA, etc.)
- 20-question security quiz with grading
- 30+ security tips with category filtering
- Daily tip highlights

### 📊 Risk & Analytics Dashboard
- Real-time metrics (attacks, crack rate, phishing checks)
- Visual charts (bar chart, donut chart)
- Detailed reports across all modules
- PDF/JSON export functionality

### 🔑 2FA Authentication System
- Secure login/signup with password strength meter
- 6-digit OTP verification
- Demo mode for testing
- SHA-256 password hashing

## Installation

### Requirements
- Python 3.12+
- CustomTkinter 5.2.2

### Setup

1. Clone the repository:
```bash
git clone https://github.com/podajaiganesh/securenetra.git
cd securenetra
```

2. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install customtkinter
```

4. Run the application:
```bash
python main.py
```

## Usage

1. **First Launch**: Authentication window appears
   - Click "Demo Mode" for quick access
   - Or create an account with OTP verification

2. **Home Screen**: 2x4 grid showing 8 modules
   - Click any ACTIVE module to launch
   - Each module has a HOME button to return

3. **Data Storage**: All activity logged to `securenetra.db`

## Project Structure

```
password-cracker/
├── main.py                        # Entry point
├── home.py                        # Home dashboard (2x4 grid)
├── auth_gui.py                    # 2FA authentication
├── gui.py                         # Password attack simulator
├── social_engineering_gui.py      # Phishing analyzer
├── domain_gui.py                  # Domain spoof detector
├── training_gui.py                # Security training
├── dashboard_gui.py               # Analytics dashboard
├── attacks/                       # Attack algorithms
├── social_engineering/            # Phishing modules
├── utils/                         # Database & session management
└── wordlists/                     # Dictionary files
```

## Color Palette

- Background: `#0a0a0a`
- Surface: `#111111`
- Card: `#141414`
- Accent Colors: Red `#e63946`, Green `#2dc653`, Cyan `#00b4d8`, Amber `#f4a261`
- Font: Courier New (monospace)

## Security Notice

⚠️ **FOR EDUCATIONAL PURPOSES ONLY**

This tool is designed for cybersecurity education and awareness training. Use responsibly and only on systems you own or have explicit permission to test.

## License

MIT License - See LICENSE file for details

## Author

Podajai Ganesh
- GitHub: [@podajaiganesh](https://github.com/podajaiganesh)

## Contributing

Contributions welcome! Please open an issue or submit a pull request.
