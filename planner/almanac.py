from datetime import datetime, timedelta
from enum import Enum
from importlib.resources import files

import yaml

import planner.data.conf


class BaseDayOfWeek(Enum):
    """七曜"""

    def __new__(cls, record):
        member = object.__new__(cls)
        member.number = record["number"]
        member.name_en = record["name_en"]
        member.name_en_long = record["name_en_long"]
        member.name_ja = record["name_ja"]
        member.name_ja_long = record["name_ja_long"]
        member._value_ = member.number
        if not hasattr(cls, "_choices"):
            cls._choices = {}
        cls._choices[member.number] = member.name_en_long
        return member

    def __str__(self):
        return self.name_en_long


def static_init(cls):
    if getattr(cls, "static_init", None):
        cls.static_init()
        return cls


@static_init
class Almanac:
    """暦注"""

    @classmethod
    def static_init(cls):
        DayOfWeek = BaseDayOfWeek(
            "DayOfWeek",
            [
                (day_of_week["name_en_long"], day_of_week)
                for day_of_week in yaml.safe_load(
                    open(files(planner.data.conf).joinpath("day_of_week.yml"))
                )
            ],
        )
        setattr(cls, "DayOfWeek", DayOfWeek)

    @classmethod
    def load_rokuyo(cls, file):
        with open(file, mode="r") as f:
            rokuyo = {
                date: label for date, label in [line.split() for line in f]
            }
        setattr(cls, "rokuyo", rokuyo)

    @classmethod
    def load_national_holidays(cls, file):
        with open(file, mode="r") as f:
            holidays = {
                date: label for date, label in [line.split() for line in f]
            }
        cls.add_holidays(holidays)
        setattr(cls, "holiday", holidays)

    @classmethod
    def add_holidays(cls, national_holidays):
        holidays = {}

        # 国民の祝日に燗する法律第3条2項
        days = list(national_holidays)
        for day in days:
            day_of_week = Almanac.day_of_week(day)
            if day_of_week == Almanac.DayOfWeek.Sunday:
                next_day = (
                    datetime.strptime(day, "%Y%m%d") + timedelta(days=1)
                ).strftime("%Y%m%d")
                if next_day not in days:
                    holidays[next_day] = "振替休日"

        # 国民の祝日に燗する法律第3条3項
        for index in range(0, len(days) - 1):
            day1 = datetime.strptime(days[index], "%Y%m%d")
            day3 = datetime.strptime(days[index + 1], "%Y%m%d")
            if (day3 - day1).days == 2:
                day2 = day1 + timedelta(days=1)
                day2_as_str = day2.strftime("%Y%m%d")
                if day2_as_str not in national_holidays:
                    holidays[day2_as_str] = "国民の休日"

        for day, name in holidays.items():
            national_holidays[day] = name

    @staticmethod
    def day_of_week(date):
        if type(date) is str:
            date = int(date)
        year = date // 10000
        month = (date % (year * 10000)) // 100
        day = date % (year * 10000 + month * 100)
        y = year if month in range(3, 13) else year - 1
        m = month if month in range(3, 13) else month + 12
        d = day
        C = y // 100
        Y = y % 100
        if y < 4:
            raise ValueError(
                "operation not supported. year ({}) < 4".format(y)
            )
        r = -2 * C + C // 4 if y >= 1582 else -1 * C + 5
        h = (d + (26 * (m + 1)) // 10 + Y + Y // 4 + r) % 7
        return Almanac.DayOfWeek(h)
