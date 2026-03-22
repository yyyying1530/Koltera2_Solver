import csv
from models import Creature, Expedition
from config import STAT_NAMES

class DataManager:
    creature_path: str
    expedition_path: str
    creatures: list[Creature]
    expeditions: list[Expedition]

    def __init__(self, creature_path: str, expedition_path: str):
        self.creature_path = creature_path
        self.expedition_path = expedition_path

    def load(self):
        with open(self.creatures_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                creature = Creature(
                    name=row["name"],
                    level=int(row["level"]),
                    creature_type=row["type"],
                    trait=row["trait"],
                    base_stats={stat: float(row[stat]) for stat in STAT_NAMES},
                )
                self.creatures.append(creature)

        with open(self.expeditions_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                expedition = Expedition(
                    name=row["name"],
                    biome=row["biome"],
                    trait=row["trait"],
                    weights={stat: float(row[stat]) for stat in STAT_NAMES},
                    max_lvl=row['max_lvl'],
                    base_exp=int(row['base_exp']),
                    base_score=int(row['base_score']),
                )
                self.expeditions.append(expedition)
