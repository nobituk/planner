import pytest

from planner.coordinate import Coordinate


def test_move():
    coordinate = Coordinate(0, 0)
    coordinate.move(1, 1)
    assert coordinate.x == 1
    assert coordinate.y == 1


def test_str():
    coordinate = Coordinate(0, 0)
    assert str(coordinate) == "(0, 0)"


def test_repr():
    coordinate = Coordinate(0, 0)
    assert repr(coordinate) == "Coordinate(0, 0)"
