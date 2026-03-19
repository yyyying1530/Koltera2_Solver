from example.data_manager import DataManager
from example.solver import Solver
from example.config import LS_MAX_NO_IMPROVE, LS_MAX_ITERATIONS


class OptimizeMenu:

    def __init__(self, data_manager: DataManager):
        self.dm = data_manager
        self.last_solution = None
        self.params = {
            "max_no_improve": LS_MAX_NO_IMPROVE,
            "max_iterations":  LS_MAX_ITERATIONS,
        }

    def show(self):
        while True:
            self._print_header()
            print("  1. 运行优化")
            print("  2. 查看上次结果")
            print("  3. 调整参数")
            print("  4. 导出结果")
            print("  0. 返回主菜单")
            print()
            choice = input("请选择：").strip()

            if choice == "1":
                self._run()
            elif choice == "2":
                self._show_result()
            elif choice == "3":
                self._set_params()
            elif choice == "4":
                self._export()
            elif choice == "0":
                break
            else:
                print("  ⚠ 无效输入")

    def _run(self):
        print()
        creatures   = self.dm.creatures
        expeditions = self.dm.expeditions

        if not creatures:
            print("  ⚠ 没有可用的 Creature，请先添加数据")
            return
        if not expeditions:
            print("  ⚠ 没有可用的 Expedition，请先添加数据")
            return

        print(f"  正在优化：{len(creatures)} 只 Creature / {len(expeditions)} 个 Expedition ...")
        print(f"  参数：max_no_improve={self.params['max_no_improve']}  "
              f"max_iterations={self.params['max_iterations']}")
        print()

        solver = Solver(
            creatures=creatures,
            expeditions=expeditions,
            max_no_improve=self.params["max_no_improve"],
            max_iterations=self.params["max_iterations"],
        )
        self.last_solution = solver.run()
        self._print_solution()

    def _show_result(self):
        print()
        if self.last_solution is None:
            print("  （尚未运行优化）")
            return
        self._print_solution()

    def _set_params(self):
        print()
        print("  ── 调整参数 ──")
        print(f"  当前 max_no_improve = {self.params['max_no_improve']}")
        raw = input("  新值（回车保持不变）：").strip()
        if raw:
            try:
                self.params["max_no_improve"] = int(raw)
            except ValueError:
                print("  ⚠ 请输入整数")
                return

        print(f"  当前 max_iterations = {self.params['max_iterations']}")
        raw = input("  新值（回车保持不变）：").strip()
        if raw:
            try:
                self.params["max_iterations"] = int(raw)
            except ValueError:
                print("  ⚠ 请输入整数")
                return

        print("  ✓ 参数已更新")

    def _export(self):
        print()
        if self.last_solution is None:
            print("  （尚未运行优化，无结果可导出）")
            return

        path = input("  导出路径（默认 result.txt）：").strip() or "result.txt"
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self._format_solution())
            print(f"  ✓ 结果已导出至 {path}")
        except IOError as e:
            print(f"  ⚠ 导出失败：{e}")

    def _print_solution(self):
        print(self._format_solution())

    def _format_solution(self) -> str:
        s = self.last_solution
        lines = []
        lines.append("═" * 60)
        lines.append("  优化结果")
        lines.append("═" * 60)

        for i, assignment in enumerate(s.assignments, 1):
            party_str = ", ".join(c.name for c in assignment.party)
            lines.append(
                f"  [{i}] [{party_str}]"
                f"  →  {assignment.expedition.name}  难度{assignment.rank}"
            )
            lines.append(
                f"       总得分: {assignment.total_score():>8.1f}  |  "
                f"用时: {assignment.completion_time():>3} min  |  "
                f"总经验效率: {assignment.total_exp_rate():.2f} exp/min"
            )

        if s.idle_creatures:
            lines.append("")
            idle_str = ", ".join(c.name for c in s.idle_creatures)
            lines.append(f"  ⚠ 闲置 Creature：{idle_str}")

        lines.append("")
        lines.append(f"  ► 总适应度：{s.total_fitness():.2f} exp/min")
        lines.append("═" * 60)
        return "\n".join(lines) + "\n"

    def _print_header(self):
        print()
        print("─" * 50)
        print("  优化运行")
        print("─" * 50)