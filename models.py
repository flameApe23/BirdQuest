import random
from datetime import date, datetime

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()

# Bird rarities with their multipliers and costs
RARITIES = {
    "common": {"multiplier": 1.0, "base_cost": 10, "color": "#d3d3d3"},
    "common_shiny": {"multiplier": 1.5, "base_cost": 15, "color": "#d3d3d3"},
    "uncommon": {"multiplier": 1.2, "base_cost": 25, "color": "#90ee90"},
    "uncommon_shiny": {"multiplier": 1.8, "base_cost": 40, "color": "#90ee90"},
    "rare": {"multiplier": 1.5, "base_cost": 60, "color": "#add8e6"},
    "rare_shiny": {"multiplier": 2.3, "base_cost": 100, "color": "#add8e6"},
    "epic": {"multiplier": 1.7, "base_cost": 150, "color": "#dda0dd"},
    "epic_shiny": {"multiplier": 2.7, "base_cost": 250, "color": "#dda0dd"},
    "legendary": {"multiplier": 2.0, "base_cost": 400, "color": "#ffd700"},
    "legendary_shiny": {"multiplier": 4.0, "base_cost": 700, "color": "#ffd700"},
}


# XP required for each level
def xp_for_level(level):
    return int(100 * (level**1.5))


# Seeds earned when leveling up
def seeds_for_level(level):
    return 5 + (level * 2)


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    # Game stats
    xp = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    seeds = db.Column(db.Integer, default=0)
    total_seeds_earned = db.Column(db.Integer, default=0)

    # Current equipped bird
    current_bird_id = db.Column(
        db.Integer, db.ForeignKey("user_birds.id"), nullable=True
    )

    # Streak tracking
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    last_activity_date = db.Column(db.Date, nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    tasks = db.relationship(
        "Task", backref="user", lazy=True, cascade="all, delete-orphan"
    )
    task_logs = db.relationship(
        "TaskLog", backref="user", lazy=True, cascade="all, delete-orphan"
    )
    owned_birds = db.relationship(
        "UserBird",
        backref="owner",
        lazy=True,
        foreign_keys="UserBird.user_id",
        cascade="all, delete-orphan",
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_xp_progress(self):
        """Returns current XP and XP needed for next level"""
        xp_needed = xp_for_level(self.level)
        return self.xp, xp_needed

    def get_xp_percentage(self):
        """Returns XP progress as percentage"""
        current, needed = self.get_xp_progress()
        return min(100, int((current / needed) * 100))

    def add_xp(self, amount):
        """Add XP and handle level ups, returns seeds earned"""
        # Get current bird multiplier
        multiplier = self.get_seed_multiplier()

        self.xp += amount
        seeds_earned = 0

        while self.xp >= xp_for_level(self.level):
            self.xp -= xp_for_level(self.level)
            self.level += 1
            level_seeds = int(seeds_for_level(self.level) * multiplier)
            seeds_earned += level_seeds
            self.seeds += level_seeds
            self.total_seeds_earned += level_seeds

        return seeds_earned

    def get_seed_multiplier(self):
        """Get the seed multiplier from equipped bird"""
        if self.current_bird_id:
            equipped = UserBird.query.get(self.current_bird_id)
            if equipped:
                rarity_key = equipped.rarity
                if equipped.is_shiny:
                    rarity_key += "_shiny"
                return RARITIES.get(rarity_key, {}).get("multiplier", 1.0)
        return 1.0

    def update_streak(self):
        """Update streak based on activity"""
        today = date.today()

        if self.last_activity_date is None:
            self.current_streak = 1
        elif self.last_activity_date == today:
            pass  # Already logged today
        elif (today - self.last_activity_date).days == 1:
            self.current_streak += 1
        elif (today - self.last_activity_date).days > 1:
            self.current_streak = 1  # Streak broken

        self.last_activity_date = today

        if self.current_streak > self.longest_streak:
            self.longest_streak = self.current_streak

    def get_equipped_bird(self):
        """Get the currently equipped bird"""
        if self.current_bird_id:
            return UserBird.query.get(self.current_bird_id)
        return None


class Bird(db.Model):
    __tablename__ = "birds"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(256), nullable=False)
    rarity = db.Column(db.String(20), nullable=False, default="common")
    base_cost = db.Column(db.Integer, nullable=False)

    # Unlock requirements
    level_required = db.Column(db.Integer, default=1)

    def get_cost(self):
        """Get the cost based on rarity"""
        return RARITIES.get(self.rarity, {}).get("base_cost", self.base_cost)

    def get_rarity_color(self):
        """Get background tint color for rarity"""
        return RARITIES.get(self.rarity, {}).get("color", "#ffffff")


class UserBird(db.Model):
    __tablename__ = "user_birds"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    bird_id = db.Column(db.Integer, db.ForeignKey("birds.id"), nullable=False)

    # Shiny status (1% chance when purchasing)
    is_shiny = db.Column(db.Boolean, default=False)
    rarity = db.Column(db.String(20), nullable=False)

    # When acquired
    acquired_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to bird template
    bird = db.relationship("Bird", backref="user_birds")

    @staticmethod
    def purchase_bird(user, bird):
        """Purchase a bird for a user, with 1% shiny chance"""
        cost = bird.base_cost

        if user.seeds < cost:
            return None, "Not enough seeds!"

        user.seeds -= cost

        # 1% chance for shiny
        is_shiny = random.random() < 0.01

        user_bird = UserBird(
            user_id=user.id, bird_id=bird.id, is_shiny=is_shiny, rarity=bird.rarity
        )

        db.session.add(user_bird)

        # If this is the user's first bird, equip it
        if not user.current_bird_id:
            db.session.flush()  # Get the ID
            user.current_bird_id = user_bird.id

        return user_bird, "Shiny!" if is_shiny else "Success!"

    def get_multiplier(self):
        """Get seed multiplier for this bird"""
        rarity_key = self.rarity
        if self.is_shiny:
            rarity_key += "_shiny"
        return RARITIES.get(rarity_key, {}).get("multiplier", 1.0)

    def get_display_name(self):
        """Get display name with shiny prefix if applicable"""
        if self.is_shiny:
            return f"✨ Shiny {self.bird.name}"
        return self.bird.name


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=False, default="general")

    # XP reward for completing
    xp_reward = db.Column(db.Integer, default=10)

    # Frequency: daily, weekly, or one-time
    frequency = db.Column(db.String(20), default="daily")

    # Active status
    is_active = db.Column(db.Boolean, default=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Task logs relationship
    logs = db.relationship(
        "TaskLog", backref="task", lazy=True, cascade="all, delete-orphan"
    )

    def is_completed_today(self):
        """Check if task was completed today"""
        today = date.today()
        return (
            TaskLog.query.filter(
                TaskLog.task_id == self.id, db.func.date(TaskLog.completed_at) == today
            ).first()
            is not None
        )

    def get_streak(self):
        """Get current streak for this task"""
        logs = (
            TaskLog.query.filter_by(task_id=self.id)
            .order_by(TaskLog.completed_at.desc())
            .all()
        )

        if not logs:
            return 0

        streak = 0
        current_date = date.today()

        for log in logs:
            log_date = log.completed_at.date()

            if log_date == current_date or (current_date - log_date).days == 1:
                streak += 1
                current_date = log_date
            elif log_date < current_date:
                break

        return streak


class TaskLog(db.Model):
    __tablename__ = "task_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), nullable=False)

    # When completed
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

    # XP earned (stored for history)
    xp_earned = db.Column(db.Integer, default=0)

    # Optional notes
    notes = db.Column(db.Text, nullable=True)


# Predefined student-relevant task categories
TASK_CATEGORIES = [
    {"id": "study", "name": "Study", "icon": "📚", "default_xp": 15},
    {"id": "exercise", "name": "Exercise", "icon": "🏃", "default_xp": 12},
    {"id": "reading", "name": "Reading", "icon": "📖", "default_xp": 10},
    {"id": "sleep", "name": "Sleep Schedule", "icon": "😴", "default_xp": 8},
    {"id": "nutrition", "name": "Healthy Eating", "icon": "🥗", "default_xp": 8},
    {"id": "social", "name": "Social", "icon": "👥", "default_xp": 10},
    {"id": "creative", "name": "Creative", "icon": "🎨", "default_xp": 12},
    {"id": "chores", "name": "Chores", "icon": "🧹", "default_xp": 8},
    {"id": "mindfulness", "name": "Mindfulness", "icon": "🧘", "default_xp": 10},
    {"id": "general", "name": "General", "icon": "✅", "default_xp": 10},
]

# Default birds to populate the shop
DEFAULT_BIRDS = [
    # Common birds
    {
        "name": "Sparrow",
        "description": "A humble beginning. Every journey starts with a single chirp.",
        "image_url": "sparrow.svg",
        "rarity": "common",
        "base_cost": 0,
        "level_required": 1,
    },
    {
        "name": "Robin",
        "description": "A cheerful friend that brings good luck.",
        "image_url": "robin.svg",
        "rarity": "common",
        "base_cost": 10,
        "level_required": 1,
    },
    {
        "name": "Finch",
        "description": "Small but mighty, with a beautiful song.",
        "image_url": "finch.svg",
        "rarity": "common",
        "base_cost": 15,
        "level_required": 2,
    },
    # Uncommon birds
    {
        "name": "Blue Jay",
        "description": "Bold and beautiful, a symbol of curiosity.",
        "image_url": "bluejay.svg",
        "rarity": "uncommon",
        "base_cost": 25,
        "level_required": 3,
    },
    {
        "name": "Cardinal",
        "description": "A vibrant red bird that stands out in any crowd.",
        "image_url": "cardinal.svg",
        "rarity": "uncommon",
        "base_cost": 30,
        "level_required": 4,
    },
    {
        "name": "Woodpecker",
        "description": "Persistent and hardworking, never gives up.",
        "image_url": "woodpecker.svg",
        "rarity": "uncommon",
        "base_cost": 35,
        "level_required": 5,
    },
    # Rare birds
    {
        "name": "Owl",
        "description": "Wise and watchful, master of the night.",
        "image_url": "owl.svg",
        "rarity": "rare",
        "base_cost": 60,
        "level_required": 7,
    },
    {
        "name": "Kingfisher",
        "description": "Swift and precise, a flash of brilliant color.",
        "image_url": "kingfisher.svg",
        "rarity": "rare",
        "base_cost": 75,
        "level_required": 9,
    },
    {
        "name": "Peacock",
        "description": "Majestic and proud, a true showstopper.",
        "image_url": "peacock.svg",
        "rarity": "rare",
        "base_cost": 90,
        "level_required": 11,
    },
    # Epic birds
    {
        "name": "Eagle",
        "description": "Soaring high above, a symbol of freedom and strength.",
        "image_url": "eagle.svg",
        "rarity": "epic",
        "base_cost": 150,
        "level_required": 14,
    },
    {
        "name": "Falcon",
        "description": "The fastest bird alive, pure speed and grace.",
        "image_url": "falcon.svg",
        "rarity": "epic",
        "base_cost": 180,
        "level_required": 17,
    },
    {
        "name": "Cockatoo",
        "description": "Intelligent and playful, a true companion.",
        "image_url": "cockatoo.svg",
        "rarity": "epic",
        "base_cost": 200,
        "level_required": 20,
    },
    # Legendary birds
    {
        "name": "Phoenix",
        "description": "Rising from the ashes, eternal and unstoppable.",
        "image_url": "phoenix.svg",
        "rarity": "legendary",
        "base_cost": 400,
        "level_required": 25,
    },
    {
        "name": "Thunderbird",
        "description": "Master of storms, legendary power incarnate.",
        "image_url": "thunderbird.svg",
        "rarity": "legendary",
        "base_cost": 500,
        "level_required": 30,
    },
    {
        "name": "Celestial Dove",
        "description": "A divine messenger from the heavens above.",
        "image_url": "celestial_dove.svg",
        "rarity": "legendary",
        "base_cost": 600,
        "level_required": 35,
    },
]


def init_default_birds():
    """Initialize the database with default birds"""
    for bird_data in DEFAULT_BIRDS:
        existing = Bird.query.filter_by(name=bird_data["name"]).first()
        if not existing:
            bird = Bird(**bird_data)
            db.session.add(bird)
    db.session.commit()


def give_starter_bird(user):
    """Give new user the starter sparrow"""
    sparrow = Bird.query.filter_by(name="Sparrow").first()
    if sparrow:
        user_bird = UserBird(
            user_id=user.id, bird_id=sparrow.id, is_shiny=False, rarity="common"
        )
        db.session.add(user_bird)
        db.session.flush()
        user.current_bird_id = user_bird.id
        db.session.commit()
        return user_bird
    return None
