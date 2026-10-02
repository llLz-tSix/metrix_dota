import concurrent.futures
import copy
import html
import hashlib
import json
import math
import os
import random
import re
import tempfile
import threading
import time
from pathlib import Path

import requests
import streamlit as st

# ===================================================================
# 1. БАЗА ДАННЫХ ГЕРОЕВ И РОЛЕЙ
# ===================================================================

HEROES = {
    1: "Anti-Mage", 2: "Axe", 3: "Bane", 4: "Bloodseeker", 5: "Crystal Maiden",
    6: "Drow Ranger", 7: "Earthshaker", 8: "Juggernaut", 9: "Mirana", 10: "Morphling",
    11: "Shadow Fiend", 12: "Phantom Lancer", 13: "Puck", 14: "Pudge", 15: "Razor",
    16: "Sand King", 17: "Storm Spirit", 18: "Sven", 19: "Tiny", 20: "Vengeful Spirit",
    21: "Windranger", 22: "Zeus", 23: "Kunkka", 25: "Lina", 26: "Lion",
    27: "Shadow Shaman", 28: "Slardar", 29: "Tidehunter", 30: "Witch Doctor",
    31: "Lich", 32: "Riki", 33: "Enigma", 34: "Tinker", 35: "Sniper",
    36: "Necrophos", 37: "Warlock", 38: "Beastmaster", 39: "Queen of Pain",
    40: "Venomancer", 41: "Faceless Void", 42: "Wraith King", 43: "Death Prophet",
    44: "Phantom Assassin", 45: "Pugna", 46: "Templar Assassin", 47: "Viper",
    48: "Luna", 49: "Dragon Knight", 50: "Dazzle", 51: "Clockwerk",
    52: "Leshrac", 53: "Nature's Prophet", 54: "Lifestealer", 55: "Dark Seer",
    56: "Clinkz", 57: "Omniknight", 58: "Enchantress", 59: "Huskar", 60: "Night Stalker",
    61: "Broodmother", 62: "Bounty Hunter", 63: "Weaver", 64: "Jakiro",
    65: "Batrider", 66: "Chen", 67: "Spectre", 68: "Ancient Apparition",
    69: "Doom", 70: "Ursa", 71: "Spirit Breaker", 72: "Gyrocopter",
    73: "Alchemist", 74: "Invoker", 75: "Silencer", 76: "Outworld Destroyer",
    77: "Lycan", 78: "Brewmaster", 79: "Shadow Demon", 80: "Lone Druid",
    81: "Chaos Knight", 82: "Meepo", 83: "Treant Protector", 84: "Ogre Magi",
    85: "Undying", 86: "Rubick", 87: "Disruptor", 88: "Nyx Assassin",
    89: "Naga Siren", 90: "Keeper of the Light", 91: "Visage", 92: "Slark",
    93: "Medusa", 94: "Troll Warlord", 95: "Centaur Warrunner", 96: "Magnus",
    97: "Timbersaw", 98: "Bristleback", 99: "Tusk", 100: "Skywrath Mage",
    101: "Abaddon", 102: "Elder Titan", 103: "Legion Commander", 104: "Techies",
    105: "Ember Spirit", 106: "Earth Spirit", 107: "Underlord", 108: "Terrorblade",
    109: "Phoenix", 110: "Oracle", 112: "Winter Wyvern", 113: "Arc Warden",
    114: "Monkey King", 119: "Dark Willow", 120: "Pangolier", 121: "Grimstroke",
    123: "Hoodwink", 126: "Void Spirit", 128: "Snapfire", 129: "Mars",
    135: "Dawnbreaker", 136: "Marci", 137: "Primal Beast", 138: "Muerta",
    145: "Ringmaster", 146: "Kez"
}

HERO_ROLES = {
    1: "carry", 2: "offlaner", 3: "support", 4: "carry", 5: "support",
    6: "carry", 7: "support", 8: "carry", 9: "support", 10: "carry",
    11: "mid", 12: "carry", 13: "mid", 14: "offlaner", 15: "carry",
    16: "offlaner", 17: "mid", 18: "carry", 19: "offlaner", 20: "support",
    21: "mid", 22: "mid", 23: "mid", 25: "mid", 26: "support",
    27: "support", 28: "offlaner", 29: "offlaner", 30: "support", 31: "support",
    32: "carry", 33: "offlaner", 34: "mid", 35: "carry", 36: "offlaner",
    37: "support", 38: "offlaner", 39: "mid", 40: "support", 41: "carry",
    42: "carry", 43: "mid", 44: "carry", 45: "mid", 46: "mid",
    47: "offlaner", 48: "carry", 49: "offlaner", 50: "support", 51: "offlaner",
    52: "mid", 53: "offlaner", 54: "carry", 55: "offlaner", 56: "carry",
    57: "support", 58: "offlaner", 59: "mid", 60: "offlaner", 61: "offlaner",
    62: "support", 63: "carry", 64: "support", 65: "offlaner", 66: "support",
    67: "carry", 68: "support", 69: "offlaner", 70: "carry", 71: "offlaner",
    72: "carry", 73: "carry", 74: "mid", 75: "support", 76: "mid",
    77: "offlaner", 78: "offlaner", 79: "support", 80: "carry", 81: "carry",
    82: "mid", 83: "support", 84: "support", 85: "support", 86: "support",
    87: "support", 88: "support", 89: "carry", 90: "support", 91: "offlaner",
    92: "carry", 93: "carry", 94: "carry", 95: "offlaner", 96: "offlaner",
    97: "offlaner", 98: "offlaner", 99: "support", 100: "support",
    101: "offlaner", 102: "offlaner", 103: "offlaner", 104: "support",
    105: "mid", 106: "offlaner", 107: "offlaner", 108: "carry",
    109: "support", 110: "support", 112: "support", 113: "mid",
    114: "carry", 119: "support", 120: "offlaner", 121: "support",
    123: "support", 126: "mid", 128: "support", 129: "offlaner",
    135: "offlaner", 136: "support", 137: "offlaner", 138: "carry",
    145: "support", 146: "carry"
}

# ===================================================================
# 2. ТЕГИ УГРОЗ И ПРОТИВОПРЕДМЕТЫ
# ===================================================================

HERO_TAGS = {
    1: ["mobility_escape", "sustained_carry"], 2: ["hard_disable_ult"],
    3: ["hard_disable_ult", "magic_burst"], 4: ["sustained_carry"],
    5: ["magic_burst"], 6: ["sustained_carry"],
    7: ["hard_disable_ult", "magic_burst"], 8: ["physical_burst"],
    9: ["magic_burst", "mobility_escape"], 10: ["sustained_carry", "mobility_escape"],
    11: ["magic_burst"], 12: ["illusions"],
    13: ["mobility_escape", "magic_burst"], 14: ["hard_disable_ult"],
    15: ["sustained_carry"], 16: ["hard_disable_ult", "magic_burst"],
    17: ["mobility_escape", "magic_burst"], 18: ["physical_burst"],
    19: ["physical_burst", "magic_burst"], 20: ["magic_burst"],
    21: ["magic_burst", "mobility_escape", "evasion"], 22: ["magic_burst"],
    23: ["hard_disable_ult", "magic_burst"], 25: ["magic_burst"],
    26: ["hard_disable_ult", "magic_burst"], 27: ["hard_disable_ult", "magic_burst"],
    28: ["physical_burst"], 29: ["hard_disable_ult", "magic_burst"],
    30: ["hard_disable_ult", "magic_burst"], 31: ["magic_burst"],
    32: ["invisible", "physical_burst"], 33: ["hard_disable_ult", "magic_burst"],
    34: ["magic_burst"], 35: ["sustained_carry"],
    36: ["pure_dot", "magic_burst", "lifesteal_regen"], 37: ["magic_burst"],
    38: ["hard_disable_ult"], 39: ["magic_burst", "mobility_escape"],
    40: ["pure_dot"], 41: ["hard_disable_ult", "physical_burst"],
    42: ["physical_burst", "sustained_carry"], 43: ["magic_burst"],
    44: ["physical_burst", "evasion"], 45: ["magic_burst", "pure_dot"],
    46: ["physical_burst"], 47: ["pure_dot"],
    48: ["sustained_carry", "physical_burst"], 49: ["sustained_carry"],
    50: ["lifesteal_regen", "magic_burst"], 51: ["hard_disable_ult"],
    52: ["magic_burst"], 53: ["sustained_carry"],
    54: ["sustained_carry", "lifesteal_regen"], 55: ["magic_burst"],
    56: ["sustained_carry", "invisible"], 57: ["lifesteal_regen", "buff_reliant"],
    58: ["sustained_carry", "evasion"], 59: ["physical_burst", "lifesteal_regen"],
    60: ["physical_burst"], 61: ["sustained_carry", "lifesteal_regen"],
    62: ["invisible", "physical_burst"], 63: ["sustained_carry", "mobility_escape"],
    64: ["magic_burst"], 65: ["hard_disable_ult", "magic_burst"],
    66: ["lifesteal_regen"], 67: ["sustained_carry", "illusions"],
    68: ["magic_burst", "pure_dot"], 69: ["hard_disable_ult"],
    70: ["physical_burst"], 71: ["hard_disable_ult", "physical_burst"],
    72: ["sustained_carry", "magic_burst"], 73: ["sustained_carry", "physical_burst"],
    74: ["magic_burst"], 75: ["magic_burst", "hard_disable_ult"],
    76: ["magic_burst"], 77: ["sustained_carry"],
    78: ["physical_burst"], 79: ["magic_burst"],
    80: ["sustained_carry"], 81: ["illusions", "physical_burst"],
    82: ["physical_burst", "illusions"], 83: ["lifesteal_regen"],
    84: ["magic_burst"], 85: ["lifesteal_regen"],
    86: ["magic_burst"], 87: ["hard_disable_ult", "magic_burst"],
    88: ["hard_disable_ult", "invisible"], 89: ["illusions", "hard_disable_ult"],
    90: ["magic_burst"], 91: ["physical_burst"],
    92: ["sustained_carry", "mobility_escape"], 93: ["sustained_carry", "mana_dependent"],
    94: ["physical_burst", "sustained_carry"], 95: ["physical_burst", "hard_disable_ult"],
    96: ["hard_disable_ult", "physical_burst"], 97: ["sustained_carry"],
    98: ["sustained_carry", "pure_dot", "lifesteal_regen"], 99: ["hard_disable_ult", "physical_burst"],
    100: ["magic_burst"], 101: ["lifesteal_regen", "buff_reliant"],
    102: ["hard_disable_ult", "magic_burst"], 103: ["hard_disable_ult", "physical_burst"],
    104: ["magic_burst"], 105: ["physical_burst", "mobility_escape"],
    106: ["hard_disable_ult", "magic_burst"], 107: ["magic_burst"],
    108: ["illusions", "sustained_carry"], 109: ["hard_disable_ult", "magic_burst"],
    110: ["lifesteal_regen", "buff_reliant"], 112: ["hard_disable_ult", "magic_burst"],
    113: ["illusions", "sustained_carry"], 114: ["physical_burst", "mobility_escape"],
    119: ["hard_disable_ult", "magic_burst"], 120: ["physical_burst", "hard_disable_ult"],
    121: ["hard_disable_ult", "magic_burst"], 123: ["magic_burst", "hard_disable_ult"],
    126: ["magic_burst", "mobility_escape"], 128: ["magic_burst", "hard_disable_ult"],
    129: ["hard_disable_ult", "physical_burst"], 135: ["physical_burst", "lifesteal_regen"],
    136: ["physical_burst", "hard_disable_ult"], 137: ["hard_disable_ult", "physical_burst"],
    138: ["physical_burst", "ghost_form"], 145: ["hard_disable_ult", "magic_burst"],
    146: ["physical_burst", "mobility_escape"],
}

TAG_ITEMS = {
    "hard_disable_ult": {
        "carry": [("Linken's Sphere", "блокирует направрованный контроль", "mid"), ("Black King Bar", "защита от массового фокуса", "mid")],
        "mid": [("Linken's Sphere", "блокирует точечную инициацию", "mid"), ("Black King Bar", "дает свободно прокастовать в бою", "mid")],
        "offlaner": [("Lotus Orb", "сбрасывает дебаффы и отражает заклинания", "mid"), ("Pipe of Insight", "защищает команду от сопутствующего магического урона", "mid")],
        "support": [("Force Staff", "выталкивает союзника из зоны поражения", "early"), ("Glimmer Cape", "маскирует цель под контролем", "early")],
    },
    "magic_burst": {
        "carry": [("Black King Bar", "полный иммунитет к магическому урону и контролю", "mid")],
        "mid": [("Black King Bar", "иммунитет к магическому фокусу", "mid"), ("Eternal Shroud", "конвертирует магический урон в ману", "mid")],
        "offlaner": [("Pipe of Insight", "магический щит на всю команду", "mid"), ("Eternal Shroud", "высокая выживаемость против прокаста", "early")],
        "support": [("Glimmer Cape", "магический барьер и невидимость", "early")],
    },
    "physical_burst": {
        "carry": [("Blade Mail", "возврат урона при физическом фокусе", "early"), ("Assault Cuirass", "высокая броня против критического урона", "late")],
        "mid": [("Wind Waker", "сейв от физического фокуса", "late"), ("Blade Mail", "возврат урона", "early")],
        "offlaner": [("Heaven's Halberd", "обезоруживает физического керри на 3-5 сек", "mid"), ("Crimson Guard", "блок физического урона по всей команде", "mid")],
        "support": [("Ghost Scepter", "полный иммунитет к физическим атакам", "early")],
    },
    "sustained_carry": {
        "carry": [("Satanic", "мгновенный отхил в длительном бое", "late")],
        "mid": [("Orchid Malevolence", "затыкает врага до применения баффов", "mid")],
        "offlaner": [("Blade Mail", "наказывает за долгий урон", "early"), ("Shiva's Guard", "снижает скорость атаки и лечение", "mid")],
        "support": [("Force Staff", "кайт вражеского керри", "early")],
    },
    "evasion": {
        "carry": [("Monkey King Bar", "пробивает уклонение (75% точных атак)", "mid")],
        "mid": [("Monkey King Bar", "игнорирует промахи", "mid")],
        "offlaner": [("Solar Crest", "дает точность и защиту союзникам", "early")],
        "support": [("Eul's Scepter of Divinity", "поднимает врага, выигрывая время", "early")],
    },
    "illusions": {
        "carry": [("Maelstrom / Mjollnir", "молнии быстро очищают поле от иллюзий", "mid"), ("Battle Fury", "сплеш-урон по группе иллюзий", "early")],
        "mid": [("Maelstrom", "быстрый фарм и зачистка иллюзий", "mid")],
        "offlaner": [("Shiva's Guard", "АОЕ урон и срезание регенерации иллюзий", "mid"), ("Radiance", "постоянный АОЕ урон по клонам", "mid")],
        "support": [("Ghost Scepter", "защищает от физического урона иллюзий", "early")],
    },
    "invisible": {
        "carry": [("Dust of Appearance", "для самостоятельной реализации убийств", "early")],
        "mid": [("Dust of Appearance", "для ганков невидимых целей", "early")],
        "offlaner": [("Dust of Appearance", "для инициации в невидимых целей", "early")],
        "support": [("Sentry Wards / Dust", "активный контроль обзора и невидимости", "early")],
    },
    "lifesteal_regen": {
        "carry": [("Eye of Skadi", "уменьшает лечение и регенерацию цели на 40%", "late")],
        "mid": [("Spirit Vessel", "уменьшает лечение цели на 45%", "early")],
        "offlaner": [("Spirit Vessel", "сокращает регенерацию хилеров", "early")],
        "support": [("Spirit Vessel", "базовый предмет против сильного отхила", "early")],
    },
    "pure_dot": {
        "carry": [("Manta Style", "сбрасывает отрицательные эффекты и яды", "mid")],
        "mid": [("Eul's Scepter of Divinity", "сбрасывает периодические дебаффы", "early")],
        "offlaner": [("Lotus Orb", "снимает периодические дебаффы с себя и команды", "mid")],
        "support": [("Glimmer Cape", "снижает входящий урон", "early")],
    },
    "mobility_escape": {
        "carry": [("Abyssal Blade", "надежный стан сквозь БКБ", "late"), ("Scythe of Vyse", "мгновенный хекс", "late")],
        "mid": [("Orchid Malevolence", "безмолвие прерывает побег", "early"), ("Scythe of Vyse", "контроль без задержки", "late")],
        "offlaner": [("Blink Dagger", "быстрая инициация до того, как цель уйдет", "early")],
        "support": [("Eul's Scepter of Divinity", "сбивает мобильность и прерывает касты", "early")],
    },
    "mana_dependent": {
        "carry": [("Diffusal Blade / Disperser", "сжигает ману и лишает способности кастовать", "early")],
        "mid": [("Diffusal Blade", "быстро лишает ресурса манозависимых героев", "early")],
        "offlaner": [("Shiva's Guard", "срезает манареген и замедляет", "mid")],
        "support": [("Eul's Scepter of Divinity", "контроль для сбивания ритма", "early")],
    },
    "buff_reliant": {
        "carry": [("Nullifier", "непрерывно снимает положительные эффекты и баффы", "late")],
        "mid": [("Nullifier", "снимает защитные баффы и сейвы", "late")],
        "offlaner": [("Nullifier", "развеивает защитные заклинания врага", "late")],
        "support": [("Eul's Scepter of Divinity", "развеивает положительные эффекты при применении на врага", "early")],
    },
    "ghost_form": {
        "carry": [("Nullifier", "снимает Ghost-форму и защитные саппорт-предметы", "late")],
        "mid": [("Nullifier", "снимает эфирное состояние Muerta/Ghost Scepter", "late")],
        "offlaner": [("Pipe of Insight / Black King Bar", "ультимейт Muerta наносит магический урон", "mid")],
        "support": [("Glimmer Cape / Pipe of Insight", "защита от магического урона под её ультимейтом", "early")],
    }
}

