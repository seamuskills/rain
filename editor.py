# this will be a level editor
import string

import pygame, pygame_gui, tkinter, tkinter.filedialog, json

pygame.init()

screenSize = (540, 360 + 40) #giving myself a little room to make potential ui?
sc = pygame.display.set_mode(screenSize, flags=pygame.DOUBLEBUF | pygame.RESIZABLE)
ds = pygame.Surface(screenSize)
c = pygame.time.Clock()

font = pygame.font.SysFont("arial", 24, False, False)

#controls
# e to export
# n for new
# o for open
# wasd for camera
# arrow keys to wall size
# , . for grid size
# left click place
# right click delete
# c to configure
# g toggle grid

properties = {
    "size": list(screenSize)
}
levelPath = None
grid = True
cell = 8

def openPath():
    global levelPath
    global player
    global objects
    global properties
    top = tkinter.Tk()
    top.withdraw()
    file = tkinter.filedialog.askopenfilename(parent=top)
    top.destroy()
    with open(file, "r") as f:
        data = json.loads(f.read())
    for i in data["level"]:
        if i["type"] == "player":
            player = pygame.Vector2(i["pos"])
            data["level"].remove(i)
            break
    objects = data["level"]
    properties = data["properties"]
    levelPath = file
    print("[loaded {}]".format(levelPath))
    return [file, objects]

def savePath():
    global levelPath
    if levelPath is None:
        createPath()

    if levelPath == "":
        print("[Level save failed. No path.]")
        return -1

    data = exp()
    if data == -1:
        print("[Level save failed. No player!]")
        return -1

    with open(levelPath, "w") as f:
        f.write(json.dumps(data))
    print("[saved file {}]".format(levelPath))
    return 1

def createPath():
    global levelPath
    top = tkinter.Tk()
    top.withdraw()
    file = tkinter.filedialog.asksaveasfilename()
    top.destroy()
    levelPath = file
    return file

configDone = False
def config():
    global properties
    global configDone
    global camera
    configDone = False
    top = tkinter.Tk()

    widthCallback = top.register(setWidth)
    heightCallback = top.register(setHeight)

    top.geometry('256x128')
    top.title("level properties")

    wText = tkinter.Label(text="width: ")
    wText.pack()

    widthBox = tkinter.Entry(validate="all", validatecommand=(widthCallback,"%P"))
    widthBox.pack()

    hText = tkinter.Label(text="height: ")
    hText.pack()

    heightBox = tkinter.Entry(top, validatecommand=(heightCallback,"%P"), validate="all")
    heightBox.pack()

    done = tkinter.Button(top, text="done", command=top.destroy)
    done.pack()

    top.mainloop()
    camera = pygame.Vector2(-8, -50)
    print("[properties set: {}]".format(properties))

def setWidth(P):
    global properties
    if str.isdigit(P) or P == "":
        if P == "":
            P = 0
        properties["size"][0] = round(float(P))
        return True
    else:
        return False

def setHeight(P):
    global properties
    if str.isdigit(P) or P == "":
        if P == "":
            P = 0
        properties["size"][1] = round(float(P))
        return True
    else:
        return False

ui = pygame_gui.UIManager(screenSize)

camera = pygame.Vector2(20, 20)

selectedItem = "wall"
selPos = [0, 0]
player = None
selProperties = {
    "width": 1,
    "height": 1,
    "target": "player",
    "rainSettings":{
        "partsPerDrop": 2,
        "ticksPerDrop": 5,
        "angle": 285,
        "dropSpeed": 10,
        "life": 80
    }
}

barButtons = {
    "player": pygame_gui.elements.UIButton(pygame.Rect(0, 0, 40, 40), "P", ui),
    "wall": pygame_gui.elements.UIButton(pygame.Rect(41, 0, 40, 40), "W", ui),
    "camTrigger": pygame_gui.elements.UIButton(pygame.Rect(82, 0, 40, 40), "C"),
    "rainTrigger": pygame_gui.elements.UIButton(pygame.Rect(123, 0, 40, 40), "R")
}

objects = []

def exp(): #export the level
    data = {"level": []} #data to be entered into json file
    if player is None:
        return -1 #no player, invalid level
    else:
        data["level"].append({"type": "player", "pos": [player.x, player.y]}) #add player object
    for i in objects: #add all other objects
        data["level"].append(i)
    data["properties"] = properties
    return data #return finished data

