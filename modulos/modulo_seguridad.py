import customtkinter as ctk
from tkinter import messagebox
from nucleo.gestor_ui import GestorUI # 🔥 Conectado al Gestor Central

class ModuloSeguridad:
    """
    ========================================================
    🔒 MÓDULO DE SEGURIDAD Y AUTENTICACIÓN
    ========================================================
    Genera una ventana modal (que bloquea el fondo) para 
    solicitar credenciales antes de ejecutar acciones críticas.
    """
    
    @staticmethod
    def solicitar_clave(ventana_actual, ventana_principal, titulo, mensaje, clave_correcta, callback_exito):
        ventana_auth = ctk.CTkToplevel(ventana_actual)
        ventana_auth.title(titulo)
        ventana_principal.centrar_ventana(ventana_auth, 350, 200)
        
        # 🎨 Extraemos los colores del Gestor
        ventana_auth.configure(fg_color=GestorUI.FONDO)
        
        # El grab_set() funciona como un "candado" para que el usuario 
        # no pueda dar clic atrás hasta que cierre esta ventanita
        ventana_auth.transient(ventana_actual)
        ventana_auth.grab_set() 
        ventana_auth.bind("<Escape>", lambda evento: ventana_auth.destroy())

        # 🔤 Usamos la FUENTE_PRINCIPAL de nuestra Fábrica de UI
        lbl_titulo = ctk.CTkLabel(ventana_auth, text=mensaje, font=(GestorUI.FUENTE_PRINCIPAL, 18, "bold"), text_color=GestorUI.TEXTO)
        lbl_titulo.pack(pady=20)

        entrada_clave = ctk.CTkEntry(ventana_auth, show="*", font=(GestorUI.FUENTE_PRINCIPAL, 16), width=200)
        entrada_clave.pack(pady=10)
        entrada_clave.focus()
        
        ventana_auth.bind("<F1>", lambda evento: entrada_clave.focus())

        def verificar_clave(evento=None):
            if entrada_clave.get() == clave_correcta:
                ventana_auth.destroy()
                callback_exito() # Ejecuta la función que se le haya mandado (ej. borrar, abrir editor)
            else:
                messagebox.showerror("Acceso Denegado", "Clave incorrecta. Inténtalo de nuevo.", parent=ventana_auth)
                entrada_clave.delete(0, "end") # Limpiamos la cajita para un nuevo intento

        entrada_clave.bind("<Return>", verificar_clave)
        
        # 🔘 Botón extraído de la Fábrica
        GestorUI.btn_desbloquear(ventana_auth, verificar_clave).pack(pady=10)