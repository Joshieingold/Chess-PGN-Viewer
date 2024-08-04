# Librarys being used.
import tkinter as tk
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
    if IsValidMove(board, from_location, to_location):
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
    print(FEN)
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
    if SwitchTurn(board, from_pos, to_pos) == True:
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
    else:
        return
# Formulates Ranks from numbers
def FormulateRank(number):
    if number == 0:
        return "8"
    elif number == 1:
        return "7"
    elif number == 2:
        return "6"
    elif number == 3:
        return "5"
    elif number == 4:
        return "4"
    elif number == 5:
        return "3"
    elif number == 6:
        return "2"
    elif number == 7:
        return "1"
    else:
        return

# Adds to the PGN NEEDS TO GO AFTER CHECKS
def AddPGN(board, from_pos, to_pos):
    global PGN
    global turn_num
    from_file, from_rank = from_pos
    to_file, to_rank = to_pos
    final = ""

    # Determine the piece being moved
    piece = board[from_rank][from_file].upper()
    to_file_str = FormulateFile(to_file)
    to_rank_str = FormulateRank(to_rank)

    # Handle pawn moves separately
    if piece == "P":
        if from_file != to_file and board[to_rank][to_file] != " ":
            final += FormulateFile(from_file).lower() + "x" + to_file_str + to_rank_str
        else:
            final += to_file_str + to_rank_str
    else:
        final += piece
        if board[to_rank][to_file] != " ":
            final += "x"
        final += to_file_str + to_rank_str
    if turn_num % 2 == 1:
        PGN.append(f"{(turn_num + 1) // 2}.")
    PGN.append(final)
    CreatePGN(PGN)
# Prints the Completed PGN
def CreatePGN(PGN):
    print(" ".join(PGN))

# Need to consider Check and Checkmate.

# Checks whose Turn it is and only lets that player move.
def SwitchTurn(board, from_pos, to_pos):
    global turn_num
    from_file, from_rank = from_pos
    if turn_num % 2 != 1:
        if board[from_rank][from_file].islower():
            AddPGN(board, from_pos, to_pos)
            turn_num += 1
            return True
        else:
            return False
    else:
        if board[from_rank][from_file].isupper():
            AddPGN(board, from_pos, to_pos)
            turn_num += 1
            return True
        else:
            return False
# Checks to see if the Piece being moved is trying to move to another friendly pieces location and will not let it if it wont.
def SameTeamCheck(board, from_pos, to_pos):
    from_file, from_rank = from_pos
    to_file, to_rank = to_pos

    from_piece = board[from_rank][from_file]
    to_piece = board[to_rank][to_file]

    # White pieces are uppercase, black pieces are lowercase
    if from_piece.isupper():
        if to_piece.isupper() and to_piece != " ":
            return False
    else:
        if to_piece.islower() and to_piece != " ":
            return False

    return True

# Creates the window that runs the GUI, Also handles getting selection in the array.
def RunWindow():
    window = tk.Tk()
    window.title("Chess PGN Viewer")
    window.geometry("600x700")
    gui_board = tk.Canvas(window, width=600, height=600, bg="white")
    gui_board.pack(side=tk.TOP)
    control_frame = tk.Frame(window)
    control_frame.pack(side=tk.BOTTOM)
    status_label = tk.Label(control_frame, text="Select a piece to move.")
    status_label.pack()
    fen_label = tk.Label(control_frame, text="Enter FEN:")
    fen_label.pack(side=tk.LEFT)
    fen_entry = tk.Entry(control_frame)
    fen_entry.pack(side=tk.LEFT)
    import_button = tk.Button(control_frame, text="Import FEN", command=lambda: on_import_fen(fen_entry.get()))
    import_button.pack(side=tk.LEFT)
    selected_piece = None
    selected_pos = None
    board = CreateBoard()

    # Load images with absolute paths
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

    # Finds the location in the board array that was clicked on in the GUI
    def on_square_click(event):
        nonlocal selected_piece, selected_pos
        x, y = event.x, event.y
        file, rank = x // 75, y // 75

        if selected_piece is None:
            # Selecting a piece to move
            if board[rank][file] != " ":
                selected_piece = board[rank][file]
                selected_pos = (file, rank)
                status_label.config(text=f"Selected {selected_piece} at {chr(file + 97)}{8 - rank}. Now select destination.")
        else:
            # Moving the selected piece
            ArrayTransfer(board, selected_pos, (file, rank))
            DrawBoard(gui_board, board, piece_images)
            CreateFEN(board)
            selected_piece = None
            selected_pos = None
            status_label.config(text="Select a piece to move.")

    # Handles importing the FEN string
    def on_import_fen(fen):
        ImportFEN(board, fen)
        DrawBoard(gui_board, board, piece_images)

    gui_board.bind("<Button-1>", on_square_click)
    DrawBoard(gui_board, board, piece_images)
    window.mainloop()

RunWindow()