SPECIAL_NOTES = {
    1: {
        "carry": [("Diffusal Blade / Disperser", "сжигает ману Anti-Mage быстрее, чем он успевает разогнаться на Battle Fury", "early")],
        "mid": [("Orchid Malevolence", "затыкает до того, как он успеет Blink + Manta в бою", "mid")],
        "offlaner": [("Heaven's Halberd", "обезоруживает Anti-Mage на время действия эффекта", "mid")],
        "support": [("Ghost Scepter", "не даёт Anti-Mage бить физическими атаками", "early")],
    },
    2: {
        "carry": [("Linken's Sphere", "полностью блокирует Berserker's Call", "mid")],
        "mid": [("Linken's Sphere", "не даёт затащить в Call перед добивающим Culling Blade", "mid")],
        "offlaner": [("Force Staff", "выход за радиус Call до завершения каста", "early")],
        "support": [("Aeon Disk", "переживает добивающий Culling Blade на низком HP", "late")],
    },
    3: {
        "carry": [("Aeon Disk", "спасает, если Bane всё же поймал в захват Fiend's Grip", "late")],
        "mid": [("Force Staff", "уходит из зоны каста до того, как Bane успеет подобраться", "early")],
        "offlaner": [("Glimmer Cape", "невидимость не даёт Bane нацелиться первым", "early")],
        "support": [("Force Staff", "вытаскивает союзника, пока захват ещё не начался", "early")],
    },
    14: {"carry": [("Linken's Sphere", "блокирует Hook и Dismember", "mid")]},
    36: {"carry": [("Nullifier", "снимает Ghost Form с Necrophos", "late")]},
    41: {"support": [("Aeon Disk", "выживание при попадании в Chronosphere", "late")]},
    57: {"carry": [("Nullifier", "снимает Guardian Angel и Repel", "late")]},
    62: {
        "carry": [("Smoke of Deceit", "безопасное перемещение по карте, чтобы не спалили под Track", "early")],
        "mid": [("Sentry Wards", "снимает невидимость до того, как Jinada нанесёт бонус-урон", "early")],
        "offlaner": [("Tranquil Boots", "компенсирует урон от внезапных забеков через Jinada", "early")],
        "support": [("Sentry Wards", "закрывает обзор у рун и леса от разведки Track", "early")],
    },
    69: {"carry": [("Linken's Sphere", "полностью блокирует ультимейт Doom", "mid")]},
    85: {"support": [("Spirit Vessel", "нейтрализует регенерацию от Decay", "early")]},
    93: {"carry": [("Diffusal Blade / Disperser", "быстро уничтожает Mana Shield Medusa", "early")]},
    103: {"support": [("Linken's Sphere", "блокирует Duel на ранней стадии", "mid")]},
    138: {"carry": [("Nullifier", "развеивает эфирную форму Muerta", "late")],
          "support": [("Pipe of Insight", "защищает от магического урона ультимейта Muerta", "mid")]},
}

# Исключения "конкретный герой (которого мы пикаем) против конкретного врага" —
# самый точный уровень детализации: перекрывает и роль, и общий SPECIAL_NOTES,
# когда обычный совет для роли не подходит именно этому герою.
# Формат: (candidate_id, enemy_id) -> список (предмет, причина, тайминг)
# Список стартовый, не исчерпывающий — сюда добавляются кейсы по мере того,
# как замечена нестыковка "по роли ок, но конкретному герою не подходит".
HERO_VS_HERO_OVERRIDES = {
    (12, 93): [("Manta Style", "иллюзии Phantom Lancer не получают эффект от орб-способности Diffusal — выгоднее давить количеством и сбрасывать дебаффы Мантой", "mid")],
}

TIMING_LABEL = {"early": "Ранняя игра (0–15 мин)", "mid": "Середина игры (15–30 мин)", "late": "Поздняя игра (30+ мин)"}
TIMING_ORDER = ["early", "mid", "late"]

# Категория урона/эффекта для угрозы — используется, чтобы на переднем экране
# сразу показать "что покупать против каста / физа", без лишних деталей.
TAG_CATEGORY = {
    "magic_burst": "magic", "pure_dot": "magic", "ghost_form": "magic",
    "physical_burst": "physical", "sustained_carry": "physical",
    "illusions": "physical", "evasion": "physical", "invisible": "physical",
    "lifesteal_regen": "sustain",
    "hard_disable_ult": "control", "mobility_escape": "control",
    "mana_dependent": "other", "buff_reliant": "other",
}
CATEGORY_LABEL = {
    "specific": "Точечно против конкретного героя",
    "magic": "Против магии",
    "physical": "Против физического урона",
    "control": "Контроль / спасение",
    "sustain": "Против лечения и реген.",
    "other": "Прочее",
}
CATEGORY_ORDER = ["specific", "magic", "physical", "control", "sustain", "other"]

# Короткая "фирменная" причина, почему герой силён — используется в блоке
# "Почему этот пик?" как смысловая часть объяснения (не просто цифры).
HERO_STRENGTHS = {
    1: "разгоняется в фарме и выключает саппортов Manta+Blink",
    2: "Berserker's Call держит и наказывает мили-состав врага",
    5: "Freezing Field контролирует и наносит АОЕ-урон по замершей толпе",
    7: "Echo Slam умножает урон по скученной команде врага",
    8: "иммунитет к магии и урону через Вращение (Blade Fury)",
    9: "Song of the Moon держит толпу, а Leap даёт мобильность в ганках",
    10: "Waveform + Replicate дают взрыв урона и контроль по площади",
    11: "Requiem of Souls выносит толпу, если враги скучены",
    12: "иллюзии Phantom Lancer сложно сфокусировать без АОЕ",
    13: "Phase Shift даёт неуязвимость, пока идёт урон по площади",
    14: "Hook стабильно достаёт цели и создаёт давление на линии",
    16: "Epicenter добивает толпу после контроля союзников",
    17: "Ball Lightning даёт мгновенный урон и мобильность сквозь карту",
    18: "God's Strength даёт разовый мощный урон в стычке",
    19: "Avalanche + Toss наносит взрывной урон по плотной группе",
    21: "Shackleshot фиксирует цель, Focus Fire добивает",
    22: "Static Field и Thundergod's Wrath дают мгновенный АОЕ-урон",
    26: "Hex мгновенно снимает угрозу без каста",
    27: "Shackles обездвиживает и наносит урон по цели",
    29: "Ravage массово контролирует толпу для командного боя",
    30: "Death Ward наносит стабильный урон по приоритетной цели",
    33: "Black Hole группирует врагов для командного вайпа",
    35: "высокий стабильный урон на дистанции без риска",
    36: "Reaper's Scythe добивает низкое HP на любой дистанции",
    39: "высокий бурст-урон комбо в ранней и средней игре",
    41: "Chronosphere изолирует цель для гарантированного килла",
    42: "Reincarnation даёт живучесть в затяжных боях",
    44: "Coup de Grace даёт шанс на критический бурст-урон",
    48: "Eclipse наносит стабильный высокий урон по одиночной цели",
    49: "Elder Dragon Form даёт универсальный дальний урон",
    54: "Rage делает неуязвимым к магии в решающий момент",
    59: "Life Break наносит урон, пропорциональный недостающему HP",
    67: "Desolate добивает изолированные цели с высоким уроном",
    69: "Doom выключает вражеский ультимейт и предметы",
    70: "Fury Swipes наращивает урон в затяжной драке",
    72: "Call Down наносит АОЕ-урон с дальней дистанции",
    74: "гибкий набор заклинаний под любую ситуацию боя",
    80: "Spirit Bear даёт вторую боевую единицу на линии и в тимфайтах",
    81: "иллюзии Chaos Knight сложно отличить от оригинала под Phantasm",
    92: "Dark Pact снимает дебаффы и наносит урон по себе и рядом",
    93: "Split Shot и Stone Gaze контролируют пространство боя",
    96: "Reverse Polarity группирует врагов для командного вайпа",
    99: "Walrus Punch даёт мгновенный бурст физического урона",
    103: "Duel гарантированно выключает одну цель из боя",
    105: "Sleight of Fist наносит АОЕ-урон, оставаясь неуязвимым",
    108: "Metamorphosis даёт дальний урон и разрушение построек",
    113: "Tempest Double удваивает урон и способности на время",
    138: "Dead Shot добивает цели независимо от расстояния",
}


def get_best_matchup(candidate_id: int, enemy_ids: list[int]):
    """Лучший matchup из high-MMR ранкеда с про-матчами как запасным источником."""
    best = None
    pro = fetch_matchups(enemy_ids)
    high_mmr = fetch_ranked_matchups(enemy_ids)
    for enemy_id in enemy_ids:
        rg, re_wins = high_mmr.get(enemy_id, {}).get(candidate_id, (0, 0))
        pg, pe_wins = pro.get(enemy_id, {}).get(candidate_id, (0, 0))
        if rg >= 10:
            games, losses, prior_games, source = rg, re_wins, 20, "Divine/Immortal"
        elif pg >= MIN_GAMES_THRESHOLD:
            games, losses, prior_games, source = pg, pe_wins, SHRINK_K, "про"
        else:
            continue
        raw_wr = (games - losses) / games * 100
        adjusted_wr = (games - losses + prior_games * 0.5) / (games + prior_games) * 100
        if best is None or adjusted_wr > best[1]:
            best = (HEROES.get(enemy_id, str(enemy_id)), adjusted_wr, games, raw_wr, source)
    return best


def generate_pick_reason(pick: dict, enemy_ids: list[int]) -> str:
    """Коротко объясняет оценку с учётом всего выбранного состава."""
    parts = [f"оценка против всего состава — {pick['score']:.0f}%"]
    matched = pick.get("matched_enemies", 0)
    if enemy_ids:
        parts.append(f"данные по {matched} из {len(enemy_ids)} врагов")
    trait = HERO_STRENGTHS.get(pick["id"])
    if trait:
        parts.append(trait)
    return " + ".join(parts)

# ===================================================================
# 3. АДАПТИВНЫЕ БИЛДЫ ПО РОЛЯМ И ГЕРОЯМ
# ===================================================================

ROLE_CORE_BUILDS = {
    "carry": {
        "start": [("Tango", "восстановление здоровья"), ("Quelling Blade", "урон по крипам"), ("Slippers of Agility / Circlet", "базовые характеристики")],
        "early": [("Power Treads / Phase Boots", "мобильность и урон"), ("Magic Wand", "накопление зарядов здоровья/маны")],
        "core": [("Maelstrom / Battle Fury / Yasha", "ускорение фарма и базовый урон"), ("Black King Bar", "защита от контроля в боях")],
        "late": [("Butterfly / Eye of Skadi / Satanic", "превосходство в поздней игре")],
    },
    "mid": {
        "start": [("Tango", "восстановление здоровья"), ("Circlet", "базовые характеристики"), ("Faerie Fire", "мгновенный хил и урон")],
        "early": [("Bottle", "контроль рун и ресурсов"), ("Power Treads / Boots of Travel", "мобильность по карте")],
        "core": [("Witch Blade / Orchid / Yasha and Kaya", "активный темп и драки"), ("Black King Bar", "безопасность в командных сражениях")],
        "late": [("Scythe of Vyse", "контроль ключевой цели"), ("Aghanim's Scepter", "усиление способностей")],
    },
    "offlaner": {
        "start": [("Tango", "восстановление здоровья"), ("Ring of Protection", "броня на линии"), ("Iron Branch", "базовые характеристики")],
        "early": [("Phase Boots", "броня и скорость передвижения"), ("Vanguard / Magic Wand", "выживаемость на сложной линии")],
        "core": [("Blink Dagger", "инициация боев"), ("Blade Mail / Pipe of Insight", "впитывание урона и защита команды")],
        "late": [("Shiva's Guard / Heart of Tarrasque", "плотность в драках")],
    },
    "support": {
        "start": [("Tango", "обмен ресурсами с керри"), ("Observer & Sentry Wards", "контроль обзора"), ("Blood Grenade", "агрессия на первых уровнях")],
        "early": [("Arcane Boots", "восстановление маны команде"), ("Magic Wand", "набор стиков")],
        "core": [("Force Staff", "позиционирование и спасение"), ("Glimmer Cape", "защита от магического урона и невидимость")],
        "late": [("Aghanim's Shard / Scepter", "усиление умений"), ("Aether Lens / Solar Crest", "утилити-поддержка")],
    },
}

HERO_SPECIFIC_BUILDS = {
    1: {
        "start": [("Tango", "восстановление здоровья"), ("Quelling Blade", "урон по крипам"), ("Iron Branch x2", "базовые характеристики")],
        "early": [("Power Treads", "скорость атаки и манабуз"), ("Ring of Health", "регенерация под Battle Fury")],
        "core": [("Battle Fury", "ускорение фарма"), ("Manta Style", "сброс сайленса и сжигание маны")],
        "late": [("Basher -> Abyssal Blade", "контроль сквозь БКБ"), ("Butterfly", "уклонение и урон")],
    },
    5: {
        "start": [("Tango", "восстановление здоровья"), ("Blood Grenade", "замедление для первой крови"), ("Sentry Ward", "снятие варда")],
        "early": [("Tranquil Boots", "регенерация и скорость"), ("Magic Wand", "набор стиков")],
        "core": [("Glimmer Cape", "Каст Freezing Field под невидимостью"), ("Force Staff", "позиционирование")],
        "late": [("Black King Bar", "непрерывный каст ультимейта"), ("Aghanim's Shard", "длительный контроль")],
    },
    14: {
        "start": [("Tango", "восстановление здоровья"), ("Gauntlets of Strength x2", "здоровье"), ("Ring of Protection", "броня")],
        "early": [("Phase Boots", "скорость для позиционирования"), ("Vanguard", "блок урона под Rot")],
        "core": [("Blink Dagger", "быстрый Hook/Dismember"), ("Aghanim's Scepter", "увеличенный радиус и урон Rot")],
        "late": [("Heart of Tarrasque", "запас здоровья"), ("Shiva's Guard", "срезание регенерации врагов")],
    },
    42: {
        "start": [("Tango", "восстановление здоровья"), ("Quelling Blade", "фарм"), ("Circlet", "базовые характеристики")],
        "early": [("Phase Boots", "мобильность"), ("Armlet of Mordiggian", "ранний разгон урона")],
        "core": [("Desolator", "снижение брони"), ("Blink Dagger", "инициация")],
        "late": [("Assault Cuirass", "аура брони"), ("Abyssal Blade", "контроль цели")],
    },
    67: {
        "start": [("Tango", "восстановление здоровья"), ("Quelling Blade", "урон по крипам"), ("Circlet", "базовые характеристики")],
        "early": [("Power Treads", "характеристики"), ("Blade Mail", "фарм и возврат урона")],
        "core": [("Radiance", "урон по области"), ("Manta Style", "активация Desolate")],
        "late": [("Heart of Tarrasque", "выживаемость"), ("Eye of Skadi", "замедление цели")],
    },
    74: {
        "start": [("Tango", "восстановление здоровья"), ("Circlet", "базовые характеристики"), ("Faerie Fire", "урон")],
        "early": [("Urn of Shadows", "зарядка под Cold Snap"), ("Power Treads / BoT", "мобильность")],
        "core": [("Spirit Vessel", "урон по плотным целям"), ("Aghanim's Scepter", "усиление заклинаний")],
        "late": [("Scythe of Vyse", "контроль"), ("Refresher Orb", "двойной прокаст")],
    },
    # Резервный керри-билд, если D2PT/OpenDota временно не отдают историю покупок.
    108: {
        "start": [("Tango", "восстановление здоровья"), ("Quelling Blade", "добивание крипов"),
                  ("Iron Branch x2", "стартовые характеристики")],
        "early": [("Power Treads", "скорость атаки и гибкость характеристик"),
                  ("Magic Wand", "заряды для выживания на линии"),
                  ("Falcon Blade", "урон, здоровье и регенерация маны")],
        "core": [("Yasha", "разгон фарма и скорости атаки"),
                 ("Manta Style", "иллюзии и снятие сайленса"),
                 ("Dragon Lance / Hurricane Pike", "дальность атаки и позиционирование")],
        "late": [("Eye of Skadi", "характеристики и снижение восстановления врагов"),
                 ("Black King Bar", "защита от контроля"),
                 ("Butterfly / Daedalus", "урон и усиление физического керри")],
    }
}

TIMING_TO_STAGE = {"early": "early", "mid": "core", "late": "late"}

# Предметы-контрпики больше не считаются автоматически подходящими только
# потому, что герой играет на этой позиции. Для героев с ручным билдом
# сначала используются предметы из его билда, затем небольшой список
# действительно универсальных ситуативных предметов.
UNIVERSAL_SITUATIONAL_ITEMS = {
    "Black King Bar", "Linken's Sphere", "Lotus Orb", "Manta Style",
    "Nullifier", "Aghanim's Scepter", "Aghanim's Shard", "Blink Dagger",
    "Force Staff", "Glimmer Cape", "Ghost Scepter", "Eul's Scepter of Divinity",
    "Spirit Vessel", "Heaven's Halberd", "Pipe of Insight", "Sentry Wards",
    "Dust of Appearance", "Smoke of Deceit",
}

# Явные исключения для ситуаций "вещь хороша на роли, но не в этом билде".
# Это обычный слой данных, а не зашитая в SQL логика: список можно расширять
# по мере появления новых героев/патчей.
HERO_ITEM_RULES = {
    1: {"blocked": {"Pipe of Insight", "Glimmer Cape", "Crimson Guard"}},
    5: {"blocked": {"Battle Fury", "Desolator", "Radiance", "Butterfly"}},
    14: {"blocked": {"Battle Fury", "Manta Style", "Diffusal Blade", "Butterfly"}},
    42: {"blocked": {"Glimmer Cape", "Pipe of Insight", "Eul's Scepter of Divinity"}},
    67: {"blocked": {"Glimmer Cape", "Pipe of Insight", "Eul's Scepter of Divinity"}},
    74: {"blocked": {"Butterfly", "Assault Cuirass", "Satanic"}},
}


