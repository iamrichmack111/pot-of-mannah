#!/usr/bin/env python3
"""Rebuild exercise.db safely from the canonical CSV source."""
from __future__ import annotations
import argparse, csv, sqlite3
from pathlib import Path

COLUMNS = ["Exercise_Name","Equipment","Variation","Utility","Mechanics","Force","Preparation","Execution","Target_Muscles","Synergist_Muscles","Stabilizer_Muscles","Antagonist_Muscles","Dynamic_Stabilizer_Muscles","Main_muscle","Difficulty","Secondary_Muscles","parent_id"]

def main() -> None:
    ap=argparse.ArgumentParser(); ap.add_argument('csv', type=Path); ap.add_argument('db', type=Path); args=ap.parse_args()
    with args.csv.open(newline='', encoding='utf-8-sig') as f:
        rows=list(csv.DictReader(f))
    if not rows or list(rows[0]) != COLUMNS:
        raise SystemExit('CSV schema mismatch; refusing to build database')
    if args.db.exists(): args.db.unlink()
    con=sqlite3.connect(args.db)
    con.execute('CREATE TABLE exercises (id INTEGER PRIMARY KEY AUTOINCREMENT, '+', '.join(f'"{c}" TEXT' for c in COLUMNS)+')')
    marks=','.join('?' for _ in COLUMNS)
    con.executemany(f'INSERT INTO exercises ({",".join(COLUMNS)}) VALUES ({marks})', [[r[c].strip() for c in COLUMNS] for r in rows])
    con.execute('CREATE INDEX idx_exercise_name ON exercises(Exercise_Name)'); con.execute('CREATE INDEX idx_exercise_muscle ON exercises(Main_muscle)')
    con.commit(); print(f'Rebuilt {args.db} with {len(rows)} validated exercises')
if __name__ == '__main__': main()
