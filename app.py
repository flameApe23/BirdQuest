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
app.config["SECRET_KEY"] = os.urandom(24).hex()
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///birdquest.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

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


# Group Models
class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    invite_code = db.Column(db.String(8), unique=True, nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    creator = db.relationship(
        "User", backref="created_groups", foreign_keys=[creator_id]
    )
    members = db.relationship(
        "GroupMember", backref="group", lazy=True, cascade="all, delete-orphan"
    )
    challenges = db.relationship(
        "GroupChallenge", backref="group", lazy=True, cascade="all, delete-orphan"
    )

    def get_member_count(self):
        return len(self.members)

    def is_member(self, user_id):
        return any(m.user_id == user_id for m in self.members)

    def is_admin(self, user_id):
        member = next((m for m in self.members if m.user_id == user_id), None)
        return member and member.is_admin


class GroupMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to user
    user = db.relationship("User", backref="group_memberships")

    __table_args__ = (
        db.UniqueConstraint("group_id", "user_id", name="unique_group_member"),
    )


class GroupChallenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    habit_name = db.Column(db.String(100), nullable=False)  # The habit to track
    target_count = db.Column(db.Integer, default=7)  # Number of times to complete
    xp_reward = db.Column(db.Integer, default=50)  # Bonus XP for completing challenge
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    creator = db.relationship("User", backref="created_challenges")
    participants = db.relationship(
        "GroupChallengeParticipant",
        backref="challenge",
        lazy=True,
        cascade="all, delete-orphan",
    )

    def is_active(self):
        today = datetime.utcnow().date()
        return self.start_date <= today <= self.end_date

    def is_expired(self):
        return datetime.utcnow().date() > self.end_date

    def days_remaining(self):
        today = datetime.utcnow().date()
        if today > self.end_date:
            return 0
        return (self.end_date - today).days


class GroupChallengeParticipant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(
        db.Integer, db.ForeignKey("group_challenge.id"), nullable=False
    )
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    progress = db.Column(db.Integer, default=0)  # Times completed
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to user
    user = db.relationship("User", backref="challenge_participations")

    __table_args__ = (
        db.UniqueConstraint(
            "challenge_id", "user_id", name="unique_challenge_participant"
        ),
    )


class GroupChallengeLog(db.Model):
    """Tracks daily completions for group challenges"""

    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(
        db.Integer, db.ForeignKey("group_challenge_participant.id"), nullable=False
    )
    date = db.Column(db.Date, default=datetime.utcnow().date)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

    participant = db.relationship("GroupChallengeParticipant", backref="logs")

    __table_args__ = (
        db.UniqueConstraint("participant_id", "date", name="unique_daily_log"),
    )


def generate_invite_code():
    """Generate a unique 8-character invite code"""
    import string

    while True:
        code = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
        if not Group.query.filter_by(invite_code=code).first():
            return code


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
        seeds_earned = int(SEEDS_PER_LEVEL * multiplier)
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
        # Already have normal, check shiny chance
        is_shiny = random.random() < SHINY_CHANCE
        if is_shiny:
            existing.is_shiny = True
            current_user.seeds -= price
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
            return jsonify({"success": False, "message": "You already own this bird!"})
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


# ==================== GROUP ROUTES ====================


@app.route("/groups")
@login_required
def groups():
    """Display all groups the user is a member of"""
    user_groups = (
        Group.query.join(GroupMember)
        .filter(GroupMember.user_id == current_user.id)
        .all()
    )

    return render_template("groups.html", groups=user_groups)


@app.route("/groups/<int:group_id>")
@login_required
def group_detail(group_id):
    """Display group details, leaderboard, and challenges"""
    group = Group.query.get_or_404(group_id)

    # Check if user is a member
    if not group.is_member(current_user.id):
        flash("You are not a member of this group.", "error")
        return redirect(url_for("groups"))

    # Get leaderboard data
    members_data = []
    for member in group.members:
        user = member.user
        members_data.append(
            {
                "id": user.id,
                "username": user.username,
                "level": user.level,
                "xp": user.xp,
                "streak": user.streak,
                "seeds": user.seeds,
                "is_admin": member.is_admin,
                "bird": get_bird_by_id(user.current_bird_id),
                "is_shiny": user.current_bird_shiny,
            }
        )

    # Sort by level, then XP
    members_data.sort(key=lambda x: (x["level"], x["xp"]), reverse=True)

    # Get active and past challenges
    today = datetime.utcnow().date()
    active_challenges = []
    past_challenges = []

    for challenge in group.challenges:
        challenge_data = {
            "id": challenge.id,
            "name": challenge.name,
            "description": challenge.description,
            "habit_name": challenge.habit_name,
            "target_count": challenge.target_count,
            "xp_reward": challenge.xp_reward,
            "start_date": challenge.start_date.strftime("%b %d"),
            "end_date": challenge.end_date.strftime("%b %d"),
            "days_remaining": challenge.days_remaining(),
            "is_active": challenge.is_active(),
            "participant_count": len(challenge.participants),
            "creator": challenge.creator.username,
        }

        # Check if current user is participating
        participation = next(
            (p for p in challenge.participants if p.user_id == current_user.id), None
        )
        challenge_data["is_participating"] = participation is not None
        challenge_data["user_progress"] = participation.progress if participation else 0
        challenge_data["user_completed"] = (
            participation.completed if participation else False
        )

        # Get top participants
        sorted_participants = sorted(
            challenge.participants, key=lambda p: p.progress, reverse=True
        )[:5]
        challenge_data["top_participants"] = [
            {
                "username": p.user.username,
                "progress": p.progress,
                "completed": p.completed,
            }
            for p in sorted_participants
        ]

        if challenge.is_active():
            active_challenges.append(challenge_data)
        else:
            past_challenges.append(challenge_data)

    is_admin = group.is_admin(current_user.id)

    return render_template(
        "group_detail.html",
        group=group,
        members=members_data,
        active_challenges=active_challenges,
        past_challenges=past_challenges,
        is_admin=is_admin,
    )


@app.route("/api/groups/create", methods=["POST"])
@login_required
def create_group():
    """Create a new group"""
    data = request.get_json()
    name = data.get("name", "").strip()
    description = data.get("description", "").strip()

    if not name:
        return jsonify({"success": False, "message": "Group name is required"})

    if len(name) > 100:
        return jsonify({"success": False, "message": "Group name is too long"})

    # Generate unique invite code
    invite_code = generate_invite_code()

    # Create the group
    group = Group(
        name=name,
        description=description,
        invite_code=invite_code,
        creator_id=current_user.id,
    )
    db.session.add(group)
    db.session.flush()

    # Add creator as admin member
    member = GroupMember(group_id=group.id, user_id=current_user.id, is_admin=True)
    db.session.add(member)
    db.session.commit()

    return jsonify(
        {
            "success": True,
            "message": "Group created successfully!",
            "group_id": group.id,
            "invite_code": invite_code,
        }
    )


@app.route("/api/groups/join", methods=["POST"])
@login_required
def join_group():
    """Join a group using invite code"""
    data = request.get_json()
    invite_code = data.get("invite_code", "").strip().upper()

    if not invite_code:
        return jsonify({"success": False, "message": "Invite code is required"})

    group = Group.query.filter_by(invite_code=invite_code).first()

    if not group:
        return jsonify({"success": False, "message": "Invalid invite code"})

    # Check if already a member
    if group.is_member(current_user.id):
        return jsonify(
            {"success": False, "message": "You are already a member of this group"}
        )

    # Add as member
    member = GroupMember(group_id=group.id, user_id=current_user.id, is_admin=False)
    db.session.add(member)
    db.session.commit()

    return jsonify(
        {
            "success": True,
            "message": f"Successfully joined {group.name}!",
            "group_id": group.id,
        }
    )


@app.route("/api/groups/<int:group_id>/leave", methods=["POST"])
@login_required
def leave_group(group_id):
    """Leave a group"""
    group = Group.query.get_or_404(group_id)

    member = GroupMember.query.filter_by(
        group_id=group_id, user_id=current_user.id
    ).first()

    if not member:
        return jsonify({"success": False, "message": "You are not a member"})

    # Check if user is the only admin
    if member.is_admin:
        admin_count = GroupMember.query.filter_by(
            group_id=group_id, is_admin=True
        ).count()
        if admin_count == 1 and len(group.members) > 1:
            return jsonify(
                {
                    "success": False,
                    "message": "Please promote another member to admin before leaving",
                }
            )

    # Remove from all challenges in this group
    for challenge in group.challenges:
        participation = GroupChallengeParticipant.query.filter_by(
            challenge_id=challenge.id, user_id=current_user.id
        ).first()
        if participation:
            db.session.delete(participation)

    db.session.delete(member)

    # If no members left, delete the group
    if len(group.members) <= 1:
        db.session.delete(group)

    db.session.commit()

    return jsonify({"success": True, "message": "Left the group"})


@app.route("/api/groups/<int:group_id>/promote", methods=["POST"])
@login_required
def promote_member(group_id):
    """Promote a member to admin"""
    group = Group.query.get_or_404(group_id)

    if not group.is_admin(current_user.id):
        return jsonify({"success": False, "message": "Only admins can promote members"})

    data = request.get_json()
    user_id = data.get("user_id")

    member = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()

    if not member:
        return jsonify({"success": False, "message": "User is not a member"})

    member.is_admin = True
    db.session.commit()

    return jsonify({"success": True, "message": "Member promoted to admin"})


@app.route("/api/groups/<int:group_id>/kick", methods=["POST"])
@login_required
def kick_member(group_id):
    """Remove a member from the group"""
    group = Group.query.get_or_404(group_id)

    if not group.is_admin(current_user.id):
        return jsonify({"success": False, "message": "Only admins can remove members"})

    data = request.get_json()
    user_id = data.get("user_id")

    if user_id == current_user.id:
        return jsonify({"success": False, "message": "You cannot kick yourself"})

    member = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()

    if not member:
        return jsonify({"success": False, "message": "User is not a member"})

    # Remove from challenges
    for challenge in group.challenges:
        participation = GroupChallengeParticipant.query.filter_by(
            challenge_id=challenge.id, user_id=user_id
        ).first()
        if participation:
            db.session.delete(participation)

    db.session.delete(member)
    db.session.commit()

    return jsonify({"success": True, "message": "Member removed"})


@app.route("/api/groups/<int:group_id>/leaderboard")
@login_required
def group_leaderboard(group_id):
    """Get group leaderboard data"""
    group = Group.query.get_or_404(group_id)

    if not group.is_member(current_user.id):
        return jsonify({"success": False, "message": "Not a member"})

    members_data = []
    for member in group.members:
        user = member.user
        members_data.append(
            {
                "id": user.id,
                "username": user.username,
                "level": user.level,
                "xp": user.xp,
                "streak": user.streak,
                "seeds": user.seeds,
            }
        )

    # Sort by level, then XP
    members_data.sort(key=lambda x: (x["level"], x["xp"]), reverse=True)

    return jsonify({"success": True, "leaderboard": members_data})


# ==================== CHALLENGE ROUTES ====================


@app.route("/api/challenges/create", methods=["POST"])
@login_required
def create_challenge():
    """Create a new group challenge"""
    data = request.get_json()
    group_id = data.get("group_id")
    name = data.get("name", "").strip()
    description = data.get("description", "").strip()
    habit_name = data.get("habit_name", "").strip()
    target_count = data.get("target_count", 7)
    duration_days = data.get("duration_days", 7)
    xp_reward = data.get("xp_reward", 50)

    if not all([group_id, name, habit_name]):
        return jsonify({"success": False, "message": "Missing required fields"})

    group = Group.query.get(group_id)
    if not group:
        return jsonify({"success": False, "message": "Group not found"})

    if not group.is_member(current_user.id):
        return jsonify({"success": False, "message": "You are not a member"})

    # Calculate dates
    start_date = datetime.utcnow().date()
    end_date = start_date + timedelta(days=int(duration_days))

    challenge = GroupChallenge(
        group_id=group_id,
        name=name,
        description=description,
        habit_name=habit_name,
        target_count=int(target_count),
        xp_reward=int(xp_reward),
        start_date=start_date,
        end_date=end_date,
        created_by=current_user.id,
    )
    db.session.add(challenge)
    db.session.flush()

    # Auto-join creator
    participant = GroupChallengeParticipant(
        challenge_id=challenge.id, user_id=current_user.id
    )
    db.session.add(participant)
    db.session.commit()

    return jsonify(
        {
            "success": True,
            "message": "Challenge created!",
            "challenge_id": challenge.id,
        }
    )


@app.route("/api/challenges/<int:challenge_id>/join", methods=["POST"])
@login_required
def join_challenge(challenge_id):
    """Join a group challenge"""
    challenge = GroupChallenge.query.get_or_404(challenge_id)

    if not challenge.group.is_member(current_user.id):
        return jsonify({"success": False, "message": "You are not a group member"})

    # Check if already participating
    existing = GroupChallengeParticipant.query.filter_by(
        challenge_id=challenge_id, user_id=current_user.id
    ).first()

    if existing:
        return jsonify({"success": False, "message": "Already participating"})

    if challenge.is_expired():
        return jsonify({"success": False, "message": "Challenge has ended"})

    participant = GroupChallengeParticipant(
        challenge_id=challenge_id, user_id=current_user.id
    )
    db.session.add(participant)
    db.session.commit()

    return jsonify({"success": True, "message": "Joined the challenge!"})


@app.route("/api/challenges/<int:challenge_id>/log", methods=["POST"])
@login_required
def log_challenge_progress(challenge_id):
    """Log daily progress for a challenge"""
    challenge = GroupChallenge.query.get_or_404(challenge_id)

    participant = GroupChallengeParticipant.query.filter_by(
        challenge_id=challenge_id, user_id=current_user.id
    ).first()

    if not participant:
        return jsonify({"success": False, "message": "Not participating"})

    if challenge.is_expired():
        return jsonify({"success": False, "message": "Challenge has ended"})

    if participant.completed:
        return jsonify(
            {"success": False, "message": "Already completed this challenge"}
        )

    today = datetime.utcnow().date()

    # Check if already logged today
    existing_log = GroupChallengeLog.query.filter_by(
        participant_id=participant.id, date=today
    ).first()

    if existing_log:
        return jsonify({"success": False, "message": "Already logged today"})

    # Create log entry
    log = GroupChallengeLog(participant_id=participant.id, date=today)
    db.session.add(log)

    # Update progress
    participant.progress += 1

    # Check if completed
    bonus_xp = 0
    if participant.progress >= challenge.target_count:
        participant.completed = True
        participant.completed_at = datetime.utcnow()
        bonus_xp = challenge.xp_reward
        current_user.xp += bonus_xp

        # Check for level up
        xp_needed = calculate_xp_for_level(current_user.level)
        if current_user.xp >= xp_needed:
            current_user.xp -= xp_needed
            current_user.level += 1
            multiplier = get_user_multiplier(current_user)
            seeds_earned = int(SEEDS_PER_LEVEL * multiplier)
            current_user.seeds += seeds_earned

    db.session.commit()

    return jsonify(
        {
            "success": True,
            "progress": participant.progress,
            "target": challenge.target_count,
            "completed": participant.completed,
            "bonus_xp": bonus_xp,
            "message": "Progress logged!"
            + (" 🎉 Challenge completed!" if participant.completed else ""),
        }
    )


@app.route("/api/challenges/<int:challenge_id>/details")
@login_required
def challenge_details(challenge_id):
    """Get detailed challenge information"""
    challenge = GroupChallenge.query.get_or_404(challenge_id)

    if not challenge.group.is_member(current_user.id):
        return jsonify({"success": False, "message": "Not a member"})

    participants_data = []
    for p in challenge.participants:
        participants_data.append(
            {
                "username": p.user.username,
                "progress": p.progress,
                "completed": p.completed,
                "user_id": p.user_id,
            }
        )

    participants_data.sort(key=lambda x: x["progress"], reverse=True)

    # Check current user participation
    user_participation = next(
        (p for p in challenge.participants if p.user_id == current_user.id), None
    )

    # Check if user already logged today
    can_log_today = False
    if user_participation and not user_participation.completed:
        today = datetime.utcnow().date()
        existing_log = GroupChallengeLog.query.filter_by(
            participant_id=user_participation.id, date=today
        ).first()
        can_log_today = existing_log is None

    return jsonify(
        {
            "success": True,
            "challenge": {
                "id": challenge.id,
                "name": challenge.name,
                "description": challenge.description,
                "habit_name": challenge.habit_name,
                "target_count": challenge.target_count,
                "xp_reward": challenge.xp_reward,
                "start_date": challenge.start_date.strftime("%Y-%m-%d"),
                "end_date": challenge.end_date.strftime("%Y-%m-%d"),
                "days_remaining": challenge.days_remaining(),
                "is_active": challenge.is_active(),
                "creator": challenge.creator.username,
            },
            "participants": participants_data,
            "user_participating": user_participation is not None,
            "user_progress": user_participation.progress if user_participation else 0,
            "user_completed": user_participation.completed
            if user_participation
            else False,
            "can_log_today": can_log_today,
        }
    )


# Initialize database
def init_db():
    with app.app_context():
        db.create_all()


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
