from submarine_py import Player, play_game
import json
import random
import logging


class RandomPlayer(Player):
    def __init__(self, seed=0):
        super().__init__()
        self.rng = random.Random(seed or None)

    def name(self):
        return 'random-player'

    def place_ship(self):
        '''初期配置を非復元抽出でランダムに決める．'''
        ps = self.rng.sample(self.field.squares, 3)
        return {'w': ps[0], 'c': ps[1], 's': ps[2]}

    def action(self):
        """移動か攻撃かランダムに決める．
        どれがどこへ移動するか，あるいはどこに攻撃するかもランダム．
        """
        act = self.rng.choice(["move", "attack"])

        if act == "move":
            ship = self.rng.choice(list(self.ships.values()))
            to = self.rng.choice(self.field.squares)
            while not ship.is_reachable(to) or not self.overlap(to) is None:
                to = self.rng.choice(self.field.squares)

            return json.dumps(self.move(ship.type, to))
        elif act == "attack":
            to = self.rng.choice(self.field.squares)
            while not self.in_attack_range(to):
                to = self.rng.choice(self.field.squares)

            return json.dumps(self.attack(to))


def main(host, port, seed=0):
    player = RandomPlayer(seed)
    play_game(host, port, player)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description="Sample Player for Submarine Game",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
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
    parser.add_argument(
        "--seed", type=int, default=0,
        help="Random seed of the player (0 for urandom)",
    )
    parser.add_argument(
        "--verbose", action='store_true',
        help="verbose output",
    )
    parser.add_argument(
        "--games", type=int, default=1,
        help="number of games to play (should be consistent with server)",
    )
    args = parser.parse_args()
    FORMAT = '%(asctime)s %(levelname)s %(message)s'
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(format=FORMAT, level=level, force=True)

    for _ in range(args.games):
        main(args.host, args.port, seed=args.seed)
