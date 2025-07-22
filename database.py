# database.py
import sqlite3
from model import Materia, Tarea, TareaDuplicadaError

class DatabaseManager:
    """Maneja la conexión y todas las operaciones con la base de datos."""
    def __init__(self, db_name="agenda_final.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._crear_tablas()

    def _crear_tablas(self):
        """Crea las tablas 'materias' y 'tareas' si no existen."""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS materias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tareas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                fecha TEXT NOT NULL,
                descripcion TEXT,
                materia_id INTEGER,
                FOREIGN KEY (materia_id) REFERENCES materias(id)
            )
        ''')
        self.conn.commit()

    def guardar_materia(self, materia):
        try:
            self.cursor.execute('INSERT INTO materias (nombre) VALUES (?)', (materia.nombre,))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            raise TareaDuplicadaError(f"La materia '{materia.nombre}' ya existe.")

    def obtener_materias(self):
        self.cursor.execute('SELECT id, nombre FROM materias ORDER BY nombre')
        return [Materia(id=row[0], nombre=row[1]) for row in self.cursor.fetchall()]

    def guardar_tarea(self, tarea):
        self.cursor.execute('SELECT id FROM tareas WHERE nombre = ? AND materia_id = ?', (tarea.nombre, tarea.materia.id))
        if self.cursor.fetchone():
            raise TareaDuplicadaError(f"La tarea '{tarea.nombre}' ya existe para esta materia.")
        
        self.cursor.execute(
            'INSERT INTO tareas (nombre, fecha, descripcion, materia_id) VALUES (?, ?, ?, ?)',
            (tarea.nombre, tarea.fecha.strftime('%Y-%m-%d'), tarea.descripcion, tarea.materia.id)
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def obtener_todas_las_tareas(self):
        return self._ejecutar_consulta_tareas('SELECT t.id, t.nombre, t.fecha, t.descripcion, m.id, m.nombre FROM tareas t JOIN materias m ON t.materia_id = m.id ORDER BY t.fecha')

    def obtener_tareas_por_rango(self, fecha_inicio, fecha_fin):
        sql = '''
            SELECT t.id, t.nombre, t.fecha, t.descripcion, m.id, m.nombre
            FROM tareas t JOIN materias m ON t.materia_id = m.id
            WHERE t.fecha BETWEEN ? AND ? ORDER BY t.fecha
        '''
        return self._ejecutar_consulta_tareas(sql, (fecha_inicio.strftime('%Y-%m-%d'), fecha_fin.strftime('%Y-%m-%d')))
    
    def _ejecutar_consulta_tareas(self, sql, params=()):
        """Función auxiliar para no repetir código de consultas de tareas."""
        self.cursor.execute(sql, params)
        tareas = []
        for row in self.cursor.fetchall():
            materia = Materia(id=row[4], nombre=row[5])
            tarea_obj = Tarea(id=row[0], nombre=row[1], fecha=row[2], materia=materia, descripcion=row[3])
            tareas.append(tarea_obj)
        return tareas

    def cerrar(self):
        self.conn.close()