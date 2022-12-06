import csv
import sys
from math import inf

class Grafo:
    def __init__(self, vertices_iniciales=None):
        self.aristas = {}
        if vertices_iniciales != None:
            for v in vertices_iniciales:
                self.aristas[v] = {}
        

    
    def agregar_vertice(self, v):
        self.aristas[v] = {}
    
    def agregar_arista(self, v, w, peso=1):
        self.aristas[v][w] = peso
    
    def existe_arista(self, v, w):
        return w in self.aristas[v]
    
    def obtener_vertices(self):
        lista = []
        for v in self.aristas.keys():
            lista.append(v)
        return lista
    
    def obtener_adyacentes(self, v):
        lista = []
        for w in self.aristas[v].keys():
            lista.append(w)
        return lista
    
    def obtener_aristas(self):
        conjunto = set()
        lista = []
        for v, dic_aristas_v in self.aristas.items():
            for w, peso in dic_aristas_v.items():
                #if (peso, w, v) in conjunto: continue
                conjunto.add((peso, v, w))
                lista.append((peso, v, w))
        return lista
    
    def existe_vertice(self, v):
        return v in self.aristas
    
        
    def modificar_peso(self, v, w, nuevo_peso):
        self.aristas[v][w] = nuevo_peso
        
    def obtener_peso(self, v, w):
        if not self.existe_arista(v, w):
            print(f"no hay arista {v}-{w}")

        return self.aristas[v][w]

def print_grafo(grafo, texto = ""):
    if texto != "":
        print("----------------------------------")
    print(texto)
    print("----------------------------------")
    for v, ar in grafo.aristas.items():
        print(f"aristas de {v}: {ar}") 
    print("----------------------------------")
    print()
    print()
    

def obtener_bottleneck(grafo, camino):
    i = 0
    bottleneck = inf
    
    while(True):
        primer_vertice = camino[i]
        segundo_vertice = camino[i+1]
        peso_actual = grafo.obtener_peso(primer_vertice, segundo_vertice)
        if (peso_actual < bottleneck):
            bottleneck = peso_actual
        
        if ( (i+1) == (len(camino)-1) ):
            break
        i += 1
    return bottleneck


def recorrido_bfs(grafo, v):
    padres = {}
    
    for vertice in grafo.obtener_vertices():
        padres[vertice] = None
        
    visitados = set()
    cola = []
    cola.append(v)

    while len(cola) != 0:
        w = cola.pop(0)

        for x in grafo.obtener_adyacentes(w):
            peso = grafo.obtener_peso(w, x)

            if x in visitados or peso == 0: continue
            padres[x] = w

            visitados.add(x)
            cola.append(x)
            
    return padres


def obtener_camino(grafo, s, t):
    
    padres = recorrido_bfs(grafo, s)
    if padres[t] == None:
        return [], 0
    vertice_actual = t
    camino = []

    while vertice_actual != s:
        camino.append(vertice_actual)
        vertice_actual = padres[vertice_actual]
    
    camino.append(s)
    camino.reverse()
 
    bottleneck = obtener_bottleneck(grafo, camino)
    return camino, bottleneck



def process_data(fileName, fuente, sumidero):
    
    grafo = Grafo()
    with open(fileName, 'r') as f:
        reader = csv.reader(f)
        
        grafo.agregar_vertice(fuente)
        grafo.agregar_vertice(sumidero)
        
        
        for row in reader:
            vertice_actual = str(row[0])
            if not grafo.existe_vertice(vertice_actual):
                grafo.agregar_vertice(vertice_actual)
            
            costo_equipo_1 = int(row[1])
            grafo.agregar_arista(fuente, vertice_actual, costo_equipo_1)
            
            costo_equipo_2 = int(row[2])
            grafo.agregar_arista(vertice_actual, sumidero, costo_equipo_2)
            
            for i in range(3, len(row), 2):
                nombre_dependencia = row[i]
                costo_dependencia = int(row[i+1])
                if (not grafo.existe_vertice(nombre_dependencia)):
                    grafo.agregar_vertice(nombre_dependencia)
                
                grafo.agregar_arista(vertice_actual, nombre_dependencia, costo_dependencia)
                
                grafo.agregar_arista(nombre_dependencia, vertice_actual, costo_dependencia)
                
            
    
    
    return grafo


