from models import Creature, Expedition, Assignment, Solution
from config import (
    STAT_NAMES,
    BIOME_TYPE_MULTIPLIERS,
    DEFAULT_TYPE_MULTIPLIER,
    MULTIPLIER_SAME_TRAIT,
    MULTIPLIER_DIFF_TRAIT,
)


def get_type_multiplier(creature_type: str, biome: str) -> float:
    return BIOME_TYPE_MULTIPLIERS.get(biome, {}).get(
        creature_type, DEFAULT_TYPE_MULTIPLIER
    )


def get_trait_multiplier(creature_trait: str, expedition_trait: str) -> float:
    return (
        MULTIPLIER_SAME_TRAIT
        if creature_trait == expedition_trait
        else MULTIPLIER_DIFF_TRAIT
    )


def calc_creature_score(creature: Creature, expedition: Expedition) -> float:
    """单只 Creature 在指定 Expedition 中的得分"""
    stats        = creature.actual_stats()
    weighted_sum = sum(
        stats[s] * expedition.weights.get(s, 0.0) for s in STAT_NAMES
    )
    type_mult  = get_type_multiplier(creature.creature_type, expedition.biome)
    trait_mult = get_trait_multiplier(creature.trait, expedition.trait)
    return weighted_sum * type_mult * trait_mult


def calc_total_score(party: list[Creature], expedition: Expedition) -> float:
    """队伍在指定 Expedition 中的总得分"""
    return sum(calc_creature_score(c, expedition) for c in party)


def calc_completion_time(
    party: list[Creature],
    expedition: Expedition,
    rank: int,
) -> int:
    """队伍完成指定难度的时间（分钟）"""
    score = calc_total_score(party, expedition)
    return expedition.completion_time(rank, score)


def calc_exp_rate(
    party: list[Creature],
    expedition: Expedition,
    rank: int,
) -> float:
    """队伍总经验效率（exp/min）"""
    t   = calc_completion_time(party, expedition, rank)
    exp = expedition.get_exp(rank)
    return exp / t if t > 0 else 0.0


def calc_per_creature_exp_rate(
    party: list[Creature],
    expedition: Expedition,
    rank: int,
) -> float:
    """单 Creature 经验效率（exp/min）"""
    n = len(party)
    if n == 0:
        return 0.0
    t   = calc_completion_time(party, expedition, rank)
    exp = expedition.get_exp(rank)
    return (exp / n) / t if t > 0 else 0.0


def calc_score_ratio(
    party: list[Creature],
    expedition: Expedition,
    rank: int,
) -> float:
    """总得分 / 需求分（>= 1.0 则达标）"""
    required = expedition.get_required_score(rank)
    if required <= 0:
        return 999.0
    return calc_total_score(party, expedition) / required


def evaluate_assignment(assignment: Assignment) -> dict:
    """
    对一个 Assignment 进行完整评估，返回所有关键指标。
    供 CLI 展示和结果导出使用。
    """
    party      = assignment.party
    expedition = assignment.expedition
    rank       = assignment.rank

    total_score = calc_total_score(party, expedition)
    time        = expedition.completion_time(rank, total_score)
    exp         = expedition.get_exp(rank)
    required    = expedition.get_required_score(rank)
    n           = len(party)

    return {
        "party":               [c.name for c in party],
        "party_size":          n,
        "expedition":          expedition.name,
        "rank":                rank,
        "total_score":         round(total_score, 2),
        "required_score":      required,
        "score_ratio":         round(total_score / required, 4) if required > 0 else 999.0,
        "meets_requirement":   total_score >= required,
        "completion_time":     time,
        "exp":                 exp,
        "exp_per_creature":    round(exp / n, 1) if n > 0 else 0.0,
        "total_exp_rate":      round(exp / time, 4) if time > 0 else 0.0,
        "per_creature_exp_rate": round((exp / n) / time, 4) if n > 0 and time > 0 else 0.0,
    }


def evaluate_solution(solution: Solution) -> dict:
    """
    对完整 Solution 进行评估，返回汇总指标。
    """
    assignment_results = [
        evaluate_assignment(a) for a in solution.assignments
    ]
    total_fitness = sum(r["total_exp_rate"] for r in assignment_results)

    return {
        "assignments":       assignment_results,
        "idle_creatures":    [c.name for c in solution.idle_creatures],
        "total_fitness":     round(total_fitness, 4),
        "total_assignments": len(solution.assignments),
        "total_idle":        len(solution.idle_creatures),
    }