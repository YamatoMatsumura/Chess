import pygame

import check_for_check as check
import move_updates as update


def get_click_piece_pos(boardState, clickCount, click1Pos, click1Piece, click2Pos, click2Piece, clicked='None', engineSkip=False):
    """
    Returns coordinate position as (y, x) of position clicked. (0, 0) is top left corner. If onePlayerMode and
    player chooses black, coordinate fill be flipped along center of board to match pieces being flipped.

    Potentially Confusing Arguments:
    clicked: Only used for onePlayerMode. Can't be just None since it can't be subscripted.
    """
    # if engine's turn
    if engineSkip:
        # manually adjust engine's castle moves to match format
        # only create click1Piece since click2Piece will change from -- to rook
        click1Piece = boardState[click1Pos[0]][click1Pos[1]]['piece']
        if 'k' in click1Piece:
            if click1Piece[0] == 'w':
                row = 7
            elif click1Piece[0] == 'b':
                row = 0
            if click1Pos == (row, 4) and click2Pos == (row, 6):
                click2Pos = row, 7
            elif click1Pos == (row, 4) and click2Pos == (row, 2):
                click2Pos = row, 0
        click2Piece = boardState[click2Pos[0]][click2Pos[1]]['piece']

        return boardState, click1Pos, click1Piece, click2Pos, click2Piece, clickCount

    for i in range(8):
        for j in range(8):
            if boardState[i][j]['square'].collidepoint(pygame.mouse.get_pos()):
                if clickCount == 0:
                    # get piece, row, col, pos(row, col) based on clicked pos
                    # also update clickCount to keep track if click1 or click2
                    if clicked[1] == 'b':
                        i = 7 - i
                        j = 7 - j
                    click1Pos = i, j
                    click1Piece = boardState[i][j]['piece']
                    clickCount += 1
                elif clickCount == 1:
                    if clicked[1] == 'b':
                        i = 7 - i
                        j = 7 - j
                    click2Pos = i, j
                    click2Piece = boardState[i][j]['piece']
                    clickCount -= 1
    return boardState, click1Pos, click1Piece, click2Pos, click2Piece, clickCount


def legal_move(click1Pos, click2Pos, mapture, boardState, enPessantInfo=False):
    """
    Figure out if move trying to be made is a legal move or not.

    Potentially Confusing Arguments:
        mapture : Either 'move' or 'capture' or 'castle' based on what kind of move player is trying to make.
        enPessantInfo : Bool if move made was a legal move. If there is an enPessant opportunity, it becomes a list containing information about it.

    Return:
        True if legal move, False if not.
    """
    click1Piece = boardState[click1Pos[0]][click1Pos[1]]['piece']
    if click1Piece[1] == 'p':
        return verify_pawn_move(click1Pos, click2Pos, mapture, boardState, enPessantInfo)
    elif click1Piece[1] == 'r':
        return verify_rook_move(click1Pos, click2Pos, mapture, boardState)
    elif click1Piece[1] == 'k':  # k is king, not knight
        return verify_king_move(click1Pos, click2Pos, mapture, boardState)
    elif click1Piece[1] == 'b':
        return verify_bishop_move(click1Pos, click2Pos, mapture, boardState)
    elif click1Piece[1] == 'q':
        return verify_queen_move(click1Pos, click2Pos, mapture, boardState)
    elif click1Piece[1] == 'n':
        return verify_knight_move(click1Pos, click2Pos, mapture, boardState)


def determine_piece_info(click1Pos, click2Pos, boardState):
    click1Piece = boardState[click1Pos[0]][click1Pos[1]]['piece']
    click1Color = click1Piece[0]
    click2Piece = boardState[click2Pos[0]][click2Pos[1]]['piece']
    click2Color = click2Piece[0]
    xDistance = click1Pos[1] - click2Pos[1]
    yDistance = click1Pos[0] - click2Pos[0]
    xAbsDistance = abs(xDistance)
    yAbsDistance = abs(yDistance)

    return click1Piece, click1Color, click2Piece, click2Color, xDistance, yDistance, xAbsDistance, yAbsDistance