def _item_parts(item: str) -> set[str]:
    """Разворачивает записи вида 'Basher -> Abyssal Blade' и 'A / B'."""
    return {
        part.strip()
        for part in re.split(r"\s*(?:/|->)\s*", item)
        if part.strip()
    }


def _hero_build_items(hero_id: int) -> set[str]:
    build = HERO_SPECIFIC_BUILDS.get(hero_id, {})
    return {
        part
        for stage in build.values()
        for item, _reason in stage
        for part in _item_parts(item)
    }


def _is_item_suitable_for_hero(hero_id: int | None, item: str, category: str) -> bool:
    """Фильтрует рольные советы через конкретный геройский профиль."""
    if hero_id is None:
        return True

    candidate_items = _item_parts(item)
    rules = HERO_ITEM_RULES.get(hero_id, {})
    if candidate_items & rules.get("blocked", set()):
        return False

    # Точечный override имеет приоритет: он добавлен именно для пары героев.
    if category == "specific":
        return True

    # Для героев с ручным билдом не показываем весь каталог роли подряд.
    # Оставляем только предметы его билда и универсальные ситуативные ответы.
    if hero_id in HERO_SPECIFIC_BUILDS:
        allowed = _hero_build_items(hero_id) | UNIVERSAL_SITUATIONAL_ITEMS
        return bool(candidate_items & allowed)
    return True


def generate_adaptive_build(hero_id: int, my_role: str, enemy_ids: list[int], pro_plan=None):
    """Возвращает (билд, источник): 'pro' — про-покупки героя, 'hero' — ручной билд, 'role' — костяк позиции."""
    role_base = ROLE_CORE_BUILDS.get(my_role) or ROLE_CORE_BUILDS[base_role(my_role)]
    static = HERO_SPECIFIC_BUILDS.get(hero_id)
    pro_build = plan_to_build(pro_plan)
    if pro_build:
        base = pro_build
        source = pro_plan.get("source", "opendota-pro")
        for stage, items in base.items():
            if not items:
                base[stage] = list((static or role_base).get(stage, []))
    elif static:
        base, source = static, "hero"
    else:
        base, source = role_base, "role"
    build = copy.deepcopy(base)

    # Убираем повторы между про-билдом, ручным билдом и контрсоветами.
    def item_key(value: str) -> str:
        return re.sub(r"[^a-z0-9]", "", value.lower())

    seen = {item_key(part) for items in build.values() for item, _ in items for part in _item_parts(item)}
    for counter in get_counters_against(enemy_ids, my_role, candidate_id=hero_id):
        stage = TIMING_TO_STAGE[counter["timing"]]
        fresh = [part for part in _item_parts(counter["item"]) if item_key(part) not in seen]
        if not fresh:
            continue
        build[stage].append((" / ".join(fresh), f"Ситуативно против {', '.join(counter['targets'])}: {counter['reason']}"))
        seen.update(item_key(part) for part in fresh)

    for stage, items in build.items():
        unique, stage_seen = [], set()
        for item, reason in items:
            key = tuple(sorted(item_key(part) for part in _item_parts(item)))
            if key in stage_seen:
                continue
            stage_seen.add(key)
            unique.append((item, reason))
        build[stage] = unique
    return build, source


def get_role_name(role_key):
    roles = {
        "carry": "Керри (Позиция 1)",
        "mid": "Мидер (Позиция 2)",
        "offlaner": "Офлейнер (Позиция 3)",
        "support4": "Саппорт (Позиция 4)",
        "support5": "Хард-саппорт (Позиция 5)",
        "support": "Саппорт (Позиция 4-5)"
    }
    return roles.get(role_key, role_key)


def get_counters_against(enemy_ids, my_role, candidate_id=None):
    """
    candidate_id — id героя, за которого играем (не только роль).
    Если для пары (candidate_id, enemy_id) есть точное исключение в
    HERO_VS_HERO_OVERRIDES — используется оно, и общий совет по роли/тегам
    для этого врага не показывается (чтобы не путать: не "и то, и то",
    а именно "то, что подходит конкретно этому герою").
    """
    my_role = base_role(my_role)
    grouped = {}
    for hero_id in enemy_ids:
        if hero_id not in HEROES:
            continue
        hero_name = HEROES[hero_id]

        override = HERO_VS_HERO_OVERRIDES.get((candidate_id, hero_id)) if candidate_id else None
        if override:
            for item, reason, timing in override:
                if not _is_item_suitable_for_hero(candidate_id, item, "specific"):
                    continue
                entry = grouped.setdefault(item, {"reason": reason, "timing": timing, "targets": [], "category": "specific"})
                entry["reason"] = reason
                entry["timing"] = timing
                entry["category"] = "specific"
                if hero_name not in entry["targets"]:
                    entry["targets"].append(hero_name)
            continue  # исключение полностью заменяет общий совет для этого врага

        for tag in HERO_TAGS.get(hero_id, []):
            category = TAG_CATEGORY.get(tag, "other")
            for item, reason, timing in TAG_ITEMS.get(tag, {}).get(my_role, []):
                if not _is_item_suitable_for_hero(candidate_id, item, category):
                    continue
                grouped.setdefault(item, {"reason": reason, "timing": timing, "targets": [], "category": category})
                if hero_name not in grouped[item]["targets"]:
                    grouped[item]["targets"].append(hero_name)

        for item, reason, timing in SPECIAL_NOTES.get(hero_id, {}).get(my_role, []):
            if not _is_item_suitable_for_hero(candidate_id, item, "specific"):
                continue
            entry = grouped.setdefault(item, {"reason": reason, "timing": timing, "targets": [], "category": "specific"})
            entry["reason"] = reason
            entry["timing"] = timing
            entry["category"] = "specific"
            if hero_name not in entry["targets"]:
                entry["targets"].append(hero_name)

    return [{"item": item, **d} for item, d in grouped.items()]


# ===================================================================
# 3b. ИСПРАВЛЕНИЕ ID ГЕРОЕВ И РАЗДЕЛЕНИЕ ПОЗИЦИЙ 4 И 5
# ===================================================================
# В исходной таблице не было героя Io (id 91), поэтому id с 91 по 110
# были сдвинуты на единицу относительно OpenDota (Medusa считалась 93,
# хотя в OpenDota это Slark; Legion Commander считался 103 — это Elder
# Titan), а Ringmaster и Kez имели неверные id. Из-за этого статистика
# приходила от других героев. Все таблицы ниже переписаны на верные id.
# Дополнительно check_hero_ids() сверяет имена с OpenDota при запуске.

_ID_FIX = {i: i + 1 for i in range(91, 111)}
_ID_FIX.update({145: 131, 146: 145})


def _fx(hero_id):
    return _ID_FIX.get(hero_id, hero_id)


def _remap_keys(table):
    fixed = {_fx(k): v for k, v in table.items()}
    table.clear()
    table.update(fixed)


for _table in (HEROES, HERO_ROLES, HERO_TAGS, HERO_STRENGTHS, SPECIAL_NOTES,
               HERO_ITEM_RULES, HERO_SPECIFIC_BUILDS):
    _remap_keys(_table)

_fixed_overrides = {(_fx(a), _fx(b)): v for (a, b), v in HERO_VS_HERO_OVERRIDES.items()}
HERO_VS_HERO_OVERRIDES.clear()
HERO_VS_HERO_OVERRIDES.update(_fixed_overrides)

HEROES[91] = "Io"
HERO_ROLES[91] = "support"

# ---------- позиции: 1, 2, 3, 4 и 5 отдельно ----------

POSITIONS = ["carry", "mid", "offlaner", "support4", "support5"]

_SUPPORT5 = {
    "Crystal Maiden", "Lion", "Shadow Shaman", "Witch Doctor", "Lich", "Warlock", "Dazzle",
    "Omniknight", "Chen", "Ancient Apparition", "Undying", "Io", "Bane", "Vengeful Spirit",
    "Oracle", "Winter Wyvern", "Treant Protector",
}
_SUPPORT4 = {
    "Earthshaker", "Mirana", "Venomancer", "Bounty Hunter", "Rubick", "Nyx Assassin", "Tusk",
    "Techies", "Phoenix", "Dark Willow", "Hoodwink", "Marci", "Ringmaster",
}
_SUPPORT_BOTH = {
    "Jakiro", "Ogre Magi", "Silencer", "Disruptor", "Snapfire", "Grimstroke",
    "Keeper of the Light", "Skywrath Mage", "Shadow Demon",
}
_EXTRA_SUPPORT4 = {
    "Pudge", "Clockwerk", "Tiny", "Spirit Breaker", "Earth Spirit", "Batrider",
    "Nature's Prophet", "Weaver",
}


def _build_positions():
    positions = {}
    for hero_id, role in HERO_ROLES.items():
        name = HEROES.get(hero_id, "")
        if role != "support":
            positions[hero_id] = {role}
        elif name in _SUPPORT_BOTH:
            positions[hero_id] = {"support4", "support5"}
        elif name in _SUPPORT5:
            positions[hero_id] = {"support5"}
        elif name in _SUPPORT4:
            positions[hero_id] = {"support4"}
        else:
            positions[hero_id] = {"support4", "support5"}
        if name in _EXTRA_SUPPORT4:
            positions[hero_id].add("support4")
    return positions


HERO_POSITIONS = _build_positions()


def hero_has_role(hero_id, role):
    return role in HERO_POSITIONS.get(hero_id, set())


def base_role(role):
    """Таблицы контрпредметов хранятся по 'support'; позиции 4 и 5 делят их."""
    return "support" if role in ("support4", "support5") else role


ROLE_CORE_BUILDS["support4"] = {
    "start": [("Tango", "обмен ресурсами с керри"), ("Blood Grenade", "агрессия на первых уровнях"),
              ("Observer & Sentry Wards", "контроль обзора")],
    "early": [("Arcane Boots / Tranquil Boots", "мана команде или регенерация"), ("Magic Wand", "набор зарядов здоровья и маны")],
    "core": [("Blink Dagger / Force Staff", "инициация и позиционирование"), ("Glimmer Cape", "защита от магии и невидимость")],
    "late": [("Aghanim's Shard / Scepter", "усиление умений"), ("Aether Lens / Solar Crest", "радиус каста и утилити")],
}
ROLE_CORE_BUILDS["support5"] = {
    "start": [("Tango", "обмен ресурсами с керри"), ("Observer & Sentry Wards", "контроль обзора и вардинг"),
              ("Clarity", "мана на ранней линии")],
    "early": [("Tranquil Boots", "регенерация на ходу"), ("Magic Wand", "набор зарядов здоровья и маны")],
    "core": [("Glimmer Cape / Force Staff", "спасение союзника"), ("Pipe of Insight / Lotus Orb", "защита команды")],
    "late": [("Aghanim's Shard / Scepter", "усиление умений"), ("Ghost Scepter / Aeon Disk", "выживание в драке")],
}


# ===================================================================
# 4. ДАННЫЕ: ПРО-ТРЕКЕР OPENDOTA + DOTABUFF (С ОБХОДОМ ЛИМИТОВ ЗАПРОСОВ)
# ===================================================================
# Как теперь устроен обход блокировки OpenDota по частоте запросов.
# Из старого файла (9.py) возвращено: лёгкие SQL-запросы, параллельная
# загрузка, кэш и "мягкое" падение (ошибка не ломает приложение).
# Сверху добавлено:
#   1. ОДИН запрос на всю матрицу про-матчапов вместо запроса на каждого
#      врага: 2 запроса раз в несколько часов, а не 5+ на каждый анализ.
#   2. Дисковый кэш (переживает перезапуск) + "stale-while-revalidate":
#      если кэш устарел, берётся он, а обновление идёт в фоне.
#   3. Общий троттлинг, повторы с задержкой при 429/5xx, учёт Retry-After.
#   4. Цепочка запасных вариантов: матрица -> SQL по каждому врагу
#      (как в 9.py) -> /heroes/{id}/matchups (вне периода, помечается).
#   5. Необязательный ключ OpenDota (OPENDOTA_API_KEY в окружении или
#      в .streamlit/secrets.toml) резко поднимает лимит запросов.

OPENDOTA_API = "https://api.opendota.com/api"
OPENDOTA_EXPLORER_URL = OPENDOTA_API + "/explorer"
OPENDOTA_HEROSTATS_URL = OPENDOTA_API + "/heroStats"
OPENDOTA_HEROES_URL = OPENDOTA_API + "/heroes"
OPENDOTA_HERO_CONSTANTS_URL = OPENDOTA_API + "/constants/heroes"
OPENDOTA_ITEMS_URL = OPENDOTA_API + "/constants/items"
DOTABUFF_BASE = "https://www.dotabuff.com"
# Период для Dotabuff. Если сайт игнорирует значение, попробуй 7d / 30d / 3m / 6m.
DOTABUFF_DATE = "3m"
USER_AGENT = "dota-metrics-app/3.0"
BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)
D2PT_BASE = "https://dota2protracker.com"
D2PT_HEADERS = {
    "User-Agent": BROWSER_UA,
    "Referer": f"{D2PT_BASE}/",
    "Accept": "application/json",
}

PRO_DAYS = 90                  # учитываем только про-матчи за последние ~3 месяца
MIN_GAMES_THRESHOLD = 3        # в про-играх выборка маленькая, порог низкий
SHRINK_K = 12                  # "вес" априорного винрейта при сглаживании
META_SHRINK_K = 10
MATCHUP_WR_MIN_GAMES = 10  # показываем процент только при достаточной выборке
MATRIX_TTL = 6 * 3600
ITEMS_TTL = 12 * 3600
DOTABUFF_TTL = 12 * 3600
CONSTANTS_TTL = 7 * 24 * 3600
MAX_WAIT = 20                  # дольше этого блокировку не пережидаем
MIN_PLAN_GAMES = 5             # минимальная выборка для плана покупок
D2PT_BUILDS_TTL = 30 * 60       # D2PT обновляет данные часто; кэшируем вежливо
RANKED_MATCHUP_TTL = 3 * 3600   # Divine/Immortal матчапы за 30 дней


class ApiError(Exception):
    pass


class ApiBlocked(ApiError):
    pass


