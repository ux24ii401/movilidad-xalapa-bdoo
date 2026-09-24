from gestor_bdoo import GestorBDOO
from modelos import TipoVehiculo, Vehiculo, Cliente, Renta, Pago, Mantenimiento
from datetime import datetime, timedelta

def ejecucion_demostrativa():
    print("-" * 60)
    print(" PASO 1: CREACIÓN DE OBJETOS Y GUARDADO EN ZODB")
    print("-" * 60)

    gestor = GestorBDOO()

    #Creación de Objetos
    sedan = TipoVehiculo("T1", "Sedán Base", "Autos compactos de 4 puertas", 500.0)
    suv = TipoVehiculo("T2", "SUV Familiar", "Camionetas de 3 filas de asientos", 900.0)

    v1 = Vehiculo("V001", "YZA-123-A", "Nissan", "Versa", 2022, sedan, 600.0, 45000)
    v2 = Vehiculo("V002", "XAL-999-B", "Toyota", "RAV4", 2023, suv, 1000.0, 105000)

    c1 = Cliente("C001", "Juan Pérez", "2281002030", "juan@gmail.com", "LIC-98765")

    #Guardar objetos en los contenedores de ZODB
    gestor.root['vehiculos'][v1.id_vehiculo] = v1
    gestor.root['vehiculos'][v2.id_vehiculo] = v2
    gestor.root['clientes'][c1.id_cliente] = c1

    #Crear una Renta activa
    f_inicio = datetime.now()
    f_fin = f_inicio + timedelta(days=3)
    r1 = Renta("R001", c1, v1, f_inicio, f_fin)
    gestor.root['rentas'][r1.id_renta] = r1

    #Registrar el Pago de la renta
    p1 = Pago("P001", r1, r1.costo_total, "EFECTIVO")
    gestor.root['pagos'][p1.id_pago] = p1

    #Guardar los cambios mediante commit
    gestor.guardar()
    print("-> Commit ejecutado exitosamente con transaction.commit()")

    #Cierre explícito de la aplicación y base de datos
    gestor.cerrar()
    print("-> Aplicación cerrada completamente.\n")


    print("-" * 60)
    print(" PASO 2: RECUPERACIÓN DE OBJETOS Y CAMBIO DE ESTADO")
    print("-" * 60)

    #Volver a abrir la base de datos
    gestor_reabierto = GestorBDOO()

    #Recuperar vehículo guardado
    v_recuperado = gestor_reabierto.buscar_vehiculo_por_id("V001")
    print(f"-> Vehículo recuperado: {v_recuperado.marca} {v_recuperado.modelo} | Estado actual: {v_recuperado.estado}")

    #Modificar el estado del objeto mediante la finalización de la renta
    print("\n-- Finalizando renta R001 para modificar estado del objeto --")
    renta_recuperada = gestor_reabierto.root['rentas']['R001']
    renta_recuperada.finalizar(kilometraje_final=45350)

    print(f"-> Estado final de la renta: {renta_recuperada.estado}")
    print(f"-> Nuevo estado del vehículo: {v_recuperado.estado}")
    print(f"-> Nuevo kilometraje del vehículo: {v_recuperado.kilometraje} km")

    #Guardar los cambios de la modificación
    gestor_reabierto.guardar()

    print("\n" + "-" * 60)
    print(" PASO 3: EJECUCIÓN DE CONSULTAS OBLIGATORIAS")
    print("-" * 60)

    print(f"1. Total de vehículos registrados: {len(gestor_reabierto.listar_vehiculos())}")
    print(f"2. Vehículos disponibles: {[v.placas for v in gestor_reabierto.vehiculos_disponibles()]}")
    print(f"3. Rentas activas actuales: {len(gestor_reabierto.rentas_activas())}")
    print(f"4. Ingresos totales acumulados: ${gestor_reabierto.calcular_ingresos():,.2f}")
    print(f"5. Vehículo asignado a R001: {gestor_reabierto.vehiculo_de_renta('R001').placas}")
    print(f"6. Vehículos que requieren mantenimiento: {[v.placas for v in gestor_reabierto.vehiculos_requieren_mantenimiento()]}")
    print(f"7. Ingreso promedio por tipo: {gestor_reabierto.ingreso_promedio_por_tipo()}")

    gestor_reabierto.cerrar()
    print("\n-> Cierre de aplicación completado.")

if __name__ == "__main__":
    ejecucion_demostrativa()