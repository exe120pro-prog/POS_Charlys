from escpos.printer import Win32Raw
import os
import sys # 🔥 NUEVO: Para manejar rutas del sistema
import qrcode
from PIL import Image

# 🔥 TRUCO SENIOR: Le enseñamos a Python dónde está la carpeta raíz del proyecto 🔥
# Así, aunque ejecutes este archivo suelto, sabrá encontrar la carpeta "nucleo"
ruta_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ruta_raiz not in sys.path:
    sys.path.append(ruta_raiz)

class HardwarePOS:
    def __init__(self, nombre_impresora=None):
        # 🔥 RUTAS INTELIGENTES Y PROTEGIDAS 🔥
        self.ruta_base = ruta_raiz
        self.ruta_recursos = os.path.join(self.ruta_base, "recursos")
        
        # Si por accidente borran la carpeta, el sistema la recrea automáticamente
        os.makedirs(self.ruta_recursos, exist_ok=True)
        
        self.ruta_logo = os.path.join(self.ruta_recursos, "logo_ticket.png")
        self.ruta_qr = os.path.join(self.ruta_recursos, "qr_temp.png")

        self.impresora = None
        self.config_db = None

        if nombre_impresora:
            self.nombre_impresora = nombre_impresora
        else:
            self._cargar_configuracion() # 🔥 Llamamos a la función centralizada

    # 🛠️ NUEVA FUNCIÓN: Centraliza la lectura de la Base de Datos para no repetir código
    def _cargar_configuracion(self):
        try:
            from nucleo.base_datos import BaseDatos
            db = BaseDatos()
            config = db.obtener_config_ticket()
            
            if config:
                if len(config) >= 13:
                    self.config_db = config[:13]
                    self.nombre_impresora = config[11]
                elif len(config) == 12:
                    self.config_db = config[:12] + ("Modo de (Ahorro de energía)",)
                    self.nombre_impresora = config[11]
                elif len(config) == 11:
                    self.config_db = config[:11] + ("58 Printer", "Modo de (Ahorro de energía)")
                    self.nombre_impresora = "58 Printer"
                elif len(config) == 10:
                    self.config_db = config + (15, "58 Printer", "Modo de (Ahorro de energía)")
                    self.nombre_impresora = "58 Printer"
                else:
                    self.config_db = config + (6, 15, "58 Printer", "Modo de (Ahorro de energía)")
                    self.nombre_impresora = "58 Printer"
            else:
                self._configuracion_por_defecto()
                
        except Exception as e:
            print(f"⚠️ No se pudo cargar la BD en Hardware. Usando defecto. Error: {e}")
            self._configuracion_por_defecto()

    def _configuracion_por_defecto(self):
        self.config_db = (1, "CHARLYS CEL & PC", "Plaza Principal Loc. 5", "Tel: 555-123-4567", 
                          "¡Gracias por su compra!", "Tamaño A (Normal)", 0, 0, 0, 6, 15, 
                          "58 Printer", "Modo de (Ahorro de energía)")
        self.nombre_impresora = "58 Printer"

    def conectar(self):
        try:
            self.impresora = Win32Raw(self.nombre_impresora)
            print(f"✅ Conexión iniciada con: {self.nombre_impresora}")
            return True
        except Exception as e:
            print(f"❌ Error al conectar con la impresora: {e}")
            return False

    def cerrar_conexion(self):
        if self.impresora:
            try:
                self.impresora.close()
                self.impresora = None
            except Exception as e:
                print(f"❌ Error al cerrar impresora: {e}")

    def limpiar_texto(self, texto):
        if not texto: return ""
        reemplazos = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
            'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
            'ñ': 'n', 'Ñ': 'N', '¿': '?', '¡': '!'
        }
        res = str(texto)
        for orig, nuevo in reemplazos.items():
            res = res.replace(orig, nuevo)
        return res

    def imprimir_ticket_venta(self, carrito, total, pago, cambio):
        # Actualizamos la configuración justo antes de imprimir
        self._cargar_configuracion()
        
        _, nombre, direccion, telefono, despedida, tamano, negritas, logo, qr, escala_qr, espacio_qr, impresora_bd, calidad_impresora = self.config_db

        if not self.conectar():
            return

        nombre = self.limpiar_texto(nombre)
        direccion = self.limpiar_texto(direccion)
        despedida = self.limpiar_texto(despedida)

        seleccion_tamano = str(tamano)
        es_negrita = bool(negritas)

        try:
            p = self.impresora
            
            p._raw(b'\x1b\x40') 
            p._raw(b'\x1c\x2e') 
            p._raw(b'\x1b!\x00')
            
            if "B" in seleccion_tamano:
                comando_tamano = b'\x1d!\x00' 
                comando_espaciado = b'\x1b\x33\x30' 
            elif "C" in seleccion_tamano:
                comando_tamano = b'\x1d!\x02' 
                comando_espaciado = b'\x1b\x32' 
            else:
                comando_tamano = b'\x1d!\x00' 
                comando_espaciado = b'\x1b\x32' 

            # Imprimir Logo
            if logo and os.path.exists(self.ruta_logo):
                try:
                    p.set(align="left")
                    p.image(self.ruta_logo, impl="bitImageColumn")
                except Exception as e:
                    print(f"⚠️ Aviso: Error imprimiendo el logo: {e}")

            if "Ahorro" in calidad_impresora:
                linea_iguales = "= = = = = = = = = = = = = = = \n"
                linea_guiones = "- - - - - - - - - - - - - - - \n"
            else:
                linea_iguales = "==============================\n"
                linea_guiones = "------------------------------\n"

            p.set(align="center", bold=True, double_height=True, double_width=True)
            if nombre:
                p.text(f"{nombre}\n")
            
            p._raw(b'\x1b!\x00')
            p._raw(comando_espaciado)
            
            p.set(align="center", bold=es_negrita)
            p._raw(comando_tamano)
            if direccion: p.text(f"{direccion}\n")
            if telefono: p.text(f"{telefono}\n")
            
            p.set(align="center", bold=es_negrita)
            p._raw(comando_tamano)
            p.text(linea_iguales)
            p.text("TICKET DE VENTA\n")
            p.text(linea_iguales)
            
            p.set(align="left", bold=es_negrita)
            p._raw(comando_tamano)
            for datos in carrito.values():
                cant_str = f"{datos['cantidad']}x"
                nombre_corto = self.limpiar_texto(datos['nombre'])[:16]
                linea = f"{cant_str:<4}{nombre_corto:<16} ${datos['subtotal']:>8.2f}\n"
                p.text(linea)
            
            p.text(linea_guiones)
            
            p.set(align="right", bold=es_negrita)
            p._raw(comando_tamano)
            p.text(f"TOTAL:  ${total:.2f}\n")
            p.text(f"PAGO:   ${pago:.2f}\n")
            p.text(f"CAMBIO: ${cambio:.2f}\n")
            
            p.set(align="center", bold=es_negrita)
            p._raw(comando_tamano)
            p.text(linea_iguales)
            
            if despedida:
                p.text(f"{despedida}\n")
            
            # 🔥 BLOQUE AISLADO PARA EL QR (Si falla, el ticket sigue) 🔥
            if qr:
                try:
                    numero = ''.join(filter(str.isdigit, str(telefono)))
                    if len(numero) == 10:
                        numero = "52" + numero
                    
                    link_wa = f"https://wa.me/{numero}?text=Hola,%20tengo%20una%20duda%20con%20mi%20compra"
                    
                    p.set(align="center", bold=es_negrita)
                    p._raw(comando_tamano)
                    p.text("\nContáctanos por WhatsApp:\n") 
                    
                    qr_obj = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=int(escala_qr), 
                        border=2,
                    )
                    qr_obj.add_data(link_wa)
                    qr_obj.make(fit=True)
                    
                    qr_img = qr_obj.make_image(fill_color="black", back_color="white").convert("RGBA")
                    
                    ancho_impresora = 384
                    espacio_qr_px = int(espacio_qr)
                    lienzo_qr = Image.new("RGB", (ancho_impresora, qr_img.height + espacio_qr_px), "WHITE")
                    x_offset = (ancho_impresora - qr_img.width) // 2
                    
                    lienzo_qr.paste(qr_img, (x_offset, espacio_qr_px), qr_img)
                    
                    lienzo_qr.convert("1").save(self.ruta_qr)
                    p.set(align="left")
                    p.image(self.ruta_qr, impl="bitImageColumn")
                    p.text("\n")
                except Exception as e_qr:
                    print(f"⚠️ Aviso: No se pudo imprimir el código QR: {e_qr}")
            
            p.text("\n\n\n\n")
            self.abrir_cajon_dinero_interno()
            print("🎫 Ticket de venta impreso correctamente.")

        except Exception as e:
            print(f"❌ Error crítico imprimiendo el recibo de venta: {e}")
        finally:
            if self.impresora:
                self.impresora._raw(b'\x1b\x32') 
            self.cerrar_conexion()

    def abrir_cajon_dinero_interno(self):
        if self.impresora:
            try:
                self.impresora.cashdraw(2)
            except Exception as e:
                print(f"❌ Error abriendo cajón: {e}")

    def abrir_cajon_independiente(self):
        self._cargar_configuracion() # 🔥 Reutilizamos la función
        if self.conectar():
            self.abrir_cajon_dinero_interno()
            self.cerrar_conexion()

    def imprimir_ticket_prueba(self):
        print("🛠️ Iniciando prueba de impresión...")
        carrito_prueba = {
            "123": {'nombre': 'Mica Cristal', 'cantidad': 1, 'subtotal': 100.00},
            "456": {'nombre': 'Funda Silicon', 'cantidad': 2, 'subtotal': 250.00}
        }
        self.imprimir_ticket_venta(carrito_prueba, total=350.00, pago=500.00, cambio=150.00)

if __name__ == "__main__":
    hw = HardwarePOS()
    hw.imprimir_ticket_prueba()