#Hi my name is uncle Sam, let's play a little game of chess shall we ?
import pygame
import sys
import ctypes
ctypes.windll.user32.SetProcessDPIAware() #magic line that fixes Windows™ window size issues when in full screen (idk what it does lol)

pygame.init()

WIDTH, HEIGHT = 1920, 1080
ROWS, COLS = 8, 8
SQUARE_SIZE = (HEIGHT // COLS) - 15
BG = (231, 212, 177)
DARK = (173, 120, 88)
DARK_RED = (163,56,63)
RED = (190, 75, 83)
GREEN = (114,164,65)
ORANGE = (191,120,43)
GREY = (135, 135, 135)
LIGHT = (225, 199, 159)
BOARD_SIZE = SQUARE_SIZE * 8
BOARD_RECT = pygame.Rect((WIDTH-BOARD_SIZE)//2, (HEIGHT-BOARD_SIZE)//2, BOARD_SIZE, BOARD_SIZE)
PANELW = 300
PANELX = WIDTH - PANELW
OFFSETX = (WIDTH - BOARD_SIZE) // 2
OFFSETY = (HEIGHT - BOARD_SIZE) // 2
PIECE_COSTS = {"pawn": 0, "knight": 199, "bishop": 120, "rook": 120, "queen": 499, "king": 295}
CAPTURE_VALUES = {"pawn": 308, "knight": 666, "bishop": 296, "rook": 296, "queen": 2468, "king": 0}
SELL_VALUES = {"pawn": 154, "knight": 333, "bishop": 148, "rook": 148, "queen": 1234, "king": 0}
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Credit Chess")


def load_sprites():
    pieces = ["pawn", "rook", "knight", "bishop", "queen", "king"]
    colors = ["white", "black"]
    sprites = {}

    for color in colors:
        for piece in pieces:
            path = f"assets/{piece}_{color}.png"
            image = pygame.image.load(path).convert_alpha()
            image = pygame.transform.smoothscale(image, (SQUARE_SIZE, SQUARE_SIZE))
            sprites[(color, piece)] = image
        
    return sprites

def draw_board():
    for row in range(ROWS):
        for col in range(COLS):
            if (row + col) % 2 == 0:
                color = LIGHT
            else:
                color = DARK
            
            pygame.draw.rect(screen, color, (col * SQUARE_SIZE + OFFSETX, row * SQUARE_SIZE + OFFSETY, SQUARE_SIZE, SQUARE_SIZE))

def get_tile_under_mouse():
    mx, my = pygame.mouse.get_pos()
    
    #checks if cursor is actually on the board
    if not (OFFSETX <= mx < OFFSETX + BOARD_SIZE and OFFSETY <= my < OFFSETY + BOARD_SIZE):
        return None
    
    col = (mx - OFFSETX) // SQUARE_SIZE
    row = (my - OFFSETY) // SQUARE_SIZE
    return int(row), int(col)

def draw_highlight(row, col, color, alpha=120):
    highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
    highlight_surface.fill((*color, alpha))
    x = OFFSETX + col * SQUARE_SIZE
    y = OFFSETY + row * SQUARE_SIZE
    screen.blit(highlight_surface, (x, y))

def highlight_green(row, col):
    draw_highlight(row, col, GREEN, 100)

def highlight_red(row, col):
    draw_highlight(row, col, RED, 100)

def highlight_orange(row, col):
    draw_highlight(row, col, ORANGE, 100)

board = [[None for _ in range(8)] for _ in range(8)]

class Piece:
    def __init__(self, color, type):
        self.color = color
        self.type = type
        self.has_moved = False

    def get_moves(self, board, row, col, en_passant_target=None, check_castling=True):
        if self.type == "pawn":
            return self.get_pawn_moves(board, row, col, en_passant_target)
        elif self.type == "rook":
            return self.get_rook_moves(board, row, col)
        elif self.type == "knight":
            return self.get_knight_moves(board, row, col)
        elif self.type == "bishop":
            return self.get_bishop_moves(board, row, col)
        elif self.type == "queen":
            return self.get_queen_moves(board, row, col)
        elif self.type == "king":
            return self.get_king_moves(board, row, col, check_castling)
        return []
    
    def get_pawn_moves(self, board, row, col, en_passant_target=None):
        moves = []
        direction = -1 if self.color == "white" else 1
        #starting row
        start_row = 6 if self.color == "white" else 1
        #forward
        if 0 <= row + direction < 8 and board[row + direction][col] is None:
            moves.append((row + direction, col))
            #pawn can move 2 tiles forward if it hasn't moven yet
            if row == start_row and board[row + 2* direction][col] is None:
                moves.append((row + 2* direction, col))
        #capture diagonals
        for dc in [-1, 1]:
            new_col = col + dc
            new_row = row + direction

            if 0 <= new_col < 8 and 0 <= new_row < 8:
                target = board[new_row][new_col]
                if target and target.color != self.color:
                    moves.append((new_row, new_col))
                if en_passant_target and (new_row, new_col) == en_passant_target:
                    moves.append((new_row, new_col))

        return moves
    
    def get_rook_moves(self, board, row, col):
        moves = []
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        for dr, dc, in directions:
            r, c = row + dr, col + dc

            while 0 <= r < 8 and 0 <= c < 8:
                if board[r][c] is None:
                    moves.append((r, c))
                else:
                    if board[r][c].color != self.color:
                        moves.append((r, c))
                    break

                r += dr
                c += dc
            
        return moves
    
    def get_knight_moves(self, board, row, col):
        moves = []
        offsets = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
        for dr, dc in offsets:
            r, c  = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                if board[r][c] is None or board[r][c].color != self.color:
                    moves.append((r, c))

        return moves
    
    def get_bishop_moves(self, board, row, col):
        moves = []
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                if board[r][c] is None:
                    moves.append((r, c))
                else:
                    if board[r][c].color != self.color:
                        moves.append((r, c))
                    break
                r += dr
                c += dc

        return moves
    
    def get_queen_moves(self, board, row, col):
        return self.get_rook_moves(board, row, col) + \
            self.get_bishop_moves(board, row, col)
    
    def get_king_moves(self, board, row, col, check_castling=True):
        moves = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue

                r, c = row + dr, col + dc
                if 0 <= r < 8 and 0 <= c < 8:
                    if board[r][c] is None or board[r][c].color != self.color:
                        moves.append((r, c))

        enemy = "black" if self.color == "white" else "white"
        if check_castling and not self.has_moved and not is_attacked(board, row, col, enemy):
            if (board[row][7] and board[row][7].type == "rook" and
                    not board[row][7].has_moved and
                    board[row][5] is None and board[row][6] is None and
                    not is_attacked(board, row, 5, enemy) and
                    not is_attacked(board, row, 6, enemy)):
                moves.append((row, 6))
            if (board[row][0] and board[row][0].type == "rook" and
                    not board[row][0].has_moved and
                    board[row][1] is None and board[row][2] is None and board[row][3] is None and
                    not is_attacked(board, row, 3, enemy) and
                    not is_attacked(board, row, 2, enemy)):
                moves.append((row, 2))

        return moves


def setup_board():
    for col in range(8):
        board[6][col] = Piece("white", "pawn")
        board[1][col] = Piece("black", "pawn")

    board[7][0] = board[7][7] = Piece("white", "rook")
    board[0][0] = board[0][7] = Piece("black", "rook")

    board[7][1] = board[7][6] = Piece("white", "knight")
    board[0][1] = board[0][6] = Piece("black", "knight")

    board[7][2] = board[7][5] = Piece("white", "bishop")
    board[0][2] = board[0][5] = Piece("black", "bishop")

    board[7][3] = Piece("white", "queen")
    board[0][3] = Piece("black", "queen")

    board[7][4] = Piece("white", "king")
    board[0][4] = Piece("black", "king")

def draw_pieces(sprites):
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece:
                x = OFFSETX + col * SQUARE_SIZE + SQUARE_SIZE // 2
                y = OFFSETY + row * SQUARE_SIZE + SQUARE_SIZE // 2

                sprite = sprites[(piece.color, piece.type)]
                rect = sprite.get_rect(center=(x, y))
                screen.blit(sprite, rect)

def find_king(board, color):
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece and piece.type == "king" and piece.color == color:
                return(row, col)
    return None

def is_attacked(board, row, col, enemy_color):
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece and piece.color == enemy_color:
                moves = piece.get_moves(board, r, c, check_castling=False)
                if (row, col) in moves:
                    return True
    return False

def is_check(board, color):
    king_pos = find_king(board, color)
    if not king_pos:
        return False
    
    enemy = "black" if color == "white" else "white"
    return is_attacked(board, king_pos[0], king_pos[1], enemy)

def simulate_move(board, sr, sc, tr, tc):
    new_board = [[board[r][c] for c in range(8)] for r in range(8)]
    new_board[tr][tc] = new_board[sr][sc]
    new_board[sr][sc] = None
    return new_board

def get_legal_moves(board, row, col, en_passant_target=None):
    piece = board[row][col]
    if not piece:
        return []
    raw_moves = piece.get_moves(board, row, col, en_passant_target)
    legal_moves = []
    for move in raw_moves:
        r, c = move
        new_board = simulate_move(board, row, col, r, c)
        if piece.type == "pawn" and en_passant_target and (r, c) == en_passant_target:
            direction = -1 if piece.color == "white" else 1
            new_board[r - direction][c] = None
        if not is_check(new_board, piece.color):
            legal_moves.append(move)
    
    return legal_moves

def has_legal_moves(board, color, en_passant_target=None):
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece and piece.color == color:
                moves = get_legal_moves(board, row, col, en_passant_target)
                if moves:
                    return True
    return False

def is_checkmate(board, color, en_passant_target=None):
    if not is_check(board, color):
        return False
    
    return not has_legal_moves(board, color, en_passant_target)

def is_stalemate(board, color, en_passant_target=None):
    if is_check(board, color):
        return False
    
    return not has_legal_moves(board, color, en_passant_target)

def to_chess_notation(row, col):
    file = chr(ord('A') + col) #names the columns with letters so A to H
    rank = str(8 - row) #same but with the rows and with numbers from 0 to 8
    return file + rank

def gain_income(money, color):
    pawns = sum(1 for row in range(8) for col in range(8) if board[row][col] and board[row][col].color == color and board[row][col].type=="pawn")
    money[color] += pawns * 220 #income based on number of pawns * 220$

def calculate_maintenance(color):
    total = 0
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece and piece.color == color:
                total += PIECE_COSTS[piece.type]
    return total

def draw_finance_panel(screen, money, debt):
    font = pygame.font.SysFont("arial", 26)
    panel_y = {"white": OFFSETY + BOARD_SIZE + (HEIGHT-OFFSETY-BOARD_SIZE) // 2 - 13, "black": OFFSETY // 2 - 13}
    x_positions = [WIDTH // 3, WIDTH // 2, 2 * WIDTH // 3]

    for color in ["white", "black"]:
        maintenance = calculate_maintenance(color)
        y = panel_y[color]

        money_text = font.render(f"Balance : {money[color]} $", True, GREEN)
        debt_text = font.render(f"Debt : {debt[color]} $", True, DARK_RED)
        upkeep_text = font.render(f"Upkeep : {maintenance}/turn", True, ORANGE)

        total_w = money_text.get_width() + debt_text.get_width() + upkeep_text.get_width()
        gap = (WIDTH - total_w) // 11.5
        x0 = total_w + gap
        x1 = x0 + money_text.get_width() + gap
        x2 = x1 + debt_text.get_width() + gap

        screen.blit(money_text, money_text.get_rect(centerx=x_positions[0], y=y))
        screen.blit(debt_text, debt_text.get_rect(centerx=x_positions[1], y=y))
        screen.blit(upkeep_text, upkeep_text.get_rect(centerx=x_positions[2], y=y))
    

def draw_move_history(screen, move_history, sprites):
    font = pygame.font.SysFont("arial", 22)
    x = 20
    y = 20

    last_moves = move_history[-5:][::-1] #shows 5 last moves / newest on top

    for i, move in enumerate(last_moves):
        piece = move["piece"]

        sprite = sprites[(piece.color, piece.type)]
        small_sprite = pygame.transform.smoothscale(sprite, (30, 30))

        from_sq = to_chess_notation(*move["from"])
        to_sq = to_chess_notation(*move["to"])
        alpha = 255 - (len(last_moves) + i - 4) * 35
        text_color = (190, 75, 83)

        if move["captured"]:
            label = f"{from_sq} got {to_sq}"
        else:
            label = f"{from_sq} to {to_sq}"

        text = font.render(label, True, text_color)
        faded_sprite = small_sprite.copy()
        faded_sprite.set_alpha(alpha)
        text.set_alpha(alpha)
        screen.blit(faded_sprite, (x, y))
        screen.blit(text, (x + 35, y + 4))
        y += 40

def draw_game_over(screen, message):
    font_big = pygame.font.SysFont("arial", 72)
    font_small = pygame.font.SysFont("arial", 32)
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    screen.blit(overlay, (0, 0))
    text = font_big.render(message, True, (255, 255, 255))
    subtext = font_small.render("Press ESC to quit", True, (200, 200, 200))
    screen.blit(text, text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40)))
    screen.blit(subtext, subtext.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50)))

