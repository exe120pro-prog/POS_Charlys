import customtkinter as ctk
from tkinter import messagebox
from modulos.modulo_seguridad import ModuloSeguridad
from nucleo.gestor_ui import GestorUI # 🔥 Conectado al Gestor Central

class VentanaInventario(ctk.CTkToplevel):
    """
    ========================================================
    📦 MÓDULO DE GESTIÓN DE INVENTARIO
    ========================================================
    Controla el alta, baja y modificación de productos en la base de datos.
    Incluye un buscador en tiempo real y animación de textos largos.
    """
    def __init__(self, padre, db, clave_propietario):
        super().__init__(padre)
        
        self.db = db
        self.clave_propietario = clave_propietario
        self.padre = padre
        
        self.title("📦 Gestión de Inventario - Charlys Cel & PC")
        self.padre.centrar_ventana(self, 900, 580)
        self.configure(fg_color=GestorUI.FONDO)
        
        self.transient(padre)
        self.grab_set()
        self.bind("<Escape>", lambda evento: self.destroy())
        
        self.etiquetas_animadas = []

        frame_izq = ctk.CTkFrame(self, fg_color=GestorUI.PANEL, corner_radius=10, width=320)
        frame_izq.pack(side="left", fill="y", padx=15, pady=15)

        frame_der = ctk.CTkFrame(self, fg_color=GestorUI.PANEL, corner_radius=10)
        frame_der.pack(side="right", fill="both", expand=True, padx=(0, 15), pady=15)

        # 🔤 Cambio de "Arial" a GestorUI.FUENTE_PRINCIPAL en todo el formulario
        ctk.CTkLabel(frame_izq, text="📝 Alta / Modificación", font=(GestorUI.FUENTE_PRINCIPAL, 18, "bold"), text_color=GestorUI.TEXTO).pack(pady=(15, 10))

        ctk.CTkLabel(frame_izq, text="Código de Barras (F1):", font=(GestorUI.FUENTE_PRINCIPAL, 13, "bold"), text_color=GestorUI.TEXTO).pack(anchor="w", padx=20)
        self.entrada_codigo = ctk.CTkEntry(frame_izq, font=(GestorUI.FUENTE_PRINCIPAL, 13))
        self.entrada_codigo.pack(pady=(2, 8), padx=20, fill="x")

        ctk.CTkLabel(frame_izq, text="Nombre del Producto:", font=(GestorUI.FUENTE_PRINCIPAL, 13, "bold"), text_color=GestorUI.TEXTO).pack(anchor="w", padx=20)
        self.entrada_nombre = ctk.CTkEntry(frame_izq, font=(GestorUI.FUENTE_PRINCIPAL, 13))
        self.entrada_nombre.pack(pady=(2, 8), padx=20, fill="x")

        ctk.CTkLabel(frame_izq, text="Precio de Venta ($):", font=(GestorUI.FUENTE_PRINCIPAL, 13, "bold"), text_color=GestorUI.TEXTO).pack(anchor="w", padx=20)
        self.entrada_precio = ctk.CTkEntry(frame_izq, font=(GestorUI.FUENTE_PRINCIPAL, 13))
        self.entrada_precio.pack(pady=(2, 8), padx=20, fill="x")

        ctk.CTkLabel(frame_izq, text="Stock / Existencias:", font=(GestorUI.FUENTE_PRINCIPAL, 13, "bold"), text_color=GestorUI.TEXTO).pack(anchor="w", padx=20)
        self.entrada_stock = ctk.CTkEntry(frame_izq, font=(GestorUI.FUENTE_PRINCIPAL, 13))
        self.entrada_stock.pack(pady=(2, 15), padx=20, fill="x")

        # 🔤 Cambio de fuente en el buscador y encabezados
        ctk.CTkLabel(frame_der, text="📋 Tabla de Inventario de Productos", font=(GestorUI.FUENTE_PRINCIPAL, 18, "bold"), text_color=GestorUI.TEXTO).pack(pady=(15, 5))

        frame_busqueda_inv = ctk.CTkFrame(frame_der, fg_color="transparent")
        frame_busqueda_inv.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(frame_busqueda_inv, text="🔍 Buscar (F1):", font=(GestorUI.FUENTE_PRINCIPAL, 13, "bold"), text_color=GestorUI.TEXTO).pack(side="left", padx=(0, 5))
        self.entrada_buscar_inv = ctk.CTkEntry(frame_busqueda_inv, placeholder_text="Filtrar por nombre o código...", font=(GestorUI.FUENTE_PRINCIPAL, 13))
        self.entrada_buscar_inv.pack(side="left", fill="x", expand=True)

        self.bind("<F1>", self.alternar_casillas_f1)
        self.entrada_codigo.bind("<F1>", self.alternar_casillas_f1)
        self.entrada_nombre.bind("<F1>", self.alternar_casillas_f1)
        self.entrada_precio.bind("<F1>", self.alternar_casillas_f1)
        self.entrada_stock.bind("<F1>", self.alternar_casillas_f1)
        self.entrada_buscar_inv.bind("<F1>", self.alternar_casillas_f1)

        self.entrada_codigo.bind("<Return>", self.verificar_codigo_existente)
        self.entrada_nombre.bind("<Return>", lambda e: self.entrada_precio.focus())
        self.entrada_precio.bind("<Return>", lambda e: self.entrada_stock.focus())
        self.entrada_stock.bind("<Return>", lambda e: self.guardar_producto())
        self.entrada_buscar_inv.bind("<KeyRelease>", self.refrescar_tabla_excel)

        # 🔘 Botones desde la Fábrica
        GestorUI.btn_guardar_inventario(frame_izq, self.guardar_producto).pack(pady=10, padx=20, fill="x")
        GestorUI.btn_limpiar_formulario(frame_izq, self.limpiar_formulario).pack(pady=5, padx=20, fill="x")

        frame_headers_excel = ctk.CTkFrame(frame_der, fg_color=GestorUI.VINO, corner_radius=5)
        frame_headers_excel.pack(fill="x", padx=15, pady=(10, 0))

        ctk.CTkLabel(frame_headers_excel, text="Código", font=(GestorUI.FUENTE_PRINCIPAL, 12, "bold"), text_color="white", width=110, anchor="w").pack(side="left", padx=10, pady=5)
        ctk.CTkLabel(frame_headers_excel, text="Producto", font=(GestorUI.FUENTE_PRINCIPAL, 12, "bold"), text_color="white", anchor="w").pack(side="left", fill="x", expand=True, padx=5, pady=5)
        ctk.CTkLabel(frame_headers_excel, text="Precio", font=(GestorUI.FUENTE_PRINCIPAL, 12, "bold"), text_color="white", width=80, anchor="e").pack(side="left", padx=5, pady=5)
        ctk.CTkLabel(frame_headers_excel, text="Existencias", font=(GestorUI.FUENTE_PRINCIPAL, 12, "bold"), text_color="white", width=90, anchor="e").pack(side="left", padx=10, pady=5)

        self.caja_tabla_excel = ctk.CTkScrollableFrame(frame_der, fg_color="white", corner_radius=5)
        self.caja_tabla_excel.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.refrescar_tabla_excel()
        self.entrada_codigo.focus()

    def alternar_casillas_f1(self, evento=None):
        foco_actual = self.focus_get()
        if foco_actual == self.entrada_buscar_inv._entry:
            self.entrada_codigo.focus()
        else:
            self.entrada_buscar_inv.focus()
        return "break"

    def cargar_para_edicion(self, codigo, nombre, precio, stock):
        self.entrada_codigo.delete(0, "end")
        self.entrada_codigo.insert(0, str(codigo))
        self.entrada_nombre.delete(0, "end")
        self.entrada_nombre.insert(0, str(nombre))
        self.entrada_precio.delete(0, "end")
        self.entrada_precio.insert(0, str(precio))
        self.entrada_stock.delete(0, "end")
        self.entrada_stock.insert(0, str(stock))

    def verificar_codigo_existente(self, evento=None):
        codigo = self.entrada_codigo.get().strip()
        if not codigo: return
        producto = self.db.buscar_producto(codigo)
        if producto:
            self.cargar_para_edicion(producto[0], producto[1], producto[2], producto[3])
        else:
            self.entrada_nombre.focus()

    def guardar_producto(self):
        codigo = self.entrada_codigo.get().strip()
        nombre = self.entrada_nombre.get().strip()
        precio_raw = self.entrada_precio.get().strip()
        stock_raw = self.entrada_stock.get().strip()

        faltantes = []
        if not codigo: faltantes.append("• Código de Barras")
        if not nombre: faltantes.append("• Nombre del Producto")
        if not precio_raw: faltantes.append("• Precio")
        if not stock_raw: faltantes.append("• Stock / Existencias")

        if faltantes:
            messagebox.showwarning("Campos Incompletos", "Por favor llena:\n" + "\n".join(faltantes), parent=self)
            return

        try:
            precio = float(precio_raw)
            stock = int(stock_raw)
        except ValueError:
            messagebox.showerror("Error de Formato", "El precio debe ser un número (ej. 15.50) y el Stock un entero.", parent=self)
            return

        existente = self.db.buscar_producto(codigo)
        if existente:
            self.db.actualizar_producto(codigo, nombre, precio, stock)
            messagebox.showinfo("Actualizado", f"¡Producto '{nombre}' actualizado correctamente!", parent=self)
        else:
            self.db.agregar_producto(codigo, nombre, precio, stock)
            messagebox.showinfo("Guardado", f"¡Producto '{nombre}' registrado correctamente!", parent=self)

        self.limpiar_formulario()
        self.refrescar_tabla_excel()

    def limpiar_formulario(self):
        self.entrada_codigo.delete(0, "end")
        self.entrada_nombre.delete(0, "end")
        self.entrada_precio.delete(0, "end")
        self.entrada_stock.delete(0, "end")
        self.entrada_codigo.focus()

    def borrar_del_inventario(self, codigo, nombre):
        def accion_borrar():
            respuesta = messagebox.askyesno(
                "Confirmar Eliminación", 
                f"⚠️ ATENCIÓN ⚠️\n\n¿Estás seguro de que deseas borrar PERMANENTEMENTE el producto:\n\n'{nombre}'\n\ndel inventario?", 
                parent=self
            )
            if respuesta:
                self.db.eliminar_producto(codigo)
                messagebox.showinfo("Eliminado", f"El producto '{nombre}' ha sido eliminado del sistema.", parent=self)
                self.limpiar_formulario()
                self.refrescar_tabla_excel()
                
        ModuloSeguridad.solicitar_clave(
            ventana_actual=self, 
            ventana_principal=self.padre, 
            titulo="🔒 Autorización de Propietario", 
            mensaje="Clave de Propietario:", 
            clave_correcta=self.clave_propietario, 
            callback_exito=accion_borrar
        )

    def refrescar_tabla_excel(self, evento=None):
        for widget in self.caja_tabla_excel.winfo_children():
            widget.destroy()
            
        self.etiquetas_animadas = []

        filtro = self.entrada_buscar_inv.get().strip()
        productos = self.db.obtener_todos_los_productos(filtro)

        if not productos:
            ctk.CTkLabel(self.caja_tabla_excel, text="No hay productos registrados.", font=(GestorUI.FUENTE_PRINCIPAL, 13, "italic"), text_color="gray").pack(pady=20)
            return

        for prod in productos:
            cod, nom, pre, stc = prod
            
            fila = ctk.CTkFrame(self.caja_tabla_excel, fg_color="transparent")
            fila.pack(fill="x", pady=2)

            color_stock = "#D90429" if stc <= 1 else GestorUI.TEXTO

            ctk.CTkLabel(fila, text=cod, font=(GestorUI.FUENTE_PRINCIPAL, 12), text_color=GestorUI.TEXTO, width=110, anchor="w").pack(side="left", padx=10)
            
            # 🔘 Botones desde la Fábrica
            GestorUI.btn_icono_borrar(fila, lambda c=cod, n=nom: self.borrar_del_inventario(c, n)).pack(side="right", padx=5)
            GestorUI.btn_icono_editar(fila, lambda c=cod, n=nom, p=pre, s=stc: self.cargar_para_edicion(c, n, p, s)).pack(side="right", padx=5)

            ctk.CTkLabel(fila, text=f"{stc} pzs", font=(GestorUI.FUENTE_PRINCIPAL, 12, "bold"), text_color=color_stock, width=90, anchor="e").pack(side="right", padx=10)
            ctk.CTkLabel(fila, text=f"${pre:.2f}", font=(GestorUI.FUENTE_PRINCIPAL, 12), text_color=GestorUI.TEXTO, width=80, anchor="e").pack(side="right", padx=5)

            lbl_nombre_inv = ctk.CTkLabel(fila, font=(GestorUI.FUENTE_PRINCIPAL, 12), text_color=GestorUI.TEXTO, anchor="w")
            lbl_nombre_inv.pack(side="left", fill="x", expand=True, padx=5)
            
            if len(nom) > 35:
                texto_marquee = f"{nom}   •   "
                lbl_nombre_inv.configure(text=texto_marquee[:35])
                self.etiquetas_animadas.append({'label': lbl_nombre_inv, 'text': texto_marquee, 'index': 0, 'limit': 35, 'pausa': 17})
            else:
                lbl_nombre_inv.configure(text=nom)

            separador = ctk.CTkFrame(self.caja_tabla_excel, height=1, fg_color="#E0E0E0")
            separador.pack(fill="x", padx=5, pady=2)
            
        if self.etiquetas_animadas:
            self.padre.animar_textos_marquesina(self.etiquetas_animadas, None)