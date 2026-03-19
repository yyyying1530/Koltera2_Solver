import csv
from models import Creature, Expedition, Assignment, Solution
from config import (
    VALID_TYPES, VALID_TRAITS, VALID_BIOMES,
    STAT_NAMES, CREATURE_CSV_COLUMNS, EXPEDITION_CSV_COLUMNS
)

class DataManager:
    creatue_path: str
    expedition_path: str
    creatues: list[Creature]
    expeditions: list[Expedition]

    def __init__(self, creatures_path: str, expedition_path: str):
        self.creatures_path = creatures_path
        self.expeditions_path = expedition_path
        self.creatures = []
        self.expeditions = []

    def load(self):
        self.load_creatues()
        self.load_expeditions()

    def load_creatues(self):
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

    def load_expeditions(self):
        self.expeditions = []
        raw: dict[str, dict] = {}

        with open(self.expeditions_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row["name"]

                # 首次遇到该地下城时初始化基础信息
                if name not in raw:
                    raw[name] = {
                        "biome": row["biome"],
                        "trait": row["trait"],
                        "weights": {
                            stat: float(row[f"weight_{stat}"])
                            for stat in STAT_NAMES
                        },
                        "difficulties": {},
                    }

                # 追加难度数据
                rank = int(row["rank"])
                raw[name]["difficulties"][rank] = (
                    float(row["required_score"]),
                    int(row["exp"]),
                )

        for name, data in raw.items():
            self.expeditions.append(
                Expedition(
                    name=name,
                    biome=data["biome"],
                    trait=data["trait"],
                    weights=data["weights"],
                    difficulties=data["difficulties"],
                )
            )

    def save(self):
        self.save_creatures()
        self.save_expeditions()

    def save_creatures(self):
        with open(self.creatures_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=CREATURE_CSV_COLUMNS)
            writer.writeheader()
            for c in self.creatures:
                row = {
                    "name": c.name,
                    "level": c.level,
                    "type": c.creature_type,
                    "trait": c.trait,
                    **c.base_stats,
                }
                writer.writerow(row)

    def save_expeditions(self):
        with open(self.expeditions_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=EXPEDITION_CSV_COLUMNS)
            writer.writeheader()
            for e in self.expeditions:
                for rank, (required_score, exp) in sorted(e.difficulties.items()):
                    row = {
                        "name": e.name,
                        "biome": e.biome,
                        "trait": e.trait,
                        **{f"weight_{stat}": e.weights.get(stat, 0.0) for stat in STAT_NAMES},
                        "rank": rank,
                        "required_score": required_score,
                        "exp": exp,
                    }
                    writer.writerow(row)

    def get_creature(self, name: str) -> Creature:
        for c in self.creatures:
            if c.name == name:
                return c
        raise KeyError(f"Creature「{name}」不存在")

    def add_creature(self, creature: Creature):
        errors = self.validate_creature(creature.__dict__)
        if errors:
            raise ValueError("\n".join(errors))
        if any(c.name == creature.name for c in self.creatures):
            raise ValueError(f"Creature「{creature.name}」已存在")
        self.creatures.append(creature)
        self.save_creatures()

    def update_creature(self, name: str, updated: Creature):
        errors = self.validate_creature(updated.__dict__)
        if errors:
            raise ValueError("\n".join(errors))
        for i, c in enumerate(self.creatures):
            if c.name == name:
                self.creatures[i] = updated
                self.save_creatures()
                return
        raise KeyError(f"Creature「{name}」不存在")

    def delete_creature(self, name: str):
        for i, c in enumerate(self.creatures):
            if c.name == name:
                self.creatures.pop(i)
                self.save_creatures()
                return
        raise KeyError(f"Creature「{name}」不存在")

    # ── Expedition CRUD

    def get_expedition(self, name: str) -> Expedition:
        for e in self.expeditions:
            if e.name == name:
                return e
        raise KeyError(f"Expedition「{name}」不存在")

    def add_expedition(self, expedition: Expedition):
        errors = self.validate_expedition(expedition.__dict__)
        if errors:
            raise ValueError("\n".join(errors))
        if any(e.name == expedition.name for e in self.expeditions):
            raise ValueError(f"Expedition「{expedition.name}」已存在")
        self.expeditions.append(expedition)
        self.save_expeditions()

    def update_expedition(self, name: str, updated: Expedition):
        errors = self.validate_expedition(updated.__dict__)
        if errors:
            raise ValueError("\n".join(errors))
        for i, e in enumerate(self.expeditions):
            if e.name == name:
                self.expeditions[i] = updated
                self.save_expeditions()
                return
        raise KeyError(f"Expedition「{name}」不存在")

    def delete_expedition(self, name: str):
        for i, e in enumerate(self.expeditions):
            if e.name == name:
                self.expeditions.pop(i)
                self.save_expeditions()
                return
        raise KeyError(f"Expedition「{name}」不存在")

# ── 校验

    def validate_creature(self, data: dict) -> list[str]:
        errors = []

        if not data.get("name", "").strip():
            errors.append("name 不能为空")

        if not self._validate_type(data.get("creature_type", "")):
            errors.append(f"creature_type 非法，可选值：{VALID_TYPES}")

        if not self._validate_trait(data.get("trait", "")):
            errors.append(f"trait 非法，可选值：{VALID_TRAITS}")

        level = data.get("level", 0)
        if not isinstance(level, int) or level < 1:
            errors.append("level 必须为正整数")

        base_stats = data.get("base_stats", {})
        for stat in STAT_NAMES:
            val = base_stats.get(stat, -1)
            if not isinstance(val, (int, float)) or val < 0:
                errors.append(f"base_stats.{stat} 必须为非负数")

        return errors

    def validate_expedition(self, data: dict) -> list[str]:
        errors = []

        if not data.get("name", "").strip():
            errors.append("name 不能为空")

        if not self._validate_biome(data.get("biome", "")):
            errors.append(f"biome 非法，可选值：{VALID_BIOMES}")

        if not self._validate_trait(data.get("trait", "")):
            errors.append(f"trait 非法，可选值：{VALID_TRAITS}")

        if not self._validate_weights(data.get("weights", {})):
            errors.append("weights 各值必须为非负数，且合计应为 1.0")

        difficulties = data.get("difficulties", {})
        if not difficulties:
            errors.append("difficulties 不能为空，至少需要一个难度")
            return errors

        for rank, val in difficulties.items():
            if not isinstance(rank, int) or rank < 1 or rank > 5:
                errors.append(f"difficulties 的 rank 必须为 1~5 的整数，当前：{rank}")
                continue
            if not isinstance(val, tuple) or len(val) != 2:
                errors.append(f"difficulties[{rank}] 格式错误，应为 (required_score, exp)")
                continue
            req, exp = val
            if not isinstance(req, (int, float)) or req < 0:
                errors.append(f"difficulties[{rank}].required_score 必须为非负数")
            if not isinstance(exp, int) or exp < 0:
                errors.append(f"difficulties[{rank}].exp 必须为非负整数")

        return errors

    def _validate_type(self, value: str) -> bool:
        return value in VALID_TYPES

    def _validate_trait(self, value: str) -> bool:
        return value in VALID_TRAITS

    def _validate_biome(self, value: str) -> bool:
        return value in VALID_BIOMES

    def _validate_weights(self, weights: dict) -> bool:
        if not weights:
            return False
        if set(weights.keys()) != set(STAT_NAMES):
            return False
        if not all(isinstance(v, (int, float)) and v >= 0 for v in weights.values()):
            return False
        total = sum(weights.values())
        return abs(total - 1.0) < 1e-6