def verify_pawn_move(click1Pos, click2Pos, mapture, boardState, enPessantInfo):
    click1Piece, click1Color, click2Piece, click2Color, xDistance, yDistance, xAbsDistance, yAbsDistance = \
        determine_piece_info(click1Pos, click2Pos, boardState)
    # if capturing piece make sure it moves diagonally
    if (mapture == 'capture') and (xAbsDistance == 1) and (yDistance == 1) and \
            (click1Color == 'w') and (click2Piece != '--') and (click2Color != click1Color):
        return True
    elif (mapture == 'capture') and (xAbsDistance == 1) and (yDistance == -1) and \
            (click1Color == 'b') and (click2Piece != '--') and (click2Color != click1Color):
        return True
    # if moving, make sure it's only moving up or down
    elif (mapture == 'move') and (yAbsDistance <= 2) and (xAbsDistance == 0):
        # if piece endswith m --> already moved --> can only move 1 square up or down
        if (click1Piece.endswith('m')) and (yAbsDistance == 1) and (click2Piece == '--'):
            if click1Color == 'w' and yDistance == 1:
                return True
            elif click1Color == 'b' and yDistance == -1:
                return True
            else:
                return False
        # if piece endwith p --> hasn't moved --> can move 1 or 2 spaces
        elif click1Piece.endswith('p') and click2Piece == '--':
            # if piece moving 2 spaces --> enPessant can happen so return special info
            if yAbsDistance == 2:
                if click1Color == 'w' and yDistance == 2:
                    return True, click1Color, click2Pos
                elif click1Color == 'b' and yDistance == -2:
                    return True, click1Color, click2Pos
            # if piece moving 1 space, standard move
            elif yAbsDistance == 1:
                if click1Color == 'w' and yDistance == 1:
                    return True
                elif click1Color == 'b' and yDistance == -1:
                    return True
                else:
                    return False
        else:
            return False
    # check if enPessantInfo has more than just True or False
    elif not isinstance(enPessantInfo, bool) and click1Pos[0] == enPessantInfo[2][0] and \
            click1Color != enPessantInfo[1]:
        # enPessantInfo[2] is click2Pos
        if click1Color == 'w' and click2Pos[1] == enPessantInfo[2][1] and (click2Pos[0] - enPessantInfo[2][0] == -1) and \
                (abs(click2Pos[1] - click1Pos[1]) == 1):
            return True
        elif click1Color == 'b' and click2Pos[1] == enPessantInfo[2][1] and (click2Pos[0] - enPessantInfo[2][0] == 1) and \
                (abs(click2Pos[1] - click1Pos[1]) == 1):
            return True
        else:
            return False
    else:
        return False


def verify_rook_move(click1Pos, click2Pos, mapture, boardState):
    click1Piece, click1Color, click2Piece, click2Color, xDistance, yDistance, xAbsDistance, yAbsDistance = \
        determine_piece_info(click1Pos, click2Pos, boardState)
    if mapture == 'move':
        if click1Pos[1] == click2Pos[1]:
            # if moving up
            if yDistance > 0:
                check = True
                for x in range(click2Pos[0], click1Pos[0]):
                    if boardState[x][click1Pos[1]]['piece'] != "--":
                        check = False
                return check
            # if moving down
            elif yDistance < 0:
                check = True
                for x in range(click1Pos[0] + 1, click2Pos[0] + 1):
                    if boardState[x][click1Pos[1]]['piece'] != "--":
                        check = False
                return check
            else:
                return False
        elif click1Pos[0] == click2Pos[0]:
            # if moving left
            if xDistance > 0:
                check = True
                for x in range(click2Pos[1], click1Pos[1]):
                    if boardState[click1Pos[0]][x]['piece'] != "--":
                        check = False
                return check
            # if moving right
            elif xDistance < 0:
                check = True
                for x in range(click1Pos[1] + 1, click2Pos[1] + 1):
                    if boardState[click1Pos[0]][x]['piece'] != "--":
                        check = False
                return check
            else:
                return False
        else:
            return False
    if mapture == 'capture':
        # same logic as moving but check everything one piece before is space
        if click1Pos[1] == click2Pos[1]:
            # if moving up
            if yDistance > 0:
                check = True
                for x in range(click2Pos[0] + 1, click1Pos[0]):
                    if boardState[x][click1Pos[1]]['piece'] != "--":
                        check = False
                # make sure current piece isn't a space
                if check and click1Color != click2Color and click2Piece != "--":
                    return True
                else:
                    return False
            # if moving down
            elif yDistance < 0:
                check = True
                for x in range(click1Pos[0] + 1, click2Pos[0]):
                    if boardState[x][click1Pos[1]]['piece'] != "--":
                        check = False
                if check and click1Color != click2Color and click2Piece != "--":
                    return True
                else:
                    return False
            else:
                return False
        elif click1Pos[0] == click2Pos[0]:
            # if moving left
            if xDistance > 0:
                check = True
                for x in range(click2Pos[1] + 1, click1Pos[1]):
                    if boardState[click1Pos[0]][x]['piece'] != "--":
                        check = False
                if check and click1Color != click2Color and click2Piece != "--":
                    return True
                else:
                    return False
            # if moving right
            elif xDistance < 0:
                check = True
                for x in range(click1Pos[1] + 1, click2Pos[1]):
                    if boardState[click1Pos[0]][x]['piece'] != "--":
                        check = False
                if check and click1Color != click2Color and click2Piece != "--":
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False
    else:
        return False