def take_loan(player, amount, bank, money):
    if amount <= 10000:
        bank[player]["loan"] += amount
        bank[player]["loan_turns"] = 0
        money[player] += amount

def invest(player, amount, turn_count, bank, money):
    if money[player] >= amount:
        money[player] -= amount
        bank[player]["investments"].append({"amount": amount, "start_turn": turn_count})

def withdraw(player, turn_count, bank, money):
    total = 0
    remaining = []
    for inv in bank[player]["investments"]:
        if turn_count - inv["start_turn"] >= 5:
            total += int(inv["amount"])
        else:
            remaining.append(inv)
        
    bank[player]["investments"] = remaining
    money[player] += total

def apply_taxes(player, board, tile_owner, money, debt, RENT_PRICE):
    piece_count = sum(1 for r in range(8) for c in range(8) if board[r][c] and board[r][c].color == player)
    rented_tiles = sum(1 for r in range(8) for c in range(8) if tile_owner[r][c] == player)
    taxable_income = (money[player] + piece_count * 5 + rented_tiles * RENT_PRICE)
    tax = int(taxable_income * 0.2) #20% taxes over total balance, number of pieces times 5, and number of rented tiles times their rent price so 112$ each

    if money[player] >= tax:
        money[player] -= tax
    else:
        debt[player] += tax
        money[player] = 0

