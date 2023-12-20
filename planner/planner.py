import math
from datetime import date, timedelta
from importlib.resources import files

import reportlab.rl_config
from reportlab.lib.colors import black, blue, red
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas

import planner.data.font
from planner.almanac import Almanac
from planner.coordinate import Coordinate


class Planner:
    """予定表"""

    # ミリメートル単位のページサイズ
    WIDTH, HEIGHT = [size / mm for size in landscape(A4)]

    COLUMNS_IN_PAGE = 3
    COLUMN_WIDTH = WIDTH / COLUMNS_IN_PAGE

    """ページ左右のマージン"""
    MARGIN_X = 5

    """ページ上下のマージン"""
    MARGIN_Y = 8

    def __init__(self):
        pass

    def _create_canvas(self, filename):
        pdfmetrics.registerFont(
            TTFont(
                "mplus-r",
                files(planner.data.font).joinpath("mplus-1m-regular.ttf"),
            )
        )
        pdfmetrics.registerFont(
            TTFont(
                "mplus-b",
                files(planner.data.font).joinpath("mplus-1m-bold.ttf"),
            )
        )
        return Canvas(
            filename,
            pagesize=landscape(A4),
            bottomup=1,
            pageCompression=None,
            encrypt=None,
        )

    def _fill_color_of_the_day(self, day):
        day_of_week = Almanac.day_of_week(day)
        if day_of_week == Almanac.DayOfWeek.Sunday or day in Almanac.holiday:
            color = red
        elif day_of_week == Almanac.DayOfWeek.Saturday:
            color = blue
        else:
            color = black
        return color


class WeeklyPlanner(Planner):
    """週間予定表"""

    ROWS_IN_COLUMN = 7
    SUBCOLUMNS_IN_COLUMN = 1
    SUBCOLUMNS_IN_PAGE = SUBCOLUMNS_IN_COLUMN * Planner.COLUMNS_IN_PAGE

    SUBCOLUMN_WIDTH = (
        Planner.WIDTH - 2 * Planner.MARGIN_X * Planner.COLUMNS_IN_PAGE
    ) / SUBCOLUMNS_IN_PAGE

    def __init__(self, year):
        self.year = year

        start = date(year, 1, 1)
        end = date(year, 12, 31)
        days_in_year = [
            start + timedelta(days=delta)
            for delta in range(0, (end - start).days + 1)
        ]

        months = []
        for month in range(1, 12 + 1):
            days_in_month = [day for day in days_in_year if day.month == month]
            months.append(
                [
                    month,
                    [
                        days_in_month[i : i + WeeklyPlanner.ROWS_IN_COLUMN]
                        for i in range(
                            0,
                            len(days_in_month),
                            WeeklyPlanner.ROWS_IN_COLUMN,
                        )
                    ],
                ]
            )
        self.months = months

    def __subcolumn_index_in_page(self, subcolumn_number):
        index = subcolumn_number % WeeklyPlanner.SUBCOLUMNS_IN_PAGE
        if index == 0:
            index = WeeklyPlanner.SUBCOLUMNS_IN_PAGE
        return index

    def __column_index_in_page(self, subcolumn_number):
        index = (
            math.ceil(subcolumn_number / WeeklyPlanner.SUBCOLUMNS_IN_COLUMN)
            % Planner.COLUMNS_IN_PAGE
        )
        if index == 0:
            index = Planner.COLUMNS_IN_PAGE
        return index

    def __subcolumn_origin(self, subcolumn_number):
        column_index_in_page = self.__column_index_in_page(subcolumn_number)

        x = (
            Planner.COLUMN_WIDTH * (column_index_in_page - 1)
            + Planner.MARGIN_X
        )
        y = Planner.HEIGHT - Planner.MARGIN_Y

        return (x, y)

    def __draw_column_separator(self, canvas):
        for i in range(1, Planner.COLUMNS_IN_PAGE):
            canvas.setDash(1, 2)
            canvas.line(
                ((Planner.WIDTH / Planner.COLUMNS_IN_PAGE) * i) * mm,
                0,
                ((Planner.WIDTH / Planner.COLUMNS_IN_PAGE) * i) * mm,
                self.HEIGHT * mm,
            )

    def __draw_header(self, canvas, origin, month_number):
        header = canvas.beginText()
        header.setFillColor(black)
        header.setTextOrigin(origin.x * mm, origin.y * mm)
        header.setFont("mplus-b", 12)
        header.textOut("{}".format(month_number))
        canvas.drawText(header)

    def __row_height(self, canvas_height):
        return canvas_height / WeeklyPlanner.ROWS_IN_COLUMN

    def __draw_row(self, canvas, origin, day):
        canvas.setDash(1, 1)
        canvas.setLineWidth(0.5)
        canvas.line(
            origin.x * mm,
            (origin.y - 1) * mm,
            (origin.x + WeeklyPlanner.SUBCOLUMN_WIDTH) * mm,
            (origin.y - 1) * mm,
        )

        day_as_str = day.strftime("%Y%m%d")
        rokuyo = (
            Almanac.rokuyo[day_as_str] if day_as_str in Almanac.rokuyo else ""
        )
        holiday = (
            Almanac.holiday[day_as_str]
            if day_as_str in Almanac.holiday
            else ""
        )
        day_of_week = Almanac.day_of_week(day_as_str)

        text_object = canvas.beginText()
        text_object.setTextOrigin(origin.x * mm, (origin.y + 22) * mm)
        text_object.setFont("mplus-r", 6)

        color = super()._fill_color_of_the_day(day_as_str)
        text_object.setFillColor(color)

        text_object.textOut(
            "{}({}) {} {}".format(
                day.strftime("%e"), day_of_week.name_ja, rokuyo, holiday
            )
        )
        canvas.drawText(text_object)

    def print_months(self, months, filename):
        self.__print_months(
            [m for m in self.months if m[0] in months], filename
        )

    def print_month(self, month, filename):
        self.__print_months(
            [m for m in self.months if m[0] == month], filename
        )

    def print(self, filename):
        self.__print_months(self.months, filename)

    def __print_months(self, months, filename):
        canvas = super()._create_canvas(filename)

        for month in months:
            month_number = month[0]
            for week in enumerate(month[1], start=1):
                week_number_in_month = week[0]
                days_in_week = week[1]

                subcolumn_index_in_page = self.__subcolumn_index_in_page(
                    week_number_in_month
                )

                if subcolumn_index_in_page == 1:
                    if week_number_in_month > 1:
                        canvas.showPage()
                    self.__draw_column_separator(canvas)

                x, y = self.__subcolumn_origin(week_number_in_month)

                origin = Coordinate(x, y)

                origin.move(0, -3)
                self.__draw_header(canvas, origin, month_number)

                row_height = self.__row_height(origin.y - Planner.MARGIN_Y)
                origin.move(0, -1 * row_height)

                for day in days_in_week:
                    self.__draw_row(canvas, origin, day)
                    origin.move(0, -1 * row_height)

            canvas.showPage()

        canvas.save()


