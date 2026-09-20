from __future__ import annotations

import json
import os
from datetime import date, timedelta

os.environ.setdefault("MANNAH_WEB_DB", os.environ.get("MANNAH_WEB_DB", "/tmp/mannah-demo.db"))
os.environ.setdefault("SECRET_KEY", "demo-secret")

from mannah_web.app import TRACKED, app_db, search_mannah  # noqa: E402
from werkzeug.security import generate_password_hash  # noqa: E402

USERNAME = os.environ.get("DEMO_USERNAME", "demo")
PASSWORD = os.environ.get("DEMO_PASSWORD", "demo1234")


def portion(food: dict, grams: float) -> dict:
    factor = grams / 100.0
    return {k: round(float(food.get(k) or 0) * factor, 4) for k in TRACKED}


def choose(query: str) -> dict:
    rows = search_mannah(query, 20)
    if not rows:
        raise RuntimeError(f"No demo food found for: {query}")
    return rows[0]


def main() -> None:
    today = date.today()
    foods = {
        "eggs": choose("egg"),
        "oats": choose("oat"),
        "banana": choose("banana"),
        "chicken": choose("chicken breast"),
        "rice": choose("rice"),
        "broccoli": choose("broccoli"),
        "salmon": choose("salmon"),
        "almonds": choose("almond"),
    }

    with app_db() as con:
        old = con.execute("select id from users where lower(username)=lower(?)", (USERNAME,)).fetchone()
        if old:
            con.execute("delete from users where id=?", (old["id"],))

        uid = con.execute(
            "insert into users(name,username,email,password_hash,is_admin) values(?,?,?,?,0)",
            ("Demo User", USERNAME, f"{USERNAME}@local.invalid", generate_password_hash(PASSWORD)),
        ).lastrowid
        con.execute(
            """insert into profiles(user_id,age,sex,height_cm,weight_kg,activity,calorie_goal,protein_goal,fiber_goal,water_goal_ml)
               values(?,?,?,?,?,?,?,?,?,?)""",
            (uid, 34, "male", 180, 82, "moderate", 2400, 160, 32, 3000),
        )

        daily_sets = [
            [("Breakfast", foods["eggs"], 150), ("Breakfast", foods["oats"], 80), ("Breakfast", foods["banana"], 118),
             ("Lunch", foods["chicken"], 180), ("Lunch", foods["rice"], 220), ("Lunch", foods["broccoli"], 140),
             ("Dinner", foods["salmon"], 190), ("Snack", foods["almonds"], 35)],
            [("Breakfast", foods["oats"], 70), ("Lunch", foods["chicken"], 200), ("Lunch", foods["rice"], 180),
             ("Dinner", foods["salmon"], 160), ("Dinner", foods["broccoli"], 180), ("Snack", foods["banana"], 120)],
            [("Breakfast", foods["eggs"], 120), ("Lunch", foods["chicken"], 160), ("Lunch", foods["rice"], 200),
             ("Dinner", foods["salmon"], 200), ("Snack", foods["almonds"], 28)],
        ]

        for offset in range(10):
            day = (today - timedelta(days=offset)).isoformat()
            meals = daily_sets[offset % len(daily_sets)]
            for idx, (meal, food, grams) in enumerate(meals):
                eaten = portion(food, grams)
                per100 = {k: float(food.get(k) or 0) for k in TRACKED}
                con.execute(
                    """insert into food_log(user_id,logged_at,eaten_on,meal,source,source_id,description,category,grams,nutrients_per100_json,nutrients_portion_json)
                       values(?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        uid,
                        f"{day}T{8 + idx:02d}:00:00",
                        day,
                        meal,
                        food["source"],
                        food["source_id"],
                        food["name"],
                        food.get("category", ""),
                        grams,
                        json.dumps(per100),
                        json.dumps(eaten),
                    ),
                )
            con.execute("insert or replace into hydration(user_id,eaten_on,ml) values(?,?,?)", (uid, day, 2200 + (offset % 3) * 300))

        con.execute(
            "insert or replace into daily_notes(user_id,eaten_on,note) values(?,?,?)",
            (uid, today.isoformat(), "Meal prep complete. Add fruit with dinner and finish the water goal."),
        )
        for offset, kg in [(14, 83.1), (10, 82.8), (7, 82.5), (3, 82.2), (0, 82.0)]:
            con.execute(
                "insert into weight_log(user_id,logged_on,weight_kg) values(?,?,?)",
                (uid, (today - timedelta(days=offset)).isoformat(), kg),
            )

        for food in (foods["chicken"], foods["rice"], foods["salmon"], foods["banana"]):
            per100 = {k: float(food.get(k) or 0) for k in TRACKED}
            con.execute(
                """insert or ignore into favorites(user_id,source_key,source_id,source,name,category,nutrients_per100_json)
                   values(?,?,?,?,?,?,?)""",
                (uid, food["source_key"], food["source_id"], food["source"], food["name"], food.get("category", ""), json.dumps(per100)),
            )

    print(f"Seeded demo account: {USERNAME} / {PASSWORD}")
    print(f"Database: {os.environ['MANNAH_WEB_DB']}")


if __name__ == "__main__":
    main()