def button(rect, color, text):
    pygame.draw.rect(screen, color, rect, border_radius=25)
    pygame.draw.rect(screen, LIGHT, rect, width=2, border_radius=25)
    font = pygame.font.SysFont("arial", 22, bold=True)
    surf = font.render(text, True, (255, 255, 255))
    screen.blit(surf, surf.get_rect(center=rect.center))

def draw_bank_menu(player, bank, money, debt, turn_count, active_input):
    w, h = 520, 360
    x, y = WIDTH // 2 - w // 2, HEIGHT // 2 - h // 2
    rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(screen, LIGHT, rect, border_radius=25)
    pygame.draw.rect(screen, (0, 0, 0), rect, width=4, border_radius=25)

    font = pygame.font.SysFont("arial", 22)
    big_font = pygame.font.SysFont("arial", 28, bold=True)

    inv_total = sum(inv["amount"] for inv in bank[player]["investments"])
    loan = bank[player]["loan"]

    lines = [
        f"Invested: {int(inv_total)}$",
        f"Loan: {loan}$",
        f"Balance: {money[player]}$",
        f"Debt: {debt[player]}$"
    ]
    for i, text in enumerate(lines):
        screen.blit(font.render(text, True, (0, 0, 0)), (x + 20, y + 20 + i * 30))

    screen.blit(big_font.render(f"Input: {active_input}", True, (0, 0, 0)), (x + 20, y + 160))
    input_rect = pygame.Rect(x + 100, y + 160, 200, 35)
    pygame.draw.rect(screen, (255, 255, 255), input_rect, border_radius=10)
    pygame.draw.rect(screen, (0, 0, 0), input_rect, width=2, border_radius=10)
    input_text = big_font.render(active_input, True, (0, 0, 0))
    screen.blit(input_text, (x + 140, y + 160))

    btn_w, btn_h = 140, 40
    invest_btn = pygame.Rect(x + 20, y + 220, btn_w, btn_h)
    loan_btn = pygame.Rect(x + 180, y + 220, btn_w, btn_h)
    withdraw_btn = pygame.Rect(x + 340, y + 220, btn_w, btn_h)

    button(invest_btn, ORANGE, "Invest")
    button(loan_btn, DARK_RED, "Loan")

    #withdraw button: green if any investment is "5+ turns old"
    can_withdraw = any(turn_count - inv["start_turn"] >= 5 for inv in bank[player]["investments"])
    withdraw_color = GREEN if can_withdraw else GREY
    button(withdraw_btn, withdraw_color, "Withdraw")

    #shows turns remaining for withdraw if grey
    if not can_withdraw and bank[player]["investments"]:
        min_turns_left = 5 - max((turn_count - inv["start_turn"]) for inv in bank[player]["investments"])
        withdraw_text = font.render(f"Withdraw in {min_turns_left} turns", True, (0, 0, 0))
        screen.blit(withdraw_text, (x + 340, y + 260))
    elif not bank[player]["investments"]:
        withdraw_text = font.render("No investments yet", True, (0, 0, 0))
        screen.blit(withdraw_text, (x + 325, y + 260))

    return invest_btn, loan_btn, withdraw_btn

