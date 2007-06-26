#! /usr/bin/env python
# -*- coding: utf8 -*-

#simulador de trafico por internet implementado en Python. 
#Martin Gaitan y Leo Rocha
#Enero de 2007
#clases.py

import funciones
import random
import pydot 
import networkx
import pylab as P
import matplotlib
import string

"""en este fuente se definen las clases router, adminitrador, pagina, paquete, etc. 
las clases no heredan sino que interactuan a nivel de instanciacion: ie, una pagina se compone de n cantidad de paquetes
"""

cant_routers = 5  
max_cant_term = 5   
max_cant_pag = 4
asincronico = False #define si el peso de las aristas es simetrico o no
max_conectividad = 2 #variable estimativa. con cuantos vecinos como maximo puede conectarse un router 
max_transferencia = 15 #velicidad de transfencia max entre un router y otro (en caracteres)
tam_paquete = 3        #cuantos caracteres maximo forman un paquete?
leer_archivo = False    #si no se lee genera un grafo aleatorio y lo guarda
grabar_archivo = False
nombre_archivo = "datos.dat"
fijo=True

def empaquetar(pagina, ip_destino, tam=tam_paquete):
    """recibe una pagina y devuelve una lista de paquetes"""
    
    global tam_paquete
    
    paquetes = []
    total = int(pagina.long/tam_paquete)+1

    print "Total: "+`total`
    
    for i in range(total):
        data = pagina.data[i*tam:(i+1)*tam]
        paq = Paquete(i, pagina.id_pagina,total, pagina.ip_origen, ip_destino, data)
        paquetes.append(paq)
    return paquetes
    
    

def dibujar(grafo, edges=False, pos=False):
    """esta funcion dibuja la red (grafo) incluyendo label en las aristas
        edges es una tupla triple del tipo (n1,n2,valor)
    """
    if not edges: edges = grafo.edges()
    if not pos: pos = networkx.drawing.spring_layout(grafo)
    
    F=networkx.XGraph()
    F.add_edges_from(edges)
    ax=matplotlib.pylab.gca()
    ax.set_xticks([])
    ax.set_yticks([])
    edge_pos = dict( ((n1,n2),(pos[n1]+pos[n2])/2) for n1,n2,v in F.edges() )
    edge_labels = dict( ((x,y), z) for x,y,z in F.edges() )
    networkx.draw_networkx_labels(grafo, edge_pos, edge_labels)
    networkx.draw_networkx(grafo, pos, True)
    P.show()


class Router:
    """esta clase define el elemento principal de la red: el router. El router se conecta con otros vecinos, formando una red.     
    a la vez, el router tiene conectado varios terminales que son los que contienen y solicitan paginas. 
    """      
       
    def __init__(self, id):
        """incializador de la clase router. setea id e iniciliaza la tabla de routeo"""
        global max_cant_term
        
        self.id_router = id     #asigna el identificador del router
        self.vecinos = {}       #diccionario que define las conexiones a los vecinos *ABSOLETO para NX
        self.terminales = []    #lista de terminales conectados a este router
        
        self.cola_vecino = {}       #colas de paquetes hacia cada vecino
        #incluye una cola hacia si mismo
        self.cola_vecino[self.id_router] = []
    
    def set_terminal(self, terminal):
        self.terminales.append(terminal)
            
    def long_cola_vecino(self, r_vecino):
        return len(self.cola_vecino[r_vecino.id_router])
    
    def es_vecino(self, router_vecino):
        """verifica si un router es vecino del instanciado (self)"""
        if router_vecino.id_router in self.cola_vecino.keys():
            return True
        else:
            return False
    
    def info(self):
        """muestra datos de un router"""
        print "Router # "+`self.id_router`+"\nTerminales: "+repr(self.terminales)
        print "colas: "+`self.cola_vecino`
        
        #`[(red.lista_routers[x],self.long_cola_vecino(red.lista_routers[x])) for x in self.cola_vecino.keys()]`
        
                    
    
    def encolar(self, paquetes, r_vecino):
        """agrega los paquetes al principio de la cola correspondiente al vecino indicado. Si el vecino no existe devuelve un error
        la cola es tipo FIFO
        """
         
        
        
        try:
            self.cola_vecino[r_vecino.id_router].extend(paquetes)
            #agrego todos los paquetes en la cola hacia el router vecino
            #si es el destino final de los paquetes, analizo completitud
            if self is r_vecino: 
                self.analizar_completitud(r_vecinos)
        except:
            print "vecino no valido"
    
    def desencolar(self, r_vecino,cant_paquetes):
        """devuelve una cantidad de paquetes del final de la cola hacia el vecino especificado"""
        
        #desencolo los or 'cant_paquetes'
        paq = self.cola_vecino[r_vecino.id_router][-cant_paquetes:]
        #actualizo la cola
        self.cola_vecino[r_vecino.id_router] = self.cola_vecino[r_vecino.id_router][:-cant_paquetes]
        #devuelvo
        return paq
    
     
    
    def analizar_completitud(self, r_vecino):
        """
        
        analiza la cola hacia el vecino en busca de una pagina completa. Si la encuentra la quita de la cola y entrega"""

        print "analizando completitud"

        cola_parcial = {}
        #separo los paquetes segun la pagina que correspondan
        for paquete in self.cola_vecino[r_vecino.id_router]:
            try: 
                cola_parcial[paquete.id_pagina].append(paquete)
            except:
                cola_parcial[paquete.id_pagina] = []
                cola_parcial[paquete.id_pagina].append(paquete)
                

