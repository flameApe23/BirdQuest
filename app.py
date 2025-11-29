import os
import random
from datetime import datetime, timedelta

from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import (
    LoginManager,
    UserMixin,
    login_required,
    login_user,
    logout_user,
)
from flask_login import (
    current_user as _current_user,
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

# Configuration for Railway deployment
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", os.urandom(24).hex())
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "sqlite:///birdquest.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Fix for Railway PostgreSQL URL (if using postgres)
if app.config["SQLALCHEMY_DATABASE_URI"].startswith("postgres://"):
    app.config["SQLALCHEMY_DATABASE_URI"] = app.config[
        "SQLALCHEMY_DATABASE_URI"
    ].replace("postgres://", "postgresql://", 1)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Constants
XP_PER_LEVEL = 50
SEEDS_PER_LEVEL = 15
SHINY_CHANCE = 0.01

# Rarity multipliers for seeds
RARITY_MULTIPLIERS = {
    "common": 1.0,
    "common_shiny": 1.5,
    "uncommon": 1.2,
    "uncommon_shiny": 1.8,
    "rare": 1.5,
    "rare_shiny": 2.3,
    "epic": 1.7,
    "epic_shiny": 2.7,
    "legendary": 2.0,
    "legendary_shiny": 4.0,
}

# Bird prices based on rarity
RARITY_PRICES = {
    "common": 10,
    "uncommon": 25,
    "rare": 50,
    "epic": 100,
    "legendary": 200,
}

# Available birds in the shop
AVAILABLE_BIRDS = [
    {
        "id": 1,
        "name": "House Sparrow",
        "rarity": "common",
        "image": "House_Sparrow.png",
        "description": "A humble beginning.",
    },
    {
        "id": 2,
        "name": "Pigeon",
        "rarity": "common",
        "image": "Pigeon.png",
        "description": "A city dweller.",
    },
    {
        "id": 3,
        "name": "Mourning Dove",
        "rarity": "common",
        "image": "Mourning_Dove.png",
        "description": "Peaceful and gentle.",
    },
    {
        "id": 4,
        "name": "European Starling",
        "rarity": "common",
        "image": "European_Starling.png",
        "description": "Iridescent beauty.",
    },
    {
        "id": 5,
        "name": "Canada Goose",
        "rarity": "common",
        "image": "Canada_Goose.png",
        "description": "Loyal traveler.",
    },
    {
        "id": 6,
        "name": "Blue Jay",
        "rarity": "uncommon",
        "image": "Blue_Jay.png",
        "description": "Bold and beautiful.",
    },
    {
        "id": 7,
        "name": "Northern Cardinal",
        "rarity": "uncommon",
        "image": "Northern_Cardinal.png",
        "description": "A vibrant spirit.",
    },
    {
        "id": 8,
        "name": "Mallard Duck",
        "rarity": "uncommon",
        "image": "Mallard_Duck.png",
        "description": "Graceful swimmer.",
    },
    {
        "id": 9,
        "name": "Cockatiel",
        "rarity": "uncommon",
        "image": "Cockatiel.png",
        "description": "Cheerful companion.",
    },
    {
        "id": 10,
        "name": "Lovebird",
        "rarity": "uncommon",
        "image": "Lovebird.png",
        "description": "Affectionate friend.",
    },
    {
        "id": 11,
        "name": "Snowy Owl",
        "rarity": "rare",
        "image": "Snowy_Owl.png",
        "description": "Wise and watchful.",
    },
    {
        "id": 12,
        "name": "Red-Tailed Hawk",
        "rarity": "rare",
        "image": "Red_Tailed_Hawk.png",
        "description": "Sharp-eyed hunter.",
    },
    {
        "id": 13,
        "name": "Great Blue Heron",
        "rarity": "rare",
        "image": "Great_Blue_Heron.png",
        "description": "Patient and elegant.",
    },
    {
        "id": 14,
        "name": "Atlantic Puffin",
        "rarity": "rare",
        "image": "Atlantic_Puffin.png",
        "description": "Colorful clown of the sea.",
    },
    {
        "id": 15,
        "name": "Peregrine Falcon",
        "rarity": "epic",
        "image": "Peregrine_Falcon.png",
        "description": "Fastest bird alive.",
    },
    {
        "id": 16,
        "name": "Ruby-Throated Hummingbird",
        "rarity": "epic",
        "image": "Ruby_Throated_Hummingbird.png",
        "description": "Tiny jewel of the sky.",
    },
    {
        "id": 17,
        "name": "Sandhill Crane",
        "rarity": "epic",
        "image": "Sandhill_Crane.png",
        "description": "Ancient dancer.",
    },
    {
        "id": 18,
        "name": "Bald Eagle",
        "rarity": "legendary",
        "image": "Bald_Eagle.png",
        "description": "King of the skies.",
    },
    {
        "id": 19,
        "name": "Trumpeter Swan",
        "rarity": "legendary",
        "image": "Trumpeter_Swan.png",
        "description": "Pure of heart",
    },
]

# Available habits for students
STUDENT_HABITS = [
    {"id": 1, "name": "Study for 30 minutes", "xp": 15, "category": "study"},
    {"id": 2, "name": "Complete homework", "xp": 20, "category": "study"},
    {"id": 3, "name": "Read for 20 minutes", "xp": 10, "category": "study"},
    {"id": 4, "name": "Review notes", "xp": 10, "category": "study"},
    {"id": 5, "name": "Practice flashcards", "xp": 10, "category": "study"},
    {"id": 6, "name": "Exercise for 30 minutes", "xp": 15, "category": "health"},
    {"id": 7, "name": "Drink 8 glasses of water", "xp": 10, "category": "health"},
    {"id": 8, "name": "Get 8 hours of sleep", "xp": 15, "category": "health"},
    {"id": 9, "name": "Eat a healthy meal", "xp": 10, "category": "health"},
    {"id": 10, "name": "Meditate for 10 minutes", "xp": 10, "category": "health"},
    {"id": 11, "name": "Clean room/desk", "xp": 10, "category": "productivity"},
    {"id": 12, "name": "Plan tomorrow's tasks", "xp": 10, "category": "productivity"},
    {
        "id": 13,
        "name": "No social media for 2 hours",
        "xp": 15,
        "category": "productivity",
    },
    {"id": 14, "name": "Attend all classes", "xp": 20, "category": "productivity"},
    {"id": 15, "name": "Help a classmate", "xp": 15, "category": "social"},
]


# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    xp = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    seeds = db.Column(db.Integer, default=0)
    current_bird_id = db.Column(db.Integer, default=1)
    current_bird_shiny = db.Column(db.Boolean, default=False)
    streak = db.Column(db.Integer, default=0)
    last_login_date = db.Column(db.Date, default=datetime.utcnow().date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    owned_birds = db.relationship("OwnedBird", backref="owner", lazy=True)
    completed_habits = db.relationship("CompletedHabit", backref="user", lazy=True)
    custom_habits = db.relationship("CustomHabit", backref="user", lazy=True)


# Type alias for current_user to help IDE recognize User model attributes
current_user: User = _current_user  # type: ignore[assignment]


class OwnedBird(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    bird_id = db.Column(db.Integer, nullable=False)
    is_shiny = db.Column(db.Boolean, default=False)
    acquired_at = db.Column(db.DateTime, default=datetime.utcnow)


class CompletedHabit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    habit_id = db.Column(db.Integer, nullable=False)
    is_custom = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    date = db.Column(db.Date, default=datetime.utcnow().date)


class CustomHabit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    xp = db.Column(db.Integer, default=10)
    category = db.Column(db.String(50), default="custom")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class HiddenHabit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    habit_id = db.Column(db.Integer, nullable=False)
    hidden_at = db.Column(db.DateTime, default=datetime.utcnow)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Helper Functions
def get_bird_by_id(bird_id):
    for bird in AVAILABLE_BIRDS:
        if bird["id"] == bird_id:
            return bird
    return AVAILABLE_BIRDS[0]


def calculate_xp_for_level(level):
    return XP_PER_LEVEL * level


def get_user_multiplier(user):
    bird = get_bird_by_id(user.current_bird_id)
    rarity = bird["rarity"]
    if user.current_bird_shiny:
        rarity = rarity + "_shiny"
    return RARITY_MULTIPLIERS.get(rarity, 1.0)


def check_and_update_streak(user):
    today = datetime.utcnow().date()
    if user.last_login_date:
        diff = (today - user.last_login_date).days
        if diff == 1:
            user.streak += 1
        elif diff > 1:
            user.streak = 1
    else:
        user.streak = 1
    user.last_login_date = today
    db.session.commit()


def get_all_habits(user):
    # Get hidden habit IDs for this user
    hidden_ids = {
        h.habit_id for h in HiddenHabit.query.filter_by(user_id=user.id).all()
    }

    # Filter out hidden built-in habits
    habits = [h for h in STUDENT_HABITS if h["id"] not in hidden_ids]

    custom = CustomHabit.query.filter_by(user_id=user.id).all()
    for h in custom:
        habits.append(
            {
                "id": f"custom_{h.id}",
                "name": h.name,
                "xp": h.xp,
                "category": h.category,
                "is_custom": True,
            }
        )
    return habits


def get_completed_today(user):
    today = datetime.utcnow().date()
    completed = CompletedHabit.query.filter_by(user_id=user.id, date=today).all()
    return [{"habit_id": c.habit_id, "is_custom": c.is_custom} for c in completed]


# Routes
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not username or not email or not password:
            flash("All fields are required.", "error")
            return redirect(url_for("register"))

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for("register"))

        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "error")
            return redirect(url_for("register"))

        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "error")
            return redirect(url_for("register"))

        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
        )
        db.session.add(user)
        db.session.commit()

        # Give user the starter sparrow
        starter_bird = OwnedBird(user_id=user.id, bird_id=1, is_shiny=False)
        db.session.add(starter_bird)
        db.session.commit()

        flash("Registration successful! Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            check_and_update_streak(user)
            flash(f"Welcome back, {username}! 🐦", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password.", "error")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))


@app.route("/dashboard")
@login_required
def dashboard():
    check_and_update_streak(current_user)
    bird = get_bird_by_id(current_user.current_bird_id)
    xp_needed = calculate_xp_for_level(current_user.level)
    multiplier = get_user_multiplier(current_user)
    habits = get_all_habits(current_user)
    completed_today = get_completed_today(current_user)

    return render_template(
        "dashboard.html",
        bird=bird,
        xp_needed=xp_needed,
        multiplier=multiplier,
        habits=habits,
        completed_today=completed_today,
    )


@app.route("/shop")
@login_required
def shop():
    owned_birds = OwnedBird.query.filter_by(user_id=current_user.id).all()
    owned_dict = {}
    for ob in owned_birds:
        key = ob.bird_id
        if key not in owned_dict:
            owned_dict[key] = {"normal": False, "shiny": False}
        if ob.is_shiny:
            owned_dict[key]["shiny"] = True
        else:
            owned_dict[key]["normal"] = True

    # Ensure current equipped bird is shown as owned
    if current_user.current_bird_id and current_user.current_bird_id not in owned_dict:
        owned_dict[current_user.current_bird_id] = {
            "normal": not current_user.current_bird_shiny,
            "shiny": current_user.current_bird_shiny,
        }
        # Also add to database if missing
        new_owned = OwnedBird(
            user_id=current_user.id,
            bird_id=current_user.current_bird_id,
            is_shiny=current_user.current_bird_shiny,
        )
        db.session.add(new_owned)
        db.session.commit()

    birds_with_prices = []
    for bird in AVAILABLE_BIRDS:
        bird_copy = bird.copy()
        bird_copy["price"] = RARITY_PRICES[bird["rarity"]]
        bird_copy["owned"] = owned_dict.get(
            bird["id"], {"normal": False, "shiny": False}
        )
        birds_with_prices.append(bird_copy)

    return render_template(
        "shop.html", birds=birds_with_prices, rarity_multipliers=RARITY_MULTIPLIERS
    )


@app.route("/api/complete-habit", methods=["POST"])
@login_required
def complete_habit():
    data = request.get_json()
    habit_id = data.get("habit_id")
    is_custom = data.get("is_custom", False)

    today = datetime.utcnow().date()

    # Check if already completed today
    if is_custom:
        actual_id = int(str(habit_id).replace("custom_", ""))
        existing = CompletedHabit.query.filter_by(
            user_id=current_user.id, habit_id=actual_id, is_custom=True, date=today
        ).first()
    else:
        existing = CompletedHabit.query.filter_by(
            user_id=current_user.id, habit_id=int(habit_id), is_custom=False, date=today
        ).first()

    if existing:
        return jsonify({"success": False, "message": "Already completed today!"})

    # Get XP for the habit
    xp_earned = 10
    if is_custom:
        actual_id = int(str(habit_id).replace("custom_", ""))
        custom_habit = CustomHabit.query.get(actual_id)
        if custom_habit:
            xp_earned = custom_habit.xp
    else:
        for h in STUDENT_HABITS:
            if h["id"] == int(habit_id):
                xp_earned = h["xp"]
                break

    # Record completion
    if is_custom:
        actual_id = int(str(habit_id).replace("custom_", ""))
        completion = CompletedHabit(
            user_id=current_user.id, habit_id=actual_id, is_custom=True, date=today
        )
    else:
        completion = CompletedHabit(
            user_id=current_user.id, habit_id=int(habit_id), is_custom=False, date=today
        )
    db.session.add(completion)

    # Add XP
    current_user.xp += xp_earned

    # Check for level up
    xp_needed = calculate_xp_for_level(current_user.level)
    leveled_up = False
    seeds_earned = 0

    if current_user.xp >= xp_needed:
        current_user.xp -= xp_needed
        current_user.level += 1
        multiplier = get_user_multiplier(current_user)
        seeds_earned = int((SEEDS_PER_LEVEL + current_user.level * 5) * multiplier)
        current_user.seeds += seeds_earned
        leveled_up = True

    db.session.commit()

    return jsonify(
        {
            "success": True,
            "xp_earned": xp_earned,
            "current_xp": current_user.xp,
            "level": current_user.level,
            "seeds": current_user.seeds,
            "leveled_up": leveled_up,
            "seeds_earned": seeds_earned,
            "xp_needed": calculate_xp_for_level(current_user.level),
        }
    )


@app.route("/api/add-habit", methods=["POST"])
@login_required
def add_habit():
    data = request.get_json()
    name = data.get("name")
    xp = data.get("xp", 10)
    category = data.get("category", "custom")

    if not name:
        return jsonify({"success": False, "message": "Habit name is required"})

    habit = CustomHabit(user_id=current_user.id, name=name, xp=xp, category=category)
    db.session.add(habit)
    db.session.commit()

    return jsonify(
        {
            "success": True,
            "habit": {
                "id": f"custom_{habit.id}",
                "name": habit.name,
                "xp": habit.xp,
                "category": habit.category,
                "is_custom": True,
            },
        }
    )


@app.route("/api/delete-habit", methods=["POST"])
@login_required
def delete_habit():
    data = request.get_json()
    habit_id = data.get("habit_id")

    if not habit_id:
        return jsonify({"success": False, "message": "No habit ID provided"})

    # Check if it's a custom habit
    if str(habit_id).startswith("custom_"):
        actual_id = int(str(habit_id).replace("custom_", ""))
        habit = CustomHabit.query.filter_by(
            id=actual_id, user_id=current_user.id
        ).first()

        if habit:
            # Delete all completion records for this habit
            CompletedHabit.query.filter_by(
                user_id=current_user.id, habit_id=actual_id, is_custom=True
            ).delete()
            db.session.delete(habit)
            db.session.commit()
            return jsonify({"success": True})

        return jsonify({"success": False, "message": "Habit not found"})

    # It's a built-in habit - hide it instead of deleting
    try:
        builtin_id = int(habit_id)
        # Check if it's a valid built-in habit
        if not any(h["id"] == builtin_id for h in STUDENT_HABITS):
            return jsonify({"success": False, "message": "Invalid habit ID"})

        # Check if already hidden
        existing = HiddenHabit.query.filter_by(
            user_id=current_user.id, habit_id=builtin_id
        ).first()
        if existing:
            return jsonify({"success": True})  # Already hidden

        # Hide the habit and delete completion records
        CompletedHabit.query.filter_by(
            user_id=current_user.id, habit_id=builtin_id, is_custom=False
        ).delete()
        hidden = HiddenHabit(user_id=current_user.id, habit_id=builtin_id)
        db.session.add(hidden)
        db.session.commit()
        return jsonify({"success": True})
    except ValueError:
        return jsonify({"success": False, "message": "Invalid habit ID"})


@app.route("/api/buy-bird", methods=["POST"])
@login_required
def buy_bird():
    data = request.get_json()
    bird_id = data.get("bird_id")

    bird = get_bird_by_id(bird_id)
    if not bird:
        return jsonify({"success": False, "message": "Bird not found"})

    price = RARITY_PRICES[bird["rarity"]]

    if current_user.seeds < price:
        return jsonify({"success": False, "message": "Not enough seeds!"})

    # Check if already owned
    existing = OwnedBird.query.filter_by(
        user_id=current_user.id, bird_id=bird_id
    ).first()
    if existing and not existing.is_shiny:
        # Already have normal, try for shiny - deduct seeds and roll
        current_user.seeds -= price
        is_shiny = random.random() < SHINY_CHANCE
        if is_shiny:
            existing.is_shiny = True
            db.session.commit()
            return jsonify(
                {
                    "success": True,
                    "is_shiny": True,
                    "message": "✨ WOW! You got a SHINY version!",
                    "seeds": current_user.seeds,
                }
            )
        else:
            db.session.commit()
            return jsonify(
                {
                    "success": True,
                    "is_shiny": False,
                    "message": f"No shiny this time... Try again! (1% chance)",
                    "seeds": current_user.seeds,
                }
            )
    elif existing and existing.is_shiny:
        return jsonify(
            {"success": False, "message": "You already own the shiny version!"}
        )

    # Roll for shiny
    is_shiny = random.random() < SHINY_CHANCE

    current_user.seeds -= price
    new_bird = OwnedBird(user_id=current_user.id, bird_id=bird_id, is_shiny=is_shiny)
    db.session.add(new_bird)
    db.session.commit()

    if is_shiny:
        return jsonify(
            {
                "success": True,
                "is_shiny": True,
                "message": "✨ WOW! You got a SHINY version!",
                "seeds": current_user.seeds,
            }
        )

    return jsonify(
        {
            "success": True,
            "is_shiny": False,
            "message": f"You got a {bird['name']}!",
            "seeds": current_user.seeds,
        }
    )


@app.route("/api/equip-bird", methods=["POST"])
@login_required
def equip_bird():
    data = request.get_json()
    bird_id = data.get("bird_id")
    use_shiny = data.get("shiny", False)

    # Check if user owns this bird
    owned = OwnedBird.query.filter_by(user_id=current_user.id, bird_id=bird_id).first()
    if not owned:
        return jsonify({"success": False, "message": "You do not own this bird!"})

    if use_shiny and not owned.is_shiny:
        return jsonify(
            {"success": False, "message": "You do not have the shiny version!"}
        )

    current_user.current_bird_id = bird_id
    current_user.current_bird_shiny = use_shiny
    db.session.commit()

    bird = get_bird_by_id(bird_id)
    return jsonify(
        {
            "success": True,
            "message": f"{bird['name']} is now your active bird!",
            "multiplier": get_user_multiplier(current_user),
        }
    )


@app.route("/api/stats")
@login_required
def get_stats():
    today = datetime.utcnow().date()
    week_ago = today - timedelta(days=7)

    # Get completions for the past week
    completions = CompletedHabit.query.filter(
        CompletedHabit.user_id == current_user.id, CompletedHabit.date >= week_ago
    ).all()

    # Group by date
    daily_counts = {}
    for c in completions:
        date_str = c.date.strftime("%Y-%m-%d")
        daily_counts[date_str] = daily_counts.get(date_str, 0) + 1

    return jsonify(
        {
            "streak": current_user.streak,
            "level": current_user.level,
            "total_xp": current_user.xp + (current_user.level - 1) * XP_PER_LEVEL,
            "seeds": current_user.seeds,
            "daily_completions": daily_counts,
        }
    )


# Initialize database
def init_db():
    with app.app_context():
        # Get the instance folder path (where Flask-SQLAlchemy stores the db)
        instance_path = app.instance_path
        db_filename = app.config["SQLALCHEMY_DATABASE_URI"].replace("sqlite:///", "")
        db_path = os.path.join(instance_path, db_filename)

        # Ensure instance folder exists
        if not os.path.exists(instance_path):
            os.makedirs(instance_path)
            print(f"📁 Created instance folder: {instance_path}")

        # Check if database file exists
        db_exists = os.path.exists(db_path)

        if not db_exists:
            print(f"📁 Database not found at {db_path}. Creating new database...")

        # Create all tables if they don't exist
        db.create_all()

        # Verify tables were created by checking if we can query them
        try:
            User.query.first()
            OwnedBird.query.first()
            CompletedHabit.query.first()
            CustomHabit.query.first()
            HiddenHabit.query.first()
            if not db_exists:
                print("✅ Database and tables created successfully!")
            else:
                print("✅ Database tables verified!")
        except Exception as e:
            print(f"⚠️ Error verifying tables: {e}")
            # Force recreate tables
            db.drop_all()
            db.create_all()
            print("✅ Database tables recreated!")


# Initialize database on import (needed for Railway)
init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
