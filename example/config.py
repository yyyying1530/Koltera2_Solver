STAT_NAMES: list[str] = [
    "power", "grit", "agility", "smart", "looting", "luck"
]

VALID_TYPES: list[str] = [
    "water", "fire", "earth", "wind"
]

VALID_TRAITS: list[str] = [
    "Camouflage", "Cold Resistance", "Gatherer", "Hard Shell",
    "Heat Resistance", "Learner", "Lucky", "Night Vision",
    "Poison Resistance", "Regeneration", "Scouting",
    "Tracking", "Water Breathing",
]

BIOME_TYPE_MULTIPLIERS: dict[str, dict[str, float]] = {
    "Plains": {"water": 0.5, "wind": 1.5, "fire": 1.0, "earth": 1.0},
}

VALID_BIOMES: list[str] = list(BIOME_TYPE_MULTIPLIERS.keys())

DEFAULT_TYPE_MULTIPLIER: float = 1.0

MULTIPLIER_SAME_TRAIT: float = 1.5
MULTIPLIER_DIFF_TRAIT: float = 1.0

PARTY_MIN_SIZE: int = 1
PARTY_MAX_SIZE: int = 3

LS_MAX_NO_IMPROVE: int = 500    # 连续无改善次数上限
LS_MAX_ITERATIONS: int = 10000  # 最大迭代次数
LS_RANDOM_SEED:    int | None = None     # 随机种子（None 则每次结果不同）

PERTURBATION_WEIGHTS: dict[str, float] = {
    "swap_pets":         0.35,  # 两个地下城间交换某只宠物
    "replace_idle":      0.30,  # 用闲置宠物替换队内某只宠物
    "switch_difficulty": 0.25,  # 切换某地下城的难度档位
    "rebuild_party":     0.10,  # 拆散并重组某支队伍
}

CREATURE_CSV_COLUMNS: list[str] = [
    "name", "level", "type", "trait",
    "power", "grit", "agility", "smart", "looting", "luck",
]

EXPEDITION_CSV_COLUMNS: list[str] = [
    "name", "biome", "trait",
    "weight_power", "weight_grit", "weight_agility",
    "weight_smart", "weight_looting", "weight_luck",
    "rank", "required_score", "exp",
]
