from __future__ import annotations

from datetime import date
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Footer, Header, Input, Label, Select, Static, TabbedContent, TabPane, TextArea

from .data import Exercise, Food, MannahStore
from .menu import menu_text
from .tracker import Tracker, UNITS


HELP = {
    'dashboard': 'Dashboard\n\nR  Refresh totals\nE  Export daily report\n?  This help\nCtrl+K  Jump to food search\nQ  Quit',
    'food': 'Food\n\nType to search the nutrition database.\nA  Log selected food\nP  Add selected food to Pantry\nF  Favorite/unfavorite\nE  Export today\n?  This help',
    'today': "Today's Food Log\n\nShows everything eaten today.\nDelete  Remove selected entry\nE  Export CSV/JSON/Markdown\n?  This help",
    'pantry': 'Pantry\n\nFoods here are available to Menu Maker.\nAdd foods with P from the Food tab.\nU  Update available grams\nDelete  Remove selected pantry item\nM  Build a menu\n?  This help',
    'menu-maker': 'Menu Maker\n\nBuilds breakfast, lunch and dinner ONLY from Pantry foods.\nM  Generate/re-generate\nL  Log generated menu to today and deduct pantry quantities\nE  Export daily report after logging\n?  This help',
    'exercise': 'Exercise Library\n\nSearch by exercise, muscle or equipment.\nA  Log a set\nF  Favorite/unfavorite\n?  This help',
    'workout': "Today's Workout\n\nSets logged from the Exercise tab appear here.\nE  Export full daily report\n?  This help",
    'notes': 'Notes\n\nN  New note\nSelect a note to read it.\nE  Export daily report\n?  This help',
    'stats': 'Stats / Gaps\n\nCompares today against configured goals.\nLowest percentages are your current nutrition gaps.\nE  Export report\n?  This help',
}


class SimpleModal(ModalScreen[str | None]):
    CSS = 'SimpleModal {align:center middle;} #box {width:78; height:auto; max-height:80%; padding:1 2; border:solid $primary; background:$surface;} #body {height:auto; max-height:28; overflow-y:auto;}'
    def __init__(self, title: str, text: str):
        super().__init__(); self.title_text = title; self.text = text
    def compose(self):
        with Vertical(id='box'):
            yield Label(f'[b]{self.title_text}[/b]')
            yield Static(self.text, id='body')
            yield Button('Close', id='close', variant='primary')
    def on_button_pressed(self, _): self.dismiss(None)


class FoodLogModal(ModalScreen[tuple[float, str] | None]):
    CSS = 'FoodLogModal {align:center middle;} #box {width:60; height:auto; padding:1 2; border:solid $primary; background:$surface;}'
    def __init__(self, food: Food): super().__init__(); self.food = food
    def compose(self):
        with Vertical(id='box'):
            yield Label(f'[b]Log food[/b]\n{self.food.description}')
            yield Input(value='100', placeholder='Grams', id='grams', type='number')
            yield Select([('Breakfast','Breakfast'),('Lunch','Lunch'),('Dinner','Dinner'),('Snack','Snack'),('Meal','Meal')], value='Meal', id='meal')
            with Horizontal():
                yield Button('Add', id='ok', variant='primary'); yield Button('Cancel', id='cancel')
    def on_button_pressed(self, e: Button.Pressed):
        if e.button.id == 'cancel': self.dismiss(None); return
        try: grams = float(self.query_one('#grams', Input).value)
        except ValueError: grams = 100
        self.dismiss((max(1, grams), str(self.query_one('#meal', Select).value or 'Meal')))


class NumberModal(ModalScreen[float | None]):
    CSS = 'NumberModal {align:center middle;} #box {width:58; height:auto; padding:1 2; border:solid $primary; background:$surface;}'
    def __init__(self, title: str, value: float = 500): super().__init__(); self.title_text=title; self.value=value
    def compose(self):
        with Vertical(id='box'):
            yield Label(f'[b]{self.title_text}[/b]')
            yield Input(value=f'{self.value:g}', id='value', type='number')
            with Horizontal(): yield Button('Save',id='ok',variant='primary'); yield Button('Cancel',id='cancel')
    def on_button_pressed(self,e:Button.Pressed):
        if e.button.id=='cancel': self.dismiss(None); return
        try: v=float(self.query_one('#value',Input).value)
        except ValueError: v=self.value
        self.dismiss(v)


