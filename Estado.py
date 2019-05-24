
class Estado:

    def __init__(self, etiqueta, hojas):
        self.etiqueta = etiqueta
        self.hojas = hojas
        self.transiciones = {}
        self.aceptacion = False
        self.nombre= ""
