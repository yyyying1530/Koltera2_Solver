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