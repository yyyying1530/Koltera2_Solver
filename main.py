from src.data_manager import DataManager
from src.main_menu import Mainmenu

def main():
    data_manager = DataManager(
        creatures_path = "data/Creature.csv",
        expedition_path = "data/Expedition.csv",
    )
    data_manager.load()
    mainmenu = Mainmenu(data_manager)
    mainmenu.run()

if __name__ == '__main__':
    main()