def draw_taxes_menu(player, money, debt, turn_count, last_tax_paid, next_tax_turn):
    w, h = 420, 200
    x, y = WIDTH // 2 - w // 2, HEIGHT // 2 - h // 2
    rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(screen, LIGHT, rect, border_radius=25)
    pygame.draw.rect(screen, (0, 0, 0), rect, width=4, border_radius=25)

    font = pygame.font.SysFont("arial", 24)
    lines = [
        f"Next tax in {max(0, next_tax_turn - turn_count)} turns",
        f"Last tax paid: {last_tax_paid.get(player, 'None')}$"
    ]
    for i, text in enumerate(lines):
        screen.blit(font.render(text, True, (0, 0, 0)), (x + 20, y + 20 + i * 40))

def main():
    clock = pygame.time.Clock()
    setup_board()

    selected_tile = None #(row, col)
    sprites = load_sprites()
    current_player = "white" # or "black"
    valid_moves = []
    move_history = []
    tile_owner = [[None for _ in range(8)] for _ in range(8)]
    en_passant_target = None
    game_over_message = None
    money = {"white": 0, "black":0}
    debt = {"white": 0, "black":0}
    sell_mode = False
    sell_confirm = None
    buy_mode = False
    buy_confirm = None
    BUY_PRICE = 199
    RENT_PRICE = 112
    SELL_TILE_PRICE = 135
    turn_count = 0
    active_input = ""
    bank_mode = False
    taxes_mode = False
    bank_action = None # invest/loan/withdraw
    last_tax_paid = {"white": "None", "black": "None"}
    next_tax_turn = 10
    piece_buy_mode = False
    piece_buy_selected = None
    piece_buy_confirm = None

    bank = {"white": {"loan":0, "loan_turns":0, "investments": [] #list of {"amount":X, "start_turn": T}
            },
            "black": {"loan": 0, "loan_turns": 0, "investments": []
            }
        }
    


    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if not game_over_message and event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mx, my = event.pos

                    if bank_btn.collidepoint(mx, my):
                        bank_mode = not bank_mode
                        taxes_mode = False
                        sell_mode = False
                        buy_mode = False
                        piece_buy_mode = False
                        piece_buy_selected = None
                        piece_buy_confirm = None
                        selected_tile = None
                        valid_moves = []

                    elif taxes_btn.collidepoint(mx, my):
                        taxes_mode = not taxes_mode
                        bank_mode = False
                        sell_mode = False
                        buy_mode = False
                        piece_buy_mode = False
                        piece_buy_selected = None
                        piece_buy_confirm = None
                        selected_tile = None
                        valid_moves = []

                    if bank_mode:
                        inv_btn, loan_btn, wd_btn = draw_bank_menu(current_player, bank, money, debt, turn_count, active_input)
                        if inv_btn.collidepoint(mx, my) and active_input:
                            invest(current_player, int(active_input), turn_count, bank, money)
                            active_input = ""
                        elif loan_btn.collidepoint(mx, my) and active_input:
                            take_loan(current_player, int(active_input), bank, money)
                            active_input = ""
                        elif wd_btn.collidepoint(mx, my):
                            withdraw(current_player, turn_count, bank, money)

                    if buy_confirm is not None:
                        pc_row, pc_col, yes_rect, no_rect = buy_confirm
                        if yes_rect and yes_rect.collidepoint(mx, my):
                            if money[current_player] >= BUY_PRICE:
                                money[current_player] -= BUY_PRICE
                                tile_owner[pc_row][pc_col] = current_player
                            buy_confirm = None
                            buy_mode = False
                        elif no_rect and no_rect.collidepoint(mx, my):
                            buy_confirm = None
                    
                    elif buy_btn_rect.collidepoint(mx, my) and not game_over_message:
                        buy_mode = not buy_mode
                        sell_mode = False
                        taxes_mode = False
                        bank_mode = False
                        piece_buy_mode = False
                        piece_buy_selected = None
                        piece_buy_confirm = None
                        selected_tile = None
                        valid_moves = []
                    
                    elif buy_mode:
                        tile = get_tile_under_mouse()
                        if tile:
                            r, c = tile
                            if board[r][c] is None and tile_owner[r][c] is None:
                                buy_confirm = (r, c, None, None)
                        else:
                            buy_mode = False

                    if piece_buy_confirm is not None:
                        pb_row, pb_col, pb_type, yes_rect, no_rect = piece_buy_confirm
                        if yes_rect and yes_rect.collidepoint(mx, my):
                            cost = CAPTURE_VALUES[pb_type]
                            if money[current_player] >= cost:
                                money[current_player] -= cost
                                new_piece = Piece(current_player, pb_type)
                                new_piece.has_moved = True
                                board[pb_row][pb_col] = new_piece
                                
                            piece_buy_confirm = None
                            piece_buy_mode = False
                            piece_buy_selected = None
                        elif no_rect and no_rect.collidepoint(mx, my):
                            piece_buy_confirm = None

                    elif piece_buy_btn_rect.collidepoint(mx, my) and not game_over_message:
                        piece_buy_mode = not piece_buy_mode
                        piece_buy_selected = None
                        piece_buy_confirm = None
                        sell_mode = False
                        buy_mode = False
                        bank_mode = False
                        taxes_mode = False
                        selected_tile = None
                        valid_moves = []

                    elif piece_buy_mode and piece_buy_selected is None:
                        for ptype, card_rect in piece_shop_rects.items():
                            if card_rect.collidepoint(mx, my):
                                if money[current_player] >= CAPTURE_VALUES[ptype]:
                                    piece_buy_selected = ptype
                                break

                    elif piece_buy_mode and piece_buy_selected is not None and piece_buy_confirm is None:
                        tile = get_tile_under_mouse()
                        if tile:
                            pr, pc2 = tile
                            start_rows = (6, 7) if current_player == "white" else (0, 1)
                            if pr in start_rows and board[pr][pc2] is None:
                                piece_buy_confirm = (pr, pc2, piece_buy_selected, None, None)
                        else:
                            piece_buy_mode = False
                            piece_buy_selected = None

                    if sell_confirm is not None:
                        pc_row, pc_col, pc_piece, yes_rect, no_rect = sell_confirm
                        if yes_rect and yes_rect.collidepoint(mx, my):
                            sale_price = SELL_VALUES[pc_piece.type]
                            money[current_player] += sale_price
                            board[pc_row][pc_col] = None
                            if debt[current_player] > 0:
                                if sale_price >= debt[current_player]:
                                    sale_price -= debt[current_player]
                                    debt[current_player] = 0
                                    money[current_player] += sale_price
                                else:
                                    debt[current_player] -= sale_price
                            else:
                                money[current_player] += sale_price
                            sell_confirm = None
                            sell_mode = False
                        elif no_rect and no_rect.collidepoint(mx, my):
                            sell_confirm = None

                    elif sell_btn_rect.collidepoint(mx, my) and not game_over_message:
                        sell_mode = not sell_mode
                        buy_mode = False
                        bank_mode = False
                        taxes_mode = False
                        piece_buy_mode = False
                        piece_buy_selected = None
                        piece_buy_confirm = None
                        selected_tile = None
                        valid_moves = []
                        
                    elif sell_mode:
                        tile = get_tile_under_mouse()
                        if tile:
                            sr2, sc2 = tile
                            target_piece = board[sr2][sc2]
                            if target_piece and target_piece.color == current_player and target_piece.type != "king":
                                sell_confirm = (sr2, sc2, target_piece, None, None)
                        else:
                            sell_mode = False

                    else:
                        tile = get_tile_under_mouse()
                        if tile:
                            row, col = tile
                            piece = board[row][col]

                            #if nothing selected
                            if selected_tile is None:
                                if piece and piece.color == current_player:
                                    selected_tile = tile
                                    valid_moves = get_legal_moves(board, row, col, en_passant_target)
                            #if something already selected
                            else:
                                sr, sc = selected_tile
                                selected_piece = board[sr][sc]
                                #click on another piece to switch selection
                                if piece and piece.color == current_player:
                                    selected_tile = tile
                                    valid_moves = get_legal_moves(board, row, col, en_passant_target)
                            #click on a valid tile
                                elif tile in valid_moves:
                                    captured_piece = board[row][col]
                                    captured = board[row][col] is not None

                                    is_en_passant = (
                                        selected_piece.type == "pawn" and
                                        en_passant_target == (row, col) and
                                        board[row][col] is None
                                    )
                                    if is_en_passant:
                                        direction = -1 if selected_piece.color == "white" else 1
                                    
                                        captured_piece = board[row - direction][col]
                                        board[row - direction][col] = None
                                        captured = True

                                    is_castling = (
                                        selected_piece.type == "king" and
                                        abs(col - sc) == 2
                                    )
                                    if is_castling:
                                        if col == 6:
                                            board[row][5] = board[row][7]
                                            board[row][7] = None
                                            board[row][5].has_moved = True
                                        elif col == 2:
                                            board[row][3] = board[row][0]
                                            board[row][0] = None
                                            board[row][3].has_moved = True

                                    board[row][col] = selected_piece
                                    board[sr][sc] = None
                                    selected_piece.has_moved = True

                                    if captured and captured_piece:
                                        reward = CAPTURE_VALUES[captured_piece.type]
                                        money[current_player] += reward

                                    if selected_piece.type == "pawn" and abs(row - sr) == 2:
                                        direction = -1 if selected_piece.color == "white" else 1
                                        en_passant_target = (row - direction, col)
                                    else:
                                        en_passant_target = None

                                    if selected_piece.type == "pawn":
                                        if (selected_piece.color == "white" and row == 0) or \
                                           (selected_piece.color == "black" and row == 7):
                                            board[row][col] = Piece(selected_piece.color, "queen")
                                            board[row][col].has_moved = True

                                    #store move in move_history
                                    move_history.append({
                                        "piece": board[row][col],
                                        "from": (sr, sc),
                                        "to": (row, col),
                                        "captured": captured
                                    })

                                    #switch sides
                                    gain_income(money, current_player)
                                    
                                    #pay rent for all pieces standing on prooperty tiles
                                    for r in range(8):
                                        for c in range(8):
                                            piece = board[r][c]
                                            owner = tile_owner[r][c]

                                            if piece and piece.color == current_player:
                                                if owner is not None and owner != current_player:
                                                    money[current_player] -= RENT_PRICE
                                                    money[owner] += RENT_PRICE

                                    net = money[current_player] - calculate_maintenance(current_player)
                                
                                
                                    if net >= 0:
                                        remainder = net - debt[current_player]
                                        if remainder >= 0:
                                            debt[current_player] = 0
                                            money[current_player] = remainder
                                        else:
                                            debt[current_player] = -remainder
                                            money[current_player] = 0
                                    else:
                                        money[current_player] = 0
                                        debt[current_player] += -net

                                    if bank[current_player]["loan"] > 0:
                                        bank[current_player]["loan_turns"] += 1
                                        repayment = int(bank[current_player]["loan"] * 0.10)

                                        if money[current_player] >= repayment:
                                            money[current_player] -= repayment
                                            bank[current_player]["loan"] -= repayment
                                        else:
                                            debt[current_player] += repayment

                                    if bank[current_player]["loan"] <= 0 and bank[current_player]["loan_turns"] > 0:
                                        penalty = bank[current_player]["loan_turns"] * 10
                                        if money[current_player] >= penalty:
                                            money[current_player] -= penalty
                                        elif money[current_player] < penalty and debt[current_player] == 0:
                                            debt[current_player] += penalty - money[current_player]
                                        elif money[current_player] == 0:
                                            debt[current_player] += penalty
                                        bank[current_player]["loan_turns"] = 0

                                    new_investments = []
                                    for inv in bank[current_player]["investments"]:
                                        inv["amount"] *= 1.05 #5% returns per turn
                                        new_investments.append(inv)

                                    bank[current_player]["investments"] = new_investments

                                    sold = False
                                    if debt[current_player] > 0:
                                        for r in range(8):
                                            for c in range(8):
                                                if tile_owner[r][c] == current_player and not sold:
                                                    tile_owner[r][c] = None
                                                    money[current_player] += SELL_TILE_PRICE
                                                    sold = True
                                    turn_count += 1
                                    if turn_count % 10 == 0:
                                        apply_taxes("white", board, tile_owner, money, debt, RENT_PRICE)
                                        apply_taxes("black", board, tile_owner, money, debt, RENT_PRICE)
                                        last_tax_paid["white"] = turn_count
                                        last_tax_paid["black"] = turn_count
                                        next_tax_turn = turn_count + 10
                                    current_player = "black" if current_player == "white" else "white"



                                    if is_checkmate(board, current_player, en_passant_target):
                                        winner = "black" if current_player == "white" else "white"
                                        game_over_message = f"{winner.capitalize()} wins by checkmate!"
                                    elif is_stalemate(board, current_player, en_passant_target):
                                        game_over_message = "Stalemate! It's a draw."

                                    for player in ("white", "black"):
                                        if debt[player] >= 10000 and not game_over_message:
                                            winner = "black" if player == "white" else "white"
                                            game_over_message = f"{winner.capitalize()} wins! {player.capitalize()} went bankrupt (10,000$)!"

                                    selected_tile = None
                                    valid_moves = []

                                #if non-valid tile selected -> cancels selection
                                else:
                                    selected_tile = None
                                    valid_moves = []


        
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if not game_over_message:
                        #going Italy mode during ww2 (aka switching sides)
                        if current_player == "white":
                            current_player = "black"
                        else:
                            current_player = "white"
                        
                        selected_tile = None #resets selections when switching sides

            
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

            if event.type == pygame.KEYDOWN and bank_mode:
                if event.key == pygame.K_BACKSPACE:
                    active_input = active_input[:-1]
                elif event.unicode.isdigit():
                    active_input += event.unicode
        

        sell_btn_w, sell_btn_h = 180, 50
        buy_btn_rect = pygame.Rect(20, HEIGHT - 50 - 40 - sell_btn_h - 70, 180, 50)
        sell_btn_rect = pygame.Rect(20, HEIGHT - 50 - 40 - sell_btn_h - 10, 170, 50)
        piece_buy_btn_rect = pygame.Rect(20, HEIGHT - 50 - 40 - sell_btn_h - 130, 180, 50)

        bank_btn = pygame.Rect(20, HEIGHT - 50 - 40 - sell_btn_h - 70 - 120, 180, 50)
        taxes_btn = pygame.Rect(20, HEIGHT - 50 - 40 - sell_btn_h - 70 - 180, 180, 50)
        piece_shop_rects = {}

        if taxes_mode:
            draw_taxes_menu(current_player, money, debt, turn_count, last_tax_paid, next_tax_turn)

        screen.fill(BG)
        #board outline
        pygame.draw.rect(screen, DARK_RED, BOARD_RECT.inflate(25, 25), border_radius=20)
        pygame.draw.rect(screen, DARK_RED, BOARD_RECT, border_radius = 15)

        #move history panel
        draw_board()
        draw_move_history(screen, move_history, sprites)
        draw_finance_panel(screen, money, debt)
        font_big = pygame.font.SysFont("arial", 28)
        text = font_big.render(f"Turn: {current_player}", True, DARK)
        screen.blit(text, (20, HEIGHT - 50))
        last_move = move_history[-1] if move_history else None
        if last_move:
            highlight_green(*last_move["to"])
            highlight_orange(*last_move["from"])

        if is_check(board, current_player):
            king_pos = find_king(board, current_player)
            if king_pos:
                highlight_red(*king_pos)

        capture_moves = []
        normal_moves = []
        for move in valid_moves:
            r, c = move
            if board[r][c] is None and en_passant_target != (r, c):
                normal_moves.append(move)
            else:
                capture_moves.append(move)

        for move in normal_moves:
            highlight_orange(*move)
        for move in capture_moves:
            highlight_red(*move)
        if selected_tile:
            highlight_orange(*selected_tile)
        #hover effetc
        tile = get_tile_under_mouse()
        if tile:
            row, col = tile
            draw_highlight(row, col, (100, 65, 50), 85)

        if selected_tile:
            if current_player == "white":
                highlight_green(*selected_tile)
            elif current_player == "black":
                highlight_red(*selected_tile)

        draw_pieces(sprites)

        #Blur effect for sell mode
        YELLOW = (230, 210, 50)
        if sell_mode:
            blur_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            blur_surf.fill((0, 0, 0, 160))
            screen.blit(blur_surf, (0, 0))

            font_price = pygame.font.SysFont("arial", 20, bold=True)
            for r in range(8):
                for c in range(8):
                    p = board[r][c]
                    if p and p.color == current_player and p.type != "king":
                        glow_surf = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                        glow_surf.fill((*YELLOW, 170))
                        screen.blit(glow_surf, (OFFSETX + c * SQUARE_SIZE, OFFSETY + r * SQUARE_SIZE))

                        sprite = sprites[(p.color, p.type)]
                        rect = sprite.get_rect(center=(OFFSETX + c * SQUARE_SIZE + SQUARE_SIZE // 2, OFFSETY + r * SQUARE_SIZE + SQUARE_SIZE // 2))
                        screen.blit(sprite, rect)
                        price_surf = font_price.render(f"{SELL_VALUES[p.type]}", True, (30, 2, 0, 0))
                        price_bg = pygame.Surface((price_surf.get_width() + 8, price_surf.get_height() + 4), pygame.SRCALPHA)
                        price_bg.fill((*YELLOW, 220))
                        px = OFFSETX + c * SQUARE_SIZE + SQUARE_SIZE // 2 - price_bg.get_width() // 2
                        py = OFFSETY + r * SQUARE_SIZE + SQUARE_SIZE - price_bg.get_height() - 4
                        screen.blit(price_bg, (px, py))
                        screen.blit(price_surf, (px + 4, py + 2))

        if piece_buy_mode:
            blur_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            blur_surf.fill((0, 0, 0, 160))
            screen.blit(blur_surf, (0, 0))
            if piece_buy_selected is not None and piece_buy_confirm is None:
                start_rows = (6, 7) if current_player == "white" else (0, 1)
                for r in start_rows:
                    for c in range(8):
                        if board[r][c] is None:
                            draw_highlight(r, c, YELLOW, 160)

        if piece_buy_selected is None and piece_buy_mode:
            shop_pieces = ["pawn", "knight", "bishop", "rook", "queen"]
            card_w, card_h = 130, 160
            gap = 20
            total_w = len(shop_pieces) * card_w + (len(shop_pieces) - 1) * gap
            shop_x = WIDTH // 2 - total_w // 2
            shop_y = HEIGHT // 2 - card_h // 2 - 20
            font_shop = pygame.font.SysFont("arial", 20, bold=True)
            font_title = pygame.font.SysFont("arial", 28, bold=True)
            title = font_title.render("Buy a Piece", True, (255, 255, 255))
            screen.blit(title, title.get_rect(centerx=WIDTH // 2, y=shop_y - 48))
            for i, ptype in enumerate(shop_pieces):
                cx = shop_x + i * (card_w + gap)
                card_rect = pygame.Rect(cx, shop_y, card_w, card_h)
                piece_shop_rects[ptype] = card_rect
                can_afford = money[current_player] >= CAPTURE_VALUES[ptype]
                card_color = LIGHT if can_afford else RED
                pygame.draw.rect(screen, card_color, card_rect, border_radius=20)
                pygame.draw.rect(screen, DARK_RED, card_rect, width=3, border_radius=20)
                spr = pygame.transform.smoothscale(sprites[(current_player, ptype)], (72, 72))
                screen.blit(spr, spr.get_rect(centerx=cx + card_w // 2, y=shop_y + 10))
                name_surf = font_shop.render(ptype.capitalize(), True, (255, 255, 255))
                screen.blit(name_surf, name_surf.get_rect(centerx=cx + card_w // 2, y=shop_y + 88))
                price_color = GREY if not can_afford else GREEN
                price_surf = font_shop.render(f"{CAPTURE_VALUES[ptype]}$", True, price_color)
                screen.blit(price_surf, price_surf.get_rect(centerx=cx + card_w // 2, y=shop_y + 116))

        if piece_buy_confirm is not None:
            pb_row, pb_col, pb_type, _, _ = piece_buy_confirm
            cost = CAPTURE_VALUES[pb_type]
            pop_w, pop_h = 480, 200
            pop_x = WIDTH // 2 - pop_w // 2
            pop_y = HEIGHT // 2 - pop_h // 2
            pop_rect = pygame.Rect(pop_x, pop_y, pop_w, pop_h)
            pygame.draw.rect(screen, LIGHT, pop_rect, border_radius=29)
            pygame.draw.rect(screen, (0, 0, 0), pop_rect, width=4, border_radius=28)
            spr = pygame.transform.smoothscale(sprites[(current_player, pb_type)], (64, 64))
            screen.blit(spr, spr.get_rect(center=(WIDTH // 2, pop_y + 75)))
            font_pop = pygame.font.SysFont("arial", 24, bold=True)
            q_surf = font_pop.render(f"Buy {pb_type.capitalize()} for {cost}$ ?", True, (0, 0, 0))
            screen.blit(q_surf, q_surf.get_rect(center=(WIDTH // 2, pop_y + 18)))
            btn_w, btn_h = 110, 44
            gap2 = 30
            yes_rect = pygame.Rect(WIDTH // 2 - btn_w - gap2 // 2, pop_y + pop_h - btn_h - 20, btn_w, btn_h)
            no_rect = pygame.Rect(WIDTH // 2 + gap2 // 2, pop_y + pop_h - btn_h - 20, btn_w, btn_h)
            pygame.draw.rect(screen, GREEN, yes_rect, border_radius=25)
            pygame.draw.rect(screen, (0, 0, 0), yes_rect, width=3, border_radius=25)
            pygame.draw.rect(screen, RED, no_rect, border_radius=25)
            pygame.draw.rect(screen, (0, 0, 0), no_rect, width=3, border_radius=25)
            font_btn2 = pygame.font.SysFont("arial", 28, bold=True)
            screen.blit(font_btn2.render("Yes",  True, (255,255,255)), font_btn2.render("Yes",  True, (255,255,255)).get_rect(center=yes_rect.center))
            screen.blit(font_btn2.render("Nope", True, (255,255,255)), font_btn2.render("Nope", True, (255,255,255)).get_rect(center=no_rect.center))
            piece_buy_confirm = (pb_row, pb_col, pb_type, yes_rect, no_rect)


        if game_over_message:
            draw_game_over(screen, game_over_message)

        #sell confirmation popup
        if sell_confirm is not None:
            pc_row, pc_col, pc_piece, _, _ = sell_confirm
            sale_price = SELL_VALUES[pc_piece.type]
            pop_w, pop_h = 480, 200
            pop_x = WIDTH // 2 - pop_w // 2
            pop_y = HEIGHT // 2 - pop_h // 2
            pop_rect = pygame.Rect(pop_x, pop_y, pop_w, pop_h)
            pygame.draw.rect(screen, LIGHT, pop_rect, border_radius=29)
            pygame.draw.rect(screen, (0, 0, 0), pop_rect, width=4, border_radius=28)
            sprite = sprites[(pc_piece.color, pc_piece.type)]
            sprite_small = pygame.transform.smoothscale(sprite, (64, 64))
            sprite_rect = sprite_small.get_rect(center=(WIDTH // 2, pop_y + 72))
            screen.blit(sprite_small, sprite_rect)
            font_pop = pygame.font.SysFont("arial", 24, bold=True)
            q_line1 = font_pop.render(f"Do you wish to sell {pc_piece.type.capitalize()} for {sale_price}$ ?", True, (0, 0, 0))
            screen.blit(q_line1, q_line1.get_rect(centerx=WIDTH // 2, y=pop_y + 18))
            btn_w, btn_h = 110, 44
            gap = 30
            yes_rect = pygame.Rect(WIDTH // 2 - btn_w - gap // 2, pop_y + pop_h - btn_h - 20, btn_w, btn_h)
            no_rect = pygame.Rect(WIDTH // 2 + gap // 2, pop_y + pop_h - btn_h - 20, btn_w, btn_h)
            pygame.draw.rect(screen, GREEN, yes_rect, border_radius=25)
            pygame.draw.rect(screen, (0, 0, 0), yes_rect, width=3, border_radius=25)
            pygame.draw.rect(screen, RED, no_rect, border_radius=25)
            pygame.draw.rect(screen, (0, 0, 0), no_rect, width=3, border_radius=25)
            font_btn2 = pygame.font.SysFont("arial", 28, bold=True)
            yes_surf = font_btn2.render("Yes", True, (255, 255, 255))
            no_surf = font_btn2.render("Nope", True, (255, 255, 255))
            screen.blit(yes_surf, yes_surf.get_rect(center=yes_rect.center))
            screen.blit(no_surf, no_surf.get_rect(center=no_rect.center))
            sell_confirm = (pc_row, pc_col, pc_piece, yes_rect, no_rect)



        if buy_mode:
            blur_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            blur_surf.fill((0, 0, 0, 160))
            screen.blit(blur_surf, (0, 0))

            for r in range(8):
                for c in range(8):
                    if board[r][c] is None and tile_owner[r][c] is None:
                        draw_highlight(r, c, (255, 255, 0), 120)

        #sell piece button
        btn_color = RED if sell_mode else DARK
        pygame.draw.rect(screen, btn_color, sell_btn_rect, border_radius=25)
        pygame.draw.rect(screen, LIGHT, sell_btn_rect, width=2, border_radius=25)
        font_btn = pygame.font.SysFont("arial", 26, bold=True)
        btn_label = "Cancel" if sell_mode else "Sell Piece"
        btn_text = font_btn.render(btn_label, True, (255, 255, 255))
        screen.blit(btn_text, btn_text.get_rect(center=sell_btn_rect.center))
    
        #buy piece button
        btn_color = RED if piece_buy_mode else DARK
        pygame.draw.rect(screen, btn_color, piece_buy_btn_rect, border_radius=25)
        pygame.draw.rect(screen, LIGHT, piece_buy_btn_rect, width=2, border_radius=25)
        btn_label = "Cancel" if piece_buy_mode else "Buy Piece"
        btn_text = font_btn.render(btn_label, True, (255, 255, 255))
        screen.blit(btn_text, btn_text.get_rect(center=piece_buy_btn_rect.center))

        #buy tile butotn
        btn_color = RED if buy_mode else DARK
        pygame.draw.rect(screen, btn_color, buy_btn_rect, border_radius=25)
        pygame.draw.rect(screen, LIGHT, buy_btn_rect, width=2, border_radius=25)
        font_btn = pygame.font.SysFont("arial", 26, bold=True)
        btn_label = "Cancel" if buy_mode else "Buy Tile"
        btn_text = font_btn.render(btn_label, True, (255, 255, 255))
        screen.blit(btn_text, btn_text.get_rect(center=buy_btn_rect.center))
        
        if buy_confirm is not None:
            pc_row, pc_col, _, _ = buy_confirm
            pop_w, pop_h = 480, 200
            pop_x = WIDTH // 2 - pop_w // 2
            pop_y = HEIGHT // 2 - pop_h // 2
            pop_rect = pygame.Rect(pop_x, pop_y, pop_w, pop_h)
            pygame.draw.rect(screen, LIGHT, pop_rect, border_radius=29)
            pygame.draw.rect(screen, (0, 0, 0), pop_rect, width=4, border_radius=28)
            font_pop = pygame.font.SysFont("arial", 24, bold=True)
            q_line1 = font_pop.render(f"Do you wish to buy this tile for {BUY_PRICE}$ ?", True, (0, 0, 0))
            screen.blit(q_line1, q_line1.get_rect(centerx=WIDTH // 2, y=pop_y + 18))
            btn_w, btn_h = 110, 44
            gap = 30
            yes_rect = pygame.Rect(WIDTH // 2 - btn_w - gap // 2, pop_y + pop_h - btn_h - 20, btn_w, btn_h)
            no_rect = pygame.Rect(WIDTH // 2 + gap // 2, pop_y + pop_h - btn_h - 20, btn_w, btn_h)
            pygame.draw.rect(screen, GREEN, yes_rect, border_radius=25)
            pygame.draw.rect(screen, (0, 0, 0), yes_rect, width=3, border_radius=25)
            pygame.draw.rect(screen, RED, no_rect, border_radius=25)
            pygame.draw.rect(screen, (0, 0, 0), no_rect, width=3, border_radius=25)
            font_btn2 = pygame.font.SysFont("arial", 28, bold=True)
            yes_surf = font_btn2.render("Yes", True, (255, 255, 255))
            no_surf = font_btn2.render("Nope", True, (255, 255, 255))
            screen.blit(yes_surf, yes_surf.get_rect(center=yes_rect.center))
            screen.blit(no_surf, no_surf.get_rect(center=no_rect.center))
            buy_confirm = (pc_row, pc_col, yes_rect, no_rect)


        btn_color = RED if bank_mode else DARK
        pygame.draw.rect(screen, btn_color, bank_btn, border_radius=25)
        pygame.draw.rect(screen, LIGHT, bank_btn, width=2, border_radius=25)
        font_btn = pygame.font.SysFont("arial", 26, bold=True)
        btn_label = "Cancel" if bank_mode else "Bank"
        btn_text = font_btn.render(btn_label, True, (255, 255, 255))
        screen.blit(btn_text, btn_text.get_rect(center=bank_btn.center))


        btn_color = RED if taxes_mode else DARK
        pygame.draw.rect(screen, btn_color, taxes_btn, border_radius=25)
        pygame.draw.rect(screen, LIGHT, taxes_btn, width=2, border_radius=25)
        btn_label = "Cancel" if taxes_mode else "Taxes"
        btn_text = font_btn.render(btn_label, True, (255, 255, 255))
        screen.blit(btn_text, btn_text.get_rect(center=taxes_btn.center))

        if bank_mode:
            inv_btn, loan_btn, wd_btn = draw_bank_menu(current_player, bank, money, debt, turn_count, active_input)

        if taxes_mode:
            draw_taxes_menu(current_player, money, debt, turn_count, last_tax_paid, next_tax_turn)


        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()