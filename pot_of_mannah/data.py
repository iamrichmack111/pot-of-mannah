from __future__ import annotations
import sqlite3
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path
from typing import Any


def _db(name: str) -> Path:
    return Path(str(files('pot_of_mannah').joinpath('data', name)))

def num(v: Any) -> float:
    try: return float(v or 0)
    except (TypeError, ValueError): return 0.0

NUTRIENT_COLUMNS = {
    'calories':'Data_Kilocalories','protein':'Data_Protein','carbs':'Data_Carbohydrate','fat':'Data_Fat_Total_Lipid',
    'fiber':'Data_Fiber','sugar':'Data_Sugar_Total','sat_fat':'Data_Fat_Saturated_Fat','mono_fat':'Data_Fat_Monosaturated_Fat',
    'poly_fat':'Data_Fat_Polysaturated_Fat','cholesterol':'Data_Cholesterol','calcium':'Data_Major_Minerals_Calcium',
    'copper':'Data_Major_Minerals_Copper','iron':'Data_Major_Minerals_Iron','magnesium':'Data_Major_Minerals_Magnesium',
    'phosphorus':'Data_Major_Minerals_Phosphorus','potassium':'Data_Major_Minerals_Potassium','sodium':'Data_Major_Minerals_Sodium',
    'zinc':'Data_Major_Minerals_Zinc','selenium':'Data_Selenium','manganese':'Data_Manganese','vitamin_a_rae':'Data_Vitamins_Vitamin_A_RAE',
    'vitamin_b6':'Data_Vitamins_Vitamin_B6','vitamin_b12':'Data_Vitamins_Vitamin_B12','vitamin_c':'Data_Vitamins_Vitamin_C',
    'vitamin_e':'Data_Vitamins_Vitamin_E','vitamin_k':'Data_Vitamins_Vitamin_K','niacin':'Data_Niacin','riboflavin':'Data_Riboflavin',
    'thiamin':'Data_Thiamin','pantothenic_acid':'Data_Pantothenic_Acid','choline':'Data_Choline','water':'Data_Water'
}

@dataclass(frozen=True, slots=True)
class Food:
    id: str; category: str; description: str; serving: str; nutrients: dict[str,float]
    def __getattr__(self, name: str) -> float:
        if name in self.nutrients: return self.nutrients[name]
        raise AttributeError(name)

@dataclass(frozen=True, slots=True)
class Exercise:
    id:int; name:str; equipment:str; main_muscle:str; difficulty:int|None; mechanics:str; force:str; preparation:str; execution:str; target_muscles:str; secondary_muscles:str

class MannahStore:
    def __init__(self, food_db:Path|None=None, exercise_db:Path|None=None):
        self.food_db=food_db or _db('food.db'); self.exercise_db=exercise_db or _db('exercise.db')
    @staticmethod
    def _connect(path:Path):
        con=sqlite3.connect(f'file:{path}?mode=ro',uri=True); con.row_factory=sqlite3.Row; return con
    def stats(self):
        with self._connect(self.food_db) as c:
            foods=c.execute('select count(*) from food_data').fetchone()[0]; cats=c.execute('select count(distinct Category) from food_data').fetchone()[0]
        with self._connect(self.exercise_db) as c:
            ex=c.execute('select count(*) from exercises').fetchone()[0]; mus=c.execute("select count(distinct Main_muscle) from exercises where Main_muscle<>''").fetchone()[0]
        return {'foods':foods,'categories':cats,'exercises':ex,'muscles':mus}
    def search_foods(self,q:str,limit:int=100):
        cols=', '.join(NUTRIENT_COLUMNS.values())
        sql=f'''select rowid as rid, Category, Description, Nutrient_Data_Bank_Number, Data_Household_Weights_2nd_Household_Weight_Description, {cols}
        from food_data where Description like ? or Category like ? order by case when Description like ? then 0 else 1 end,length(Description),Description limit ?'''
        needle=f'%{q.strip()}%'; prefix=f'{q.strip()}%'
        with self._connect(self.food_db) as c: rows=c.execute(sql,(needle,needle,prefix,limit)).fetchall()
        out=[]
        for r in rows:
            nutrients={k:num(r[v]) for k,v in NUTRIENT_COLUMNS.items()}
            out.append(Food(str(r['Nutrient_Data_Bank_Number'] or r['rid']),r['Category'] or '',r['Description'] or '',r['Data_Household_Weights_2nd_Household_Weight_Description'] or 'per 100 g',nutrients))
        return out
    def search_exercises(self,q:str='',limit:int=100):
        n=f'%{q.strip()}%'
        sql='''select id,Exercise_Name,Equipment,Main_muscle,Difficulty,Mechanics,Force,Preparation,Execution,Target_Muscles,Secondary_Muscles from exercises
        where Exercise_Name like ? or Main_muscle like ? or Target_Muscles like ? or Equipment like ? order by Main_muscle,Difficulty,Exercise_Name limit ?'''
        with self._connect(self.exercise_db) as c: rows=c.execute(sql,(n,n,n,n,limit)).fetchall()
        return [Exercise(r['id'],r['Exercise_Name'],r['Equipment'] or 'Bodyweight',r['Main_muscle'] or 'Unspecified',r['Difficulty'],r['Mechanics'] or '',r['Force'] or '',r['Preparation'] or '',r['Execution'] or '',r['Target_Muscles'] or '',r['Secondary_Muscles'] or '') for r in rows]