def obtener_grafo_residual(grafo):
    lista_vertices = grafo.obtener_vertices()
    grafo_residual = Grafo(lista_vertices)
    lista_aristas = grafo.obtener_aristas()
    
    for peso, v, w in lista_aristas:
        grafo_residual.agregar_arista(v, w, peso)
    
    return grafo_residual
    

def max_flow(grafo, fuente, sumidero): 
    grafo_residual = obtener_grafo_residual(grafo)
             
    camino, bottleneck = obtener_camino(grafo_residual, fuente, sumidero)

    
    while (bottleneck != 0):
        
        i = 0
        v = camino[i]
        w = camino[i + 1]
        
        while (True):
            peso = grafo_residual.obtener_peso(v, w)
            
            if (not grafo_residual.existe_arista(w, v)):
                grafo_residual.agregar_arista(w, v, 0)
                
            # Si la acabo de crear vale 0, si ya tenia (por ser bidireccional o por alguna iteración adicional del FF) 
            # va a tener un valor
            peso_vuelta = grafo_residual.obtener_peso(w, v)
            
            
            grafo_residual.modificar_peso(w, v, peso_vuelta + bottleneck)
            grafo_residual.modificar_peso(v, w, peso - bottleneck)
            
            
            # Si fue la ultima arista, se corta
            if (w == sumidero):
                break
                
            i += 1
            v = camino[i]
            w = camino[i + 1]    
            
        camino, bottleneck = obtener_camino(grafo_residual, fuente, sumidero)

    return grafo_residual

        
         
""" Devuelve dos listas de tareas, la primera contiene las realizadas por el equipo 1, 
    y la seguna lista contiene las realizadas por el equipo 2. Devuelve como tercer valor el costo total    
"""
def procesar_grafo_residual(grafo_residual, fuente, sumidero):
    lista_equipo_1 = []
    lista_equipo_2 = []
    costo = 0
    tareas = grafo_residual.obtener_vertices()
    tareas.remove(fuente)
    tareas.remove(sumidero)
    for tarea in tareas:
        if grafo_residual.obtener_peso(fuente, tarea) == 0:
            lista_equipo_1.append(tarea)
            # Se le agrega el peso de la arista opuesta
            costo += grafo_residual.obtener_peso(tarea, fuente)
        else:
            lista_equipo_2.append(tarea)
            costo += grafo_residual.obtener_peso(sumidero, tarea)
    
    for tarea in lista_equipo_1:
        
        adyacentes_tarea = grafo_residual.obtener_adyacentes(tarea)
        adyacentes_tarea.remove(fuente)
        adyacentes_tarea.remove(sumidero)
        for correlativa in adyacentes_tarea:
            if (correlativa in lista_equipo_2):
                # Una de las dos aristas valdrá cero
                costo += int(grafo_residual.obtener_peso(tarea, correlativa)/2)
                costo += int(grafo_residual.obtener_peso(correlativa, tarea)/2)
    
    return lista_equipo_1, lista_equipo_2, costo
    
     
    
    
def imprimir_resultado(lista_equipo1, lista_equipo2, costo_total):
    print(f"Costo total: {costo_total}")
    
    print("Tareas realizadas por el equipo 1:")
    for tarea in lista_equipo1:
        print(tarea)
    
    
    print("Tareas realizadas por el equipo 2:")
    for tarea in lista_equipo2:
        print(tarea)
    
    



def main():
    fuente = "Equipo 1"
    sumidero = "Equipo 2"
    grafo = process_data(sys.argv[1], fuente, sumidero)
    grafo_residual = max_flow(grafo, fuente, sumidero)
    lista_equipo1, lista_equipo2, costo_total = procesar_grafo_residual(grafo_residual, fuente, sumidero)
    imprimir_resultado(lista_equipo1, lista_equipo2, costo_total)


main()