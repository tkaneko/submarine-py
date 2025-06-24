from .ship import Ship
from .field import Field
from .protocol import Protocol
import json
import abc
import logging


class Player(abc.ABC):
    """プレイヤーを表すクラスである．艦を複数保持している．

    Typical sequence:
    - make a (subclass of) Player object
    - call initialize(field).
      - self.field is set
      - self.place_ship() is internally called
      - self.ships is set
    - play a game
    """

    def __init__(self):
        '''construct a player.

        Actual initialization is postponed until initialize(field) is called.
        '''
        self.field = None
        self.ships = {}
        self.last_msg = None

    def initialize(self, field: Field):
        '''
        艦種ごとに座標を subclass で決め，Shipオブジェクトを作成し，連想配列で保持する．
        艦のtypeがkeyになる．
        '''
        self.field = field
        logging.debug(f'field is \n{field.to_ascii()}')
        positions = self.place_ship()
        logging.debug(f'place ships at {positions}')
        self.ships = {ship_type: Ship(ship_type, position)
                      for ship_type, position in positions.items()}

    def ships_to_json(self):
        '''船の状態をJSONで返す．'''
        cond = {ship.type: ship.position for ship in self.ships.values()}
        return json.dumps(cond)

    @abc.abstractmethod
    def action(self) -> str:
        '''行動を表す json を返す．

        行動を決定するアルゴリズムはサブクラスで記述する．
        self.field は設定済み，self.ships, self.last_msg は最新の状況に更新済み
        '''
        pass

    @abc.abstractmethod
    def name(self) -> str:
        '''return player's name

        Note: might be called before initialize()
        '''
        pass

    @abc.abstractmethod
    def place_ship(self) -> dict:
        '''船を配置をdict で返す．

        アルゴリズムはサブクラスで記述する．
        self.field は設定済み
        '''
        pass

    def update(self, json_, info):
        '''通知された情報で艦の状態を更新する．'''
        self.last_msg = json.loads(json_)
        status = self.last_msg['observation']['me']
        for ship_type in list(self.ships):
            if ship_type not in status:
                self.ships.pop(ship_type)
            else:
                self.ships[ship_type].hp = status[ship_type]['hp']
                self.ships[ship_type].position = status[ship_type]['position']

    def move(self, ship_type, to):
        '''移動の処理を行い，連想配列で結果を返す．'''
        ship = self.ships[ship_type]
        ship.move_to(to)
        return {
            "move": {
                "ship": ship_type,
                "to": to
            }
        }

    def attack(self, to):
        '''攻撃の処理を行い，連想配列で結果を返す．'''
        return {
            "attack": {
                "to": to
            }
        }

    def in_attack_range(self, to):
        '''艦隊の攻撃可能な範囲か判定を返す．'''
        return self.in_field(to)\
            and any([ship.in_attack_range(to) for ship in self.ships.values()])

    def in_field(self, position):
        '''与えられた座標がフィールドないかどうかを返す．'''
        return (
            0 <= position[0] < self.field.width
            and 0 <= position[1] < self.field.height
        )

    def overlap(self, position):
        '''与えられた座標にいる艦を返す．'''
        for ship in self.ships.values():
            if ship.position == position:
                return ship
        return None


def play_game(host: str, port: int, player: Player):
    """仕様に従ってサーバとソケット通信を行う．"""
    import socket
    import logging
    assert isinstance(host, str) and isinstance(port, int)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, port))
        with sock.makefile(mode='rw', buffering=1) as sockfile:
            # (2a) receive greeting from the server
            greeting = sockfile.readline().rstrip()
            logging.debug(f'< {greeting}')
            assert greeting == Protocol.greeting
            logging.info(f'connect to server with name {player.name()}')
            # (2b) send its name to the server
            sockfile.write(player.name()+'\n')

            # (3) receive filed information
            field = sockfile.readline()
            player.initialize(Field.from_json(field))
            # (4) send initial placement of ships
            ships = player.ships_to_json()
            logging.debug('send initial placement ' + ships)
            sockfile.write(ships+'\n')

            # (5) main loop in game
            t = 1
            while True:
                # receive (5a) turn to move or (6) game end
                game_status = sockfile.readline().rstrip()
                print(f't={t} {game_status}')
                if game_status == "your turn":
                    # (5b) send action if my turn
                    action = player.action()
                    logging.debug('> ' + action)
                    sockfile.write(action+'\n')
                elif game_status == "waiting":
                    pass
                elif game_status == Protocol.you_win:
                    break
                elif game_status == Protocol.you_lose:
                    break
                elif game_status == Protocol.draw:
                    break
                else:
                    raise RuntimeError("unexpected information from server")
                observation = sockfile.readline()
                # (5c) receive result of action either by me or by opponent
                if not observation:
                    logging.error('disconnected from server')
                    break
                player.update(observation, game_status)
                t += 1
