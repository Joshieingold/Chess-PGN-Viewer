import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
from PIL import Image, ImageTk
import os
import clipboard

# Global Variables
turn_num = 1
global PGN
PGN = []

# Creates a fresh chess board for the use of the game.
def CreateBoard():
    board = []
    black_minor_pieces = ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r']
    black_pawns = ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p']
    white_minor_pieces = ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
    white_pawns = ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P']
    blank_spaces = [" ", " ", " ", " ", " ", " ", " ", " "]
    board.append(black_minor_pieces)
    board.append(black_pawns)
    for space in range(4):
        board.append(blank_spaces[:])
    board.append(white_pawns)
    board.append(white_minor_pieces)
    return board

# Prints the chess board into the console.
def PrintConsoleBoard(board):
    for i in board:
        print(i)

# Does the logic for making the 64 squares of a chess board.
def DrawBoard(gui_board, board, images):
    gui_board.delete("all")  # Clear the current board
    for i in range(8):
        for j in range(8):
            x0, y0 = i * 75, j * 75
            x1, y1 = x0 + 75, y0 + 75
            color = "#769656" if (i + j) % 2 == 0 else "#eeeed2"
            gui_board.create_rectangle(x0, y0, x1, y1, fill=color)
            piece = board[j][i]
            if piece != " ":
                gui_board.create_image((x0 + x1) // 2, (y0 + y1) // 2, image=images[piece])

# Takes the location of your selected piece in the array and moves it to the next selected place.
def ArrayTransfer(board, from_location, to_location):
    if SwitchTurn(board, from_location, to_location):
        file_from, rank_from = from_location
        file_to, rank_to = to_location

        piece = board[rank_from][file_from]
        board[rank_from][file_from] = " "
        board[rank_to][file_to] = piece

# Prints a FEN to the console after every move.
def CreateFEN(board):
    FEN = ""
    for ranks in board:
        count = 0
        if len(FEN) > 0:
            FEN += "/"
        for piece in ranks:
            if piece == " ":
                count += 1
            else:
                if count > 0:
                    FEN += str(count)
                    count = 0
                FEN += piece
        if count > 0:
            FEN += str(count)
    clipboard.copy(FEN)

# Imports a FEN string into the board
def ImportFEN(board, fen):
    imported_FEN = fen.split("/")
    new_board = []
    for fen_rank in imported_FEN:
        new_rank = []
        for char in fen_rank:
            if char.isdigit():
                new_rank.extend([" "] * int(char))
            else:
                new_rank.append(char)
        new_board.append(new_rank)
    for i in range(8):
        board[i] = new_board[i]

# Checks if a move is valid
def IsValidMove(board, from_pos, to_pos):
    piece = board[from_pos[1]][from_pos[0]]

    if piece.lower() == 'p':
        return IsValidPawnMove(board, from_pos, to_pos, piece.isupper())
    elif piece.lower() == 'r':
        return IsValidRookMove(board, from_pos, to_pos)
    elif piece.lower() == 'n':
        return IsValidKnightMove(board, from_pos, to_pos)
    elif piece.lower() == 'b':
        return IsValidBishopMove(board, from_pos, to_pos)
    elif piece.lower() == 'q':
        return IsValidQueenMove(board, from_pos, to_pos)
    elif piece.lower() == 'k':
        return IsValidKingMove(board, from_pos, to_pos)
    return False

# Pawn move validation
def IsValidPawnMove(board, from_pos, to_pos, is_white):
    from_file, from_rank = from_pos
    to_file, to_rank = to_pos

    direction = -1 if is_white else 1  # White pawns move up (-1), black pawns move down (+1)

    # Normal move (one square forward)
    if to_file == from_file and to_rank == from_rank + direction:
        if board[to_rank][to_file] == " ":
            return True

    # Double move (two squares forward from starting position)
    if to_file == from_file and to_rank == from_rank + 2 * direction:
        if (from_rank == 6 and is_white) or (from_rank == 1 and not is_white):
            if board[from_rank + direction][from_file] == " " and board[to_rank][to_file] == " ":
                return True

    # Capturing move (one square diagonally forward)
    if abs(to_file - from_file) == 1 and to_rank == from_rank + direction:
        if board[to_rank][to_file] != " " and board[to_rank][to_file].isupper() != is_white:
            return True

    # Don't take your own pieces loser.
    SameTeamCheck(board, from_pos, to_pos)

    return False

# Rook move validation
def IsValidRookMove(board, from_pos, to_pos):
    from_file, from_rank = from_pos
    to_file, to_rank = to_pos

    if from_file != to_file and from_rank != to_rank:
        return False

    if from_file == to_file:
        step = 1 if to_rank > from_rank else -1
        for rank in range(from_rank + step, to_rank, step):
            if board[rank][from_file] != " ":
                return False
    elif from_rank == to_rank:
        step = 1 if to_file > from_file else -1
        for file in range(from_file + step, to_file, step):
            if board[from_rank][file] != " ":
                return False

    return SameTeamCheck(board, from_pos, to_pos)

# Knight move validation
def IsValidKnightMove(board, from_pos, to_pos):
    from_file, from_rank = from_pos
    to_file, to_rank = to_pos

    if (abs(from_file - to_file), abs(from_rank - to_rank)) in [(1, 2), (2, 1)]:
        return SameTeamCheck(board, from_pos, to_pos)

# Bishop move validation
def IsValidBishopMove(board, from_pos, to_pos):
    from_file, from_rank = from_pos
    to_file, to_rank = to_pos

    if abs(from_file - to_file) != abs(from_rank - to_rank):
        return False

    file_step = 1 if to_file > from_file else -1
    rank_step = 1 if to_rank > from_rank else -1
    for file, rank in zip(range(from_file + file_step, to_file, file_step), range(from_rank + rank_step, to_rank, rank_step)):
        if board[rank][file] != " ":
            return False

    return SameTeamCheck(board, from_pos, to_pos)

# Queen move validation
def IsValidQueenMove(board, from_pos, to_pos):
    if IsValidRookMove(board, from_pos, to_pos) or IsValidBishopMove(board, from_pos, to_pos):
        return SameTeamCheck(board, from_pos, to_pos)

# King move validation
def IsValidKingMove(board, from_pos, to_pos):
    from_file, from_rank = from_pos
    to_file, to_rank = to_pos

    if max(abs(from_file - to_file), abs(from_rank - to_rank)) == 1:
        return SameTeamCheck(board, from_pos, to_pos)

# Formulates files from numbers
def FormulateFile(number):
    if number == 0:
        return "a"
    elif number == 1:
        return "b"
    elif number == 2:
        return "c"
    elif number == 3:
        return "d"
    elif number == 4:
        return "e"
    elif number == 5:
        return "f"
    elif number == 6:
        return "g"
    elif number == 7:
        return "h"

# Formulates numbers from files
def FormulateRank(file):
    if file == 0:
        return "8"
    elif file == 1:
        return "7"
    elif file == 2:
        return "6"
    elif file == 3:
        return "5"
    elif file == 4:
        return "4"
    elif file == 5:
        return "3"
    elif file == 6:
        return "2"
    elif file == 7:
        return "1"

# Changes turn to ensure legality.
def SwitchTurn(board, from_pos, to_pos):
    global turn_num
    turn = 'W' if turn_num % 2 == 1 else 'B'

    piece = board[from_pos[1]][from_pos[0]]
    if piece == ' ':
        return False

    if (piece.isupper() and turn == 'W') or (piece.islower() and turn == 'B'):
        if IsValidMove(board, from_pos, to_pos):
            turn_num += 1
            MoveMemory(board, from_pos, to_pos, turn)
            return True

    return False

# Keeps track of what moves were played in memory
def MoveMemory(board, from_pos, to_pos, turn):
    global PGN
    from_file, from_rank = from_pos
    to_file, to_rank = to_pos
    move_number = str((turn_num + 1) // 2)
    
    piece = board[from_rank][from_file]

    from_square = str(FormulateFile(from_file)) + str(FormulateRank(from_rank))
    to_square = str(FormulateFile(to_file)) + str(FormulateRank(to_rank))
    move = ""
    if piece.lower() == "p":
        if board[to_pos[1]][to_pos[0]] != " ":
            move += from_square[0] 
            move += "x"
        move += to_square
    else:
        move += piece.upper()
        if board[to_pos[1]][to_pos[0]] != " ":
            move += "x"
        move += to_square
    if turn == 'W':
        PGN.append(move)
    else:
        PGN[-1] += " " + move

# Returns false if the move is on the same team.
def SameTeamCheck(board, from_pos, to_pos):
    from_piece = board[from_pos[1]][from_pos[0]]
    to_piece = board[to_pos[1]][to_pos[0]]

    if to_piece != " " and (from_piece.isupper() and to_piece.isupper() or from_piece.islower() and to_piece.islower()):
        return False

    return True

# Gradient Navbar
def create_gradient(canvas, color1, color2):
    width = canvas.winfo_reqwidth()
    height = canvas.winfo_reqheight()
    limit = height
    (r1, g1, b1) = canvas.winfo_rgb(color1)
    (r2, g2, b2) = canvas.winfo_rgb(color2)
    r_ratio = float(r2 - r1) / limit
    g_ratio = float(g2 - g1) / limit
    b_ratio = float(b2 - b1) / limit

    for i in range(limit):
        nr = int(r1 + (r_ratio * i))
        ng = int(g1 + (g_ratio * i))
        nb = int(b1 + (b_ratio * i))
        color = f'#{nr:04x}{ng:04x}{nb:04x}'
        canvas.create_line(0, i, width, i, fill=color)


# GUI Setup
class ChessGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess PGN Viewer")

        # Top gradient navbar
        self.navbar = tk.Canvas(root, height=40, bg="blue")
        self.navbar.pack(fill=tk.X)
        create_gradient(self.navbar, "#1E90FF", "#87CEEB")

        self.import_fen_button = tk.Button(root, text="Import FEN", command=self.import_fen)
        self.navbar.create_window(50, 25, window=self.import_fen_button)

        self.copy_pgn_button = tk.Button(root, text="Copy PGN", command=self.copy_pgn)
        self.navbar.create_window(150, 25, window=self.copy_pgn_button)

        self.copy_fen_button = tk.Button(root, text="Copy FEN", command=self.copy_fen)
        self.navbar.create_window(250, 25, window=self.copy_fen_button)

        # Main frame
        self.main_frame = tk.Frame(root, height="300")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Side tab for PGN
        self.pgn_frame = tk.Frame(self.main_frame, width=200, bg="#121111")
        self.pgn_frame.pack(side=tk.RIGHT, fill=tk.Y)
        self.pgn_label = tk.Label(self.pgn_frame, text="PGN:", bg='#121111', fg='#ffffff', padx = 10, pady = 5)
        self.pgn_label.pack(anchor=tk.NW)
        self.pgn_text = tk.Text(self.pgn_frame, height=40, width=25, bg="#292929", fg="#ffffff", state=tk.DISABLED)
        self.pgn_text.pack(anchor=tk.NW, padx=10, pady=10)

        # Canvas for chess board
        self.board_canvas = tk.Canvas(self.main_frame, width=600, height=600, bg="#121111")
        self.board_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.images = self.load_images()
        self.board = CreateBoard()
        DrawBoard(self.board_canvas, self.board, self.images)

        # Bind clicks
        self.board_canvas.bind("<Button-1>", self.on_board_click)
        self.selected_piece = None

    def load_images(self):
        base_path = os.path.join(os.path.dirname(__file__), "images")
        piece_images = {
        'r': ImageTk.PhotoImage(Image.open(os.path.join(base_path, "br.png"))),
        'n': ImageTk.PhotoImage(Image.open(os.path.join(base_path, "bn.png"))),
        'b': ImageTk.PhotoImage(Image.open(os.path.join(base_path, "bb.png"))),
        'q': ImageTk.PhotoImage(Image.open(os.path.join(base_path, "bq.png"))),
        'k': ImageTk.PhotoImage(Image.open(os.path.join(base_path, "bk.png"))),
        'p': ImageTk.PhotoImage(Image.open(os.path.join(base_path, "bp.png"))),
        'R': ImageTk.PhotoImage(Image.open(os.path.join(base_path, "wr.png"))),
        'N': ImageTk.PhotoImage(Image.open(os.path.join(base_path, "wn.png"))),
        'B': ImageTk.PhotoImage(Image.open(os.path.join(base_path, "wb.png"))),
        'Q': ImageTk.PhotoImage(Image.open(os.path.join(base_path, "wq.png"))),
        'K': ImageTk.PhotoImage(Image.open(os.path.join(base_path, "wk.png"))),
        'P': ImageTk.PhotoImage(Image.open(os.path.join(base_path, "wp.png")))
    }
        return piece_images

    def on_board_click(self, event):
        file = event.x // 75
        rank = event.y // 75
        if self.selected_piece:
            to_location = (file, rank)
            from_location = self.selected_piece
            ArrayTransfer(self.board, from_location, to_location)
            self.selected_piece = None
            DrawBoard(self.board_canvas, self.board, self.images)
            self.update_pgn_text()
        else:
            self.selected_piece = (file, rank)

    def update_pgn_text(self):
        self.pgn_text.config(state=tk.NORMAL)
        self.pgn_text.delete(1.0, tk.END)
        for move in PGN:
            self.pgn_text.insert(tk.END, move + "\n")
        self.pgn_text.config(state=tk.DISABLED)

    def import_fen(self):
        fen = tk.simpledialog.askstring("Import FEN", "Enter FEN string:")
        if fen:
            ImportFEN(self.board, fen)
            DrawBoard(self.board_canvas, self.board, self.images)

    def copy_pgn(self):
        pgn_string = " ".join(PGN)
        clipboard.copy(pgn_string)


    def copy_fen(self):
        CreateFEN(self.board)

if __name__ == "__main__":
    root = tk.Tk()
    app = ChessGUI(root)
    root.mainloop()