class YearlyPlanner(Planner):
    """年間予定表"""

    MONTHS_IN_COLUMN = 2
    MONTHS_IN_PAGE = MONTHS_IN_COLUMN * Planner.COLUMNS_IN_PAGE
    MONTH_WIDTH = (
        Planner.WIDTH - 2 * Planner.MARGIN_X * Planner.COLUMNS_IN_PAGE
    ) / MONTHS_IN_PAGE

    def __init__(self, year):
        self.year = year
        start = date(self.year, 1, 1)
        end = date(self.year, 12, 31)
        self.days_in_year = [
            start + timedelta(days=delta)
            for delta in range(0, (end - start).days + 1)
        ]

    def print(self, filename):
        canvas = super()._create_canvas(filename)

        for month in range(1, 12 + 1):
            if month % YearlyPlanner.MONTHS_IN_PAGE == 1:
                if month > YearlyPlanner.MONTHS_IN_PAGE:
                    canvas.showPage()
                for i in range(1, Planner.COLUMNS_IN_PAGE):
                    canvas.setDash(1, 2)
                    canvas.line(
                        ((Planner.WIDTH / Planner.COLUMNS_IN_PAGE) * i) * mm,
                        0,
                        ((Planner.WIDTH / Planner.COLUMNS_IN_PAGE) * i) * mm,
                        Planner.HEIGHT * mm,
                    )

            index_in_page = (month - 1) % YearlyPlanner.MONTHS_IN_PAGE
            column_index = ((month - 1) % YearlyPlanner.MONTHS_IN_PAGE) // (
                Planner.COLUMNS_IN_PAGE - 1
            )
            index_in_column = index_in_page % YearlyPlanner.MONTHS_IN_COLUMN

            #   12   34   56   month
            #   01   23   45   index_in_page
            #   00   11   22   column_index
            #   01   01   01   index_in_column
            # +----+----+----+
            # |:##:|:##:|:##:|
            # |:##:|:##:|:##:|
            # +----+----+----+
            x = (
                (
                    2 * Planner.MARGIN_X
                    + YearlyPlanner.MONTHS_IN_COLUMN
                    * YearlyPlanner.MONTH_WIDTH
                )
                * column_index
                + Planner.MARGIN_X
                + YearlyPlanner.MONTH_WIDTH * index_in_column
            )
            y = Planner.HEIGHT - Planner.MARGIN_Y
            origin = Coordinate(x, y)

            month_label = canvas.beginText()
            month_label.setFillColor(black)
            month_label.setTextOrigin(origin.x * mm, (origin.y - 3) * mm)
            month_label.setFont("mplus-b", 12)
            month_label.textOut("{}".format(month))
            canvas.drawText(month_label)

            for day in filter(lambda d: d.month == month, self.days_in_year):
                origin.move(
                    0, -1 * (Planner.HEIGHT - Planner.MARGIN_Y * 2) / 31
                )

                canvas.setDash(1, 1)
                canvas.setLineWidth(0.5)
                canvas.line(
                    origin.x * mm,
                    (origin.y - 1) * mm,
                    (origin.x + YearlyPlanner.MONTH_WIDTH) * mm,
                    (origin.y - 1) * mm,
                )

                day_as_str = day.strftime("%Y%m%d")
                rokuyo = (
                    Almanac.rokuyo[day_as_str]
                    if day_as_str in Almanac.rokuyo
                    else ""
                )
                holiday = (
                    Almanac.holiday[day_as_str]
                    if day_as_str in Almanac.holiday
                    else ""
                )
                day_of_week = Almanac.day_of_week(day_as_str)

                text_object = canvas.beginText()
                text_object.setTextOrigin(origin.x * mm, origin.y * mm)
                text_object.setFont("mplus-r", 6)

                color = super()._fill_color_of_the_day(day_as_str)
                text_object.setFillColor(color)

                text_object.textOut(
                    "{}({}) {} {}".format(
                        day.strftime("%e"),
                        day_of_week.name_ja,
                        rokuyo,
                        holiday,
                    )
                )
                canvas.drawText(text_object)

        canvas.showPage()
        canvas.save()