def _i(value, default=0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _norm(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(name).lower())


# ---------- дисковый кэш ----------

def _cache_dir():
    here = Path(globals().get("__file__", ".")).resolve().parent
    for base in (here, Path(tempfile.gettempdir())):
        d = base / ".dota_cache"
        try:
            d.mkdir(exist_ok=True)
            probe = d / ".probe"
            probe.write_text("1")
            probe.unlink()
            return d
        except OSError:
            continue
    return None


def _cache_file(key: str):
    d = _cache_dir()
    return None if d is None else d / (hashlib.md5(key.encode()).hexdigest() + ".json")


def disk_read(key: str):
    """Возвращает (данные, возраст_в_секундах) или (None, None)."""
    path = _cache_file(key)
    if path is None or not path.exists():
        return None, None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload["data"], max(0.0, time.time() - payload["saved_at"])
    except (OSError, ValueError, KeyError):
        return None, None


def disk_write(key: str, data) -> None:
    path = _cache_file(key)
    if path is None:
        return
    tmp = path.with_suffix(".tmp")
    try:
        tmp.write_text(json.dumps({"saved_at": time.time(), "data": data}), encoding="utf-8")
        os.replace(tmp, path)
    except OSError:
        pass


# ---------- HTTP-клиент с троттлингом и повторами ----------

class ApiClient:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        self._lock = threading.Lock()
        self._last_call = 0.0
        self._blocked_until = 0.0
        self.min_interval = 0.08 if api_key else 0.35

    def _wait_turn(self):
        with self._lock:
            now = time.time()
            wait = max(self._blocked_until - now, self._last_call + self.min_interval - now, 0.0)
            if wait > MAX_WAIT:
                raise ApiBlocked(f"лимит запросов: подождать нужно ещё ~{int(wait)} с")
            self._last_call = now + wait
        if wait > 0:
            time.sleep(wait)

    @staticmethod
    def _backoff(attempt: int) -> float:
        return min(1.5 * (2 ** attempt) + random.random(), 10.0)

    def _request(self, url, params=None, headers=None, timeout=30, retries=3):
        last_exc = None
        for attempt in range(retries + 1):
            self._wait_turn()
            try:
                resp = self.session.get(url, params=params, headers=headers, timeout=timeout)
            except (requests.Timeout, requests.ConnectionError) as exc:
                last_exc = ApiError(f"{type(exc).__name__}: {exc}")
                time.sleep(self._backoff(attempt))
                continue
            if resp.status_code == 200:
                return resp
            if resp.status_code in (429, 502, 503, 504):
                try:
                    delay = float(resp.headers.get("Retry-After", ""))
                except ValueError:
                    delay = self._backoff(attempt)
                with self._lock:
                    self._blocked_until = max(self._blocked_until, time.time() + delay)
                last_exc = ApiBlocked(f"HTTP {resp.status_code} (лимит или перегрузка сервера)")
                continue
            if resp.status_code == 403:
                raise ApiBlocked("HTTP 403 (доступ закрыт защитой сайта)")
            resp.raise_for_status()
        raise last_exc or ApiError("запрос не удался")

    def get_json(self, url, params=None, timeout=30, headers=None, retries=3):
        params = dict(params or {})
        if self.api_key and "opendota" in url:
            params["api_key"] = self.api_key
        resp = self._request(url, params=params, headers=headers, timeout=timeout, retries=retries)
        try:
            data = resp.json()
        except ValueError as exc:
            raise ApiError("ответ сервера не является JSON") from exc
        if isinstance(data, dict) and data.get("err"):
            raise ApiError(str(data["err"])[:300])
        return data

    def get_text(self, url, headers=None, timeout=25):
        return self._request(url, headers=headers, timeout=timeout, retries=1).text


def _read_api_key():
    key = os.environ.get("OPENDOTA_API_KEY")
    if key:
        return key
    try:
        return st.secrets.get("OPENDOTA_API_KEY")
    except Exception:
        return None


@st.cache_resource(show_spinner=False)
def get_client() -> ApiClient:
    return ApiClient(_read_api_key())


@st.cache_resource(show_spinner=False)
def _inflight():
    return {"lock": threading.Lock(), "keys": set()}


def _run_sql(client: ApiClient, sql: str) -> list:
    return client.get_json(OPENDOTA_EXPLORER_URL, params={"sql": sql}, timeout=45).get("rows", []) or []


def _since() -> str:
    return f"extract(epoch from now() - interval '{PRO_DAYS} days')"


def _parallel(fn, items, workers=6):
    """Возвращает [(item, результат, ошибка)] — исключения не пробрасываются."""
    items = list(items)
    if not items:
        return []

    def _safe(item):
        try:
            return item, fn(item), None
        except Exception as exc:  # noqa: BLE001
            return item, None, f"{type(exc).__name__}: {exc}"

    with concurrent.futures.ThreadPoolExecutor(max_workers=min(workers, len(items))) as ex:
        return list(ex.map(_safe, items))


def _note_error(msg: str) -> None:
    st.session_state.setdefault("api_errors", []).append(msg)


# ---------- про-матрица матчапов и мета ----------

def _download_pro_data(client: ApiClient) -> dict:
    """Загружает мету. Полную матрицу не запрашиваем: Explorer часто отклоняет
    огромный результат, а отдельные запросы по выбранным врагам надёжнее.
    """
    q_meta = f"""
SELECT pm.hero_id AS hero_id, COUNT(*) AS picks,
       SUM(CASE WHEN (pm.player_slot < 128) = m.radiant_win THEN 1 ELSE 0 END) AS wins
FROM player_matches pm
JOIN matches m ON m.match_id = pm.match_id
WHERE m.leagueid > 0 AND m.start_time > {_since()}
GROUP BY pm.hero_id"""
    rows = _run_sql(client, q_meta)
    meta = [[_i(r["hero_id"]), _i(r["picks"]), _i(r["wins"])] for r in rows]
    return {
        "matrix": [],
        "meta": meta,
        "matches": sum(m[1] for m in meta) // 10,
        "days": PRO_DAYS,
        "partial": "matchups-fetched-per-enemy",
    }


def _refresh_in_background(client: ApiClient) -> None:
    reg = _inflight()
    with reg["lock"]:
        if "pro" in reg["keys"]:
            return
        reg["keys"].add("pro")

    def _job():
        try:
            data = _download_pro_data(client)
            if data["matrix"] or data["meta"]:
                disk_write("pro_data_v4", data)
        except Exception:  # noqa: BLE001
            pass
        finally:
            with reg["lock"]:
                reg["keys"].discard("pro")

    threading.Thread(target=_job, daemon=True).start()


def get_pro_data(client: ApiClient):
    """Возвращает один свежий набор на анализ; принудительно обновляет по кнопке."""
    if st.session_state.get("_force_refresh_data"):
        if st.session_state.get("_request_pro_bundle") is not None:
            return st.session_state["_request_pro_bundle"], {"age": 0.0, "stale": False, "error": None}
        cached, age = disk_read("pro_data_v4")
        try:
            data = _download_pro_data(client)
            if data["matrix"] or data["meta"]:
                disk_write("pro_data_v4", data)
                st.session_state["_request_pro_bundle"] = data
                st.session_state.pop("_matrix_cache", None)
                return data, {"age": 0.0, "stale": False, "error": None}
        except Exception as exc:  # noqa: BLE001
            if cached is None:
                return None, {"age": None, "stale": False, "error": f"{type(exc).__name__}: {exc}"}
            return cached, {"age": age, "stale": True, "error": f"обновление не удалось: {type(exc).__name__}: {exc}"}
    cached, age = disk_read("pro_data_v4")
    if cached is not None and age < MATRIX_TTL:
        return cached, {"age": age, "stale": False, "error": None}
    if cached is not None:
        _refresh_in_background(client)
        return cached, {"age": age, "stale": True, "error": None}
    try:
        data = _download_pro_data(client)
    except Exception as exc:  # noqa: BLE001
        return None, {"age": None, "stale": False, "error": f"{type(exc).__name__}: {exc}"}
    if data["matrix"] or data["meta"]:
        disk_write("pro_data_v4", data)
    return data, {"age": 0.0, "stale": False, "error": None}


@st.cache_resource(show_spinner=False)
def _warm_once() -> bool:
    """Прогрев при старте сервера: к первому анализу данные уже на диске."""
    client = get_client()
    _hero_cache, _hero_age = disk_read("hero_icon_paths_v1")
    if _hero_cache is None or _hero_age >= CONSTANTS_TTL:
        threading.Thread(target=_warm_hero_icon_paths, daemon=True).start()
    _, age = disk_read("pro_data_v4")
    if age is None or age >= MATRIX_TTL:
        _refresh_in_background(client)
    return True


def _matrix_dict(bundle: dict) -> dict:
    """{enemy_id: {hero_id: (games, enemy_wins)}} — кэшируется на время жизни пакета."""
    # Новая выгрузка часто имеет тот же объём строк, поэтому размер пакета
    # нельзя использовать как ключ свежести — проверяем содержимое матрицы.
    stamp = hashlib.md5(json.dumps(bundle["matrix"], separators=(",", ":")).encode()).hexdigest()
    cached = st.session_state.get("_matrix_cache")
    if cached and cached[0] == stamp:
        return cached[1]
    out: dict = {}
    for enemy_id, hero_id, games, wins in bundle["matrix"]:
        if enemy_id == hero_id:
            continue
        out.setdefault(enemy_id, {})[hero_id] = (games, games - wins)
    st.session_state["_matrix_cache"] = (stamp, out)
    return out


def _enemy_sql(client: ApiClient, enemy_id: int) -> dict:
    """Про-матчапы выбранного врага; при сбое использует сохранённый снимок."""
    key = f"pro_enemy_v3_{int(enemy_id)}"
    cached, age = disk_read(key)
    if not st.session_state.get("_force_refresh_data") and cached is not None and age < MATRIX_TTL:
        return {int(k): tuple(v) for k, v in cached.items()}
    sql = f"""
SELECT c.hero_id AS hero_id, COUNT(*) AS games,
       SUM(CASE WHEN (c.player_slot < 128) = m.radiant_win THEN 1 ELSE 0 END) AS wins
FROM matches m
JOIN player_matches e ON e.match_id = m.match_id AND e.hero_id = {int(enemy_id)}
JOIN player_matches c ON c.match_id = m.match_id
 AND (c.player_slot < 128) <> (e.player_slot < 128)
WHERE m.leagueid > 0 AND m.start_time > {_since()}
GROUP BY c.hero_id"""
    try:
        out = {}
        for r in _run_sql(client, sql):
            games, wins = _i(r["games"]), _i(r["wins"])
            out[_i(r["hero_id"])] = (games, games - wins)
        if out:
            disk_write(key, {str(k): list(v) for k, v in out.items()})
            return out
        if cached is not None:
            return {int(k): tuple(v) for k, v in cached.items()}
        return out
    except Exception:
        if cached is not None:
            return {int(k): tuple(v) for k, v in cached.items()}
        raise

def _enemy_combined_matchups(enemy_id: int) -> dict:
    """За один SQL-запрос получает про- и high-MMR матчапы выбранного врага."""
    enemy_id = int(enemy_id)
    request_cache = st.session_state.setdefault("_request_enemy_combined", {})
    if enemy_id in request_cache:
        return request_cache[enemy_id]

    pro_key = f"pro_enemy_v3_{enemy_id}"
    ranked_key = f"ranked_hmm_v2_{enemy_id}"
    pro_cached, pro_age = disk_read(pro_key)
    ranked_cached, ranked_age = disk_read(ranked_key)
    force = st.session_state.get("_force_refresh_data")
    if (not force and pro_cached is not None and pro_age < MATRIX_TTL
            and ranked_cached is not None and ranked_age < RANKED_MATCHUP_TTL):
        result = {
            "pro": {int(hero): tuple(values) for hero, values in pro_cached.items()},
            "ranked": {int(hero): tuple(values) for hero, values in ranked_cached.items()},
        }
        request_cache[enemy_id] = result
        return result

    since_pro = _since()
    sql = f"""
SELECT c.hero_id AS hero_id,
       COUNT(*) FILTER (WHERE m.leagueid > 0 AND m.start_time > {since_pro}) AS pro_games,
       SUM(CASE WHEN (c.player_slot < 128) = m.radiant_win THEN 1 ELSE 0 END)
         FILTER (WHERE m.leagueid > 0 AND m.start_time > {since_pro}) AS pro_wins,
       COUNT(DISTINCT m.match_id) FILTER (
         WHERE m.start_time > extract(epoch from now() - interval '30 days')
           AND m.lobby_type = 7 AND m.avg_rank_tier >= 70) AS ranked_games,
       SUM(CASE WHEN (c.player_slot < 128) = m.radiant_win THEN 1 ELSE 0 END)
         FILTER (WHERE m.start_time > extract(epoch from now() - interval '30 days')
           AND m.lobby_type = 7 AND m.avg_rank_tier >= 70) AS ranked_wins
FROM matches m
JOIN player_matches e ON e.match_id = m.match_id AND e.hero_id = {enemy_id}
JOIN player_matches c ON c.match_id = m.match_id
 AND (c.player_slot < 128) <> (e.player_slot < 128)
WHERE (m.leagueid > 0 AND m.start_time > {since_pro})
   OR (m.start_time > extract(epoch from now() - interval '30 days')
       AND m.lobby_type = 7 AND m.avg_rank_tier >= 70)
GROUP BY c.hero_id"""
    rows = _run_sql(get_client(), sql)
    pro, ranked = {}, {}
    for row in rows:
        hero = _i(row.get("hero_id"))
        pro_games, pro_wins = _i(row.get("pro_games")), _i(row.get("pro_wins"))
        ranked_games, ranked_wins = _i(row.get("ranked_games")), _i(row.get("ranked_wins"))
        if not hero:
            continue
        if pro_games:
            pro[hero] = (pro_games, pro_games - pro_wins)
        if ranked_games:
            ranked[hero] = (ranked_games, ranked_games - ranked_wins)

    disk_write(pro_key, {str(hero): list(values) for hero, values in pro.items()})
    disk_write(ranked_key, {str(hero): list(values) for hero, values in ranked.items()})
    result = {"pro": pro, "ranked": ranked}
    request_cache[enemy_id] = result
    return result


def _enemy_public(client: ApiClient, enemy_id: int) -> dict:
    """All-time OpenDota matchup snapshot, retained as offline fallback."""
    key = f"hero_matchups_v3_{int(enemy_id)}"
    cached, age = disk_read(key)
    if cached is not None and age < MATRIX_TTL:
        return {int(k): tuple(v) for k, v in cached.items()}
    try:
        rows = client.get_json(f"{OPENDOTA_HEROES_URL}/{int(enemy_id)}/matchups")
        out = {_i(r["hero_id"]): (_i(r["games_played"]), _i(r["wins"])) for r in rows}
        if out:
            disk_write(key, {str(k): list(v) for k, v in out.items()})
            return out
        # A transient empty response must not erase a previously useful snapshot.
        if cached is not None:
            return {int(k): tuple(v) for k, v in cached.items()}
        return out
    except Exception:
        # Keep last successful all-time matchup data indefinitely when upstream is down.
        if cached is not None:
            return {int(k): tuple(v) for k, v in cached.items()}
        raise

def fetch_matchups(enemy_ids) -> dict:
    """{enemy_id: {hero_id: (games, enemy_wins)}} — про-матчи за PRO_DAYS дней."""
    ids = tuple(sorted({int(i) for i in enemy_ids}))
    if not ids:
        return {}
    request_cache = st.session_state.get("_request_matchups")
    if request_cache and request_cache[0] == ids:
        return request_cache[1]
    status = st.session_state.setdefault("data_status", {})
    client = get_client()

    bundle, info = get_pro_data(client)
    status["pro"] = info
    if bundle is not None and bundle["matrix"]:
        status["matchup_source"] = "pro-matrix"
        status["matches"] = bundle.get("matches")
        matrix = _matrix_dict(bundle)
        result = {e: matrix.get(e, {}) for e in ids}
        st.session_state["_request_matchups"] = (ids, result)
        return result

    if info.get("error"):
        _note_error(f"explorer/pro-matrix -> {info['error']}")
        status["matrix_error"] = info["error"]

    # Один запрос на врага получает обе выборки; при сбое сохраняем старый fallback.
    out, failed = {}, []
    for enemy_id, data, err in _parallel(_enemy_combined_matchups, ids):
        if err:
            failed.append(enemy_id)
            _note_error(f"explorer/combined-matchups/{enemy_id} -> {err}")
        else:
            out[enemy_id] = data["pro"]
    if out:
        status["matchup_source"] = "pro-per-enemy"
    # запасной путь 2: публичные матчапы героя (вне периода — помечаем)
    if failed:
        for enemy_id, data, err in _parallel(lambda e: _enemy_sql(client, e), failed):
            if err:
                _note_error(f"explorer/pro-enemy/{enemy_id} -> {err}")
            else:
                out[enemy_id] = data
                status["matchup_source"] = "pro-per-enemy"
        failed = [enemy_id for enemy_id in failed if enemy_id not in out]
    if failed:
        for enemy_id, data, err in _parallel(lambda e: _enemy_public(client, e), failed):
            if err:
                _note_error(f"heroes/{enemy_id}/matchups -> {err}")
            else:
                out[enemy_id] = data
                status["matchup_source"] = "public-fallback"
    st.session_state["_request_matchups"] = (ids, out)
    return out


def fetch_public_matchups(enemy_ids) -> dict:
    """All-time OpenDota matchups used as a weak fallback for sparse recent data."""
    ids = tuple(sorted({int(i) for i in enemy_ids if int(i) in HEROES}))
    if not ids:
        return {}
    cached_request = st.session_state.get("_request_public_matchups")
    if cached_request and cached_request[0] == ids:
        return cached_request[1]
    client = get_client()
    out = {}
    # Keep stale all-time snapshots as a disk-backed reserve if refresh fails.
    stale_before = set()
    for enemy_id in ids:
        _snapshot, _age = disk_read(f"hero_matchups_v3_{enemy_id}")
        if _snapshot and _age is not None and _age >= MATRIX_TTL:
            stale_before.add(enemy_id)
    for enemy_id, data, err in _parallel(lambda e: _enemy_public(client, e), ids, workers=5):
        if err:
            _note_error(f"heroes/{enemy_id}/matchups -> {err}")
        else:
            out[enemy_id] = data
    stale_used = []
    for enemy_id in stale_before:
        _snapshot, _age = disk_read(f"hero_matchups_v3_{enemy_id}")
        if out.get(enemy_id) and _age is not None and _age >= MATRIX_TTL:
            stale_used.append(enemy_id)
    data_status = st.session_state.setdefault("data_status", {})
    if stale_used:
        data_status["matchup_backup"] = f"резерв: сохранённые OpenDota матчапы для {len(stale_used)} враг(ов)"
    elif not any(out.values()):
        data_status["matchup_backup"] = "нет матчап-статистики; рекомендации опираются на доступную мету и билды"
    st.session_state["_request_public_matchups"] = (ids, out)
    return out


def _ranked_enemy_matchups(enemy_id: int) -> dict:
    key = f"ranked_hmm_v2_{int(enemy_id)}"
    cached, age = disk_read(key)
    force = st.session_state.get("_force_refresh_data")
    if not force and cached is not None and age < RANKED_MATCHUP_TTL:
        return {int(hero): tuple(values) for hero, values in cached.items()}
    sql = f"""
SELECT c.hero_id AS hero_id, COUNT(DISTINCT m.match_id) AS games,
       SUM(CASE WHEN (c.player_slot < 128) = m.radiant_win THEN 1 ELSE 0 END) AS wins
FROM matches m
JOIN player_matches e ON e.match_id = m.match_id AND e.hero_id = {int(enemy_id)}
JOIN player_matches c ON c.match_id = m.match_id
 AND (c.player_slot < 128) <> (e.player_slot < 128)
WHERE m.start_time > extract(epoch from now() - interval '30 days')
  AND m.lobby_type = 7 AND m.avg_rank_tier >= 70
GROUP BY c.hero_id"""
    try:
        out = {}
        for row in _run_sql(get_client(), sql):
            hero_id, games, wins = _i(row.get("hero_id")), _i(row.get("games")), _i(row.get("wins"))
            if hero_id and games:
                out[hero_id] = (games, games - wins)
        disk_write(key, {str(hero): list(values) for hero, values in out.items()})
        return out
    except Exception:
        if cached is not None:
            return {int(hero): tuple(values) for hero, values in cached.items()}
        raise


def fetch_ranked_matchups(enemy_ids) -> dict:
    """Ранговые матчапы Divine/Immortal; результаты кэшируются отдельно по врагу."""
    ids = tuple(sorted({int(i) for i in enemy_ids if int(i) in HEROES}))
    if not ids:
        return {}
    request_cache = st.session_state.get("_request_ranked_matchups")
    if request_cache and request_cache[0] == ids:
        return request_cache[1]
    out, errors = {}, []
    combined, failed = {}, []
    for enemy_id, data, err in _parallel(_enemy_combined_matchups, ids, workers=5):
        if err:
            failed.append(enemy_id)
        else:
            combined[enemy_id] = data["ranked"]
    for enemy_id, data, err in _parallel(_ranked_enemy_matchups, failed, workers=5):
        if err:
            errors.append((enemy_id, err))
        else:
            combined[enemy_id] = data
    out = combined
    st.session_state.setdefault("data_status", {})["ranked_matchups"] = {
        "error": "; ".join(f"{enemy}: {err}" for enemy, err in errors) if errors else None
    }
    if errors and not out:
        _note_error(f"explorer/ranked-matchups -> {errors[0][1]}")
    st.session_state["_request_ranked_matchups"] = (ids, out)
    return out



def fetch_enemy_matchups(enemy_id: int) -> dict:
    return fetch_matchups([enemy_id]).get(int(enemy_id), {})


def prefetch_matchups(enemy_ids) -> None:
    fetch_matchups(enemy_ids)


def fetch_meta_stats() -> dict:
    """Про-мета за период; при недоступности API использует последний снимок."""
    client = get_client()
    bundle, _info = get_pro_data(client)
    result = {}
    if bundle is not None and bundle["meta"]:
        for hero_id, picks, wins in bundle["meta"]:
            result[hero_id] = {
                "picks": picks,
                "winrate": (wins + META_SHRINK_K * 0.5) / (picks + META_SHRINK_K) * 100 if picks else None,
            }
        return result

    cached, age = disk_read("herostats_v3")
    if st.session_state.get("_force_refresh_data") or cached is None or age >= MATRIX_TTL:
        try:
            fresh = client.get_json(OPENDOTA_HEROSTATS_URL, timeout=20)
            if fresh:
                cached = fresh
                disk_write("herostats_v3", cached)
        except Exception as exc:  # noqa: BLE001
            if cached is None:
                _note_error(f"heroStats -> {type(exc).__name__}: {exc}")
    for h in cached or []:
        picks, wins = _i(h.get("pro_pick")), _i(h.get("pro_win"))
        result[_i(h.get("id"))] = {
            "picks": picks,
            "winrate": (wins + META_SHRINK_K * 0.5) / (picks + META_SHRINK_K) * 100 if picks else None,
        }
    return result

# ---------- Dotabuff (дополнительный источник) ----------

def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower().replace("'", "")).strip("-")


