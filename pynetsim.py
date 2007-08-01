#! /usr/bin/env python
# -*- coding: utf8 -*-

"""(c) Martin Gaitan y Leonardo Rocha Junio de 2007.
Este programa es Software Libre bajo los términos de la licencia GPL 3.0



Requerimientos
--------------------

    * requiere python 2.5 (por las formas cortas de la sentencia if)
    * libreria networkx . https://networkx.lanl.gov/wiki
	
	En ubuntu/debian: 

	$sudo apt-get install python-networkx

    * libreria matplotlib/pylab para graficar. http://matplotlib.sourceforge.net/
	
	$sudo  apt-get install python-matplotlib 

Ejecucion basica
-----------------------

import pynetsim
red = pynetsims.Red()
red.demo()

Forma de Uso:
----------------------
en la consola escribir:

$ python pynetsim.py 

(esto inicia el programa en modo no interactivo)

Otra forma, con la consola de Python:
Abrir una consola interactiva de Python en el directorio donde se encuentra el archivo.
en el prompt:

>>> import pynetsim

se iniciará el programa interactivo de forma automática

Documentacion
----------------

El codigo se ha autodocumentado en formato PyDoc (funciones, metodos y demas). Para ver una 
descripcion de cada uno de los elementos ver el archivo 

pynetsim.html



"""

import random
import networkx
import pylab, matplotlib
import string
from copy import copy

"""en este fuente se definen las clases router, adminitrador, pagina, paquete, etc. 
las clases no heredan sino que interactuan a nivel de instanciacion: ie, una pagina se compone de n cantidad de paquetes
"""

CANT_ROUTERS = 5	#cantidad de routers en la red
MAX_TERMINALES = 5   	#maxima cantidad relativa de terminales conectados a cada router 
MAX_PAGINAS = 4		#maxima cantidad de paginas por terminal
ASINCRONICO = False 	#define si el peso de las aristas es simetrico o no
MAX_CONECTIVIDAD = 2 	#variable estimativa. con cuantos vecinos como maximo puede conectarse un router 
MAX_TRANSFERENCIA = 30 #velicidad de transfencia max entre un router y otro (en caracteres)
TAM_PAQUETE = 3        #cuantos caracteres maximo forman un paquete?
LEER_ARCHIVO = False    #si no se lee genera un grafo aleatorio y lo guarda
GRABAR_ARCHIVO = False
NOMBRE_ARCHIVO = "datos.dat"
FIJO=True

def clearscreen(numlines=100):
    """Clear the console.

    numlines is an optional argument used only as a fall-back.
    """
    import os
    if os.name == "posix":
        # Unix/Linux/MacOS/BSD/etc
        os.system('clear')
    elif os.name in ("nt", "dos", "ce"):
        # DOS/Windows
        os.system('CLS')
    else:
        # Fallback for other operating systems.
        print '\n' * numlines    
    

def dibujar(grafo, edges=False, pos=False):
    """esta funcion dibuja la red (grafo) incluyendo label en los puentes
        edges es una tupla triple del tipo (n1,n2,valor). La inclusion del label en el puente se hace a mano. 
    """
    if not edges: edges = grafo.edges()
    if not pos: pos = networkx.drawing.spring_layout(grafo)
    
    pylab.clf()     #limpia la figura actual
    F=networkx.XGraph()
    F.add_edges_from(edges)
    ax=matplotlib.pylab.gca()
    ax.set_xticks([])
    ax.set_yticks([])
    edge_pos = dict( ((n1,n2),(pos[n1]+pos[n2])/2) for n1,n2,v in F.edges() )
    edge_labels = dict( ((x,y), z) for x,y,z in F.edges() )
    networkx.draw_networkx_labels(grafo, edge_pos, edge_labels)
    networkx.draw_networkx(grafo, pos, True)   
    pylab.show()


