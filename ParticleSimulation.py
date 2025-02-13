import pygame
import random
import math

pygame.init()
width,height = 1200,800
clock = pygame.time.Clock()
screen = pygame.display.set_mode((width, height))

# CONSTANTS
COULOMBS_CONSTANT = 9.1 * 10
DRAW_VECTORS = False
MAXFIELD = .04
DRAW_MAGNETIC = True
BRUSH_SIZE = 50
CONSERVE_MASS = False
NEUTRINO = False
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
    #neutrons are kinda useless, until i add the strong force
    'neutron': {
        'charge': 0,
        'mass': 5,
        'radius': 5,
        'color': [0, 255, 0]
    }
}

#USER INPUT
FixedParticle = False
MagneticMode = False

#SIMUATLION VARIABLES
objects = []
#magfield = [[-MAXFIELD for _ in range(width)] if h%5 else [MAXFIELD for _ in range(width)] for h in range(height)]  # ranges from -1 to 1
magfield = [[0 for _ in range(width)] for h in range(height)]
fieldimage = pygame.Surface((width,height))

def inBounds(pos):
    return True if 0<=pos[0]<=width and 0<=pos[1]<=height else False

def isMoving(vel):
    return False if vel[0]==0 and vel[1]==0 else True

def getdist(pos1,pos2):
    return ((pos1[0]-pos2[0])**2+(pos1[1]-pos2[1])**2)**.5

def getdirection(pos1,pos2):
    return math.atan2(pos1[1]-pos2[1],pos1[0]-pos2[0])

def draw_fields():
    # blit on an image, then only create a new image when field is being changed
    fieldimage.fill((255 // 2, 255 // 2, 255 // 2))
    for y in range(height):
        for x in range(width):
            color = int(((magfield[y][x] + MAXFIELD)/MAXFIELD) * (255 // 2))
            fieldimage.set_at((x, y), (color, color, color))
    
def moving_charge(particle):
    # any charge moving through a magnetic field experiences a force described by qvB = F
    # the direction of the force can be determined through the right-hand rule
    # since magnetic fields in this simulation only go in or out of the page, the force will always be acting perpendicular to the velocity

    net_velocity = (particle.vel[0]**2 + particle.vel[1]**2)**.5
    future_pos = [
        particle.pos[0] + particle.vel[0],
        particle.pos[1] + particle.vel[1]
    ]
    direction = getdirection(particle.pos, future_pos) if particle.id == 'proton' else -getdirection(particle.pos, future_pos)+math.pi
    field_strength = magfield[int(particle.pos[1])][int(particle.pos[0])]
    force = net_velocity*particle.charge*field_strength

    particle.vel = [
        particle.vel[0]+force*math.sin(direction),
        particle.vel[1]+force*math.cos(direction)
    ]


def electroStatic(particle1, particle2):
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

def form_neutrino(particle1,particle2):
    if getdist(particle1.pos,particle2.pos) < (CONST_PARTICLES[particle1.id]['radius'] + CONST_PARTICLES[particle2.id]['radius']):
        objects.remove(particle1)
        objects.remove(particle2)
        objects.append(Particle(particle1.pos,'neutron'))
        del particle1
        del particle2



#plan to add magents, then particle that moves through an electric field which is affected by qvB = F, unfortunately, magnetic fields can only move into or out of the page, white represents out of the page black represents into the page
#to prevent infinite energy when protons touch electrons they form a neutron while emitting a neutrino

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
    def __init__(self,pos,id,radius=3,color = [255,0,0], width = 100, vel=[0,0], fixed = False):
        self.vel = vel
        self.pos = pos
        self.width = width
        self.id = id

        self.fixed = fixed

        try:
            self.mass = CONST_PARTICLES[id]['mass']
            self.charge = CONST_PARTICLES[id]['charge']
            self.rad = CONST_PARTICLES[id]['radius']
            self.color = CONST_PARTICLES[id]['color']
        except KeyError:
            print('Invalid particle ID')
            del self

    def update(self):
        # velocity updates
        if not self.fixed:
            self.pos = [
                self.pos[0] + self.vel[0],
                self.pos[1] + self.vel[1]
            ]
        # acceleration is rate of velocity change
        pygame.draw.circle(screen, self.color, self.pos, self.rad, self.width)

        for obj in objects:
            if obj != self:
                electroStatic(self, obj)
                if NEUTRINO and self.id == 'electron' and obj.id == 'proton':
                    form_neutrino(self,obj)

        if isMoving(self.vel) and inBounds(self.pos):
            moving_charge(self)

        if not inBounds([self.pos[0] + self.vel[0],self.pos[1] + self.vel[1]]) and CONSERVE_MASS:
            self.vel = [
                -self.vel[0],
                -self.vel[1]
            ]

        if not inBounds(self.pos):
            if CONSERVE_MASS:
                print(f"Mass lost {self.id}")
            objects.remove(self)
            del self

#delete after adding the field making thing
#draw_fields()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                exit()
            elif event.key == pygame.K_q:
                if not MagneticMode:
                    objects.append(Particle(pygame.mouse.get_pos(), 'proton',fixed=FixedParticle,vel=[0,0]))
                else:
                    #create a postiive magnetic field here
                    #no way to create yet
                    
                    draw_fields()
            elif event.key == pygame.K_e:
                if not MagneticMode:
                    objects.append(Particle(pygame.mouse.get_pos(), 'electron',fixed=FixedParticle,vel=[0,0]))
                else:
                    #create a negative magnetic field here

                    draw_fields()
                
            elif event.key == pygame.K_r:
                FixedParticle= not FixedParticle
            elif event.key == pygame.K_t:
                MagneticMode = not MagneticMode

            

    if DRAW_MAGNETIC:
        screen.blit(fieldimage,(0,0))
    else:    
        screen.fill((0, 0, 0))

    for obj in objects:
        obj.update()

    pygame.display.flip()
    clock.tick(120)