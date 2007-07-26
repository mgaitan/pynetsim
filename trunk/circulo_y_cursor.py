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
"""
Copyright (C) <2007>  <Martín Gaitán, Leonardo M. Rocha>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
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

##TODO for comming versions of the program
##TODO para una nueva versión:
##TODO hacerlo todo con orientación a objetos
##TODO Que sean arbitrarias la cantidad de objetos creados, y de tipos arbitrarios

##TODO para una nueva versión:
##TODO hacerlo todo con orientación a objetos
##TODO Hacer las imágenes en 3D con OpenGL o algo del estilo
##TODO Ponerle un piso al escenario
##TODO Hacer que el movimiento del puntero sea en 3D 
##    (por ejemplo, presionando la tecla Ctrl o con un boton del mouse)


import ode
from pygame.locals import *
import pygame

#inicio pygame
pygame.init()


#The screen where it's going to happen everithing
#creo la pantalla de trabajo
srf =pygame.display.set_mode((800,600))

#Creo el mundo
#Create a world object
world = ode.World()
world.setGravity((0,0,-9810)) #la gravedad estaba muy baja para que anduviera como deseaba con las dimensiones que tiene

#Creando el espacio de objetos para la detección de colisiones
#Create a space object, for collision detection

space = ode.Space()

#Una JointGroup se crea cuando hay una colisión, para uso en la función
#A joint group for the contact joints that are generated whenever
#  two bodies collide
contactgroup = ode.JointGroup()

#Walls, floor and ceiling, for constraining the objects to stay where I want
#paredes, piso y techo, para que no se escapen los objetos
#paredes:

#izquierda (left)
pared_izq = ode.GeomPlane(space, (1,0,0), 50)
#frente (top)
pared_top = ode.GeomPlane(space, (0,1,0), 50)
#piso (floor)
piso = ode.GeomPlane(space, (0,0,1), 50)

#this cause strange behaviour when I uncomment any of this lines (solved Magically)
#derecha (rigth)
pared_der = ode.GeomPlane(space, (-1,0,0), -750)#funcionó "mágicamente" negando los parámetros
#pared_der.setPosition((800,0,0))
#fondo (bottom)
pared_bottom = ode.GeomPlane(space, (0,-1,0), -550)#funcionó "mágicamente" negando los parámetros
#techo (ceiling)
techo = ode.GeomPlane(space, (0,0,-1), -750)#funcionó "mágicamente" negando los parámetros


#Creo las esferas
#The sphere objects creation step
puntero = ode.Body(world)
M = ode.Mass()
M.setSphere(5000, 30)
puntero.setMass(M)
puntero.setPosition((100,100,100))

circulo = ode.Body(world)
M = ode.Mass()
M.setSphere(2500, 30.0)
circulo.setMass(M)
circulo.setPosition((400,300,100))

circulo2 = ode.Body(world)
M = ode.Mass()
M.setSphere(2500, 30.0)
circulo2.setMass(M)
circulo2.setPosition((401,300,100))

rect1= ode.Body(world)
M=ode.Mass()
M.setBox(3000,50.0,50.0,50.0)
rect1.setMass(M)
rect1.setPosition((150,200,100))

#crear los objetos de colisiones:
#creating Geom objects for the collision detection algorithm
geom_circulo=ode.GeomSphere(space,30)
geom_circulo.setBody(circulo)

geom_circulo2=ode.GeomSphere(space,30)
geom_circulo2.setBody(circulo2)

geom_puntero=ode.GeomSphere(space,30)
geom_puntero.setBody(puntero)
#geom_puntero.setRadius(15)

geom_rect1=ode.GeomBox(space,(50,50,50))
geom_rect1.setBody(rect1)

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


# Bucle de simulación...
# Simulation loop...

fps = 500
dt = 1.0/fps
loopFlag = True
clk = pygame.time.Clock()
#posicion relativa del mouse en la pantalla
#mouse position coordinates
xmouse=0
ymouse=0

while loopFlag:
    events = pygame.event.get()
    for e in events:
        if e.type==QUIT:
            loopFlag=False
        if e.type==KEYDOWN:
            loopFlag=False
        
    #obtiene las coordenadas actuales:
    #getting the coordinates 
    x1,y1,z1 = puntero.getPosition()
    #print "x1,y1,z1 = ", x1,y1,z1
    x2,y2,z2 = circulo.getPosition()
    #print "x2,y2,z2 = ", x2,y2,z2    
    x3,y3,z3 = circulo2.getPosition()
    #print "x3,y3,z3 = ", x3,y3,z3    
    x4,y4,z4=rect1.getPosition()
    #print "x4,y4,z4 = ", x4,y4,z4
    r=pygame.Rect(x4-25,y4-25,50,50)
    #x4-25 and y4-25 are needed to correctly draw the square in the rigth position
    #getting the mouse position
    #obtiene la posicion del mouse
    xmouse,ymouse =pygame.mouse.get_pos()
    #setting mouse pointer coordinates in puntero 
    #la setea en el puntero objeto en ODE:
    puntero.setPosition((xmouse,ymouse,z1))
    #
    # Clear the screen
    srf.fill((255,255,255))

    # Draw the bodies
    #Dibujando los objetos
    pygame.draw.circle(srf, (100,100,100), (x1,y1), 30, 0)
    pygame.draw.circle(srf, (55,0,200), (x2,y2), 30, 0)
    pygame.draw.circle(srf, (200,0,50), (x3,y3), 30, 0)
    pygame.draw.rect(srf,(0,200,0),r,0)
    #Renueva el contenido de la pantalla
    #Update the display content
    pygame.display.flip()

    #Detección de colisiones y creación de los contact joints
    # Detect collisions and create contact joints
    space.collide((world,contactgroup), near_callback)

    # Paso de simulación
    # Next simulation step
    world.step(dt)

    #Eliminar los contacts joints (es necesario limpiarlos)
    # Remove all contact joints
    
    contactgroup.empty()
    
    # Try to keep the specified framerate    
    clk.tick(fps)
#Cerrando ODE, necesario para liberar memoria (especificado en el manual)
#Closing ODE. This is needed for some cleaning (specified in the manual)
ode.CloseODE()
