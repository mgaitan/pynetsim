#! /usr/bin/env python
#-*- coding: utf-8 -*-
"""
This is a program in progress for I learn about PyODE and PyGame
The idea is to draw circles on the screen and then pushing them with a cursor
moved by the mouse
"""
"""
Este es un programa para que yo aprenda PyODE y PyGame
La idea es dibujar un circulo en la pantalla y luego poder empujarlo y 
traccionarlo con un puntero manejado por el mouse
"""
#DONE:
#creating and drawing the elements
# dibujar y crear los elementos

#pick the mouse movement and set the black circle position
# tomar el movimiento del mouse y pasarlo al circulo pequeño

#done physical simulation
# ODE realiza la simulación físicas

# x=0, y=0, z=0 planes are working well.
# listos los límites en x=0,y=0,z=0, (costó hacerlos andar en otras coordenadas)
#fixing limits for the balls don't scape of the scene (x=800, y=600, z=600 missing,
#   don't know how to make it work, those limits are having strange behaviour)
#Ponerle límites a los costados para que no se escapen los objetos
#    hacia el infinito (faltan 3 límites)

# included a square in the scene
# Agregado un cuadrado en la escena

# FIXED:
# arreglado el solape de las pelotitas para que no ocurra
# arreglado que del primer uso del mouse no volvía a colisionar (modificaba mal la coordenada z)
#IMPORTANTE Los límites en x=800, y=600, z=600 se solucionaron pasando las coordenadas y versor
#   en forma negativa (pared_der = ode.GeomPlane(space, (-1,0,0), -800) en vez de
#       pared_der = ode.GeomPlane(space, (1,0,0), 800))

# Hecho; imágenes en 3D con OpenGL o algo del estilo
# Hecho; cantidad arbitraria de objetos en el escenario

#TODO:
#TODO putting more objects to the scene (squares, cones, etc)
#TODO Agregar otros objetos distintos a la escena


#TODO to make the black circle drag and push the other elements
#TODO Hacer que se pueda empujar y traccionar los elementos, dependiendo del
#    estado de un botón del mouse

#TODO to understand better the way ODE does the metrics, how to dimension correctly
#   stuff, gravity, and forces,etc
#TODO entender mejor como maneja ODE las métricas, como dimensionar correctamente
#   las cosas, gravedad, y fuerzas, etc

#TODO Que los objetos dibujados por OpenGL sean de colores arbitrarios

##TODO for comming versions of the program
##TODO para una nueva versión:
##TODO hacerlo todo con orientación a objetos
##TODO Que los objetos sean de tipos arbitrarios (hasta ahora hay solo prismas rectangulares y esferas)

##TODO para una nueva versión:
##TODO hacerlo todo con orientación a objetos
##TODO Hacer que el movimiento del puntero sea en 3D 
##    (por ejemplo, presionando la tecla Ctrl o con un boton del mouse)


import ode
from pygame.locals import *
import pygame

import sys, os, random, time
from math import *

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

x = 0
y = 0
width = 1024
height = 768

# geometric utility functions
def scalp (vec, scal):
    vec[0] *= scal
    vec[1] *= scal
    vec[2] *= scal

def vect_length (vec):
    return sqrt (vec[0]**2 + vec[1]**2 + vec[2]**2)

# prepare_GL
def prepare_GL():
    """Prepare drawing.
    """
    #global width,height 
    # Viewport
    glViewport(0,0,width,height)

    # Initialize
    glClearColor(0.3,0.4,0.8,0)#(0.8,0.8,0.9,0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    glEnable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    glEnable(GL_LIGHTING)
    glEnable(GL_NORMALIZE)
    glShadeModel(GL_FLAT)

    # Projection
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective (45,1.3333,0.2,20)
    
    # Initialize ModelView matrix
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # Light source
    glLightfv(GL_LIGHT0,GL_POSITION,[5,5,10,0])
    glLightfv(GL_LIGHT0,GL_DIFFUSE,[1,1,1,1])
    glLightfv(GL_LIGHT0,GL_SPECULAR,[1,1,1,1])
    glEnable(GL_LIGHT0)

    # View transformation (camera point of view)
    gluLookAt (7.5, 8, 7.5, 2.5, 1.5, 2.5, 0, 1, 0)
    