def verify_king_move(click1Pos, click2Pos, mapture, boardState):
    click1Piece, click1Color, click2Piece, click2Color, xDistance, yDistance, xAbsDistance, yAbsDistance = \
        determine_piece_info(click1Pos, click2Pos, boardState)

    if mapture == 'move' and xAbsDistance <= 1 and yAbsDistance <= 1 and click2Piece == '--':
        return True
    elif mapture == 'capture' and xAbsDistance <= 1 and yAbsDistance <= 1 and \
            click2Piece != '--' and click2Color != click1Color:
        return True
    elif mapture == 'castle' and yAbsDistance == 0 and not check.is_my_king_in_check(click1Piece, boardState):
        kingPos, pieceList, posList = check.get_king_and_opponent_piece_pos(click1Piece, boardState)
        castleStatus = True

        if click1Color == 'w':
            row = 7
        elif click1Color == 'b':
            row = 0

        # if short castleing
        if xDistance == -3 or xDistance == -2:
            for opponentPiecePos in posList:
                # make sure nothing attacking or piece occupying space in between king and rook
                for i in range(5, 7):
                    if boardState[row][i]['piece'] != '--' or legal_move(opponentPiecePos, [row, i], 'move', boardState):
                        castleStatus = False
            return castleStatus
        # if long castleing
        elif xDistance == 4 or xDistance == 2:
            for opponentPiecePos in posList:
                for i in range(1, 4):
                    if boardState[row][i]['piece'] != '--' or legal_move(opponentPiecePos, [row, i], 'move', boardState):
                        castleStatus = False
            return castleStatus
        else:
            return False
    else:
        return False


def verify_bishop_move(click1Pos, click2Pos, mapture, boardState):
    click1Piece, click1Color, click2Piece, click2Color, xDistance, yDistance, xAbsDistance, yAbsDistance = \
        determine_piece_info(click1Pos, click2Pos, boardState)
    if mapture == 'move':
        if xAbsDistance == yAbsDistance:
            # if moving up and left
            if yDistance > 0 and xDistance > 0:
                check = True
                for x in range(1, xAbsDistance + 1):
                    if boardState[click1Pos[0] - x][click1Pos[1] - x]["piece"] != "--":
                        check = False
                return check
            # if moving up and right
            elif yDistance > 0 and xDistance < 0:
                check = True
                for x in range(1, xAbsDistance + 1):
                    if boardState[click1Pos[0] - x][click1Pos[1] + x]["piece"] != "--":
                        check = False
                return check
            # if moving down and left
            elif yDistance < 0 and xDistance > 0:
                check = True
                for x in range(1, xAbsDistance + 1):
                    if boardState[click1Pos[0] + x][click1Pos[1] - x]["piece"] != "--":
                        check = False
                return check
            # if moving down and right
            elif yDistance < 0 and xDistance < 0:
                check = True
                for x in range(1, xAbsDistance + 1):
                    if boardState[click1Pos[0] + x][click1Pos[1] + x]["piece"] != "--":
                        check = False
                return check
            else:
                return False
        else:
            return False
    if mapture == 'capture':
        # same logic as moving but check everything one piece before is space
        # very similar to rooks, just diagnol
        if xAbsDistance == yAbsDistance:
            # if moving up and left
            if yDistance > 0 and xDistance > 0:
                check = True
                for x in range(1, xAbsDistance):
                    if boardState[click1Pos[0] - x][click1Pos[1] - x]["piece"] != "--":
                        check = False
                if check and click1Color != click2Color and click2Piece != "--":
                    return True
                else:
                    return False
            # if moving up and right
            elif yDistance > 0 and xDistance < 0:
                check = True
                for x in range(1, xAbsDistance):
                    if boardState[click1Pos[0] - x][click1Pos[1] + x]["piece"] != "--":
                        check = False
                if check and click1Color != click2Color and click2Piece != "--":
                    return True
                else:
                    return False
            # if moving down and left
            elif yDistance < 0 and xDistance > 0:
                check = True
                for x in range(1, xAbsDistance):
                    if boardState[click1Pos[0] + x][click1Pos[1] - x]["piece"] != "--":
                        check = False
                if check and click1Color != click2Color and click2Piece != "--":
                    return True
                else:
                    return False
            # if moving down and right
            elif yDistance < 0 and xDistance < 0:
                check = True
                for x in range(1, xAbsDistance):
                    if boardState[click1Pos[0] + x][click1Pos[1] + x]["piece"] != "--":
                        check = False
                if check and click1Color != click2Color and click2Piece != "--":
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False
    else:
        return False