#        print "cola pacial:"+`cola_parcial` 

        #evaluo si la cantidad de paquetes de la pagina esta completa. el dato lo saco del primer paquete
        for id_pagina in cola_parcial.keys():
            if cola_parcial[id_pagina][0].total == len(cola_parcial[id_pagina]):
                print "----Se ha completado la pagina Nº"+`id_pagina`+ "hacia "+ `cola_parcial[id_pagina][0].ip_destino`+" ----"
                
                ###completar! habria que ordenar los paquetes y mostrar la pagina.  ###
                    
                #quitando los paquetes de esta pagina de la cola"
                for paquete in cola_parcial[id_pagina]:
                    #quito el paquete (posicion index donde se encuentra el paquete 'paquete' de la cola al vecino
                    del self.cola_vecino[r_vecino.id_router][self.cola_vecino[r_vecino.id_router].index(paquete)]
                print "despues:"
                

        
    def __repr__(self):
        return "R"+`self.id_router`
    
        
class Ip:
    def __init__(self, id_terminal, id_router):
        self.id_terminal = id_terminal
        self.id_router = id_router
    def __repr__(self):
        return `self.id_router`+"."+`self.id_terminal`
    

class Admin2:
    """Otra estructura de administrador basada en grafos del paquete networkX   
    ahora el conocimiento de la red lo tiene el grafo mismo, y se consultan sus metodos para saber los vecinos
    etc.
    """  
    def __init__(self):
        global cant_routers
        global asincronico
        global max_conectividad
        global max_transferencia
        global desde_archivo
        global nombre_archivo
        global max_cant_term
        global max_cant_pag
        
        self.lista_terminales = {} #mapa id->terminal
        self.lista_paginas = {}  #mapa id->pagina
        self.lista_routers = {}  #mapa id->router
        
    
        if leer_archivo:
        #leo el grafo desde un archivo
            self.red = networkx.read_adjlist(nombre_archivo)
        else:
        #create empty directed graph with edge data.     
            self.red = networkx.XGraph()
            
               
            for i in range(cant_routers):
                r = Router(i)
                self.red.add_node(r)
                self.lista_routers[i] = r
            #el grafo tiene distintos valores en sus aristas bajo la lista [costo,tasa]
            #donde costo = Cola[vecino]/floor(tasa/tam_paquete)
            
            
            for router in self.red.nodes():
                #agrego una cantidad de vecinos al azar para cada router
                posibles = self.red.nodes()
                for vec_actual in [self.lista_routers[x] for x in router.cola_vecino.keys()]:
                    posibles.remove(vec_actual)
                    
                max = max_conectividad if max_conectividad <= len(posibles) else len(posibles) #uso version corta de if 
                vecinos_asignados = random.sample(posibles, random.choice(range(1, max +1 )))
                for x in vecinos_asignados:
                    tasa = random.choice(range(tam_paquete, max_transferencia)) #el minimo es el tamaño de 1 paquete
                    self.red.add_edge(router, x, [1 ,tasa])
                    #inicializo las colas
                    router.cola_vecino[x.id_router] = []
                    x.cola_vecino[router.id_router] = []
        self.pos = networkx.drawing.spring_layout(self.red) #fijo la posicion de los nodos del grafo        

        #genero terminales aleatoriamente y paginas dentro de el. Se lleva un diccionario 
        #para el admin tenga i  nformacion para buscar terminales y paginas mediante su id
        counter = 0
        counter_p = 0
        for router in self.red.nodes():
            for id in range(random.choice(range(1,max_cant_term))):
                counter += 1
                
                t = Terminal(Ip(counter, router.id_router)) #genero el terminal
                router.set_terminal(t)   #lo asigno a un router
                self.lista_terminales[counter] = t   #lo agrego al diccionario para busquedas rapidas mediante id
        
        #genero paginas aleotariamente. Cada terminal tiene al menos 1 pagina.

            for terminal in router.terminales:
                for i in range(1, random.choice(range(max_cant_pag))):
                    p = Pagina(counter_p, terminal.ip_terminal)
                    terminal.set_pagina(p)
                    self.lista_paginas[p.id_pagina]=p
                    counter_p += 1
        

    def info(self):
        print "######## La GRan RED ######"
        print "cantidad de nodos"+`len(self.red.nodes())`
        print "lista de nodos"+`self.red.nodes()`
        print "cantidad de puentes"+`len(self.red.edges())`
        print "lista de puentes"+`self.red.edges()`
        

    def mostrar(self):       
        edges = [ (x,y,z) for x,y,z in self.red.edges() ]
        dibujar(self.red, edges, self.pos)
        return "ok"

    def demo(self):
        """un metodo para obetener informacion en forma dinamica"""
        while 1:
            print "##############################"
            print "a :\t info Red"
            print "t :\t info terminal"
            print "p :\t info pagina"
            print "g :\t ver grafo de red"
            print "r :\t info router"
            print "e :\t empaquetar pagina"
            print "d :\t pedir pagina"
            print "s :\t paso"
            print "S :\t salir"
            opcion = raw_input("Ingrese opcion: ")
            
            if opcion=='S': 
                break
            elif opcion=='a':
                self.info()
            elif opcion=='t':
                t = raw_input("Ingrese id terminal: ")
                if t=='s': break
                term = self.lista_terminales[int(t)]
                funciones.separador("el terminal tiene los siguientes datos")
                term.info()
            elif opcion=='p':
                p = raw_input("Ingrese id_pagina: ")
                if p=='s': break
                pag = self.lista_paginas[int(p)]
                print pag
            elif opcion=='g':
                self.mostrar()
            elif opcion=='r':
                p = raw_input("Ingrese id_router: ")
                print  self.lista_routers[int(p)].info()
                print  "vecinos: "+ `self.red.neighbors(self.lista_routers[int(p)])`
            elif opcion=='e':
                p = raw_input("Ingrese id_pagina: ")
                t = raw_input("Ingrese id terminal de destino: ")
                if p=='s' or t=='s': break
                print empaquetar(self.lista_paginas[int(p)],self.lista_terminales[int(t)].ip_terminal)
            elif opcion=='d':
                p = raw_input("Ingrese id_pagina: ")
                t = raw_input("Ingrese id terminal de destino: ")
                if p=='s' or t=='s': break
                self.pedir_pagina(self.lista_paginas[int(p)],self.lista_terminales[int(t)])
            elif opcion=='s':
                self.paso()
            
    def pedir_pagina(self, pagina, t_destino):
        #empaqueto la pagina
        paquetes = empaquetar(pagina, t_destino.ip_terminal)
        
        print "Se ha solicitado la pagina "+`pagina.id_pagina`
        print "IP origen: "+`pagina.ip_origen`
        print "IP destino: "+`t_destino.ip_terminal`
        r = t_destino.ip_terminal.id_router

        
        #y muevo los paquetes al primer router del camino
        vecino = self.determinar_vecino(self.lista_routers[pagina.ip_origen.id_router], self.lista_routers[t_destino.ip_terminal.id_router])       
        
        
        #print self.lista_routers[pagina.ip_origen.id_router].cola_vecino
        self.lista_routers[pagina.ip_origen.id_router].encolar(paquetes, vecino) 
   
    def camino(self, r_origen, r_destino):
        """Dado un router de origen y uno de destino, devuelve el camino menos 
        costoso segun el balance de carga actual
        """
        puentes = [(r1,r2,costo) for (r1,r2,[costo,t]) in self.red.edges()] 
        
       
        G = networkx.XGraph()
        G.add_edges_from(puentes)       
                
        return networkx.dijkstra_path(G, r_origen, r_destino)
    
    def determinar_vecino(self, r_origen, r_destino):
        """Dado un router de origen y uno de destino, devuelve el paso inmediato segun el camino actual
        """
        camino = self.camino(r_origen, r_destino)

        if len(camino)>1:
            return camino[1]
        else:
            return camino[0]
        
    def paso(self, iteraciones=1):
        """Paso envia secuencialmente la cantidad de paquetes posibles a cada vecino.        
        """
        global tam_paquete
        
        while iteraciones>0:
            iteraciones -= 1 #decremento el numero de iteraciones
            if iteraciones>0: print "********* Iteracion "+`iteraciones`+" **************"
            for router in self.red.nodes():
                #por cada vecino del router de la red, envio la cantidad posible de paquetes hacia el siguiente router
                
                for vecino in [self.lista_routers[x] for x in router.cola_vecino.keys()]:
                    if vecino is router: continue #ignoro el paso de mover paquetes hacia si mismo
                    long_cola = router.long_cola_vecino(vecino)                
                    if long_cola==0: continue #si la cola a un vecino está vacia, la ignoro y sigo con el siguiente vecino
                    
                    
                    #determino la cantidad de paquetes que se pueden enviar. Si la cantidad en la cola es menor a lo posible, los tomo todos. 
                    tasa = self.red.get_edge(router,vecino)[1]
                    cant_paquetes = int(tasa/tam_paquete) if int(tasa/tam_paquete) < long_cola else long_cola
                    print "****Moviendo "+`cant_paquetes`+" paquetes desde "+`router`+" hacia "+`vecino`+ "(tasa "+`tasa`+")"
                    
                    #desencolo la cantidad de paquetes de la cola del router.    
                    paquetes = router.desencolar(vecino, cant_paquetes)
                    
                    #por cada paquete (porque pueden tener distintos destinos), 
                    #encuentro cual es su destino final y encolo al siguiente paso del camino hasta alli
                    for paquete in paquetes:
                        router_destino = self.lista_routers[paquete.ip_destino.id_router]
                        #sabiendo el destino encuentro el siguiente paso. 
                        siguiente = self.determinar_vecino(vecino, router_destino)
                        print "destino: "+ `router_destino` + " Siguiente : "+ `siguiente`
                        #encolo el paquete al siguiente paso
                        vecino.encolar([paquete], siguiente)  #convierto paquetes en un secuencia de 1 elemento
                
                
                
            
        
        
        
        
        
        

