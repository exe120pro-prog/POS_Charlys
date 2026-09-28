class Credenciales:
    """
    ========================================================
    🔐 BÓVEDA DE CREDENCIALES Y PERMISOS
    ========================================================
    Clase centralizada para manejar las contraseñas del sistema.
    Al estar aislada, si el dueño pide cambiar su nip de "0000" a "7777",
    solo se modifica este archivo y todo el sistema se actualiza.
    """
    
    # 🔒 Clave para el empleado/cajero 
    # Permisos: Eliminar productos del carrito, devoluciones básicas.
    ADMIN = "1234"
    
    # 👑 Clave maestra para el dueño 
    # Permisos: Borrar inventario permanentemente, modificar diseño del ticket.
    PROPIETARIO = "0000"

    """
    ========================================================
    🚀 NOTA PARA FUTURAS ACTUALIZACIONES:
    ========================================================
    Cuando decidamos que el dueño pueda cambiar su clave desde 
    una pantalla dentro del programa, esta clase evolucionará 
    a algo como esto (sin romper el resto del sistema):

    @classmethod
    def verificar_propietario(cls, clave_ingresada, db):
        clave_real = db.obtener_clave_dueño()
        return clave_ingresada == clave_real
    """