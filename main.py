# Importamos la pantalla que creamos en el otro archivo
from modulos.modulo_interfaz import VentanaPrincipal

if __name__ == "__main__":
    # Creamos la ventana y la arrancamos
    app = VentanaPrincipal()
    app.mainloop()