import random
from itertools import combinations

from models import Creature, Expedition, Assignment, Solution
from config import (
    STAT_NAMES,
    BIOME_TYPE_MULTIPLIERS,
    DEFAULT_TYPE_MULTIPLIER,
    MULTIPLIER_SAME_TRAIT,
    MULTIPLIER_DIFF_TRAIT,
    PARTY_MIN_SIZE,
    PARTY_MAX_SIZE,
    LS_MAX_NO_IMPROVE,
    LS_MAX_ITERATIONS,
    LS_RANDOM_SEED,
    PERTURBATION_WEIGHTS,
)


class Solver:

    def __init__(
        self,
        creatures: list[Creature],
        expeditions: list[Expedition],
        max_no_improve: int = LS_MAX_NO_IMPROVE,
        max_iterations: int = LS_MAX_ITERATIONS,
        random_seed: int | None = LS_RANDOM_SEED,
    ):
        self.creatures    = creatures
        self.expeditions  = expeditions
        self.max_no_improve = max_no_improve
        self.max_iterations = max_iterations

        if random_seed is not None:
            random.seed(random_seed)

        # 预计算所有 (creature, expedition, rank) 的得分，避免重复计算
        self._score_cache: dict[tuple, float] = {}

    # ═══════════════════════════════════════════════════════
    # 公开接口
    # ═══════════════════════════════════════════════════════

    def run(self) -> Solution:
        solution = self._greedy_init()
        solution = self._local_search(solution)
        return solution

    # ═══════════════════════════════════════════════════════
    # 得分计算
    # ═══════════════════════════════════════════════════════

    def _creature_score(self, creature: Creature, expedition: Expedition) -> float:
        key = (creature.name, expedition.name)
        if key in self._score_cache:
            return self._score_cache[key]

        stats        = creature.actual_stats()
        weighted_sum = sum(stats[s] * expedition.weights.get(s, 0.0) for s in STAT_NAMES)

        type_mult = BIOME_TYPE_MULTIPLIERS.get(
            expedition.biome, {}
        ).get(creature.creature_type, DEFAULT_TYPE_MULTIPLIER)

        trait_mult = (
            MULTIPLIER_SAME_TRAIT
            if creature.trait == expedition.trait
            else MULTIPLIER_DIFF_TRAIT
        )

        score = weighted_sum * type_mult * trait_mult
        self._score_cache[key] = score
        return score

    def _party_score(self, party: list[Creature], expedition: Expedition) -> float:
        return sum(self._creature_score(c, expedition) for c in party)

    def _assignment_exp_rate(self, assignment: Assignment) -> float:
        score = self._party_score(assignment.party, assignment.expedition)
        t     = assignment.expedition.completion_time(assignment.rank, score)
        exp   = assignment.expedition.get_exp(assignment.rank)
        return exp / t if t > 0 else 0.0

    def _solution_fitness(self, solution: Solution) -> float:
        return sum(self._assignment_exp_rate(a) for a in solution.assignments)

    # ═══════════════════════════════════════════════════════
    # 第一阶段：贪心初始化
    # ═══════════════════════════════════════════════════════

    def _greedy_init(self) -> Solution:
        # 枚举所有候选组合 (expedition, rank, party)
        candidates = []
        for expedition in self.expeditions:
            for rank in expedition.available_ranks():
                max_size = min(PARTY_MAX_SIZE, len(self.creatures))
                for size in range(PARTY_MIN_SIZE, max_size + 1):
                    for combo in combinations(self.creatures, size):
                        party = list(combo)
                        score = self._party_score(party, expedition)
                        exp   = expedition.get_exp(rank)
                        t     = expedition.completion_time(rank, score)
                        rate  = exp / t if t > 0 else 0.0
                        candidates.append((rate, expedition, rank, party))

        # 按总经验效率降序排列
        candidates.sort(key=lambda x: x[0], reverse=True)

        used_creatures:   set[str] = set()
        used_expeditions: set[str] = set()
        assignments: list[Assignment] = []

        for rate, expedition, rank, party in candidates:
            party_names = {c.name for c in party}
            if expedition.name in used_expeditions:
                continue
            if party_names & used_creatures:
                continue
            assignments.append(Assignment(
                expedition=expedition,
                rank=rank,
                party=party,
            ))
            used_creatures   |= party_names
            used_expeditions.add(expedition.name)

        # 收集闲置 creature
        idle = [c for c in self.creatures if c.name not in used_creatures]

        return Solution(assignments=assignments, idle_creatures=idle)

    # ═══════════════════════════════════════════════════════
    # 第二阶段：局部搜索
    # ═══════════════════════════════════════════════════════

    def _local_search(self, solution: Solution) -> Solution:
        current         = solution
        current_fitness = self._solution_fitness(current)
        best            = current
        best_fitness    = current_fitness

        ops     = list(PERTURBATION_WEIGHTS.keys())
        weights = list(PERTURBATION_WEIGHTS.values())

        no_improve = 0
        for _ in range(self.max_iterations):
            if no_improve >= self.max_no_improve:
                break

            op       = random.choices(ops, weights=weights, k=1)[0]
            neighbor = self._perturb(current, op)

            if neighbor is None:
                no_improve += 1
                continue

            neighbor_fitness = self._solution_fitness(neighbor)

            if neighbor_fitness > current_fitness:
                current         = neighbor
                current_fitness = neighbor_fitness
                no_improve      = 0

                if current_fitness > best_fitness:
                    best         = current
                    best_fitness = current_fitness
            else:
                no_improve += 1

        return best

    # ═══════════════════════════════════════════════════════
    # 扰动操作
    # ═══════════════════════════════════════════════════════

    def _perturb(self, solution: Solution, op: str) -> Solution | None:
        if op == "swap_pets":
            return self._swap_creatures(solution)
        elif op == "replace_idle":
            return self._replace_idle(solution)
        elif op == "switch_difficulty":
            return self._switch_difficulty(solution)
        elif op == "rebuild_party":
            return self._rebuild_party(solution)
        return None

    def _swap_creatures(self, solution: Solution) -> Solution | None:
        """两个不同 Assignment 中各取一只 Creature 互换"""
        if len(solution.assignments) < 2:
            return None

        a1, a2 = random.sample(solution.assignments, 2)
        if not a1.party or not a2.party:
            return None

        c1 = random.choice(a1.party)
        c2 = random.choice(a2.party)

        new_party1 = [c2 if c is c1 else c for c in a1.party]
        new_party2 = [c1 if c is c2 else c for c in a2.party]

        new_assignments = []
        for a in solution.assignments:
            if a is a1:
                new_assignments.append(Assignment(a1.expedition, a1.rank, new_party1))
            elif a is a2:
                new_assignments.append(Assignment(a2.expedition, a2.rank, new_party2))
            else:
                new_assignments.append(a)

        return Solution(assignments=new_assignments, idle_creatures=solution.idle_creatures)

    def _replace_idle(self, solution: Solution) -> Solution | None:
        """用一只闲置 Creature 替换某个 Assignment 中的某只 Creature"""
        if not solution.idle_creatures or not solution.assignments:
            return None

        idle_c      = random.choice(solution.idle_creatures)
        assignment  = random.choice(solution.assignments)
        if not assignment.party:
            return None
        target_c    = random.choice(assignment.party)

        new_party = [idle_c if c is target_c else c for c in assignment.party]
        new_idle  = [c for c in solution.idle_creatures if c is not idle_c]
        new_idle.append(target_c)

        new_assignments = [
            Assignment(a.expedition, a.rank, new_party) if a is assignment else a
            for a in solution.assignments
        ]

        return Solution(assignments=new_assignments, idle_creatures=new_idle)

    def _switch_difficulty(self, solution: Solution) -> Solution | None:
        """将某个 Assignment 的难度调高或调低一级"""
        if not solution.assignments:
            return None

        assignment = random.choice(solution.assignments)
        ranks      = assignment.expedition.available_ranks()
        if len(ranks) < 2:
            return None

        current_idx = ranks.index(assignment.rank)
        candidates  = []
        if current_idx > 0:
            candidates.append(ranks[current_idx - 1])
        if current_idx < len(ranks) - 1:
            candidates.append(ranks[current_idx + 1])

        new_rank        = random.choice(candidates)
        new_assignments = [
            Assignment(a.expedition, new_rank, a.party) if a is assignment else a
            for a in solution.assignments
        ]

        return Solution(assignments=new_assignments, idle_creatures=solution.idle_creatures)

    def _rebuild_party(self, solution: Solution) -> Solution | None:
        """拆散某支队伍，将成员放回闲置池，再贪心重新组一支队"""
        if not solution.assignments:
            return None

        assignment   = random.choice(solution.assignments)
        freed        = list(assignment.party)
        all_idle     = solution.idle_creatures + freed
        all_idle_set = {c.name for c in all_idle}

        # 从闲置池中贪心选出最优队伍（1~3只）
        best_rate   = -1.0
        best_party  = []
        best_rank   = assignment.expedition.available_ranks()[0]
        max_size    = min(PARTY_MAX_SIZE, len(all_idle))

        for size in range(PARTY_MIN_SIZE, max_size + 1):
            for combo in combinations(all_idle, size):
                party = list(combo)
                for rank in assignment.expedition.available_ranks():
                    score = self._party_score(party, assignment.expedition)
                    exp   = assignment.expedition.get_exp(rank)
                    t     = assignment.expedition.completion_time(rank, score)
                    rate  = exp / t if t > 0 else 0.0
                    if rate > best_rate:
                        best_rate  = rate
                        best_party = party
                        best_rank  = rank

        if not best_party:
            return None

        new_idle = [c for c in all_idle if c.name not in {c.name for c in best_party}]
        new_assignments = [
            Assignment(assignment.expedition, best_rank, best_party) if a is assignment else a
            for a in solution.assignments
        ]

        return Solution(assignments=new_assignments, idle_creatures=new_idle)