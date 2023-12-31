import pygame
from sys import exit
import chess
import chess.engine


import move_updates as update
import move_validation as validate
import check_for_check as check
import images
import engine_file_path as path
import test

# initialize pygame window
pygame.init()
pygame.display.set_caption('Chess')
clock = pygame.time.Clock()

# load in all pieces and adjust sizes
wb = pygame.image.load('images/w_bishop.png')
wk = pygame.image.load('images/w_king.png')
wn = pygame.image.load('images/w_knight.png')
wp = pygame.image.load('images/w_pawn.png')
wq = pygame.image.load('images/w_queen.png')
wr = pygame.image.load('images/w_rook.png')
bb = pygame.image.load('images/b_bishop.png')
bk = pygame.image.load('images/b_king.png')
bn = pygame.image.load('images/b_knight.png')
bp = pygame.image.load('images/b_pawn.png')
bq = pygame.image.load('images/b_queen.png')
br = pygame.image.load('images/b_rook.png')
space = pygame.image.load('images/transparent_image.png')
greenCircle = pygame.image.load('images/green_circle.png')
redCircle = pygame.image.load('images/red_circle.webp')
greenCircle = pygame.transform.scale(greenCircle, (20, 20))
redCircle = pygame.transform.scale(redCircle, (25, 25))

s = pygame.transform.scale(space, (60, 60))

# load in menu images
onePlayerImg = pygame.image.load('images/single_player.png')
twoPlayerImg = pygame.image.load('images/two_player.png')

# load board and get dimensions
board = pygame.image.load('images/empty_chess_board.png')
boardBackground = pygame.image.load('images/empty_chess_board.png')
board = pygame.transform.scale(board, (560, 560))
boardBackground = pygame.transform.scale(boardBackground, (560, 560))
boardRect = board.get_rect()
screen = pygame.display.set_mode((boardRect.width, boardRect.height))


boardState = [
    [{'piece': "br", 'image': br}, {'piece': "bn", 'image': bn},
     {'piece': "bb", 'image': bb}, {'piece': "bq", 'image': bq},
     {'piece': "bk", 'image': bk}, {'piece': "bb", 'image': bb},
     {'piece': "bn", 'image': bn}, {'piece': "br", 'image': br}],

    [{'piece': "bp", 'image': bp}, {'piece': "bp", 'image': bp},
     {'piece': "bp", 'image': bp}, {'piece': "bp", 'image': bp},
     {'piece': "bp", 'image': bp}, {'piece': "bp", 'image': bp},
     {'piece': "bp", 'image': bp}, {'piece': "bp", 'image': bp}],

    [{'piece': "--", 'image': s}, {'piece': "--", 'image': s},
     {'piece': "--", 'image': s}, {'piece': "--", 'image': s},
     {'piece': "--", 'image': s}, {'piece': "--", 'image': s},
     {'piece': "--", 'image': s}, {'piece': "--", 'image': s}],

    [{'piece': "--", 'image': s}, {'piece': "--", 'image': s},
     {'piece': "--", 'image': s}, {'piece': "--", 'image': s},
     {'piece': "--", 'image': s}, {'piece': "--", 'image': s},
     {'piece': "--", 'image': s}, {'piece': "--", 'image': s}],

    [{'piece': "--", 'image': s}, {'piece': "--", 'image': s},
     {'piece': "--", 'image': s}, {'piece': "--", 'image': s},
     {'piece': "--", 'image': s}, {'piece': "--", 'image': s},
     {'piece': "--", 'image': s}, {'piece': "--", 'image': s}],

    [{'piece': "--", 'image': s}, {'piece': "--", 'image': s},
     {'piece': "--", 'image': s}, {'piece': "--", 'image': s},
     {'piece': "--", 'image': s}, {'piece': "--", 'image': s},
     {'piece': "--", 'image': s}, {'piece': "--", 'image': s}],

    [{'piece': "wp", 'image': wp}, {'piece': "wp", 'image': wp},
     {'piece': "wp", 'image': wp}, {'piece': "wp", 'image': wp},
     {'piece': "wp", 'image': wp}, {'piece': "wp", 'image': wp},
     {'piece': "wp", 'image': wp}, {'piece': "wp", 'image': wp}],

    [{'piece': "wr", 'image': wr}, {'piece': "wn", 'image': wn},
     {'piece': "wb", 'image': wb}, {'piece': "wq", 'image': wq},
     {'piece': "wk", 'image': wk}, {'piece': "wb", 'image': wb},
     {'piece': "wn", 'image': wn}, {'piece': "wr", 'image': wr}],
]


