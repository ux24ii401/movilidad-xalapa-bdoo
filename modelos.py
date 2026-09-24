import persistent
from datetime import datetime

class TipoVehiculo(persistent.Persistent):
    def __init__(self, id_tipo_vehiculo, nombre_categoria, descripcion, tarifa_base_dia):
        self.id_tipo_vehiculo = id_tipo_vehiculo
        self.nombre_categoria = nombre_categoria
        self.descripcion = descripcion
        self.tarifa_base_dia = tarifa_base_dia

class Vehiculo(persistent.Persistent):
    def __init__(self, id_vehiculo, placas, marca, modelo, anio, tipo, precio_dia, kilometraje, estado="DISPONIBLE"):
        self.id_vehiculo = id_vehiculo
        self.placas = placas
        self.marca = marca
        self.modelo = modelo
        self.anio = anio
        self.tipo = tipo  #Referencia al objeto TipoVehiculo
        self.precio_dia = precio_dia
        self.kilometraje = kilometraje
        self.estado = estado

    def esta_disponible(self):
        return self.estado == "DISPONIBLE"

    def rentar(self):
        #Reglas 1 y 2: Validar disponibilidad antes de rentar
        if self.estado != "DISPONIBLE":
            raise ValueError(f"El vehículo {self.placas} no está disponible (Estado actual: {self.estado}).")
        self.estado = "RENTADO"

    def devolver(self, nuevo_km):
        if nuevo_km < self.kilometraje:
            raise ValueError("El nuevo kilometraje no puede ser menor al kilometraje actual.")
        self.kilometraje = nuevo_km
        self.estado = "DISPONIBLE"

    def enviar_mantenimiento(self):
        self.estado = "EN_MANTENIMIENTO"

    def requiere_mantenimiento(self):
        return self.estado == "EN_MANTENIMIENTO" or self.kilometraje >= 100000

class Cliente(persistent.Persistent):
    def __init__(self, id_cliente, nombre, telefono, correo, licencia, tipo_cliente="PARTICULAR"):
        self.id_cliente = id_cliente
        self.nombre = nombre
        self.telefono = telefono
        self.correo = correo
        self.licencia = licencia
        self.tipo_cliente = tipo_cliente

class Reservacion(persistent.Persistent):
    def __init__(self, id_reservacion, cliente, vehiculo, fecha_inicio_prevista, fecha_fin_prevista):
        self.id_reservacion = id_reservacion
        self.cliente = cliente  #Referencia a Cliente
        self.vehiculo = vehiculo  #Referencia a Vehiculo
        self.fecha_reservacion = datetime.now()
        self.fecha_inicio_prevista = fecha_inicio_prevista
        self.fecha_fin_prevista = fecha_fin_prevista
        self.estado = "PENDIENTE"

class Renta(persistent.Persistent):
    def __init__(self, id_renta, cliente, vehiculo, fecha_inicio, fecha_fin, reservacion=None):
        # Regla 3: La fecha de devolución no puede ser anterior a la fecha de inicio
        if fecha_fin < fecha_inicio:
            raise ValueError("La fecha de devolución no puede ser anterior a la fecha de inicio.")
        
        #Cambia el estado del vehículo utilizando su propio comportamiento
        vehiculo.rentar()

        self.id_renta = id_renta
        self.cliente = cliente  #Referencia directa
        self.vehiculo = vehiculo  #Referencia directa
        self.reservacion = reservacion  #Referencia opcional
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.estado = "ACTIVA"
        self.costo_total = self.calcular_costo()

    def calcular_dias(self):
        dias = (self.fecha_fin - self.fecha_inicio).days
        return dias if dias > 0 else 1

    def calcular_costo(self):
        #Regla 4: Cálculo considerando días de utilización
        return self.calcular_dias() * self.vehiculo.precio_dia

    def finalizar(self, kilometraje_final):
        self.estado = "FINALIZADA"
        self.vehiculo.devolver(kilometraje_final)

class Pago(persistent.Persistent):
    def __init__(self, id_pago, renta, monto, metodo_pago):
        self.id_pago = id_pago
        self.renta = renta  # Referencia a Renta
        self.fecha_pago = datetime.now()
        self.monto = monto
        self.metodo_pago = metodo_pago

class Mantenimiento(persistent.Persistent):
    def __init__(self, id_mantenimiento, vehiculo, fecha_ingreso, tipo_mantenimiento, descripcion, costo):
        self.id_mantenimiento = id_mantenimiento
        self.vehiculo = vehiculo  #Referencia a Vehiculo
        self.fecha_ingreso = fecha_ingreso
        self.fecha_salida = None
        self.tipo_mantenimiento = tipo_mantenimiento
        self.descripcion = descripcion
        self.costo = costo
        
        #Cambia el estado del vehículo automáticamente a mantenimiento
        self.vehiculo.enviar_mantenimiento()

    def finalizar_servicio(self, fecha_salida):
        self.fecha_salida = fecha_salida
        self.vehiculo.estado = "DISPONIBLE"