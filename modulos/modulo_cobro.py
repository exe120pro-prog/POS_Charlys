import customtkinter as ctk
from tkinter import messagebox
from nucleo.gestor_ui import GestorUI # 🔥 Conectado al Gestor Central

class VentanaCobro(ctk.CTkToplevel):
    """
    ========================================================
    💵 MÓDULO DE COBRO Y TRANSACCIONES
    ========================================================
    Calcula el cambio, descuenta el stock de la base de datos,
    dispara la orden de impresión térmica y muestra el resumen de venta.
    """
    def __init__(self, padre, db, hardware, carrito, total, callback_exito):
        super().__init__(padre)
        
        self.padre = padre
        self.db = db
        self.hardware = hardware
        self.carrito_compras = carrito
        self.total_venta = total
        self.callback_exito = callback_exito 
        
        self.title("💵 Calculadora de Cambio")
        self.padre.centrar_ventana(self, 400, 350)
        self.configure(fg_color=GestorUI.FONDO)
        
        self.transient(padre)
        self.grab_set()
        self.bind("<Escape>", lambda evento: self.destroy())

        # 🔤 Cambio de fuentes a GestorUI.FUENTE_PRINCIPAL
        ctk.CTkLabel(self, text="Total a Cobrar:", font=(GestorUI.FUENTE_PRINCIPAL, 22, "bold"), text_color=GestorUI.TEXTO).pack(pady=(25, 5))
        ctk.CTkLabel(self, text=f"${self.total_venta:.2f}", font=(GestorUI.FUENTE_PRINCIPAL, 40, "bold"), text_color=GestorUI.VINO).pack(pady=(0, 25))

        ctk.CTkLabel(self, text="¿Con cuánto paga el cliente? (F1):", font=(GestorUI.FUENTE_PRINCIPAL, 16, "bold"), text_color=GestorUI.TEXTO).pack(pady=(10, 5))
        
        self.entrada_pago = ctk.CTkEntry(self, font=(GestorUI.FUENTE_PRINCIPAL, 24), width=200, justify="center")
        self.entrada_pago.pack(pady=10)
        self.entrada_pago.focus()
        
        self.bind("<F1>", lambda evento: self.entrada_pago.focus())
        self.entrada_pago.bind("<Return>", self.confirmar_pago)
        
        # 🔘 Botón desde la Fábrica
        GestorUI.btn_confirmar_pago(self, self.confirmar_pago).pack(pady=20)

    def confirmar_pago(self, evento=None):
        pago_str = self.entrada_pago.get().strip()
        
        if not pago_str:
            messagebox.showerror("Error", "Por favor ingresa la cantidad con la que te están pagando.", parent=self)
            return
            
        try:
            pago = float(pago_str)
        except ValueError:
            messagebox.showerror("Error", "Ingresa una cantidad válida con números (ej. 200).", parent=self)
            return

        if pago < self.total_venta:
            faltante = self.total_venta - pago
            messagebox.showwarning("Fondos Insuficientes", f"⚠️ El pago no cubre el total.\n\nFaltan: ${faltante:.2f}", parent=self)
            return

        cambio = pago - self.total_venta

        productos_stock_critico = []
        for codigo, datos in self.carrito_compras.items():
            self.db.descontar_stock(codigo, datos['cantidad'])
            prod_actualizado = self.db.buscar_producto(codigo)
            
            if prod_actualizado and prod_actualizado[3] <= 1:
                productos_stock_critico.append(f"• {prod_actualizado[1]} (Quedan: {prod_actualizado[3]} pzs)")

        self.db.registrar_venta(self.total_venta)
        self.hardware.imprimir_ticket_venta(self.carrito_compras, self.total_venta, pago, cambio)
        
        self.mostrar_ventana_exito(pago, cambio, productos_stock_critico)

    def mostrar_ventana_exito(self, pago, cambio, productos_stock_critico):
        ventana_exito = ctk.CTkToplevel(self)
        ventana_exito.title("✅ Venta Realizada")
        self.padre.centrar_ventana(ventana_exito, 450, 400)
        ventana_exito.configure(fg_color=GestorUI.FONDO)
        ventana_exito.transient(self)
        ventana_exito.grab_set()

        # 🔤 Cambio de fuentes en la ventana de éxito
        ctk.CTkLabel(ventana_exito, text="✅ ¡Venta Exitosa!", font=(GestorUI.FUENTE_PRINCIPAL, 30, "bold"), text_color="#28a745").pack(pady=(30, 10))
        ctk.CTkLabel(ventana_exito, text=f"Recibido: ${pago:.2f}", font=(GestorUI.FUENTE_PRINCIPAL, 20), text_color=GestorUI.TEXTO).pack(pady=5)
        ctk.CTkLabel(ventana_exito, text="💰 CAMBIO A DEVOLVER:", font=(GestorUI.FUENTE_PRINCIPAL, 22, "bold"), text_color=GestorUI.TEXTO).pack(pady=(20, 0))
        
        ctk.CTkLabel(ventana_exito, text=f"${cambio:.2f}", font=(GestorUI.FUENTE_PRINCIPAL, 60, "bold"), text_color=GestorUI.VINO).pack(pady=(0, 20))

        if productos_stock_critico:
            frame_critico = ctk.CTkScrollableFrame(ventana_exito, fg_color="#ffe6e6", height=60)
            frame_critico.pack(fill="x", padx=30, pady=(5, 10))
            ctk.CTkLabel(frame_critico, text="⚠️ Quedan 1 o 0 piezas de:", font=(GestorUI.FUENTE_PRINCIPAL, 12, "bold"), text_color="#D90429").pack(anchor="w")
            for prod_crit in productos_stock_critico:
                ctk.CTkLabel(frame_critico, text=prod_crit, font=(GestorUI.FUENTE_PRINCIPAL, 12), text_color="#D90429").pack(anchor="w")

        def cerrar_todo(evento=None):
            ventana_exito.destroy()
            self.destroy()
            self.callback_exito() 

        ventana_exito.bind("<Return>", cerrar_todo)
        ventana_exito.bind("<Escape>", cerrar_todo)
        
        # 🔘 Botón desde la Fábrica
        GestorUI.btn_aceptar_venta(ventana_exito, cerrar_todo).pack(pady=(10, 20))