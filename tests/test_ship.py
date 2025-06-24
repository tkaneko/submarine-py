from submarine_py import Ship
import pytest


def test_init():
    with pytest.raises(ValueError):
        Ship('a', [0, 0])
    w = Ship('w', [1, 1])
    assert "w" == w.type
    assert 3 == w.hp
    assert [1, 1] == w.position


def test_moved():
    w = Ship("w", [1, 1])
    w.move_to([1, 2])
    assert w.position == [1, 2]


def test_damaged():
    w = Ship("w", [1, 1])
    w.deal_damage(1)
    assert w.hp == 2


def test_is_reachable():
    w = Ship("w", [0, 0])
    assert w.is_reachable([0, 4])
    assert w.is_reachable([4, 0])
    assert not w.is_reachable([1, 1])


def test_can_attack():
    w = Ship("w", [2, 2])
    assert w.in_attack_range([2, 3])
    assert w.in_attack_range([3, 1])
    assert w.in_attack_range([3, 3])
    assert not w.in_attack_range([2, 0])
