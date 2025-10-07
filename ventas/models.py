from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from datetime import datetime
from services.tipo_cambio_service import obtener_tipo_cambio_actual

# Create your models here.
# -- ACTAS --
class ActaServicioTecnico(models.Model):
    # 1. Información de la Orden
    numero_acta = models.CharField(max_length=20, unique=True, null=True, blank= True,help_text="Identificador único del Acta")
    fecha_acta = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    sot = models.IntegerField(default=0)
    numero_cintillo = models.IntegerField(default=0,blank=True)
    plano = models.CharField(max_length=20)
    validacion = models.IntegerField(default=0)
    fat = models.CharField(max_length=50, blank=True)
    numero_borne_fat = models.IntegerField(default=0,blank=True)
    
    # 2.INFORMACIÓN DEL CLIENTE
    razon_social = models.CharField(max_length=50)
    direccion = models.CharField(max_length=150)
    cod_cliente = models.CharField(max_length=20)
    telefono = models.CharField(max_length=9)
    provincia = models.CharField(max_length=30)
    distrito = models.CharField(max_length=30)
    titular = models.BooleanField(default=False, blank=True)
    otros = models.BooleanField(default=False, blank=True)
    usuario = models.BooleanField(default=False, blank=True)
    relacion_titular = models.CharField(max_length=15, blank=True)
    cliente_buena_brinda = models.BooleanField(default=False)
    cliente_mala_brinda = models.BooleanField(default=False)
    
    # 3.SERVICIO TÉCNICO
    # 3.1 Personal Tecnico T1/T2 (Nombres apellidos)
    t1_lider = models.CharField(max_length=30)
    t2_apoyo = models.CharField(max_length=30)
    t_adicional = models.CharField(max_length=30, blank=True)
    
    # 3.3 PLATAFORMA (Aplica para residencias y Claro empresas)
    HFC = models.BooleanField(default=False, blank=True)
    FTTH = models.BooleanField(default=False, blank=True)
    LTE = models.BooleanField(default=False, blank=True)
    DTH = models.BooleanField(default=False, blank=True)
    Otro = models.BooleanField(default=False, blank=True)
    Otro_text = models.CharField(max_length=20, blank=True)
    Plan = models.CharField(max_length=20, blank=True)
    
    # 3.4 SERVICIO REALIZADO
    instalacion = models.BooleanField(default=False, blank=True)
    post_venta = models.BooleanField(default=False, blank=True)
    cambio_de_plan = models.BooleanField(default=False, blank=True) # Cambio de nombre
    migracion = models.BooleanField(default=False, blank=True) # Cambio de nombre
    traslado_externo = models.BooleanField(default=False, blank=True)
    traslado_interno = models.BooleanField(default=False, blank=True) # nuevos
    traslado_acometida = models.BooleanField(default=False, blank=True) # nuevos
    retiro = models.BooleanField(default=False, blank=True) # nuevos
    
    # 3.5 MATERIALES EMPLEADOS 1
    Coaxial_c_mens_RG6 = models.IntegerField(default=0, blank=True)
    Coaxial_s_mens_RG6 = models.IntegerField(default=0, blank=True)
    cable_telefonico = models.IntegerField(default=0, blank=True)
    cable_utp = models.IntegerField(default=0, blank=True)
    cable_sc_APC = models.IntegerField(default=0, blank=True)
    conector_rj11 = models.IntegerField(default=0, blank=True)
    conector_rj45 = models.IntegerField(default=0, blank=True)
    conector_rg6 = models.IntegerField(default=0, blank=True)
    conector_opt = models.IntegerField(default=0, blank=True)
    anclaje_p = models.IntegerField(default=0, blank=True)
    control_remoto = models.IntegerField(default=0, blank=True)
    cable_hdmi = models.IntegerField(default=0, blank=True)
    roseta_telef = models.IntegerField(default=0, blank=True)
    roseta_optica = models.IntegerField(default=0, blank=True)
    chapa_q = models.IntegerField(default=0, blank=True)
    cable_fibra_drop = models.CharField(choices=[('50M','50M'),('80M','80M'),('100M','100M'),('150M','150M'),('','-')], blank=True, max_length=20)
    divisor = models.CharField(choices=[('2V','2V'), ('3V','3V'),('4V','4V'),('','-')], blank=True, max_length=20)
    otros_material = models.CharField(max_length=120, blank=True)
    
    # 3.6 MATERIALES EMPLEADOS 2
    grapas_pared = models.IntegerField(default=0, blank=True)
    anclaje_p = models.IntegerField(default=0, blank=True)
    cinta_aislante = models.IntegerField(default=0, blank=True)
    cinta_doble_contacto = models.IntegerField(default=0, blank=True)
    alcohol_isopropilico = models.IntegerField(default=0, blank=True)
    panos_secos = models.IntegerField(default=0, blank=True)
    otros_material2 = models.CharField(max_length=100, blank=True)
    
    # IV. INFORMACIÓN TÉCNICA
    # 4.1 NIVELES
    down_stream_rx_ont = models.CharField(max_length=50, blank=True)
    up_stream_tx_ont = models.CharField(max_length=50, blank=True)
    sinr = models.CharField(max_length=50, blank=True)
    rsrp = models.CharField(max_length=50, blank=True)
    # 4.2 SVA
    hunting = models.BooleanField(default=False, blank=True)
    ip_fija = models.BooleanField(default=False, blank=True)
    central_virtual = models.BooleanField(default=False, blank=True)
    post_forwarding = models.BooleanField(default=False, blank=True)
    ip_text = models.CharField(max_length=20, blank=True)
    # 4.3 WIFI
    SSID_2_4_GHZ = models.CharField(max_length=20, blank=True)
    SSID_5_GHZ = models.CharField(max_length=20, blank=True)
    
    # V. LLENAR SOLO EN CASO DE MANTENIMIENTO / RECLAMO POR CALIDAD (OBLIGATORIO)
    # 5.1 INCOVENIENTE
    incoveniente_texto = models.TextField(blank=True)
    # 5.3. Factibilidad de solucion (Llenado por el personal tecnico) 
    incoveniente_solucionado = models.CharField(choices=[('SI','SI'), ('NO', 'NO'), ('','-')], blank=True, max_length=10)
    indicar_porque = models.TextField(blank=True)
    
    # VI. COMENTARIOS Y OBSERVACIONES DEL SERVICIO (LLENADO POR EL PERSONAL TECNICO)
    comentarios_texto = models.TextField(blank=True)
    
    # VII. CONFORMIDAD DEL SERVICIO
    nombre_tecnico = models.CharField(max_length=20, null=False)
    dni_tecnico = models.CharField(max_length=10, null=False)
    el_cliente_nego_acta = models.BooleanField(default=False)
    motivo_texto = models.TextField(blank=True)
    
    # Para guardarlo con un codigo aleatoreo
    def save(self, *args, **kwargs):
        if not self.pk and not self.numero_acta:
            # Aún no existe en BD, pero no tenemos pk para usar en el código
            super().save(*args, **kwargs)  # Guardar para obtener pk
            self.numero_acta = f"ACT-{self.pk:06d}"
            return super().save(update_fields=["numero_acta"])
        return super().save(*args, **kwargs)

