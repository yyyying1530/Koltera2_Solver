from example.data_manager import DataManager
from example.models import Creature
from example.config import VALID_TYPES, VALID_TRAITS, STAT_NAMES


class CreatureMenu:

    def __init__(self, data_manager: DataManager):
        self.dm = data_manager

    def show(self):
        while True:
            self._print_header()
            print("  1. 查看所有 Creature")
            print("  2. 新增 Creature")
            print("  3. 编辑 Creature")
            print("  4. 删除 Creature")
            print("  5. 快捷升级")
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
            elif choice == "5":
                self._level_up()
            elif choice == "0":
                break
            else:
                print("  ⚠ 无效输入")

    def _list(self):
        print()
        creatures = self.dm.creatures
        if not creatures:
            print("  （暂无 Creature）")
            return
        print(f"  {'名称':<16} {'等级':>4} {'类型':<8} {'Trait':<22} {'属性'}")
        print("  " + "─" * 80)
        for c in creatures:
            stats = c.actual_stats()
            stat_str = "  ".join(f"{s}={v:.0f}" for s, v in stats.items())
            print(f"  {c.name:<16} {c.level:>4} {c.creature_type:<8} {c.trait:<22} {stat_str}")
        print()

    def _add(self):
        print()
        print("  ── 新增 Creature ──")
        name = input("  名称：").strip()
        if not name:
            print("  ⚠ 名称不能为空")
            return

        level = self._input_int("  等级：", min_val=1)
        if level is None:
            return

        creature_type = self._input_choice("  类型", VALID_TYPES)
        if creature_type is None:
            return

        trait = self._input_choice("  Trait", VALID_TRAITS)
        if trait is None:
            return

        print("  输入各属性基础值（一级时的数值）：")
        base_stats = {}
        for stat in STAT_NAMES:
            val = self._input_float(f"    {stat}：", min_val=0)
            if val is None:
                return
            base_stats[stat] = val

        creature = Creature(
            name=name,
            level=level,
            creature_type=creature_type,
            trait=trait,
            base_stats=base_stats,
        )

        try:
            self.dm.add_creature(creature)
            print(f"  ✓ Creature「{name}」已添加")
        except ValueError as e:
            print(f"  ⚠ {e}")

    def _edit(self):
        print()
        name = input("  输入要编辑的 Creature 名称：").strip()
        try:
            creature = self.dm.get_creature(name)
        except KeyError as e:
            print(f"  ⚠ {e}")
            return

        print()
        print("  选择要修改的字段：")
        print("  1. 等级")
        print("  2. 类型")
        print("  3. Trait")
        print("  4. 基础属性")
        print("  0. 取消")
        choice = input("  请选择：").strip()

        if choice == "1":
            level = self._input_int("  新等级：", min_val=1)
            if level is not None:
                creature.level = level
        elif choice == "2":
            creature_type = self._input_choice("  新类型", VALID_TYPES)
            if creature_type is not None:
                creature.creature_type = creature_type
        elif choice == "3":
            trait = self._input_choice("  新 Trait", VALID_TRAITS)
            if trait is not None:
                creature.trait = trait
        elif choice == "4":
            print("  输入各属性新基础值：")
            for stat in STAT_NAMES:
                val = self._input_float(f"    {stat} (当前 {creature.base_stats.get(stat, 0)})：", min_val=0)
                if val is None:
                    return
                creature.base_stats[stat] = val
        elif choice == "0":
            return
        else:
            print("  ⚠ 无效输入")
            return

        try:
            self.dm.update_creature(name, creature)
            print(f"  ✓ Creature「{name}」已更新")
        except ValueError as e:
            print(f"  ⚠ {e}")

    def _delete(self):
        print()
        name = input("  输入要删除的 Creature 名称：").strip()
        confirm = input(f"  确认删除「{name}」？(y/n)：").strip().lower()
        if confirm != "y":
            print("  已取消")
            return
        try:
            self.dm.delete_creature(name)
            print(f"  ✓ Creature「{name}」已删除")
        except KeyError as e:
            print(f"  ⚠ {e}")

    def _level_up(self):
        print()
        name = input("  输入 Creature 名称：").strip()
        try:
            creature = self.dm.get_creature(name)
        except KeyError as e:
            print(f"  ⚠ {e}")
            return

        new_level = self._input_int(f"  新等级（当前 {creature.level}）：", min_val=1)
        if new_level is None:
            return

        creature.level = new_level
        try:
            self.dm.update_creature(name, creature)
            print(f"  ✓「{name}」等级已更新为 {new_level}")
        except ValueError as e:
            print(f"  ⚠ {e}")

    # ── 输入辅助

    def _print_header(self):
        print()
        print("─" * 50)
        print("  Creature 管理")
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