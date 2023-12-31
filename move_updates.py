import move_validation as validate
import check_for_check as check

import test


def display_moves(click1Pos, click2Pos, boardState, greenCircle, redCircle, inCheck, s, enPessantInfo):
    """
    Returns boardState with new 'moves' key to later blit onto board.
    Tries every single possible move and if it is a legal move, add a 'moves' key to the square.
    """

    # remove moves once click 2 is made
    if click2Pos:
        for x in range(8):
            for y in range(8):
                if "moves" in boardState[x][y]:
                    del boardState[x][y]["moves"]

    if click1Pos and click2Pos is None:
        for i in range(8):
            for j in range(8):
                if validate.legal_move(click1Pos, [i, j], 'capture', boardState, enPessantInfo):
                    if not inCheck:
                        boardState[i][j]['moves'] = redCircle
                    elif inCheck and check.did_move_resolve_check(click1Pos, [i, j], boardState, 'capture', s, True):
                        boardState[i][j]['moves'] = redCircle
                elif validate.legal_move(click1Pos, [i, j], 'move', boardState, enPessantInfo):
                    if not inCheck:
                        boardState[i][j]['moves'] = greenCircle
                    elif inCheck and check.did_move_resolve_check(click1Pos, [i, j], boardState, 'move', s, True):
                        boardState[i][j]['moves'] = greenCircle
                elif validate.legal_move(click1Pos, [i, j], 'castle', boardState, enPessantInfo):
                    boardState[i][j]['moves'] = greenCircle
    return boardState


def update_move(mapture, boardState, click1Pos, click2Pos, s):
    click1Piece = boardState[click1Pos[0]][click1Pos[1]]['piece']
    click1Color = click1Piece[0]

    if mapture == 'move':
        # if enPessant move
        if ('p' in click1Piece) and (abs(click1Pos[0] - click2Pos[0]) == 1) and (abs(click1Pos[1] - click2Pos[1]) == 1):
            # swap but replace initial with space
            boardState[click2Pos[0]][click2Pos[1]]['piece'], boardState[click2Pos[0]][click2Pos[1]]['image'] = \
                boardState[click1Pos[0]][click1Pos[1]]['piece'], boardState[click1Pos[0]][click1Pos[1]]['image']
            boardState[click1Pos[0]][click1Pos[1]]['piece'], boardState[click1Pos[0]][click1Pos[1]]['image'] = '--', s
            # make enPessanted pawn a space aswell
            if click1Color == 'w':
                boardState[click2Pos[0] + 1][click2Pos[1]]['piece'] = '--'
                boardState[click2Pos[0] + 1][click2Pos[1]]['image'] = s
            elif click1Color == 'b':
                boardState[click2Pos[0] - 1][click2Pos[1]]['piece'] = '--'
                boardState[click2Pos[0] - 1][click2Pos[1]]['image'] = s
        else:
            # swap piece and image with other piece and image
            boardState[click1Pos[0]][click1Pos[1]]['piece'], boardState[click2Pos[0]][click2Pos[1]]['piece'] = \
                boardState[click2Pos[0]][click2Pos[1]]['piece'], boardState[click1Pos[0]][click1Pos[1]]['piece']
            boardState[click1Pos[0]][click1Pos[1]]['image'], boardState[click2Pos[0]][click2Pos[1]]['image'] = \
                boardState[click2Pos[0]][click2Pos[1]]['image'], boardState[click1Pos[0]][click1Pos[1]]['image']

    elif mapture == 'capture':
        # swap but replace initial with space
        boardState[click2Pos[0]][click2Pos[1]]['piece'], boardState[click2Pos[0]][click2Pos[1]]['image'] = \
            boardState[click1Pos[0]][click1Pos[1]]['piece'], boardState[click1Pos[0]][click1Pos[1]]['image']
        boardState[click1Pos[0]][click1Pos[1]]['piece'] = '--'
        boardState[click1Pos[0]][click1Pos[1]]['image'] = s

    elif mapture == 'castle':
        if click1Color == 'w':
            i = 7
        elif click1Color == 'b':
            i = 0

        if click2Pos == (i, 7) or click2Pos == (i, 6):
            boardState[i][6]['piece'], boardState[i][6]['image'] = boardState[i][4]['piece'], boardState[i][4]['image']
            boardState[i][5]['piece'], boardState[i][5]['image'] = boardState[i][7]['piece'], boardState[i][7]['image']
            boardState[i][4]['piece'], boardState[i][4]['image'] = '--', s
            boardState[i][7]['piece'], boardState[i][7]['image'] = '--', s
        elif click2Pos == (i, 0) or click2Pos == (i, 2):
            boardState[i][3]['piece'], boardState[i][3]['image'] = boardState[i][0]['piece'], boardState[i][0]['image']
            boardState[i][2]['piece'], boardState[i][2]['image'] = boardState[i][4]['piece'], boardState[i][4]['image']
            boardState[i][0]['piece'], boardState[i][0]['image'] = '--', s
            boardState[i][4]['piece'], boardState[i][4]['image'] = '--', s
    return boardState


