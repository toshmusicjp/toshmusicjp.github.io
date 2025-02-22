import pyxel

pyxel.init(128, 128, title="NINJA")
pyxel.load("ninja.pyxres")

STAGE_WIDTH = 256 * 3
STAGE_HEIGHT = 128 * 2
LEFT_LINE = 40
RIGHT_LINE = pyxel.width - 48
UPPER_LINE = 40
BOTTOM_LINE = pyxel.height - 20
scroll_x = 0
scroll_y = 0
x = 8
y = 100
dx = 0
dy = 0
pldir = 1
jump = 0
score = 0
is_bgm_playing = False  # BGM再生フラグ
SE_CH = 1  # 効果音のチャンネル
is_goal = False  # ゴール判定フラグ
time_left = 60  # 制限時間
is_game_over = False  # ゲームオーバーフラグ

chkpoint = [(2, 0), (6, 0), (2, 7), (6, 7)]

def chkwall(cx, cy):
    c = 0
    if cx < 0 or STAGE_WIDTH - 8 < cx:
        c += 1
    if STAGE_HEIGHT < cy:
        c += 1
    for cpx, cpy in chkpoint:
        xi = (cx + cpx) // 8
        yi = (cy + cpy) // 8
        if (1, 0) == pyxel.tilemap(0).pget(xi, yi):
            c += 1
    return c

def restart_game():
    pyxel.load("ninja.pyxres")
    global x, y, dx, dy, jump, score, scroll_x, scroll_y, is_goal, is_game_over, time_left
    x, y = 8, 100
    dx, dy = 0, 0
    jump = 0
    score = 0
    scroll_x, scroll_y = 0, 0
    is_goal = False
    is_game_over = False
    time_left = 60

def update():
    global scroll_x, scroll_y, x, y, dx, dy, pldir, jump, score, is_bgm_playing, is_goal, time_left, is_game_over
    
    if is_goal or is_game_over:
        if pyxel.btnp(pyxel.KEY_A):
            restart_game()
        return  # ゲーム終了時は操作無効
    
    # BGMを一度だけ再生
    if not is_bgm_playing:
        pyxel.playm(0, loop=True)
        is_bgm_playing = True
    
    # タイマー更新
    if pyxel.frame_count % 30 == 0:
        time_left -= 1
        if time_left <= 1:
            is_game_over = True
    
    # 操作判定
    if pyxel.btn(pyxel.KEY_LEFT):
        if -3 < dx:
            dx -= 1
        pldir = -1
    elif pyxel.btn(pyxel.KEY_RIGHT):
        if dx < 3:
            dx += 1
        pldir = 1
    else:
        dx = int(dx * 0.7)
    
    # 横方向の移動
    lr = pyxel.sgn(dx)
    loop = abs(dx)
    while loop > 0:
        if chkwall(x + lr, y) != 0:
            dx = 0
            break
        x += lr
        loop -= 1
    
    # 左方向へのスクロール
    if x < scroll_x + LEFT_LINE:
        scroll_x = max(0, x - LEFT_LINE)
    
    # 右方向へのスクロール
    if scroll_x + RIGHT_LINE < x:
        scroll_x = min(STAGE_WIDTH - pyxel.width, x - RIGHT_LINE)
    
    # ジャンプと落下
    if jump == 0:
        if chkwall(x, y + 1) == 0:
            jump = 2
        if pyxel.btnp(pyxel.KEY_SPACE):
            dy = 8
            jump = 1
    else:
        dy -= 1
        if dy < 0:
            jump = 2
    
    ud = pyxel.sgn(dy)
    loop = abs(dy)
    while loop > 0:
        if chkwall(x, y - ud) != 0:
            dy = 0
            jump = 2 if jump == 1 else 0
            break
        y -= ud
        loop -= 1
    
    # 0以下に落下したらゲームオーバー
    if y > 128:
        is_game_over = True
    
    # コイン判定
    xi, yi = (x + 4) // 8, (y + 4) // 8
    if pyxel.tilemap(0).pget(xi, yi) == (1, 1):
        score += 100
        pyxel.tilemap(0).pset(xi, yi, (0, 0))
        pyxel.play(1, 8, loop=False)
    
    # ジャック判定
    if pyxel.tilemap(0).pget(xi, yi) == (1, 2):
        score -= 200
        pyxel.tilemap(0).pset(xi, yi, (0, 0))
        pyxel.play(1, 9, loop=False)
    
    # ゴール判定
    if pyxel.tilemap(0).pget(xi, yi) == (1, 3):
        is_goal = True

def draw():
    pyxel.cls(0)
    pyxel.camera()
    pyxel.bltm(0, 0, 0, scroll_x, scroll_y, pyxel.width, pyxel.height, 0)
    pyxel.camera(scroll_x, scroll_y)
    pyxel.blt(x, y, 0, 0, 8, pldir * 8, 8, 0)
    
    # 画面右上にスコアと残り時間表示
    pyxel.text(scroll_x + pyxel.width - 45, scroll_y + 5, f"SCORE: {score}", 7)
    pyxel.text(scroll_x + pyxel.width - 40, scroll_y + 15, f"TIME: {time_left}", 7)
    
    # ゲーム終了時のメッセージ表示
    if is_goal:
        pyxel.text(scroll_x + 45, scroll_y + 56, "YOU WIN!" if score > 0 else "YOU LOSE!", 7)
    elif is_game_over:
        pyxel.text(scroll_x + 45, scroll_y + 56, "GAME OVER!", 7)
    
    if is_goal or is_game_over:
        pyxel.text(scroll_x + 30, scroll_y + 70, "PRESS A KEY TO RESTART", 7)

pyxel.run(update, draw)
