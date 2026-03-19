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
    difficulties: dict[int, tuple[float, int]] = field(default_factory=dict)

    def completion_time(self, rank: int, total_score: float) -> int:
        import math
        required_score, _ = self.difficulties[rank]
        ratio = total_score / required_score
        return int(math.floor(max(60 - ratio * 55, 5)))

    def exp_rate(self, rank: int, total_score: float, party_size: int) -> float:
        _, exp = self.difficulties[rank]
        t = self.completion_time(rank, total_score)
        return (exp / party_size) / t

    def get_exp(self, rank: int) -> int:
        return self.difficulties[rank][1]

    def get_required_score(self, rank: int) -> float:
        return self.difficulties[rank][0]

    def available_ranks(self) -> list[int]:
        return sorted(self.difficulties.keys())

    def is_valid_rank(self, rank: int) -> bool:
        return rank in self.difficulties

@dataclass
class Assignment:

    expedition: Expedition
    rank: int
    party: list[Creature] = field(default_factory=list)

    def total_score(self) -> float:
        from evaluator import calc_total_score
        return calc_total_score(self.party, self.expedition)

    def completion_time(self) -> int:
        return self.expedition.completion_time(self.rank, self.total_score())

    def total_exp_rate(self) -> float:
        t = self.completion_time()
        return self.expedition.get_exp(self.rank) / t if t > 0 else 0.0

    def per_creature_exp_rate(self) -> float:
        n = len(self.party)
        t = self.completion_time()
        return (self.expedition.get_exp(self.rank) / n) / t if n > 0 and t > 0 else 0.0

    def is_valid(self) -> bool:
        from config import PARTY_MIN_SIZE, PARTY_MAX_SIZE
        return (
            self.expedition is not None
            and self.expedition.is_valid_rank(self.rank)
            and PARTY_MIN_SIZE <= len(self.party) <= PARTY_MAX_SIZE
        )

@dataclass
class Solution:

    assignments: list[Assignment] = field(default_factory=list)
    idle_creatures: list[Creature] = field(default_factory=list)

    def total_fitness(self) -> float:
        return sum(a.total_exp_rate() for a in self.assignments)

    def assigned_creatures(self) -> set[Creature]:
        return {c for a in self.assignments for c in a.party}

    def used_expeditions(self) -> set[Expedition]:
        return {a.expedition for a in self.assignments}

    def is_valid(self) -> bool:
        creatures = [c for a in self.assignments for c in a.party]
        expeditions = [a.expedition for a in self.assignments]
        return (
            len(creatures) == len(set(creatures))
            and len(expeditions) == len(set(expeditions))
            and all(a.is_valid() for a in self.assignments)
        )