def parse_dotabuff_counters(html: str) -> dict:
    """{hero_id: (matches, winrate%)} — винрейт героя из таблицы против страницы-врага."""
    name_to_id = {_norm(n): i for i, n in HEROES.items()}
    out = {}
    for row in re.findall(r"<tr[^>]*>(.*?)</tr>", html, flags=re.S):
        values = re.findall(r'data-value="([^"]+)"', row)
        if len(values) < 4:
            continue
        hero_id = name_to_id.get(_norm(values[0]))
        if hero_id is None:
            continue
        try:
            winrate, matches = float(values[2]), _i(values[3])
        except ValueError:
            continue
        if matches > 0 and 0 < winrate < 100:
            out[hero_id] = (matches, winrate)
    return out


def _dotabuff_one(client: ApiClient, enemy_id: int) -> dict:
    key = f"dotabuff_v3_{enemy_id}_{DOTABUFF_DATE}"
    cached, age = disk_read(key)
    if not st.session_state.get("_force_refresh_data") and cached is not None and age < DOTABUFF_TTL:
        return {int(k): tuple(v) for k, v in cached.items()}
    url = f"{DOTABUFF_BASE}/heroes/{_slug(HEROES[enemy_id])}/counters?date={DOTABUFF_DATE}"
    html = client.get_text(url, headers={"User-Agent": BROWSER_UA, "Accept-Language": "en-US,en;q=0.9"})
    out = parse_dotabuff_counters(html)
    if not out:
        raise ApiError("страница Dotabuff получена, но таблицу разобрать не удалось")
    disk_write(key, {str(k): list(v) for k, v in out.items()})
    return out


def fetch_dotabuff(enemy_ids):
    """({enemy_id: {hero_id: (matches, wr)}}, текст статуса). Не критично для работы."""
    ids = [e for e in enemy_ids if e in HEROES]
    client = get_client()
    _, block_age = disk_read("dotabuff_blocked_v3")
    if block_age is not None and block_age < 6 * 3600:
        return {}, "сайт закрыт защитой от ботов (повторная проверка раз в 6 часов)"
    out, errors = {}, []
    for enemy_id, data, err in _parallel(lambda e: _dotabuff_one(client, e), ids, workers=3):
        if err:
            errors.append(err)
        else:
            out[enemy_id] = data
    if not out and any("403" in e for e in errors):
        disk_write("dotabuff_blocked_v3", {"blocked": True})
    if out and not errors:
        return out, "ok"
    if out:
        return out, f"частично ({len(out)} из {len(ids)})"
    return {}, errors[0] if errors else "нет данных"


# ---------- оценка героев ----------

def get_candidate_score(candidate_id, enemy_ids, meta, matchups_by_enemy=None, dotabuff=None, ranked_by_enemy=None, public_by_enemy=None):
    """Считает matchup по каждому врагу с байесовским сглаживанием; мета — слабый prior."""
    matchups_by_enemy = matchups_by_enemy if matchups_by_enemy is not None else fetch_matchups(enemy_ids)
    dotabuff = dotabuff or {}
    ranked_by_enemy = ranked_by_enemy or {}
    public_by_enemy = public_by_enemy or {}
    meta_info = meta.get(candidate_id, {})
    meta_score = meta_info.get("winrate")
    meta_picks = meta_info.get("picks", 0)

    # Не позволяем высокому WR по небольшой/смешанной выборке затмить matchup.
    meta_trust = min(meta_picks / (meta_picks + 40), 0.75) if meta_picks else 0.0
    meta_prior = 50 + ((meta_score if meta_score is not None else 50) - 50) * meta_trust
    per_enemy, total_games, covered_enemies, db_used = [], 0, 0, False
    for enemy_id in enemy_ids:
        games, enemy_wins = matchups_by_enemy.get(enemy_id, {}).get(candidate_id, (0, 0))
        ranked_games, ranked_enemy_wins = ranked_by_enemy.get(enemy_id, {}).get(candidate_id, (0, 0))
        public_games, public_enemy_wins = public_by_enemy.get(enemy_id, {}).get(candidate_id, (0, 0))
        sources = []
        if ranked_games > 0:
            ranked_wr = (ranked_games - ranked_enemy_wins + 20 * 0.5) / (ranked_games + 20) * 100
            sources.append((ranked_wr, ranked_games / (ranked_games + 20), 0.8))
            total_games += ranked_games
        if games > 0:
            pro_wr = (games - enemy_wins + SHRINK_K * 0.5) / (games + SHRINK_K) * 100
            sources.append((pro_wr, games / (games + SHRINK_K), 0.2))
            total_games += games
        if public_games > 0:
            # All-time all-rank data fills holes, but its low weight prevents it overruling
            # recent Divine/Immortal or professional matchup evidence.
            public_wr = (public_games - public_enemy_wins + 80 * 0.5) / (public_games + 80) * 100
            sources.append((public_wr, public_games / (public_games + 80), 0.08))
            total_games += public_games
        if ranked_games >= 10 or games >= MIN_GAMES_THRESHOLD or public_games >= 20:
            covered_enemies += 1
        db = dotabuff.get(enemy_id, {}).get(candidate_id)
        if db:
            matches, wr = db
            db_wr = (wr / 100 * matches + SHRINK_K * 0.5) / (matches + SHRINK_K) * 100
            sources.append((db_wr, matches / (matches + SHRINK_K), 0.4))
            db_used = True
        if sources:
            source_weight = sum(base_weight for _value, _confidence, base_weight in sources)
            observed_weight = sum(confidence * base_weight for _value, confidence, base_weight in sources)
            observed = sum(value * confidence * base_weight for value, confidence, base_weight in sources) / observed_weight
            confidence = min(1.0, observed_weight / source_weight)
            per_enemy.append(50 + (observed - 50) * confidence)
        else:
            per_enemy.append(50.0)

    matchup_score = sum(per_enemy) / len(per_enemy) if per_enemy else 50.0
    # Мета с небольшим весом помогает при пустых matchup-данных, но сама по
    # себе не должна проталкивать героя на первое место.
    score = matchup_score * 0.9 + meta_prior * 0.1
    has_matchup = total_games > 0 or db_used
    if not has_matchup and meta_score is None:
        return None
    return {
        "score": score,
        "matchup_score": matchup_score if has_matchup else None,
        "has_matchup": has_matchup,
        "matchup_games": total_games,
        "matched_enemies": covered_enemies,
        "meta_score": meta_score,
        "meta_picks": meta_picks,
        "dotabuff_used": db_used,
    }


def analyze_pick(enemy_ids, my_role, limit=5):
    """Сортировка: сначала по пику врага (округлено до 1%), затем по текущей мете."""
    enemy_ids = list(enemy_ids)
    meta = fetch_meta_stats()
    matchups = fetch_matchups(enemy_ids)
    ranked_matchups = fetch_ranked_matchups(enemy_ids)
    public_matchups = fetch_public_matchups(enemy_ids)
    dotabuff, db_status = fetch_dotabuff(enemy_ids)
    st.session_state["_db_data"] = dotabuff
    st.session_state.setdefault("data_status", {})["dotabuff"] = db_status
    scores = []
    for hero_id, hero_name in HEROES.items():
        if hero_id in enemy_ids or not hero_has_role(hero_id, my_role):
            continue
        info = get_candidate_score(hero_id, enemy_ids, meta, matchups, dotabuff, ranked_matchups, public_matchups)
        if info is not None:
            scores.append({"id": hero_id, "name": hero_name, **info})
    scores.sort(key=lambda x: (x["has_matchup"], x["score"], x["matched_enemies"],
                              x["matchup_games"], x["meta_picks"]), reverse=True)
    return scores[:limit]


# ---------- предметы под конкретного героя (про-покупки) ----------

IGNORED_ITEMS = {
    "tango", "flask", "clarity", "faerie_fire", "enchanted_mango", "tpscroll", "ward_observer",
    "ward_sentry", "ward_dispenser", "smoke_of_deceit", "dust", "cheese", "aegis", "refresher_shard",
    "tome_of_knowledge", "bottle", "blood_grenade", "gem", "river_painter",
}
KEEP_CHEAP_ITEMS = {"magic_wand", "tranquil_boots", "urn_of_shadows", "vanguard", "wind_lace",
                    "arcane_boots", "boots", "bracer", "wraith_band", "null_talisman", "orb_of_venom"}

ITEM_KEY_TO_NAME = {
    "black_king_bar": "Black King Bar", "sphere": "Linken's Sphere", "blade_mail": "Blade Mail",
    "force_staff": "Force Staff", "ghost": "Ghost Scepter", "cyclone": "Eul's Scepter of Divinity",
    "pipe": "Pipe of Insight", "crimson_guard": "Crimson Guard", "heavens_halberd": "Heaven's Halberd",
    "manta": "Manta Style", "diffusal_blade": "Diffusal Blade", "skadi": "Eye of Skadi",
    "assault": "Assault Cuirass", "abyssal_blade": "Abyssal Blade", "monkey_king_bar": "Monkey King Bar",
    "sheepstick": "Scythe of Vyse", "orchid": "Orchid Malevolence", "bloodthorn": "Bloodthorn",
    "nullifier": "Nullifier", "aeon_disk": "Aeon Disk", "solar_crest": "Solar Crest",
    "glimmer_cape": "Glimmer Cape", "spirit_vessel": "Spirit Vessel", "shivas_guard": "Shiva's Guard",
    "lotus_orb": "Lotus Orb", "satanic": "Satanic", "butterfly": "Butterfly", "heart": "Heart of Tarrasque",
    "blink": "Blink Dagger", "ultimate_scepter": "Aghanim's Scepter", "aghanims_shard": "Aghanim's Shard",
    "tranquil_boots": "Tranquil Boots", "power_treads": "Power Treads", "phase_boots": "Phase Boots",
    "arcane_boots": "Arcane Boots", "magic_wand": "Magic Wand", "travel_boots": "Boots of Travel",
    "travel_boots_2": "Boots of Travel 2", "radiance": "Radiance", "desolator": "Desolator",
    "mjollnir": "Mjollnir", "maelstrom": "Maelstrom", "battle_fury": "Battle Fury", "yasha": "Yasha",
    "sange_and_yasha": "Sange and Yasha", "kaya_and_sange": "Kaya and Sange", "yasha_and_kaya": "Yasha and Kaya",
    "silver_edge": "Silver Edge", "shadow_blade": "Shadow Blade", "daedalus": "Daedalus",
    "greater_crit": "Daedalus", "basher": "Skull Basher", "bfury": "Battle Fury", "mekansm": "Mekansm",
    "guardian_greaves": "Guardian Greaves", "aether_lens": "Aether Lens", "veil_of_discord": "Veil of Discord",
    "rod_of_atos": "Rod of Atos", "gungir": "Gleipnir", "wind_waker": "Wind Waker", "kaya": "Kaya",
    "refresher": "Refresher Orb", "octarine_core": "Octarine Core", "bloodstone": "Bloodstone",
    "revenants_brooch": "Revenant's Brooch", "witch_blade": "Witch Blade", "armlet": "Armlet of Mordiggian",
    "echo_sabre": "Echo Sabre", "harpoon": "Harpoon", "disperser": "Disperser", "meteor_hammer": "Meteor Hammer",
    "hurricane_pike": "Hurricane Pike", "ethereal_blade": "Ethereal Blade", "dagon_5": "Dagon 5",
    "shivas": "Shiva's Guard", "pavise": "Pavise", "vanguard": "Vanguard", "urn_of_shadows": "Urn of Shadows",
    "medallion_of_courage": "Medallion of Courage", "hand_of_midas": "Hand of Midas",
    "linkens_sphere": "Linken's Sphere", "moon_shard": "Moon Shard", "swift_blink": "Swift Blink",
    "overwhelming_blink": "Overwhelming Blink", "arcane_blink": "Arcane Blink", "khanda": "Khanda",
    "spirit_vessel": "Spirit Vessel", "boots": "Boots of Speed", "bracer": "Bracer",
}


def _item_name(key: str, catalog: dict) -> str:
    if key in ITEM_KEY_TO_NAME:
        return ITEM_KEY_TO_NAME[key]
    entry = catalog.get(key)
    if entry and entry[0]:
        return entry[0]
    return key.replace("_", " ").title()


def get_item_catalog(client: ApiClient) -> dict:
    """{key: [имя, цена, id, изображение]} из /constants/items; кэш на неделю."""
    cached, age = disk_read("items_catalog_v5")
    if cached is not None and age < CONSTANTS_TTL:
        st.session_state["_item_asset_paths"] = {
            key: values[3] for key, values in cached.items() if len(values) > 3 and values[3]
        }
        st.session_state["_item_name_to_asset_key"] = {
            values[0]: key for key, values in cached.items() if values and values[0]
        }
        return cached
    legacy_cached, _legacy_age = disk_read("items_catalog_v4")
    try:
        # Always try the current constants first: the old cache has names but no exact
        # Valve image paths, which made some newer and aliased item icons silently miss.
        raw = client.get_json(OPENDOTA_ITEMS_URL, timeout=30)
        catalog = {k: [v.get("dname") or "", _i(v.get("cost")), _i(v.get("id"), -1), v.get("img") or ""]
                   for k, v in raw.items() if isinstance(v, dict)}
        st.session_state["_item_asset_paths"] = {key: values[3] for key, values in catalog.items() if values[3]}
        st.session_state["_item_name_to_asset_key"] = {
            values[0]: key for key, values in catalog.items() if values[0]
        }
        disk_write("items_catalog_v5", catalog)
        return catalog
    except Exception as exc:  # noqa: BLE001
        _note_error(f"constants/items -> {type(exc).__name__}: {exc}")
        old_catalog = legacy_cached
        if old_catalog:
            st.session_state["_item_name_to_asset_key"] = {
                values[0]: key for key, values in old_catalog.items() if values and values[0]
            }
        return cached or old_catalog or {}


def _stage_for(avg_time: float) -> str:
    if avg_time < 60:
        return "start"
    if avg_time < 12 * 60:
        return "early"
    if avg_time < 28 * 60:
        return "core"
    return "late"


@st.cache_resource(show_spinner=False)
def _d2pt_request_gate():
    return {"lock": threading.Lock(), "last": 0.0}


def _d2pt_position(role: str) -> str:
    return {"carry": "pos 1", "mid": "pos 2", "offlaner": "pos 3",
            "support4": "pos 4", "support5": "pos 5"}.get(role, "pos 1")


