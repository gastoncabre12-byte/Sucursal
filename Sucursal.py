
from enum import Enum
from datetime import date, datetime


class Estado_vehiculo(Enum):
    Disponible = "disponible"
    Reservado = "reservado"
    En_Alquiler = "en_alquiler"
    Fuera_de_Servicio = "fuera_de_servicio"


class Estado_reserva(Enum):
    Solicitada = "solicitada"
    Confirmada = "confirmada"
    En_Curso = "en_curso"
    Finalizada = "finalizada"
    Cancelada = "cancelada"

class cliente:
    def __init__(self, nombre, apellido, dni, telefono, correo_electronico):
        self.__nombre = nombre
        self.__apellido = apellido
        self.__dni = dni
        self.__telefono = telefono
        self.__correo_electronico = correo_electronico
        self.reservas: list = []

    @property
    def nombre(self):
        return self.__nombre

    @property
    def apellido(self):
        return self.__apellido

    @property
    def correo_electronico(self):
        return self.__correo_electronico

    def __repr__(self):
        return (f"Cliente({self.__nombre} {self.__apellido} "
                f"DNI:{self.__dni} Tel:{self.__telefono} "
                f"Mail:{self.__correo_electronico})")


class vehiculo:
    FACTOR_TARIFA = 1.0

    def __init__(self, patente, marca, modelo, tarifa_base,
                 estado=Estado_vehiculo.Disponible):
        if tarifa_base <= 0:
            raise TarifaInvalidaError(
                f"La tarifa base debe ser > 0, se recibió {tarifa_base}")
        self.__patente = patente
        self.__marca = marca
        self.__modelo = modelo
        self.__tarifa_base = tarifa_base
        self.__estado = estado

    @property
    def patente(self):
        return self.__patente

    @property
    def marca(self):
        return self.__marca

    @property
    def modelo(self):
        return self.__modelo

    @property
    def tarifa_base(self):
        return self.__tarifa_base

    @property
    def estado(self):
        return self.__estado

    @estado.setter
    def estado(self, nuevo):
        self.__estado = nuevo

    def costo(self, dias: int) -> float:
        costo = self.__tarifa_base * self.FACTOR_TARIFA * dias
        if costo < 0:
            raise CostoNegativoError("El costo no puede ser negativo.")
        return costo

    def __repr__(self):
        return (f"{self.__class__.__name__}({self.__patente}, "
                f"{self.__marca} {self.__modelo}, "
                f"${self.__tarifa_base}/día, {self.__estado.value})")

class auto(vehiculo):
    FACTOR_TARIFA = 1.0       # tarifa base


class camioneta(vehiculo):
    FACTOR_TARIFA = 1.20      # +20 %


class moto(vehiculo):
    FACTOR_TARIFA = 0.85      # -15 %

class registro_historial:
    def __init__(self, estado: Estado_reserva, descripcion: str):
        self.fecha = datetime.now().date()
        self.hora = datetime.now().time()
        self.estado = estado
        self.descripcion = descripcion

    def __repr__(self):
        return (f"[{self.fecha} {self.hora}] "
                f"{self.estado.value} - {self.descripcion}")


class servicio_notificaciones:
    def notificar(self, cliente, mensaje):
        print(f"A {cliente.nombre} {cliente.apellido} "
              f"({cliente.correo_electronico}): {mensaje}")

class reserva:
    _contador = 0

    def __init__(self, nro_identificador, cliente, vehiculo_seleccionado,
                 fecha_inicio: date, fecha_finalizada: date,
                 notificador: servicio_notificaciones):
        if fecha_finalizada <= fecha_inicio:
            raise FechaInvalidaError(
                "La fecha de finalización debe ser posterior a la de inicio.")

        reserva._contador += 1
        self.__nro_identificador = nro_identificador
        self.__cliente = cliente
        self.__vehiculo = vehiculo_seleccionado
        self.__fecha_inicio = fecha_inicio
        self.__fecha_finalizada = fecha_finalizada
        self.__notificador = notificador
        self.__historial: list = []
        self.__estado = Estado_reserva.Solicitada

        self.__historial.append(
            registro_historial(Estado_reserva.Solicitada, "Reserva creada"))


    @property
    def nro_identificador(self):
        return self.__nro_identificador

    @property
    def estado(self):
        return self.__estado

    @property
    def historial(self):
        return list(self.__historial)

    @property
    def vehiculo(self):
        return self.__vehiculo

    @property
    def cliente(self):
        return self.__cliente

    def cambiar_estado(self, nuevo_estado: Estado_reserva,
                       descripcion: str = ""):

        if (self.__estado == Estado_reserva.Solicitada
                and nuevo_estado == Estado_reserva.Finalizada):
            raise TransicionInvalidaError(
                "SOLICITADA no puede pasar directamente a FINALIZADA.")

        self.__estado = nuevo_estado
        self.__historial.append(
            registro_historial(nuevo_estado, descripcion))


    def calcular_costo(self) -> float:
        dias = (self.__fecha_finalizada - self.__fecha_inicio).days
        return self.__vehiculo.costo(dias)

    def __repr__(self):
        return (f"Reserva #{self.__nro_identificador} "
                f"[{self.__estado.value}] "
                f"{self.__vehiculo.patente} "
                f"{self.__fecha_inicio}→{self.__fecha_finalizada}")


if __name__ == "__main__":
    notificador = servicio_notificaciones()

    a1 = auto("ABC123", "Volkswagen", "Gol", 15000)
    c1 = camioneta("XYZ789", "Toyota", "Hilux", 25000)
    m1 = moto("MOT001", "Yamaha", "MT-07", 8000)

    cli = cliente("Juan", "Pérez", 30123456,
                  "11-5555-0000", "juan.perez@mail.com")

    r1 = reserva(1, cli, a1, date(2026, 9, 25),
                 date(2026, 9, 28), notificador)
    cli.reservas.append(r1)

    r2 = reserva(2, cli, c1, date(2026, 10, 1),
                 date(2026, 10, 5), notificador)
    cli.reservas.append(r2)

    r1.cambiar_estado(Estado_reserva.Confirmada, "Vehículo confirmado")

    print(f"\nCosto auto (3 días):       ${a1.costo(3):,.0f}")
    print(f"Costo camioneta (4 días):  ${c1.costo(4):,.0f}")
    print(f"Costo moto (2 días):       ${m1.costo(2):,.0f}")

    # Costo por reserva
    print(f"\nReserva #{r1.nro_identificador} costo total: "
          f"${r1.calcular_costo():,.0f}")

    # Historial
    print(f"\nHistorial Reserva #{r1.nro_identificador}:")
    for reg in r1.historial:
        print(f"  {reg}")   