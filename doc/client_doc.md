# クライアント側のプログラムについて
## 共通ライブラリ
クライアント側のプログラムは、[document](/doc/document.md)の要件を満たしていればどんな言語で実装されていてもよい。
ソケット通信を行って、適切なJSONを送りさえすればよい。Python の場合は (Player)[/src/submarine_py/player_base.py]クラスを継承して使うと便利と思われる。
なお [サーバ側のコード](/src/submarine_py/server.py)は、プレイヤー側を書く目的では読む必要がない。

### Ship
Shipクラスは、艦を表すクラスである。各プレイヤーが持つ艦の状態（種類、位置、HP）を管理する。1つの艦につき1つのオブジェクトを作成する。
[ship.py](/src/submarine_py/ship.py)

### Field
ゲームのマップを保持する．基本は 5x5 の正方形だが，縦横を指定して長方形にもできる．
[field.py](/src/submarine_py/field.py)

`Reporter` は，ターミナルに `Field` をわかりやすく表示する．

### Player
PlayerクラスはAIの雛形となるクラスで、艦を連想配列で複数持ち、移動や攻撃を受けた時の処理を行うメソッドが記述されている。行動を決定するアルゴリズム自体は抽象メソッドになっていて、継承したサブクラスで定義されなければならない。
[player_baes.py](/src/submarine_py/player_base.py)

## 単純なAI
上の共通ライブラリの利用例及びソケット通信の例として、単純なAIプログラムを作成し、[random_player.py](/sample/random_player.py) とした。
このプレイヤーは可能な行動の中からランダムに行動を決定する。ルール違反をすることはない。

## 操作できるプレイヤー
作成したAIの評価に使う目的で、操作できるプレイヤーとして [manual_player.py](/sample/manual_player.py) を作成した。
これは文面とアスキーアートでコマンドライン上に状況を表示する．