# make tile for each square to see mouse collision
tile = []
# minor adjustment so piece blitted somewhat centered
rowSpace = 4
colSpace = 8
rowCount = 0
turnCount = 0
for col in boardState:
    for row in col:
        # get rect from piece image to check if it is clicked
        # guess and check dimensions
        rect = row['image'].get_rect(topleft=(rowSpace-2.3, colSpace-5.8))
        rect = pygame.Rect(rect.left, rect.top, int(rect.width * 1.16), int(rect.height * 1.14))
        tile.append(rect)
        rowSpace += 70
        rowCount += 1
        if rowCount == 8:
            colSpace += 70
            rowCount = 0
            rowSpace = 4
        if colSpace == 568:
            colSpace = 8
# add square key to boardState to check for mouse collision
tileCount = 0
for x in range(8):
    for y in range(8):
        # add square field and add tile to it to check if it is clicked
        boardState[x][y]['square'] = tile[tileCount]
        tileCount += 1

# initialize variables
click1Piece, click2Piece, click1Pos, click2Pos, mapture, gameOver, pawnPos, originalBoardState, promotionPiece = (None,) * 9
inCheck, started, onePlayerMode, twoPlayerMode, enPessantInfo, promotionMenu, bool, colorClicked, engineTurn, engineSkip = (False, ) * 10
clickCount, loopCount = (0, ) * 2
firstTimeColorClicked = True

# initialize menu image objects & images
onePlayer = images.Button(239, 73, onePlayerImg, 0.12)
twoPlayer = images.Button(231, 170, twoPlayerImg, 0.14)

# adjust transparency of background
boardBackground = boardBackground.convert_alpha()
boardBackground.set_alpha(190)

# initialize variables to write text on screen
menuFont = pygame.font.Font('fonts/CaviarDreams.ttf', 45)
endFont = pygame.font.Font('fonts/CaviarDreams.ttf', 30)
text = 'Select Mode'
textSurface = menuFont.render(text, True, (50, 50, 50))
textRect = textSurface.get_rect()
textRect.topleft = (150, 10)

# initialize engine for single player
enginePath = path.engineFilePath()
engine = chess.engine.SimpleEngine.popen_uci(enginePath)

