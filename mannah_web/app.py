from __future__ import annotations

import json
import os
import re
import sqlite3
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta
from functools import wraps
from pathlib import Path

from flask import Flask, Response, flash, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

ROOT = Path(__file__).resolve().parents[1]
FOOD_DB = ROOT / "pot_of_mannah" / "data" / "food.db"
APP_DB = Path(os.environ.get("MANNAH_WEB_DB", ROOT / "mannah_web.db"))
USDA_API_KEY = os.environ.get("USDA_API_KEY", "DEMO_KEY")
USER_AGENT = "PotOfMannah-Web/5.0"
ADMIN_USERNAME = os.environ.get("MANNAH_ADMIN_USERNAME", "admin").strip() or "admin"
ADMIN_PASSWORD = os.environ.get("MANNAH_ADMIN_PASSWORD", "MannahAdmin2026!")

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "pot-of-mannah-local-change-me")

# Canonical Pot of Mannah fields. Source values are per 100 grams.
NUTRIENTS = {
    "calories": ("Data_Kilocalories", "kcal"),
    "protein": ("Data_Protein", "g"),
    "carbs": ("Data_Carbohydrate", "g"),
    "fat": ("Data_Fat_Total_Lipid", "g"),
    "fiber": ("Data_Fiber", "g"),
    "sugar": ("Data_Sugar_Total", "g"),
    "sat_fat": ("Data_Fat_Saturated_Fat", "g"),
    "mono_fat": ("Data_Fat_Monosaturated_Fat", "g"),
    "poly_fat": ("Data_Fat_Polysaturated_Fat", "g"),
    "cholesterol": ("Data_Cholesterol", "mg"),
    "calcium": ("Data_Major_Minerals_Calcium", "mg"),
    "copper": ("Data_Major_Minerals_Copper", "mg"),
    "iron": ("Data_Major_Minerals_Iron", "mg"),
    "magnesium": ("Data_Major_Minerals_Magnesium", "mg"),
    "phosphorus": ("Data_Major_Minerals_Phosphorus", "mg"),
    "potassium": ("Data_Major_Minerals_Potassium", "mg"),
    "sodium": ("Data_Major_Minerals_Sodium", "mg"),
    "zinc": ("Data_Major_Minerals_Zinc", "mg"),
    "selenium": ("Data_Selenium", "µg"),
    "manganese": ("Data_Manganese", "mg"),
    "vitamin_a_rae": ("Data_Vitamins_Vitamin_A_RAE", "µg"),
    "vitamin_b6": ("Data_Vitamins_Vitamin_B6", "mg"),
    "vitamin_b12": ("Data_Vitamins_Vitamin_B12", "µg"),
    "vitamin_c": ("Data_Vitamins_Vitamin_C", "mg"),
    "vitamin_e": ("Data_Vitamins_Vitamin_E", "mg"),
    "vitamin_k": ("Data_Vitamins_Vitamin_K", "µg"),
    "niacin": ("Data_Niacin", "mg"),
    "riboflavin": ("Data_Riboflavin", "mg"),
    "thiamin": ("Data_Thiamin", "mg"),
    "pantothenic_acid": ("Data_Pantothenic_Acid", "mg"),
    "choline": ("Data_Choline", "mg"),
    "water": ("Data_Water", "g"),
}
TRACKED = list(NUTRIENTS)

LABELS = {
    "calories": "Calories", "protein": "Protein", "carbs": "Carbohydrates", "fat": "Fat",
    "fiber": "Fiber", "sugar": "Total sugar", "sat_fat": "Saturated fat", "mono_fat": "Monounsaturated fat",
    "poly_fat": "Polyunsaturated fat", "cholesterol": "Cholesterol", "calcium": "Calcium", "copper": "Copper",
    "iron": "Iron", "magnesium": "Magnesium", "phosphorus": "Phosphorus", "potassium": "Potassium",
    "sodium": "Sodium", "zinc": "Zinc", "selenium": "Selenium", "manganese": "Manganese",
    "vitamin_a_rae": "Vitamin A", "vitamin_b6": "Vitamin B6", "vitamin_b12": "Vitamin B12",
    "vitamin_c": "Vitamin C", "vitamin_e": "Vitamin E", "vitamin_k": "Vitamin K", "niacin": "Niacin",
    "riboflavin": "Riboflavin", "thiamin": "Thiamin", "pantothenic_acid": "Pantothenic acid",
    "choline": "Choline", "water": "Water",
}


def number(value, default=0.0):
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return default


def app_db():
    con = sqlite3.connect(APP_DB)
    con.row_factory = sqlite3.Row
    con.execute("pragma foreign_keys=on")
    return con


