import sqlite3
from datetime import datetime
import os

class BaseDatos:
    """
    ========================================================
    🗄️ GESTOR DE BASE DE DATOS (SQLite)
    ========================================================
    Maneja toda la interacción con inventario_charlys.db.
    Consultas, inserciones, actualizaciones y migraciones de tablas.
    """
    
    def __init__(self):
        # 🔥 MAGIA DE RUTAS ABSOLUTAS Y PROTECCIÓN DE CARPETA 🔥
        ruta_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        carpeta_datos = os.path.join(ruta_base, "datos")
        
        # Si no existe la carpeta 'datos', la creamos para evitar errores críticos
        os.makedirs(carpeta_datos, exist_ok=True)
        
        ruta_db = os.path.join(carpeta_datos, "inventario_charlys.db")
        
        self.conexion = sqlite3.connect(ruta_db)
        self.cursor = self.conexion.cursor()
        self.crear_tablas()

    def cerrar_conexion(self):
        """Cierra la conexión a la base de datos de forma segura para evitar bloqueos en Windows."""
        try:
            self.conexion.close()
        except Exception as e:
            print(f"⚠️ Error al cerrar la base de datos: {e}")

    def crear_tablas(self):
        """Crea las tablas iniciales y aplica parches/actualizaciones si faltan columnas."""
        
        # 1. Tabla de Productos
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                codigo_barras TEXT PRIMARY KEY,
                nombre TEXT NOT NULL,
                precio REAL NOT NULL,
                stock INTEGER NOT NULL DEFAULT 0
            )
        ''')
        
        # Parche: Agregar stock si la tabla es de una versión anterior
        try:
            self.cursor.execute("ALTER TABLE productos ADD COLUMN stock INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass 
        
        # 2. Tabla de Ventas
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                total REAL NOT NULL
            )
        ''')

        # 3. Tabla de Configuración de Ticket
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS configuracion_ticket (
                id INTEGER PRIMARY KEY DEFAULT 1,
                nombre TEXT,
                direccion TEXT,
                telefono TEXT,
                despedida TEXT,
                tamano TEXT,
                negritas INTEGER,
                logo INTEGER,
                qr INTEGER
            )
        ''')
        
        # Parches de actualización para el ticket (Escala, Espacio, Impresora y Calidad)
        try: self.cursor.execute("ALTER TABLE configuracion_ticket ADD COLUMN escala_qr INTEGER DEFAULT 6")
        except sqlite3.OperationalError: pass 
            
        try: self.cursor.execute("ALTER TABLE configuracion_ticket ADD COLUMN espacio_qr INTEGER DEFAULT 15")
        except sqlite3.OperationalError: pass 

        try: self.cursor.execute("ALTER TABLE configuracion_ticket ADD COLUMN impresora_nombre TEXT DEFAULT 'Seleccionar'")
        except sqlite3.OperationalError: pass 
            
        try: self.cursor.execute("ALTER TABLE configuracion_ticket ADD COLUMN calidad_impresora TEXT DEFAULT 'Modo de (Ahorro de energía)'")
        except sqlite3.OperationalError: pass 
        
        # Insertar configuración por defecto si la tabla está vacía
        self.cursor.execute("SELECT COUNT(*) FROM configuracion_ticket")
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute('''
                INSERT INTO configuracion_ticket (id, nombre, direccion, telefono, despedida, tamano, negritas, logo, qr, escala_qr, espacio_qr, impresora_nombre, calidad_impresora)
                VALUES (1, 'CHARLYS CEL & PC', 'Plaza Principal Loc. 5', 'Tel: 555-123-4567', '¡Gracias por su compra!', 'Tamaño A (Normal)', 0, 0, 0, 6, 15, 'Seleccionar', 'Modo de (Ahorro de energía)')
            ''')

        self.conexion.commit()

    # ==========================================
    # 📦 MÉTODOS DE INVENTARIO
    # ==========================================
    def agregar_producto(self, codigo, nombre, precio, stock):
        try:
            self.cursor.execute("INSERT INTO productos VALUES (?, ?, ?, ?)", (codigo, nombre, precio, stock))
            self.conexion.commit()
            return True 
        except sqlite3.IntegrityError:
            return False # El código de barras ya existe

    def actualizar_producto(self, codigo, nombre, precio, stock):
        self.cursor.execute('''
            UPDATE productos 
            SET nombre = ?, precio = ?, stock = ? 
            WHERE codigo_barras = ?
        ''', (nombre, precio, stock, codigo))
        self.conexion.commit()

    def eliminar_producto(self, codigo):
        self.cursor.execute("DELETE FROM productos WHERE codigo_barras = ?", (codigo,))
        self.conexion.commit()

    def buscar_producto(self, codigo):
        """Busca un producto por su código exacto. Retorna una tupla o None."""
        self.cursor.execute("SELECT codigo_barras, nombre, precio, stock FROM productos WHERE codigo_barras = ?", (codigo,))
        return self.cursor.fetchone()

    def buscar_productos_por_nombre(self, keyword):
        """Buscador inteligente con LIKE (limitado a 10 resultados para no saturar la UI)."""
        self.cursor.execute('''
            SELECT codigo_barras, nombre, precio, stock 
            FROM productos 
            WHERE nombre LIKE ? OR codigo_barras LIKE ? 
            ORDER BY nombre ASC LIMIT 10
        ''', (f"%{keyword}%", f"%{keyword}%"))
        return self.cursor.fetchall()

    def obtener_todos_los_productos(self, filtro=""):
        """Obtiene todo el inventario, opcionalmente filtrado por un texto."""
        if filtro:
            query = "SELECT codigo_barras, nombre, precio, stock FROM productos WHERE nombre LIKE ? OR codigo_barras LIKE ? ORDER BY nombre ASC"
            self.cursor.execute(query, (f"%{filtro}%", f"%{filtro}%"))
        else:
            self.cursor.execute("SELECT codigo_barras, nombre, precio, stock FROM productos ORDER BY nombre ASC")
        return self.cursor.fetchall()

    def descontar_stock(self, codigo, cantidad):
        self.cursor.execute("UPDATE productos SET stock = stock - ? WHERE codigo_barras = ?", (cantidad, codigo))
        self.conexion.commit()

    # ==========================================
    # 💰 MÉTODOS DE VENTAS
    # ==========================================
    def registrar_venta(self, total):
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("INSERT INTO ventas (fecha, total) VALUES (?, ?)", (fecha_actual, total))
        self.conexion.commit()
        return True

    def obtener_ventas_del_dia(self, fecha_buscada):
        """Busca las ventas de una fecha específica y retorna (cantidad_ventas, total_dinero)"""
        self.cursor.execute("SELECT total FROM ventas WHERE fecha LIKE ?", (f"{fecha_buscada}%",))
        ventas = self.cursor.fetchall()
        total_dia = sum(venta[0] for venta in ventas)
        cantidad_ventas = len(ventas)
        return cantidad_ventas, total_dia

    # ==========================================
    # 🎨 MÉTODOS DE CONFIGURACIÓN DEL TICKET
    # ==========================================
    def obtener_config_ticket(self):
        self.cursor.execute("SELECT * FROM configuracion_ticket WHERE id = 1")
        return self.cursor.fetchone()

    def actualizar_config_ticket(self, nombre, direccion, telefono, despedida, tamano, negritas, logo, qr, escala_qr=6, espacio_qr=15, impresora_nombre='Seleccionar', calidad_impresora='Modo de (Ahorro de energía)'):
        self.cursor.execute('''
            UPDATE configuracion_ticket 
            SET nombre=?, direccion=?, telefono=?, despedida=?, tamano=?, negritas=?, logo=?, qr=?, escala_qr=?, espacio_qr=?, impresora_nombre=?, calidad_impresora=? 
            WHERE id=1
        ''', (nombre, direccion, telefono, despedida, tamano, negritas, logo, qr, escala_qr, espacio_qr, impresora_nombre, calidad_impresora))
        self.conexion.commit()