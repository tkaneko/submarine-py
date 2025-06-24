from submarine_py import Client, Field
import pytest


def test_init():
    field = Field()

    with pytest.raises(ValueError):
        _ = Client(field, {"w": [0, 0],  "c": [0, 1],  "s": [0, 0]})

    with pytest.raises(ValueError):
        _ = Client(field, {"w": [5, 0],  "c": [0, 1],  "s": [0, 0]})

    c = Client(field, {"w": [0, 0],  "c": [0, 1],  "s": [1, 0]})
    assert [0, 0] == c.ships["w"].position
    assert [0, 1] == c.ships["c"].position
    assert [1, 0] == c.ships["s"].position


def test_client_move():
    field = Field()

    c = Client(field, {"w": [0, 0],  "c": [0, 1],  "s": [1, 0]})
    with pytest.raises(KeyError):
        c.move("a", [1, 1])
    assert not c.move("w", [5, 5])
    assert not c.move("w", [0, 1])
    assert not c.move("w", [1, 1])
    assert {"ship": "w",  "distance": [0,  2]} == c.move("w",  [0, 2])
    assert [0, 2] == c.ships["w"].position


def test_client_attacked():
    field = Field()

    c = Client(field, {"w": [0, 0],  "c": [0, 1],  "s": [1, 0]})
    assert not c.attacked([5, 5])
    assert ({
        "position": [2, 2],
        "near": []
    } == c.attacked([2, 2]))
    assert ({
        "position": [0, 0],
        "hit": "w",
        "near": ["c",  "s"]
    } == c.attacked([0, 0]))
    assert 2 == c.ships["w"].hp
    assert ({
        "position": [1, 0],
        "hit": "s",
        "near": ["w",  "c"]
    } == c.attacked([1, 0]))
    assert "s" not in c.ships


def test_client_observation():
    field = Field()

    c = Client(field, {"w": [0, 0], "c": [0, 1], "s": [1, 0]})
    assert ({
        "w": {
            "hp": 3,
            "position": [0, 0]
        },
        "c": {
            "hp": 2,
            "position": [0, 1]
        },
        "s": {
            "hp": 1,
            "position": [1, 0]
        }
    } == c.observation(True))
    assert ({
        "w": {
            "hp": 3
        },
        "c": {
            "hp": 2
        },
        "s": {
            "hp": 1
        }
    } == c.observation(False))


def test_client_overlap():
    field = Field()

    c = Client(field, {"w": [0, 0], "c": [0, 1], "s": [1, 0]})
    assert c.overlap([1, 1]) is None
    assert c.ships["w"] == c.overlap([0, 0])


def test_client_near():
    field = Field()

    c = Client(field, {"w": [0, 0], "c": [0, 1], "s": [1, 0]})
    assert c.near([2, 2]) == []
    assert c.ships["c"], c.near([0, 2])
