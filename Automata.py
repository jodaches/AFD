from itertools import groupby
from anytree import Node, RenderTree, PostOrderIter, PreOrderIter
from Estado import Estado
from graphviz import Digraph
import re

class Automata:

    def __init__(self, er):
        self.nodeId = 0
        self.tablaSiguientes = {}
        self.diccionarioHojas = {}
        self.estados = {}
        self.tablaTransiciones = []
        self.er = "(" + er + ")$"
        self.tokens = self.obtenerTokens(self.er)
        self.raiz = self.crearArbol(self.tokens)
        print(RenderTree(self.raiz))
        self.calcularAnulablesPrimerosUltimos()
        tabla = self.crearTablaSiguientes()
        self.crearTablaTransiciones()
        print("end")

    def obtenerTokens(self, er):
        allTokens = re.findall(r'[^\+\*\(\)\-\|]|\+|\*|\(|\)|\[|\]|\-|\|', er)
        tokens = []
        i=0
        while i < len(allTokens):
            token = allTokens[i]
            print(token, " ", i)
            if token == "(":
                count = 1
                i += 1
                while count > 0 and i < len(allTokens):
                    token += allTokens[i]
                    if allTokens[i] == "(":
                        count += 1
                    elif allTokens[i] == ")":
                        count -= 1
                    i += 1
                i -= 1

            if token == "[":
                count = 1
                i += 1
                while count > 0 and i < len(allTokens):
                    token += allTokens[i]
                    if allTokens[i] == "]":
                        count -= 1
                    i += 1
                i -= 1

            tokens.append(token)
            i+=1

        return tokens

    def analizar(self):
        self.analizarER(self.er)

    def analizarER(self, er):
        return 0

    # retorna un node
    def crearArbol(self, tokens):
        i = 0
        nodoActual = None
        nodoAnterior = None
        nodoOr = None

        gruposSeparadosPorOR = [list(g) for k, g in groupby(tokens, lambda x: x != '|') if k]


        while i < len(gruposSeparadosPorOR):
            grupo = gruposSeparadosPorOR[i]
            nodoActual = self.crearSubArbol(grupo)

            if nodoAnterior:
                nodoOr = self.nuevoNodo("|")
                nodoAnterior.parent = nodoOr
                nodoActual.parent = nodoOr
                nodoActual = nodoOr

            nodoAnterior = nodoActual

            i += 1

        return nodoActual

    def nuevoNodo(self, token):
        self.nodeId+=1
        return Node(token, nodeId=self.nodeId)

    def crearSubArbol(self, grupo):
        j = 0
        nodoAnterior = None

        while j < len(grupo):

            token = grupo[j]
            tokenSiguiente = None
            if j+1 < len(grupo):
                tokenSiguiente = grupo[j+1]

            if tokenSiguiente == "+" or tokenSiguiente == "*" or tokenSiguiente == "?":
                nodoActual = self.nuevoNodo(tokenSiguiente)
                nodoHijo = self.crearArbol([token])
                nodoHijo.parent = nodoActual
                j+=1

            elif token.startswith("("):  # PARENTESIS
                nodoActual = self.crearArbol(self.obtenerTokens(token[1:-1]))

            elif re.findall(r'^([^\+\*\(\)\[\]\-\|]|\[.*\])$', token):  # VALOR ESPECIFICO
                nodoActual = self.nuevoNodo(token)

            if nodoAnterior:
                nodoAnd = self.nuevoNodo(".")
                nodoAnterior.parent = nodoAnd
                nodoActual.parent = nodoAnd
                nodoActual = nodoAnd

            nodoAnterior = nodoActual
            j += 1

        return nodoActual

    def calcularAnulablesPrimerosUltimos(self):
        #numerar hojas
        i=0
        for nodo in PreOrderIter(self.raiz):
            if nodo.is_leaf:
                i += 1
                nodo.numeroHoja = i
                self.diccionarioHojas[i] = nodo.name

        for nodo in PostOrderIter(self.raiz):
            self.calcularAnulable(nodo)
            self.calcularPrimerosUltimos(nodo)
            print(nodo.name, " an: ", nodo.anulable, " p: ", nodo.primeros, " u:", nodo.ultimos)

    def calcularAnulable(self, nodo):
        flag = None

        if nodo.is_leaf:
            flag = False
        elif nodo.name == "*" or nodo.name == "?":
            flag = True
        elif nodo.name == "+":
            flag = nodo.children[0].anulable
        elif nodo.name == "|":
            flag = nodo.children[0].anulable or nodo.children[1].anulable
        elif nodo.name == ".":
            flag = nodo.children[0].anulable and nodo.children[1].anulable
        nodo.anulable = flag

    def calcularPrimerosUltimos(self, nodo):
        ultimos = None
        primeros = None

        if nodo.is_leaf:
            primeros = [nodo.numeroHoja]
            ultimos = [nodo.numeroHoja]

        elif nodo.name == "*" or nodo.name == "?" or nodo.name == "+":
            primeros = nodo.children[0].primeros
            ultimos = nodo.children[0].ultimos

        elif nodo.name == "|":
            si = nodo.children[0]
            sd = nodo.children[1]
            primeros = si.primeros + sd.primeros
            ultimos = si.ultimos + sd.ultimos

        elif nodo.name == ".":
            si = nodo.children[0]
            sd = nodo.children[1]
            primeros = si.primeros + sd.primeros if si.anulable else si.primeros
            ultimos = si.ultimos + sd.ultimos if sd.anulable else sd.ultimos

        nodo.ultimos = ultimos
        nodo.primeros = primeros

    def crearTablaSiguientes(self):
        for nodo in PreOrderIter(self.raiz):
            if nodo.name == ".":
                si = nodo.children[0]
                sd = nodo.children[1]
                for i in si.ultimos:
                    self.tablaSiguientes[i] = self.tablaSiguientes[i] + sd.primeros if i in self.tablaSiguientes else sd.primeros

            elif nodo.name == "*" or nodo.name == "+":
                for i in nodo.ultimos:
                    self.tablaSiguientes[i] = self.tablaSiguientes[i] + nodo.primeros if i in self.tablaSiguientes else nodo.primeros

    def crearTablaTransiciones(self):
        estado0 = Estado(",".join(str(e) for e in self.raiz.primeros), self.raiz.primeros)
        estado0.nombre = "S0"
        self.hojaAceptacion = self.raiz.ultimos[0]

        self.estados[estado0.etiqueta] = estado0.nombre
        self.tablaTransiciones.append(estado0)

        i=0
        for estado in self.tablaTransiciones:

            for hoja in estado.hojas:

                #SI TIENE LA HOJA DE ACEPTACION ES ESTADO DE ACEPTACION
                if hoja == self.hojaAceptacion:
                    estado.aceptacion = True
                    continue

                siguientesDeLaHoja = self.tablaSiguientes[hoja]
                estadoEncontrado = Estado(",".join(str(e) for e in siguientesDeLaHoja), siguientesDeLaHoja)

                if estadoEncontrado.etiqueta not in self.estados:
                    i += 1
                    estadoEncontrado.nombre = "S" + str(i)
                    self.estados[estadoEncontrado.etiqueta] = estadoEncontrado.nombre
                    self.tablaTransiciones.append(estadoEncontrado)

                estado.transiciones[hoja] = self.estados[estadoEncontrado.etiqueta]

    def dibujarAFD(self):
        dot = Digraph(comment='The Round Table')

        for estado in self.tablaTransiciones:
            dot.node(estado.nombre, peripheries="2" if estado.aceptacion else "1")

        for estado in self.tablaTransiciones:
            for hoja, estadoObjetivo in estado.transiciones.items():
                dot.edge(estado.nombre, estadoObjetivo, label=self.diccionarioHojas[hoja])

        dot.format = "png"
        dot.render('afd.gv')
