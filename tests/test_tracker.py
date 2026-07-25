from pathlib import Path
from pot_of_mannah.data import Food
from pot_of_mannah.tracker import Tracker

def test_food_logging_and_totals(tmp_path: Path):
    tr=Tracker(tmp_path/'m.db')
    food=Food('1','Test','Test Food','per 100 g',{'calories':100,'protein':10,'carbs':20,'fat':2})
    tr.add_food(food,200,'Lunch')
    t=tr.totals(); assert t['calories']==200; assert t['protein']==20
    assert tr.foods_for_day()[0]['meal']=='Lunch'

def test_notes_and_workout(tmp_path: Path):
    tr=Tracker(tmp_path/'m.db'); tr.add_note('A','Body','General'); assert tr.notes()[0]['title']=='A'
    tr.add_set(1,'Bench Press',10,135,'good'); rows=tr.workout_sets_today(); assert rows[0]['weight']==135

def test_pantry_menu_and_export(tmp_path: Path):
    tr=Tracker(tmp_path/'m.db')
    chicken=Food('c','Protein','Chicken breast','per 100 g',{'calories':165,'protein':31,'carbs':0,'fat':3.6,'fiber':0,'magnesium':29,'potassium':256,'calcium':15,'iron':1,'vitamin_c':0,'vitamin_e':0.3})
    rice=Food('r','Grain','Brown rice','per 100 g',{'calories':123,'protein':2.7,'carbs':25.6,'fat':1,'fiber':1.6,'magnesium':39,'potassium':86,'calcium':3,'iron':0.6,'vitamin_c':0,'vitamin_e':0.1})
    spinach=Food('s','Vegetable','Spinach','per 100 g',{'calories':23,'protein':2.9,'carbs':3.6,'fat':0.4,'fiber':2.2,'magnesium':79,'potassium':558,'calcium':99,'iron':2.7,'vitamin_c':28,'vitamin_e':2})
    for f in (chicken,rice,spinach): tr.add_to_pantry(f,600)
    menu=tr.make_menu()
    assert len(menu)==3
    assert all(item['description'] in {'Chicken breast','Brown rice','Spinach'} for meal in menu for item in meal['items'])
    tr.log_menu(menu)
    assert tr.foods_for_day()
    p=tr.export_report(fmt='json',out_dir=tmp_path)
    assert p.exists() and 'totals' in p.read_text()

def test_favorites(tmp_path: Path):
    tr=Tracker(tmp_path/'m.db')
    assert tr.toggle_favorite('food','1','Apple') is True
    assert len(tr.favorites('food'))==1
    assert tr.toggle_favorite('food','1','Apple') is False
    assert len(tr.favorites('food'))==0
