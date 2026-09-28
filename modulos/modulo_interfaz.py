import customtkinter as ctk
from tkinter import messagebox
from nucleo.base_datos import BaseDatos
from nucleo.hardware import HardwarePOS 
from datetime import datetime

# 🌟 NUESTROS MÓDULOS DE ARQUITECTURA 🌟
from modulos.editor_ticket import EditorTicket 
from modulos.modulo_inventario import VentanaInventario
from modulos.modulo_cobro import VentanaCobro
from modulos.modulo_seguridad import ModuloSeguridad
from nucleo.credenciales import Credenciales 

# 🎨 NUESTRO GESTOR CENTRAL DE INTERFAZ 🎨
from nucleo.gestor_ui import GestorUI

class VentanaPrincipal(ctk.CTk):
    """
    ========================================================
    🖥️ MÓDULO PRINCIPAL (DIRECTOR DE ORQUESTA)
    ========================================================
    Es el núcleo gráfico del programa. Administra el escáner, 
    el carrito de compras y delega las tareas complejas a 
    los demás módulos (Inventario, Cobro, Hardware, etc.)
    """
    def __init__(self):
        super().__init__()
        
        self.db = BaseDatos()
        self.hardware = HardwarePOS()  
        self.total_venta = 0.0  
        self.carrito_compras = {} 
        
        ctk.set_appearance_mode("light")  
        self.configure(fg_color=GestorUI.FONDO) # 🎨 Leemos el color desde el Gestor Central
        self.title("POS Charlys - Cel & PC")
        
        self.centrar_ventana(self, 1000, 700)
        
        # --- ATAJOS DE TECLADO ---
        self.bind("<F12>", self.procesar_cobro)
        self.bind("<F1>", self.enfocar_buscador) 
        self.bind("<F2>", self.abrir_ventana_inventario) 
        self.bind("<F3>", self.solicitar_clave_eliminacion) 
        self.bind("<F4>", self.mostrar_corte_caja)
        self.bind("<F5>", self.solicitar_clave_editor) 

        # --- ÁREAS DE LA PANTALLA ---
        # 🔤 Cambio de fuente a GestorUI.FUENTE_PRINCIPAL
        self.titulo = ctk.CTkLabel(self, text="Caja Registradora - Charlys Cel & PC", font=(GestorUI.FUENTE_PRINCIPAL, 28, "bold"), text_color=GestorUI.TEXTO)
        self.titulo.pack(pady=20)

        self.frame_central = ctk.CTkFrame(self, fg_color=GestorUI.FONDO)
        self.frame_central.pack(fill="both", expand=True, padx=20, pady=10)

        # PANEL IZQUIERDO: Buscador y Carrito
        self.frame_izquierdo = ctk.CTkFrame(self.frame_central, fg_color=GestorUI.PANEL, corner_radius=10)
        self.frame_izquierdo.pack(side="left", fill="both", expand=True, padx=10)

        self.label_buscador = ctk.CTkLabel(self.frame_izquierdo, text="🔍 Escanea o busca un producto (F1):", font=(GestorUI.FUENTE_PRINCIPAL, 16, "bold"), text_color=GestorUI.TEXTO)
        self.label_buscador.pack(pady=(20, 5), padx=20, anchor="w")

        self.sugerencias_actuales = []
        self.botones_sugerencias = []
        self.indice_sugerencia_seleccionada = -1
        self.etiquetas_animadas = []
        self.animacion_activa = False

        self.entrada_buscador = ctk.CTkEntry(self.frame_izquierdo, placeholder_text="Código de barras o nombre...", font=(GestorUI.FUENTE_PRINCIPAL, 18), height=40)
        self.entrada_buscador.pack(pady=5, padx=20, fill="x")
        
        self.entrada_buscador.bind("<Return>", self.escanear_producto)
        self.entrada_buscador.bind("<KeyRelease>", self.mostrar_sugerencias)
        self.entrada_buscador.bind("<FocusOut>", self.ocultar_sugerencias_con_retraso)
        self.entrada_buscador.bind("<Up>", self.navegar_sugerencias)
        self.entrada_buscador.bind("<Down>", self.navegar_sugerencias)

        self.frame_sugerencias = ctk.CTkScrollableFrame(self.frame_izquierdo, fg_color="white", corner_radius=5, border_width=1, border_color="#CCCCCC")

        self.label_carrito = ctk.CTkLabel(self.frame_izquierdo, text="🛒 Carrito de Compras", font=(GestorUI.FUENTE_PRINCIPAL, 16, "bold"), text_color=GestorUI.TEXTO)
        self.label_carrito.pack(pady=(15, 5), padx=20, anchor="w")

        self.frame_encabezados = ctk.CTkFrame(self.frame_izquierdo, fg_color=GestorUI.VINO, corner_radius=5)
        self.frame_encabezados.pack(fill="x", padx=20, pady=(5, 0))

        ctk.CTkLabel(self.frame_encabezados, text="Cant.", font=(GestorUI.FUENTE_PRINCIPAL, 14, "bold"), text_color="white", width=60).pack(side="left", padx=5, pady=5)
        ctk.CTkLabel(self.frame_encabezados, text="Producto", font=(GestorUI.FUENTE_PRINCIPAL, 14, "bold"), text_color="white", anchor="w").pack(side="left", fill="x", expand=True, padx=5, pady=5)
        ctk.CTkLabel(self.frame_encabezados, text="Precio", font=(GestorUI.FUENTE_PRINCIPAL, 14, "bold"), text_color="white", width=100, anchor="e").pack(side="left", padx=5, pady=5)
        ctk.CTkLabel(self.frame_encabezados, text="Subtotal", font=(GestorUI.FUENTE_PRINCIPAL, 14, "bold"), text_color="white", width=100, anchor="e").pack(side="left", padx=20, pady=5)

        self.caja_carrito = ctk.CTkScrollableFrame(self.frame_izquierdo, fg_color="white", corner_radius=5)
        self.caja_carrito.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # PANEL DERECHO: Totales y Botones
        self.frame_derecho = ctk.CTkFrame(self.frame_central, fg_color=GestorUI.PANEL, corner_radius=10, width=300)
        self.frame_derecho.pack(side="right", fill="y", padx=10)

        self.label_resumen = ctk.CTkLabel(self.frame_derecho, text="Resumen de Venta", font=(GestorUI.FUENTE_PRINCIPAL, 20, "bold"), text_color=GestorUI.TEXTO)
        self.label_resumen.pack(pady=20, padx=20)

        self.label_total = ctk.CTkLabel(self.frame_derecho, text="Total: $0.00", font=(GestorUI.FUENTE_PRINCIPAL, 35, "bold"), text_color=GestorUI.VINO)
        self.label_total.pack(pady=40, padx=20)

        # 🔘 LLAMAMOS A LOS BOTONES DESDE NUESTRA FÁBRICA CENTRAL 🔘
        GestorUI.btn_inventario(self.frame_derecho, self.abrir_ventana_inventario).pack(pady=10, padx=20, fill="x")
        GestorUI.btn_eliminar_prod(self.frame_derecho, self.solicitar_clave_eliminacion).pack(pady=10, padx=20, fill="x")
        GestorUI.btn_corte_caja(self.frame_derecho, self.mostrar_corte_caja).pack(pady=10, padx=20, fill="x")
        GestorUI.btn_diseno_ticket(self.frame_derecho, self.solicitar_clave_editor).pack(pady=10, padx=20, fill="x")
        GestorUI.btn_cobrar(self.frame_derecho, self.procesar_cobro).pack(pady=20, padx=20, fill="x", side="bottom")

    # --- FUNCIONES BASE ---
    def enfocar_buscador(self, evento=None):
        self.entrada_buscador.focus()

    def centrar_ventana(self, ventana, ancho, alto, bloquear=True):
        pantalla_ancho = ventana.winfo_screenwidth()
        pantalla_alto = ventana.winfo_screenheight()
        x = int((pantalla_ancho / 2) - (ancho / 2))
        y = int((pantalla_alto / 2) - (alto / 2))
        ventana.geometry(f"{ancho}x{alto}+{x}+{y}")
        
        if ventana != self and bloquear:
            def advertencia_bloqueo(evento):
                x_raton, y_raton = evento.x_root, evento.y_root
                x_min, y_min = ventana.winfo_rootx() - 15, ventana.winfo_rooty() - 40 
                x_max, y_max = ventana.winfo_rootx() + ventana.winfo_width() + 15, ventana.winfo_rooty() + ventana.winfo_height() + 15
                if not (x_min <= x_raton <= x_max and y_min <= y_raton <= y_max):
                    if getattr(ventana, "mostrando_alerta", False) == False:
                        ventana.mostrando_alerta = True
                        messagebox.showwarning("Operación Pendiente", "⚠️ Por favor, termine la operación actual o presione 'Esc' para regresar.", parent=ventana)
                        ventana.mostrando_alerta = False
            ventana.bind("<Button-1>", advertencia_bloqueo, add="+")

    def mostrar_alerta_error(self, codigo):
        messagebox.showwarning("Alerta de Inventario", f"¡Cuidado!\nEl código '{codigo}' no está registrado.", parent=self)

    # --- DELEGACIÓN DE MÓDULOS EXTERNOS ---
    def abrir_ventana_inventario(self, evento=None):
        VentanaInventario(self, self.db, Credenciales.PROPIETARIO)

    def procesar_cobro(self, evento=None):
        if self.total_venta <= 0:
            messagebox.showwarning("Carrito Vacío", "No hay ningún producto en el carrito para cobrar.", parent=self)
            return
        VentanaCobro(self, self.db, self.hardware, self.carrito_compras, self.total_venta, self.limpiar_carrito_post_venta)

    def limpiar_carrito_post_venta(self):
        self.total_venta = 0.0
        self.label_total.configure(text="Total: $0.00")
        self.carrito_compras.clear()
        self.actualizar_pantalla_carrito()
        self.entrada_buscador.focus()

    def solicitar_clave_editor(self, evento=None):
        ModuloSeguridad.solicitar_clave(self, self, "🔒 Autorización de Propietario", "Clave de Propietario (F1):", Credenciales.PROPIETARIO, self.abrir_editor_ticket)

    def abrir_editor_ticket(self):
        try:
            if hasattr(self, 'ventana_editor_abierta') and self.ventana_editor_abierta is not None and self.ventana_editor_abierta.winfo_exists():
                self.ventana_editor_abierta.lift() 
                self.ventana_editor_abierta.focus()
                return
            self.ventana_editor_abierta = EditorTicket(self)
            self.centrar_ventana(self.ventana_editor_abierta, 950, 750, bloquear=False) 
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el Editor:\n{e}", parent=self)

    def solicitar_clave_eliminacion(self, evento=None):
        if not self.carrito_compras:
            messagebox.showwarning("Carrito Vacío", "No hay productos en el carrito para eliminar.", parent=self)
            return
        ModuloSeguridad.solicitar_clave(self, self, "🔒 Autorización de Gerente", "Ingresa Clave (F1):", Credenciales.ADMIN, self.abrir_ventana_eliminar)

    # --- LÓGICA INTERNA DE LA VENTANA (CARRITO Y BUSCADOR) ---
    def mostrar_corte_caja(self, evento=None):
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")
        cantidad_ventas, total_dia = self.db.obtener_ventas_del_dia(fecha_hoy)
        mensaje = f"📅 Fecha: {fecha_hoy}\n\n🛒 Número de ventas hoy: {cantidad_ventas}\n💰 Total recaudado: ${total_dia:.2f}"
        messagebox.showinfo("📊 Reporte Financiero", mensaje, parent=self)

    def escanear_producto(self, evento=None):
        if self.botones_sugerencias and self.indice_sugerencia_seleccionada != -1:
            codigo_escaneado = self.sugerencias_actuales[self.indice_sugerencia_seleccionada]
            self.entrada_buscador.delete(0, "end")
            self.entrada_buscador.insert(0, codigo_escaneado)
        else:
            codigo_escaneado = self.entrada_buscador.get().strip()
        
        self.frame_sugerencias.place_forget()
        self.sugerencias_actuales, self.botones_sugerencias, self.indice_sugerencia_seleccionada = [], [], -1
        
        producto = self.db.buscar_producto(codigo_escaneado)
        if producto:
            codigo, nombre, precio, stock = producto
            cantidad_en_carrito = self.carrito_compras[codigo]['cantidad'] if codigo in self.carrito_compras else 0
            nueva_cantidad = cantidad_en_carrito + 1
            
            if nueva_cantidad > stock:
                messagebox.showwarning("Stock Insuficiente", f"⚠️ ¡No puedes agregar más!\n\nSe están pidiendo {nueva_cantidad} pieza(s), pero solo te quedan {stock} pieza(s) de '{nombre}' en inventario.", parent=self)
                self.entrada_buscador.delete(0, "end")
                return 

            stock_restante = stock - nueva_cantidad
            if codigo in self.carrito_compras:
                self.carrito_compras[codigo]['cantidad'] += 1
                self.carrito_compras[codigo]['subtotal'] += precio
            else:
                self.carrito_compras[codigo] = {'nombre': nombre, 'precio': precio, 'cantidad': 1, 'subtotal': precio}
            
            self.total_venta += precio
            self.label_total.configure(text=f"Total: ${self.total_venta:.2f}")
            self.actualizar_pantalla_carrito()
            self.entrada_buscador.delete(0, "end")

            if stock_restante == 1: messagebox.showwarning("Stock Crítico", f"⚠️ ¡Atención! Solo te queda 1 pieza de '{nombre}'.", parent=self)
            elif stock_restante == 0: messagebox.showwarning("Producto Agotado", f"⚠️ Con esta venta, '{nombre}' se ha AGOTADO por completo.", parent=self)
        else:
            if codigo_escaneado: self.mostrar_alerta_error(codigo_escaneado)
            self.entrada_buscador.delete(0, "end")

    def actualizar_pantalla_carrito(self):
        for widget in self.caja_carrito.winfo_children(): widget.destroy()
        self.etiquetas_animadas = [] 
            
        for datos in self.carrito_compras.values():
            renglon = ctk.CTkFrame(self.caja_carrito, fg_color="transparent")
            renglon.pack(fill="x", pady=2)
            
            ctk.CTkLabel(renglon, text=str(datos['cantidad']), font=(GestorUI.FUENTE_PRINCIPAL, 16), text_color=GestorUI.TEXTO, width=60).pack(side="left", padx=5)
            ctk.CTkLabel(renglon, text=f"${datos['subtotal']:.2f}", font=(GestorUI.FUENTE_PRINCIPAL, 16, "bold"), text_color=GestorUI.VINO, width=100, anchor="e").pack(side="right", padx=15)
            ctk.CTkLabel(renglon, text=f"${datos['precio']:.2f}", font=(GestorUI.FUENTE_PRINCIPAL, 16), text_color=GestorUI.TEXTO, width=100, anchor="e").pack(side="right", padx=5)
            
            nombre_completo = datos['nombre']
            lbl_nombre = ctk.CTkLabel(renglon, font=(GestorUI.FUENTE_PRINCIPAL, 16), text_color=GestorUI.TEXTO, anchor="w")
            lbl_nombre.pack(side="left", fill="x", expand=True, padx=5)
            
            if len(nombre_completo) > 22:
                texto_marquee = f"{nombre_completo}   •   "
                lbl_nombre.configure(text=texto_marquee[:22])
                self.etiquetas_animadas.append({'label': lbl_nombre, 'text': texto_marquee, 'index': 0, 'limit': 22, 'pausa': 17})
            else:
                lbl_nombre.configure(text=nombre_completo) 
            
            ctk.CTkFrame(self.caja_carrito, height=1, fg_color="#E0E0E0").pack(fill="x", padx=10, pady=2)

        if self.etiquetas_animadas and not self.animacion_activa:
            self.animacion_activa = True
            self.animar_textos_marquesina(self.etiquetas_animadas, lambda: self.animacion_activa)

    def animar_textos_marquesina(self, lista_etiquetas, bandera_activa):
        if not lista_etiquetas: return
        etiquetas_vivas = []
        for item in lista_etiquetas:
            lbl = item['label']
            if lbl.winfo_exists():
                if item.get('pausa', 0) > 0:
                    item['pausa'] -= 1
                    etiquetas_vivas.append(item)
                    continue
                txt, idx, limite = item['text'], item['index'], item['limit']
                idx = (idx + 1) % len(txt)
                item['index'] = idx
                texto_mostrar = (txt + txt)[idx : idx + limite]
                lbl.configure(text=texto_mostrar)
                if idx == 0: item['pausa'] = 17 
                etiquetas_vivas.append(item)
                
        lista_etiquetas.clear()
        lista_etiquetas.extend(etiquetas_vivas)
        if lista_etiquetas: self.after(120, lambda: self.animar_textos_marquesina(lista_etiquetas, bandera_activa))

    def mostrar_sugerencias(self, evento=None):
        if evento and evento.keysym in ['Return', 'Up', 'Down', 'Left', 'Right', 'Escape']: return
        texto = self.entrada_buscador.get().strip()
        self.sugerencias_actuales, self.botones_sugerencias, self.indice_sugerencia_seleccionada = [], [], -1

        if len(texto) < 2:
            self.frame_sugerencias.place_forget()
            return
        
        productos = self.db.buscar_productos_por_nombre(texto)
        for widget in self.frame_sugerencias.winfo_children(): widget.destroy()

        ancho_barra = self.entrada_buscador.winfo_width()
        if ancho_barra <= 50: ancho_barra = 400
        ancho_base = max(300, int(ancho_barra * 0.55))

        if not productos:
            self.frame_sugerencias.configure(height=40, width=ancho_base) 
            ctk.CTkLabel(self.frame_sugerencias, text="⚠️ Producto inexistente", font=(GestorUI.FUENTE_PRINCIPAL, 13, "italic"), text_color="#888888", width=ancho_base - 25).pack(pady=5, padx=5)
        else:
            max_chars = max(len(f"{p[1]} | ${p[2]:.2f} | Stock: {p[3]}") for p in productos)
            ancho_final = max(ancho_base, min(int(max_chars * 8.5) + 40, ancho_barra))
            self.frame_sugerencias.configure(height=min(len(productos) * 36, 120), width=ancho_final)
            ancho_hijos = ancho_final - 25
            
            for prod in productos:
                cod, nom, pre, stc = prod
                self.sugerencias_actuales.append(cod) 
                nom_corto = nom if len(nom) <= 35 else nom[:32] + "..."
                btn = ctk.CTkButton(self.frame_sugerencias, text=f"{nom_corto} | ${pre:.2f} | Stock: {stc}", font=(GestorUI.FUENTE_PRINCIPAL, 13), anchor="w", fg_color="transparent", text_color=GestorUI.TEXTO, hover_color="#0078D7", width=ancho_hijos, height=28, command=lambda c=cod: self.seleccionar_sugerencia(c))
                btn.pack(pady=2, padx=5)
                self.botones_sugerencias.append(btn) 

        self.frame_sugerencias.place(x=self.entrada_buscador.winfo_x(), y=self.entrada_buscador.winfo_y() + self.entrada_buscador.winfo_height() + 2)
        self.frame_sugerencias.lift() 

    def navegar_sugerencias(self, evento):
        if not self.botones_sugerencias: return
        if evento.keysym == 'Down':
            self.indice_sugerencia_seleccionada = (self.indice_sugerencia_seleccionada + 1) % len(self.botones_sugerencias)
        elif evento.keysym == 'Up':
            self.indice_sugerencia_seleccionada = (self.indice_sugerencia_seleccionada - 1) % len(self.botones_sugerencias)

        for i, btn in enumerate(self.botones_sugerencias):
            btn.configure(fg_color="#0078D7" if i == self.indice_sugerencia_seleccionada else "transparent", text_color="white" if i == self.indice_sugerencia_seleccionada else GestorUI.TEXTO) 
        return "break" 

    def seleccionar_sugerencia(self, codigo):
        self.entrada_buscador.delete(0, "end")
        self.entrada_buscador.insert(0, codigo)
        self.frame_sugerencias.place_forget()
        self.sugerencias_actuales, self.botones_sugerencias, self.indice_sugerencia_seleccionada = [], [], -1
        self.escanear_producto(None)

    def ocultar_sugerencias_con_retraso(self, evento=None):
        self.after(200, lambda: self.frame_sugerencias.place_forget())

    def abrir_ventana_eliminar(self):
        ventana_eliminar = ctk.CTkToplevel(self)
        ventana_eliminar.title("🗑️ Eliminar Producto")
        self.centrar_ventana(ventana_eliminar, 400, 250)
        ventana_eliminar.configure(fg_color=GestorUI.FONDO)
        ventana_eliminar.transient(self)
        ventana_eliminar.grab_set()
        ventana_eliminar.bind("<Escape>", lambda evento: ventana_eliminar.destroy())

        ctk.CTkLabel(ventana_eliminar, text="Escanea para eliminar (F1):", font=(GestorUI.FUENTE_PRINCIPAL, 18, "bold"), text_color=GestorUI.TEXTO).pack(pady=20)
        entrada_eliminar = ctk.CTkEntry(ventana_eliminar, placeholder_text="Código de barras...", font=(GestorUI.FUENTE_PRINCIPAL, 16), width=300)
        entrada_eliminar.pack(pady=10)
        entrada_eliminar.focus()
        ventana_eliminar.bind("<F1>", lambda evento: entrada_eliminar.focus())

        def procesar_escaneo(evento=None):
            codigo = entrada_eliminar.get()
            if codigo in self.carrito_compras:
                cantidad_actual = self.carrito_compras[codigo]['cantidad']
                nombre = self.carrito_compras[codigo]['nombre']
                precio = self.carrito_compras[codigo]['precio']
                
                if cantidad_actual == 1:
                    del self.carrito_compras[codigo]
                    self.total_venta -= precio
                    self.label_total.configure(text=f"Total: ${self.total_venta:.2f}")
                    self.actualizar_pantalla_carrito()
                    messagebox.showinfo("Éxito", f"Se eliminó '{nombre}' del carrito.", parent=ventana_eliminar)
                    entrada_eliminar.delete(0, "end")
                    entrada_eliminar.focus()
                else:
                    ventana_cant = ctk.CTkToplevel(ventana_eliminar)
                    ventana_cant.title("Cantidad a borrar")
                    self.centrar_ventana(ventana_cant, 350, 220)
                    ventana_cant.configure(fg_color=GestorUI.FONDO)
                    ventana_cant.transient(ventana_eliminar)
                    ventana_cant.grab_set()
                    ventana_cant.bind("<Escape>", lambda evento: ventana_cant.destroy())

                    ctk.CTkLabel(ventana_cant, text=f"En carrito tienes: {cantidad_actual}\n\n¿Cuántos '{nombre}'\ndeseas anular?", font=(GestorUI.FUENTE_PRINCIPAL, 16, "bold"), text_color=GestorUI.TEXTO).pack(pady=10)
                    entrada_cant = ctk.CTkEntry(ventana_cant, font=(GestorUI.FUENTE_PRINCIPAL, 16), width=100)
                    entrada_cant.insert(0, "1") 
                    entrada_cant.pack(pady=10)
                    entrada_cant.focus()
                    ventana_cant.bind("<F1>", lambda evento: entrada_cant.focus())

                    def confirmar_borrado(evento=None):
                        try:
                            cant_borrar = int(entrada_cant.get())
                            if 1 <= cant_borrar <= cantidad_actual:
                                self.carrito_compras[codigo]['cantidad'] -= cant_borrar
                                self.carrito_compras[codigo]['subtotal'] -= (precio * cant_borrar)
                                self.total_venta -= (precio * cant_borrar)
                                if self.carrito_compras[codigo]['cantidad'] <= 0: del self.carrito_compras[codigo]
                                self.label_total.configure(text=f"Total: ${self.total_venta:.2f}")
                                self.actualizar_pantalla_carrito()
                                messagebox.showinfo("Éxito", f"Se anularon {cant_borrar} pieza(s) de '{nombre}'.", parent=ventana_cant)
                                ventana_cant.destroy()
                                entrada_eliminar.delete(0, "end")
                                entrada_eliminar.focus()
                            else:
                                messagebox.showwarning("Error", f"Por favor ingresa un número entre 1 y {cantidad_actual}.", parent=ventana_cant)
                        except ValueError:
                            messagebox.showerror("Error", "Debes ingresar un número válido.", parent=ventana_cant)

                    entrada_cant.bind("<Return>", confirmar_borrado)
                    GestorUI.btn_confirmar_anulacion(ventana_cant, confirmar_borrado).pack(pady=10)
            else:
                messagebox.showwarning("Error", "Ese código no está en el carrito de compras actual.", parent=ventana_eliminar)
                entrada_eliminar.delete(0, "end")

        entrada_eliminar.bind("<Return>", procesar_escaneo)