"""
Servicio robusto de tipo de cambio con múltiples fuentes de respaldo
Prioridad:
1. SUNAT (oficial para Perú)
2. BCR (Banco Central de Reserva del Perú)
3. DolarPe API (actualizado en tiempo real)
4. ExchangeRate-API (respaldo internacional)
5. Valor por defecto
"""
import requests
from datetime import datetime, date
from decimal import Decimal
import logging
import json

logger = logging.getLogger(__name__)


class TipoCambioService:
    """Servicio multi-fuente para obtener tipo de cambio USD -> PEN"""
    
    # Margen de seguridad para cotizaciones
    MARGEN_SEGURIDAD = Decimal("0.10")
    
    # Valor por defecto (actualizado manualmente según mercado)
    DEFAULT_TIPO_CAMBIO = Decimal("3.75")
    
    @classmethod
    def obtener_tipo_cambio(cls, con_margen=True):
        """
        Obtiene el tipo de cambio USD -> PEN intentando múltiples fuentes
        
        Args:
            con_margen (bool): Si agregar margen de seguridad de 0.10
            
        Returns:
            Decimal: Tipo de cambio con 3 decimales
        """
        # Intentar fuentes en orden de prioridad
        fuentes = [
            cls._obtener_de_sunat,
            cls._obtener_de_bcr,
            cls._obtener_de_dolarpe,
            cls._obtener_de_exchangerate_api,
        ]
        
        for fuente in fuentes:
            try:
                tipo_cambio = fuente()
                if tipo_cambio and tipo_cambio > 0:
                    logger.info(f"Tipo de cambio obtenido de {fuente.__name__}: {tipo_cambio}")
                    
                    if con_margen:
                        tipo_cambio += cls.MARGEN_SEGURIDAD
                    
                    return tipo_cambio.quantize(Decimal("0.001"))
            except Exception as e:
                logger.warning(f"Error en {fuente.__name__}: {e}")
                continue
        
        # Si todas las fuentes fallan, usar valor por defecto
        logger.warning("Todas las fuentes fallaron, usando tipo de cambio por defecto")
        return cls._obtener_fallback(con_margen)
    
    @classmethod
    def _obtener_de_sunat(cls):
        """
        Obtiene tipo de cambio de SUNAT (Fuente oficial para Perú)
        Endpoint: https://api.apis.net.pe/v1/tipo-cambio-sunat
        """
        try:
            url = "https://api.apis.net.pe/v1/tipo-cambio-sunat"
            headers = {
                'User-Agent': 'Mozilla/5.0',
                'Accept': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=8)
            response.raise_for_status()
            
            data = response.json()
            
            # SUNAT devuelve: {"compra": 3.745, "venta": 3.748, ...}
            # Usamos el precio de venta (más conservador para cotizaciones)
            if 'venta' in data:
                tipo_cambio = Decimal(str(data['venta']))
                logger.info(f"SUNAT - Compra: {data.get('compra')}, Venta: {data.get('venta')}")
                return tipo_cambio
            
            return None
            
        except Exception as e:
            logger.error(f"Error consultando SUNAT: {e}")
            return None
    
    @classmethod
    def _obtener_de_bcr(cls):
        """
        Obtiene tipo de cambio del BCR (Banco Central de Reserva del Perú)
        API: https://estadisticas.bcrp.gob.pe/estadisticas/series/api
        """
        try:
            # Serie del tipo de cambio (compra interbancario)
            serie = "PD04637PD"
            fecha_actual = date.today()
            anio = fecha_actual.strftime("%Y")
            
            url = f"https://estadisticas.bcrp.gob.pe/estadisticas/series/api/{serie}/{anio}"
            headers = {
                'User-Agent': 'SVC-INGENIEROS/1.0',
                'Accept': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            if not response.text.strip():
                return None
            
            data = response.json()
            
            if 'periods' in data and data['periods']:
                periodos = data['periods']
                # Buscar el último valor disponible
                for periodo in reversed(periodos):
                    if 'values' in periodo and periodo['values']:
                        ultimo_valor = periodo['values'][0]
                        tipo_cambio = Decimal(str(ultimo_valor))
                        return tipo_cambio
            
            return None
            
        except Exception as e:
            logger.error(f"Error consultando BCR: {e}")
            return None
    
    @classmethod
    def _obtener_de_dolarpe(cls):
        """
        Obtiene tipo de cambio de DolarPe API (actualizado en tiempo real)
        Endpoint: https://dolarapi.com/v1/dolares
        """
        try:
            url = "https://dolarapi.com/v1/dolares/oficial"
            headers = {
                'User-Agent': 'Mozilla/5.0',
                'Accept': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=8)
            response.raise_for_status()
            
            data = response.json()
            
            # La API devuelve: {"compra": 3.74, "venta": 3.75, ...}
            # Usamos venta para cotizaciones
            if 'venta' in data:
                tipo_cambio = Decimal(str(data['venta']))
                return tipo_cambio
            
            return None
            
        except Exception as e:
            logger.error(f"Error consultando DolarPe: {e}")
            return None
    
    @classmethod
    def _obtener_de_exchangerate_api(cls):
        """
        Obtiene tipo de cambio de ExchangeRate-API (respaldo internacional)
        Endpoint: https://api.exchangerate-api.com/v4/latest/USD
        """
        try:
            url = "https://api.exchangerate-api.com/v4/latest/USD"
            headers = {
                'User-Agent': 'Mozilla/5.0',
                'Accept': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=8)
            response.raise_for_status()
            
            data = response.json()
            
            # La API devuelve: {"rates": {"PEN": 3.75, ...}}
            if 'rates' in data and 'PEN' in data['rates']:
                tipo_cambio = Decimal(str(data['rates']['PEN']))
                return tipo_cambio
            
            return None
            
        except Exception as e:
            logger.error(f"Error consultando ExchangeRate-API: {e}")
            return None
    
    @classmethod
    def _obtener_fallback(cls, con_margen=True):
        """
        Retorna el tipo de cambio por defecto cuando todas las APIs fallan
        
        Args:
            con_margen (bool): Si agregar margen de seguridad
            
        Returns:
            Decimal: Tipo de cambio por defecto
        """
        tipo_cambio = cls.DEFAULT_TIPO_CAMBIO
        
        if con_margen:
            tipo_cambio += cls.MARGEN_SEGURIDAD
        
        logger.warning(f"Usando tipo de cambio por defecto: {tipo_cambio}")
        return tipo_cambio.quantize(Decimal("0.001"))
    
    @classmethod
    def verificar_fuentes(cls):
        """
        Verifica el estado de todas las fuentes
        
        Returns:
            dict: Estado de cada fuente {nombre: bool}
        """
        estado = {}
        
        fuentes = [
            ('SUNAT', cls._obtener_de_sunat),
            ('BCR', cls._obtener_de_bcr),
            ('DolarPe', cls._obtener_de_dolarpe),
            ('ExchangeRate-API', cls._obtener_de_exchangerate_api),
        ]
        
        for nombre, funcion in fuentes:
            try:
                resultado = funcion()
                estado[nombre] = {
                    'disponible': resultado is not None,
                    'valor': float(resultado) if resultado else None
                }
            except Exception as e:
                estado[nombre] = {
                    'disponible': False,
                    'error': str(e)
                }
        
        return estado


# Función de conveniencia para usar en los modelos
def obtener_tipo_cambio_actual():
    """
    Función de conveniencia para obtener el tipo de cambio actual
    con margen de seguridad incluido
    
    Returns:
        Decimal: Tipo de cambio USD -> PEN con margen
    """
    return TipoCambioService.obtener_tipo_cambio(con_margen=True)