while True:
    if not gameOver and not started:
        # fill with initial menu screen
        screen.fill((255, 255, 255))
        screen.blit(boardBackground, boardRect)
        screen.blit(textSurface, textRect)

    # check if one player or two player icon clicked
    if not started:
        onePlayer.draw(screen)
        twoPlayer.draw(screen)
        if onePlayer.clicked or twoPlayer.clicked:
            started = True
            click1Pos, click2Pos = None, None
            if onePlayer.clicked:
                onePlayerMode = True
            else:
                twoPlayerMode = True
        # Check for closing window in game menu screen
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
    if gameOver:
        loopCount += 1
    if loopCount > 1:
        if click1Piece[0] == 'w':
            text = 'White Wins!'
        elif click1Piece[0] == 'b':
            text = 'Black Wins!'
        winSurface = endFont.render(text, True, (0, 178, 42))
        winRect = winSurface.get_rect()
        winRect.center = (280, 280)
        pygame.draw.rect(screen, (255, 255, 255), winRect)
        screen.blit(winSurface, winRect)

        # check for closing window in game over screen
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        pygame.display.update()
        clock.tick(60)
        continue
    # if either icon was clicked
    if started:
        # placed here so it works for both one and two player modes
        if promotionMenu:
            promotionMenuClicked = False
            clickedPiece = None
            for event in pygame.event.get():
                # check for closing window in promotion menu
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    promotionMenuClicked = True
            if pawnPos[0] == 0:
                # if white pawn promoting, draw it and specify dictionary keys to white pieces
                clickedPiece = {
                    'piece': images.promotion_menu(screen, [wq, wn, wr, wb], 'w', pawnPos[1], promotionMenuClicked, colorClicked),
                    'name': ['wq', 'wn', 'wr', 'wb'],
                    'var': [wq, wn, wr, wb]
                }
            elif pawnPos[0] == 7:
                # if black pawn promoting, draw it and specificy dictinoary keys to black pieces
                clickedPiece = {
                    'piece': images.promotion_menu(screen, [bq, bn, br, bb], 'b', pawnPos[1], promotionMenuClicked, colorClicked),
                    'name': ['bq', 'bn', 'br', 'bb'],
                    'var': [bq, bn, br, bb]
                }
            # if user clicks something
            if clickedPiece['piece'] is not None:
                promotionMenu = False
                # if user clicks anything outside of promotion menu, undo the move
                if clickedPiece['piece'] == 'nothing':
                    boardState = originalBoardState
                    if turnCount == 1:
                        turnCount = 0
                    elif turnCount == 0:
                        turnCount = 1
                    continue
                elif clickedPiece['piece'] == 'queen':
                    index = 0
                elif clickedPiece['piece'] == 'knight':
                    index = 1
                elif clickedPiece['piece'] == 'rook':
                    index = 2
                elif clickedPiece['piece'] == 'bishop':
                    index = 3
                boardState[pawnPos[0]][pawnPos[1]]['piece'] = clickedPiece['name'][index]
                boardState[pawnPos[0]][pawnPos[1]]['image'] = clickedPiece['var'][index]
                # add redSquare if move made put king in check
                if isinstance(
                    check.is_check_after_move(
                        clickedPiece['name'][index], pawnPos, boardState
                    ),
                    tuple
                ):
                    boardState = check.is_check_after_move(clickedPiece['name'][index], pawnPos, boardState)[1]
                if check.checkmate(boardState, s):
                    gameOver = True

            pygame.display.update()
            clock.tick(60)
            continue
        if twoPlayerMode:
            # main game event loop
            for event in pygame.event.get():
                # check for closing window in game
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                # event.button == 1 is a left click
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # get info about click pos
                    boardState, click1Pos, click1Piece, click2Pos, click2Piece, clickCount = \
                        validate.get_click_piece_pos(
                            boardState, clickCount, click1Pos, click1Piece, click2Pos, click2Piece
                        )
                    if click1Pos or click2Pos:
                        # display moves if clicked
                        boardState = update.display_moves(
                            click1Pos, click2Pos, boardState, greenCircle, redCircle, inCheck, s, enPessantInfo
                        )
                    if click1Pos and click2Pos:
                        # figure out if move or capture
                        mapture = update.move_type(click1Piece, click2Piece)
                        if validate.legal_move(click1Pos, click2Pos, mapture, boardState, enPessantInfo) and \
                                (validate.turn_counter(click1Piece, click2Piece, turnCount, mapture)[0]) and \
                                check.did_move_resolve_check(click1Pos, click2Pos, boardState, mapture, s):
                            # check if en pessant opportunity is there
                            enPessantInfo = validate.legal_move(
                                click1Pos, click2Pos, mapture, boardState, enPessantInfo
                            )
                            if inCheck:
                                # check if move made after check made it so not in check
                                if isinstance(check.did_move_resolve_check(
                                    click1Pos, click2Pos, boardState, mapture, s
                                        ), tuple):
                                    inCheck = False
                                    boardState = check.did_move_resolve_check(
                                        click1Pos, click2Pos, boardState, mapture, s
                                    )[1]
                                else:
                                    # reset click positions because invalid move
                                    click1Pos, click2Pos = None, None
                                    continue

                            # check if king put its self in check
                            elif 'k' in click1Piece and \
                                    not isinstance(check.did_move_resolve_check(
                                        click1Pos, click2Pos, boardState, mapture, s
                                    ), tuple):
                                # reset click positions and skip this loop iteration
                                click1Pos, click2Pos = None, None
                                continue

                            # since nothing failed, must be a valid move so update it
                            if 'p' in click1Piece or 'k' in click1Piece:
                                # add m to keep track of pawn and king moves. Pawn is for two space move, king is for castleing
                                boardState[click1Pos[0]][click1Pos[1]]['piece'] += 'm'
                            # check if a pawn can promote
                            if validate.check_promotion(click1Pos, click2Pos, mapture, boardState, s):
                                promotionMenu = True
                                bool, pawnPos, originalBoardState = validate.check_promotion(
                                    click1Pos, click2Pos, mapture, boardState, s
                                )
                            # update move based on move or capture
                            boardState = update.update_move(mapture, boardState, click1Pos, click2Pos, s)
                            # update turn count
                            turnCount = validate.turn_counter(click1Piece, click2Piece, turnCount, mapture)[1]

                            # see if move put king in check
                            if isinstance(check.is_check_after_move(click1Piece, click2Pos, boardState), tuple):
                                inCheck = True
                                boardState = check.is_check_after_move(click1Piece, click2Pos, boardState)[1]

                            # clear click pos b/c messes up click1Pos or click2Pos statements and more idk
                            click1Pos, click2Pos = None, None
                        else:
                            print("clearing pos")
                            print("--------------")
                            # still clear if not legal move
                            click1Pos, click2Pos = None, None
                    if check.checkmate(boardState, s):
                        gameOver = True

            # blit board rectangles
            screen.blit(board, boardRect)
            for col in boardState:
                for row in col:
                    try:
                        screen.blit(row['check'], (rowSpace-3.01, colSpace-8))
                    except KeyError:
                        pass
                    # blit pieces on board
                    screen.blit(row["image"], (rowSpace, colSpace))
                    try:
                        # blit green/red circle on board
                        screen.blit(row["moves"], (rowSpace+20, colSpace+16))
                    except KeyError:
                        pass
                    rowSpace += 70
                    rowCount += 1
                    if rowCount == 8:
                        colSpace += 70
                        rowCount = 0
                        rowSpace = 4
                    if colSpace == 568:
                        colSpace = 8
        if onePlayerMode:
            # display options to choose color
            text = 'Select Color'
            textSurface = menuFont.render(text, True, (50, 50, 50))
            textRect = textSurface.get_rect()
            textRect.topleft = (150, 10)
            screen.blit(board, boardRect)
            screen.blit(textSurface, textRect)

            # display color options
            white = images.Button(210, 140, wk, 1.15)
            black = images.Button(280, 140, bk, 1.15)
            white.draw(screen)
            black.draw(screen)

            # not firstTimeColorClicked needed b/c engine lag on loading board in without it
            if engineTurn:
                currentFen = update.generate_FEN(boardState, click1Piece)
                currentBoard = chess.Board(currentFen)
                info = engine.analyse(currentBoard, chess.engine.Limit(depth=20))
                print(f'making move: {info["pv"][0]}')
                click1Pos, click2Pos, promotionPiece = update.parse_engine_move(info['pv'][0])
                engineTurn = False
                # create variable to skip click1/click2 checks below
                engineSkip = True

            # make sure one of the color options haven't been chosen before with firstTimeColorClicked
            # Need because without it, you can still click one of the icons since it's only covered by the board and not actually gone.
            if firstTimeColorClicked and (white.clicked or black.clicked):
                if white.clicked:
                    colorClicked = [True, 'w']
                elif black.clicked:
                    colorClicked = [True, 'b']
                    engineTurn = True
                firstTimeColorClicked = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                # event.button == 1 is a left click
                # also make sure not firstTimeColorClicked so clicking icon doesn't count as click1
                if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not firstTimeColorClicked) or engineSkip:
                    # get info about click pos
                    boardState, click1Pos, click1Piece, click2Pos, click2Piece, clickCount = \
                        validate.get_click_piece_pos(
                            boardState, clickCount, click1Pos, click1Piece, click2Pos, click2Piece, colorClicked, engineSkip    
                        )
                    if click1Pos or click2Pos:
                        # display moves if clicked
                        boardState = update.display_moves(
                            click1Pos, click2Pos, boardState, greenCircle, redCircle, inCheck, s, enPessantInfo
                        )
                    if click1Pos and click2Pos:
                        # figure out if move or capture
                        mapture = update.move_type(click1Piece, click2Piece)
                        if validate.legal_move(click1Pos, click2Pos, mapture, boardState, enPessantInfo) and \
                                (validate.turn_counter(click1Piece, click2Piece, turnCount, mapture)[0]) and \
                                check.did_move_resolve_check(click1Pos, click2Pos, boardState, mapture, s):
                            # check if en pessant opportunity is there
                            enPessantInfo = validate.legal_move(
                                click1Pos, click2Pos, mapture, boardState, enPessantInfo
                            )
                            if inCheck:
                                # check if move made after check made it so not in check
                                if isinstance(check.did_move_resolve_check(
                                    click1Pos, click2Pos, boardState, mapture, s
                                        ), tuple):
                                    inCheck = False
                                    boardState = check.did_move_resolve_check(
                                        click1Pos, click2Pos, boardState, mapture, s
                                    )[1]
                                else:
                                    # reset click positions because invalid move
                                    click1Pos, click2Pos = None, None
                                    continue

                            # check if king put its self in check
                            elif 'k' in click1Piece and \
                                    not isinstance(check.did_move_resolve_check(
                                        click1Pos, click2Pos, boardState, mapture, s
                                    ), tuple):
                                # reset click positions and skip this loop iteration
                                click1Pos, click2Pos = None, None
                                continue

                            # add m to keep track of pawn and king moves. Pawn is for two space move, king is for castleing
                            if 'p' in click1Piece or 'k' in click1Piece:
                                boardState[click1Pos[0]][click1Pos[1]]['piece'] += 'm'
                            # check if a pawn can promote
                            if validate.check_promotion(click1Pos, click2Pos, mapture, boardState, s):
                                promotionMenu = True
                                bool, pawnPos, originalBoardState = validate.check_promotion(
                                    click1Pos, click2Pos, mapture, boardState, s
                                )
                            # since nothing failed, must be a valid move so update it
                            boardState = update.update_move(mapture, boardState, click1Pos, click2Pos, s)
                            # update turn count, 0=white's turn, 1=black's turn
                            turnCount = validate.turn_counter(click1Piece, click2Piece, turnCount, mapture)[1]

                            # manually handle promotions if engine promotes
                            if promotionPiece is not None:
                                if click2Pos[0] == 0:
                                    promotionPiece = 'b' + promotionPiece
                                elif click2Pos[0] == 7:
                                    promotionPiece = 'w' + promotionPiece
                                boardState[click2Pos[0]][click2Pos[1]]['piece'] = promotionPiece
                                # globals() allows using string variation of variable to access it
                                boardState[click2Pos[0]][click2Pos[1]]['image'] = globals()[promotionPiece]
                                promotionPiece = None
                            # only set engineTurn to true once player makaes move
                            if (turnCount == 1 and colorClicked[1] == 'w') or (turnCount == 0 and colorClicked[1] == 'b'):
                                engineTurn = True, click1Piece
                            engineSkip = False

                            # see if move put king in check
                            if isinstance(check.is_check_after_move(click1Piece, click2Pos, boardState), tuple):
                                inCheck = True
                                boardState = check.is_check_after_move(click1Piece, click2Pos, boardState)[1]

                            # clear click pos b/c messes up click1Pos or click2Pos statements and more idk
                            click1Pos, click2Pos = None, None
                        else:
                            print("clearing pos")
                            print("--------------")
                            # still clear if not legal move
                            click1Pos, click2Pos = None, None
                    if check.checkmate(boardState, s):
                        gameOver = True

            # set appropriate values to make sure it blit's from top left or bottom right of board
            if colorClicked:
                if colorClicked[1] == 'w':
                    rowSpace = 4
                    colSpace = 8
                elif colorClicked[1] == 'b':
                    rowSpace = 495
                    colSpace = 500

                # blit board rectangles
                screen.blit(board, boardRect)
                for col in boardState:
                    for row in col:
                        try:
                            screen.blit(row['check'], (rowSpace-3.01, colSpace-8))
                        except KeyError:
                            pass
                        # blit pieces on board
                        screen.blit(row["image"], (rowSpace, colSpace))
                        try:
                            # blit green/red circle on board
                            screen.blit(row["moves"], (rowSpace+20, colSpace+16))
                        except KeyError:
                            pass
                        # adjust by color either blitting top to bottom or bottom to top
                        if colorClicked[1] == 'w':
                            rowSpace += 70
                            rowCount += 1
                            if rowCount == 8:
                                colSpace += 70
                                rowCount = 0
                                rowSpace = 4
                        elif colorClicked[1] == 'b':
                            rowSpace -= 70
                            rowCount += 1
                            if rowCount == 8:
                                colSpace -= 70
                                rowCount = 0
                                rowSpace = 495
    pygame.display.update()
    clock.tick(60)