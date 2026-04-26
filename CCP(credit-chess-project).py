#Hi my name is uncle Sam, let's play a little game of chess will you ?
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
LIGHT = (225, 199, 159)
BOARD_SIZE = SQUARE_SIZE * 8
BOARD_RECT = pygame.Rect((WIDTH-BOARD_SIZE)//2, (HEIGHT-BOARD_SIZE)//2, BOARD_SIZE, BOARD_SIZE)
PANELW = 300
PANELX = WIDTH - PANELW
OFFSETX = (WIDTH - BOARD_SIZE) // 2
OFFSETY = (HEIGHT - BOARD_SIZE) // 2

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

def main():
    clock = pygame.time.Clock()
    setup_board()

    selected_tile = None #(row, col)
    sprites = load_sprites()
    current_player = "white" # or "black"
    valid_moves = []
    move_history = []
    en_passant_target = None
    game_over_message = None

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if not game_over_message and event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
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
                                captured = board[row][col] is not None

                                is_en_passant = (
                                    selected_piece.type == "pawn" and
                                    en_passant_target == (row, col) and
                                    board[row][col] is None
                                )
                                if is_en_passant:
                                    direction = -1 if selected_piece.color == "white" else 1
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

                                #store move in movre_history
                                move_history.append({
                                    "piece": board[row][col],
                                    "from": (sr, sc),
                                    "to": (row, col),
                                    "captured": captured
                                })

                                #switch sides
                                current_player = "black" if current_player == "white" else "white"

                                if is_checkmate(board, current_player, en_passant_target):
                                    winner = "black" if current_player == "white" else "white"
                                    game_over_message = f"{winner.capitalize()} wins by checkmate!"
                                elif is_stalemate(board, current_player, en_passant_target):
                                    game_over_message = "Stalemate! It's a draw."

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

        screen.fill(BG)
        #board outline
        pygame.draw.rect(screen, DARK_RED, BOARD_RECT.inflate(25, 25), border_radius=20)
        pygame.draw.rect(screen, DARK_RED, BOARD_RECT, border_radius = 15)
        #move history panel

        draw_board()
        draw_move_history(screen, move_history, sprites)
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

        draw_pieces(sprites)
        
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

        if game_over_message:
            draw_game_over(screen, game_over_message)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()