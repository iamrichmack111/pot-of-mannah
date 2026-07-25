from __future__ import annotations

import csv
import json
import sqlite3
from datetime import date, datetime
from pathlib import Path
from platformdirs import user_data_dir

from .data import Food, NUTRIENT_COLUMNS

DEFAULT_GOALS = {
    'calories': 2200, 'protein': 160, 'carbs': 240, 'fat': 75, 'fiber': 30,
    'calcium': 1000, 'iron': 18, 'magnesium': 420, 'potassium': 3400,
    'zinc': 11, 'selenium': 55, 'sodium': 2300, 'vitamin_a_rae': 900,
    'vitamin_b6': 1.3, 'vitamin_b12': 2.4, 'vitamin_c': 90,
    'vitamin_e': 15, 'vitamin_k': 120, 'choline': 550,
}
UNITS = {
    'calories':'kcal','protein':'g','carbs':'g','fat':'g','fiber':'g','sugar':'g',
    'sat_fat':'g','mono_fat':'g','poly_fat':'g','cholesterol':'mg','calcium':'mg',
    'copper':'mg','iron':'mg','magnesium':'mg','phosphorus':'mg','potassium':'mg',
    'sodium':'mg','zinc':'mg','selenium':'µg','manganese':'mg','vitamin_a_rae':'µg',
    'vitamin_b6':'mg','vitamin_b12':'µg','vitamin_c':'mg','vitamin_e':'mg',
    'vitamin_k':'µg','niacin':'mg','riboflavin':'mg','thiamin':'mg',
    'pantothenic_acid':'mg','choline':'mg','water':'g'
}


