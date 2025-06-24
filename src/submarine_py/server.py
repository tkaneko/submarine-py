from .ship import Ship
from .field import Reporter, Field
from .protocol import Protocol
import socket
import json
import logging
import collections


class Client:
    """プレイヤーを表すクラスである．艦を複数保持している．"""

    def __init__(self, field: Field, positions):
        """艦種ごとに座標を与えられるので，Shipオブジェクトを作成し，連想配列に加える．
        艦のtypeがkeyになる．
        """
        self.ships = {}
        self.field = field
        for type, position in positions.items():
            if self.overlap(position):
                raise ValueError("overlapping positions")
            if not self.field.passable(position):
                raise ValueError(f"position {position} out of field")
            self.ships[type] = Ship(type, position)

    def move(self, type, to):
        """艦が座標に移動可能か確かめてから移動させる．相手プレイヤーに渡す情報を連想配列で返す．

        反則の場合は False を返す
        """
        ship = self.ships[type]

        if not ship or not self.field.passable(to) \
           or not ship.is_reachable(to) or self.overlap(to):
            return False

        offset = [to[0] - ship.position[0], to[1] - ship.position[1]]
        ship.move_to(to)
        return {"ship": type, "distance": offset}

    def attacked(self, to):
        """攻撃された時の処理．攻撃を受けた艦，あるいは周囲1マスにいる艦を調べ，状態を更新する．
        相手プレイヤーに渡す情報を連想配列で返す．
        """
        if not self.field.passable(to):
            return False

        info = {"position": to}
        ship = self.overlap(to)
        near = self.near(to)

        if ship:
            ship.deal_damage(1)
            info["hit"] = ship.type

            if ship.hp == 0:
                del self.ships[ship.type]

        info["near"] = [s.type for s in near]
        return info

    def observation(self, me):
        """艦の座標とHPを返す．meで自分かどうかを判定し，違うならpositionは教えない．"""
        cond = {}
        for ship in self.ships.values():
            cond[ship.type] = {"hp": ship.hp}
            if me:
                cond[ship.type]["position"] = ship.position
        return cond

    def in_attack_range(self, to):
        """艦隊の攻撃可能な範囲かどうかを返す．"""
        return (
            self.field.passable(to)
            and any([ship.in_attack_range(to)
                     for ship in self.ships.values()])
        )

    def overlap(self, position):
        """与えられた座標にいる艦を返す．"""
        for ship in self.ships.values():
            if ship.position == position:
                return ship
        return None

    def near(self, to):
        """与えられた座標の周り1マスにいる艦を配列で返す．"""
        near = []
        for ship in self.ships.values():
            if ship.position != to and ship.in_attack_range(to):
                near.append(ship)
        return near


class GameControl:
    """Gameの処理を行うクラスである．プレイヤー2人を保持している．

    self.cliernts はプレイヤーの配列で
    行動プレイヤーのインデックスをc in {0, 1} とすると
    プレイヤーが2人であるという前提なので， 待機プレイヤーのインデックスは1-cである．
    """
    def __init__(self, field):
        self.field = field
        self.clients = None

    def initialize(self, json1, json2):
        self.clients = [
            Client(self.field, json.loads(json1)),
            Client(self.field, json.loads(json2))
        ]

    def initial_condition(self, c):
        """初期配置をJSONで返す．"""
        return [
            json.dumps(self.observation(c)),
            json.dumps(self.observation(1-c))
        ]

    def action(self, c, json_msg):
        """
        可能かどうかチェックしてから攻撃，あるいは移動の処理を行い，両プレイヤーに結果を通知するJSONを作る．
        JSONの配列を返す．0番目の要素が行動プレイヤー宛，1番目の要素が待機プレイヤー宛である．
        """
        info = [{}, {}]
        active = self.clients[c]
        passive = self.clients[1-c]
        act = json.loads(json_msg)

        if "attack" in act:
            to = act["attack"]["to"]

            if not active.in_attack_range(to):
                result = False
            else:
                result = passive.attacked(to)

            info[c]["result"] = {"attacked": result}
            info[1-c]["result"] = {"attacked": result}

            if not passive.ships:
                info[c]["outcome"] = True
                info[1-c]["outcome"] = False

        elif "move" in act:
            result = active.move(act["move"]["ship"], act["move"]["to"])
            info[1-c]["result"] = {"moved": result}

        if not result:
            info[c]["outcome"] = False
            info[1-c]["outcome"] = True

        info[c].update(self.observation(c))
        info[1-c].update(self.observation(1-c))

        return [json.dumps(info[c]), json.dumps(info[1-c])]

    def observation(self, c):
        """自分と相手の状態を連想配列で返す．"""
        return {
            "observation": {
                "me": self.clients[c].observation(True),
                "opponent": self.clients[1-c].observation(False)
            }
        }


