import pytest

import planner
from planner.almanac import Almanac


@pytest.mark.parametrize(
    "provided_input, expected_output",
    [
        (
            {"20090921": "勤労感謝の日", "20090923": "秋分の日"},
            {"20090921": "勤労感謝の日", "20090923": "秋分の日", "20090922": "国民の休日"},
        ),
        (
            {"20230101": "元日"},
            {"20230101": "元日", "20230102": "振替休日"},
        ),
    ],
)
def test_add_holidays(provided_input, expected_output):
    Almanac.add_holidays(provided_input)
    assert len(provided_input.keys()) == len(expected_output.keys())
    assert all(
        expected_output[key] == value for key, value in provided_input.items()
    )
