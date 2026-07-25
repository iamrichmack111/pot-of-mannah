"""Small formatting helpers for pantry-driven menu plans."""
from __future__ import annotations


def menu_text(menu: list[dict]) -> str:
    if not menu:
        return 'Your pantry is empty. Add foods from the Food tab first.'
    lines = ['[b]PANTRY MENU[/b]', '[dim]Built only from foods currently in Pantry.[/dim]', '']
    for meal in menu:
        t = meal['totals']
        lines.append(f"[b]{meal['meal']}[/b]  {t.get('calories',0):.0f} kcal • {t.get('protein',0):.1f}g protein")
        if meal['items']:
            lines.extend(f"  • {i['description']} — {i['grams']:.0f} g" for i in meal['items'])
        else:
            lines.append('  • Not enough pantry food available')
        lines.append('')
    return '\n'.join(lines)
