import customtkinter as ctk
from tkinter import messagebox, filedialog
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps 
import qrcode 
import win32print

# 🔥 Rutas importadas según la nueva arquitectura 🔥
from nucleo.hardware import HardwarePOS 
from nucleo.gestor_ui import GestorUI

class EditorTicket(ctk.CTkToplevel):
    """
    ========================================================
    🎨 MÓDULO DEL EDITOR DE TICKET
    ========================================================
    Permite al dueño personalizar el encabezado, despedida, logo 
    y QR del recibo de compra. Incluye un simulador visual (Canvas) 
    y conexión directa para pruebas físicas.
    """
    def __init__(self, master=None):
        super().__init__(master)
        
        # 🔥 RUTAS INTELIGENTES PARA LAS IMÁGENES 🔥
        self.ruta_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.ruta_recursos = os.path.join(self.ruta_base, "recursos")
        
        # Protección por si borran la carpeta
        os.makedirs(self.ruta_recursos, exist_ok=True)
        
        self.ruta_logo = os.path.join(self.ruta_recursos, "logo_ticket.png")
        self.ruta_qr = os.path.join(self.ruta_recursos, "qr_temp.png")

        self.title("🎨 Editor de Plantilla de Ticket")
        self.update_idletasks() 
        
        pantalla_ancho = self.winfo_screenwidth()
        pantalla_alto = self.winfo_screenheight()
        
        ancho_ventana = min(950, pantalla_ancho - 20)
        alto_ventana = min(750, pantalla_alto - 50)
        
        x = int((pantalla_ancho / 2) - (ancho_ventana / 2))
        y = int((pantalla_alto / 2) - (alto_ventana / 2))
        
        self.geometry(f"{ancho_ventana}x{alto_ventana}+{x}+{y}") 
        
        self.configure(fg_color=GestorUI.FONDO) 
        
        self.hardware = HardwarePOS()
        self.img_final = None
        self.id_timer_resize = None
        
        try:
            from nucleo.base_datos import BaseDatos 
            self.db = BaseDatos()
            config = self.db.obtener_config_ticket()
            if config:
                if len(config) >= 13:
                    _, self.val_nombre, self.val_dir, self.val_tel, self.val_desp, self.val_tam, self.val_neg, self.val_logo, self.val_qr, self.val_escala, self.val_espacio, self.val_impresora, self.val_calidad = config[:13]
                elif len(config) == 12:
                    _, self.val_nombre, self.val_dir, self.val_tel, self.val_desp, self.val_tam, self.val_neg, self.val_logo, self.val_qr, self.val_escala, self.val_espacio, self.val_impresora = config[:12]
                    self.val_calidad = "Modo de (Ahorro de energía)"
                elif len(config) == 11:
                    _, self.val_nombre, self.val_dir, self.val_tel, self.val_desp, self.val_tam, self.val_neg, self.val_logo, self.val_qr, self.val_escala, self.val_espacio = config[:11]
                    self.val_impresora = "Seleccionar"
                    self.val_calidad = "Modo de (Ahorro de energía)"
                elif len(config) == 10:
                    _, self.val_nombre, self.val_dir, self.val_tel, self.val_desp, self.val_tam, self.val_neg, self.val_logo, self.val_qr, self.val_escala = config
                    self.val_espacio = 15
                    self.val_impresora = "Seleccionar"
                    self.val_calidad = "Modo de (Ahorro de energía)"
                else:
                    _, self.val_nombre, self.val_dir, self.val_tel, self.val_desp, self.val_tam, self.val_neg, self.val_logo, self.val_qr = config
                    self.val_escala = 6
                    self.val_espacio = 15
                    self.val_impresora = "Seleccionar"
                    self.val_calidad = "Modo de (Ahorro de energía)"
            else:
                self.val_nombre, self.val_dir, self.val_tel, self.val_desp = "CHARLYS CEL & PC", "Plaza Principal Loc. 5", "Tel: 555-123-4567", "¡Gracias por su compra!"
                self.val_tam, self.val_neg, self.val_logo, self.val_qr, self.val_escala, self.val_espacio, self.val_impresora, self.val_calidad = "Tamaño A (Normal)", 0, 0, 0, 6, 15, "Seleccionar", "Modo de (Ahorro de energía)"
        except Exception as e:
            print(f"⚠️ No se pudo cargar la BD: {e}")
            self.val_nombre, self.val_dir, self.val_tel, self.val_desp = "CHARLYS CEL & PC", "Plaza", "Tel: 123", "¡Gracias!"
            self.val_tam, self.val_neg, self.val_logo, self.val_qr, self.val_escala, self.val_espacio, self.val_impresora, self.val_calidad = "Tamaño A (Normal)", 0, 0, 0, 6, 15, "Seleccionar", "Modo de (Ahorro de energía)"

        self.frame_izquierdo = ctk.CTkFrame(self, fg_color=GestorUI.PANEL, corner_radius=10, width=420)
        self.frame_izquierdo.pack(side="left", fill="y", padx=20, pady=20)
        
        self.frame_derecho = ctk.CTkFrame(self, fg_color="#333333", corner_radius=10)
        self.frame_derecho.pack(side="right", fill="both", expand=True, padx=(0, 20), pady=20)
        
        self.construir_panel_configuracion()
        self.construir_panel_vista_previa()
        
        self.actualizar_vista_previa()
        self.bind("<Configure>", self.evento_redimensionar)

    def obtener_impresoras_windows(self):
        try:
            impresoras = [printer[2] for printer in win32print.EnumPrinters(2)]
            return impresoras if impresoras else []
        except Exception as e:
            return []

    def construir_panel_configuracion(self):
        # 🔤 Cambio de fuente en todos los componentes visuales
        ctk.CTkLabel(self.frame_izquierdo, text="⚙️ Configuración del Ticket", font=(GestorUI.FUENTE_PRINCIPAL, 20, "bold"), text_color=GestorUI.TEXTO).pack(pady=(20, 10))
        
        lista_impresoras = ["Seleccionar"] + self.obtener_impresoras_windows()
        
        if self.val_impresora and self.val_impresora != "Seleccionar" and self.val_impresora != "58 Printer" and self.val_impresora not in lista_impresoras:
            lista_impresoras.append(self.val_impresora) 
            
        if self.val_impresora == "58 Printer" or not self.val_impresora:
            self.val_impresora = "Seleccionar"

        ctk.CTkLabel(self.frame_izquierdo, text="Impresora Seleccionada:", font=(GestorUI.FUENTE_PRINCIPAL, 14, "bold"), text_color=GestorUI.VINO).pack(anchor="w", padx=20)
        self.opcion_impresora = ctk.CTkOptionMenu(
            self.frame_izquierdo, 
            values=lista_impresoras, 
            font=(GestorUI.FUENTE_PRINCIPAL, 14), 
            fg_color="#333333", button_color="#1A1A1A", width=320, height=32
        )
        self.opcion_impresora.set(self.val_impresora)
        self.opcion_impresora.pack(pady=(0, 10), padx=20)
        
        ctk.CTkLabel(self.frame_izquierdo, text="Potencia de Impresora:", font=(GestorUI.FUENTE_PRINCIPAL, 14, "bold"), text_color=GestorUI.TEXTO).pack(anchor="w", padx=20)
        self.opcion_potencia = ctk.CTkOptionMenu(
            self.frame_izquierdo, 
            values=["Modo de (Ahorro de energía)", "Modo de (Alto rendimiento)"], 
            font=(GestorUI.FUENTE_PRINCIPAL, 14), 
            fg_color="#005f73", button_color="#0a9396", width=320, height=32,
            command=self.actualizar_vista_previa
        )
        self.opcion_potencia.set(self.val_calidad)
        self.opcion_potencia.pack(pady=(0, 15), padx=20)

        ctk.CTkLabel(self.frame_izquierdo, text="Nombre del Negocio:", font=(GestorUI.FUENTE_PRINCIPAL, 14, "bold"), text_color=GestorUI.TEXTO).pack(anchor="w", padx=20)
        self.ent_nombre = ctk.CTkEntry(self.frame_izquierdo, font=(GestorUI.FUENTE_PRINCIPAL, 14), width=320)
        self.ent_nombre.insert(0, self.val_nombre)
        self.ent_nombre.pack(pady=(0, 10), padx=20)
        self.ent_nombre.bind("<KeyRelease>", self.actualizar_vista_previa)
        
        ctk.CTkLabel(self.frame_izquierdo, text="Dirección o Sucursal:", font=(GestorUI.FUENTE_PRINCIPAL, 14, "bold"), text_color=GestorUI.TEXTO).pack(anchor="w", padx=20)
        self.ent_direccion = ctk.CTkEntry(self.frame_izquierdo, font=(GestorUI.FUENTE_PRINCIPAL, 14), width=320)
        self.ent_direccion.insert(0, self.val_dir)
        self.ent_direccion.pack(pady=(0, 10), padx=20)
        self.ent_direccion.bind("<KeyRelease>", self.actualizar_vista_previa)
        
        ctk.CTkLabel(self.frame_izquierdo, text="Teléfono:", font=(GestorUI.FUENTE_PRINCIPAL, 14, "bold"), text_color=GestorUI.TEXTO).pack(anchor="w", padx=20)
        self.ent_telefono = ctk.CTkEntry(self.frame_izquierdo, font=(GestorUI.FUENTE_PRINCIPAL, 14), width=320)
        self.ent_telefono.insert(0, self.val_tel)
        self.ent_telefono.pack(pady=(0, 10), padx=20)
        self.ent_telefono.bind("<KeyRelease>", self.actualizar_vista_previa)
        
        ctk.CTkLabel(self.frame_izquierdo, text="Mensaje de Despedida:", font=(GestorUI.FUENTE_PRINCIPAL, 14, "bold"), text_color=GestorUI.TEXTO).pack(anchor="w", padx=20)
        self.ent_despedida = ctk.CTkEntry(self.frame_izquierdo, font=(GestorUI.FUENTE_PRINCIPAL, 14), width=320)
        self.ent_despedida.insert(0, self.val_desp)
        self.ent_despedida.pack(pady=(0, 10), padx=20)
        self.ent_despedida.bind("<KeyRelease>", self.actualizar_vista_previa)

        ctk.CTkLabel(self.frame_izquierdo, text="Formato del texto:", font=(GestorUI.FUENTE_PRINCIPAL, 14, "bold"), text_color=GestorUI.TEXTO).pack(anchor="w", padx=20)
        self.frame_formato = ctk.CTkFrame(self.frame_izquierdo, fg_color="transparent")
        self.frame_formato.pack(fill="x", padx=20, pady=(0, 5))

        self.opcion_tamano = ctk.CTkOptionMenu(
            self.frame_formato, 
            values=["Tamaño A (Normal)", "Tamaño B (Doble Alto)", "Tamaño C (Triple Alto)"], 
            fg_color="#333333", button_color="#1A1A1A", font=(GestorUI.FUENTE_PRINCIPAL, 12),
            command=self.actualizar_vista_previa, width=200
        )
        self.opcion_tamano.set(self.val_tam) 
        self.opcion_tamano.pack(side="left")

        self.check_negritas = ctk.CTkCheckBox(self.frame_formato, text="Negritas", font=(GestorUI.FUENTE_PRINCIPAL, 14, "bold"), text_color=GestorUI.TEXTO, command=self.actualizar_vista_previa)
        if self.val_neg: self.check_negritas.select()
        self.check_negritas.pack(side="left", padx=(15, 0))
        
        ctk.CTkLabel(self.frame_izquierdo, text="Imágenes y Extras:", font=(GestorUI.FUENTE_PRINCIPAL, 14, "bold"), text_color=GestorUI.TEXTO).pack(anchor="w", padx=20, pady=(5, 0))
        
        self.frame_logo = ctk.CTkFrame(self.frame_izquierdo, fg_color="transparent")
        self.frame_logo.pack(fill="x", padx=20, pady=5)
        
        self.check_logo = ctk.CTkCheckBox(self.frame_logo, text="Imprimir Logotipo", font=(GestorUI.FUENTE_PRINCIPAL, 14), text_color=GestorUI.TEXTO, command=self.actualizar_vista_previa)
        if self.val_logo: self.check_logo.select()
        self.check_logo.pack(side="left")
        
        GestorUI.btn_seleccionar_logo(self.frame_logo, self.cargar_logo).pack(side="right")
        
        self.frame_qr = ctk.CTkFrame(self.frame_izquierdo, fg_color="transparent")
        self.frame_qr.pack(fill="x", padx=20, pady=5)
        
        self.check_qr = ctk.CTkCheckBox(self.frame_qr, text="Código QR", font=(GestorUI.FUENTE_PRINCIPAL, 14), text_color=GestorUI.TEXTO, command=self.actualizar_vista_previa)
        if self.val_qr: self.check_qr.select()
        self.check_qr.pack(side="left")
        
        self.opcion_escala_qr = ctk.CTkOptionMenu(
            self.frame_qr, 
            values=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"], 
            width=50, height=28, fg_color="#333333", button_color="#1A1A1A", font=(GestorUI.FUENTE_PRINCIPAL, 12),
            command=self.actualizar_vista_previa
        )
        self.opcion_escala_qr.set(str(self.val_escala))
        self.opcion_escala_qr.pack(side="right", padx=(5, 0))
        ctk.CTkLabel(self.frame_qr, text="Tam:", font=(GestorUI.FUENTE_PRINCIPAL, 12, "bold"), text_color=GestorUI.TEXTO).pack(side="right")

        self.opcion_espacio_qr = ctk.CTkOptionMenu(
            self.frame_qr, 
            values=["5", "15", "30"], 
            width=50, height=28, fg_color="#333333", button_color="#1A1A1A", font=(GestorUI.FUENTE_PRINCIPAL, 12),
            command=self.actualizar_vista_previa
        )
        self.opcion_espacio_qr.set(str(self.val_espacio))
        self.opcion_espacio_qr.pack(side="right", padx=(15, 5))
        ctk.CTkLabel(self.frame_qr, text="Sep:", font=(GestorUI.FUENTE_PRINCIPAL, 12, "bold"), text_color=GestorUI.TEXTO).pack(side="right")

        GestorUI.btn_guardar_diseno(self.frame_izquierdo, self.guardar_configuracion).pack(side="bottom", fill="x", padx=20, pady=(10, 20))
        GestorUI.btn_imprimir_prueba(self.frame_izquierdo, self.imprimir_prueba_fisica).pack(side="bottom", fill="x", padx=20, pady=(10, 0))

    def construir_panel_vista_previa(self):
        ctk.CTkLabel(self.frame_derecho, text="Vista Previa Dinámica", font=(GestorUI.FUENTE_PRINCIPAL, 16, "bold"), text_color="white").pack(pady=(15, 5))
        
        self.frame_scroll = ctk.CTkScrollableFrame(self.frame_derecho, width=360, height=480, fg_color="transparent", corner_radius=0)
        self.frame_scroll.pack(pady=10, padx=20, fill="both", expand=True)
        
        self.lbl_vista_imagen = ctk.CTkLabel(self.frame_scroll, text="")
        self.lbl_vista_imagen.pack(pady=10, anchor="center")

    def cargar_logo(self):
        ruta_imagen = filedialog.askopenfilename(
            title="Seleccionar Logo del Negocio",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.bmp")]
        )
        if ruta_imagen:
            try:
                img = Image.open(ruta_imagen).convert("RGBA")
                fondo_blanco = Image.new("RGBA", img.size, "WHITE")
                fondo_blanco.paste(img, (0, 0), img)
                
                max_ancho = 300
                if fondo_blanco.width > max_ancho:
                    wpercent = (max_ancho / float(fondo_blanco.width))
                    hsize = int((float(fondo_blanco.height) * float(wpercent)))
                    img_redimensionada = fondo_blanco.resize((max_ancho, hsize), Image.Resampling.LANCZOS)
                else:
                    img_redimensionada = fondo_blanco

                ancho_impresora = 384
                lienzo_final = Image.new("RGB", (ancho_impresora, img_redimensionada.height), "WHITE")
                x_offset = (ancho_impresora - img_redimensionada.width) // 2
                lienzo_final.paste(img_redimensionada, (x_offset, 0))
                
                imagen_termica = lienzo_final.convert("1")
                # 🔥 Guarda en recursos 🔥
                imagen_termica.save(self.ruta_logo)
                
                self.check_logo.select()
                self.actualizar_vista_previa()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar la imagen:\n{e}", parent=self)
        
    def actualizar_vista_previa(self, evento=None):
        def centrar(texto):
            return texto[:30].center(30) + "\n"
            
        if "Ahorro" in self.opcion_potencia.get():
            linea_iguales = "= = = = = = = = = = = = = = = \n"
            linea_guiones = "- - - - - - - - - - - - - - - \n"
        else:
            linea_iguales = "==============================\n"
            linea_guiones = "------------------------------\n"
            
        ticket = ""
        ticket += centrar(self.ent_nombre.get().strip().upper())
        ticket += centrar(self.ent_direccion.get().strip())
        ticket += centrar(self.ent_telefono.get().strip())
        ticket += linea_iguales
        ticket += centrar("TICKET DE VENTA")
        ticket += linea_iguales
        ticket += "1x Mica Cristal        $100.00\n"
        ticket += "2x Funda Silicon       $250.00\n"
        ticket += linea_guiones
        ticket += "TOTAL:                 $350.00\n"
        ticket += linea_iguales
        ticket += centrar(self.ent_despedida.get().strip())
        
        try:
            ruta_fuente = "courbd.ttf" if self.check_negritas.get() else "cour.ttf"
            fuente = ImageFont.truetype(ruta_fuente, 16)
        except:
            fuente = ImageFont.load_default()

        ancho_ticket = 340 
        lineas = ticket.split("\n")
        alto_texto = max(len(lineas) * 19, 100)
        
        logo_procesado = None
        offset_y_logo = 15 
        # 🔥 Busca en recursos 🔥
        if self.check_logo.get() and os.path.exists(self.ruta_logo):
            try:
                logo_orig = Image.open(self.ruta_logo)
                wpercent = (ancho_ticket / float(logo_orig.width))
                hsize = int((float(logo_orig.height) * float(wpercent)))
                logo_procesado = logo_orig.resize((ancho_ticket, hsize), Image.Resampling.LANCZOS)
                logo_procesado = logo_procesado.convert("1").convert("L")
                offset_y_logo += logo_procesado.height + 15
            except Exception as e:
                pass

        qr_procesado = None
        alto_qr_seccion = 0
        espacio_qr_px = int(self.opcion_espacio_qr.get()) 
        
        if self.check_qr.get():
            try:
                numero = ''.join(filter(str.isdigit, self.ent_telefono.get()))
                if len(numero) == 10: numero = "52" + numero
                link_wa = f"https://wa.me/{numero}?text=Hola"
                qr_obj = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=2)
                qr_obj.add_data(link_wa)
                qr_obj.make(fit=True)
                qr_img = qr_obj.make_image(fill_color="black", back_color="white")
                nivel_escala = int(self.opcion_escala_qr.get())
                tamano_qr = int(nivel_escala * 30) 
                qr_procesado = qr_img.resize((tamano_qr, tamano_qr), Image.Resampling.NEAREST).convert("L")
                alto_qr_seccion = tamano_qr + 30 + espacio_qr_px 
            except Exception as e:
                pass

        alto_total = offset_y_logo + alto_texto + alto_qr_seccion + 20 
        img_base = Image.new("RGB", (ancho_ticket, alto_total), color="#FFFFCC")
        draw = ImageDraw.Draw(img_base)
        
        if logo_procesado:
            pos_x = (ancho_ticket - logo_procesado.width) // 2
            logo_mask = ImageOps.invert(logo_procesado)
            draw.bitmap((pos_x, 15), logo_mask, fill="black")

        draw.multiline_text((20, offset_y_logo), ticket, font=fuente, fill="black", spacing=3)

        if qr_procesado:
            y_qr_inicio = offset_y_logo + alto_texto + 10
            texto_wa = centrar("Contáctanos por WhatsApp:")
            draw.multiline_text((20, y_qr_inicio), texto_wa, font=fuente, fill="black", spacing=3)
            pos_x_qr = (ancho_ticket - qr_procesado.width) // 2
            qr_mask = ImageOps.invert(qr_procesado)
            offset_y_final = y_qr_inicio + 20 + espacio_qr_px
            draw.bitmap((pos_x_qr, offset_y_final), qr_mask, fill="black")

        seleccion_tamano = self.opcion_tamano.get()
        escala_y = 1
        if "B" in seleccion_tamano: escala_y = 2
        elif "C" in seleccion_tamano: escala_y = 3

        if escala_y > 1:
            nuevo_alto = img_base.height * escala_y
            try: metodo = Image.Resampling.NEAREST
            except AttributeError: metodo = Image.NEAREST
            self.img_final = img_base.resize((img_base.width, nuevo_alto), metodo)
        else:
            self.img_final = img_base

        ctk_img = ctk.CTkImage(light_image=self.img_final, dark_image=self.img_final, size=(self.img_final.width, self.img_final.height))
        self.lbl_vista_imagen.configure(image=ctk_img)
        self.lbl_vista_imagen.image = ctk_img
        self.evento_redimensionar(None)

    def evento_redimensionar(self, evento):
        if self.id_timer_resize is not None:
            self.after_cancel(self.id_timer_resize)
        self.id_timer_resize = self.after(100, self.ajustar_scrollbar)

    def ajustar_scrollbar(self):
        if not self.img_final: return
        try:
            altura_disponible = self.frame_scroll._parent_canvas.winfo_height()
            if altura_disponible < 100:
                self.update_idletasks()
                altura_disponible = self.frame_scroll._parent_canvas.winfo_height()
            if altura_disponible > 50: 
                if self.img_final.height > altura_disponible: self.frame_scroll._scrollbar.grid()
                else: self.frame_scroll._scrollbar.grid_remove()
        except Exception:
            pass

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

    def imprimir_prueba_fisica(self):
        if self.opcion_impresora.get() == "Seleccionar":
            messagebox.showwarning("Impresora no seleccionada", "Por favor selecciona una impresora real de la lista.", parent=self)
            return

        self.hardware.nombre_impresora = self.opcion_impresora.get()
        if not self.hardware.conectar():
            messagebox.showerror("Error de Hardware", f"No se pudo conectar con '{self.hardware.nombre_impresora}'.", parent=self)
            return

        try:
            p = self.hardware.impresora
            p._raw(b'\x1b\x40') 
            p._raw(b'\x1c\x2e') 
            p._raw(b'\x1b!\x00') 
            
            nombre = self.limpiar_texto(self.ent_nombre.get().strip().upper())
            direccion = self.limpiar_texto(self.ent_direccion.get().strip())
            telefono = self.limpiar_texto(self.ent_telefono.get().strip())
            despedida = self.limpiar_texto(self.ent_despedida.get().strip())

            seleccion_tamano = self.opcion_tamano.get()
            es_negrita = bool(self.check_negritas.get()) 
            
            if "B" in seleccion_tamano: comando_tamano = b'\x1d!\x01' 
            elif "C" in seleccion_tamano: comando_tamano = b'\x1d!\x02' 
            else: comando_tamano = b'\x1d!\x00' 

            # 🔥 Busca e imprime desde recursos 🔥
            if self.check_logo.get() and os.path.exists(self.ruta_logo):
                try:
                    p.set(align="left")
                    p.image(self.ruta_logo, impl="bitImageColumn")
                except Exception as e_logo:
                    print(f"⚠️ Aviso: Error imprimiendo logo en prueba: {e_logo}")

            if "Ahorro" in self.opcion_potencia.get():
                linea_iguales = "= = = = = = = = = = = = = = =\n"
                linea_guiones = "- - - - - - - - - - - - - - -\n"
            else:
                linea_iguales = "==============================\n"
                linea_guiones = "------------------------------\n"

            p.set(align="center", bold=True, double_height=True, double_width=True)
            if nombre: p.text(f"{nombre}\n")
            
            p._raw(b'\x1b!\x00')
            p.set(align="center", bold=es_negrita)
            p._raw(comando_tamano) 
            if direccion: p.text(f"{direccion}\n")
            if telefono: p.text(f"{telefono}\n")
            
            p.set(align="center", bold=es_negrita)
            p._raw(comando_tamano) 
            p.text(linea_iguales)
            p.text("TICKET DE PRUEBA\n")
            p.text(linea_iguales)
            
            p.set(align="left", bold=es_negrita)
            p._raw(comando_tamano) 
            p.text("1x Mica Cristal        $100.00\n")
            p.text("2x Funda Silicon       $250.00\n")
            p.text(linea_guiones)
            
            p.set(align="right", bold=es_negrita)
            p._raw(comando_tamano) 
            p.text("TOTAL:  $350.00\n")
            
            p.set(align="center", bold=es_negrita)
            p._raw(comando_tamano) 
            p.text(linea_iguales)
            
            if despedida: p.text(f"{despedida}\n")
            
            if self.check_qr.get():
                try:
                    numero_puro = ''.join(filter(str.isdigit, telefono))
                    if len(numero_puro) == 10: numero_puro = "52" + numero_puro
                    link_wa = f"https://wa.me/{numero_puro}?text=Hola"
                    p.set(align="center", bold=es_negrita)
                    p._raw(comando_tamano)
                    p.text("\nContáctanos por WhatsApp:\n")
                    
                    ESCALA_QR = int(self.opcion_escala_qr.get())
                    ESPACIO_QR = int(self.opcion_espacio_qr.get())
                    qr_obj = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=ESCALA_QR, border=2)
                    qr_obj.add_data(link_wa)
                    qr_obj.make(fit=True)
                    qr_img = qr_obj.make_image(fill_color="black", back_color="white").convert("RGBA")
                    ancho_impresora = 384
                    lienzo_qr = Image.new("RGB", (ancho_impresora, qr_img.height + ESPACIO_QR), "WHITE")
                    x_offset = (ancho_impresora - qr_img.width) // 2
                    lienzo_qr.paste(qr_img, (x_offset, ESPACIO_QR), qr_img)
                    
                    # 🔥 Guarda e imprime el QR de prueba desde recursos 🔥
                    lienzo_qr.convert("1").save(self.ruta_qr)
                    p.set(align="left")
                    p.image(self.ruta_qr, impl="bitImageColumn")
                    p.text("\n")
                except Exception as e_qr:
                    print(f"⚠️ Aviso: Error imprimiendo QR en prueba: {e_qr}")

            p.text("\n\n\n\n")

        except Exception as e:
            messagebox.showerror("Error", f"Fallo al imprimir:\n{e}", parent=self)
        finally:
            self.hardware.cerrar_conexion()

    def guardar_configuracion(self):
        try:
            nombre = self.ent_nombre.get().strip()
            direccion = self.ent_direccion.get().strip()
            telefono = self.ent_telefono.get().strip()
            despedida = self.ent_despedida.get().strip()
            tamano = self.opcion_tamano.get()
            
            negritas = 1 if self.check_negritas.get() else 0
            logo = 1 if self.check_logo.get() else 0
            qr = 1 if self.check_qr.get() else 0
            escala_qr = int(self.opcion_escala_qr.get())
            espacio_qr = int(self.opcion_espacio_qr.get())
            
            impresora_seleccionada = self.opcion_impresora.get()
            calidad_seleccionada = self.opcion_potencia.get() 

            if impresora_seleccionada == "Seleccionar":
                messagebox.showwarning("Atención", "Recuerda que debes seleccionar tu impresora de la lista para que el ticket físico se imprima.", parent=self)
            
            self.db.actualizar_config_ticket(nombre, direccion, telefono, despedida, tamano, negritas, logo, qr, escala_qr, espacio_qr, impresora_seleccionada, calidad_seleccionada)
            
            messagebox.showinfo("¡Guardado Exitoso!", f"El diseño del ticket y la impresora se han actualizado.", parent=self)
            self.destroy() 
            
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un problema al guardar:\n{e}", parent=self)