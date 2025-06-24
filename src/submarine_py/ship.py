class Ship:
    """Player's ship

    >>> ship = Ship('w', (1, 2))
    >>> ship.hp
    3
    >>> ship.move_to((4, 3))
    >>> ship.position
    (4, 3)
    """
    MAX_HPS = {"w": 3, "c": 2, "s": 1}  #: maixmum HP for each ship

    def __init__(self, type, position):
        if type not in Ship.MAX_HPS:
            raise ValueError(f'invalid type {type} for Ship')
        self.type = type
        self.position = position
        self.hp = Ship.MAX_HPS[type]

    def to_dict(self):
        '''convert to dict

        >>> ship = Ship('w', (1, 2))
        >>> ship.to_dict() == {'type': 'w', 'position': (1, 2), 'hp': 3}
        True
        '''
        return self.__dict__

    def move_to(self, to):
        """座標を変更する"""
        self.position = to

    def deal_damage(self, d):
        """ダメージを受けてHPが減る．"""
        self.hp -= d

    def is_reachable(self, to):
        """座標が移動できる範囲(縦横)にあるか確認する．"""
        return self.position[0] == to[0] or self.position[1] == to[1]

    def in_attack_range(self, to):
        """座標が攻撃できる範囲(自分の座標及び周囲1マス)にあるか確認する．"""
        return (abs(to[0] - self.position[0]) <= 1
                and abs(to[1] - self.position[1]) <= 1)