class SetModal(ModalScreen[tuple[float,float,str]|None]):
    CSS='SetModal {align:center middle;} #box {width:60; height:auto; padding:1 2; border:solid $primary; background:$surface;}'
    def __init__(self,e:Exercise): super().__init__(); self.exercise=e
    def compose(self):
        with Vertical(id='box'):
            yield Label(f'[b]Add set[/b]\n{self.exercise.name}')
            yield Input(value='10',placeholder='Reps',id='reps',type='number'); yield Input(value='0',placeholder='Weight',id='weight',type='number'); yield Input(placeholder='Set note (optional)',id='note')
            with Horizontal(): yield Button('Add set',id='ok',variant='primary'); yield Button('Cancel',id='cancel')
    def on_button_pressed(self,e:Button.Pressed):
        if e.button.id=='cancel': self.dismiss(None); return
        try: reps=float(self.query_one('#reps',Input).value or 0); weight=float(self.query_one('#weight',Input).value or 0)
        except ValueError: reps,weight=0,0
        self.dismiss((reps,weight,self.query_one('#note',Input).value))


class NoteModal(ModalScreen[tuple[str,str,str]|None]):
    CSS='NoteModal {align:center middle;} #box {width:76; height:28; padding:1 2; border:solid $primary; background:$surface;} TextArea {height:12;}'
    def compose(self):
        with Vertical(id='box'):
            yield Label('[b]New note[/b]'); yield Select([('General','General'),('Food','Food'),('Workout','Workout'),('Daily Journal','Daily Journal')],value='General',id='kind'); yield Input(placeholder='Title',id='title'); yield TextArea(id='body')
            with Horizontal(): yield Button('Save',id='ok',variant='primary'); yield Button('Cancel',id='cancel')
    def on_button_pressed(self,e:Button.Pressed):
        if e.button.id=='cancel': self.dismiss(None); return
        title=self.query_one('#title',Input).value.strip() or 'Untitled'; body=self.query_one('#body',TextArea).text.strip(); kind=str(self.query_one('#kind',Select).value or 'General'); self.dismiss((title,body,kind))


class ExportModal(ModalScreen[str | None]):
    CSS='ExportModal {align:center middle;} #box {width:58; height:auto; padding:1 2; border:solid $primary; background:$surface;}'
    def compose(self):
        with Vertical(id='box'):
            yield Label('[b]Export Daily Report[/b]\nSaved under ~/Downloads/pot-of-mannah-reports/')
            yield Select([('Markdown','md'),('CSV','csv'),('JSON','json')],value='md',id='fmt')
            with Horizontal(): yield Button('Export',id='ok',variant='primary'); yield Button('Cancel',id='cancel')
    def on_button_pressed(self,e:Button.Pressed):
        if e.button.id=='cancel': self.dismiss(None); return
        self.dismiss(str(self.query_one('#fmt',Select).value or 'md'))