def resizeLevel():
    global ds
    if ds.get_size() != properties["size"]:
        ds = pygame.transform.scale(ds, properties["size"])
        for i in objects:
            if not pygame.Rect(i["pos"][0], i["pos"][1], i["width"], i["height"]).colliderect((0, 0, ds.get_size()[0], ds.get_size()[1])):
                objects.remove(i)

while True:
    dt = c.tick(60) / 1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()

        if event.type == pygame.WINDOWRESIZED:
            ui.set_window_resolution(sc.get_size())
            screenSize = sc.get_size()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                savePath()
            if event.key == pygame.K_PERIOD:
                cell *= 2
                pygame.event.post(pygame.event.Event(pygame.MOUSEMOTION))
            elif event.key == pygame.K_COMMA:
                cell = max(cell // 2, 4)
                pygame.event.post(pygame.event.Event(pygame.MOUSEMOTION))
            elif event.key == pygame.K_o:
                levelPath = openPath()
            elif event.key == pygame.K_n:
                levelPath = createPath()
            elif event.key == pygame.K_c:
                config()

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
            mouse = pygame.Vector2(pygame.mouse.get_pos()) + camera
            if event.button == 1 and pygame.mouse.get_pos()[1] > 41: #left click
                match selectedItem:
                    case "player":
                        player = pygame.Vector2(selPos[0], selPos[1])
                        print("[placed player at {}]".format(str(player)))
                    case "wall":
                        objects.append({"type": "wall", "pos": selPos, "width": selProperties["width"] * cell, "height": selProperties["height"] * cell, "color": [0xc2, 0xc2, 0xc2]})
                        print("[placed {}]".format(objects[-1]))
                    case "camTrigger":
                        objects.append({"type": "camTrigger", "pos": selPos, "width": selProperties["width"] * cell, "height": selProperties["height"] * cell, "target": selProperties["target"]})
                        print("[placed {}]".format(objects[-1]))
                    case "rainTrigger":
                        objects.append({"type": "rainTrigger", "pos": selPos, "width": selProperties["width"] * cell, "height": selProperties["height"] * cell, "rainSettings": selProperties["rainSettings"]})
                        print("[placed {}]".format(objects[-1]))
            if event.button == 3: #right click
                if player is not None:
                    if pygame.Rect(player.x, player.y, 8, 16).collidepoint(mouse):
                        player = None
                        print("[player removed!]")
                for i in objects:
                    if pygame.Rect(i["pos"][0], i["pos"][1], i["width"], i["height"]).collidepoint(mouse):
                        objects.remove(i)
                        print("[removed {}]".format(i))

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            for k, v in barButtons.items():
                if event.ui_element == v:
                    selectedItem = k
                    print("[selected {}]".format(selectedItem))

        ui.process_events(event)

    resizeLevel()

    ds.fill([0x22, 0x22, 0x22])

    if selectedItem == "player":
        selProperties["width"] = 1
        selProperties["height"] = 1
    pygame.draw.rect(ds, [0x33, 0x33, 0x33], (selPos[0], selPos[1], cell * selProperties["width"], cell * selProperties["height"]))

    for o in objects:
        match o["type"]:
            case "wall":
                pygame.draw.rect(ds, o["color"], (o["pos"][0], o["pos"][1], o["width"], o["height"]))
                if grid: pygame.draw.rect(ds, [0, 0, 0], (o["pos"][0], o["pos"][1], o["width"], o["height"]), round(cell * 0.5))

    if player is not None:
        pygame.draw.rect(ds, (255, 255, 255), (player.x, player.y, 8, 16))

    if grid:
        for x in range(round(camera.x - (camera.x % cell)), round(camera.x) + screenSize[0], cell):
            pygame.draw.line(ds, [0x33, 0x33, 0x33], (x, 0), (x, screenSize[1]))

        for y in range(round(camera.y - (camera.y % cell)), round(camera.y) + screenSize[1], cell):
            pygame.draw.line(ds, [0x33, 0x33, 0x33], (0, y), (screenSize[0], y))

    sc.fill([0, 0, 0])
    sc.blit(ds, -camera)

    pygame.draw.rect(sc, [0x11, 0x11, 0x11], (0, 0, screenSize[0], 42))
    ui.update(dt)
    ui.draw_ui(sc)

    coord = font.render("{}".format(selPos), True, [255, 255, 255])
    sc.blit(coord, [2, screenSize[1] - (font.get_point_size() + 5)])

    pygame.display.update((0, 0, screenSize[0], screenSize[1]))