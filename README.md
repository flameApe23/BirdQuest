# 🐦 BirdQuest

**Level up your habits, grow your flock!**

BirdQuest is a gamified habit-tracking and productivity app designed for students. Complete real-life tasks, earn XP, level up, and collect beautiful birds along the way!

![BirdQuest Banner](static/images/favicon.svg)

## ✨ Features

- **📚 Student-Focused Habits**: Pre-built habits relevant to students including study sessions, homework, exercise, reading, and more
- **🔥 Streak Tracking**: Build momentum with daily streaks to stay motivated
- **⭐ XP & Leveling System**: Earn experience points for completing tasks and level up your account
- **🌱 Seeds Currency**: Earn seeds when you level up to spend in the bird shop
- **🐦 Bird Collection**: Collect birds of different rarities from Common to Legendary
- **✨ Shiny Variants**: 1% chance to get a shiny bird with special effects and bonus multipliers
- **📊 Progress Dashboard**: Visual tracking of your habits, XP, and statistics

## 🎮 How It Works

1. **Add Your Habits**: Choose from student-focused habits or create custom tasks
2. **Complete & Earn XP**: Check off habits daily to earn experience points
3. **Level Up & Get Seeds**: Accumulate XP to level up and earn seeds
4. **Collect Amazing Birds**: Spend seeds in the shop to unlock new birds with unique effects

## 🦜 Bird Rarities & Multipliers

| Rarity | Seed Multiplier | Shiny Multiplier | Background Effect |
|--------|-----------------|------------------|-------------------|
| Common | 1.0x | 1.5x | Light gray |
| Uncommon | 1.2x | 1.8x | Light green |
| Rare | 1.5x | 2.3x | Light blue |
| Epic | 1.7x | 2.7x | Light purple |
| Legendary | 2.0x | 4.0x | Light gold |

**Shiny birds** have a 1% chance to appear when purchasing and feature sparkle effects with a golden outline!

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/BirdQuest.git
   cd BirdQuest
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv

   # On Windows
   venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open your browser** and navigate to `http://localhost:5000`

## 📁 Project Structure

```
BirdQuest/
├── app.py                 # Main Flask application
├── models.py              # Database models (alternative structure)
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── static/
│   ├── css/
│   │   ├── style.css      # Main stylesheet
│   │   └── dashboard.css  # Dashboard-specific styles
│   ├── js/
│   │   ├── main.js        # Common JavaScript
│   │   └── dashboard.js   # Dashboard functionality
│   └── images/
│       └── favicon.svg    # App icon
└── templates/
    ├── base.html          # Base template
    ├── home.html          # Landing page
    ├── login.html         # Login page
    ├── register.html      # Registration page
    ├── dashboard.html     # Main dashboard
    └── shop.html          # Bird shop
```

## 🎯 Available Habits

### Study
- Study for 30 minutes (+15 XP)
- Complete homework (+20 XP)
- Read for 20 minutes (+10 XP)
- Review notes (+10 XP)
- Practice flashcards (+10 XP)

### Health
- Exercise for 30 minutes (+15 XP)
- Drink 8 glasses of water (+10 XP)
- Get 8 hours of sleep (+15 XP)
- Eat a healthy meal (+10 XP)
- Meditate for 10 minutes (+10 XP)

### Productivity
- Clean room/desk (+10 XP)
- Plan tomorrow's tasks (+10 XP)
- No social media for 2 hours (+15 XP)
- Attend all classes (+20 XP)

### Social
- Help a classmate (+15 XP)

### Custom
- Create your own habits with custom XP values!

## 🛠️ Technologies Used

- **Backend**: Flask (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: Flask-Login
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Styling**: Custom CSS with CSS Variables

## 📱 Screenshots

### Home Page
The landing page explains the app and its benefits for students.

### Dashboard
Track your habits, view your current bird, and monitor your progress.

### Bird Shop
Browse and purchase birds of different rarities with your earned seeds.

## 🔧 Configuration

The app uses SQLite by default. The database file (`birdquest.db`) is created automatically when you first run the application.

To customize the configuration, you can modify these settings in `app.py`:

```python
app.config["SECRET_KEY"] = "your-secret-key"  # Change for production
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///birdquest.db"
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Designed with students in mind
- Inspired by gamification principles
- Built with ❤️ for productivity

---

**Start your journey today and watch your productivity soar! 🐦✨**