def _download_d2pt_item_plan(client: ApiClient, hero_id: int, role: str, catalog: dict):
    """Позиционный билд 7000+ MMR из D2PT; отсутствие API не ломает OpenDota fallback."""
    pos = _d2pt_position(role)
    key = f"d2pt_item_plan_v1_{hero_id}_{pos.replace(' ', '')}"
    cached, age = disk_read(key)
    if cached is not None and age < D2PT_BUILDS_TTL:
        if cached:
            st.session_state.setdefault("data_status", {})["d2pt"] = "ok"
        return cached or None

    url = f"{D2PT_BASE}/api/hero/{int(hero_id)}/builds"
    gate = _d2pt_request_gate()
    with gate["lock"]:
        wait = max(0.0, 1.0 - (time.time() - gate["last"]))
        if wait:
            time.sleep(wait)
        try:
            payload = client.get_json(url, params={"position": pos}, headers=D2PT_HEADERS, timeout=20, retries=0)
        finally:
            gate["last"] = time.time()
    builds = payload if isinstance(payload, list) else payload.get("builds", []) if isinstance(payload, dict) else []
    if not builds:
        st.session_state.setdefault("data_status", {})["d2pt"] = "нет подходящего билда для этой позиции"
        disk_write(key, {})
        return None
    build = next((b for b in builds if isinstance(b, dict) and isinstance(b.get("build_data"), dict)), None)
    if not build:
        st.session_state.setdefault("data_status", {})["d2pt"] = "неожиданный формат ответа"
        disk_write(key, {})
        return None
    data = build["build_data"]
    id_to_name = {}
    for item_key, item_data in catalog.items():
        if len(item_data) > 2 and item_data[2] >= 0 and item_data[0]:
            id_to_name[item_data[2]] = item_data[0]

    raw_items = {}
    starting = []
    inventories = data.get("starting_items_new") or []
    if inventories and isinstance(inventories[0], (list, tuple)) and inventories[0]:
        starting = inventories[0][0] if isinstance(inventories[0][0], list) else []
    for item in data.get("starting_items") or []:
        if isinstance(item, dict):
            iid = _i(item.get("raw_item_id"), -1)
            if iid >= 0 and _i(item.get("count")):
                raw_items[iid] = item
    progression = {}
    for field in ("anchor_items", "anchor_items2", "items_mid_late"):
        for item in data.get(field) or []:
            if not isinstance(item, dict):
                continue
            iid = _i(item.get("raw_item_id"), -1)
            if iid < 0:
                continue
            if iid not in progression or _i(item.get("count")) > _i(progression[iid].get("count")):
                progression[iid] = item
    items = []
    seen = set()
    for iid in starting:
        iid = _i(iid, -1)
        name = id_to_name.get(iid)
        if name and name not in seen:
            seen.add(name)
            items.append({"key": str(iid), "name": name, "games": 0, "wr": 50.0,
                          "freq": 1.0, "minute": 0, "stage": "start"})
    for iid, item in raw_items.items():
        name = id_to_name.get(iid)
        if not name or name in seen:
            continue
        freq = float(item.get("pr") or 0)
        if freq > 1:
            freq /= 100
        if freq < 0.25:
            continue
        seen.add(name)
        items.append({"key": str(iid), "name": name, "games": _i(item.get("count")),
                      "wr": float(item.get("win_rate") or 50), "freq": freq,
                      "minute": 0, "stage": "start"})
    for iid, item in progression.items():
        name = id_to_name.get(iid)
        if not name or name in seen:
            continue
        freq = float(item.get("pr") or 0)
        if freq > 1:
            freq /= 100
        if freq < 0.18:
            continue
        minute = float(item.get("avg_minute") or 0)
        stage = "early" if minute < 15 else "core" if minute < 30 else "late"
        seen.add(name)
        items.append({"key": str(iid), "name": name, "games": _i(item.get("count")),
                      "wr": float(item.get("win_rate") or 50), "freq": freq,
                      "minute": round(minute), "stage": stage})
    if not items:
        st.session_state.setdefault("data_status", {})["d2pt"] = "у билда нет распознанных предметов"
        disk_write(key, {})
        return None
    games = max(_i(build.get("matches")), _i(build.get("match_count")),
                _i(data.get("matches")), max((i["games"] for i in items), default=0), MIN_PLAN_GAMES)
    plan = {"games": games, "items": items, "source": "d2pt", "position": pos,
            "sample": _i(build.get("matches") or build.get("match_count") or data.get("matches"))}
    disk_write(key, plan)
    st.session_state.setdefault("data_status", {})["d2pt"] = "ok"
    return plan


def _download_item_plan(client: ApiClient, hero_id: int, catalog: dict):
    key = f"item_plan_v3_{hero_id}"
    cached, age = disk_read(key)
    if not st.session_state.get("_force_refresh_data") and cached is not None and age < ITEMS_TTL:
        return cached or None
    sql = f"""
WITH hero_games AS (
  SELECT pm.match_id, pm.purchase_log,
         ((pm.player_slot < 128) = m.radiant_win) AS won
  FROM player_matches pm JOIN matches m ON m.match_id = pm.match_id
  WHERE pm.hero_id = {int(hero_id)} AND m.leagueid > 0 AND m.start_time > {_since()}
    AND pm.purchase_log IS NOT NULL
)
SELECT t.item_key, COUNT(*) AS games, SUM(CASE WHEN t.won THEN 1 ELSE 0 END) AS wins,
       AVG(t.first_time) AS avg_time, (SELECT COUNT(*) FROM hero_games) AS total_games
FROM (
  SELECT g.match_id, g.won, p.item ->> 'key' AS item_key,
         MIN((p.item ->> 'time')::int) AS first_time
  FROM hero_games g
  CROSS JOIN LATERAL jsonb_array_elements(g.purchase_log::jsonb) AS p(item)
  GROUP BY g.match_id, g.won, p.item ->> 'key'
) t
GROUP BY t.item_key"""
    rows = _run_sql(client, sql)
    total = _i(rows[0]["total_games"]) if rows else 0
    items = []
    for r in rows:
        k, games = r["item_key"], _i(r["games"])
        if not k or k in IGNORED_ITEMS or k.startswith("recipe") or games < 3 or not total:
            continue
        cost = (catalog.get(k) or ["", 0])[1]
        if catalog:
            if cost < 1300 and k not in KEEP_CHEAP_ITEMS:
                continue
        elif k not in ITEM_KEY_TO_NAME:
            continue
        avg_time = float(r["avg_time"] or 0)
        items.append({
            "key": k, "name": _item_name(k, catalog), "games": games,
            "wr": _i(r["wins"]) / games * 100, "freq": games / total,
            "minute": max(0, round(avg_time / 60)), "stage": _stage_for(avg_time),
        })
    plan = {"games": total, "items": items}
    disk_write(key, plan if total else {})
    return plan if total else None


def get_item_plans(hero_ids, role):
    """Позиционные D2PT билды; OpenDota pro-покупки служат резервным источником."""
    client = get_client()
    catalog = get_item_catalog(client)
    plans = {}
    for hero_id in hero_ids:
        try:
            plan = _download_d2pt_item_plan(client, hero_id, role, catalog)
        except Exception as exc:  # noqa: BLE001
            st.session_state.setdefault("data_status", {})["d2pt"] = f"недоступен ({exc})"
            disk_write(f"d2pt_item_plan_v1_{hero_id}_{_d2pt_position(role).replace(' ', '')}", {})
            plan = None
        if plan is None:
            try:
                plan = _download_item_plan(client, hero_id, catalog)
                if plan:
                    plan["source"] = "opendota-pro"
            except Exception as exc:  # noqa: BLE001
                _note_error(f"explorer/item-plan/{hero_id} -> {type(exc).__name__}: {exc}")
        plans[hero_id] = plan
    return plans


def plan_to_build(plan):
    """Преобразует про-план в билд по стадиям или None, если игр мало."""
    if not plan or plan["games"] < MIN_PLAN_GAMES:
        return None
    limits = {"start": 4, "early": 3, "core": 4, "late": 3}
    build = {"start": [], "early": [], "core": [], "late": []}
    for stage, limit in limits.items():
        frequency_floor = 0.18 if plan.get("source") == "d2pt" else 0.25
        picked = [i for i in plan["items"] if i["stage"] == stage and i["freq"] >= frequency_floor]
        picked.sort(key=lambda i: i["freq"], reverse=True)
        for i in picked[:limit]:
            when = "в стартовом закупе" if stage == "start" else f"обычно около {i['minute']} мин"
            build[stage].append((
                i["name"],
                f"{i['freq'] * 100:.0f}% про-игр героя за {PRO_DAYS} дн., "
                f"WR с предметом {i['wr']:.0f}% ({i['games']} игр), {when}",
            ))
    return build if any(build.values()) else None


# ---------- проверка ID героев по API ----------

def check_hero_ids():
    """Сверяет имена из HEROES с OpenDota /heroes. Возвращает список расхождений."""
    client = get_client()
    try:
        cached, age = disk_read("heroes_v3")
        if cached is None or age >= CONSTANTS_TTL:
            cached = client.get_json(OPENDOTA_HEROES_URL, timeout=20)
            disk_write("heroes_v3", cached)
    except Exception:  # noqa: BLE001
        return []
    api = {h["id"]: h.get("localized_name", "") for h in cached}
    return [(i, n, api.get(i)) for i, n in HEROES.items()
            if api.get(i) is not None and _norm(api[i]) != _norm(n)]


# ===================================================================
# 5. СИНЕРГИЯ СОЮЗНИКОВ
# ===================================================================

SYNERGY_COMBOS = {
    96: [(33, "Magnus затягивает врагов в кучу — идеально под Black Hole Enigma"),
         (16, "RP держит толпу — Sand King добивает Epicenter'ом")],
    33: [(96, "Black Hole ловит толпу — Magnus добивает Empower'ом группу"),
         (104, "Толпа под Black Hole — идеальная цель для мин Techies")],
    29: [(96, "Ravage массово оглушает — RP Магнуса продлевает контроль"),
         (7, "Ravage + Echo Slam — комбинация, сносящая группу за секунды")],
    7: [(29, "Толпа после Ravage получает полный урон от Echo Slam"),
        (16, "Скученная группа умножает урон Epicenter")],
    16: [(96, "Epicenter держит группу — RP продлевает контроль дальше")],
    26: [(74, "Hex снимает опасную цель — Invoker добивает комбо-прокастом"),
         (11, "Finger of Death добивает цель после Requiem of Souls")],
    27: [(11, "Shackles удерживает керри на месте под Requiem Shadow Fiend")],
    55: [(19, "Vacuum стягивает врагов — Avalanche/Toss Tiny наносит АОЕ-урон"),
         (33, "Vacuum усиливает эффект скучивания перед Black Hole")],
    19: [(55, "Собранная Vacuum группа фиксируется через Avalanche + Toss")],
    90: [(1, "Восполнение маны ускоряет фарм Anti-Mage в ранней игре")],
    2: [(103, "Call фиксирует цель для безопасного старта Duel")],
    103: [(2, "Call фиксирует цель перед началом Дуэли")],
    50: [(59, "Shadow Wave одновременно лечит и наносит урон — усиливает агрессию Huskar")],
    110: [(1, "False Promise дает время Anti-Mage наносить урон под давлением")],
}


_fixed_synergy = {_fx(k): [(_fx(p), r) for p, r in pairs] for k, pairs in SYNERGY_COMBOS.items()}
SYNERGY_COMBOS.clear()
SYNERGY_COMBOS.update(_fixed_synergy)


def get_synergy_recommendations(ally_ids, my_role, exclude_ids):
    grouped = {}
    for ally_id in ally_ids:
        for partner_id, reason in SYNERGY_COMBOS.get(ally_id, []):
            if partner_id in exclude_ids or not hero_has_role(partner_id, my_role):
                continue
            grouped.setdefault(partner_id, {"reason": reason, "with": []})
            grouped[partner_id]["with"].append(HEROES.get(ally_id, str(ally_id)))
    return [{"hero": HEROES.get(pid, str(pid)), **d} for pid, d in grouped.items()]


# ===================================================================
# 6. ИНИЦИАЛИЗАЦИЯ И СЕССИЯ
# ===================================================================

for _key, _default in (("role", "carry"), ("enemy_ids", []), ("ally_ids", []), ("analyzed", False)):
    if _key not in st.session_state:
        st.session_state[_key] = _default
if st.session_state.role == "support":  # старое значение из прошлых сессий
    st.session_state.role = "support4"

# ===================================================================
# 7. ИНТЕРФЕЙС STREAMLIT
# ===================================================================

st.set_page_config(page_title="Dota Metrix", layout="wide")


HERO_IMAGE_SLUGS = {
    1: "antimage", 2: "axe", 3: "bane", 4: "bloodseeker", 5: "crystal_maiden",
    6: "drow_ranger", 7: "earthshaker", 8: "juggernaut", 9: "mirana", 10: "morphling",
    11: "nevermore", 12: "phantom_lancer", 13: "puck", 14: "pudge", 15: "razor",
    16: "sand_king", 17: "storm_spirit", 18: "sven", 19: "tiny", 20: "vengefulspirit",
    21: "windrunner", 22: "zuus", 23: "kunkka", 25: "lina", 26: "lion",
    27: "shadow_shaman", 28: "slardar", 29: "tidehunter", 30: "witch_doctor", 31: "lich",
    32: "riki", 33: "enigma", 34: "tinker", 35: "sniper", 36: "necrolyte",
    37: "warlock", 38: "beastmaster", 39: "queenofpain", 40: "venomancer", 41: "faceless_void",
    42: "skeleton_king", 43: "death_prophet", 44: "phantom_assassin", 45: "pugna",
    46: "templar_assassin", 47: "viper", 48: "luna", 49: "dragon_knight", 50: "dazzle",
    51: "rattletrap", 52: "leshrac", 53: "furion", 54: "life_stealer", 55: "dark_seer",
    56: "clinkz", 57: "omniknight", 58: "enchantress", 59: "huskar", 60: "night_stalker",
    61: "broodmother", 62: "bounty_hunter", 63: "weaver", 64: "jakiro", 65: "batrider",
    66: "chen", 67: "spectre", 68: "ancient_apparition", 69: "doom_bringer", 70: "ursa",
    71: "spirit_breaker", 72: "gyrocopter", 73: "alchemist", 74: "invoker", 75: "silencer",
    76: "obsidian_destroyer", 77: "lycan", 78: "brewmaster", 79: "shadow_demon", 80: "lone_druid",
    81: "chaos_knight", 82: "meepo", 83: "treant", 84: "ogre_magi", 85: "undying",
    86: "rubick", 87: "disruptor", 88: "nyx_assassin", 89: "naga_siren", 90: "keeper_of_the_light",
    91: "visage", 92: "slark", 93: "medusa", 94: "troll_warlord", 95: "centaur",
    96: "magnataur", 97: "shredder", 98: "bristleback", 99: "tusk", 100: "skywrath_mage",
    101: "abaddon", 102: "elder_titan", 103: "legion_commander", 104: "techies", 105: "ember_spirit",
    106: "earth_spirit", 107: "abyssal_underlord", 108: "terrorblade", 109: "phoenix", 110: "oracle",
    112: "winter_wyvern", 113: "arc_warden", 114: "monkey_king", 119: "dark_willow",
    120: "pangolier", 121: "grimstroke", 123: "hoodwink", 126: "void_spirit",
    128: "snapfire", 129: "mars", 135: "dawnbreaker", 136: "marci", 137: "primal_beast",
    138: "muerta", 145: "ringmaster", 146: "kez",
}
HERO_LEGACY_SLUGS = dict(HERO_IMAGE_SLUGS)
HERO_ICON_CDN = "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/icons"
HERO_LEGACY_CDN = "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/heroes"
STEAM_CDN = "https://cdn.cloudflare.steamstatic.com"
STEAM_CDN_ALT = "https://cdn.steamstatic.com"
ITEM_ICON_CDN = "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items"
ITEM_LEGACY_CDN = "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/items"
ITEM_IMAGE_SLUGS = {
    "Aghanim's Scepter": "ultimate_scepter", "Aghanim's Shard": "aghanims_shard",
    "Black King Bar": "black_king_bar", "Blink Dagger": "blink", "Boots of Travel": "travel_boots",
    "Boots of Travel 2": "boots_of_travel_2", "Eye of Skadi": "skadi", "Hand of Midas": "hand_of_midas",
    "Battle Fury": "bfury", "Linken's Sphere": "sphere", "Eul's Scepter of Divinity": "cyclone",
    "Boots of Speed": "boots", "Monkey King Bar": "monkey_king_bar", "Rod of Atos": "rod_of_atos",
    "Scythe of Vyse": "sheepstick",
    "Shiva's Guard": "shivas_guard", "Town Portal Scroll": "tpscroll", "Power Treads": "power_treads",
    "Black King Bar Recipe": "recipe_black_king_bar",
}
ITEM_NAME_TO_KEY = {}
for _item_key, _item_label in ITEM_KEY_TO_NAME.items():
    ITEM_NAME_TO_KEY.setdefault(_item_label, _item_key)
ITEM_NAME_TO_KEY.update(ITEM_IMAGE_SLUGS)
ITEM_LEGACY_SLUGS = {"Battle Fury": "bfury", "Eul's Scepter of Divinity": "cyclone",
                     "Linken's Sphere": "sphere", "Aghanim's Scepter": "ultimate_scepter",
                     "Aghanim's Shard": "aghanims_shard", "Town Portal Scroll": "tpscroll"}


def _asset_url(path: str, host: str = STEAM_CDN) -> str:
    if not path:
        return ""
    if path.startswith(("https://", "http://")):
        return path
    return host + (path if path.startswith("/") else "/" + path)


def _warm_hero_icon_paths() -> None:
    """Cache exact Valve icon paths from OpenDota's mirrored hero constants."""
    try:
        cached, age = disk_read("hero_icon_paths_v1")
        if cached is not None and age < CONSTANTS_TTL:
            return
        rows = ApiClient().get_json(OPENDOTA_HERO_CONSTANTS_URL, timeout=20)
        paths = {
            str(int(hero_id)): info["icon"]
            for hero_id, info in rows.items()
            if str(hero_id).isdigit() and isinstance(info, dict) and info.get("icon")
        }
        if paths:
            disk_write("hero_icon_paths_v1", paths)
    except Exception:
        # The complete local slug map remains available while this refresh retries.
        return


def _hero_asset_path(hero_id: int) -> str:
    paths = st.session_state.get("_hero_icon_paths")
    if paths is None:
        cached, _age = disk_read("hero_icon_paths_v1")
        if cached is not None:
            paths = cached
            st.session_state["_hero_icon_paths"] = paths
    return (paths or {}).get(str(int(hero_id)), "")


def _image_error_attrs(fallback_url: str, label: str, css_class: str) -> str:
    safe_url = html.escape(fallback_url, quote=True)
    safe_label = html.escape(label, quote=True)
    initial = html.escape((label[:2] or "?").upper())
    return (f'data-fallback="{safe_url}" '
            f'onerror="if(!this.dataset.fallbackTried){{this.dataset.fallbackTried=1;this.src=this.dataset.fallback}}else{{this.onerror=null;this.outerHTML=\'<span class=&quot;{css_class}&quot; title=&quot;{safe_label}&quot;>{initial}</span>\'}}"')


def _hero_icon_url(hero_id: int) -> str:
    path = _hero_asset_path(hero_id)
    if path:
        return _asset_url(path)
    name = HEROES.get(hero_id, "")
    slug = HERO_IMAGE_SLUGS.get(hero_id) or re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    return f"{HERO_ICON_CDN}/{slug}.png"


def _hero_icon_fallback_url(hero_id: int) -> str:
    path = _hero_asset_path(hero_id)
    if path:
        return _asset_url(path, STEAM_CDN_ALT)
    name = HEROES.get(hero_id, "")
    slug = HERO_LEGACY_SLUGS.get(hero_id) or HERO_IMAGE_SLUGS.get(hero_id)
    if not slug:
        slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    return f"{HERO_LEGACY_CDN}/{slug}_icon.png"


