import argparse
import sys
import tomllib
from datetime import datetime
from pathlib import Path

from . import planner


def version_template():
    project_metadata = Path(__file__).parent.parent.joinpath("pyproject.toml")
    with open(project_metadata, mode="rb") as metadata:
        version_number = tomllib.load(metadata)["tool"]["poetry"]["version"]
    return "%(prog)s {}".format(version_number)


def create_parser():
    parser = argparse.ArgumentParser(
        prog="planner", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=version_template(),
    )
    parser.add_argument(
        "year", nargs="?", default=(datetime.now().year + 1), type=int
    )
    parser.add_argument("-y", "--yearly", action="store_true", help="年間予定表")
    parser.add_argument("-w", "--weekly", action="store_true", help="週間予定表")
    parser.add_argument("-t", "--todo", action="store_true", help="TODOリスト")
    parser.add_argument("-a", "--all", action="store_true", help="すべて")
    parser.add_argument("-R", "--rokuyo", help="六曜定義ファイル, 予定表を出力する場合必須")
    parser.add_argument("-H", "--holiday", help="国民の祝日定義ファイル, 予定表を出力する場合必須")

    return parser


if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    year = args.year

    if args.all or args.yearly or args.weekly:
        if args.rokuyo is None or args.holiday is None:
            parser.print_help()
            parser.error("六曜定義ファイル／国民の祝日定義ファイルを指定してください")
        else:
            planner.Almanac.load_rokuyo(args.rokuyo)
            planner.Almanac.load_national_holidays(args.holiday)

    if args.all or args.yearly:
        yearly_planner = planner.YearlyPlanner(year)
        yearly_planner.print("{}.pdf".format(year))

    if args.all or args.weekly:
        weekly_planner = planner.WeeklyPlanner(year)
        weekly_planner.print("{}-weekly.pdf".format(year))

    if args.all or args.todo:
        todo_list = planner.ToDoList()
        todo_list.print("todo.pdf")
