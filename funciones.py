#! /usr/bin/env python
# -*- coding: utf8 -*-

#simulador de trafico por internet implementado en Python. 
#Martin Gaitan y Leo Rocha
#Enero de 2007
#funciones.py

import sys

modo_global = "txt" # o "html"

def separador(mensaje, modo=modo_global):
    """define el tipo y formato del separador para la presentacion de informacion de salida y depuración"""
  
    #print modo
    if modo=="html":
        print "<p>"
        print mensaje+"<br/>"
        print "<hr/><p/>"
    elif modo=="txt":    
        print mensaje
        print "================================================================\n"


def imprime_matriz(matriz, sufijo="", titulo="", modo=modo_global):
    """imprime la matriz enviada (lista de listas) en formato html o txt"""
       
    if modo=="html":
        if titulo!="":
             print "<strong>"+titulo+"</strong>"
        print "<table border='1' cellpadding='5'><tr>\n<td>&nbsp;</td>"
        for i in range(len(matriz[0])):
            print "<td><bold>", i, "</bold></td>"
        print "<tr>"
        for i in range(len(matriz)):
            print "<tr><td><bold>", i , "</bold></td>"
            for celda in matriz[i]:
                print "<td>"
                if celda:
                    print celda, sufijo
                else:
                    print " - "
                print "</td>"
            print "</tr>"
        print "</table>"
    elif modo=="txt":
        pass



        
def pos_min(dic):
    """devuelve la clave cuyo valor es el minimo de todo el campo"""
    #minimo = min(dic.values())
    dicFlip = dict([(v,k) for k,v in dic.iteritems()])
    return dicFlip[min(dic.values())]


def dijkstra(origen, destino, red):
    """Dijkstra devuelve el costo menor desde origen hasta destino. Origen destino son objetos tipo router 
    y red es una lista de routers."""
    infinito = sys.maxint - 1
    costos = {}
    T = {} #T es el conjunto de todos los vertices cuya distancia a origen todavia no se determina. 
    for router in red:
        T[router.id_router]= True #Al principio ninguno se determinó.
        costos[router.id_router] = infinito
    costos[origen.id_router] = 0
    
    while T[destino.id_router]:
        #elegimos un vertice v perteneciente a T con costo(v) minimo. La primera vez serà v = origen. 
        Cmin = costos
        ok = False
        while 1:
            v = pos_min(Cmin)
            if T[v]:
                ok = True
            else:
                Cmin[v] = infinito
            if not ok:
                break
        #una vez encontrado el v lo quito del conjunto. 
        T[v] = False
        
        #por cada nodo adyacente a v encuentro el costo minimo
        for router in red:
            if red[v].es_vecino(router):
                costos[router.id_router] = min(costos(router.id_router), costos(v) + red[v].vecinos[router.id_router])
        return costos[destino.id_router]



##function dijkstra($a, $z, $pesos) {
##	global $cant_routers;
##	global $routers;
##	$L[$a] = 0;
##	for($i=0;$i<$cant_routers;$i++){
##		if($i!=$a) $L[$i] = 1300; //infinito (buuuu)
##	}
##	//$T es el conjunto de todos los vertices cuya distancia a a todavia no se determina. Al principio ninguno se determinó.
##	for ($i=0;$i<$cant_routers;$i++){
##		$T[$i] = true;
##	}
##
##	while($T[$z]==true){
##		//elegimos un $v perteneciente a $T con L(v) minimo. La primera vez serà $v = $a. 
##		$Lmin = $L; 
##		$ok = false;
##		do{
##			$v = posMinimo($Lmin);
##			if ($T[$v]==true) {
##				$ok = true;
##				}else{
##				$Lmin[$v] = 1300; //garantizo que ya no sea el menor... ;-)
##			}
##		}while(!$ok);
##
##		//una vez encontrado el v lo quito del conjunto. 
##		$T[$v] = false;
##	
##		//por cada nodo adyacente a v encuentro el costo minimo. 
##		for ($i=0;$i<$cant_routers;$i++){
##			if($routers[$v]->es_vecino($i)){	
##				$L[$i] = min($L[$i], $L[$v] + $pesos[$v][$i]); //$routers[$v]->peso($i));
##
##			}
##		}
##				
##		}
##
##	return $L[$z];	 
##}
	




##mat = [[3,2,1,3],[5,2,4,],[2,3,4,0]]
##imprime_matriz(mat, modo="html")