class Router:
    """esta clase define el elemento principal de la red: el router. El router se conecta con otros vecinos, formando una red.     
    a la vez, el router tiene conectado varios terminales que son los que contienen y solicitan paginas. 
    """      
       
    def __init__(self, id):
        """incializador de la clase router. setea id e iniciliaza la tabla de routeo"""
        global MAX_TERMINALES
        
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
            #agrega todos los paquetes en la cola hacia el router vecino
            #si es el destino final de los paquetes, analizo completitud
            if self is r_vecino: 
                self.analizar_completitud(r_vecino)
        except:
            print "vecino no valido"
    
    def desencolar(self, r_vecino,cant_paquetes):
        """devuelve una cantidad de paquetes del final de la cola hacia el vecino especificado"""
        
        #desencola los or 'cant_paquetes'
        paq = self.cola_vecino[r_vecino.id_router][-cant_paquetes:]
        #actualiza la cola
        self.cola_vecino[r_vecino.id_router] = self.cola_vecino[r_vecino.id_router][:-cant_paquetes]
        #devuelve
        return paq
    
     
    
    def analizar_completitud(self, r_vecino):
        """
        
        analiza la cola hacia el vecino en busca de una pagina completa. Si la encuentra la quita de la cola y entrega"""

        print "analizando completitud"

        cola_parcial = {}
        #separa los paquetes según la pagina que correspondan
        for paquete in self.cola_vecino[r_vecino.id_router]:
            try: 
                cola_parcial[paquete.id_pagina].append(paquete)
            except:
                cola_parcial[paquete.id_pagina] = []
                cola_parcial[paquete.id_pagina].append(paquete)
                

#        print "cola pacial:"+`cola_parcial` 

        #evalúa si la cantidad de paquetes de la pagina esta completa. el dato lo saco del primer paquete
        for id_pagina in cola_parcial.keys():
            if cola_parcial[id_pagina][0].total == len(cola_parcial[id_pagina]):
                print "----Se ha completado la pagina Nº"+`id_pagina`+ "hacia "+ `cola_parcial[id_pagina][0].ip_destino`+" ----"
                
                ###completar! habria que ordenar los paquetes y mostrar la pagina.  ###
                    
                #quitando los paquetes de esta pagina de la cola"
                for paquete in cola_parcial[id_pagina]:
                    #quita el paquete (posicion index donde se encuentra el paquete 'paquete' de la cola al vecino
                    del self.cola_vecino[r_vecino.id_router][self.cola_vecino[r_vecino.id_router].index(paquete)]
                
    
    def actualizar_cola(self, nueva_cola):
        self.cola_vecino = nueva_cola
    
        
    def __repr__(self):
        return "R"+`self.id_router`
    
        
class Ip:
    def __init__(self, id_terminal, id_router):
        self.id_terminal = id_terminal
        self.id_router = id_router
    def __repr__(self):
        return `self.id_router`+"."+`self.id_terminal`
    