class ToDoList(Planner):
    """ToDoリスト"""

    TODOS_IN_COLUMN = 31
    TODO_COLUMN_IN_COLUMN = 1
    TODO_COLUMN_IN_PAGE = TODO_COLUMN_IN_COLUMN * Planner.COLUMNS_IN_PAGE
    TODO_COLUMN_WIDTH = (
        Planner.WIDTH - Planner.MARGIN_X * Planner.COLUMNS_IN_PAGE * 2
    ) / TODO_COLUMN_IN_PAGE

    def __row_height(self, canvas_height):
        return canvas_height / ToDoList.TODOS_IN_COLUMN

    def __draw_row(self, canvas, origin):
        canvas.setDash(1, 1)
        canvas.setLineWidth(0.5)
        canvas.line(
            origin.x * mm,
            (origin.y - 1) * mm,
            (origin.x + ToDoList.TODO_COLUMN_WIDTH) * mm,
            (origin.y - 1) * mm,
        )

        text_object = canvas.beginText()
        text_object.setTextOrigin(origin.x * mm, origin.y * mm)
        text_object.setFont("mplus-r", 16)
        text_object.textOut("　｜ ｜")
        canvas.drawText(text_object)

    def print(self, filename):
        canvas = super()._create_canvas(filename)
        for todo_number in range(1, ToDoList.TODO_COLUMN_IN_PAGE * 2 + 1):
            if todo_number % ToDoList.TODO_COLUMN_IN_PAGE == 0:
                todo_index = ToDoList.TODO_COLUMN_IN_PAGE
            else:
                todo_index = todo_number % ToDoList.TODO_COLUMN_IN_PAGE

            if todo_index == 1:
                if todo_number > 1:
                    canvas.showPage()
                for i in range(1, Planner.COLUMNS_IN_PAGE):
                    canvas.setDash(1, 2)
                    canvas.line(
                        ((Planner.WIDTH / Planner.COLUMNS_IN_PAGE) * i) * mm,
                        0,
                        ((Planner.WIDTH / Planner.COLUMNS_IN_PAGE) * i) * mm,
                        Planner.HEIGHT * mm,
                    )

            x = Planner.COLUMN_WIDTH * (todo_index - 1) + Planner.MARGIN_X
            y = Planner.HEIGHT - Planner.MARGIN_Y

            origin = Coordinate(x, y)
            dy = self.__row_height(origin.y - Planner.MARGIN_Y)
            origin.move(0, -1 * dy)

            for j in range(1, ToDoList.TODOS_IN_COLUMN + 1):
                self.__draw_row(canvas, origin)
                origin.move(0, -1 * dy)

        canvas.showPage()
        canvas.save()