class Tracker:
    def __init__(self, path: Path | None = None):
        self.path = path or Path(user_data_dir('pot-of-mannah')) / 'mannah.db'
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def con(self):
        c = sqlite3.connect(self.path)
        c.row_factory = sqlite3.Row
        c.execute('pragma foreign_keys=on')
        return c

    def _init(self):
        with self.con() as c:
            c.executescript('''
            create table if not exists food_log(
              id integer primary key, logged_at text not null, meal text not null default 'Meal',
              food_id text, description text not null, grams real not null, nutrients_json text not null);
            create table if not exists workouts(
              id integer primary key, started_at text not null, name text not null default 'Workout', notes text default '');
            create table if not exists workout_sets(
              id integer primary key, workout_id integer not null references workouts(id) on delete cascade,
              exercise_id integer, exercise_name text not null, set_no integer not null,
              reps real default 0, weight real default 0, duration_min real default 0,
              distance real default 0, rpe real default 0, notes text default '');
            create table if not exists notes(
              id integer primary key, created_at text not null, kind text not null default 'General',
              title text not null, body text not null);
            create table if not exists goals(key text primary key,value real not null);
            create table if not exists pantry(
              id integer primary key, food_id text not null, description text not null,
              category text not null default '', available_grams real not null default 500,
              nutrients_json text not null, added_at text not null, unique(food_id, description));
            create table if not exists favorites(
              id integer primary key, kind text not null, ref_id text not null, name text not null,
              data_json text not null default '{}', unique(kind, ref_id));
            create table if not exists meal_templates(
              id integer primary key, name text not null unique, created_at text not null,
              items_json text not null);
            create table if not exists workout_templates(
              id integer primary key, name text not null unique, created_at text not null,
              exercises_json text not null);
            ''')
            for k, v in DEFAULT_GOALS.items():
                c.execute('insert or ignore into goals(key,value) values(?,?)', (k, v))

    def add_food(self, food: Food, grams: float = 100, meal: str = 'Meal'):
        factor = grams / 100.0
        vals = {k: v * factor for k, v in food.nutrients.items()}
        with self.con() as c:
            c.execute('insert into food_log(logged_at,meal,food_id,description,grams,nutrients_json) values(?,?,?,?,?,?)',
                      (datetime.now().isoformat(timespec='seconds'), meal, food.id, food.description, grams, json.dumps(vals)))

    def foods_for_day(self, day: date | None = None):
        d = (day or date.today()).isoformat()
        with self.con() as c:
            return c.execute("select * from food_log where substr(logged_at,1,10)=? order by logged_at", (d,)).fetchall()

    def delete_food(self, row_id: int):
        with self.con() as c:
            c.execute('delete from food_log where id=?', (row_id,))

    def totals(self, day: date | None = None):
        totals = {k: 0.0 for k in NUTRIENT_COLUMNS}
        for r in self.foods_for_day(day):
            for k, v in json.loads(r['nutrients_json']).items():
                totals[k] = totals.get(k, 0.0) + float(v or 0)
        return totals

    def goals(self):
        with self.con() as c:
            return {r['key']: float(r['value']) for r in c.execute('select * from goals')}

    def set_goal(self, key: str, value: float):
        with self.con() as c:
            c.execute('insert into goals(key,value) values(?,?) on conflict(key) do update set value=excluded.value', (key, value))

    def gaps(self, day: date | None = None):
        t, g = self.totals(day), self.goals()
        rows = []
        for k, target in g.items():
            if target <= 0:
                continue
            pct = t.get(k, 0) / target * 100
            rows.append((pct, k, t.get(k, 0), target))
        return sorted(rows)

    def nutrient_sources(self, nutrient: str, day: date | None = None, limit: int = 10):
        rows = []
        for r in self.foods_for_day(day):
            amount = float(json.loads(r['nutrients_json']).get(nutrient, 0) or 0)
            if amount > 0:
                rows.append((amount, r['description'], r['grams']))
        return sorted(rows, reverse=True)[:limit]

    def add_note(self, title: str, body: str, kind: str = 'General'):
        with self.con() as c:
            c.execute('insert into notes(created_at,kind,title,body) values(?,?,?,?)',
                      (datetime.now().isoformat(timespec='seconds'), kind, title, body))

    def notes(self, limit: int = 100):
        with self.con() as c:
            return c.execute('select * from notes order by created_at desc limit ?', (limit,)).fetchall()

    def add_set(self, exercise_id: int, exercise_name: str, reps: float, weight: float = 0, notes: str = ''):
        with self.con() as c:
            row = c.execute("select id from workouts where substr(started_at,1,10)=? order by id desc limit 1",
                            (date.today().isoformat(),)).fetchone()
            wid = row['id'] if row else c.execute(
                'insert into workouts(started_at,name) values(?,?)',
                (datetime.now().isoformat(timespec='seconds'), 'Daily Workout')).lastrowid
            n = c.execute('select count(*) from workout_sets where workout_id=? and exercise_name=?',
                          (wid, exercise_name)).fetchone()[0] + 1
            c.execute('insert into workout_sets(workout_id,exercise_id,exercise_name,set_no,reps,weight,notes) values(?,?,?,?,?,?,?)',
                      (wid, exercise_id, exercise_name, n, reps, weight, notes))

    def workout_sets_today(self):
        with self.con() as c:
            return c.execute('''select ws.* from workout_sets ws join workouts w on w.id=ws.workout_id
              where substr(w.started_at,1,10)=? order by ws.id''', (date.today().isoformat(),)).fetchall()

    # Pantry -----------------------------------------------------------------
    def add_to_pantry(self, food: Food, grams: float = 500):
        with self.con() as c:
            c.execute('''insert into pantry(food_id,description,category,available_grams,nutrients_json,added_at)
              values(?,?,?,?,?,?) on conflict(food_id,description) do update set
              available_grams=pantry.available_grams + excluded.available_grams,
              nutrients_json=excluded.nutrients_json, category=excluded.category''',
              (food.id, food.description, food.category, max(1, grams), json.dumps(food.nutrients),
               datetime.now().isoformat(timespec='seconds')))

    def pantry_items(self):
        with self.con() as c:
            return c.execute('select * from pantry order by category, description').fetchall()

    def update_pantry_grams(self, row_id: int, grams: float):
        with self.con() as c:
            if grams <= 0:
                c.execute('delete from pantry where id=?', (row_id,))
            else:
                c.execute('update pantry set available_grams=? where id=?', (grams, row_id))

    def delete_pantry(self, row_id: int):
        with self.con() as c:
            c.execute('delete from pantry where id=?', (row_id,))

    def make_menu(self):
        """Build three balanced meals using pantry foods only.

        This is intentionally deterministic and local: it scores each pantry food by
        how well a 100 g serving reduces the remaining calorie/protein/fiber and
        selected micronutrient gaps, while respecting available quantity.
        """
        pantry = [dict(r) for r in self.pantry_items() if r['available_grams'] > 0]
        if not pantry:
            return []
        goals = self.goals()
        meal_shares = [('Breakfast', .25), ('Lunch', .35), ('Dinner', .40)]
        used: dict[int, float] = {}
        result = []
        priority = ['protein', 'fiber', 'magnesium', 'potassium', 'calcium', 'iron', 'vitamin_c', 'vitamin_e']

        for meal_name, share in meal_shares:
            target_cal = goals['calories'] * share
            target_pro = goals['protein'] * share
            chosen = []
            totals = {k: 0.0 for k in NUTRIENT_COLUMNS}
            for _ in range(4):
                best = None
                best_score = -1e18
                for p in pantry:
                    remaining = p['available_grams'] - used.get(p['id'], 0.0)
                    if remaining < 25:
                        continue
                    n = json.loads(p['nutrients_json'])
                    kcal = float(n.get('calories', 0) or 0)
                    if kcal <= 0:
                        continue
                    grams = min(100.0, remaining)
                    factor = grams / 100.0
                    projected_cal = totals['calories'] + kcal * factor
                    # Reward closing calorie/protein gaps and nutrient density.
                    cal_gap_before = abs(target_cal - totals['calories'])
                    cal_gap_after = abs(target_cal - projected_cal)
                    score = (cal_gap_before - cal_gap_after) / max(target_cal, 1) * 12
                    pro = float(n.get('protein', 0) or 0) * factor
                    pro_gap_before = abs(target_pro - totals['protein'])
                    pro_gap_after = abs(target_pro - (totals['protein'] + pro))
                    score += (pro_gap_before - pro_gap_after) / max(target_pro, 1) * 10
                    for key in priority[1:]:
                        target = goals.get(key, 0) * share
                        if target:
                            score += min((float(n.get(key, 0) or 0) * factor) / target, 1.0)
                    # Encourage variety across meals.
                    score -= used.get(p['id'], 0.0) / max(p['available_grams'], 1) * 2
                    if projected_cal > target_cal * 1.25:
                        score -= 5
                    if score > best_score:
                        best_score, best = score, (p, grams, n)
                if not best:
                    break
                p, grams, n = best
                used[p['id']] = used.get(p['id'], 0.0) + grams
                chosen.append({'pantry_id': p['id'], 'food_id': p['food_id'], 'description': p['description'], 'grams': grams})
                factor = grams / 100.0
                for k in totals:
                    totals[k] += float(n.get(k, 0) or 0) * factor
                if totals['calories'] >= target_cal * .9 and totals['protein'] >= target_pro * .8:
                    break
            result.append({'meal': meal_name, 'items': chosen, 'totals': totals})
        return result

    def log_menu(self, menu: list[dict]):
        pantry_by_id = {r['id']: r for r in self.pantry_items()}
        with self.con() as c:
            for meal in menu:
                for item in meal['items']:
                    p = pantry_by_id.get(item['pantry_id'])
                    if not p:
                        continue
                    grams = min(float(item['grams']), float(p['available_grams']))
                    base = json.loads(p['nutrients_json'])
                    vals = {k: float(v or 0) * grams / 100.0 for k, v in base.items()}
                    c.execute('insert into food_log(logged_at,meal,food_id,description,grams,nutrients_json) values(?,?,?,?,?,?)',
                              (datetime.now().isoformat(timespec='seconds'), meal['meal'], p['food_id'], p['description'], grams, json.dumps(vals)))
                    c.execute('update pantry set available_grams=max(0,available_grams-?) where id=?', (grams, p['id']))
            c.execute('delete from pantry where available_grams<=0')

    # Favorites and templates -------------------------------------------------
    def toggle_favorite(self, kind: str, ref_id: str, name: str, data: dict | None = None):
        with self.con() as c:
            row = c.execute('select id from favorites where kind=? and ref_id=?', (kind, str(ref_id))).fetchone()
            if row:
                c.execute('delete from favorites where id=?', (row['id'],)); return False
            c.execute('insert into favorites(kind,ref_id,name,data_json) values(?,?,?,?)',
                      (kind, str(ref_id), name, json.dumps(data or {}))); return True

    def favorites(self, kind: str | None = None):
        with self.con() as c:
            if kind:
                return c.execute('select * from favorites where kind=? order by name', (kind,)).fetchall()
            return c.execute('select * from favorites order by kind,name').fetchall()

    def save_meal_template_from_day(self, name: str, meal: str, day: date | None = None):
        items = []
        for r in self.foods_for_day(day):
            if r['meal'] == meal:
                items.append({'food_id': r['food_id'], 'description': r['description'], 'grams': r['grams'], 'nutrients': json.loads(r['nutrients_json'])})
        with self.con() as c:
            c.execute('insert into meal_templates(name,created_at,items_json) values(?,?,?) on conflict(name) do update set items_json=excluded.items_json',
                      (name, datetime.now().isoformat(timespec='seconds'), json.dumps(items)))

    # Exports -----------------------------------------------------------------
    def export_report(self, kind: str = 'daily', fmt: str = 'md', day: date | None = None, out_dir: Path | None = None) -> Path:
        d = day or date.today()
        out_dir = out_dir or (Path.home() / 'Downloads' / 'pot-of-mannah-reports')
        out_dir.mkdir(parents=True, exist_ok=True)
        safe_kind = kind.replace(' ', '-').lower()
        path = out_dir / f'mannah-{safe_kind}-{d.isoformat()}.{fmt}'
        foods = self.foods_for_day(d)
        sets = self.workout_sets_today() if d == date.today() else []
        totals, goals = self.totals(d), self.goals()

        payload = {
            'date': d.isoformat(), 'kind': kind,
            'totals': totals, 'goals': goals,
            'foods': [dict(r) | {'nutrients': json.loads(r['nutrients_json'])} for r in foods],
            'workout_sets': [dict(r) for r in sets],
            'gaps': [{'percent': p, 'nutrient': k, 'current': cur, 'target': target} for p,k,cur,target in self.gaps(d)],
            'notes': [dict(r) for r in self.notes() if r['created_at'][:10] == d.isoformat()],
        }
        for f in payload['foods']:
            f.pop('nutrients_json', None)

        if fmt == 'json':
            path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding='utf-8')
        elif fmt == 'csv':
            with path.open('w', newline='', encoding='utf-8') as fh:
                w = csv.writer(fh)
                w.writerow(['meal','food','grams','calories','protein_g','carbs_g','fat_g','fiber_g'])
                for r in payload['foods']:
                    n = r['nutrients']
                    w.writerow([r['meal'], r['description'], r['grams'], n.get('calories',0), n.get('protein',0), n.get('carbs',0), n.get('fat',0), n.get('fiber',0)])
        else:
            lines = [f'# Pot of Mannah Daily Report — {d.isoformat()}', '', '## Nutrition', '']
            for key in ('calories','protein','carbs','fat','fiber'):
                lines.append(f'- **{key.replace("_"," ").title()}**: {totals.get(key,0):.1f} / {goals.get(key,0):g} {UNITS.get(key,"")}')
            lines += ['', '## Food Log', '']
            lines += [f"- {r['meal']}: {r['description']} — {r['grams']:.0f} g" for r in payload['foods']] or ['- No food logged.']
            lines += ['', '## Micronutrient Coverage', '']
            for g in payload['gaps']:
                if g['nutrient'] not in ('calories','protein','carbs','fat','fiber'):
                    lines.append(f"- {g['nutrient'].replace('_',' ').title()}: {g['percent']:.0f}%")
            lines += ['', '## Workout', '']
            lines += [f"- {r['exercise_name']}: set {r['set_no']}, {r['reps']:g} reps @ {r['weight']:g}" for r in payload['workout_sets']] or ['- No workout logged.']
            lines += ['', '## Notes', '']
            lines += [f"- **{r['title']}** ({r['kind']}): {r['body']}" for r in payload['notes']] or ['- No notes.']
            path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
        return path
