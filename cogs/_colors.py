from random import choice

from discord import Color

light_colors = [
    Color(0xaaffaa),
    Color(0xF9FFAA),
    Color(0xFFAAAA),
    Color(0xFFCCAA),
    Color(0xAAFFE3),
    Color(0xAAB0FF),
    Color(0xFFAAF7)
]

def choise_light_color(): return choice(light_colors)