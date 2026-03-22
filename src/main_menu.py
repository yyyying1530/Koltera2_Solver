from data_manager import DataManager

class Mainmenu:
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager

    def run(self):
        while True:
            pass

    def run(self):
        while True:
            self._print_header()
            choice = self._main_menu()
            if choice == "1":
                pass
                # self.creature_menu.show()
            elif choice == "2":
                pass
                # self.expedition_menu.show()
            elif choice == "3":
                pass
                # self.optimize_menu.show()
            elif choice == "0":
                print("\n再见！")
                break
            else:
                self._invalid()

    def _main_menu(self) -> str:
        print("  1. Creature 管理")
        print("  2. Expedition 管理")
        print("  3. 运行优化")
        print("  0. 退出")
        print()
        return input("请选择：").strip()

    def _print_header(self):
        print()
        print("═" * 50)
        print("  Expedition Optimizer")
        print("═" * 50)

    def _invalid(self):
        print("  ⚠ 无效输入，请重新选择")