def food_db():
    con = sqlite3.connect(f"file:{FOOD_DB}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    return con


def init_db():
    with app_db() as con:
        con.executescript("""
        create table if not exists users(
          id integer primary key, name text not null, username text unique, email text not null unique,
          password_hash text not null, is_admin integer not null default 0, created_at text not null default current_timestamp);
        create table if not exists profiles(
          user_id integer primary key references users(id) on delete cascade,
          age integer, sex text, height_cm real, weight_kg real, activity text default 'moderate',
          calorie_goal real, protein_goal real, fiber_goal real, water_goal_ml real default 2500);
        create table if not exists custom_foods(
          id integer primary key, user_id integer references users(id) on delete cascade,
          source text not null default 'Custom', source_id text, name text not null, category text default 'CUSTOM',
          brand text default '', nutrients_json text not null, created_at text not null default current_timestamp);
        create table if not exists food_log(
          id integer primary key, user_id integer not null references users(id) on delete cascade,
          logged_at text not null, eaten_on text not null, meal text not null default 'Meal',
          source text not null, source_id text, description text not null, category text default '',
          grams real not null, nutrients_per100_json text not null, nutrients_portion_json text not null);
        create table if not exists favorites(
          id integer primary key, user_id integer not null references users(id) on delete cascade,
          source_key text not null, source_id text not null, source text not null, name text not null,
          category text default '', nutrients_per100_json text not null, created_at text not null default current_timestamp,
          unique(user_id,source_key,source_id));
        create table if not exists hydration(
          user_id integer not null references users(id) on delete cascade, eaten_on text not null, ml real not null default 0,
          primary key(user_id,eaten_on));
        create table if not exists daily_notes(
          user_id integer not null references users(id) on delete cascade, eaten_on text not null, note text not null default '',
          primary key(user_id,eaten_on));
        create table if not exists weight_log(
          id integer primary key, user_id integer not null references users(id) on delete cascade,
          logged_on text not null, weight_kg real not null, created_at text not null default current_timestamp);
        create index if not exists idx_foodlog_user_day on food_log(user_id,eaten_on);
        create index if not exists idx_custom_foods_user_name on custom_foods(user_id,name);
        create index if not exists idx_weight_user_day on weight_log(user_id,logged_on);
        """)
        # Migrate older web databases without breaking existing accounts.
        columns = {r[1] for r in con.execute("pragma table_info(users)").fetchall()}
        if "username" not in columns:
            con.execute("alter table users add column username text")
        if "is_admin" not in columns:
            con.execute("alter table users add column is_admin integer not null default 0")
        profile_columns = {r[1] for r in con.execute("pragma table_info(profiles)").fetchall()}
        for col, ddl in {
            "calorie_goal": "real", "protein_goal": "real", "fiber_goal": "real", "water_goal_ml": "real default 2500"
        }.items():
            if col not in profile_columns:
                con.execute(f"alter table profiles add column {col} {ddl}")
        rows = con.execute("select id,name,email,username from users order by id").fetchall()
        used = {str(r["username"]).lower() for r in rows if r["username"]}
        for r in rows:
            if r["username"]:
                continue
            base = re.sub(r"[^a-z0-9_]+", "", (r["name"] or "user").lower().replace(" ", "_")) or f"user{r['id']}"
            candidate = base
            n = 2
            while candidate.lower() in used:
                candidate = f"{base}{n}"; n += 1
            used.add(candidate.lower())
            con.execute("update users set username=? where id=?", (candidate, r["id"]))
        con.execute("create unique index if not exists idx_users_username on users(username collate nocase)")
        # A local admin is always available. Override credentials with MANNAH_ADMIN_USERNAME / MANNAH_ADMIN_PASSWORD.
        admin = con.execute("select * from users where lower(username)=lower(?)", (ADMIN_USERNAME,)).fetchone()
        if admin:
            con.execute("update users set is_admin=1 where id=?", (admin["id"],))
        else:
            email = f"{re.sub(r'[^a-z0-9]+','-',ADMIN_USERNAME.lower()).strip('-') or 'admin'}@local.invalid"
            con.execute("insert into users(name,username,email,password_hash,is_admin) values(?,?,?,?,1)",
                        ("Administrator", ADMIN_USERNAME, email, generate_password_hash(ADMIN_PASSWORD)))


def login_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapped


def admin_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login"))
        if not session.get("is_admin"):
            flash("Admin access required.", "error")
            return redirect(url_for("dashboard"))
        return fn(*args, **kwargs)
    return wrapped


def food_count():
    with food_db() as con:
        return con.execute("select count(*) from food_data").fetchone()[0]


def food_from_row(row):
    n = {key: number(row[col]) for key, (col, _) in NUTRIENTS.items()}
    raw_name = (row["Description"] or "Food").strip()
    display = raw_name.replace(",", ", ").replace("  ", " ").title()
    return {
        "source": "Pot of Mannah", "source_key": "mannah",
        "source_id": str(row["Nutrient_Data_Bank_Number"] or row["rid"]),
        "name": display, "category": (row["Category"] or "").title(), "brand": "",
        "serving": row["Data_Household_Weights_2nd_Household_Weight_Description"] or "",
        **n,
    }


def search_mannah(query, limit=30):
    q = query.strip()
    cols = ",".join(col for col, _ in NUTRIENTS.values())
    sql = f"""select rowid rid,Category,Description,Nutrient_Data_Bank_Number,
      Data_Household_Weights_2nd_Household_Weight_Description,{cols}
      from food_data
      where Description like ? or Category like ?
      order by case when Description like ? then 0 else 1 end, length(Description), Description limit ?"""
    needle, prefix = f"%{q}%", f"{q}%"
    with food_db() as con:
        return [food_from_row(r) for r in con.execute(sql, (needle, needle, prefix, limit)).fetchall()]


def get_mannah_food(source_id):
    cols = ",".join(col for col, _ in NUTRIENTS.values())
    sql = f"""select rowid rid,Category,Description,Nutrient_Data_Bank_Number,
      Data_Household_Weights_2nd_Household_Weight_Description,{cols}
      from food_data where Nutrient_Data_Bank_Number=? limit 1"""
    with food_db() as con:
        row = con.execute(sql, (str(source_id),)).fetchone()
        return food_from_row(row) if row else None


def custom_food_from_row(row):
    n = json.loads(row["nutrients_json"] or "{}")
    return {"source": row["source"], "source_key": "custom", "source_id": str(row["id"]),
            "name": row["name"], "category": row["category"], "brand": row["brand"], "serving": "", **n}


def search_custom(user_id, query, limit=12):
    with app_db() as con:
        rows = con.execute("select * from custom_foods where user_id=? and name like ? order by name limit ?",
                           (user_id, f"%{query.strip()}%", limit)).fetchall()
    return [custom_food_from_row(r) for r in rows]


def get_custom(user_id, row_id):
    with app_db() as con:
        r = con.execute("select * from custom_foods where id=? and user_id=?", (row_id, user_id)).fetchone()
    return custom_food_from_row(r) if r else None


def portion(per100, grams):
    f = max(number(grams), 0) / 100.0
    return {k: number(per100.get(k)) * f for k in TRACKED}


def calorie_target(profile):
    if not profile or not profile["age"]:
        return None
    age = int(profile["age"])
    sex = profile["sex"] or ""
    activity = profile["activity"] or "moderate"
    youth = {
        2:{"male":(1000,1000,1000),"female":(1000,1000,1000)}, 3:{"male":(1000,1400,1400),"female":(1000,1200,1400)},
        4:{"male":(1200,1400,1600),"female":(1200,1400,1400)}, 5:{"male":(1200,1400,1600),"female":(1200,1400,1600)},
        6:{"male":(1400,1600,1800),"female":(1200,1400,1600)}, 7:{"male":(1400,1600,1800),"female":(1200,1600,1800)},
        8:{"male":(1400,1600,2000),"female":(1400,1600,1800)}, 9:{"male":(1600,1800,2000),"female":(1400,1600,1800)},
        10:{"male":(1600,1800,2200),"female":(1400,1800,2000)},11:{"male":(1800,2000,2200),"female":(1600,1800,2000)},
        12:{"male":(1800,2200,2400),"female":(1600,2000,2200)},13:{"male":(2000,2200,2600),"female":(1600,2000,2200)},
        14:{"male":(2000,2400,2800),"female":(1800,2000,2400)},15:{"male":(2200,2600,3000),"female":(1800,2000,2400)},
        16:{"male":(2400,2800,3200),"female":(1800,2000,2400)},17:{"male":(2400,2800,3200),"female":(1800,2000,2400)},
    }
    if age < 18:
        if sex not in ("male", "female") or age not in youth:
            return None
        idx = 0 if activity == "sedentary" else 2 if activity in ("active", "very") else 1
        return youth[age][sex][idx]
    if sex not in ("male", "female") or not profile["height_cm"] or not profile["weight_kg"]:
        return None
    bmr = 10 * float(profile["weight_kg"]) + 6.25 * float(profile["height_cm"]) - 5 * age + (5 if sex == "male" else -161)
    factor = {"sedentary":1.2,"light":1.375,"moderate":1.55,"active":1.725,"very":1.9}.get(activity, 1.55)
    return round(bmr * factor)


def targets(profile):
    age = int(profile["age"]) if profile and profile["age"] else 30
    sex = profile["sex"] if profile else ""
    weight = number(profile["weight_kg"]) if profile and profile["weight_kg"] else None
    cal = calorie_target(profile)
    # Age-aware reference goals. Values are informational references, not medical prescriptions.
    if age <= 3:
        p, ca, fe, mg, k, zn, se, va, b6, b12, vc, ve, vk, ch = 13,700,7,80,2000,3,20,300,0.5,0.9,15,6,30,200
    elif age <= 8:
        p, ca, fe, mg, k, zn, se, va, b6, b12, vc, ve, vk, ch = 19,1000,10,130,2300,5,30,400,0.6,1.2,25,7,55,250
    elif age <= 13:
        p, ca, fe, mg, k, zn, se, va, b6, b12, vc, ve, vk, ch = 34,1300,8,240,(2500 if sex=="male" else 2300),8,40,600,1.0,1.8,45,11,60,375
    elif age <= 18:
        if sex == "male": p,fe,mg,k,zn,va,vc,vk,ch = 52,11,410,3000,11,900,75,75,550
        else: p,fe,mg,k,zn,va,vc,vk,ch = 46,15,360,2300,9,700,65,75,400
        ca,se,b6,b12,ve = 1300,55,1.3,2.4,15
    else:
        p = round(weight * .8,1) if weight else (56 if sex=="male" else 46)
        ca = 1200 if age >= 71 or (sex=="female" and age>=51) else 1000
        fe = 8 if sex=="male" or age>=51 else 18
        mg = 420 if sex=="male" and age>=31 else 400 if sex=="male" else 320 if age>=31 else 310
        k = 3400 if sex=="male" else 2600; zn = 11 if sex=="male" else 8; se=55
        va = 900 if sex=="male" else 700; b6 = 1.7 if age>=51 and sex=="male" else 1.5 if age>=51 else 1.3
        b12=2.4; vc=90 if sex=="male" else 75; ve=15; vk=120 if sex=="male" else 90; ch=550 if sex=="male" else 425
    goal = {
        "calories": cal, "protein": p, "fiber": round((cal or 2000)*14/1000,1), "calcium":ca, "iron":fe,
        "magnesium":mg, "potassium":k, "zinc":zn, "selenium":se, "sodium":2300,
        "vitamin_a_rae":va, "vitamin_b6":b6, "vitamin_b12":b12, "vitamin_c":vc,
        "vitamin_e":ve, "vitamin_k":vk, "choline":ch,
    }
    if profile:
        if number(profile["calorie_goal"]) > 0: goal["calories"] = round(number(profile["calorie_goal"]))
        if number(profile["protein_goal"]) > 0: goal["protein"] = round(number(profile["protein_goal"]),1)
        if number(profile["fiber_goal"]) > 0: goal["fiber"] = round(number(profile["fiber_goal"]),1)
    return goal


def day_data(user_id, day):
    totals = {k:0.0 for k in TRACKED}
    with app_db() as con:
        rows = con.execute("select * from food_log where user_id=? and eaten_on=? order by logged_at,id", (user_id, day)).fetchall()
    entries=[]
    for r in rows:
        vals=json.loads(r["nutrients_portion_json"])
        for k in TRACKED: totals[k]+=number(vals.get(k))
        entries.append({"row":r,"nutrients":vals})
    return entries, totals


def profile_for(user_id):
    with app_db() as con:
        return con.execute("select * from profiles where user_id=?", (user_id,)).fetchone()


def favorite_foods(user_id, limit=12):
    with app_db() as con:
        rows = con.execute("select * from favorites where user_id=? order by created_at desc limit ?", (user_id, limit)).fetchall()
    out=[]
    for r in rows:
        vals=json.loads(r["nutrients_per100_json"] or "{}")
        out.append({"source_key":r["source_key"],"source_id":r["source_id"],"source":r["source"],"name":r["name"],"category":r["category"] or "Food","serving":"",**vals})
    return out


def recent_foods(user_id, limit=12):
    with app_db() as con:
        rows=con.execute("""
            select * from food_log where user_id=? group by source,source_id,description
            order by max(logged_at) desc limit ?
        """,(user_id,limit)).fetchall()
    out=[]
    for r in rows:
        vals=json.loads(r["nutrients_per100_json"] or "{}")
        out.append({"source_key":"mannah" if r["source"]=="Pot of Mannah" else "custom",
                    "source_id":str(r["source_id"]),"source":r["source"],"name":r["description"],
                    "category":r["category"] or "Food","serving":"",**vals})
    return out


def hydration_for(user_id, day):
    with app_db() as con:
        row=con.execute("select ml from hydration where user_id=? and eaten_on=?",(user_id,day)).fetchone()
    return number(row["ml"]) if row else 0.0


def note_for(user_id, day):
    with app_db() as con:
        row=con.execute("select note from daily_notes where user_id=? and eaten_on=?",(user_id,day)).fetchone()
    return row["note"] if row else ""


def logging_streak(user_id):
    with app_db() as con:
        days={r[0] for r in con.execute("select distinct eaten_on from food_log where user_id=?",(user_id,)).fetchall()}
    streak=0; d=date.today()
    while d.isoformat() in days:
        streak+=1; d-=timedelta(days=1)
    return streak


def status_rows(total, goal):
    rows=[]
    for key,target in goal.items():
        if key=="calories" or not target: continue
        val=number(total.get(key)); pct=(val/target*100) if target else 0
        upper = key=="sodium"
        if upper:
            state="high" if pct>100 else "warn" if pct>80 else "good"
            note="over limit" if pct>100 else "near limit" if pct>80 else "within limit"
        else:
            state="low" if pct<50 else "warn" if pct<90 else "good" if pct<=130 else "high"
            note="low" if pct<50 else "getting there" if pct<90 else "on target" if pct<=130 else "above target"
        rows.append({"key":key,"label":LABELS.get(key,key),"value":val,"target":target,"unit":NUTRIENTS[key][1],"pct":min(pct,100),"raw_pct":pct,"state":state,"note":note,"missing":max(target-val,0)})
    return sorted(rows,key=lambda x:(x["raw_pct"] if x["key"]!="sodium" else 200-x["raw_pct"]))


def nutrition_score(stats):
    if not stats:
        return 0
    scores=[]
    for row in stats:
        if row["key"] == "sodium":
            # Staying under the sodium reference earns full credit; going above tapers the score.
            scores.append(100 if row["raw_pct"] <= 100 else max(0, 200-row["raw_pct"]))
        else:
            scores.append(min(row["raw_pct"],100))
    return round(sum(scores)/len(scores)) if scores else 0


def nutrient_food_suggestions(key, limit=6):
    if key not in NUTRIENTS or key in ("calories", "sodium"):
        return []
    nutrient_col=NUTRIENTS[key][0]
    cols=",".join(col for col,_ in NUTRIENTS.values())
    sql=f"""select rowid rid,Category,Description,Nutrient_Data_Bank_Number,
      Data_Household_Weights_2nd_Household_Weight_Description,{cols}
      from food_data
      where cast({nutrient_col} as real) > 0
        and cast(Data_Kilocalories as real) between 15 and 900
        and upper(Description) not like '%INFANT%'
        and upper(Description) not like '%BABYFOOD%'
        and upper(Description) not like '%FORMULA%'
      order by cast({nutrient_col} as real) desc limit 240"""
    with food_db() as con:
        rows=con.execute(sql).fetchall()
    ranked=[]
    for row in rows:
        food=food_from_row(row)
        value=number(food.get(key))
        kcal=max(number(food.get("calories")),80)
        # Blend absolute amount and calorie density so suggestions are useful without being only spices/oils.
        density=value/kcal*100
        score=value*(0.65)+(density*0.35)
        ranked.append((score,food))
    ranked.sort(key=lambda x:x[0],reverse=True)
    out=[]; seen_categories=set(); seen_names=set()
    for _,food in ranked:
        cat=(food.get("category") or "Food").lower(); name=food["name"].lower()
        if name in seen_names: continue
        if cat in seen_categories and len(out) < max(2,limit//2): continue
        food=dict(food); food["focus_value"]=number(food.get(key)); food["focus_key"]=key
        out.append(food); seen_categories.add(cat); seen_names.add(name)
        if len(out)>=limit: break
    if len(out)<limit:
        for _,food in ranked:
            if food["name"].lower() in seen_names: continue
            food=dict(food); food["focus_value"]=number(food.get(key)); food["focus_key"]=key
            out.append(food); seen_names.add(food["name"].lower())
            if len(out)>=limit: break
    return out


def biggest_gaps(stats, limit=6):
    rows=[s for s in stats if s["key"]!="sodium" and s["raw_pct"]<100]
    rows.sort(key=lambda s:s["raw_pct"])
    return rows[:limit]


def achievement_data(user_id):
    with app_db() as con:
        log_count=con.execute("select count(*) from food_log where user_id=?",(user_id,)).fetchone()[0]
        unique_foods=con.execute("select count(distinct source||':'||coalesce(source_id,description)) from food_log where user_id=?",(user_id,)).fetchone()[0]
        logged_days=con.execute("select count(distinct eaten_on) from food_log where user_id=?",(user_id,)).fetchone()[0]
        water_days=con.execute("select count(*) from hydration where user_id=? and ml>0",(user_id,)).fetchone()[0]
        favs=con.execute("select count(*) from favorites where user_id=?",(user_id,)).fetchone()[0]
    streak=logging_streak(user_id)
    return [
        {"name":"First bite","icon":"✦","done":log_count>=1,"detail":f"{log_count} foods logged","target":"Log your first food"},
        {"name":"Seven-day rhythm","icon":"🔥","done":streak>=7,"detail":f"{streak} day streak","target":"Reach a 7-day streak"},
        {"name":"Food explorer","icon":"⌕","done":unique_foods>=25,"detail":f"{unique_foods} unique foods","target":"Try 25 different foods"},
        {"name":"Consistency","icon":"◫","done":logged_days>=14,"detail":f"{logged_days} days logged","target":"Log on 14 different days"},
        {"name":"Hydration habit","icon":"◌","done":water_days>=7,"detail":f"{water_days} water days","target":"Track water on 7 days"},
        {"name":"Quick shelf","icon":"★","done":favs>=5,"detail":f"{favs} favorites","target":"Favorite 5 foods"},
    ]


def remote_json(url, data=None, timeout=4):
    headers={"User-Agent":USER_AGENT,"Accept":"application/json"}; body=None
    if data is not None:
        body=json.dumps(data).encode(); headers["Content-Type"]="application/json"
    req=urllib.request.Request(url,data=body,headers=headers,method="POST" if body else "GET")
    with urllib.request.urlopen(req,timeout=timeout) as resp: return json.loads(resp.read().decode())


def off_item(p):
    n=p.get("nutriments") or {}; name=(p.get("product_name_en") or p.get("product_name") or "").strip()
    if not name:return None
    def gmg(k): return number(n.get(k))*1000
    def gmcg(k): return number(n.get(k))*1_000_000
    return {"source":"Open Food Facts","source_key":"off","source_id":str(p.get("code") or ""),"name":name,"brand":p.get("brands") or "","category":"Packaged food","serving":p.get("serving_size") or "",
            "calories":number(n.get("energy-kcal_100g")),"protein":number(n.get("proteins_100g")),"carbs":number(n.get("carbohydrates_100g")),"fat":number(n.get("fat_100g")),"fiber":number(n.get("fiber_100g")),"sugar":number(n.get("sugars_100g")),"sat_fat":number(n.get("saturated-fat_100g")),"mono_fat":0,"poly_fat":0,"cholesterol":gmg("cholesterol_100g"),"calcium":gmg("calcium_100g"),"copper":gmg("copper_100g"),"iron":gmg("iron_100g"),"magnesium":gmg("magnesium_100g"),"phosphorus":gmg("phosphorus_100g"),"potassium":gmg("potassium_100g"),"sodium":gmg("sodium_100g"),"zinc":gmg("zinc_100g"),"selenium":gmcg("selenium_100g"),"manganese":gmg("manganese_100g"),"vitamin_a_rae":gmcg("vitamin-a_100g"),"vitamin_b6":gmg("vitamin-b6_100g"),"vitamin_b12":gmcg("vitamin-b12_100g"),"vitamin_c":gmg("vitamin-c_100g"),"vitamin_e":gmg("vitamin-e_100g"),"vitamin_k":gmcg("vitamin-k_100g"),"niacin":gmg("vitamin-pp_100g"),"riboflavin":gmg("vitamin-b2_100g"),"thiamin":gmg("vitamin-b1_100g"),"pantothenic_acid":gmg("pantothenic-acid_100g"),"choline":gmg("choline_100g"),"water":0}


def search_off(query, limit=10):
    params=urllib.parse.urlencode({"action":"process","search_simple":"1","search_terms":query,"json":"1","page_size":limit,"fields":"code,product_name,product_name_en,brands,nutriments,serving_size"})
    data=remote_json("https://world.openfoodfacts.org/cgi/search.pl?"+params)
    return [x for x in (off_item(p) for p in data.get("products",[])) if x]


def usda_value(food,names,unit=None):
    names={n.lower() for n in names}
    for e in food.get("foodNutrients") or []:
        nn=e.get("nutrient") or {}; name=(e.get("nutrientName") or nn.get("name") or "").lower(); u=(e.get("unitName") or nn.get("unitName") or "").upper()
        if name in names and (not unit or u==unit.upper()): return number(e.get("value") if "value" in e else e.get("amount"))
    return 0


def usda_item(food):
    name=(food.get("description") or "").strip()
    if not name:return None
    get=lambda names,unit=None: usda_value(food,set(names),unit)
    return {"source":"USDA FoodData Central","source_key":"usda","source_id":str(food.get("fdcId") or ""),"name":name.title() if name.isupper() else name,"brand":food.get("brandName") or food.get("brandOwner") or "","category":food.get("dataType") or "USDA","serving":food.get("householdServingFullText") or "",
            "calories":get(["Energy"],"KCAL"),"protein":get(["Protein"],"G"),"carbs":get(["Carbohydrate, by difference","Carbohydrate, by summation"],"G"),"fat":get(["Total lipid (fat)"],"G"),"fiber":get(["Fiber, total dietary"],"G"),"sugar":get(["Sugars, total including NLEA","Total Sugars","Sugars, total"],"G"),"sat_fat":get(["Fatty acids, total saturated"],"G"),"mono_fat":get(["Fatty acids, total monounsaturated"],"G"),"poly_fat":get(["Fatty acids, total polyunsaturated"],"G"),"cholesterol":get(["Cholesterol"],"MG"),"calcium":get(["Calcium, Ca"],"MG"),"copper":get(["Copper, Cu"],"MG"),"iron":get(["Iron, Fe"],"MG"),"magnesium":get(["Magnesium, Mg"],"MG"),"phosphorus":get(["Phosphorus, P"],"MG"),"potassium":get(["Potassium, K"],"MG"),"sodium":get(["Sodium, Na"],"MG"),"zinc":get(["Zinc, Zn"],"MG"),"selenium":get(["Selenium, Se"],"UG"),"manganese":get(["Manganese, Mn"],"MG"),"vitamin_a_rae":get(["Vitamin A, RAE"],"UG"),"vitamin_b6":get(["Vitamin B-6"],"MG"),"vitamin_b12":get(["Vitamin B-12"],"UG"),"vitamin_c":get(["Vitamin C, total ascorbic acid"],"MG"),"vitamin_e":get(["Vitamin E (alpha-tocopherol)"],"MG"),"vitamin_k":get(["Vitamin K (phylloquinone)"],"UG"),"niacin":get(["Niacin"],"MG"),"riboflavin":get(["Riboflavin"],"MG"),"thiamin":get(["Thiamin"],"MG"),"pantothenic_acid":get(["Pantothenic acid"],"MG"),"choline":get(["Choline, total"],"MG"),"water":get(["Water"],"G")}


def search_usda(query,limit=10):
    url="https://api.nal.usda.gov/fdc/v1/foods/search?"+urllib.parse.urlencode({"api_key":USDA_API_KEY})
    data=remote_json(url,{"query":query,"pageSize":limit,"pageNumber":1})
    return [x for x in (usda_item(f) for f in data.get("foods",[])) if x]


def save_remote_food(user_id,item):
    n={k:number(item.get(k)) for k in TRACKED}
    with app_db() as con:
        existing=con.execute("select * from custom_foods where user_id=? and source=? and source_id=?",(user_id,item["source"],item["source_id"])).fetchone()
        if existing:return custom_food_from_row(existing)
        cur=con.execute("insert into custom_foods(user_id,source,source_id,name,category,brand,nutrients_json) values(?,?,?,?,?,?,?)",
                        (user_id,item["source"],item["source_id"],item["name"],item.get("category",""),item.get("brand",""),json.dumps(n)))
        row=con.execute("select * from custom_foods where id=?",(cur.lastrowid,)).fetchone()
    return custom_food_from_row(row)


@app.context_processor
def global_context():
    return {"today_iso":date.today().isoformat(),"food_total":food_count(),"labels":LABELS,"units":{k:v[1] for k,v in NUTRIENTS.items()}}


@app.route("/")
def index():
    return redirect(url_for("dashboard")) if session.get("user_id") else render_template("landing.html")


@app.route("/signup",methods=["GET","POST"])
def signup():
    if request.method=="POST":
        name=request.form.get("name","").strip(); username=request.form.get("username","").strip(); pw=request.form.get("password","")
        if not name or not re.fullmatch(r"[A-Za-z0-9_.-]{3,32}", username) or len(pw)<6:
            flash("Enter your name, a 3–32 character username, and a password of at least 6 characters.","error")
        else:
            try:
                email=f"{username.lower()}@local.invalid"
                with app_db() as con:
                    uid=con.execute("insert into users(name,username,email,password_hash,is_admin) values(?,?,?,?,0)",(name,username,email,generate_password_hash(pw))).lastrowid
                session.clear();session.update(user_id=uid,name=name,username=username,is_admin=False);return redirect(url_for("profile",first=1))
            except sqlite3.IntegrityError:
                flash("That username is already taken.","error")
    return render_template("signup.html")


@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        username=request.form.get("username","").strip()
        with app_db() as con: u=con.execute("select * from users where lower(username)=lower(?)",(username,)).fetchone()
        if u and check_password_hash(u["password_hash"],request.form.get("password","")):
            session.clear();session.update(user_id=u["id"],name=u["name"],username=u["username"],is_admin=bool(u["is_admin"]));return redirect(url_for("admin_dashboard") if u["is_admin"] else url_for("dashboard"))
        flash("Incorrect username or password.","error")
    return render_template("login.html")


@app.route("/logout")
def logout(): session.clear(); return redirect(url_for("index"))


@app.route("/admin")
@admin_required
def admin_dashboard():
    with app_db() as con:
        stats = {
            "users": con.execute("select count(*) from users").fetchone()[0],
            "logs": con.execute("select count(*) from food_log").fetchone()[0],
            "custom_foods": con.execute("select count(*) from custom_foods").fetchone()[0],
            "favorites": con.execute("select count(*) from favorites").fetchone()[0],
            "water_days": con.execute("select count(*) from hydration where ml>0").fetchone()[0],
        }
        users = con.execute("""
            select u.id,u.name,u.username,u.is_admin,u.created_at,
                   count(distinct f.id) log_count,count(distinct c.id) custom_count
            from users u
            left join food_log f on f.user_id=u.id
            left join custom_foods c on c.user_id=u.id
            group by u.id order by u.is_admin desc,u.created_at desc
        """).fetchall()
    return render_template("admin.html",stats=stats,users=users)


@app.post("/admin/delete-user/<int:user_id>")
@admin_required
def admin_delete_user(user_id):
    if user_id == session.get("user_id"):
        flash("You cannot delete the account you are currently using.", "error")
    else:
        with app_db() as con:
            target=con.execute("select username,is_admin from users where id=?",(user_id,)).fetchone()
            if not target:
                flash("Account not found.","error")
            elif target["is_admin"]:
                flash("Admin accounts cannot be deleted here.","error")
            else:
                con.execute("delete from users where id=?",(user_id,))
                flash(f"Deleted @{target['username']} and its local logs.","success")
    return redirect(url_for("admin_dashboard"))


@app.post("/admin/change-password")
@admin_required
def admin_change_password():
    current=request.form.get("current_password",""); new=request.form.get("new_password","")
    with app_db() as con:
        u=con.execute("select * from users where id=?",(session["user_id"],)).fetchone()
        if not u or not check_password_hash(u["password_hash"],current):
            flash("Current password is incorrect.","error")
        elif len(new)<8:
            flash("Use at least 8 characters for the new admin password.","error")
        else:
            con.execute("update users set password_hash=? where id=?",(generate_password_hash(new),u["id"]))
            flash("Admin password changed.","success")
    return redirect(url_for("admin_dashboard"))


@app.route("/profile",methods=["GET","POST"])
@login_required
def profile():
    p=profile_for(session["user_id"])
    if request.method=="POST":
        age=request.form.get("age",type=int); sex=request.form.get("sex","")
        height=request.form.get("height_cm",type=float); weight=request.form.get("weight_kg",type=float)
        activity=request.form.get("activity","moderate")
        calorie_goal=request.form.get("calorie_goal",type=float); protein_goal=request.form.get("protein_goal",type=float)
        fiber_goal=request.form.get("fiber_goal",type=float); water_goal=request.form.get("water_goal_ml",type=float)
        if not age or age<1 or age>120:
            flash("Enter a valid age.","error")
        else:
            with app_db() as con:
                con.execute("""insert into profiles(user_id,age,sex,height_cm,weight_kg,activity,calorie_goal,protein_goal,fiber_goal,water_goal_ml)
                    values(?,?,?,?,?,?,?,?,?,?) on conflict(user_id) do update set age=excluded.age,sex=excluded.sex,
                    height_cm=excluded.height_cm,weight_kg=excluded.weight_kg,activity=excluded.activity,
                    calorie_goal=excluded.calorie_goal,protein_goal=excluded.protein_goal,fiber_goal=excluded.fiber_goal,
                    water_goal_ml=excluded.water_goal_ml""",
                    (session["user_id"],age,sex,height,weight,activity,calorie_goal,protein_goal,fiber_goal,water_goal or 2500))
                if weight and weight>0:
                    today=date.today().isoformat()
                    last=con.execute("select weight_kg from weight_log where user_id=? and logged_on=? order by id desc limit 1",(session["user_id"],today)).fetchone()
                    if not last or abs(number(last["weight_kg"])-weight)>.01:
                        con.execute("insert into weight_log(user_id,logged_on,weight_kg) values(?,?,?)",(session["user_id"],today,weight))
            flash("Account goals updated.","success")
            return redirect(url_for("dashboard"))
    with app_db() as con:
        weights=con.execute("select logged_on,weight_kg from weight_log where user_id=? order by logged_on desc,id desc limit 12",(session["user_id"],)).fetchall()
    return render_template("profile.html",profile=p,first=request.args.get("first"),weights=weights)


@app.post("/account/password")
@login_required
def change_password():
    current=request.form.get("current_password",""); new=request.form.get("new_password","")
    with app_db() as con:
        u=con.execute("select * from users where id=?",(session["user_id"],)).fetchone()
        if not u or not check_password_hash(u["password_hash"],current):
            flash("Current password is incorrect.","error")
        elif len(new)<8:
            flash("Use at least 8 characters for the new password.","error")
        else:
            con.execute("update users set password_hash=? where id=?",(generate_password_hash(new),u["id"]))
            flash("Password changed.","success")
    return redirect(url_for("profile"))


@app.route("/dashboard")
@login_required
def dashboard():
    p=profile_for(session["user_id"])
    if not p:
        return redirect(url_for("profile",first=1))
    day=request.args.get("day") or date.today().isoformat()
    entries,total=day_data(session["user_id"],day)
    goal=targets(p)
    stats=status_rows(total,goal)
    missing=[s for s in stats if s["key"]!="sodium" and s["raw_pct"]<90][:4]
    calgoal=goal.get("calories") or 0
    calpct=min((total["calories"]/calgoal*100) if calgoal else 0,100)
    water=hydration_for(session["user_id"],day)
    water_goal=number(p["water_goal_ml"]) or 2500
    water_pct=min(water/water_goal*100 if water_goal else 0,100)
    meals={m:[] for m in ["Breakfast","Lunch","Dinner","Snack","Meal"]}
    for e in entries:
        meals.setdefault(e["row"]["meal"],[]).append(e)
    recent_entries=list(reversed(entries[-5:]))
    return render_template(
        "dashboard.html",day=day,entries=entries,recent_entries=recent_entries,total=total,
        goal=goal,stats=stats,missing=missing,calpct=calpct,meals=meals,water=water,
        water_goal=water_goal,water_pct=water_pct,streak=logging_streak(session["user_id"]),
        favorites=favorite_foods(session["user_id"],4),recent=recent_foods(session["user_id"],4)
    )


@app.route("/diary")
@login_required
def diary():
    p=profile_for(session["user_id"])
    if not p:
        return redirect(url_for("profile",first=1))
    day=request.args.get("day") or date.today().isoformat()
    entries,total=day_data(session["user_id"],day)
    goal=targets(p)
    meals={m:[] for m in ["Breakfast","Lunch","Dinner","Snack","Meal"]}
    for e in entries:
        meals.setdefault(e["row"]["meal"],[]).append(e)
    water=hydration_for(session["user_id"],day)
    water_goal=number(p["water_goal_ml"]) or 2500
    water_pct=min(water/water_goal*100 if water_goal else 0,100)
    note=note_for(session["user_id"],day)
    return render_template(
        "diary.html",day=day,entries=entries,total=total,goal=goal,meals=meals,
        water=water,water_goal=water_goal,water_pct=water_pct,note=note
    )


@app.route("/log",methods=["GET","POST"])
@login_required
def log_food():
    if request.method=="POST":
        source_key=request.form.get("source_key")
        source_id=request.form.get("source_id")
        grams=number(request.form.get("grams"))
        meal=request.form.get("meal","Meal")
        day=request.form.get("eaten_on") or date.today().isoformat()
        food=get_mannah_food(source_id) if source_key=="mannah" else get_custom(session["user_id"],source_id) if source_key=="custom" else None
        if not food or grams<=0:
            flash("Choose a food and enter grams greater than zero.","error")
        else:
            per100={k:number(food.get(k)) for k in TRACKED}
            vals=portion(per100,grams)
            with app_db() as con:
                con.execute("insert into food_log(user_id,logged_at,eaten_on,meal,source,source_id,description,category,grams,nutrients_per100_json,nutrients_portion_json) values(?,?,?,?,?,?,?,?,?,?,?)",
                            (session["user_id"],datetime.now().isoformat(timespec="seconds"),day,meal,food["source"],food["source_id"],food["name"],food.get("category",""),grams,json.dumps(per100),json.dumps(vals)))
            flash(f"Logged {grams:g} g of {food['name']}.","success")
            return redirect(url_for("diary",day=day))
    default_day=request.args.get("day") or date.today().isoformat()
    default_meal=request.args.get("meal") or "Meal"
    return render_template(
        "log_food.html",favorites=favorite_foods(session["user_id"],12),
        recent=recent_foods(session["user_id"],12),default_day=default_day,default_meal=default_meal
    )


@app.post("/delete-log/<int:row_id>")
@login_required
def delete_log(row_id):
    day=request.form.get("day") or date.today().isoformat()
    with app_db() as con:
        con.execute("delete from food_log where id=? and user_id=?",(row_id,session["user_id"]))
    return redirect(url_for("diary",day=day))


@app.post("/relog/<int:row_id>")
@login_required
def relog(row_id):
    target=request.form.get("day") or date.today().isoformat()
    with app_db() as con:
        r=con.execute("select * from food_log where id=? and user_id=?",(row_id,session["user_id"])).fetchone()
        if r:
            con.execute("""insert into food_log(user_id,logged_at,eaten_on,meal,source,source_id,description,category,grams,nutrients_per100_json,nutrients_portion_json)
                values(?,?,?,?,?,?,?,?,?,?,?)""",
                (session["user_id"],datetime.now().isoformat(timespec="seconds"),target,r["meal"],r["source"],r["source_id"],r["description"],r["category"],r["grams"],r["nutrients_per100_json"],r["nutrients_portion_json"]))
            flash(f"Logged {r['description']} again.","success")
    return redirect(url_for("diary",day=target))


@app.post("/copy-yesterday")
@login_required
def copy_yesterday():
    target=request.form.get("day") or date.today().isoformat()
    td=date.fromisoformat(target)
    source=(td-timedelta(days=1)).isoformat()
    with app_db() as con:
        rows=con.execute("select * from food_log where user_id=? and eaten_on=?",(session["user_id"],source)).fetchall()
        for r in rows:
            con.execute("""insert into food_log(user_id,logged_at,eaten_on,meal,source,source_id,description,category,grams,nutrients_per100_json,nutrients_portion_json)
                values(?,?,?,?,?,?,?,?,?,?,?)""",
                (session["user_id"],datetime.now().isoformat(timespec="seconds"),target,r["meal"],r["source"],r["source_id"],r["description"],r["category"],r["grams"],r["nutrients_per100_json"],r["nutrients_portion_json"]))
    flash(f"Copied {len(rows)} food entr{'y' if len(rows)==1 else 'ies'} from yesterday.","success")
    return redirect(url_for("diary",day=target))


@app.post("/water")
@login_required
def water():
    day=request.form.get("day") or date.today().isoformat()
    delta=number(request.form.get("delta_ml"))
    set_value=request.form.get("set_ml")
    with app_db() as con:
        row=con.execute("select ml from hydration where user_id=? and eaten_on=?",(session["user_id"],day)).fetchone()
        current=number(row["ml"]) if row else 0
        value=max(number(set_value) if set_value not in (None,"") else current+delta,0)
        con.execute("insert into hydration(user_id,eaten_on,ml) values(?,?,?) on conflict(user_id,eaten_on) do update set ml=excluded.ml",(session["user_id"],day,value))
    return redirect(url_for("diary",day=day))


@app.post("/daily-note")
@login_required
def daily_note():
    day=request.form.get("day") or date.today().isoformat()
    note=(request.form.get("note") or "").strip()[:1000]
    with app_db() as con:
        con.execute("insert into daily_notes(user_id,eaten_on,note) values(?,?,?) on conflict(user_id,eaten_on) do update set note=excluded.note",(session["user_id"],day,note))
    flash("Daily note saved.","success")
    return redirect(url_for("diary",day=day))


@app.route("/nutrition")
@login_required
def nutrition():
    p=profile_for(session["user_id"])
    if not p:
        return redirect(url_for("profile",first=1))
    day=request.args.get("day") or date.today().isoformat()
    entries,total=day_data(session["user_id"],day)
    goal=targets(p)
    stats=status_rows(total,goal)
    score=nutrition_score(stats)
    gaps=biggest_gaps(stats,6)
    gap_cards=[]
    for gap in gaps:
        gap_cards.append({"gap":gap,"foods":nutrient_food_suggestions(gap["key"],4)})
    met=sum(1 for s in stats if s["key"]!="sodium" and s["raw_pct"]>=90)
    total_targets=sum(1 for s in stats if s["key"]!="sodium")
    sodium=next((s for s in stats if s["key"]=="sodium"),None)
    macro_keys={"protein","fiber"}
    mineral_keys={"calcium","iron","magnesium","potassium","zinc","selenium"}
    groups={
        "Core":[s for s in stats if s["key"] in macro_keys or s["key"]=="sodium"],
        "Minerals":[s for s in stats if s["key"] in mineral_keys],
        "Vitamins":[s for s in stats if s["key"].startswith("vitamin_") or s["key"]=="choline"],
    }
    return render_template("nutrition.html",day=day,total=total,goal=goal,stats=stats,score=score,
                           gaps=gaps,gap_cards=gap_cards,met=met,total_targets=total_targets,sodium=sodium,groups=groups)


@app.route("/nutrient/<key>")
@login_required
def nutrient_detail(key):
    if key not in NUTRIENTS or key=="calories":
        return redirect(url_for("nutrition"))
    p=profile_for(session["user_id"])
    day=request.args.get("day") or date.today().isoformat()
    _,total=day_data(session["user_id"],day)
    goal=targets(p) if p else {}
    stat=next((s for s in status_rows(total,goal) if s["key"]==key),None)
    foods=nutrient_food_suggestions(key,18) if key!="sodium" else []
    return render_template("nutrient_detail.html",key=key,label=LABELS.get(key,key),unit=NUTRIENTS[key][1],
                           day=day,total=total,goal=goal,stat=stat,foods=foods)


@app.route("/planner")
@login_required
def planner():
    p=profile_for(session["user_id"])
    if not p:
        return redirect(url_for("profile",first=1))
    day=request.args.get("day") or date.today().isoformat()
    _,total=day_data(session["user_id"],day)
    goal=targets(p); stats=status_rows(total,goal); gaps=biggest_gaps(stats,4)
    suggestions=[]; seen=set()
    for gap in gaps:
        for food in nutrient_food_suggestions(gap["key"],5):
            key=(food["source_key"],food["source_id"])
            if key in seen: continue
            seen.add(key)
            item=dict(food); item["reason"]=gap["label"]; item["reason_key"]=gap["key"]
            item["reason_unit"]=gap["unit"]; item["reason_missing"]=gap["missing"]
            suggestions.append(item)
            if len(suggestions)>=12: break
        if len(suggestions)>=12: break
    return render_template("planner.html",day=day,total=total,goal=goal,gaps=gaps,suggestions=suggestions)


@app.route("/progress")
@app.route("/history")
@login_required
def progress():
    p=profile_for(session["user_id"])
    goal=targets(p) if p else {}
    selected_day=request.args.get("day") or date.today().isoformat()
    _,selected_total=day_data(session["user_id"],selected_day)
    selected_stats=status_rows(selected_total,goal) if goal else []
    end=date.today(); start=end-timedelta(days=29); days=[]
    for i in range(30):
        d=(start+timedelta(days=i)).isoformat(); _,total=day_data(session["user_id"],d)
        days.append({"day":d,"label":(start+timedelta(days=i)).strftime("%b %-d"),"total":total,"logged":total["calories"]>0})
    logged=[d for d in days if d["logged"]]
    avg={k:(sum(d["total"][k] for d in logged)/len(logged) if logged else 0) for k in ["calories","protein","carbs","fat","fiber"]}
    max_cal=max([d["total"]["calories"] for d in days]+[1])
    avg_total={k:(sum(d["total"].get(k,0) for d in logged)/len(logged) if logged else 0) for k in TRACKED}
    avg_stats=status_rows(avg_total,goal) if goal else []
    with app_db() as con:
        weights=con.execute("select logged_on,weight_kg from weight_log where user_id=? order by logged_on,id",(session["user_id"],)).fetchall()
    adherence=[]
    calgoal=number(goal.get("calories"))
    for d in days[-7:]:
        pct=(d["total"]["calories"]/calgoal*100) if calgoal and d["logged"] else 0
        adherence.append({**d,"pct":min(pct,120)})
    return render_template("progress.html",days=days,avg=avg,max_cal=max_cal,logged_days=len(logged),
        avg_stats=avg_stats,weights=weights,selected_day=selected_day,selected_total=selected_total,
        selected_stats=selected_stats,goal=goal,streak=logging_streak(session["user_id"]),
        achievements=achievement_data(session["user_id"]),adherence=adherence)


@app.route("/more")
@login_required
def more():
    return render_template("more.html")


@app.route("/export/day.csv")
@login_required
def export_day_csv():
    day=request.args.get("day") or date.today().isoformat()
    entries,total=day_data(session["user_id"],day)
    rows=["meal,food,grams,calories,protein_g,carbs_g,fat_g,fiber_g"]
    def csvq(value):
        text=str(value).replace('"','""')
        return f'"{text}"'
    for e in entries:
        r=e["row"]; n=e["nutrients"]
        rows.append(",".join([csvq(r["meal"]),csvq(r["description"]),f'{number(r["grams"]):.1f}',f'{number(n.get("calories")):.1f}',
                              f'{number(n.get("protein")):.1f}',f'{number(n.get("carbs")):.1f}',f'{number(n.get("fat")):.1f}',f'{number(n.get("fiber")):.1f}']))
    rows.append(",".join([csvq("TOTAL"),csvq(day),"",f'{total["calories"]:.1f}',f'{total["protein"]:.1f}',f'{total["carbs"]:.1f}',f'{total["fat"]:.1f}',f'{total["fiber"]:.1f}']))
    return Response("\n".join(rows)+"\n",mimetype="text/csv",headers={"Content-Disposition":f'attachment; filename="mannah-{day}.csv"'})


@app.route("/custom-food",methods=["GET","POST"])
@login_required
def custom_food():
    if request.method=="POST":
        name=request.form.get("name","").strip(); category=request.form.get("category","").strip() or "Custom"
        if not name: flash("Give the food a name.","error")
        else:
            n={k:number(request.form.get(k)) for k in TRACKED}
            with app_db() as con:
                con.execute("insert into custom_foods(user_id,source,name,category,brand,nutrients_json) values(?,?,?,?,?,?)",(session["user_id"],"Custom",name,category,request.form.get("brand","").strip(),json.dumps(n)))
            flash("Custom food saved. All values are stored per 100 g.","success")
            return redirect(url_for("custom_food"))
    with app_db() as con:
        custom=con.execute("select * from custom_foods where user_id=? order by created_at desc limit 100",(session["user_id"],)).fetchall()
    return render_template("custom_food.html",custom=custom,favorites=favorite_foods(session["user_id"],100))


@app.post("/custom-food/delete/<int:row_id>")
@login_required
def delete_custom_food(row_id):
    with app_db() as con:
        con.execute("delete from favorites where user_id=? and source_key='custom' and source_id=?",(session["user_id"],str(row_id)))
        con.execute("delete from custom_foods where id=? and user_id=?",(row_id,session["user_id"]))
    flash("Food removed from your library.","success")
    return redirect(url_for("custom_food"))


@app.get("/api/favorite-state")
@login_required
def api_favorite_state():
    source_key=request.args.get("source_key",""); source_id=request.args.get("source_id","")
    with app_db() as con:
        row=con.execute("select 1 from favorites where user_id=? and source_key=? and source_id=?",(session["user_id"],source_key,source_id)).fetchone()
    return jsonify({"active":bool(row)})


@app.post("/api/favorite")
@login_required
def api_favorite():
    data=request.get_json(silent=True) or {}; source_key=data.get("source_key"); source_id=str(data.get("source_id") or "")
    food=get_mannah_food(source_id) if source_key=="mannah" else get_custom(session["user_id"],source_id) if source_key=="custom" else None
    if not food:return jsonify({"error":"Food not found"}),404
    with app_db() as con:
        existing=con.execute("select id from favorites where user_id=? and source_key=? and source_id=?",(session["user_id"],source_key,source_id)).fetchone()
        if existing:
            con.execute("delete from favorites where id=?",(existing["id"],)); active=False
        else:
            n={k:number(food.get(k)) for k in TRACKED}
            con.execute("insert into favorites(user_id,source_key,source_id,source,name,category,nutrients_per100_json) values(?,?,?,?,?,?,?)",
                        (session["user_id"],source_key,source_id,food["source"],food["name"],food.get("category",""),json.dumps(n))); active=True
    return jsonify({"active":active})


@app.get("/api/search-foods")
@login_required
def api_search_foods():
    q=request.args.get("q","").strip(); limit=min(max(request.args.get("limit",30,type=int),1),50)
    if len(q)<1:return jsonify({"results":[]})
    results=search_custom(session["user_id"],q,8)+search_mannah(q,limit)
    return jsonify({"results":results[:limit],"local_count":food_count()})


@app.get("/api/global-foods")
@login_required
def api_global_foods():
    q=request.args.get("q","").strip(); out=[]; errors=[]
    if len(q)<2:return jsonify({"results":[],"errors":[]})
    for name,fn in (("USDA",search_usda),("Open Food Facts",search_off)):
        try: out.extend(fn(q,8))
        except Exception: errors.append(name)
    return jsonify({"results":out,"errors":errors})


@app.post("/api/import-food")
@login_required
def api_import_food():
    item=request.get_json(silent=True) or {}
    if item.get("source_key") not in ("usda","off"): return jsonify({"error":"Unsupported source"}),400
    saved=save_remote_food(session["user_id"],item)
    return jsonify({"food":saved})


@app.get("/api/food/<source_key>/<source_id>")
@login_required
def api_food(source_key,source_id):
    food=get_mannah_food(source_id) if source_key=="mannah" else get_custom(session["user_id"],source_id) if source_key=="custom" else None
    if not food:return jsonify({"error":"Food not found"}),404
    return jsonify({"food":food})


@app.get("/healthz")
def healthz():
    return jsonify({"status": "ok", "foods": food_count()})


init_db()

def main():
    app.run(
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "8012")),
        debug=os.environ.get("FLASK_DEBUG", "0") == "1",
    )

if __name__ == "__main__":
    main()