# draw_body
def draw_body(body):
    """Draw an ODE body.
    """

    x,y,z = body.getPosition()
    R = body.getRotation()
    rot = [R[0], R[3], R[6], 0.,
           R[1], R[4], R[7], 0.,
           R[2], R[5], R[8], 0.,
           x, y, z, 1.0]
    glPushMatrix()
    glMultMatrixd(rot)
###    glClearColor (1.0, 1.0, 1.0, 1.0);
###    glClear (GL_COLOR_BUFFER_BIT);
#    glColor3fv(body.color3)
    glColor3f(1.0,1.0,0)

    
    if body.shape=="box":
        sx,sy,sz = body.boxsize
        glScale(sx, sy, sz)
        glutSolidCube(1)
    else:#if body.shape=="sphere":
        r=body.radius
        glutSolidSphere(r,25,25)
    glPopMatrix()


# create_box
def create_box(world, space, density, lx, ly, lz):
    """Create a box body and its corresponding geom."""

    # Create body
    body = ode.Body(world)
    M = ode.Mass()
    M.setBox(density, lx, ly, lz)
    body.setMass(M)

    # Set parameters for drawing the body
    body.shape = "box"
    body.boxsize = (lx, ly, lz)

    # Create a box geom for collision detection
    geom = ode.GeomBox(space, lengths=body.boxsize)
    geom.setBody(body)

    #color RGBA, for drawing purposes
    body.color3=(random.uniform(0,1),random.uniform(0,1),random.uniform(0,1))
    
    return body

#create sphere
def create_sphere(world, space,density,radius):
    """create a sphere body and its corresponding geom"""
    # Create body
    body = ode.Body(world)
    M = ode.Mass()  
    M.setSphere(density,radius)
    body.setMass(M)
    
    # Set parameters for drawing the body
    body.shape = "sphere"
    body.radius = radius

    # Create a box geom for collision detection
    r=body.radius
    geom = ode.GeomSphere(space,r)
    geom.setBody(body)
    
    #color RGBA, for drawing purposes
    body.color3=(random.uniform(0,1),random.uniform(0,1),random.uniform(0,1))

    return body


# Collision callback
def near_callback(args, geom1, geom2):
    """Callback function for the collide() method.

    This function checks if the given geoms do collide and
    creates contact joints if they do.
    """
    #Ver si los objetos chocan
    # Check if the objects do collide
    contacts = ode.collide(geom1, geom2)

    #Armar los joints de contacto
    # Create contact joints
    world,contactgroup = args
    for c in contacts:
        c.setBounce(0.5)
        c.setMu(5000)
        j = ode.ContactJoint(world, contactgroup, c)
        j.attach(geom1.getBody(), geom2.getBody())

# drop_object
def drop_object():
    """Drop an object into the scene."""

    global bodies, counter, objcount

    if random.uniform(0,1)<0.5:
        body = create_box(world, space, 1000, 0.90,0.20,0.20)
    else:
        body=create_sphere(world,space,1000,0.2)
    body.setPosition((random.uniform(1.0,4.0),random.uniform(2.0,4.0),random.uniform(1.0,4.0)) )
    #body.setPosition((2.5,2.5,2.5))
    theta = random.uniform(0,2*pi)
    ct = cos (theta)
    st = sin (theta)
    body.setRotation([ct, 0., -st, 0., 1., 0., st, 0., ct])
    bodies.append(body)
    counter=0
    objcount+=1

######################################################################

# Initialize Glut
glutInit ([])

# Open a window
glutInitDisplayMode (GLUT_RGB | GLUT_DOUBLE)


