from django.db import models

# Create your models here.
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