def move_type(piece1, piece2):
    if (piece1 == 'wk' and piece2 == 'wr') or (piece1 == 'bk' and piece2 == 'br'):
        return 'castle'
    # if second square clicked is space
    elif (piece1[0] == 'w' and piece2[0] == '-') or (piece1[0] == 'b' and piece2[0] == '-'):
        return 'move'
    # if second square clicked is piece
    elif ((piece1[0] == 'w' and piece2[0] == 'b') or (piece1[0] == 'b' and piece2[0] == 'w')):
        return 'capture'


def generate_FEN(boardState, click1Piece):
    fenString = ''
    spaceCount = 0
    castleFen = ''
    # if black is selected, click1Piece is still None so manually change to black so engine will make the first move
    if click1Piece is None:
        click1Piece = 'bb'
    for i in range(8):
        for j in range(8):
            # convert spaces
            # keep a count of each space
            if boardState[i][j]['piece'] == '--':
                spaceCount += 1
            # if this piece isn't a space, add the space count to fen string
            if spaceCount != 0 and boardState[i][j]['piece'] != '--':
                fenString += str(spaceCount)
                spaceCount = 0
            # if it's the end of a row, add the space count
            elif j == 7 and spaceCount != 0:
                fenString += str(spaceCount)
                spaceCount = 0

            if 'b' in boardState[i][j]['piece'] and boardState[i][j]['piece'] != 'wb':
                piece = boardState[i][j]['piece'][1]
                fenString += piece
            # same as black but capitalize the piece
            elif 'w' in boardState[i][j]['piece']:
                piece = boardState[i][j]['piece'][1]
                piece = piece.upper()
                fenString += piece

            # add dash at the end of every row but not at the very end
            if j == 7 and i != 7:
                fenString += '/'

            # figure out which colors have what castleing option
            if boardState[i][j]['piece'] == 'wk':
                if boardState[7][7]['piece'] == 'wr':
                    castleFen += 'K'
                if boardState[7][0]['piece'] == 'wr':
                    castleFen += 'Q'
            elif boardState[i][j]['piece'] == 'bk':
                if boardState[0][7]['piece'] == 'br':
                    castleFen += 'k'
                if boardState[0][0]['piece'] == 'br':
                    castleFen += 'q'
    # add who's turn it is, i.e. opposite color of whoever just made a move
    if click1Piece[0] == 'w':
        fenString += ' b'
    elif click1Piece[0] == 'b':
        fenString += ' w'
    # add castleing options
    if castleFen != '':
        # add space for castling options
        fenString += ' '
        # reorder so white's options always come first
        castleOptions = ['K', 'Q', 'k', 'q']
        for option in castleOptions:
            if option in castleFen:
                fenString += f'{option}'
    return fenString


def parse_engine_move(move):
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    move = str(move)
    promotionPiece = None
    # standard move (ex. g8f6)
    click1 = move[0:2]
    click2 = move[2:4]
    # promotion move (ex. a7a8q)
    if len(move) == 5:
        promotionPiece = move[4]
    # switch from letter to numbers
    for index, value in enumerate(letters):
        if value in click1:
            click1 = click1.replace(value, str(index))
        if value in click2:
            click2 = click2.replace(value, str(index))
    # swap number positions so it goes y,x
    click1Pos = 8 - int(click1[1]), int(click1[0])
    click2Pos = 8 - int(click2[1]), int(click2[0])

    return click1Pos, click2Pos, promotionPiece