class Equipos_ActaServicioTecnico(models.Model):
    acta_principal = models.ForeignKey(ActaServicioTecnico,on_delete=models.CASCADE, related_name='equipos')
    label_i = models.CharField(max_length=10, blank=True)
    label_r = models.CharField(max_length=10, blank=True)
    desc = models.CharField(max_length=30, blank=True)
    marca = models.CharField(max_length=10, blank=True)
    modelo = models.CharField(max_length=10, blank=True)
    serie = models.CharField(max_length=10, blank=True)
    mac_pon = models.CharField(max_length=10, blank=True)
    ua = models.CharField(max_length=10, blank=True)
    datos_tv = models.CharField(max_length=10, blank=True)

class Acciones_ActaServicioTecnico(models.Model):
    acta_principal = models.ForeignKey(ActaServicioTecnico, on_delete=models.CASCADE, related_name='acciones')
    codigo = models.CharField(max_length=20, blank=True)
    acciones_text = models.CharField(max_length=50, blank=True)


class UnidadNegocio(models.Model):
    codigo = models.CharField(blank=False, unique=True, null=False, max_length=20)
    nombre = models.CharField(blank=False, unique=True, null=False, max_length=50)
    
    def __str__(self):
        # Elige el formato que quieras mostrar en el select:
        # Solo nombre:
        # return self.nombre
        # Código + nombre (mi favorito):
        return f"{self.codigo} — {self.nombre}"
    
    def save(self, *args, **kwargs):
        if not self.pk and not self.codigo:
            super().save(*args, **kwargs)
            self.codigo = f"UN-00{self.pk:01d}"
            return super().save(update_fields=["codigo"])
        return super().save(*args, **kwargs)
    
