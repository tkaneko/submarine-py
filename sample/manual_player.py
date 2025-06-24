from submarine_py import Player, Ship, play_game, Reporter, Field
import json
import logging


def input_position(field: Field):
    """座標の選択"""
    while True:
        x = input("x = ")
        y = input("y = ")
        try:
            position = [int(x), int(y)]
            if field.passable(position):
                return position
        except ValueError:
            pass
        print("out of field")


def input_action():
    """攻撃の入力を受け付ける．"""
    prompt = "select your action: move (m) or attack (a) ?  "
    act = None
    while act not in ["m", "a"]:
        act = input(prompt)
    return act


def input_ship(available_ships):
    """艦の選択を受け付ける．"""
    print("select your ship: "
          "warship(w), cruiser(c), or submarine(s)")

    ship = input()
    while ship not in available_ships:
        print("please input existing ship")
        ship = input("select your ship: ")

    return available_ships[ship]


def report_moved(moved):
    """移動された場合の文章を作る．"""
    if moved["distance"][0] > 0:
        arrow = ">" * moved["distance"][0]
    elif moved["distance"][0] < 0:
        arrow = "<" * (-moved["distance"][0])
    elif moved["distance"][1] > 0:
        arrow = "v" * moved["distance"][1]
    elif moved["distance"][1] < 0:
        arrow = "^" * (-moved["distance"][1])
    print(f' moved {moved["ship"]} by {arrow}')


def report_attacked(attacked):
    """攻撃した，された場合の文章を作る．"""
    msg = f' attacked {attacked["position"]}'
    if "hit" in attacked:
        msg += " hit " + attacked["hit"]
    if "near" in attacked:
        msg += " near " + str(attacked["near"])
    print(msg)


def report_observation(observation):
    """相手の艦の状態を通知する．"""
    msg = "opponent ships: "
    for type, state in observation["opponent"].items():
        msg += type + ":" + str(state["hp"]) + " "
    print(msg)


class ManualPlayer(Player):
    """操作できるプレイヤーである．"""

    def __init__(self):
        super().__init__()

    def name(self):
        return 'manual-player'

    def place_ship(self):
        """入力を受け付けて初期位置を決定する．"""
        print(Reporter.make_view(self.field, {}, False))
        msg = "please input x, y in "
        msg += f"([0, {self.field.w_size - 1}] x [0, {self.field.h_size - 1}])"
        if self.field.rock:
            msg += f' except for {self.field.rock}'
        print(msg)
        ps = {}
        for type in Ship.MAX_HPS.keys():
            print(type)
            np = input_position(self.field)
            while np in ps.values():
                input("position overlapping")
                np = input_position(self.field)
            ps[type] = np
        return ps

    def action(self):
        """行動の決定は入力による．指定不可能な座標についてはメッセージを表示し再度入力を取る．"""
        act = input_action()

        if act == "m":
            ship = input_ship(self.ships)
            to = input_position(self.field)
            while (not ship.is_reachable(to)) or self.overlap(to):
                print(f"you can't move {ship.type} {ship.position} to {to}")
                to = input_position(self.field)
            return json.dumps(self.move(ship.type, to))
        elif act == "a":
            to = input_position(self.field)
            while not self.in_attack_range(to):
                print(f"you can't attack {to}")
                to = input_position(self.field)
            return json.dumps(self.attack(to))

    def update(self, json_str, turn_info):
        """状態を更新する
        自分・相手の行動を文字で，自分のフィールドの状態をAAで表示する．
        """
        super().update(json_str, turn_info)
        c = 0 if turn_info == 'your turn' else 1
        info = self.last_msg
        self.report(info, c)
        if c == 1:              # after action by the opponent
            if "result" in info and "attacked" in info["result"]:
                self.show_field(info["result"]["attacked"]["position"])
            else:
                self.show_field()
        print()

    def report(self, info, c):
        """行動を文章で表示する．"""
        if c == 0:
            player = "you"
        else:
            player = "opponent"
        if "result" in info:
            print(player, end='')
            if "attacked" in info["result"]:
                report_attacked(info["result"]["attacked"])
            elif "moved" in info["result"]:
                report_moved(info["result"]["moved"])

        report_observation(info["observation"])

    def show_field(self, hit=None):
        """フィールドをAAで表示する．"""
        view = Reporter.make_view(
            self.field,
            {k: v.to_dict() for k, v in self.ships.items()},
            hit
        )
        print(view)


def main(host, port):
    try:
        player = ManualPlayer()
        play_game(host, port, player)
    except KeyboardInterrupt:   # e.g., received Ctrl-C
        logging.warning('interrupted by user')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description="Terminal controller for Submarine Game",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "host",
        help="Hostname of the server, e.g., localhost",
    )
    parser.add_argument(
        "port",
        type=int,
        help="Port of the server, e.g., 2000",
    )
    args = parser.parse_args()
    main(args.host, args.port)
