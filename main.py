import pygame, math, random, sys

debug = "debug" in sys.argv

screenSize = [1080, 720]

flags = pygame.DOUBLEBUF
if "software" not in sys.argv:
    flags = flags | pygame.HWSURFACE #makes pygame use hardware surface unless user specifies that they don't want it forced
sc = pygame.display.set_mode(screenSize, flags)
c = pygame.time.Clock()

pygame.event.set_allowed([pygame.QUIT])

ticks = 0

keys = {}

rainSettings = {
    "partsPerDrop": 2,
    "ticksPerDrop": 5,
    "angle": 285,
    "dropSpeed": 10,
    "life": 80
}

def approach(x, y, a):
    if x < y:
        return min(x + a, y)
    if x > y:
        return max(x - a, y)
    return y

def sign(x):
    if x > 0:
        return 1
    if x < 0:
        return -1
    return 0

camera = pygame.Vector2(0, 0)
camTarget = [0, 0]
camTargetPlayer = True

parts = [] #all particles
class Drop: #raindrop
    def __init__(self, x, y, speed, direction, life):
        direction = direction * (math.pi / 180)
        self.pos = pygame.Vector2(x, y)
        self.speed = pygame.Vector2(math.cos(direction), math.sin(direction) * -1) * speed
        self.life = life
        self.prevPos = self.pos.copy()
        parts.append(self)

    def draw(self):
        self.life -= 1
        self.prevPos = self.pos.copy()
        self.pos += self.speed
        pygame.draw.line(sc, [0xee, 0xee, 0xef], self.prevPos - camera, self.pos - camera)

        if self.pos.x > camera.x + (screenSize[0] + 10):
            self.pos.x = camera.x - 9
        elif self.pos.x < camera.x - 10:
            self.pos.x = camera.x + (screenSize[0] + 9)

        for i in solids:
            if i.collidePoint(self.pos.x, self.pos.y):
                Splash(self.prevPos.x, self.prevPos.y)
                parts.remove(self)
                return

        if self.life == 0:
            parts.remove(self)

class Splash:
    def __init__(self, x, y, diameter=16):
        self.pos = pygame.Vector2(x, y)
        self.life = diameter - 1
        self.diameter = diameter
        self.surf = pygame.Surface([diameter, diameter])
        self.surf.set_colorkey([0, 0, 0])
        parts.append(self)

    def draw(self):
        self.surf.fill([0, 0, 0])
        pygame.draw.circle(self.surf, [0xff, 0xff, 0xff], [self.diameter / 2, self.diameter / 2], (self.diameter - self.life) / 2)
        self.surf.set_alpha(round((self.life / self.diameter) * 0xff))
        sc.blit(self.surf, self.pos - pygame.Vector2(self.diameter / -2, self.diameter / 2) - camera)
        self.life -= 1
        if self.life <= 0:
            parts.remove(self)

solids = [] #all solid objects
class Solid:
    def __init__(self):
        solids.append(self)
    def collidePoint(self, x, y):
        return False

    def collideRect(self, rect):
        return False

statics = [] #all static objects
class Static(Solid): # the most basic static object
    def __init__(self, x, y, w, h, color = [0xff, 0xff, 0xff]):
        super().__init__()
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color
        statics.append(self)

    def draw(self):
        pygame.draw.rect(sc, self.color, [self.rect.x - camera.x, self.rect.y - camera.y, self.rect.w, self.rect.h])

    def collidePoint(self, x, y): #this is needed just incase the shape is not a rect, in which case I can add conditions to rectify the collision detection
        return self.rect.collidepoint(x, y)

    def collideRect(self, rect): #same reason for existing as collidePoint
        return self.rect.colliderect(rect)

class CamTrigger:
    def __init__(self, x, y, w, h, target):
        self.rect = pygame.Rect(x, y, w, h)
        self.target = target
        statics.append(self)

    def collidePoint(self, x, y): #this is needed just incase the shape is not a rect, in which case I can add conditions to rectify the collision detection
        return self.rect.collidepoint(x, y)

    def collideRect(self, rect): #same reason for existing as collidePoint
        return self.rect.colliderect(rect)

    def draw(self):
        global camTargetPlayer
        global camTarget
        global player
        global debug
        if debug:
            pygame.draw.rect(sc, [255, 0, 0], [self.rect.x - camera.x, self.rect.y - camera.y, self.rect.w, self.rect.h], 2)

        if player.collideRect(self.rect):
            if self.target == "player":
                camTargetPlayer = True
            else:
                camTargetPlayer = False
                camTarget = self.target