class Red:
    """Otra estructura de administrador basada en grafos del paquete networkX   
    ahora el conocimiento de la red lo tiene el grafo mismo, y se consultan sus metodos para saber los vecinos
    etc.
    """  
    def __init__(self):
        global CANT_ROUTERS
        global ASINCRONICO
        global MAX_CONECTIVIDAD
        global MAX_TRANSFERENCIA
        global desde_archivo
        global NOMBRE_ARCHIVO
        global MAX_TERMINALES
        global MAX_PAGINAS
        
        self.lista_terminales = {} #mapa id->terminal
        self.lista_paginas = {}  #mapa id->pagina
        self.lista_routers = {}  #mapa id->router
        
    
        if LEER_ARCHIVO:
        #lee el grafo desde un archivo
            self.red = networkx.read_adjlist(NOMBRE_ARCHIVO)
        else:
        #create empty directed graph with edge data.     
            self.red = networkx.XGraph()
            
               
            for i in range(CANT_ROUTERS):
                r = Router(i)
                self.red.add_node(r)
                self.lista_routers[i] = r
            #el grafo tiene distintos valores en sus aristas bajo la lista [costo,tasa]
            #donde costo = Cola[vecino]/floor(tasa/TAM_PAQUETE)
            
            
            for router in self.red.nodes():
                #agrega una cantidad de vecinos al azar para cada router
                posibles = self.red.nodes()
                for vec_actual in [self.lista_routers[x] for x in router.cola_vecino.keys()]:
                    posibles.remove(vec_actual)
                    
                max = MAX_CONECTIVIDAD if MAX_CONECTIVIDAD <= len(posibles) else len(posibles) #uso version corta de if 
                vecinos_asignados = random.sample(posibles, random.choice(range(1, max +1 )))
                for x in vecinos_asignados:
                    tasa = random.choice(range(TAM_PAQUETE, MAX_TRANSFERENCIA)) #el minimo es el tamaño de 1 paquete
                    self.red.add_edge(router, x, [1 ,tasa])
                    #inicializa las colas
                    router.cola_vecino[x.id_router] = []
                    x.cola_vecino[router.id_router] = []
        self.pos = networkx.drawing.spring_layout(self.red) #FIJO la posicion de los nodos del grafo        

        #genera terminales aleatoriamente y paginas dentro de el. Se lleva un diccionario 
        #para el admin tenga i  nformacion para buscar terminales y paginas mediante su id
        counter = 0
        counter_p = 0
        for router in self.red.nodes():
            for id in range(random.choice(range(1,MAX_TERMINALES))):
                counter += 1
                
                t = Terminal(Ip(counter, router.id_router)) #genero el terminal
                router.set_terminal(t)   #lo asigno a un router
                self.lista_terminales[counter] = t   #lo agrego al diccionario para busquedas rapidas mediante id
        
        #genera paginas aleotariamente. Cada terminal tiene al menos 1 pagina.

            for terminal in router.terminales:
                for i in range(1, random.choice(range(MAX_PAGINAS))):
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

   
            
    def pedir_pagina(self, pagina, t_destino):
        #empaqueta la pagina
        
        if pagina.__class__.__name__ == "int": pagina = self.lista_paginas[pagina]
        if t_destino.__class__.__name__ == "int" : t_destino = self.lista_terminales[t_destino]
        
        paquetes = pagina.empaquetar(t_destino.ip_terminal)
        
        print "Se ha solicitado la pagina "+`pagina.id_pagina`
        print "IP origen: "+`pagina.ip_origen`
        print "IP destino: "+`t_destino.ip_terminal`
        r = t_destino.ip_terminal.id_router

        
        #y mueve los paquetes al primer router del camino
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
        global TAM_PAQUETE
        
        vuelta = 0
        while vuelta<iteraciones:
            vuelta += 1 #decrementa el numero de iteraciones
            if iteraciones>0: print "********* Iteracion "+`vuelta`+" **************"
            for router in self.red.nodes():
                #por cada vecino del router de la red, envia la cantidad posible de paquetes hacia el siguiente router
                
                for vecino in [self.lista_routers[x] for x in router.cola_vecino.keys()]:
                    if vecino is router: continue #ignora el paso de mover paquetes hacia si mismo
                    long_cola = router.long_cola_vecino(vecino)                
                    if long_cola==0: continue #si la cola a un vecino está vacia, la ignoro y sigo con el siguiente vecino
                    
                    #determina la cantidad de paquetes que se pueden enviar. Si la cantidad en la cola es menor a lo posible, los tomo todos. 
                    tasa = self.red.get_edge(router,vecino)[1]
                    cant_paquetes = int(tasa/TAM_PAQUETE) if int(tasa/TAM_PAQUETE) < long_cola else long_cola
                    print "****Moviendo "+`cant_paquetes`+" paquetes desde "+`router`+" hacia "+`vecino`+ "(tasa "+`tasa`+")"
                    
                    #desencola la cantidad de paquetes de la cola del router.    
                    paquetes = router.desencolar(vecino, cant_paquetes)
                    
                    #por cada paquete (porque pueden tener distintos destinos), 
                    #encuentra cual es su destino final y encolo al siguiente paso del camino hasta alli
                    for paquete in paquetes:
                        print "Paquete*****"+ `paquete`
                        router_destino = self.lista_routers[paquete.ip_destino.id_router]
                        #sabiendo el destino encuentro el siguiente paso. 
                        siguiente = self.determinar_vecino(vecino, router_destino)
                        print "destino: "+ `router_destino` + " Siguiente : "+ `siguiente`
                        #encola el paquete al siguiente paso
                        vecino.encolar([paquete], siguiente)  #convierto paquetes en un secuencia de 1 elemento

    def actualizar(self):
        """este metodo actualiza los valores del primer valor en la arista, que representa
        el costo (en ciclos) que representa enviar los paquetes entre un nodo y otro. 
        
        En este punto, interfiere la carga actual de la red. 
        Por ejemplo, por más que Entre 1 y 3 hay una conexion rapida, pero hay muchos paquetes hacia 3, 
        entonces será preferible enviarla por otro camino. 
        
        Ademas del valor, se deben actualizar las colas de cada router, esto es, desencolar cada paquete y encolarlo en la cola que corresponda al nuevo camino hacia el destino. 
        """
        global TAM_PAQUETE
        for router in self.red.nodes():
            router.cola_temp ={} #cola temporal
            for vecino in [self.lista_routers[x] for x in router.cola_vecino.keys()]:             
                router.cola_temp[vecino.id_router] = [] #incializa la cola temporal hacia el nuevo vecino
                if vecino is router: continue #ignora el paso de mover paquetes hacia si mismo
                long_cola = router.long_cola_vecino(vecino)                
                if long_cola==0: continue #si la cola a un vecino está vacia, la ignoro y sigo con el siguiente vecino
                tasa = self.red.get_edge(router,vecino)[1]
                costo = int(long_cola/int(tasa/TAM_PAQUETE)) 
                #actualiza el valor de costo de transferencia actual entre dos routers. 
                self.red.add_edge(router, vecino, [costo ,tasa])
                
        for router in self.red.nodes():
           
            for vecino in [self.lista_routers[x] for x in router.cola_vecino.keys()]:
                #actualizo las colas de router (para cada vecino). 
                for i in range(router.long_cola_vecino(vecino)):
                    paquete = router.desencolar(vecino, 1) #desencolo el paquete en cuestion. 
                    paquete = paquete[0]  #el metodo desencolar devuelve una lista, aunque sea 1 elemento
                    router_destino = self.lista_routers[paquete.ip_destino.id_router] #extraigo el destino final del paquete
                    siguiente = self.determinar_vecino(router, router_destino) #sabiendo el destino encuentro el nuevo siguiente paso. 
                    router.cola_temp[siguiente.id_router].append(paquete) 
            
            router.actualizar_cola(router.cola_temp)
        self.mostrar() #para que se actualice la red.
         
        
    def demo(self):
        """un metodo para obetener informacion e interactuar en forma dinamica a traves de un menu"""
	clearscreen()
        while 1:
            print "##############################"
            print "a :\t info Red"
	    print "r :\t info router"
            print "t :\t info terminal"
            print "p :\t info pagina"
            print "g :\t ver grafo de red"  
            print "e :\t empaquetar pagina"
            print "d :\t pedir pagina"
            print "s :\t paso"
	    print "h :\t AYUDA"
            print "S :\t salir"
            print "##############################"
            opcion = raw_input("Ingrese opcion: ")
            
            if opcion=='S':
		print " Saludos...."
                break
	    elif opcion=="h":
		clearscreen()
		print "############ AYUDA #################"
		print "Cada momento de simulación consta de:"
            	print "pedir una o más páginas y"
	        print "luego llamar a la función paso"
        	print "puede luego observarse viendo el grafo"
            	print "o pedir la información de la red, "
            	print "terminales, páginas o routers."
            	print "##############################"

            elif opcion=='a':
                self.info()
            elif opcion=='t':
		while 1:
			try:
		                t = raw_input("Ingrese id terminal  o (s)alir: ")
                		if t=='s': break
		                term = self.lista_terminales[int(t)]
                		print "---el terminal tiene los siguientes datos"
		                term.info()
				break
			except:
				print "hubo un problema con el terminal elegido. Intente de nuevo"
            elif opcion=='p':
		while 1:
	                p = raw_input("Ingrese id_pagina o (s)alir: ")
        	        if p=='s': break
			try:
		                pag = self.lista_paginas[int(p)]
		                print pag
				break
			except:
				print "Hubo un problema con la pagina que eligio. Intente de nuevo"
				continue		    
            elif opcion=='g':
                self.mostrar()
            elif opcion=='r':
		while 1:
			try:
	                	p = raw_input("Ingrese id_router o (s)alir: ")
		                if p=='s': break
        		        print  self.lista_routers[int(p)].info()
		                print  "vecinos: "+ `self.red.neighbors(self.lista_routers[int(p)])`
				break
			except:
				print "Hubo un problema con el router que eligio. Intente de nuevo"
				continue


            elif opcion=='e':
		while 1:
			try:
				p = raw_input("Ingrese id_pagina o (s)alir: ")
                		t = raw_input("Ingrese id terminal de destino: ")
		                if p=='s' or t=='s': break
                		print self.lista_paginas[int(p)].empaquetar(self.lista_terminales[int(t)].ip_terminal)
				break
			except:
				print "hubo un problema con la pagina o el terminal elegidos. Intente de nuevo"
				continue

            elif opcion=='d':
		while 1:
			try:
		                p = raw_input("Ingrese id_pagina o (s)alir: ")
		                t = raw_input("Ingrese id terminal de destino: ")
		                if p=='s' or t=='s': break
		                self.pedir_pagina(self.lista_paginas[int(p)],self.lista_terminales[int(t)])
				break
			except:
				"Hubo un problema con la pagina el terminal elegidos. Intente de nuevo"
				continue
            elif opcion=='s':
                self.paso()

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
    
    def empaquetar(self, ip_destino, tam=TAM_PAQUETE):
        """recibe una pagina y devuelve una lista de paquetes"""
        
        global TAM_PAQUETE
        
        paquetes = []
        total = int(self.long/TAM_PAQUETE)+1
        
        for i in range(total):
            data = self.data[i*tam:(i+1)*tam]
            paq = Paquete(i, self.id_pagina,total, self.ip_origen, ip_destino, data)
            paquetes.append(paq)
        return paquetes
        
    def __len__(self):
        return self.long

    def __repr__(self):
        global TAM_PAQUETE
        salida = "------------------------------\n"
        salida += "Pagina Nº"+`self.id_pagina`+" en "+`self.ip_origen`+"\n"
        salida +="Data ("+ `self.long`+"): "+ `self.data`+"\n"
        salida +="paquetes: "+ `int(self.long/TAM_PAQUETE)+1`+"\n"
        return salida
        
        
        
