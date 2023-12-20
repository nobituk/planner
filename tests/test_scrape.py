from importlib.resources import files

import pytest
from bs4 import BeautifulSoup

import planner
import tests
from planner.scrape import parse_national_holidays, parse_rokuyo


@pytest.mark.parametrize(
    "provided_input, expected_output",
    [
        (
            """
            <div class="clearfix grpelem" id="u385-732" data-sizePolicy="fixed" data-pintopage="page_fixedCenter"><!-- content -->
                <p>2023年1月1日(日)</p>
                <p>2023年1月2日(月)</p>
            </div>
            <div class="clearfix grpelem" id="u386-732" data-sizePolicy="fixed" data-pintopage="page_fixedCenter"><!-- content -->
                <p>先負</p>
                <p>仏滅</p>
            </div>""",
            {"20230101": "先負", "20230102": "仏滅"},
        )
    ],
)
def test_parse_rokuyo(provided_input, expected_output):
    actual_output = parse_rokuyo(provided_input)
    assert len(actual_output.keys()) == len(expected_output.keys())
    assert all(
        actual_output[key] == value for key, value in expected_output.items()
    )


@pytest.mark.parametrize(
    "provided_input_file, expected_output_file",
    [
        (
            files(tests).joinpath("data/rokuyo_2023.html"),
            files(tests).joinpath("data/rokuyo-2023.txt"),
        ),
        (
            files(tests).joinpath("data/rokuyo_2024.html"),
            files(tests).joinpath("data/rokuyo-2024.txt"),
        ),
    ],
)
def test_parse_rokuyo_html(provided_input_file, expected_output_file):
    with open(provided_input_file, "r") as f:
        provided_input = f.read()

    expected_output = {}
    with open(expected_output_file, "r") as f:
        for line in f:
            day, name = line.split()
            expected_output[day] = name

    actual_output = parse_rokuyo(provided_input)
    assert len(actual_output.keys()) == len(set(actual_output.keys()))
    assert len(actual_output.keys()) == len(expected_output.keys())
    assert set(actual_output.keys()) == set(expected_output.keys())
    for day, name in actual_output.items():
        assert expected_output[day] == name


@pytest.mark.parametrize(
    "provided_input, expected_output",
    [
        (
            (
                2009,
                """
                <table class="table--default  table--solid-line table--striped">
                <tr>
                   <td>敬老の日</td><td>9月21日</td>
                </tr>
                <tr>
                   <td>秋分の日</td><td>9月23日</td>
                </tr>
                </table>""",
            ),
            {"20090921": "敬老の日", "20090923": "秋分の日"},
        )
    ],
)
def test_parse_national_holidays(provided_input, expected_output):
    year = provided_input[0]
    data = provided_input[1]
    actual_output = parse_national_holidays(year, data)
    assert len(actual_output.keys()) == len(expected_output.keys())
    assert all(
        actual_output[key] == value for key, value in expected_output.items()
    )


@pytest.mark.parametrize(
    "provided_input, expected_output",
    [
        (
            (2023, files(tests).joinpath("data/20220201-rekiyoko.html")),
            {
                "20230101": "元日",
                "20230109": "成人の日",
                "20230211": "建国記念の日",
                "20230223": "天皇誕生日",
                "20230321": "春分の日",
                "20230429": "昭和の日",
                "20230503": "憲法記念日",
                "20230504": "みどりの日",
                "20230505": "こどもの日",
                "20230717": "海の日",
                "20230811": "山の日",
                "20230918": "敬老の日",
                "20230923": "秋分の日",
                "20231009": "スポーツの日",
                "20231103": "文化の日",
                "20231123": "勤労感謝の日",
            },
        ),
        (
            (2024, files(tests).joinpath("data/20230201-rekiyoko.html")),
            {
                "20240101": "元日",
                "20240108": "成人の日",
                "20240211": "建国記念の日",
                "20240223": "天皇誕生日",
                "20240320": "春分の日",
                "20240429": "昭和の日",
                "20240503": "憲法記念日",
                "20240504": "みどりの日",
                "20240505": "こどもの日",
                "20240715": "海の日",
                "20240811": "山の日",
                "20240916": "敬老の日",
                "20240922": "秋分の日",
                "20241014": "スポーツの日",
                "20241103": "文化の日",
                "20241123": "勤労感謝の日",
            },
        ),
    ],
)
def test_parse_national_holidays_html(provided_input, expected_output):
    year = provided_input[0]
    file = provided_input[1]
    with open(file, "r") as f:
        data = f.read()
    actual_output = parse_national_holidays(year, data)
    assert len(actual_output.keys()) == len(set(actual_output.keys()))
    assert len(actual_output.keys()) == len(expected_output.keys())
    assert set(actual_output.keys()) == set(expected_output.keys())
    for day, name in actual_output.items():
        assert expected_output[day] == name
