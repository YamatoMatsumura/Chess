import pygame

import move_validation as validate
import move_updates as update


def is_check_after_move(click1Piece, click2Pos, boardState):
    # checks if the move just made put a king in check. Move has to be updated in boardState for it to work
    redSquare = pygame.image.load('images/redSquare.png')
    redSquare = pygame.transform.scale(redSquare, (71, 70))
    # find opponents king location
    for i in range(len(boardState)):
        for j in range(len(boardState[i])):
            if click1Piece[0] == 'b' and 'wk' in boardState[i][j]['piece']:
                kingPos = i, j
            elif click1Piece[0] == 'w' and 'bk' in boardState[i][j]['piece']:
                kingPos = i, j
    # see if next move can be taking the king. If yes, move put king into check
    if validate.legal_move(click2Pos, kingPos, "capture", boardState):
        boardState[kingPos[0]][kingPos[1]]['check'] = redSquare
        return True, boardState
    else:
        return False


def did_move_resolve_check(click1Pos, click2Pos, boardState, mapture, s, displayMoveCall=False):
    click1Piece = boardState[click1Pos[0]][click1Pos[1]]['piece']
    # create deep copy of boardState
    tempBoardState = deep_copy_structure(boardState)
    tempBoardState = update.update_move(mapture, tempBoardState, click1Pos, click2Pos, s)
    # get your kings pos and oppnent pieces and positions that could attack your king
    kingPos, pieceList, posList = get_king_and_opponent_piece_pos(click1Piece, tempBoardState)

    # if king not found, move must have taken king when updating it in this function
    if kingPos is None:
        return False
    # loop through each piece and see if taking king is possible
    flag = True
    for i in range(len(pieceList)):
        if validate.legal_move(posList[i], kingPos, 'capture', tempBoardState):
            flag = False

    # make sure red king highlight doesn't go away if only theoretically checking if the move resolved check like from display or checking for checkmate
    if displayMoveCall:
        return flag
    if flag:
        for i in range(8):
            for j in range(8):
                if 'check' in boardState[i][j]:
                    del boardState[i][j]['check']
        return flag, boardState
    return flag


# *** code copied from ChatGPT ***
# manually do deep copy of boardState since import copy doesn't work with pygame surfaces
def deep_copy_structure(structure):
    if not isinstance(structure, (list, dict)):
        return structure  # Base case: if it's not a list or dict, return the element itself

    if isinstance(structure, list):
        return [deep_copy_structure(item) for item in structure]  # Copying lists recursively
    elif isinstance(structure, dict):
        return {key: deep_copy_structure(value) for key, value in structure.items()}  # Copying dictionaries recursively


def get_king_and_opponent_piece_pos(click1Piece, boardState):
    # return your king location and all of opponents pieces and pos of those pieces
    pieceList = []
    posList = []
    # get king location again
    for i in range(len(boardState)):
        for j in range(len(boardState[i])):
            # see where same color king as move made because this is response move to check
            if click1Piece[0] == 'b' and 'bk' in boardState[i][j]['piece']:
                kingPos = i, j
            elif click1Piece[0] == 'w' and 'wk' in boardState[i][j]['piece']:
                kingPos = i, j
            # get all pieces and positions currently on board that can attack king
            if click1Piece[0] == 'b' and boardState[i][j]['piece'][0] == 'w':
                pieceList.append(boardState[i][j]['piece'])
                posList.append([i, j])
            elif click1Piece[0] == 'w' and boardState[i][j]['piece'][0] == 'b':
                pieceList.append(boardState[i][j]['piece'])
                posList.append([i, j])
    return kingPos, pieceList, posList


def is_my_king_in_check(click1Piece, boardState, enPessantInfo=False):
    # Only works on move trying to move king out of check
    kingPos, pieceList, posList = get_king_and_opponent_piece_pos(click1Piece, boardState)
    kingCheckStatus = False
    for pos in posList:
        if validate.legal_move(pos, kingPos, 'capture', boardState, enPessantInfo):
            kingCheckStatus = True

    return kingCheckStatus


def get_my_pieces(pieceColor, boardState):
    pieceList = []
    posList = []
    for i in range(8):
        for j in range(8):
            if boardState[i][j]['piece'][0] == pieceColor:
                posList.append([i, j])
                pieceList.append(boardState[i][j]['piece'])
    return posList, pieceList


def checkmate(boardState, s):
    whitePosList, whitePieceList = get_my_pieces('w', boardState)
    blackPosList, blackPieceList = get_my_pieces('b', boardState)

    checkMate = False
    posList = None
    if is_my_king_in_check('ww', boardState):
        posList = whitePosList
    elif is_my_king_in_check('bb', boardState):
        posList = blackPosList

    if posList is not None:
        checkMate = True
        for pos in posList:
            for i in range(8):
                for j in range(8):
                    if (validate.legal_move(pos, [i, j], 'move', boardState) and
                            did_move_resolve_check(pos, [i, j], boardState, 'move', s, True)) or \
                            (validate.legal_move(pos, [i, j], 'capture', boardState) and
                             did_move_resolve_check(pos, [i, j], boardState, 'capture', s, True)):
                        checkMate = False
    return checkMate