def _item_icon_url(item_name: str) -> str:
    item_name_to_key = st.session_state.get("_item_name_to_asset_key", {})
    key = item_name_to_key.get(item_name)
    if not key:
        normalized = _norm(item_name)
        key = next((item_key for label, item_key in item_name_to_key.items()
                    if _norm(label) == normalized), None)
    slug = key or ITEM_IMAGE_SLUGS.get(item_name) or ITEM_NAME_TO_KEY.get(item_name)
    key = slug or re.sub(r"[^a-z0-9]+", "_", item_name.lower()).strip("_")
    image_path = st.session_state.get("_item_asset_paths", {}).get(key)
    if image_path:
        return _asset_url(image_path)
    slug = slug or re.sub(r"[^a-z0-9]+", "_", item_name.lower()).strip("_")
    return f"{ITEM_ICON_CDN}/{slug}.png"


def _item_icon_fallback_url(item_name: str) -> str:
    primary_url = _item_icon_url(item_name)
    if primary_url.startswith(STEAM_CDN):
        return STEAM_CDN_ALT + primary_url[len(STEAM_CDN):]
    slug = (ITEM_LEGACY_SLUGS.get(item_name) or ITEM_IMAGE_SLUGS.get(item_name)
            or ITEM_NAME_TO_KEY.get(item_name)
            or st.session_state.get("_item_name_to_asset_key", {}).get(item_name))
    if not slug:
        slug = re.sub(r"[^a-z0-9]+", "_", item_name.lower()).strip("_")
    return f"{ITEM_LEGACY_CDN}/{slug}_lg.png"


def _hero_image(hero_id: int, size: int = 38) -> str:
    label = HEROES.get(hero_id, "Hero")
    name = html.escape(label, quote=True)
    fallback_class = f"dm-icon-fallback dm-hero-icon-fallback dm-icon-size-{size}"
    fallback_attrs = _image_error_attrs(_hero_icon_fallback_url(hero_id), label, fallback_class)
    return (f'<img class="dm-hero-icon" src="{_hero_icon_url(hero_id)}" '
            f'{fallback_attrs} width="{size}" height="{size}" alt="{name}" loading="lazy">')


def _hero_pick_card(rank: int, pick: dict) -> str:
    name = html.escape(pick["name"])
    score = html.escape(f'{pick["score"]:.0f}%')
    role = html.escape(get_role_name(st.session_state.role))
    return (f'<div class="dm-pick-card">{_hero_image(pick["id"], 54)}'
            f'<div><strong>{rank}. {name}</strong><small>Контрпик · {role}</small></div>'
            f'<b class="dm-pick-score">{score}</b></div>')


def _hero_team_strip(hero_ids: list[int]) -> str:
    if not hero_ids:
        return ""
    units = "".join(
        f'<span class="dm-team-unit" title="{html.escape(HEROES[hero_id], quote=True)}">'
        f'{_hero_image(hero_id, 34)}<small>{html.escape(HEROES[hero_id])}</small></span>'
        for hero_id in hero_ids if hero_id in HEROES
    )
    return f'<div class="dm-team-strip">{units}</div>'


def _item_build_row(item: str, desc: str) -> str:
    safe_item, safe_desc = html.escape(item), html.escape(desc)
    fallback_attrs = _image_error_attrs(_item_icon_fallback_url(item), item, "dm-icon-fallback dm-item-row-icon-fallback")
    return (f'<div class="dm-item-row"><img src="{_item_icon_url(item)}" '
            f'{fallback_attrs} alt="{html.escape(item, quote=True)}" loading="lazy">'
            f'<span><strong>{safe_item}</strong><small title="{safe_desc}">{safe_desc}</small></span></div>')


def _item_stage_card(title: str, entries: list[tuple[str, str]]) -> str:
    safe_title = html.escape(title)
    cards = []
    for item, desc in entries:
        safe_item, safe_desc = html.escape(item), html.escape(desc, quote=True)
        fallback_attrs = _image_error_attrs(_item_icon_fallback_url(item), item, "dm-icon-fallback dm-item-tile-icon-fallback")
        cards.append(
            f'<article class="dm-item-tile"><img src="{_item_icon_url(item)}" '
            f'{fallback_attrs} alt="{html.escape(item, quote=True)}" loading="lazy">'
            f'<strong>{safe_item}</strong><small title="{safe_desc}">{safe_desc}</small></article>'
        )
    return (f'<section class="dm-item-stage"><h4>{safe_title}</h4>'
            f'<div class="dm-item-grid">{"".join(cards)}</div></section>')


def _matchup_rate_label(source: str, rate: float, games: int) -> str:
    if games < MATCHUP_WR_MIN_GAMES:
        return f"{source}: мало данных ({games} матч.)"
    return f"{source} {rate:.0f}% · {games} игр"

def _matchup_visual(candidate_id: int, enemy_ids: list[int], pro: dict, ranked: dict, dotabuff: dict, public: dict | None = None) -> str:
    public = public or {}
    cards = []
    for enemy_id in enemy_ids:
        games, enemy_wins = pro.get(enemy_id, {}).get(candidate_id, (0, 0))
        ranked_games, ranked_enemy_wins = ranked.get(enemy_id, {}).get(candidate_id, (0, 0))
        public_games, public_enemy_wins = public.get(enemy_id, {}).get(candidate_id, (0, 0))
        sources = []
        if ranked_games:
            value = (ranked_games - ranked_enemy_wins + 10) / (ranked_games + 20) * 100
            sources.append((value, ranked_games / (ranked_games + 20), 0.8))
        if games:
            value = (games - enemy_wins + SHRINK_K * 0.5) / (games + SHRINK_K) * 100
            sources.append((value, games / (games + SHRINK_K), 0.2))
        if public_games:
            value = (public_games - public_enemy_wins + 40) / (public_games + 80) * 100
            sources.append((value, public_games / (public_games + 80), 0.08))
        db = dotabuff.get(enemy_id, {}).get(candidate_id)
        if db:
            db_games, db_wr = db
            value = (db_wr / 100 * db_games + SHRINK_K * 0.5) / (db_games + SHRINK_K) * 100
            sources.append((value, db_games / (db_games + SHRINK_K), 0.4))
        if sources:
            weight = sum(base for _, _, base in sources)
            observed_weight = sum(confidence * base for _, confidence, base in sources)
            observed = sum(value * confidence * base for value, confidence, base in sources) / observed_weight
            rate = 50 + (observed - 50) * min(1.0, observed_weight / weight)
            sample = max(games, ranked_games, public_games, db[0] if db else 0)
            source_text = "вся история OpenDota" if public_games and public_games >= max(games, ranked_games, db[0] if db else 0) else "свежие выборки"
            if sample < MATCHUP_WR_MIN_GAMES:
                rate_text = "—"
                bar = '<i class="dm-match-low" style="width:50%"></i>'
                sample_text = f"мало данных · {sample} матч. · {source_text}"
            else:
                rate_text = f"{rate:.0f}%"
                bar = f'<i style="width:{rate:.1f}%"></i>'
                sample_text = f"{sample} игр · {source_text}"
        else:
            rate_text, bar, sample_text = "—", "", "нет данных"
        cards.append(
            f'<div class="dm-match-card"><div class="dm-match-head">{_hero_image(enemy_id, 30)}'
            f'<span>{html.escape(HEROES.get(enemy_id, "Враг"))}</span><b>{rate_text}</b></div>'
            f'<div class="dm-match-track">{bar}</div><small>{sample_text}</small></div>'
        )
    return '<div class="dm-match-grid">' + "".join(cards) + '</div>'


def _hero_text_row(hero_id: int, text: str) -> str:
    return f'<div class="dm-hero-text-row">{_hero_image(hero_id, 32)}<span>{html.escape(text)}</span></div>'


THEME_TOML = """[theme]
base = "dark"
primaryColor = "#c06c4f"
backgroundColor = "#111311"
secondaryBackgroundColor = "#191b18"
textColor = "#eef0f5"
font = "sans serif"
"""


def ensure_theme_config() -> None:
    """Создаёт .streamlit/config.toml, если его нет. Streamlit читает тему при
    запуске, поэтому она применится со следующего старта; до этого интерфейс
    красит CSS ниже, так что отдельный файл руками класть не нужно."""
    try:
        target = Path.cwd() / ".streamlit" / "config.toml"
        if not target.exists():
            target.parent.mkdir(exist_ok=True)
            target.write_text(THEME_TOML, encoding="utf-8")
    except OSError:
        pass


ensure_theme_config()
_warm_once()

APP_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');