def verify_queen_move(click1Pos, click2Pos, mapture, boardState):
    click1Piece, click1Color, click2Piece, click2Color, xDistance, yDistance, xAbsDistance, yAbsDistance = \
        determine_piece_info(click1Pos, click2Pos, boardState)
    # combine rook and bishop movement
    if mapture == 'move':
        # copy of rook moves
        if click1Pos[1] == click2Pos[1]:
            # if moving up
            if yDistance > 0:
                check = True
                for x in range(click2Pos[0], click1Pos[0]):
                    if boardState[x][click1Pos[1]]['piece'] != "--":
                        check = False
                return check
            # if moving down
            elif yDistance < 0:
                check = True
                for x in range(click1Pos[0] + 1, click2Pos[0] + 1):
                    if boardState[x][click1Pos[1]]['piece'] != "--":
                        check = False
                return check
            else:
                return False
        elif click1Pos[0] == click2Pos[0]:
            # if moving left
            if xDistance > 0:
                check = True
                for x in range(click2Pos[1], click1Pos[1]):
                    if boardState[click1Pos[0]][x]['piece'] != "--":
                        check = False
                return check
            # if moving right
            elif xDistance < 0:
                check = True
                for x in range(click1Pos[1] + 1, click2Pos[1] + 1):
                    if boardState[click1Pos[0]][x]['piece'] != "--":
                        check = False
                return check
            else:
                return False
        # copy of bishop moves
        if xAbsDistance == yAbsDistance:
            # if moving up and left
            if yDistance > 0 and xDistance > 0:
                check = True
                for x in range(1, xAbsDistance + 1):
                    if boardState[click1Pos[0] - x][click1Pos[1] - x]["piece"] != "--":
                        check = False
                return check
            # if moving up and right
            elif yDistance > 0 and xDistance < 0:
                check = True
                for x in range(1, xAbsDistance + 1):
                    if boardState[click1Pos[0] - x][click1Pos[1] + x]["piece"] != "--":
                        check = False
                return check
            # if moving down and left
            elif yDistance < 0 and xDistance > 0:
                check = True
                for x in range(1, xAbsDistance + 1):
                    if boardState[click1Pos[0] + x][click1Pos[1] - x]["piece"] != "--":
                        check = False
                return check
            # if moving down and right
            elif yDistance < 0 and xDistance < 0:
                check = True
                for x in range(1, xAbsDistance + 1):
                    if boardState[click1Pos[0] + x][click1Pos[1] + x]["piece"] != "--":
                        check = False
                return check
            else:
                return False
        else:
            return False
    # combine rook and bishop capture
    elif mapture == 'capture':
        if click1Pos[1] == click2Pos[1]:
            # if moving up
            if yDistance > 0:
                check = True
                for x in range(click2Pos[0] + 1, click1Pos[0]):
                    if boardState[x][click1Pos[1]]['piece'] != "--":
                        check = False
                if check and click1Color != click2Color and click2Piece != "--":
                    return True
                else:
                    return False
            # if moving down
            elif yDistance < 0:
                check = True
                for x in range(click1Pos[0] + 1, click2Pos[0]):
                    if boardState[x][click1Pos[1]]['piece'] != "--":
                        check = False
                if check and click1Color != click2Color and click2Piece != "--":
                    return True
                else:
                    return False
            else:
                return False
        elif click1Pos[0] == click2Pos[0]:
            # if moving left
            if xDistance > 0:
                check = True
                for x in range(click2Pos[1] + 1, click1Pos[1]):
                    if boardState[click1Pos[0]][x]['piece'] != "--":
                        check = False
                if check and click1Color != click2Color and click2Piece != "--":
                    return True
                else:
                    return False
            # if moving right
            elif xDistance < 0:
                check = True
                for x in range(click1Pos[1] + 1, click2Pos[1]):
                    if boardState[click1Pos[0]][x]['piece'] != "--":
                        check = False
                if check and click1Color != click2Color and click2Piece != "--":
                    return True
                else:
                    return False
            else:
                return False
        # copy of bishop capture
        if xAbsDistance == yAbsDistance:
            # if moving up and left
            if yDistance > 0 and xDistance > 0:
                check = True
                for x in range(1, xAbsDistance):
                    if boardState[click1Pos[0] - x][click1Pos[1] - x]["piece"] != "--":
                        check = False
                if check and click1Color != click2Color and click2Piece != "--":
                    return True
                else:
                    return False
                # if moving up and right
            elif yDistance > 0 and xDistance < 0:
                check = True
                for x in range(1, xAbsDistance):
                    if boardState[click1Pos[0] - x][click1Pos[1] + x]["piece"] != "--":
                        check = False
                if check and click1Color != click2Color and click2Piece != "--":
                    return True
                else:
                    return False
                # if moving down and left
            elif yDistance < 0 and xDistance > 0:
                check = True
                for x in range(1, xAbsDistance):
                    if boardState[click1Pos[0] + x][click1Pos[1] - x]["piece"] != "--":
                        check = False
                if check and click1Color != click2Color and click2Piece != "--":
                    return True
                else:
                    return False
                # if moving down and right
            elif yDistance < 0 and xDistance < 0:
                check = True
                for x in range(1, xAbsDistance):
                    if boardState[click1Pos[0] + x][click1Pos[1] + x]["piece"] != "--":
                        check = False
                if check and click1Color != click2Color and click2Piece != "--":
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False
    else:
        return False


