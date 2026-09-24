import ZODB, ZODB.FileStorage
import transaction
from BTrees.OOBTree import OOBTree

class GestorBDOO:
    def __init__(self, archivo_db="movilidad_xalapa.fs"):
        self.storage = ZODB.FileStorage.FileStorage(archivo_db)
        self.db = ZODB.DB(self.storage)
        self.conexion = self.db.open()
        self.root = self.conexion.root()

        # Inicializar colecciones de objetos si no existen
        if 'vehiculos' not in self.root:
            self.root['vehiculos'] = OOBTree()
        if 'clientes' not in self.root:
            self.root['clientes'] = OOBTree()
        if 'rentas' not in self.root:
            self.root['rentas'] = OOBTree()
        if 'mantenimientos' not in self.root:
            self.root['mantenimientos'] = OOBTree()
        if 'pagos' not in self.root:
            self.root['pagos'] = OOBTree()

    def guardar(self):
        transaction.commit()

    def cerrar(self):
        self.conexion.close()
        self.db.close()

    # --- CONSULTAS OBLIGATORIAS DEL PROYECTO ---
    
    #Listar vehículos
    def listar_vehiculos(self):
        return list(self.root['vehiculos'].values())

    #Buscar vehículo por identidad
    def buscar_vehiculo_por_id(self, id_vehiculo):
        return self.root['vehiculos'].get(id_vehiculo, None)

    #Mostrar vehículos disponibles
    def vehiculos_disponibles(self):
        return [v for v in self.root['vehiculos'].values() if v.estado == "DISPONIBLE"]

    #Mostrar vehículos rentados
    def vehiculos_rentados(self):
        return [v for v in self.root['vehiculos'].values() if v.estado == "RENTADO"]

    #Mostrar vehículos en mantenimiento
    def vehiculos_en_mantenimiento(self):
        return [v for v in self.root['vehiculos'].values() if v.estado == "EN_MANTENIMIENTO"]

    #Mostrar rentas de un cliente
    def rentas_de_cliente(self, id_cliente):
        return [r for r in self.root['rentas'].values() if r.cliente.id_cliente == id_cliente]

    #Mostrar el vehículo asignado a una renta
    def vehiculo_de_renta(self, id_renta):
        renta = self.root['rentas'].get(id_renta)
        return renta.vehiculo if renta else None

    #Mostrar rentas activas
    def rentas_activas(self):
        return [r for r in self.root['rentas'].values() if r.estado == "ACTIVA"]

    #Calcular ingresos
    def calcular_ingresos(self):
        return sum(pago.monto for pago in self.root['pagos'].values())

    #Identificar vehículos más rentados
    def vehiculos_mas_rentados(self):
        conteo = {}
        for renta in self.root['rentas'].values():
            v_id = renta.vehiculo.id_vehiculo
            conteo[v_id] = conteo.get(v_id, 0) + 1
        return sorted(conteo.items(), key=lambda x: x[1], reverse=True)

    #Identificar clientes con mayor número de rentas
    def clientes_mas_rentas(self):
        conteo = {}
        for renta in self.root['rentas'].values():
            c_nombre = renta.cliente.nombre
            conteo[c_nombre] = conteo.get(c_nombre, 0) + 1
        return sorted(conteo.items(), key=lambda x: x[1], reverse=True)

    #Mostrar vehículos que requieren mantenimiento
    def vehiculos_requieren_mantenimiento(self):
        return [v for v in self.root['vehiculos'].values() if v.requiere_mantenimiento()]

    #Consulta compleja (Ingreso promedio por categoría de vehículo)
    def ingreso_promedio_por_tipo(self):
        totales = {}
        conteo = {}
        for renta in self.root['rentas'].values():
            tipo = renta.vehiculo.tipo.nombre_categoria
            totales[tipo] = totales.get(tipo, 0) + renta.costo_total
            conteo[tipo] = conteo.get(tipo, 0) + 1
        return {tipo: totales[tipo] / conteo[tipo] for tipo in totales}