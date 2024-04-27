import csv
import re
from datetime import datetime
from urllib import request
from urllib.error import HTTPError

from bs4 import BeautifulSoup


def download_html(url):
    try:
        response = request.urlopen(url)
        return response.read()
    except HTTPError:
        return None


def download_national_holidays(year):
    url = "https://www.nao.ac.jp/news/topics/{year}/{year}0201-rekiyoko.html".format(
        year=year - 1
    )
    return download_html(url)


def download_rokuyo(year):
    url = "https://www.genkibox.com/rokuyo/rokuyo_{}.html".format(year)
    return download_html(url)


def rokuyo_tag(tag):
    # html tags and attributes are case insensitive
    # https://html.spec.whatwg.org/multipage/syntax.html#writing
    return (
        tag.name == "div"
        and set(("grpelem", "clearfix")) == set(tag.attrs.get("class"))
        and tag.attrs.get("data-sizepolicy") == "fixed"
    )


def parse_rokuyo(data):
    soup = BeautifulSoup(data, "html.parser")
    divs = soup.find_all(rokuyo_tag)
    if not divs or len(divs) != 2:
        return None

    rows = divs[0].findChildren("p")
    if not rows:
        return None

    days = []
    for row in rows:
        match = re.search("([0-9]{4})年([0-9]{1,2})月([0-9]{1,2})日", row.text)
        if match.groups() and len(match.groups()) == 3:
            year = match.group(1)
            month = match.group(2)
            day = match.group(3)
            ymd = "{year}{month}{day}".format(
                year=year.zfill(4), month=month.zfill(2), day=day.zfill(2)
            )
            days.append(ymd)

    rows = divs[1].findChildren("p")
    if not rows:
        return None

    names = []
    for row in rows:
        names.append(row.text)

    if len(days) != len(names):
        return None

    rokuyo = {}
    for day, name in zip(days, names):
        rokuyo[day] = name

    return rokuyo


class NationalHolidayParser:
    def parse(self, year, data):
        pass


class NationalHolidayCaoParser(NationalHolidayParser):
    def parse(self, year, data):
        national_holidays = {}
        for col1, col2 in csv.reader(data):
            if col1 != "国民の祝日・休日月日":
                date = datetime.strptime(col1, "%Y/%m/%d")
                if date.year == year:
                    ymd = date.strftime("%Y%m%d")
                    national_holidays[ymd] = col2
        return national_holidays


class NationalHolidayNaojParser(NationalHolidayParser):
    def parse(self, year, data):
        soup = BeautifulSoup(data, "html.parser")

        table = soup.find("table", {"class": "table--default"})
        if not table:
            return None
        rows = table.findChildren("tr", recursive=False)

        if not rows:
            return None

        national_holidays = {}
        for row in rows:
            columns = row.findChildren("td", recursive=False)
            name = columns[0].text
            date = columns[1].text
            match = re.search("([0-9]{1,})月([0-9]{1,})日", date)
            if match.groups() and len(match.groups()) == 2:
                month = match.group(1)
                if len(month) == 1:
                    month = "0" + month
                day = match.group(2)
                if len(day) == 1:
                    day = "0" + day
                ymd = "{}{}{}".format(year, month, day)
                national_holidays[ymd] = name
            else:
                return None
        return national_holidays


def parse_national_holidays(parser, year, data):
    return parser.parse(year, data)
