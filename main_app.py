# main_app.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, timedelta

from model import *
from database import DatabaseManager

class App(tk.Tk):
    """Clase principal que gestiona la ventana y las vistas."""
    def __init__(self):
        super().__init__()
        self.title("Agenda Académica Inteligente")
        self.geometry("900x600")

        self.db = DatabaseManager()

        # --- Requisito: Barra de Navegación ---
        nav_frame = tk.Frame(self, bg="#f0f0f0", bd=1, relief=tk.RAISED)
        nav_frame.pack(side="top", fill="x")

        tk.Button(nav_frame, text="Ver Tareas", command=lambda: self.show_frame("TareasView")).pack(side="left", padx=5, pady=5)
        tk.Button(nav_frame, text="Añadir Contenido", command=lambda: self.show_frame("AddView")).pack(side="left", padx=5, pady=5)
        tk.Button(nav_frame, text="Reportes", command=lambda: self.show_frame("ReportesView")).pack(side="left", padx=5, pady=5)
        
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (TareasView, AddView, ReportesView):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("TareasView")
        self.after(500, self._verificar_recordatorios)

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        if hasattr(frame, "actualizar"):
            frame.actualizar()
        frame.tkraise()

    def _verificar_recordatorios(self):
        """Requisito: Recordatorios automáticos."""
        hoy, fin = date.today(), date.today() + timedelta(days=7)
        tareas_proximas = self.db.obtener_tareas_por_rango(hoy, fin)
        if tareas_proximas:
            mensaje = "Tareas para los próximos 7 días:\n\n" + "\n".join([f"- {t.nombre} ({t.materia.nombre}) vence el {t.fecha}" for t in tareas_proximas])
            messagebox.showinfo("Recordatorio", mensaje)

class TareasView(tk.Frame):
    """Vista para mostrar y buscar tareas."""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # --- Búsqueda ---
        search_frame = tk.Frame(self)
        search_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(search_frame, text="Buscar:").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self._filtrar)
        tk.Entry(search_frame, textvariable=self.search_var).pack(fill="x", expand=True, side="left", padx=5)

        # --- Tabla de Tareas ---
        cols = ("Materia", "Fecha Entrega", "Descripción")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for col in cols: self.tree.heading(col, text=col)
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)
    
    def actualizar(self):
        self._todas_las_tareas = self.controller.db.obtener_todas_las_tareas()
        self._mostrar_en_tabla(self._todas_las_tareas)

    def _filtrar(self, *args):
        keyword = self.search_var.get().lower()
        if not keyword:
            filtradas = self._todas_las_tareas
        else:
            filtradas = [t for t in self._todas_las_tareas if keyword in t.nombre.lower() or keyword in t.materia.nombre.lower()]
        self._mostrar_en_tabla(filtradas)

    def _mostrar_en_tabla(self, tareas):
        self.tree.delete(*self.tree.get_children())
        for tarea in tareas: self.tree.insert("", "end", values=(tarea.materia.nombre, tarea.fecha, tarea.descripcion))

