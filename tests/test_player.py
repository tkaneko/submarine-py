from submarine_py import Player, Field
import json


class MocPlayer(Player):
    def __init__(self, predefined_placement):
        super().__init__()
        self.placement_for_test = predefined_placement

    def place_ship(self):
        '''return the placement of ships for test.

        Note: this is only for testing purpose.  A decent player
        should consider self.field here.
        '''
        # make sure positions are valid
        for _, position in self.placement_for_test.items():
            assert self.field.passable(position)
        return self.placement_for_test

    def action(self):
        pass

    def name(self):
        return 'moc player for test'


def test_init():
    field = Field()
    p = MocPlayer({"w": [0, 0], "c": [0, 1], "s": [1, 0]})
    p.initialize(field)
    assert [0, 0] == p.ships["w"].position
    assert [0, 1] == p.ships["c"].position
    assert [1, 0] == p.ships["s"].position


def test_ships_to_json():
    field = Field()
    p = MocPlayer({"w": [0, 0], "c": [0, 1], "s": [1, 0]})
    p.initialize(field)

    assert (json.dumps({"w": [0, 0], "c": [0, 1], "s": [1, 0]})
            == p.ships_to_json())


def test_update():
    field = Field()
    p = MocPlayer({"w": [0, 0], "c": [0, 1], "s": [1, 0]})
    p.initialize(field)

    json_ = json.dumps({
        "observation": {
            "me": {
                "w": {
                    "hp": 2,
                    "position": [0, 0]
                },
                "c": {
                    "hp": 2,
                    "position": [0, 4]
                },
                "s": {
                    "hp": 1,
                    "position": [1, 0]
                }
            }
        }
    })
    p.update(json_, 'your turn')
    assert 2 == p.ships["w"].hp
    assert [0, 4] == p.ships["c"].position


def test_move():
    field = Field()
    p = MocPlayer({"w": [0, 0], "c": [0, 1], "s": [1, 0]})
    p.initialize(field)

    assert ({
        "move": {
            "ship": "w",
            "to": [0, 2]
        }
    } == p.move("w", [0, 2]))
    assert [0, 2] == p.ships["w"].position


def test_attack():
    field = Field()
    p = MocPlayer({"w": [0, 0], "c": [0, 1], "s": [1, 0]})
    p.initialize(field)

    assert {"attack": {"to": [1, 1]}} == p.attack([1, 1])


def test_overlap():
    field = Field()
    p = MocPlayer({"w": [0, 0], "c": [0, 1], "s": [1, 0]})
    p.initialize(field)

    assert p.overlap([1, 1]) is None
    assert p.ships["w"] == p.overlap([0, 0])
