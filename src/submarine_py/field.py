import json
import tabulate


class Field:
    """Map of a game"""
    def __init__(self, h_size: int = 5, w_size: int = 5, rock=[]):
        self.h_size = h_size
        self.w_size = w_size
        self.rock = rock
        if len(rock) > 0:
            if (not isinstance(rock[0], list)) or len(rock[0]) != 2:
                raise ValueError('expects list of x,y pairs for rock')
        self.positions = [
            [i, j] for i in range(self.w_size) for j in range(self.h_size)
            if [i, j] not in rock
        ]

    @property
    def width(self):
        """return width where x in [0, width-1] is valid

        >>> field = Field(2, 3)
        >>> field.width
        3
        """
        return self.w_size

    @property
    def height(self):
        """return height where y in [0, height-1] is valid

        >>> field = Field(2, 3)
        >>> field.height
        2
        """
        return self.h_size

    @property
    def squares(self):
        """return passable location as list of (x, y) positions

        >>> field = Field(2, 3)
        >>> field.squares
        [[0, 0], [0, 1], [1, 0], [1, 1], [2, 0], [2, 1]]
        """
        return self.positions

    def passable(self, position):
        """与えられた座標に船を移動/配置可能である．

        >>> field = Field(2, 2)
        >>> field.passable([0, 1])
        True
        >>> field.passable([1, 2])
        False
        >>> field_with_rock_at_zerozero = Field(3, 2, [[0, 0]])
        >>> field_with_rock_at_zerozero.passable([0, 0])
        False
        """
        return position in self.positions

    def to_ascii(self):
        '''return ascii representation for handy printing

        >>> field = Field(2, 3)
        >>> print(field.to_ascii())
        ___
        ___
        >>> field = Field(3, 2, [[0, 0]])
        >>> print(field.to_ascii())
        *_
        __
        __
        '''
        rep = []
        for y in range(self.height):
            line = ''
            for x in range(self.width):
                sq = '_' if self.passable([x, y]) else '*'
                line += sq
            rep.append(line)
        return '\n'.join(rep)

    def to_json(self):
        return json.dumps({
            'height': self.height,
            'width': self.width,
            'rock': self.rock
        })

    @staticmethod
    def from_json(msg):
        data = json.loads(msg)
        return Field(data['height'], data['width'], data['rock'])


class Reporter:
    """処理結果をターミナルにわかりやすく出力するためのモジュール．"""

    @staticmethod
    def report_result(results, c):
        """結果を文章で通知する．現在未使用．"""
        result1 = json.loads(results[0])
        result2 = json.loads(results[1])

        if "moved" in result2["result"]:
            if result2["result"]["moved"]:
                print("player" + (c+1)
                      + " moved " + result2["result"]["moved"]["ship"]
                      + " by " + result2["result"]["moved"]["distance"])
            else:
                print("player " + (c+1) + " faild to move")
        else:
            if result2["result"]["attacked"]:
                print("player" + (c+1)
                      + " attacked "
                      + result2["result"]["attacked"]["position"])

                if "hit" in result2["result"]["attacked"]:
                    print("hit " + result2["result"]["attacked"]["hit"])
                if "near" in result2["result"]["attacked"]:
                    print("near " + result2["result"]["attacked"]["near"])
            else:
                print("player" + (c+1).to_s + " faild to attack")

        if c == 0:
            print("player" + (c+1) + ": " + result1["observation"]["me"])
            print("player" + (2-c) + ": " + result2["observation"]["me"])
        else:
            print("player" + (2-c) + ": " + result2["observation"]["me"])
            print("player" + (c+1) + ": " + result1["observation"]["me"])
        print()

    def make_view(field, fleets, attacked) -> str:
        """convert field to string"""
        ascii = field.to_ascii().replace('_', ' ')
        table = [list(line) for line in ascii.split('\n')]
        if attacked:
            x, y = attacked
            table[y][x] = '!'
        for type, ship in fleets.items():
            x, y = ship['position']
            table[y][x] += f'{type}{ship["hp"]}'
        header = range(field.width)
        view = tabulate.tabulate(
            table, header, tablefmt="simple_grid", showindex="always",
            stralign='center'
        )
        return view

    def report_field(field, result, c):
        results = [json.loads(result[0]), json.loads(result[1])]
        fleets = [results[c]["observation"]["me"],
                  results[1-c]["observation"]["me"]]
        attacked = None
        if "result" in result[1] and "attacked" in results[1]["result"]:
            attacked = results[1]["result"]["attacked"]["position"]
        views = [
            Reporter.make_view(field, fleets[0], (c == 1) and attacked),
            Reporter.make_view(field, fleets[1], (c == 0) and attacked),
        ]
        lines = [_.split('\n') for _ in views]
        for left, right in zip(*lines):
            print(left, right)
