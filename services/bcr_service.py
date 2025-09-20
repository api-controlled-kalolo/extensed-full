import requests
from datetime import datetime, date
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class BCRService:
    """
    Servicio para consultar el tipo de cambio del BCR (Banco Central de Reserva del Perú)
    API Documentation: https://estadisticas.bcrp.gob.pe/estadisticas/series/ayuda/api
    """
    
    BASE_URL = "https://estadisticas.bcrp.gob.pe/estadisticas/series/api"
    TIPO_CAMBIO_SERIE = "PD04637PD"  # Serie del tipo de cambio (compra interbancario)
    DEFAULT_TIPO_CAMBIO = Decimal("3.750")  # Fallback si la API falla
    MARGEN_SEGURIDAD = Decimal("0.10")  # Margen adicional de 0.10
    
    @classmethod
    def obtener_tipo_cambio_actual(cls, con_margen=True):
        """
        Obtiene el tipo de cambio del día actual desde la API del BCR
        
        Args:
            con_margen (bool): Si agregar el margen de seguridad de 0.10
            
        Returns:
            Decimal: Tipo de cambio USD -> PEN
        """
        try:
            # Obtener fecha actual en formato requerido por la API
            fecha_actual = date.today()
            fecha_str = fecha_actual.strftime("%Y")  # Solo año para obtener datos recientes
            
            # Construir URL de la API
            url = f"{cls.BASE_URL}/{cls.TIPO_CAMBIO_SERIE}/{fecha_str}"
            
            # Headers recomendados
            headers = {
                'User-Agent': 'SVC-INGENIEROS-COTIZADOR/1.0',
                'Accept': 'application/json'
            }
            
            # Realizar petición con timeout
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Validar que la respuesta no esté vacía
            if not response.text.strip():
                logger.warning("Respuesta vacía del BCR")
                return cls._obtener_fallback(con_margen)
            
            # Procesar respuesta JSON
            try:
                data = response.json()
            except ValueError as json_error:
                logger.error(f"Error parseando JSON del BCR: {json_error}. Respuesta: {response.text[:200]}")
                return cls._obtener_fallback(con_margen)
            
            if 'periods' in data and data['periods']:
                # Obtener el último valor disponible
                periodos = data['periods']
                ultimo_periodo = periodos[-1]
                
                if 'values' in ultimo_periodo and ultimo_periodo['values']:
                    ultimo_valor = ultimo_periodo['values'][0]
                    tipo_cambio = Decimal(str(ultimo_valor))
                    
                    # Agregar margen de seguridad si se solicita
                    if con_margen:
                        tipo_cambio += cls.MARGEN_SEGURIDAD
                    
                    logger.info(f"Tipo de cambio obtenido del BCR: {tipo_cambio}")
                    return tipo_cambio.quantize(Decimal("0.001"))
            
            # Si no hay datos disponibles, usar fallback
            logger.warning("No se encontraron datos de tipo de cambio en la respuesta del BCR")
            return cls._obtener_fallback(con_margen)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de conexión con API del BCR: {e}")
            return cls._obtener_fallback(con_margen)
        except (ValueError, KeyError, IndexError) as e:
            logger.error(f"Error procesando respuesta del BCR: {e}")
            return cls._obtener_fallback(con_margen)
        except Exception as e:
            logger.error(f"Error inesperado consultando BCR: {e}")
            return cls._obtener_fallback(con_margen)
    
    @classmethod
    def obtener_tipo_cambio_fecha(cls, fecha, con_margen=True):
        """
        Obtiene el tipo de cambio de una fecha específica
        
        Args:
            fecha (date): Fecha a consultar
            con_margen (bool): Si agregar el margen de seguridad de 0.10
            
        Returns:
            Decimal: Tipo de cambio USD -> PEN
        """
        try:
            # Formatear fecha para la API (YYYY-MM-DD)
            fecha_str = fecha.strftime("%Y-%m-%d")
            
            # Construir URL para fecha específica
            url = f"{cls.BASE_URL}/{cls.TIPO_CAMBIO_SERIE}/{fecha_str}/{fecha_str}"
            
            headers = {
                'User-Agent': 'SVC-INGENIEROS-COTIZADOR/1.0',
                'Accept': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'periods' in data and data['periods']:
                periodo = data['periods'][0]
                if 'values' in periodo and periodo['values']:
                    valor = periodo['values'][0]
                    tipo_cambio = Decimal(str(valor))
                    
                    if con_margen:
                        tipo_cambio += cls.MARGEN_SEGURIDAD
                    
                    logger.info(f"Tipo de cambio para {fecha_str}: {tipo_cambio}")
                    return tipo_cambio.quantize(Decimal("0.001"))
            
            logger.warning(f"No se encontró tipo de cambio para la fecha {fecha_str}")
            return cls._obtener_fallback(con_margen)
            
        except Exception as e:
            logger.error(f"Error consultando tipo de cambio para {fecha}: {e}")
            return cls._obtener_fallback(con_margen)
    
    @classmethod
    def _obtener_fallback(cls, con_margen=True):
        """
        Retorna el tipo de cambio por defecto cuando la API no está disponible
        
        Args:
            con_margen (bool): Si agregar el margen de seguridad
            
        Returns:
            Decimal: Tipo de cambio por defecto
        """
        tipo_cambio = cls.DEFAULT_TIPO_CAMBIO
        
        if con_margen:
            tipo_cambio += cls.MARGEN_SEGURIDAD
        
        logger.info(f"Usando tipo de cambio por defecto: {tipo_cambio}")
        return tipo_cambio
    
    @classmethod
    def verificar_conexion(cls):
        """
        Verifica si la API del BCR está disponible
        
        Returns:
            bool: True si la API responde correctamente
        """
        try:
            url = f"{cls.BASE_URL}/{cls.TIPO_CAMBIO_SERIE}/2024"
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except:
            return False


# Función de conveniencia para usar en los modelos
def obtener_tipo_cambio_bcr():
    """
    Función de conveniencia para obtener el tipo de cambio actual del BCR
    con margen de seguridad incluido
    """
    return BCRService.obtener_tipo_cambio_actual(con_margen=True)