class PotOfMannahApp(App[None]):
    TITLE='Pot of Mannah'; SUB_TITLE='Nutrition + Training + Pantry Intelligence'
    BINDINGS=[
        Binding('q','quit','Quit'), Binding('ctrl+k','focus_search','Search'), Binding('a','add','Add'),
        Binding('p','pantry_add','Pantry'), Binding('f','favorite','Favorite'), Binding('m','make_menu','Menu'),
        Binding('l','log_menu','Log Menu'), Binding('u','update_pantry','Quantity'), Binding('n','new_note','Note'),
        Binding('e','export','Export'), Binding('?','help','Help'), Binding('r','refresh','Refresh'),
        Binding('delete','delete_item','Delete')]
    CSS='''
    Screen {layout:vertical;} #hero {height:3;padding:0 2;content-align:left middle;} .pane {height:1fr;} .left {width:2fr;} .right {width:1fr;padding:1 2;border-left:solid $primary;overflow-y:auto;} Input {margin:0 1 1 1;} DataTable {height:1fr;} #status {height:1;padding:0 2;} #dash,#stats-panel,#menu-panel {padding:1 2;overflow-y:auto;} #notes-layout {height:1fr;} .toolbar {height:3;padding:0 1;} Button {margin-right:1;}
    '''
    def __init__(self):
        super().__init__(); self.store=MannahStore(); self.tracker=Tracker(); self.food_rows=[]; self.exercise_rows=[]; self.note_rows=[]; self.pantry_rows=[]; self.current_menu=[]

    def compose(self)->ComposeResult:
        yield Header(show_clock=True)
        yield Static('[b]POT OF MANNAH[/b]  •  Nutrition, pantry menus, training, notes, and reports.',id='hero')
        with TabbedContent(initial='dashboard'):
            with TabPane('Dashboard',id='dashboard'): yield Static(id='dash')
            with TabPane('Food',id='food'):
                yield Input(placeholder='Search foods…',id='food-search')
                with Horizontal(classes='pane'):
                    yield DataTable(id='food-table',classes='left',cursor_type='row'); yield Static('Select a food.',id='food-detail',classes='right')
            with TabPane('Today',id='today'):
                yield Static("[b]TODAY'S FOOD LOG[/b]  •  E export • Delete removes selected entry • ? help",classes='toolbar'); yield DataTable(id='log-table',cursor_type='row')
            with TabPane('Pantry',id='pantry'):
                yield Static('[b]PANTRY[/b]  •  Add foods with P from Food • U quantity • M menu • ? help',classes='toolbar'); yield DataTable(id='pantry-table',cursor_type='row')
            with TabPane('Menu Maker',id='menu-maker'):
                yield Static('[b]MENU MAKER[/b]  •  M generate • L log generated menu • ? help',classes='toolbar'); yield Static(id='menu-panel')
            with TabPane('Exercise',id='exercise'):
                yield Input(placeholder='Search exercise, muscle, equipment…',id='exercise-search')
                with Horizontal(classes='pane'):
                    yield DataTable(id='exercise-table',classes='left',cursor_type='row'); yield Static('Select an exercise.',id='exercise-detail',classes='right')
            with TabPane('Workout',id='workout'):
                yield Static("[b]TODAY'S WORKOUT[/b]  •  E export • ? help",classes='toolbar'); yield DataTable(id='workout-table',cursor_type='row')
            with TabPane('Notes',id='notes'):
                yield Static('N new note • E export • ? help',classes='toolbar')
                with Horizontal(id='notes-layout'):
                    yield DataTable(id='notes-table',classes='left',cursor_type='row'); yield Static('Select a note.',id='note-detail',classes='right')
            with TabPane('Stats / Gaps',id='stats'): yield Static(id='stats-panel')
        yield Static('READY • ? for instructions',id='status'); yield Footer()

    def on_mount(self):
        self.query_one('#food-table',DataTable).add_columns('Food','Category','kcal','Protein','Carbs','Fat')
        self.query_one('#log-table',DataTable).add_columns('Meal','Food','grams','kcal','Protein','Carbs','Fat')
        self.query_one('#pantry-table',DataTable).add_columns('Food','Category','Available g','kcal/100g','Protein')
        self.query_one('#exercise-table',DataTable).add_columns('Exercise','Muscle','Equipment','Difficulty','Mechanics')
        self.query_one('#workout-table',DataTable).add_columns('Exercise','Set','Reps','Weight','RPE','Note')
        self.query_one('#notes-table',DataTable).add_columns('Date','Type','Title')
        self._load_foods(''); self._load_exercises(''); self.action_refresh()

    def _status(self,s): self.query_one('#status',Static).update(s)
    def _load_foods(self,q):
        self.food_rows=self.store.search_foods(q); t=self.query_one('#food-table',DataTable); t.clear()
        for f in self.food_rows: t.add_row(f.description,f.category,f'{f.calories:.0f}',f'{f.protein:.1f}g',f'{f.carbs:.1f}g',f'{f.fat:.1f}g')
    def _load_exercises(self,q):
        self.exercise_rows=self.store.search_exercises(q); t=self.query_one('#exercise-table',DataTable); t.clear()
        for e in self.exercise_rows: t.add_row(e.name,e.main_muscle,e.equipment,str(e.difficulty or '—'),e.mechanics or '—')
    def on_input_changed(self,e:Input.Changed):
        if e.input.id=='food-search': self._load_foods(e.value)
        elif e.input.id=='exercise-search': self._load_exercises(e.value)
    def on_data_table_row_highlighted(self,e:DataTable.RowHighlighted):
        i=e.cursor_row
        if e.data_table.id=='food-table' and 0<=i<len(self.food_rows): self._show_food(self.food_rows[i])
        elif e.data_table.id=='exercise-table' and 0<=i<len(self.exercise_rows): self._show_ex(self.exercise_rows[i])
        elif e.data_table.id=='notes-table' and 0<=i<len(self.note_rows):
            r=self.note_rows[i]; self.query_one('#note-detail',Static).update(f"[b]{r['title']}[/b]\n[dim]{r['kind']} • {r['created_at'][:16]}[/dim]\n\n{r['body']}")

    def _show_food(self,f):
        n=f.nutrients
        self.query_one('#food-detail',Static).update(f'''[b]{f.description}[/b]\n[dim]{f.category} • per 100 g[/dim]\n\n[b]MACROS[/b]\nCalories  {n['calories']:.0f} kcal\nProtein   {n['protein']:.1f} g\nCarbs     {n['carbs']:.1f} g\nFat       {n['fat']:.1f} g\nFiber     {n['fiber']:.1f} g\nSugar     {n['sugar']:.1f} g\n\n[b]MINERALS[/b]\nCalcium   {n['calcium']:.1f} mg\nIron      {n['iron']:.1f} mg\nMagnesium {n['magnesium']:.1f} mg\nPotassium {n['potassium']:.1f} mg\nSodium    {n['sodium']:.1f} mg\nZinc      {n['zinc']:.1f} mg\nSelenium  {n['selenium']:.1f} µg\n\n[b]VITAMINS[/b]\nA (RAE)   {n['vitamin_a_rae']:.1f} µg\nB6        {n['vitamin_b6']:.2f} mg\nB12       {n['vitamin_b12']:.2f} µg\nC         {n['vitamin_c']:.1f} mg\nE         {n['vitamin_e']:.2f} mg\nK         {n['vitamin_k']:.1f} µg\nCholine   {n['choline']:.1f} mg\n\n[dim]A log • P pantry • F favorite • ? help[/dim]''')
    def _show_ex(self,e):
        self.query_one('#exercise-detail',Static).update(f'''[b]{e.name}[/b]\n[dim]{e.main_muscle} • {e.equipment}[/dim]\n\nDifficulty  {e.difficulty or '—'} / 5\nMechanics   {e.mechanics or '—'}\nForce       {e.force or '—'}\nTargets     {e.target_muscles or '—'}\nSecondary   {e.secondary_muscles or '—'}\n\n[b]Preparation[/b]\n{e.preparation or '—'}\n\n[b]Execution[/b]\n{e.execution or '—'}\n\n[dim]A log set • F favorite • ? help[/dim]''')

    def action_add(self):
        tab=self.query_one(TabbedContent).active
        if tab=='food':
            i=self.query_one('#food-table',DataTable).cursor_row
            if 0<=i<len(self.food_rows): self.push_screen(FoodLogModal(self.food_rows[i]),lambda r:self._food_added(self.food_rows[i],r))
        elif tab=='exercise':
            i=self.query_one('#exercise-table',DataTable).cursor_row
            if 0<=i<len(self.exercise_rows): self.push_screen(SetModal(self.exercise_rows[i]),lambda r:self._set_added(self.exercise_rows[i],r))
    def _food_added(self,f,result):
        if result: self.tracker.add_food(f,*result); self.action_refresh(); self._status(f'LOGGED • {f.description}')
    def _set_added(self,e,result):
        if result: self.tracker.add_set(e.id,e.name,result[0],result[1],result[2]); self.action_refresh(); self._status(f'SET LOGGED • {e.name}')

    def action_pantry_add(self):
        if self.query_one(TabbedContent).active!='food': return
        i=self.query_one('#food-table',DataTable).cursor_row
        if 0<=i<len(self.food_rows):
            f=self.food_rows[i]
            self.push_screen(NumberModal(f'Add to Pantry\n{f.description}',500), lambda grams:self._pantry_added(f,grams))
    def _pantry_added(self,f,grams):
        if grams is not None: self.tracker.add_to_pantry(f,max(1,grams)); self.action_refresh(); self._status(f'PANTRY • {f.description}')
    def action_update_pantry(self):
        if self.query_one(TabbedContent).active!='pantry': return
        i=self.query_one('#pantry-table',DataTable).cursor_row
        if 0<=i<len(self.pantry_rows):
            r=self.pantry_rows[i]; self.push_screen(NumberModal(f"Available grams\n{r['description']}",r['available_grams']),lambda grams:self._pantry_updated(r['id'],grams))
    def _pantry_updated(self,row_id,grams):
        if grams is not None: self.tracker.update_pantry_grams(row_id,grams); self.action_refresh(); self._status('PANTRY UPDATED')

    def action_make_menu(self):
        self.current_menu=self.tracker.make_menu(); self.query_one('#menu-panel',Static).update(menu_text(self.current_menu)); self.query_one(TabbedContent).active='menu-maker'; self._status('MENU GENERATED FROM PANTRY')
    def action_log_menu(self):
        if self.query_one(TabbedContent).active!='menu-maker' or not self.current_menu: return
        self.tracker.log_menu(self.current_menu); self.current_menu=[]; self.query_one('#menu-panel',Static).update('[b]Menu logged.[/b]\nPantry quantities were deducted. Press M to build another menu.'); self.action_refresh(); self._status('MENU LOGGED')

    def action_favorite(self):
        tab=self.query_one(TabbedContent).active
        if tab=='food':
            i=self.query_one('#food-table',DataTable).cursor_row
            if 0<=i<len(self.food_rows):
                f=self.food_rows[i]; added=self.tracker.toggle_favorite('food',f.id,f.description,{'category':f.category}); self._status(('FAVORITED • ' if added else 'UNFAVORITED • ')+f.description)
        elif tab=='exercise':
            i=self.query_one('#exercise-table',DataTable).cursor_row
            if 0<=i<len(self.exercise_rows):
                ex=self.exercise_rows[i]; added=self.tracker.toggle_favorite('exercise',str(ex.id),ex.name,{'muscle':ex.main_muscle}); self._status(('FAVORITED • ' if added else 'UNFAVORITED • ')+ex.name)

    def action_new_note(self): self.push_screen(NoteModal(),self._note_added)
    def _note_added(self,result):
        if result: self.tracker.add_note(*result); self.action_refresh(); self._status('NOTE SAVED')

    def action_export(self): self.push_screen(ExportModal(),self._export_done)
    def _export_done(self,fmt):
        if fmt:
            p=self.tracker.export_report('daily',fmt); self._status(f'EXPORTED • {p}'); self.push_screen(SimpleModal('Report Exported',f'Saved to:\n{p}'))
    def action_help(self):
        tab=self.query_one(TabbedContent).active or 'dashboard'; self.push_screen(SimpleModal('Instructions',HELP.get(tab,HELP['dashboard'])))

    def action_delete_item(self):
        tab=self.query_one(TabbedContent).active
        if tab=='today':
            rows=self.tracker.foods_for_day(); i=self.query_one('#log-table',DataTable).cursor_row
            if 0<=i<len(rows): self.tracker.delete_food(rows[i]['id']); self.action_refresh(); self._status('FOOD ENTRY DELETED')
        elif tab=='pantry':
            i=self.query_one('#pantry-table',DataTable).cursor_row
            if 0<=i<len(self.pantry_rows): self.tracker.delete_pantry(self.pantry_rows[i]['id']); self.action_refresh(); self._status('PANTRY ITEM REMOVED')

    def action_focus_search(self):
        if self.query_one(TabbedContent).active=='exercise': self.query_one('#exercise-search',Input).focus()
        else: self.query_one(TabbedContent).active='food'; self.query_one('#food-search',Input).focus()
    def action_refresh(self):
        self._render_log(); self._render_pantry(); self._render_workout(); self._render_notes(); self._render_dashboard(); self._render_stats()
    def _render_log(self):
        import json
        t=self.query_one('#log-table',DataTable); t.clear()
        for r in self.tracker.foods_for_day():
            n=json.loads(r['nutrients_json']); t.add_row(r['meal'],r['description'],f"{r['grams']:.0f}",f"{n.get('calories',0):.0f}",f"{n.get('protein',0):.1f}",f"{n.get('carbs',0):.1f}",f"{n.get('fat',0):.1f}")
    def _render_pantry(self):
        import json
        self.pantry_rows=list(self.tracker.pantry_items()); t=self.query_one('#pantry-table',DataTable); t.clear()
        for r in self.pantry_rows:
            n=json.loads(r['nutrients_json']); t.add_row(r['description'],r['category'],f"{r['available_grams']:.0f}",f"{n.get('calories',0):.0f}",f"{n.get('protein',0):.1f}g")
    def _render_workout(self):
        t=self.query_one('#workout-table',DataTable); t.clear()
        for r in self.tracker.workout_sets_today(): t.add_row(r['exercise_name'],str(r['set_no']),f"{r['reps']:g}",f"{r['weight']:g}",f"{r['rpe']:g}",r['notes'] or '')
    def _render_notes(self):
        self.note_rows=list(self.tracker.notes()); t=self.query_one('#notes-table',DataTable); t.clear()
        for r in self.note_rows: t.add_row(r['created_at'][:10],r['kind'],r['title'])
    def _render_dashboard(self):
        t=self.tracker.totals(); g=self.tracker.goals(); sets=self.tracker.workout_sets_today()
        def line(k,label):
            pct=(t.get(k,0)/g[k]*100) if g.get(k) else 0; return f'{label:<12} {t.get(k,0):>7.1f} / {g.get(k,0):<7g} {UNITS.get(k,""):<4}  {pct:>5.0f}%'
        gaps=self.tracker.gaps()[:5]; low='\n'.join(f"{k.replace('_',' ').title():<18} {pct:>5.0f}%" for pct,k,_,_ in gaps)
        self.query_one('#dash',Static).update(f'''[b]{date.today().strftime('%A, %B %d')}[/b]\n\n[b]MACROS[/b]\n{line('calories','Calories')}\n{line('protein','Protein')}\n{line('carbs','Carbs')}\n{line('fat','Fat')}\n{line('fiber','Fiber')}\n\n[b]LOWEST NUTRIENT COVERAGE[/b]\n{low or 'Log food to begin analysis.'}\n\n[b]PANTRY[/b]\nFoods available: [b]{len(self.tracker.pantry_items())}[/b]  •  Press M to build today's menu\n\n[b]TRAINING[/b]\nSets logged today: [b]{len(sets)}[/b]\n\n[b]NOTES[/b]\nSaved notes: [b]{len(self.note_rows)}[/b]\n\n[dim]E export • ? instructions[/dim]''')
    def _render_stats(self):
        gaps=self.tracker.gaps(); lines=[]
        for pct,k,cur,target in gaps:
            status='LOW' if pct<70 else ('OK' if pct<100 else 'MET'); lines.append(f'{status:<4} {k.replace("_"," ").title():<22} {cur:>8.1f} / {target:<8g} {UNITS.get(k,""):<4} {pct:>5.0f}%')
        s=self.store.stats(); self.query_one('#stats-panel',Static).update('[b]NUTRITION COVERAGE • TODAY[/b]\n\n'+'\n'.join(lines)+f'''\n\n[b]REFERENCE DATA[/b]\nFoods: {s['foods']:,} • Categories: {s['categories']:,}\nExercises: {s['exercises']:,} • Muscle groups: {s['muscles']:,}\n\n[dim]E exports the report • ? opens instructions • Personal DB: {self.tracker.path}[/dim]''')


def main(): PotOfMannahApp().run()
if __name__=='__main__': main()
