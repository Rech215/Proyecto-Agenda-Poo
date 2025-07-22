# test_agenda.py
import unittest
from unittest.mock import MagicMock
from model import Materia, Tarea, CampoVacioError, TareaDuplicadaError

# Una clase simplificada para probar la interacción con la base de datos
class AgendaController:
    def __init__(self, db_manager):
        self.db = db_manager

    def agregar_tarea(self, nombre, fecha, materia, descripcion=""):
        tarea_obj = Tarea(id=None, nombre=nombre, fecha=fecha, materia=materia, descripcion=descripcion)
        return self.db.guardar_tarea(tarea_obj)

class TestAgenda(unittest.TestCase):
    def setUp(self):
        """Prepara un entorno de prueba limpio antes de cada test."""
        self.mock_db = MagicMock()
        self.controller = AgendaController(self.mock_db)
        self.materia_prog = Materia(id=1, nombre="Programación")

    def test_crear_tarea_exitosa(self):
        """Prueba que una tarea válida llama al método de guardar de la BD."""
        self.mock_db.guardar_tarea.return_value = 1 # Simula que la BD devuelve el ID 1
        
        tarea_id = self.controller.agregar_tarea("API REST", "2025-06-20", self.materia_prog)
        
        self.assertEqual(tarea_id, 1)
        self.mock_db.guardar_tarea.assert_called_once() # Verifica que el método fue llamado

    def test_crear_tarea_nombre_vacio_lanza_error(self):
        """Prueba que el modelo de Tarea no permite un nombre vacío."""
        with self.assertRaises(CampoVacioError):
            Tarea(id=None, nombre="", fecha="2025-06-20", materia=self.materia_prog)

    def test_db_lanza_error_duplicado(self):
        """Prueba que el controlador maneja el error de duplicado de la BD."""
        # Configuramos el mock para que lance un error cuando se le llame
        self.mock_db.guardar_tarea.side_effect = TareaDuplicadaError("La tarea ya existe.")
        
        with self.assertRaises(TareaDuplicadaError):
            self.controller.agregar_tarea("API REST", "2025-06-20", self.materia_prog)

if __name__ == '__main__':
    unittest.main()