glutInitWindowPosition (x, y);
glutInitWindowSize (width, height);
glutCreateWindow ("Jueguito")

# Create a world object
world = ode.World()
world.setGravity( (0,-9.81,0) )
world.setERP(0.8)
world.setCFM(1E-5)

# Create a space object
space = ode.Space()

# A list with ODE bodies
bodies = []

# A joint group for the contact joints that are generated whenever
# two bodies collide
contactgroup = ode.JointGroup()

#Walls, floor and ceiling, for constraining the objects to stay where I want
#paredes, piso y techo, para que no se escapen los objetos
#paredes:
#
#izquierda (left)
pared_izq = ode.GeomPlane(space, (1,0,0), 0)
#frente (top)
pared_top = ode.GeomPlane(space, (0,1,0), 0)
#piso (floor)
piso = ode.GeomPlane(space, (0,0,1), 0)

#this cause strange behaviour when I uncomment any of this lines (solved Magically)
#derecha (rigth)
pared_der = ode.GeomPlane(space, (-1,0,0), -5)#funcionó "mágicamente" negando los parámetros
#pared_der.setPosition((800,0,0))
#fondo (bottom)
pared_bottom = ode.GeomPlane(space, (0,-1,0), -5)#funcionó "mágicamente" negando los parámetros
#techo (ceiling)
techo = ode.GeomPlane(space, (0,0,-1), -5)#funcionó "mágicamente" negando los parámetros



# Some variables used inside the simulation loop
fps = 100
dt = 1.0/fps
running = True
state = 0
counter = 0
objcount = 0
lasttime = time.time()
lasttimeobj=time.time()
"""
Handling Input Events

You can use these routines to register callback commands that are invoked when specified events occur.

    * glutReshapeFunc(void (*func)(int w, int h)) indicates what action should be taken when the window is resized.
    * glutKeyboardFunc(void (*func)(unsigned char key, int x, int y)) and glutMouseFunc(void (*func)(int button, int state, int x, int y)) allow you to link a keyboard key or a mouse button with a routine that's invoked when the key or mouse button is pressed or released.
    * glutMotionFunc(void (*func)(int x, int y)) registers a routine to call back when the mouse is moved while a mouse button is also pressed.
"""
#callback for reshaping window event
def _windowReshapeFunc(w,h):
    pass #yet empty, TODO, fullfill it

glutReshapeFunc(_windowReshapeFunc)
#mouse callback
def _mousefunc(button,state,x,y):
    pass #yet empty, TODO, fullfill it    
    
glutMouseFunc(_mousefunc)

# keyboard callback
def _keyfunc (c, x, y):
    sys.exit (0)

glutKeyboardFunc (_keyfunc)

# draw callback
def _drawfunc ():
    # Draw the scene
    prepare_GL()
    for b in bodies:
        draw_body(b)

    glutSwapBuffers () #swaps the buffers so that the nextimage is the correct one (using Double buffering)

#Sets wich function will be called for each redrawing
glutDisplayFunc (_drawfunc)

# idle callback
def _idlefunc ():
    global counter, state, lasttime, lasttimeobj

    t = dt - (time.time() - lasttime)
    if (t > 0):
        time.sleep(t)
    if objcount <100 and ((time.time()-lasttimeobj) > t*15):
        drop_object()
        lasttimeobj=time.time()
##    elif objcount>=100:
##        sys.exit(0)
    
    glutPostRedisplay ()#asks for redisplay whenever is possible to the loop routine

    # Simulate
    n = 2

    for i in range(n):
        # Detect collisions and create contact joints
        space.collide((world,contactgroup), near_callback)

        # Simulation step
        world.step(dt/n)

        # Remove all contact joints
        contactgroup.empty()

    lasttime = time.time()

#the function that will be called when the loop is idle
glutIdleFunc (_idlefunc)

glutMainLoop ()

#Cerrando ODE, necesario para liberar memoria (especificado en el manual)
#Closing ODE. This is needed for some cleaning (specified in the manual)
ode.CloseODE()