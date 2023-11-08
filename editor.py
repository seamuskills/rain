# this will be a level editor
import pygame, pygame_gui

pygame.init()

screenSize = (540, 360 + 40) #giving myself a little room to make potential ui?
sc = pygame.display.set_mode(screenSize, flags=pygame.DOUBLEBUF | pygame.RESIZABLE)
ds = pygame.Surface(screenSize)
c = pygame.time.Clock()

grid = True
cell = 8

ui = pygame_gui.UIManager(screenSize)

camera = pygame.Vector2(20, 20)

selectedItem = "wall"
selPos = [0, 0]
player = None
selProperties = {
    "width": 1,
    "height": 1,
}

barButtons = {
    "player": pygame_gui.elements.UIButton(pygame.Rect(0, 0, 40, 40), "P", ui),
    "wall": pygame_gui.elements.UIButton(pygame.Rect(41, 0, 40, 40), "W", ui)
}

objects = []

while True:
    dt = c.tick(60) / 1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()

        if event.type == pygame.WINDOWRESIZED:
            ui.set_window_resolution(ds.get_size())
            screenSize = ds.get_size()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_PERIOD:
                cell *= 2
                pygame.event.post(pygame.event.Event(pygame.MOUSEMOTION))
            elif event.key == pygame.K_COMMA:
                cell = max(cell // 2, 4)
                pygame.event.post(pygame.event.Event(pygame.MOUSEMOTION))

            if selectedItem != "player":
                if event.key == pygame.K_UP:
                    selProperties["height"] -= 1
                    selProperties["height"] = max(selProperties["height"], 1)
                elif event.key == pygame.K_DOWN:
                    selProperties["height"] += 1
                elif event.key == pygame.K_LEFT:
                    selProperties["width"] -= 1
                    selProperties["width"] = max(selProperties["width"], 1)
                elif event.key == pygame.K_RIGHT:
                    selProperties["width"] += 1

            if event.key == pygame.K_g:
                grid = not grid

            if event.key == pygame.K_a:
                camera.x -= 4
            elif event.key == pygame.K_d:
                camera.x += 4
            elif event.key == pygame.K_w:
                camera.y -= 4
            elif event.key == pygame.K_s:
                camera.y += 4

            if event.key == pygame.K_r:
                selProperties = {
                    "width": 1,
                    "height": 1
                }

        if event.type == pygame.MOUSEMOTION:
            selPos = list(pygame.mouse.get_pos())
            selPos[0] += camera.x
            selPos[1] += camera.y
            selPos[0] -= selPos[0] % cell
            selPos[1] -= selPos[1] % cell

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and pygame.mouse.get_pos()[1] > 41: #left click
                match selectedItem:
                    case "player":
                        player = pygame.Vector2(selPos[0], selPos[1])
                    case "wall":
                        objects.append({"type": "wall", "pos": selPos, "width": selProperties["width"] * cell, "height": selProperties["height"] * cell, "color": [0xc2, 0xc2, 0xc2]})
            if event.button == 3: #right click
                pass

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            for k, v in barButtons.items():
                if event.ui_element == v:
                    selectedItem = k
                    print(selectedItem)

        ui.process_events(event)

    ds.fill([0x22, 0x22, 0x22])

    if selectedItem == "player":
        selProperties["width"] = 1
        selProperties["height"] = 1
    pygame.draw.rect(ds, [0x33, 0x33, 0x33], (selPos[0], selPos[1], cell * selProperties["width"], cell * selProperties["height"]))

    for o in objects:
        match o["type"]:
            case "wall":
                pygame.draw.rect(ds, o["color"], (o["pos"][0], o["pos"][1], o["width"], o["height"]))

    if player is not None:
        pygame.draw.rect(ds, (255, 255, 255), (player.x, player.y, 8, 16))

    if grid:
        for x in range(0, screenSize[0], cell):
            pygame.draw.line(ds, [0x33, 0x33, 0x33], (x, 0), (x, screenSize[1]))

        for y in range(0, screenSize[1], cell):
            pygame.draw.line(ds, [0x33, 0x33, 0x33], (0, y), (screenSize[0], y))

    sc.fill([0, 0, 0])
    sc.blit(ds, -camera)

    ui.update(dt)
    ui.draw_ui(sc)

    pygame.display.update()