############Clase Terminal######
class Terminal:
    """el objeto terminal está conectado a un router y puede ser servidor o cliente indistintamente
    los terminales tienen paginas generadas aleatoriamente. La transferencia entre terminal y router 
    se considera infinita, por lo que solo toma un ciclo mover toda una pagina al primer router.
    """
    
    def __init__(self, ip):
        self.ip_terminal = ip       #setea el id del terminal y del router al que esta conectado
        self.id_router = ip.id_router
        
        self.paginas = []       #incializa la lista de paginas que contiene este terminal
        
    
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

print """Bienvenido a PynetSim, un software de simulación para el estudio del trafico de redes.
(c) Martin Gaitan y Leonardo Rocha Junio de 2007.

Este programa es Software Libre bajo los términos de la licencia GPL 3.0"""


if __name__ == '__main__':
	"""si el el programa se ejecuta en modo no interactivo, invoco el modo 'demo'. """

	print """Usted ha ejecutado el software en modo NO interactivo. Se ejecutará el modo demo() para interactuar con la red. """
	raw_input("Creando la red aleatoriamente....Presione una tecla para continuar")
	

	ad = Red()
	ad.demo()
else:
	print """Usted ha ejecutado el software en modo interactivo. En primera instancia, cree un objeto tipo Red().
"""
	