###Clase Pagina###

class Pagina:
    """una pagina es una cadena de tamaño y caracteres aleatorios que pertenece a un terminal. 
    La pagina guarda el ip de origen"""
    
    def __init__(self,id,ip_origen):
        self.id_pagina = id
        self.long = random.choice(range(50,100))
        self.ip_origen = ip_origen
        vocales = 'aeiou'
        otros = 'bcdfghjklmnpqrstvwz'
        self.data = ''
        for i in range(self.long):
            if i%2:
                self.data += random.choice(vocales)
            else:
                self.data += random.choice(otros)
        
    def __len__(self):
        return self.long

    def __repr__(self):
        global tam_paquete
        salida = "------------------------------\n"
        salida += "Pagina Nº"+`self.id_pagina`+" en "+`self.ip_origen`+"\n"
        salida +="Data ("+ `self.long`+"): "+ `self.data`+"\n"
        salida +="paquetes: "+ `int(self.long/tam_paquete)+1`+"\n"
        return salida
        
        
        
############Clase Terminal######
class Terminal:
    """el objeto terminal está conectado a un router y puede ser servidor o cliente indistintamente
    los terminales tienen paginas generadas aleatoriamente. La transferencia entre terminal y router 
    se considera infinita, por lo que solo toma un ciclo mover toda una pagina al primer router.
    """
    
    def __init__(self, ip):
        self.ip_terminal = ip       #seteo el id del terminal y del router al que esta conectado
        self.id_router = ip.id_router
        
        self.paginas = []       #incializo la lista de paginas que contiene este terminal
        
    
    def set_pagina(self, pagina):
        self.paginas.append(pagina)
    def __repr__(self):
        return "T: "+`self.ip_terminal`
    def info(self):
        print self
        print "Cantidad de paginas: "+`len(self.paginas)`
        print "Lista de paginas:"+`[p.id_pagina for p in self.paginas]`
        

