# model.py
from datetime import datetime

# --- Requisito: Excepciones Personalizadas ---
class AppError(Exception):
    """Clase base para todos los errores de la aplicación."""
    pass

class CampoVacioError(AppError):
    """Se lanza cuando un campo obligatorio está vacío."""
    pass

class FechaInvalidaError(AppError):
    """Se lanza cuando el formato de la fecha es incorrecto."""
    pass

class TareaDuplicadaError(AppError):
    """Se lanza al intentar agregar una tarea o materia que ya existe."""
    pass

# --- Requisito: Herencia y Composición ---

# Clase "Padre" para Herencia
class EntradaAgenda:
    """Clase base para cualquier evento con nombre y fecha."""
    def __init__(self, id, nombre, fecha):
        if not nombre or not fecha:
            raise CampoVacioError("El nombre y la fecha son obligatorios.")
        try:
            self.fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
        except ValueError:
            raise FechaInvalidaError("El formato de la fecha debe ser YYYY-MM-DD.")
        self.id = id
        self.nombre = nombre

class Materia:
    """Representa una materia académica."""
    def __init__(self, id, nombre):
        if not nombre:
            raise CampoVacioError("El nombre de la materia no puede estar vacío.")
        self.id = id
        self.nombre = nombre

    def __str__(self):
        return self.nombre

# Clase "Hija" que usa Herencia y Composición
class Tarea(EntradaAgenda):
    """
    Representa una tarea específica.
    - HEREDA de EntradaAgenda (es un tipo de entrada).
    - TIENE UNA Materia (Composición).
    """
    def __init__(self, id, nombre, fecha, materia, descripcion=""):
        super().__init__(id, nombre, fecha)  # Llama al constructor de la clase padre
        self.materia = materia  # Composición
        self.descripcion = descripcion

    def __str__(self):
        return f"Tarea: '{self.nombre}' de '{self.materia.nombre}' para {self.fecha}"