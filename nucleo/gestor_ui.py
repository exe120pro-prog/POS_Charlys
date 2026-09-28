import customtkinter as ctk

class GestorUI:
    """
    ========================================================
    🎨 PALETA DE COLORES GLOBAL DEL SISTEMA
    ========================================================
    Aquí se centralizan los colores. Si cambias un color aquí,
    cambiará automáticamente en TODO el sistema.
    """
    FONDO = "#F0F0F0"       # Fondo general de todas las ventanas
    PANEL = "#E0E0E0"       # Fondo de los cuadros y divisiones
    TEXTO = "#1A1A1A"       # Color del texto general
    
    # 🍷 Color Principal (La identidad de Charlys)
    VINO = "#800020"        
    VINO_HOVER = "#5E0018"  
    
    # 🌈 Colores Secundarios y de Acción
    AZUL = "#0078D7"
    AZUL_HOVER = "#005A9E"
    VERDE = "#005f73"
    VERDE_HOVER = "#0a9396"
    MORADO = "#5A189A"
    MORADO_HOVER = "#3C096C"
    NARANJA = "#FF4500"
    NARANJA_HOVER = "#CC3700"
    
    # ⚙️ Colores Neutros
    GRIS = "#333333"
    GRIS_HOVER = "#1A1A1A"
    GRIS_CLARO = "#666666"
    GRIS_CLARO_HOVER = "#444444"

    """
    ========================================================
    🔤 TIPOGRAFÍA GLOBAL DEL SISTEMA
    ========================================================
    """
    FUENTE_PRINCIPAL = "Arial"

    """
    ========================================================
    🔘 FÁBRICA CENTRAL DE BOTONES
    ========================================================
    Todos los botones del sistema se fabrican aquí. 
    Para agregar uno nuevo, agrégalo a su bloque correspondiente.
    """

    # --------------------------------------------------------
    # 🏠 BOTONES DE LA VENTANA PRINCIPAL (Caja Registradora)
    # --------------------------------------------------------
    @staticmethod
    def btn_inventario(master, comando):
        return ctk.CTkButton(master, text="📦 Administrar Inventario (F2)", font=(GestorUI.FUENTE_PRINCIPAL, 16, "bold"), text_color="white", fg_color=GestorUI.GRIS, hover_color=GestorUI.GRIS_HOVER, height=40, command=comando)

    @staticmethod
    def btn_eliminar_prod(master, comando):
        return ctk.CTkButton(master, text="🗑️ Eliminar Producto (F3)", font=(GestorUI.FUENTE_PRINCIPAL, 16, "bold"), text_color="white", fg_color=GestorUI.NARANJA, hover_color=GestorUI.NARANJA_HOVER, height=40, command=comando)

    @staticmethod
    def btn_corte_caja(master, comando):
        return ctk.CTkButton(master, text="📊 Corte de Caja (F4)", font=(GestorUI.FUENTE_PRINCIPAL, 16, "bold"), text_color="white", fg_color=GestorUI.VERDE, hover_color=GestorUI.VERDE_HOVER, height=40, command=comando)

    @staticmethod
    def btn_diseno_ticket(master, comando):
        return ctk.CTkButton(master, text="🎨 Diseño de Ticket (F5)", font=(GestorUI.FUENTE_PRINCIPAL, 16, "bold"), text_color="white", fg_color=GestorUI.MORADO, hover_color=GestorUI.MORADO_HOVER, height=40, command=comando)

    @staticmethod
    def btn_cobrar(master, comando):
        return ctk.CTkButton(master, text="💰 COBRAR (F12)", font=(GestorUI.FUENTE_PRINCIPAL, 20, "bold"), text_color="white", fg_color=GestorUI.VINO, hover_color=GestorUI.VINO_HOVER, height=60, command=comando)


    # --------------------------------------------------------
    # 💵 BOTONES DEL MÓDULO DE COBRO
    # --------------------------------------------------------
    @staticmethod
    def btn_confirmar_pago(master, comando):
        return ctk.CTkButton(master, text="✅ Confirmar Pago (Enter)", font=(GestorUI.FUENTE_PRINCIPAL, 16, "bold"), text_color="white", fg_color=GestorUI.AZUL, hover_color=GestorUI.AZUL_HOVER, height=45, command=comando)

    @staticmethod
    def btn_aceptar_venta(master, comando):
        return ctk.CTkButton(master, text="Aceptar (Enter)", font=(GestorUI.FUENTE_PRINCIPAL, 18, "bold"), text_color="white", fg_color=GestorUI.VINO, hover_color=GestorUI.VINO_HOVER, height=45, command=comando)


    # --------------------------------------------------------
    # 📦 BOTONES DEL MÓDULO DE INVENTARIO
    # --------------------------------------------------------
    @staticmethod
    def btn_guardar_inventario(master, comando):
        return ctk.CTkButton(master, text="💾 Guardar / Actualizar", font=(GestorUI.FUENTE_PRINCIPAL, 14, "bold"), text_color="white", fg_color=GestorUI.VINO, hover_color=GestorUI.VINO_HOVER, height=38, command=comando)

    @staticmethod
    def btn_limpiar_formulario(master, comando):
        return ctk.CTkButton(master, text="🧹 Limpiar Formulario", font=(GestorUI.FUENTE_PRINCIPAL, 12), text_color="white", fg_color=GestorUI.GRIS_CLARO, hover_color=GestorUI.GRIS_CLARO_HOVER, height=30, command=comando)

    @staticmethod
    def btn_icono_borrar(master, comando):
        return ctk.CTkButton(master, text="🗑️", width=28, height=24, text_color="white", fg_color=GestorUI.NARANJA, hover_color=GestorUI.NARANJA_HOVER, command=comando)

    @staticmethod
    def btn_icono_editar(master, comando):
        return ctk.CTkButton(master, text="✏️", width=28, height=24, text_color="white", fg_color=GestorUI.GRIS, hover_color=GestorUI.GRIS_HOVER, command=comando)


    # --------------------------------------------------------
    # 🔒 BOTONES DE SEGURIDAD (Módulo Seguridad y Eliminación)
    # --------------------------------------------------------
    @staticmethod
    def btn_desbloquear(master, comando):
        return ctk.CTkButton(master, text="Desbloquear", font=(GestorUI.FUENTE_PRINCIPAL, 14, "bold"), text_color="white", fg_color=GestorUI.VINO, hover_color=GestorUI.VINO_HOVER, height=35, command=comando)

    @staticmethod
    def btn_confirmar_anulacion(master, comando):
        return ctk.CTkButton(master, text="Confirmar Anulación", font=(GestorUI.FUENTE_PRINCIPAL, 14, "bold"), text_color="white", fg_color=GestorUI.VINO, hover_color=GestorUI.VINO_HOVER, height=35, command=comando)


    # --------------------------------------------------------
    # 🎨 BOTONES DEL EDITOR DE TICKET
    # --------------------------------------------------------
    @staticmethod
    def btn_seleccionar_logo(master, comando):
        return ctk.CTkButton(master, text="📂 Seleccionar", font=(GestorUI.FUENTE_PRINCIPAL, 12, "bold"), text_color="white", fg_color=GestorUI.GRIS, hover_color=GestorUI.GRIS_HOVER, width=100, height=28, command=comando)

    @staticmethod
    def btn_guardar_diseno(master, comando):
        return ctk.CTkButton(master, text="💾 Guardar Diseño", font=(GestorUI.FUENTE_PRINCIPAL, 16, "bold"), text_color="white", fg_color=GestorUI.VINO, hover_color=GestorUI.VINO_HOVER, height=45, command=comando)

    @staticmethod
    def btn_imprimir_prueba(master, comando):
        return ctk.CTkButton(master, text="🖨️ Imprimir Prueba", font=(GestorUI.FUENTE_PRINCIPAL, 16, "bold"), text_color="white", fg_color=GestorUI.VERDE, hover_color=GestorUI.VERDE_HOVER, height=45, command=comando)