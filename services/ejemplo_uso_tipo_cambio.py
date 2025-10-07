"""
Script de prueba para verificar el servicio de tipo de cambio
Ejecutar con: python services/ejemplo_uso_tipo_cambio.py
"""

import sys
import os

# Agregar el directorio raíz al path para poder importar el servicio
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.tipo_cambio_service import TipoCambioService

def main():
    print("=" * 60)
    print("VERIFICACIÓN DEL SERVICIO DE TIPO DE CAMBIO")
    print("=" * 60)
    print()
    
    # 1. Obtener tipo de cambio actual
    print("1. Obteniendo tipo de cambio actual con margen...")
    tipo_cambio = TipoCambioService.obtener_tipo_cambio(con_margen=True)
    print(f"   Tipo de cambio USD -> PEN: {tipo_cambio}")
    print()
    
    # 2. Obtener sin margen
    print("2. Obteniendo tipo de cambio sin margen...")
    tipo_cambio_sin_margen = TipoCambioService.obtener_tipo_cambio(con_margen=False)
    print(f"   Tipo de cambio USD -> PEN (sin margen): {tipo_cambio_sin_margen}")
    print(f"   Diferencia (margen): {tipo_cambio - tipo_cambio_sin_margen}")
    print()
    
    # 3. Verificar estado de todas las fuentes
    print("3. Verificando estado de todas las fuentes...")
    print("-" * 60)
    estado = TipoCambioService.verificar_fuentes()
    
    for fuente, info in estado.items():
        disponible = "✓ DISPONIBLE" if info.get('disponible') else "✗ NO DISPONIBLE"
        print(f"   {fuente:20s} {disponible}")
        
        if info.get('disponible'):
            valor = info.get('valor')
            if valor:
                print(f"   {'':20s} Valor: {valor:.3f}")
        else:
            error = info.get('error', 'Sin detalles')
            print(f"   {'':20s} Error: {error[:50]}")
        print()
    
    print("=" * 60)
    print("RESUMEN")
    print("=" * 60)
    fuentes_ok = sum(1 for info in estado.values() if info.get('disponible'))
    total_fuentes = len(estado)
    print(f"Fuentes disponibles: {fuentes_ok}/{total_fuentes}")
    print(f"Tipo de cambio final (con margen): {tipo_cambio}")
    print()
    
    if fuentes_ok == 0:
        print("⚠️  ADVERTENCIA: Ninguna fuente está disponible.")
        print("   Se está usando el valor por defecto.")
    elif fuentes_ok < total_fuentes:
        print("ℹ️  INFORMACIÓN: Algunas fuentes no están disponibles.")
        print("   El servicio está funcionando con respaldo.")
    else:
        print("✓ ÉXITO: Todas las fuentes están disponibles.")
    
    print("=" * 60)

if __name__ == '__main__':
    main()
