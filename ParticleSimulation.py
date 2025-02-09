import pygame
import random
import math

pygame.init()
width,height = 1200,800
clock = pygame.time.Clock()
objects = []
screen = pygame.display.set_mode((width, height))

# CONSTANTS
COULOMBS_CONSTANT = 9.1 * 10  # Fixed typo
DRAW_VECTORS = True
CONST_PARTICLES = {
    'electron': {
        'charge': -1,
        'mass': 1,
        'radius': 3,
        'color': [0, 0, 255]
    },
    'proton': {
        'charge': 1,
        'mass': 5,
        'radius': 10,
        'color': [255, 0, 0]
    },
    'neutron': {
        'charge': 0,
        'mass': 5,
        'radius': 5,
        'color': [0, 255, 0]
    }
}


def inBounds(pos):
    return True if 0<=pos[0]<=width and 0<=pos[1]<=height else False

def getdist(pos1,pos2):
    return ((pos1[0]-pos2[0])**2+(pos1[1]-pos2[1])**2)**.5

def getdirection(pos1,pos2):
    return math.atan2(pos1[1]-pos2[1],pos1[0]-pos2[0])

def electroMagnetic(particle1, particle2):
    # newtons = kg m / s^2
    # kqq/r^2
    distance_squared = getdist(particle1.pos, particle2.pos) ** 2
    magForce = (particle1.charge * particle2.charge * COULOMBS_CONSTANT) / distance_squared if distance_squared != 0 else 0

    magDirection1 = getdirection(particle1.pos, particle2.pos)
    magDirection2 = getdirection(particle2.pos, particle1.pos)

    # equal and opposite forces are exerted
    # when the same force is exerted on a heavy mass it will accelerate by F/m = a

    particle1.vel = [
        particle1.vel[0] + magForce * math.cos(magDirection1),
        particle1.vel[1] + magForce * math.sin(magDirection1)
    ]

    particle2.vel = [
        particle2.vel[0] + magForce * math.cos(magDirection2),
        particle2.vel[1] + magForce * math.sin(magDirection2)
    ]

    if DRAW_VECTORS:
        Vector(magForce, magDirection1, particle1.pos).update()
        Vector(magForce, magDirection2, particle2.pos).update()


class Vector:
    def __init__(self,magnitude,direction,startpos,width=1,color = [255,255,255]):
        self.mag = magnitude
        self.color = color
        self.startpos = startpos
        self.direction = direction
        self.width = width

    def update(self):
        endpos = [
            self.startpos[0]+self.mag*math.cos(self.direction),
            self.startpos[1]+self.mag*math.sin(self.direction)
        ]
        pygame.draw.line(screen,self.color,self.startpos,endpos)
    
class Particle:
    def __init__(self,pos,id,radius=3,color = [255,0,0], width = 1, vel=[0,0]):
        self.vel = vel
        self.pos = pos
        self.width = width
        self.id = id

        try:
            self.mass = CONST_PARTICLES[id]['mass']
            self.charge = CONST_PARTICLES[id]['charge']
            self.rad = CONST_PARTICLES[id]['radius']
            self.color = CONST_PARTICLES[id]['color']
        except KeyError:
            print('Invalid particle ID')
            self.mass = 1
            self.charge = 0
            self.rad = radius
            self.color = color

    def update(self):
        # velocity updates
        self.pos = [
            self.pos[0] + self.vel[0],
            self.pos[1] + self.vel[1]
        ]
        # acceleration is rate of velocity change
        pygame.draw.circle(screen, self.color, self.pos, self.rad, self.width)

        for obj in objects:
            if obj != self:
                electroMagnetic(self, obj)

        if not inBounds(self.pos):
            objects.remove(self)
            del self


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                exit()
            elif event.key == pygame.K_q:
                objects.append(Particle(pygame.mouse.get_pos(), 'proton'))
            elif event.key == pygame.K_e:
                objects.append(Particle(pygame.mouse.get_pos(), 'electron'))
            elif event.key == pygame.K_n:  # Added neutron creation
                objects.append(Particle(pygame.mouse.get_pos(), 'neutron'))

    screen.fill((0, 0, 0))

    for obj in objects:
        obj.update()

    pygame.display.flip()
    clock.tick(120)