def step(time, active, passive, c, game, *, quiet):
    """
    プレイヤーの行動をソケットから取得して処理し，結果を通知する．
    勝利したプレイヤーを返す．勝敗が決していない時は-1を返す．
    """
    # (5a) notify player to move
    print("your turn", file=active)
    print("waiting", file=passive)
    # (5b) recieve action
    act = active.readline().rstrip()
    if not act:
        logging.error(f'client disconnected at time {time}')
        logging.error('aborted')
        exit(1)
    logging.debug(f"action {time=} player={c+1} {act}")
    results = game.action(c, act)
    logging.debug(f"{results[0]=} {results[1]=}")
    if not quiet:
        Reporter.report_field(game.field, results, c)
    # (5c) notify results
    print(results[0], file=active)
    print(results[1], file=passive)

    if "outcome" in json.loads(results[0]):
        return c if json.loads(results[0])["outcome"] else 1 - c
    return -1


def play_game(field, clients, *, quiet):
    """play one game to return winner (-1 for draw)"""
    # (2a) receive name from each client
    names = [cl.readline().rstrip() for cl in clients]
    logging.info(f'start game for {names}')
    game = GameControl(field)
    # (3) send field information to both clients
    field_rep = field.to_json()
    logging.debug(f'>> {field_rep}')
    for cl in clients:
        print(field_rep, file=cl)
    # (4) receive initial ship placement
    ships = [cl.readline() for cl in clients]
    logging.debug(f'<< {ships}')
    try:
        game.initialize(*ships)
    except ValueError as e:
        logging.error(f'error in initial ship placement {e}')
        exit(1)

    # (5) main loop of game
    t = 0
    limit = 10000
    c = 0                       # turn to move
    if not quiet:
        Reporter.report_field(field, game.initial_condition(c), c)
    winner = -1
    while winner == -1 and t < limit:
        winner = step(t+1, clients[c], clients[1-c], c, game, quiet=quiet)
        c = 1 - c
        t += 1

    # (6) game ends
    if winner == -1:
        for client in clients:
            print(Protocol.draw, file=client)
        logging.info("draw")
    else:
        print(Protocol.you_win, file=clients[winner])
        print(Protocol.you_lose, file=clients[1-winner])
        logging.info(f"player {1+winner} {names[winner]} win")
    return winner, names[winner]


def server_main(host: str, port: int, games: int, field: Field, *, quiet):
    listen_addr = (host, port)
    win_count = collections.Counter()
    with socket.create_server(listen_addr, reuse_port=True) as s:
        # (1) server started
        for g in range(games):
            logging.info(f'waiting client players at {host}:{port}')
            clients, addrs = [], []
            for i in range(2):
                conn, addr = s.accept()
                logging.info(f'player {i+1} from {addr}')
                c = conn.makefile(mode='rw', buffering=1)
                # (2a) server -> client: greeting
                logging.debug(f'> {Protocol.greeting}')
                print(Protocol.greeting, file=c)
                clients.append(c)
                addrs.append(addr)
            # (2b), (3) - (6)
            winner, name = play_game(field, clients, quiet=quiet)
            for client in clients:
                client.close()
            if winner >= 0:
                id = f'{name}@{addrs[winner][0]}'
                win_count[id] += 1
    if games > 1:
        for name, wins in win_count.items():
            print(f'{name} win {wins} time(s)')