class RainTrigger:
    def __init__(self, x, y, w, h, settings):
        self.rect = pygame.Rect(x, y, w, h)
        self.settings = settings

    def collidePoint(self, x, y): #this is needed just incase the shape is not a rect, in which case I can add conditions to rectify the collision detection
        return self.rect.collidepoint(x, y)

    def collideRect(self, rect): #same reason for existing as collidePoint
        return self.rect.colliderect(rect)
    def draw(self):
        global debug
        global player
        global rainSettings
        if debug:
            pygame.draw.rect(sc, [0, 255, 0],[self.rect.x - camera.x, self.rect.y - camera.y, self.rect.w, self.rect.h], 2)

        if player.collideRect(self.rect):
            rainSettings = self.settings

class Player(Solid):
    def __init__(self, x, y):
        super().__init__()
        self.rect = pygame.Rect(x, y, 32, 64)
        self.speed = pygame.Vector2(0, 0)
        self.accel = 0.3
        self.grav = 1
        self.jmp = -20
        self.topSpeed = 4
        self.ground = False

    def collideRect(self, rect):
        return self.rect.colliderect(rect)

    def collidePoint(self, x, y):
        return self.rect.collidepoint(x, y)

    def update(self):
        move = pygame.Vector2(
            keys[pygame.K_d] - keys[pygame.K_a],
            keys[pygame.K_w] - keys[pygame.K_s]
        )

        self.speed.x = approach(self.speed.x, move.x * self.topSpeed, self.accel)

        projection = self.rect.copy()
        projection.x = self.rect.x + self.speed.x
        for i in solids:
            if i is self:
                continue
            else:
                if i.collideRect(projection):
                    projection.x -= self.speed.x
                    while not i.collideRect(projection):
                        projection.x += sign(self.speed.x)
                    self.rect.x = projection.x - sign(self.speed.x)
                    self.speed.x = 0
                    break

        self.speed.y += self.grav

        if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and self.ground:
            self.speed.y = self.jmp

        self.ground = False
        projection = self.rect.copy()
        projection.y = self.rect.y + self.speed.y
        for i in solids:
            if i is self:
                continue
            else:
                if i.collideRect(projection):
                    projection.y -= self.speed.y
                    while not i.collideRect(projection):
                        projection.y += sign(self.speed.y)
                    self.rect.y = projection.y - sign(self.speed.y)
                    if self.speed.y > 0:
                        self.ground = True
                    self.speed.y = 0
                    break

        self.rect.x += self.speed.x
        self.rect.y += self.speed.y
    def draw(self):
        if debug: pygame.draw.rect(sc, [255,255,255], [self.rect.x - camera.x, self.rect.y - camera.y, self.rect.w, self.rect.h])


Static(0, 710, 720, 10, [0xc2, 0xc2, 0xc2])
player = Player(100, 96)

while True:
    keys = pygame.key.get_pressed()

    ticks += 1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    if ticks % rainSettings["ticksPerDrop"]:
        for i in range(rainSettings["partsPerDrop"]):
            Drop(random.randint(round(camera.x), round(camera.x + screenSize[0])), camera.y - 10, rainSettings["dropSpeed"], rainSettings["angle"], rainSettings["life"])

    sc.fill([0x22, 0x22, 0x22])

    for i in parts:
        i.draw()

    for i in statics:
        if i.collideRect(camera.x, camera.y, screenSize[0], screenSize[1]):
            i.draw()

    player.update()
    player.draw()

    if camTargetPlayer:
        camTarget = [player.rect.x, player.rect.y]

    cameraDist = pygame.Vector2(camTarget) - camera
    camera.x = approach(camera.x, camTarget[0] - (screenSize[0] / 2), 0.25 * cameraDist.x)
    camera.y = approach(camera.y, camTarget[1] - (screenSize[1] / 2), 0.25 * cameraDist.y)

    pygame.display.update()
    c.tick(60)