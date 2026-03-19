from example.data_manager import DataManager
from example.models import Expedition
from example.config import VALID_TRAITS, VALID_BIOMES, STAT_NAMES


class ExpeditionMenu:

    def __init__(self, data_manager: DataManager):
        self.dm = data_manager

    def show(self):
        while True:
            self._print_header()
            print("  1. 查看所有 Expedition")
            print("  2. 新增 Expedition")
            print("  3. 编辑 Expedition")
            print("  4. 删除 Expedition")
            print("  0. 返回主菜单")
            print()
            choice = input("请选择：").strip()

            if choice == "1":
                self._list()
            elif choice == "2":
                self._add()
            elif choice == "3":
                self._edit()
            elif choice == "4":
                self._delete()
            elif choice == "0":
                break
            else:
                print("  ⚠ 无效输入")

    def _list(self):
        print()
        expeditions = self.dm.expeditions
        if not expeditions:
            print("  （暂无 Expedition）")
            return
        for e in expeditions:
            print(f"  【{e.name}】Biome: {e.biome}  Trait: {e.trait}")
            weight_str = "  ".join(
                f"{s}×{v:.0%}" for s, v in e.weights.items() if v > 0
            )
            print(f"    权重：{weight_str}")
            print(f"    难度：", end="")
            for rank in e.available_ranks():
                req, exp = e.difficulties[rank]
                print(f"[{rank}] 需求={req} 经验={exp}  ", end="")
            print()
        print()

    def _add(self):
        print()
        print("  ── 新增 Expedition ──")

        name = input("  名称：").strip()
        if not name:
            print("  ⚠ 名称不能为空")
            return

        biome = self._input_choice("  Biome", VALID_BIOMES)
        if biome is None:
            return

        trait = self._input_choice("  Trait", VALID_TRAITS)
        if trait is None:
            return

        print("  输入属性权重（合计应为 1.0）：")
        weights = {}
        for stat in STAT_NAMES:
            val = self._input_float(f"    {stat}：", min_val=0.0)
            if val is None:
                return
            weights[stat] = val

        difficulties = self._input_difficulties()
        if difficulties is None:
            return

        expedition = Expedition(
            name=name,
            biome=biome,
            trait=trait,
            weights=weights,
            difficulties=difficulties,
        )

        try:
            self.dm.add_expedition(expedition)
            print(f"  ✓ Expedition「{name}」已添加")
        except ValueError as e:
            print(f"  ⚠ {e}")

    def _edit(self):
        print()
        name = input("  输入要编辑的 Expedition 名称：").strip()
        try:
            expedition = self.dm.get_expedition(name)
        except KeyError as e:
            print(f"  ⚠ {e}")
            return

        print()
        print("  选择要修改的字段：")
        print("  1. Biome")
        print("  2. Trait")
        print("  3. 属性权重")
        print("  4. 难度配置")
        print("  0. 取消")
        choice = input("  请选择：").strip()

        if choice == "1":
            biome = self._input_choice("  新 Biome", VALID_BIOMES)
            if biome is not None:
                expedition.biome = biome
        elif choice == "2":
            trait = self._input_choice("  新 Trait", VALID_TRAITS)
            if trait is not None:
                expedition.trait = trait
        elif choice == "3":
            print("  输入各属性新权重：")
            for stat in STAT_NAMES:
                val = self._input_float(
                    f"    {stat} (当前 {expedition.weights.get(stat, 0.0)})：",
                    min_val=0.0
                )
                if val is None:
                    return
                expedition.weights[stat] = val
        elif choice == "4":
            difficulties = self._input_difficulties()
            if difficulties is None:
                return
            expedition.difficulties = difficulties
        elif choice == "0":
            return
        else:
            print("  ⚠ 无效输入")
            return

        try:
            self.dm.update_expedition(name, expedition)
            print(f"  ✓ Expedition「{name}」已更新")
        except ValueError as e:
            print(f"  ⚠ {e}")

    def _delete(self):
        print()
        name = input("  输入要删除的 Expedition 名称：").strip()
        confirm = input(f"  确认删除「{name}」？(y/n)：").strip().lower()
        if confirm != "y":
            print("  已取消")
            return
        try:
            self.dm.delete_expedition(name)
            print(f"  ✓ Expedition「{name}」已删除")
        except KeyError as e:
            print(f"  ⚠ {e}")

    def _input_difficulties(self) -> dict[int, tuple[float, int]] | None:
        print("  输入难度配置（最多5个难度，输入 0 结束）：")
        difficulties = {}
        for rank in range(1, 6):
            print(f"  难度 {rank}（直接回车跳过）：")
            raw = input(f"    需求分数：").strip()
            if not raw:
                break
            try:
                required_score = float(raw)
            except ValueError:
                print("  ⚠ 请输入数字")
                return None
            exp = self._input_int(f"    经验奖励：", min_val=0)
            if exp is None:
                return None
            difficulties[rank] = (required_score, exp)
        if not difficulties:
            print("  ⚠ 至少需要一个难度")
            return None
        return difficulties

    # ── 输入辅助

    def _print_header(self):
        print()
        print("─" * 50)
        print("  Expedition 管理")
        print("─" * 50)

    def _input_int(self, prompt: str, min_val: int = 0) -> int | None:
        try:
            val = int(input(prompt).strip())
            if val < min_val:
                print(f"  ⚠ 值必须 ≥ {min_val}")
                return None
            return val
        except ValueError:
            print("  ⚠ 请输入整数")
            return None

    def _input_float(self, prompt: str, min_val: float = 0.0) -> float | None:
        try:
            val = float(input(prompt).strip())
            if val < min_val:
                print(f"  ⚠ 值必须 ≥ {min_val}")
                return None
            return val
        except ValueError:
            print("  ⚠ 请输入数字")
            return None

    def _input_choice(self, prompt: str, options: list[str]) -> str | None:
        print(f"  {prompt}：")
        for i, opt in enumerate(options, 1):
            print(f"    {i}. {opt}")
        try:
            idx = int(input("  请选择编号：").strip()) - 1
            if 0 <= idx < len(options):
                return options[idx]
            print("  ⚠ 编号超出范围")
            return None
        except ValueError:
            print("  ⚠ 请输入编号")
            return None