def verify_knight_move(click1Pos, click2Pos, mapture, boardState):
    click1Piece, click1Color, click2Piece, click2Color, xDistance, yDistance, xAbsDistance, yAbsDistance = \
        determine_piece_info(click1Pos, click2Pos, boardState)
    if ((xAbsDistance == 1 and yAbsDistance == 2) or (xAbsDistance == 2 and yAbsDistance == 1)) and \
            (mapture == 'move') and (click2Piece == '--'):
        return True
    elif ((xAbsDistance == 1 and yAbsDistance == 2) or (xAbsDistance == 2 and yAbsDistance == 1)) and \
            (mapture == 'capture') and (click2Piece != '--') and (click2Color != click1Color):
        return True
    else:
        return False


def turn_counter(piece1, piece2, turnCount, mapture=False):
    # Alternate between 0 and 1 based on who made a move
    if mapture == 'castle':
        if turnCount == 0 and piece1[0] == 'w' and piece2[0] == 'w':
            turnCount += 1
            return True, turnCount
        elif turnCount == 1 and piece1[0] == 'b' and piece2[0] == 'b':
            turnCount -= 1
            return True, turnCount
    if turnCount == 0 and piece1[0] == 'w' and (piece2[0] == '-' or piece2[0] == 'b'):
        turnCount += 1
        return True, turnCount
    elif turnCount == 1 and piece1[0] == 'b' and (piece2[0] == '-' or piece2[0] == 'w'):
        turnCount -= 1
        return True, turnCount
    else:
        return False, turnCount


def check_promotion(click1Pos, click2Pos, mapture, boardState, s):
    # make 2 copies of boardState. 1 to simulate making the move and 1 to have previous position to revert back to incase user takes promotion move back
    originalBoardState = check.deep_copy_structure(boardState)
    tempBoardState = check.deep_copy_structure(boardState)
    tempBoardState = update.update_move(mapture, tempBoardState, click1Pos, click2Pos, s)

    # check if a pawn can promote. (i.e. is there a pawn on the 0th or 7th rank?)
    for i in range(0, 8, 7):
        for j in range(8):
            if 'p' in tempBoardState[i][j]['piece']:
                return True, (i, j), originalBoardState
    return False