#####################clase paquete##############3

class Paquete:
    def __init__(self, numero_paq, id_pagina, total, ip_origen, ip_destino, data):
        self.id_paquete = numero_paq
        self.id_pagina = id_pagina
        self.total = total       
        self.ip_origen = ip_origen
        self.ip_destino = ip_destino
        self.data = data
    
    def __len__(self):
        """devuelve la longitud del paquete"""
        return len(self.data)
    
    def __repr__(self):
        return "P#"+`self.id_pagina`+"("+`self.id_paquete`+"/"+`self.total`+")"
    
    def info(self):
        print "P#"+`self.id_pagina`+"("+`self.numero_paq`+"/"+`self.total`+")"
        print "data: "+self.data
        print "tamaño: "+`len(self)`
        print "ip origen: "+`self.ip_origen`+"\tip destino:"+`self.ip_destino`
        
        

##################### MAIN #########################


ad = Admin2()
ad.mostrar()
###ad.demo()
p = ad.lista_paginas[1] #probablemente en el primer router
t = ad.lista_terminales[10] #en algun router subsecuente

ad.pedir_pagina(p,t)



##if not leer_archivo:
##    networkx.write_adjlist(ad.red, nombre_archivo)
##
##org_dst = (ad.red.nodes()[0], ad.red.nodes()[1])





