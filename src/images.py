import pygame


class Button:
    def __init__(self, x, y, image, scale=1):
        # add scaling feature
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))

        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self, surface):
        action = False
        pos = pygame.mouse.get_pos()

        # check if mouse is clicking button
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked is False:
                self.clicked = True
                action = True
        # if not clicking, reset variables
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # blit image onto screen at x, y
        surface.blit(self.image, (self.rect.x, self.rect.y))

        return action


def promotion_menu(screen, piece, color, xIndex, promotionMenuClicked, colorClicked):
    # errors if actually False when doing [1]
    if colorClicked is False:
        colorClicked = 'False'
    # piece contains queen, knight, rook, bishop respectively to index
    pieceX = 4.5 + (70 * xIndex)  # 4.5 is to make piece centered
    rectX = 70 * xIndex
    if color == 'w':
        pieceY = 4.5
        rectY = 0
        gap = 70
        # flip if player is playing black
        # +10 manual adjustment for pieceX
        if colorClicked[1] == 'b':
            pieceY = 500
            pieceX = 500 - pieceX
            rectY = 70 * 4
            rectX = 490 - rectX
            gap = -70
    elif color == 'b':
        pieceY = 500
        rectY = 70 * 4
        gap = -70
        # flip if player is playing black
        # +10 manual adjustment for pieceX
        if colorClicked[1] == 'b':
            pieceY = 4.5
            pieceX = 500 - pieceX
            rectY = 0
            rectX = 490 - rectX
            gap = 70
    queenPromote = Button(pieceX, pieceY, piece[0])
    knightPromote = Button(pieceX, pieceY + gap, piece[1])
    rookPromote = Button(pieceX, pieceY + (gap * 2), piece[2])
    bishopPromote = Button(pieceX, pieceY + (gap * 3), piece[3])
    pygame.draw.rect(screen, (237, 234, 222), pygame.Rect(rectX, rectY, 70.5, 280))

    promotePieces = [queenPromote, knightPromote, rookPromote, bishopPromote]
    for piece in promotePieces:
        piece.draw(screen)

    if promotionMenuClicked:
        returnVar = 'nothing'
        if queenPromote.clicked:
            returnVar = 'queen'
        elif knightPromote.clicked:
            returnVar = 'knight'
        elif rookPromote.clicked:
            returnVar = 'rook'
        elif bishopPromote.clicked:
            returnVar = 'bishop'
        return returnVar
