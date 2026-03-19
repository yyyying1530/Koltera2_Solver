from dataclasses import dataclass, field
from config import STAT_NAMES

@dataclass
class Creature:
    name: str
    level: int
    creature_type: str
    trait: str
    base_stats: dict[str, float]

    def actual_stats(self) -> dict[str, float]:
        return {
            stat: self.base_stats.get(stat, 0.0) * self.level
            for stat in STAT_NAMES
        }

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other) -> bool:
        return isinstance(other, Creature) and self.name == other.name


@dataclass
class Expedition:
    name: str
    biome: str
    trait: str
    weights: dict[str, float]
    max_lvl: int
    base_score: int
    base_exp: int
    
    def completion_time(self, rank: int, total_score: float) -> int:
        import math
        required_score = self.base_score * (1 + (rank - 1) * 0.5)
        ratio = total_score / required_score
        return int(math.floor(max(60 - ratio * 55, 5))) * 60
    
    def exp_rate(self, rank: int, total_score: float, party_size: int) -> float:
        exp = self.base_exp * (1 + (rank - 1) * 0.2)
        t = self.completion_time(rank, total_score)
        return (exp / party_size) / t
    
    def get_exp(self, rank: int) -> int:
        return self.base_exp * (1 + (rank - 1) * 0.2)

    def get_required_score(self, rank: int) -> float:
        return self.base_score * (1 + (rank - 1) * 0.5)

    def available_ranks(self) -> list[int]:
        return list(range(1, self.max_lvl + 1))

    def is_valid_rank(self, rank: int) -> bool:
        return 1 <= rank <= self.max_lvl