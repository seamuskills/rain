# this will be a level editor
import pygame, pygame_gui

pygame.init()

screenSize = (540, 360 + 40) #giving myself a little room to make potential ui?
sc = pygame.display.set_mode(screenSize, flags=pygame.DOUBLEBUF | pygame.RESIZABLE)
c = pygame.time.Clock()

cell = 8

ui = pygame_gui.UIManager(screenSize)

camera = pygame.Vector2(0, 0)

selectedItem = "wall"
selPos = [0, 0]
player = None

barButtons = {
    "player": pygame_gui.elements.UIButton(pygame.Rect(0, 0, 40, 40), "P", ui),
    "wall": pygame_gui.elements.UIButton(pygame.Rect(41, 0, 40, 40), "W", ui)
}

while True:
    dt = c.tick(60) / 1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()

        if event.type == pygame.WINDOWRESIZED:
            ui.set_window_resolution(sc.get_size())
            screenSize = sc.get_size()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_PERIOD:
                cell *= 2
                pygame.event.post(pygame.event.Event(pygame.MOUSEMOTION))
            elif event.key == pygame.K_COMMA:
                cell = max(cell // 2, 4)
                pygame.event.post(pygame.event.Event(pygame.MOUSEMOTION))
            if  selectedItem == "wall":
                if event.key == pygame.K_UP:
                    pass
                elif event.key == pygame.K_DOWN:
                    pass
                elif event.key == pygame.K_LEFT:
                    pass
                elif event.key == pygame.K_RIGHT:
                    pass

        if event.type == pygame.MOUSEMOTION:
            selPos = list(pygame.mouse.get_pos())
            selPos[0] -= selPos[0] % cell
            selPos[1] -= selPos[1] % cell

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: #left click
                match selectedItem:
                    case "player":
                        player = pygame.Vector2(selPos[0], selPos[1])
            if event.button == 3: #right click
                pass

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            for k, v in barButtons.items():
                if event.ui_element == v:
                    selectedItem = k
                    print(selectedItem)

        ui.process_events(event)

    sc.fill([0x22, 0x22, 0x22])

    for x in range(0, screenSize[0], cell):
        pygame.draw.line(sc, [0x33, 0x33, 0x33], (x, 0), (x, screenSize[1]))

    for y in range(0, screenSize[1], cell):
        pygame.draw.line(sc, [0x33, 0x33, 0x33], (0, y), (screenSize[0], y))

    pygame.draw.rect(sc, [0x33, 0x33, 0x33], (selPos[0], selPos[1], cell, cell))

    ui.update(dt)
    ui.draw_ui(sc)

    if player != None:
        pygame.draw.rect(sc, (255, 255, 255), (player.x, player.y, 8, 16))

    pygame.display.update()