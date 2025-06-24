from submarine_py import Field
import pytest


def test_field():
    field = Field()
    assert field.passable([0, 0])
    assert not field.passable([5, 5])
    assert not field.passable([-1, 0])


def test_rect():
    field = Field(2, 3)         # h, w
    for sq in field.squares:
        assert field.passable(sq)


def test_rock():
    field = Field(3, 2, [[0, 0]])
    assert not field.passable([0, 0])
    assert len(field.squares) == 5

    field = Field(3, 2, [[0, 0], [1, 2]])
    assert not field.passable([0, 0])
    assert not field.passable([1, 2])
    assert len(field.squares) == 4

    with pytest.raises(ValueError):
        _ = Field(3, 2, [0, 0])