# -- PROYECTO --
class Proyecto(models.Model):
    codigo = models.CharField(blank=False, unique=True, null=False, max_length=20)
    nombre = models.CharField(blank=False, null=False, max_length=20)
    
    #Relacion
    unidad_negocio_principal = models.ForeignKey(UnidadNegocio, on_delete=models.CASCADE, related_name='unidad_negocio')
    
    def save(self, *args, **kwargs):
        if not self.pk and not self.codigo:
            super().save(*args, **kwargs)
            self.codigo = f"P-00{self.pk:01d}"
            return super().save(update_fields=["codigo"])
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre}"


class Cliente(models.Model):
    proyecto_principal = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='clientes')
    codigo = models.CharField(blank=False, unique=True, null=False, max_length=20)
    ruc = models.CharField(blank=False, unique=True, null=False, max_length=20)
    razon_social = models.CharField(blank=False, null=False, max_length=20)
    direccion = models.CharField(blank=False, null=False, max_length=50)
    distrito = models.CharField(blank=False, null=False, max_length=20)
    provincia = models.CharField(blank=False, null=False, max_length=25)
    
    def save(self, *args, **kwargs):
        if not self.pk and not self.codigo:
            super().save(*args, **kwargs)
            self.codigo = f"CLI-00{self.pk:01d}"
            return super().save(update_fields=["codigo"])
        return super().save(*args, **kwargs)

    def __str__(self):
        # Mostrar razón social y RUC en selects
        return f"{self.razon_social} ({self.ruc})"

class Contacto(models.Model):
    cliente_principal = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='contacto')
    apellidos = models.CharField(blank=False, null=False, max_length=20)
    nombres = models.CharField(blank=False,  null=False, max_length=20)
    cargo = models.CharField(blank=False, null=False, max_length=20)
    correo = models.EmailField(blank=False)
    Celular = models.CharField(max_length=9, blank=False)
    Sede = models.CharField(blank=False, null=False, max_length=20)

    def __str__(self):
        # Mostrar nombre completo y cargo
        return f"{self.nombres} {self.apellidos} - {self.cargo}"
    
