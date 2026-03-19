from data_manager import DataManager
from cli import CLI


def main():
    data_manager = DataManager(
        creatures_path="data/Creature.csv",
        expedition_path="data/Expedition.csv",
    )
    data_manager.load()

    cli = CLI(data_manager=data_manager)
    cli.run()


if __name__ == "__main__":
    main()