class AddView(tk.Frame):
    """Vista para añadir materias y tareas."""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        # ... (El código de los formularios es largo, se pega a continuación)
        self._crear_widgets()

    def _crear_widgets(self):
        # --- Formulario Materia ---
        materia_frame = ttk.LabelFrame(self, text="Añadir Nueva Materia", padding=10)
        materia_frame.pack(fill="x", padx=10, pady=10)
        tk.Label(materia_frame, text="Nombre:").grid(row=0, column=0, padx=5, pady=5)
        self.materia_nombre = tk.Entry(materia_frame, width=40)
        self.materia_nombre.grid(row=0, column=1, sticky="ew", padx=5)
        tk.Button(materia_frame, text="Guardar Materia", command=self._guardar_materia).grid(row=0, column=2, padx=10)

        # --- Formulario Tarea ---
        tarea_frame = ttk.LabelFrame(self, text="Añadir Nueva Tarea", padding=10)
        tarea_frame.pack(fill="x", padx=10, pady=10, expand=True)
        
        tk.Label(tarea_frame, text="Nombre:").grid(row=0, column=0, sticky="w", pady=2)
        self.tarea_nombre = tk.Entry(tarea_frame)
        self.tarea_nombre.grid(row=0, column=1, sticky="ew", pady=2, columnspan=2)

        tk.Label(tarea_frame, text="Fecha (YYYY-MM-DD):").grid(row=1, column=0, sticky="w", pady=2)
        self.tarea_fecha = tk.Entry(tarea_frame)
        self.tarea_fecha.grid(row=1, column=1, sticky="ew", pady=2, columnspan=2)

        tk.Label(tarea_frame, text="Descripción:").grid(row=2, column=0, sticky="w", pady=2)
        self.tarea_desc = tk.Entry(tarea_frame)
        self.tarea_desc.grid(row=2, column=1, sticky="ew", pady=2, columnspan=2)

        tk.Label(tarea_frame, text="Materia:").grid(row=3, column=0, sticky="w", pady=2)
        self.materia_var = tk.StringVar()
        self.materia_menu = ttk.Combobox(tarea_frame, textvariable=self.materia_var, state="readonly")
        self.materia_menu.grid(row=3, column=1, sticky="ew", pady=2)
        
        tk.Button(tarea_frame, text="Guardar Tarea", command=self._guardar_tarea).grid(row=4, columnspan=3, pady=10)
    
    def actualizar(self):
        self._materias = self.controller.db.obtener_materias()
        self.materia_menu['values'] = [m.nombre for m in self._materias]
        if self._materias: self.materia_menu.current(0)

    def _guardar_materia(self):
        try:
            materia = Materia(id=None, nombre=self.materia_nombre.get())
            self.controller.db.guardar_materia(materia)
            messagebox.showinfo("Éxito", "Materia guardada.")
            self.materia_nombre.delete(0, 'end')
            self.actualizar()
        except AppError as e: messagebox.showerror("Error", str(e))

    def _guardar_tarea(self):
        try:
            materia_sel = next((m for m in self._materias if m.nombre == self.materia_var.get()), None)
            if not materia_sel: raise CampoVacioError("Debes seleccionar una materia.")
            
            tarea = Tarea(id=None, nombre=self.tarea_nombre.get(), fecha=self.tarea_fecha.get(), materia=materia_sel, descripcion=self.tarea_desc.get())
            self.controller.db.guardar_tarea(tarea)
            messagebox.showinfo("Éxito", "Tarea guardada.")
            for entry in [self.tarea_nombre, self.tarea_fecha, self.tarea_desc]: entry.delete(0, 'end')
        except AppError as e: messagebox.showerror("Error", str(e))

class ReportesView(tk.Frame):
    """Vista para generar reportes."""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Tareas de esta Semana", command=self._reporte_semanal).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Tareas de este Mes", command=self._reporte_mensual).pack(side="left", padx=10)

        self.reporte_texto = tk.Text(self, height=20, width=80, font=("Courier New", 10), wrap="word", state="disabled")
        self.reporte_texto.pack(pady=10, padx=10, fill="both", expand=True)

    def _reporte_semanal(self):
        hoy = date.today()
        inicio = hoy - timedelta(days=hoy.weekday())
        fin = inicio + timedelta(days=6)
        self._generar_reporte(f"Reporte Semanal ({inicio} al {fin})", inicio, fin)

    def _reporte_mensual(self):
        hoy = date.today()
        inicio = hoy.replace(day=1)
        fin = (inicio.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        self._generar_reporte(f"Reporte Mensual ({hoy.strftime('%B %Y')})", inicio, fin)

    def _generar_reporte(self, titulo, inicio, fin):
        tareas = self.controller.db.obtener_tareas_por_rango(inicio, fin)
        self.reporte_texto.config(state="normal")
        self.reporte_texto.delete('1.0', tk.END)
        self.reporte_texto.insert(tk.END, f"--- {titulo} ---\n\n")
        if not tareas:
            self.reporte_texto.insert(tk.END, "No hay tareas programadas para este período.")
        else:
            for tarea in tareas: self.reporte_texto.insert(tk.END, f"{tarea.fecha} - [{tarea.materia.nombre.upper():<15}] - {tarea.nombre}\n")
        self.reporte_texto.config(state="disabled")

    def actualizar(self):
        self.reporte_texto.config(state="normal")
        self.reporte_texto.delete('1.0', tk.END)
        self.reporte_texto.config(state="disabled")

if __name__ == "__main__":
    app = App()
    app.mainloop()