# -- COTIZACIONES --
class Cotizacion(models.Model):
    numero_cotizacion = models.CharField(max_length=20, unique=True, null=False, blank=False, help_text="Identificador unico para generar las cotizaciones, formato a seguir: 'COT[numero][año]'") # Completado automático por el sistema
    nombre_cotizacion = models.CharField(max_length=50, blank=False, null=False) # Dato ingresado manualmente
    ruc = models.CharField(max_length=30, blank=False, null=False) # Sistema lo determina
    razon_social = models.CharField(max_length=30, blank=False) # Sistema lo determina
    fecha_creacion = models.DateField(auto_now_add=True) # Sistema lo determina
    celular = models.CharField(max_length=9, blank=False, null=False) # Lista desplegable
    direccion = models.CharField(max_length=50, blank=False, null=False) # Lista desplegable
    correo = models.EmailField(blank=False) # Lista desplegable
    forma_pago = models.CharField(max_length=20, choices=[('','-'),('15 dias','15 dias'),('21 dias', '21 dias'),('30 dias', '30 dias'),('45 dias', '45 dias'), ('60 dias', '60 dias')], blank=True)
    validez_oferta = models.CharField(max_length=20, choices=[('','-'),('15 dias','15 dias'),('21 dias', '21 dias'),('30 dias', '30 dias'),('45 dias', '45 dias'), ('60 dias', '60 dias')], blank=False)
    moneda = models.CharField(max_length=10, choices=[('','-'),('Soles', 'Soles'), ('Dolares','Dolares')], blank=False)
    tipo_cambio = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True, help_text="Tipo de cambio USD a PEN (se actualiza automáticamente desde BCR + 0.10)")
    incluye_igv = models.BooleanField(default=True, help_text="Si la cotización incluye IGV (18%)")
    alcance_total_oferta = models.TextField()
    estado_coti = models.CharField(max_length=20, choices=[('', '-'), ('En Negociación', 'En Negociación'),('Ganado', 'Ganado'), ('Perdida', 'Perdida')], default='En Negociación')
    fecha_actualizacion_estado = models.DateTimeField(auto_now_add=True)
    #Relaciones
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='cotizaciones',)
    contacto = models.ForeignKey(Contacto, on_delete=models.CASCADE, related_name='cotizaciones_contacto', )
    
    def obtener_tipo_cambio_actual(self):
        """
        Obtiene el tipo de cambio actual con múltiples fuentes de respaldo
        """
        try:
            return obtener_tipo_cambio_actual()
        except Exception:
            return Decimal("3.850")  # Fallback seguro
    
    def actualizar_tipo_cambio(self):
        """
        Actualiza el tipo de cambio con el valor actual usando múltiples fuentes
        """
        try:
            self.tipo_cambio = self.obtener_tipo_cambio_actual()
            return self.tipo_cambio
        except Exception:
            # Si falla, mantener el tipo de cambio actual o usar fallback
            if not self.tipo_cambio:
                self.tipo_cambio = Decimal("3.850")
            return self.tipo_cambio
    
    @property
    def tipo_cambio_efectivo(self):
        """
        Retorna el tipo de cambio a usar (actualizado o por defecto)
        """
        if not self.tipo_cambio:
            # Si no hay tipo de cambio guardado, obtener uno nuevo
            try:
                return self.obtener_tipo_cambio_actual()
            except Exception:
                # Si falla la obtención del tipo de cambio, usar un valor por defecto
                return Decimal("3.760")  # Tipo de cambio por defecto + margen
        return self.tipo_cambio
    
    @property
    def subtotal(self):
        """Subtotal de todos los detalles (sin IGV)"""
        total = Decimal("0.00")
        for detalle in self.detalles.all():
            total += detalle.precio_total
        return total.quantize(Decimal("0.01"))
    
    @property
    def igv_monto(self):
        """Monto del IGV (18%)"""
        if self.incluye_igv:
            igv = self.subtotal * Decimal("0.18")
            return igv.quantize(Decimal("0.01"))
        return Decimal("0.00")
    
    @property 
    def total_con_igv(self):
        """Total con IGV incluido"""
        if self.incluye_igv:
            return (self.subtotal + self.igv_monto).quantize(Decimal("0.01"))
        return self.subtotal
    
    @property
    def total_soles(self):
        """Total siempre en soles (convierte si está en dólares)"""
        total = self.total_con_igv
        if self.moneda == 'Dolares':
            tipo_cambio = Decimal(str(self.tipo_cambio_efectivo))
            total_convertido = total * tipo_cambio
            return total_convertido.quantize(Decimal("0.01"))
        return total
    
    @property
    def total_dolares(self):
        """Total siempre en dólares (convierte si está en soles)"""
        total = self.total_con_igv
        if self.moneda == 'Soles':
            tipo_cambio = Decimal(str(self.tipo_cambio_efectivo))
            total_convertido = total / tipo_cambio
            return total_convertido.quantize(Decimal("0.01"))
        return total
    
    def __str__(self):
        return f"{self.numero_cotizacion} - {self.nombre_cotizacion}"
    
    
    def save(self, *args, **kwargs):
        # Actualizar tipo de cambio al crear una nueva cotización
        if not self.pk:
            # Nueva cotización: obtener tipo de cambio actual del BCR
            if not self.tipo_cambio:
                self.tipo_cambio = self.obtener_tipo_cambio_actual()
        
        # Generar número de cotización y datos de empresa
        if not self.pk and not self.numero_cotizacion:
            super().save(*args, **kwargs)
            self.numero_cotizacion = f"COT00{self.pk:02d}{datetime.now().year}"
            self.ruc = f"20607494283"
            self.razon_social = f"SVC INGENIEROS S.A.C"
            self.direccion = f"Comas, Lima, Lima"
            return super().save(update_fields=["numero_cotizacion", "ruc", "razon_social", "direccion", "tipo_cambio"])
        
        return super().save(*args, **kwargs)
    
class Detalles_Cotizacion(models.Model):
    cotizacion_principal = models.ForeignKey(Cotizacion, on_delete=models.CASCADE, related_name='detalles')
    descripcion = models.TextField(blank=False, help_text="Ingrese la descripción de la Cotización") # Ingreso Manual
    unidad = models.CharField(choices=[('','-- Selecciona --'),('UNIDAD','UNIDAD'),('DECENA', 'DECENA')], blank=False) # Ingreso Manual
    cantidad = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(300)]) # Ingreso Manual
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, default=0) # Ingreso Manual

    @property
    def precio_total(self):
        try:
            if self.cantidad is None or self.precio_unitario is None:
                return Decimal('0.00')
            
            cantidad = Decimal(str(self.cantidad))
            precio = Decimal(str(self.precio_unitario))
            total = cantidad * precio
            return total.quantize(Decimal("0.01"))
        except (TypeError, ValueError, AttributeError):
            return Decimal('0.00')
    
    def get_precio_total_safe(self):
        """Método más seguro para obtener el precio total"""
        try:
            cantidad = getattr(self, 'cantidad', 0) or 0
            precio_unitario = getattr(self, 'precio_unitario', 0) or 0
            
            if cantidad and precio_unitario:
                return float(cantidad) * float(precio_unitario)
            return 0.00
        except:
            return 0.00
    
    def __str__(self):
        try:
            return f"{self.descripcion} x {self.cantidad} = {self.precio_total}"
        except:
            return f"{self.descripcion or 'Sin descripción'}"