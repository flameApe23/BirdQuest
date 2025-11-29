import os
import sys
from datetime import datetime

project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

from app import app, db, User, OwnedBird
from werkzeug.security import generate_password_hash

USERNAME = "ShinyBird"
EMAIL    = "shiny@birdquest.com"
PASSWORD = "SUPANINJA"

SEEDS = 999_999
LEVEL = 99

def create_god_account():
    with app.app_context():
        print("Creating / upgrading god account...")

        user = User.query.filter_by(username=USERNAME).first()
        if user:
            print(f"User '{USERNAME}' already exists > upgrading to legendary mode")
        else:
            user = User(
                username=USERNAME,
                email=EMAIL,
                password_hash=generate_password_hash(PASSWORD),
                created_at=datetime.utcnow()
            )
            db.session.add(user)
            db.session.commit()
            print(f"Created new user: {USERNAME}")

        user.seeds = SEEDS
        user.total_seeds_earned = SEEDS + 999_999
        user.level = LEVEL
        user.xp = 999_999
        user.current_streak = 9999
        user.longest_streak = 9999
        user.last_activity_date = datetime.utcnow().date()

        from app import AVAILABLE_BIRDS
        legendary = next((b for b in AVAILABLE_BIRDS if b["rarity"] == "legendary"), None)
        if not legendary:
            legendary = AVAILABLE_BIRDS[-1]

        bird_id = legendary["id"]
        bird_name = legendary["name"]

        print(f"Chosen legendary bird: {bird_name} (ID {bird_id})")

        owned = OwnedBird.query.filter_by(user_id=user.id, bird_id=bird_id).first()
        if not owned:
            owned = OwnedBird(
                user_id=user.id,
                bird_id=bird_id,
                is_shiny=True
            )
            db.session.add(owned)
            print("Gave shiny legendary bird!")
        else:
            owned.is_shiny = True
            print("Upgraded existing bird > SHINY!")

        # Equip it
        user.current_bird_id = bird_id
        user.current_bird_shiny = True

        db.session.commit()

        print("\n" + "="*60)
        print("Created and equipped")
        print(f"   Username : {USERNAME}")
        print(f"   Password : {PASSWORD}")
        print(f"   Level    : {LEVEL}")
        print(f"   Seeds    : {SEEDS:,}")
        print(f"   Equipped : SHINY {bird_name}")
        print("="*60)

if __name__ == "__main__":
    create_god_account()