:root{--dm-bg:#111311;--dm-card:#191b18;--dm-line:#30332d;--dm-text:#eef0e8;--dm-muted:#a3a59a;
--dm-green:#c06c4f;--dm-green-ink:#170d09;--dm-topo:rgba(204,185,144,.055)}

/* Шрифт: Manrope поддерживает кириллицу; иконки Streamlit не трогаем */
.stApp, .stApp p, .stApp li, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4,
.stApp button, .stApp input, .stApp textarea, .stApp [data-baseweb="select"] *:not(svg):not([data-testid="stIconMaterial"]){
  font-family:'Manrope','Segoe UI','Helvetica Neue',Arial,sans-serif;
}
.stApp{background:var(--dm-bg);color:var(--dm-text)}
.stApp p, .stApp li, .stApp label, .stApp span, .stApp div[data-testid="stMarkdownContainer"]{color:var(--dm-text)}
.stApp h1{font-weight:800;letter-spacing:.04em;color:#fff}
.stApp h2, .stApp h3, .stApp h4{font-weight:700;letter-spacing:-.01em;color:#fff}
.stApp [data-testid="stCaptionContainer"], .stApp small{color:var(--dm-muted)}

/* Кнопки: текст всегда контрастен фону */
.stApp [data-testid="stBaseButton-secondary"], .stApp button[kind="secondary"]{
  background:var(--dm-card);border:1px solid var(--dm-line);color:var(--dm-text);border-radius:6px;
  font-weight:600;transition:border-color .2s,transform .15s,background .2s}
.stApp [data-testid="stBaseButton-secondary"] p, .stApp button[kind="secondary"] p{color:var(--dm-text)}
.stApp [data-testid="stBaseButton-secondary"]:hover, .stApp button[kind="secondary"]:hover{
  border-color:var(--dm-green);background:#20242d;transform:translateY(-1px)}
.stApp [data-testid="stBaseButton-primary"], .stApp button[kind="primary"]{
  background:var(--dm-green);border:1px solid var(--dm-green);color:var(--dm-green-ink);border-radius:6px;
  font-weight:800;letter-spacing:.06em;transition:box-shadow .2s,transform .15s}
.stApp [data-testid="stBaseButton-primary"] p, .stApp button[kind="primary"] p{
  color:var(--dm-green-ink) !important;font-weight:800}
.stApp [data-testid="stBaseButton-primary"]:hover, .stApp button[kind="primary"]:hover{
  background:#d89473;border-color:#d89473;box-shadow:0 6px 28px rgba(192,108,79,.35);transform:translateY(-1px)}

/* Поля выбора */
.stApp [data-baseweb="select"] > div{background:var(--dm-card);border-color:var(--dm-line);color:var(--dm-text)}
.stApp [data-baseweb="select"] input{color:var(--dm-text)}
.stApp span[data-baseweb="tag"]{background:var(--dm-green);color:var(--dm-green-ink);font-weight:700;border-radius:4px}
.stApp span[data-baseweb="tag"] span{color:var(--dm-green-ink)}
.stApp [data-testid="stExpander"]{border:1px solid var(--dm-line);border-radius:6px;background:rgba(27,30,38,.7)}
.stApp [data-testid="stAlert"]{border-radius:6px}


/* Замена config.toml: тёмная тема для частей, которые Streamlit красит сам */
:root{color-scheme:dark}
html,body,[data-testid="stAppViewContainer"],[data-testid="stSidebar"]{background:var(--dm-bg)}
[data-baseweb="popover"],[data-baseweb="popover"] > div,[data-baseweb="menu"],ul[role="listbox"]{
  background:var(--dm-card) !important;color:var(--dm-text) !important;border:1px solid var(--dm-line);border-radius:6px}
li[role="option"],[data-baseweb="menu"] li{background:transparent !important;color:var(--dm-text) !important}
li[role="option"]:hover,li[role="option"][aria-selected="true"]{background:#262a32 !important}
.stApp [data-testid="stAlert"]{background:rgba(27,30,38,.92);border:1px solid var(--dm-line)}
.stApp [data-testid="stAlert"] *{color:var(--dm-text)}
.stApp pre,.stApp code{background:#0e1015 !important;color:#d6f5e0 !important}
.stApp [data-testid="stSpinner"] *{color:var(--dm-muted)}
.stApp hr{border-color:var(--dm-line)}
::-webkit-scrollbar{width:10px;height:10px}::-webkit-scrollbar-track{background:var(--dm-bg)}
::-webkit-scrollbar-thumb{background:#2a2f3a;border-radius:6px}

/* Dota-inspired spiral made from dim, slowly pulsing points */
.stApp::before{content:"";position:fixed;inset:0;z-index:0;pointer-events:none;
  background:radial-gradient(ellipse at 50% 46%,rgba(35,38,39,.28),transparent 67%),
  linear-gradient(145deg,#090a0b 0%,#0d0e0f 48%,#080909 100%)}
.stApp::after{content:"";position:fixed;inset:0;z-index:0;pointer-events:none;
  background:radial-gradient(620px circle at 100% 0%,rgba(221,43,49,.035),transparent 72%),
  radial-gradient(640px circle at 0% 100%,rgba(54,62,64,.07),transparent 74%),
  linear-gradient(180deg,rgba(0,0,0,.08),rgba(0,0,0,.34))}
[data-testid="stAppViewContainer"]{position:relative;z-index:1}
[data-testid="stHeader"]{background:transparent}
.dm-fx{position:fixed;inset:0;z-index:0;pointer-events:none;overflow:hidden}
.dm-spiral{position:absolute;inset:0;overflow:hidden;opacity:.50;
  mask-image:radial-gradient(ellipse at 50% 48%,#000 10%,rgba(0,0,0,.84) 70%,transparent 100%)}
.dm-spiral svg{display:block;width:100%;height:100%;animation:dm-spiral-turn 58s linear infinite}
.dm-spiral circle{fill:#d9dedc;opacity:.12;animation:dm-spiral-pulse 8s ease-in-out infinite;
  animation-delay:var(--delay);transform-box:fill-box;transform-origin:center}
.dm-spiral circle:nth-child(17n+2){fill:#e9983e;opacity:.22}
@keyframes dm-spiral-turn{to{transform:rotate(360deg)}}
@keyframes dm-spiral-pulse{0%,100%{opacity:.06;transform:scale(.78)}50%{opacity:.40;transform:scale(1.2)}}
@media (prefers-reduced-motion:reduce){.dm-spiral svg,.dm-spiral circle{animation:none !important}.dm-spiral circle{opacity:.17}}
.stApp [data-testid="stMultiSelect"] [role="group"]{border-color:#e9983e !important}
.stApp [data-testid="stMultiSelect"] [role="group"][data-focus-within="true"],
.stApp [data-testid="stMultiSelect"] [role="group"][data-hovered="true"]{
  border-color:#e9983e !important;box-shadow:0 0 0 1px rgba(233,152,62,.34) !important}
.matrix-brand{display:flex;align-items:center;gap:13px;margin:2px 0 0}
.matrix-brand-mark{display:grid;grid-template-columns:repeat(3,5px);gap:3px;padding:9px;border:1px solid rgba(192,108,79,.30);
  border-radius:9px;background:rgba(28,24,22,.52);box-shadow:0 0 24px rgba(192,108,79,.08)}
.matrix-brand-mark i{width:5px;height:5px;border-radius:50%;background:#d4d5d3;box-shadow:0 0 7px rgba(230,231,229,.3)}
.matrix-brand-mark i:nth-child(5){background:#d9363e;box-shadow:0 0 8px rgba(217,54,62,.6)}
.matrix-brand-title{font:800 25px/1.05 'Manrope','Segoe UI',sans-serif;letter-spacing:.13em;color:#f0f0ed;text-shadow:0 0 22px rgba(230,230,225,.10)}
.matrix-brand-sub{margin-top:6px;font:10px/1.2 'Consolas',monospace;letter-spacing:.22em;color:#a3a59a}

/* DotaProTracker-style hero portraits and compact item build rows */
.dm-hero-icon{display:block;flex:none;object-fit:cover;border-radius:6px;border:1px solid rgba(205,190,157,.23);
  background:#20221d;box-shadow:0 3px 12px rgba(0,0,0,.24)}
.dm-icon-fallback{box-sizing:border-box;display:inline-flex;flex:none;align-items:center;justify-content:center;
  width:38px;height:38px;border:1px solid rgba(205,190,157,.24);border-radius:6px;background:#25251f;
  color:#e0c5a4;font-size:12px;font-weight:700;letter-spacing:.04em}
.dm-hero-icon-fallback{width:38px;height:38px}
.dm-icon-size-30{width:30px;height:30px}.dm-icon-size-32{width:32px;height:32px}
.dm-icon-size-34{width:34px;height:34px}.dm-icon-size-54{width:54px;height:54px}
.dm-item-row-icon-fallback{width:38px;height:30px;border-radius:5px}
.dm-item-tile-icon-fallback{width:100%;height:58px;border:0;border-radius:5px;background:#11130f;color:#c8b89e}
.dm-team-strip{display:flex;flex-wrap:wrap;gap:8px;margin:8px 0 14px}
.dm-team-unit{display:flex;align-items:center;gap:6px;padding:4px 8px 4px 4px;border:1px solid rgba(205,190,157,.16);
  border-radius:7px;background:rgba(15,17,14,.68);backdrop-filter:blur(5px)}
.dm-team-unit small{font-size:12px;color:var(--dm-muted)!important}
.dm-pick-card{display:flex;align-items:center;gap:13px;margin:8px 0;padding:12px 14px;border:1px solid rgba(192,108,79,.34);
  border-radius:9px;background:linear-gradient(105deg,rgba(192,108,79,.11),rgba(17,19,17,.72) 62%);backdrop-filter:blur(6px)}
.dm-pick-card strong{display:block;font-size:17px;color:var(--dm-text)}
.dm-pick-card small,.dm-item-row small{display:block;margin-top:3px;font-size:11px;color:var(--dm-muted)}
.dm-pick-score{margin-left:auto;color:#d99875;font-size:18px;font-variant-numeric:tabular-nums}
.dm-item-row,.dm-hero-text-row{display:flex;align-items:center;gap:10px;margin:7px 0;padding:8px 10px;border:1px solid rgba(205,190,157,.15);
  border-radius:7px;background:rgba(19,21,18,.72)}
.dm-item-row img{width:38px;height:30px;flex:none;object-fit:cover;border-radius:5px;border:1px solid rgba(205,190,157,.18);background:#20221d}
.dm-item-row strong{font-size:13px;color:var(--dm-text)}
.dm-item-row small{max-width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.dm-hero-text-row span{font-size:13px}
.dm-match-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(156px,1fr));gap:8px;margin:10px 0 4px}
.dm-match-card{min-width:0;padding:9px 10px;border:1px solid rgba(205,190,157,.14);border-radius:7px;background:rgba(16,18,15,.72)}
.dm-match-head{display:flex;align-items:center;gap:7px;min-width:0}
.dm-match-head span{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:11px;color:var(--dm-text)}
.dm-match-head b{margin-left:auto;font-size:14px;font-variant-numeric:tabular-nums;color:#d99875}
.dm-match-track{position:relative;height:5px;margin:8px 0 4px;overflow:hidden;border-radius:99px;background:#2b2e28}
.dm-match-track:after{content:"";position:absolute;left:50%;top:0;bottom:0;width:1px;background:rgba(239,232,209,.45)}
.dm-match-track i{display:block;height:100%;border-radius:inherit;background:linear-gradient(90deg,#80624e,#cf8a68)}
.dm-match-track i.dm-match-low{background:#45463f;opacity:.7}
.dm-match-card>small{font-size:10px;color:var(--dm-muted)}
.dm-match-head .dm-hero-icon{width:30px;height:30px}
.dm-item-stage{margin:14px 0 18px}
.dm-item-stage h4{margin:0 0 8px;font-size:15px;color:var(--dm-text)}
.dm-item-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(132px,1fr));gap:8px}
.dm-item-tile{min-width:0;padding:9px;border:1px solid rgba(205,190,157,.15);border-radius:8px;background:rgba(19,21,18,.76)}
.dm-item-tile img{display:block;width:100%;height:58px;object-fit:contain;border-radius:5px;background:#11130f}
.dm-item-tile strong{display:block;margin-top:7px;font-size:12px;line-height:1.25;color:var(--dm-text)}
.dm-item-tile small{display:block;margin-top:4px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:10px;color:var(--dm-muted)}
@media(max-width:640px){.dm-team-unit small{display:none}.dm-pick-card{gap:9px;padding:9px}.dm-pick-card strong{font-size:14px}}
</style>
"""
SPIRAL_DOTS = []
_SPIRAL_RINGS = 16
_SPIRAL_STEP = 72
for _ring in range(_SPIRAL_RINGS + 1):
    _count = 1 if _ring == 0 else _ring * 7
    _base_radius = _ring * _SPIRAL_STEP
    for _dot in range(_count):
        _angle = (_dot / _count * math.tau if _count > 1 else 0) + _ring * 0.19
        _x = 800 + math.cos(_angle) * _base_radius
        _y = 450 + math.sin(_angle) * _base_radius
        _dot_radius = 1.1 + ((_dot + _ring) % 3) * 0.18
        _delay = -((_ring * 0.42 + _dot * 0.035) % 8)
        SPIRAL_DOTS.append(
            f'<circle cx="{_x:.1f}" cy="{_y:.1f}" r="{_dot_radius:.1f}" '
            f'style="--delay:{_delay:.2f}s"></circle>'
        )
SPIRAL_FIELD = (
    '<div class="dm-fx"><div class="dm-spiral" aria-hidden="true"><svg viewBox="0 0 1600 900" '
    'preserveAspectRatio="xMidYMid slice">' + "".join(SPIRAL_DOTS) + '</svg></div></div>'
)
st.markdown(APP_CSS + SPIRAL_FIELD, unsafe_allow_html=True)

st.markdown(
    '<div class="matrix-brand"><span class="matrix-brand-mark"><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i></span>'
    '<div><div class="matrix-brand-title">DOTA METRIX</div><div class="matrix-brand-sub">MATCHUP SEARCH · LIVE ANALYSIS</div></div></div>',
    unsafe_allow_html=True,
)
st.caption("Контрпики и предметы по про-матчам OpenDota. Рекомендации пересчитываются при смене позиции или вражеского пика.")

if "id_check" not in st.session_state:
    st.session_state.id_check = check_hero_ids()
if st.session_state.id_check:
    with st.expander("Внимание: имена героев не совпали с OpenDota"):
        st.caption("Таблица героев в коде расходится с API. Проверь id ниже.")
        for _hid, _mine, _api in st.session_state.id_check:
            st.write(f"id {_hid}: в коде «{_mine}», в OpenDota «{_api}»")

st.divider()

st.subheader("Шаг 1. Выбери свою позицию")
ROLE_BUTTONS = [
    ("Керри (поз. 1)", "carry"),
    ("Мидер (поз. 2)", "mid"),
    ("Офлейн (поз. 3)", "offlaner"),
    ("Саппорт (поз. 4)", "support4"),
    ("Хард-саппорт (поз. 5)", "support5"),
]
for col, (label, key) in zip(st.columns(len(ROLE_BUTTONS)), ROLE_BUTTONS):
    with col:
        is_active = st.session_state.role == key
        if st.button(label, use_container_width=True, type="primary" if is_active else "secondary", key=f"role_{key}"):
            st.session_state.role = key
            st.rerun()

st.caption(f"Выбрано: {get_role_name(st.session_state.role)}")

st.divider()

name_to_id = {name: hid for hid, name in HEROES.items()}

st.subheader("Шаг 2. Герои противника")
enemy_names_selected = st.multiselect(
    "Выбери до 5 героев вражеской команды:",
    options=sorted(HEROES.values()),
    default=[HEROES[i] for i in st.session_state.enemy_ids if i in HEROES],
    max_selections=5,
    key="enemy_multiselect",
)

st.subheader("Шаг 3 (необязательно). Герои твоей команды")
ally_names_selected = st.multiselect(
    "Выбери героев своей команды для поиска синергий:",
    options=[n for n in sorted(HEROES.values()) if n not in enemy_names_selected],
    default=[HEROES[i] for i in st.session_state.ally_ids if i in HEROES],
    max_selections=4,
    key="ally_multiselect",
)

# Streamlit перезапускает скрипт после изменения виджетов, поэтому сохраняем
# актуальный пик сразу. Кнопка ниже нужна только для принудительного обновления
# источников при неизменном составе.
selected_enemy_ids = [name_to_id[n] for n in enemy_names_selected]
selected_ally_ids = [name_to_id[n] for n in ally_names_selected if n not in enemy_names_selected]
if selected_enemy_ids:
    st.markdown(_hero_team_strip(selected_enemy_ids), unsafe_allow_html=True)
if selected_ally_ids:
    st.markdown(_hero_team_strip(selected_ally_ids), unsafe_allow_html=True)
selection_signature = (st.session_state.role, tuple(sorted(selected_enemy_ids)))
if selection_signature != st.session_state.get("_selection_signature"):
    st.session_state["_selection_signature"] = selection_signature
    st.session_state.enemy_ids = selected_enemy_ids
    st.session_state.ally_ids = selected_ally_ids
    st.session_state.analyzed = bool(selected_enemy_ids)
    # Изменение пика требует нового расчёта, но не принудительной загрузки
    # одних и тех же источников: свежие данные берутся из дискового кэша.
    st.session_state["_force_refresh_data"] = False
    st.session_state.pop("_request_matchups", None)
    st.session_state.pop("_request_ranked_matchups", None)
else:
    # Союзники влияют на синергию, поэтому их текущий выбор тоже применяем
    # сразу, но без ненужного повторного запроса статистики матчапов.
    st.session_state.ally_ids = selected_ally_ids

st.write("")
if st.button("ОБНОВИТЬ ДАННЫЕ И ПЕРЕСЧИТАТЬ", use_container_width=True, type="primary",
             key="analyze_btn", disabled=not selected_enemy_ids):
    st.session_state.enemy_ids = selected_enemy_ids
    st.session_state.ally_ids = selected_ally_ids
    st.session_state.analyzed = True
    st.session_state["_force_refresh_data"] = True
    for cache_key in ("_request_pro_bundle", "_request_matchups", "_request_ranked_matchups",
                      "_request_enemy_combined"):
        st.session_state.pop(cache_key, None)
    st.rerun()


def _status_text() -> str:
    s = st.session_state.get("data_status", {})
    parts = []
    src = s.get("matchup_source")
    if src == "pro-matrix":
        extra = ", обновляется в фоне" if (s.get("pro") or {}).get("stale") else ""
        parts.append(f"про-матчи OpenDota за {PRO_DAYS} дн.: {s.get('matches', '?')} матчей{extra}")
    elif src == "pro-per-enemy":
        parts.append(f"про-матчи OpenDota за {PRO_DAYS} дн. (запросы по каждому выбранному врагу, кэш на диске)")
    elif src == "public-fallback":
        parts.append("про-данные недоступны, использованы публичные матчапы OpenDota (вне периода)")
    if s.get("matchup_backup"):
        parts.append(s["matchup_backup"])
    if s.get("ranked_matchups", {}).get("error") is None and s.get("ranked_matchups"):
        parts.append("матчапы Divine/Immortal за 30 дней")
    d2pt = s.get("d2pt")
    if d2pt == "ok":
        parts.append("билды Dota2ProTracker по позиции")
    elif d2pt:
        parts.append(f"Dota2ProTracker: резервный источник ({d2pt})")
    db = s.get("dotabuff")
    if db == "ok":
        parts.append("Dotabuff: подключён")
    elif db:
        parts.append(f"Dotabuff: недоступен ({db})")
    return "Источники: " + "; ".join(parts) if parts else ""


if st.session_state.analyzed and st.session_state.enemy_ids:
    ids = st.session_state.enemy_ids
    ally_ids = st.session_state.ally_ids
    role = st.session_state.role

    st.divider()
    st.markdown(f"**Состав врагов:** {', '.join(HEROES[i] for i in ids)}")
    if ally_ids:
        st.markdown(f"**Состав союзников:** {', '.join(HEROES[i] for i in ally_ids)}")

    st.session_state["api_errors"] = []
    st.session_state["data_status"] = {}

    # ===== КОГО ПИКАТЬ =====
    st.subheader("Кого пикать")
    st.caption("Рейтинг учитывает всех выбранных врагов; мета влияет меньше, чем матчапы.")

    with st.spinner("Загружаю про-статистику..."):
        top_picks = analyze_pick(ids, role, limit=8)

    plans = {}
    status_line = _status_text()
    if status_line:
        st.caption(status_line)

    if top_picks:
        top3, rest = top_picks[:3], top_picks[3:]
        _matchups = fetch_matchups(ids)
        _high_mmr_matchups = fetch_ranked_matchups(ids)
        _public_matchups = fetch_public_matchups(ids)
        _db = st.session_state.get("_db_data", {})

        for i, pick in enumerate(top3, start=1):
            reason = generate_pick_reason(pick, ids)
            with st.container(border=True):
                st.markdown(_hero_pick_card(i, pick), unsafe_allow_html=True)
                st.markdown(_matchup_visual(pick["id"], ids, _matchups, _high_mmr_matchups, _db, _public_matchups),
                            unsafe_allow_html=True)
                with st.expander("Почему этот пик"):
                    st.write(reason)
                    st.caption(f"Общая оценка: {pick['score']:.0f}% · учтены данные по {pick['matched_enemies']} из {len(ids)} врагов.")
                    for enemy_id in ids:
                        games, enemy_wins = _matchups.get(enemy_id, {}).get(pick["id"], (0, 0))
                        parts = []
                        if games:
                            adjusted_wr = (games - enemy_wins + SHRINK_K * 0.5) / (games + SHRINK_K) * 100
                            parts.append(_matchup_rate_label("OpenDota", adjusted_wr, games))
                        high_games, high_enemy_wins = _high_mmr_matchups.get(enemy_id, {}).get(pick["id"], (0, 0))
                        if high_games:
                            high_adjusted = (high_games - high_enemy_wins + 10) / (high_games + 20) * 100
                            parts.append(_matchup_rate_label("Divine/Immortal", high_adjusted, high_games))
                        db_entry = _db.get(enemy_id, {}).get(pick["id"])
                        if db_entry:
                            parts.append(_matchup_rate_label("Dotabuff", db_entry[1], db_entry[0]))
                        st.caption(f"{HEROES[enemy_id]}: " + (" · ".join(parts) or "нет статистики"))

        if rest:
            with st.expander(f"Ещё {len(rest)} вариант(а) в запасе"):
                for pick in rest:
                    why = HERO_STRENGTHS.get(pick["id"], "")
                    tail = f" — {why}" if why else ""
                    st.markdown(_hero_text_row(pick["id"], f"{pick['name']} — скор {pick['score']:.1f}%{tail}"),
                                unsafe_allow_html=True)
    else:
        api_errors = st.session_state.get("api_errors", [])
        if api_errors:
            st.error("Не удалось получить данные (это не значит, что данных не существует). Причина ниже.")
            with st.expander("Что именно пошло не так", expanded=True):
                for err in api_errors:
                    st.code(err, language=None)
                st.caption(
                    "Частые причины: сработал лимит запросов OpenDota, сервер перегружен или таймаут. "
                    "Приложение уже делало повторные попытки. Подожди минуту и нажми «Анализировать матч». "
                    "Ключ OPENDOTA_API_KEY сильно поднимает лимит."
                )
        else:
            st.warning(
                f"Для этой позиции и этих врагов в про-матчах за {PRO_DAYS} дней данных мало. "
                "Попробуй других героев или другую позицию."
            )

    # ===== БИЛД ПОД КОНКРЕТНОГО ГЕРОЯ =====
    if top_picks:
        st.divider()
        st.subheader("Предметы под выбранного героя")
        st.caption("Билд для выбранного героя и позиции.")

        selected_name = st.selectbox("За кого играем:", options=[p["name"] for p in top_picks])
        selected_id = name_to_id[selected_name]
        with st.spinner("Подбираю билд выбранного героя..."):
            plans = get_item_plans([selected_id], role)

        build, source = generate_adaptive_build(selected_id, role, ids, plans.get(selected_id))
        if source == "d2pt":
            sample = plans[selected_id].get("sample") or plans[selected_id].get("games", 0)
            st.success(f"Dota2ProTracker · позиция {plans[selected_id].get('position', _d2pt_position(role))} · около {sample} матчей")
        elif source == "opendota-pro":
            games = plans[selected_id]["games"]
            st.success(f"OpenDota · {games} про-матчей")
        elif source == "hero":
            st.info("Показан базовый билд героя.")
        else:
            st.warning("Про-билд недоступен; показан базовый билд позиции.")

        stage_titles = {
            "start": "Стартовый закуп",
            "early": "Ранняя игра (до 15 мин)",
            "core": "Мидгейм / основные предметы (15–30 мин)",
            "late": "Поздняя игра",
        }
        for stage_key, title in stage_titles.items():
            if build.get(stage_key):
                st.markdown(_item_stage_card(title, build[stage_key]), unsafe_allow_html=True)
    else:
        selected_id = None

    st.session_state["_force_refresh_data"] = False

    # ===== СИНЕРГИЯ =====
    if ally_ids:
        st.divider()
        st.subheader("Синергия с выбранными союзниками")
        synergy = get_synergy_recommendations(ally_ids, role, exclude_ids=set(ids) | set(ally_ids))
        if synergy:
            for s in synergy:
                synergy_id = name_to_id.get(s["hero"])
                if synergy_id:
                    synergy_text = f"{s['hero']} · комбо с {', '.join(s['with'])}: {s['reason']}"
                    st.markdown(_hero_text_row(synergy_id, synergy_text), unsafe_allow_html=True)
        else:
            st.write("Специфических комбо-связок с указанной комбинацией не найдено.")

    # ===== ЧТО ПОКУПАТЬ ПРОТИВ ЭТОГО СОСТАВА =====
    if top_picks:
        st.divider()
        st.subheader(f"Что докупить за {selected_name} против этого состава")
        counters = get_counters_against(ids, role, candidate_id=selected_id)
        if counters:
            by_category = {c: [] for c in CATEGORY_ORDER}
            for c in counters:
                by_category[c.get("category", "other")].append(c)

            for category in CATEGORY_ORDER:
                items = by_category[category]
                if not items:
                    continue
                st.markdown(f"#### {CATEGORY_LABEL[category]}")
                for c in items:
                    detail = f"{c['reason']} · против {', '.join(c['targets'])}"
                    st.markdown(_item_build_row(c["item"], detail), unsafe_allow_html=True)

            with st.expander("Предметы по времени покупки"):
                by_timing = {t: [] for t in TIMING_ORDER}
                for c in counters:
                    by_timing[c["timing"]].append(c)
                for timing in TIMING_ORDER:
                    if not by_timing[timing]:
                        continue
                    st.markdown(f"**{TIMING_LABEL[timing]}**")
                    for c in by_timing[timing]:
                        detail = f"Против {', '.join(c['targets'])} · {c['reason']}"
                        st.markdown(_item_build_row(c["item"], detail), unsafe_allow_html=True)
        else:
            st.write("Специфических предметных противодействий не требуется.")

    st.success("Данные успешно сформированы.")









