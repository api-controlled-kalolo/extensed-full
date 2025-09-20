from django.core.management.base import BaseCommand
from ventas.models import Cotizacion
from services.bcr_service import BCRService


class Command(BaseCommand):
    help = 'Actualiza el tipo de cambio de todas las cotizaciones activas usando la API del BCR'

    def add_arguments(self, parser):
        parser.add_argument(
            '--solo-vacias',
            action='store_true',
            help='Solo actualiza cotizaciones que no tienen tipo de cambio definido',
        )
        parser.add_argument(
            '--estado',
            type=str,
            default='En Negociación',
            help='Estado de cotizaciones a actualizar (default: "En Negociación")',
        )

    def handle(self, *args, **options):
        self.stdout.write('Iniciando actualización de tipos de cambio...')
        
        # Verificar conexión con BCR
        if not BCRService.verificar_conexion():
            self.stdout.write(
                self.style.WARNING('⚠️  API del BCR no disponible. Se usará tipo de cambio por defecto.')
            )
        
        # Filtrar cotizaciones
        cotizaciones = Cotizacion.objects.filter(estado_coti=options['estado'])
        
        if options['solo_vacias']:
            cotizaciones = cotizaciones.filter(tipo_cambio__isnull=True)
        
        total_cotizaciones = cotizaciones.count()
        
        if total_cotizaciones == 0:
            self.stdout.write(
                self.style.WARNING('No se encontraron cotizaciones para actualizar.')
            )
            return
        
        self.stdout.write(
            f'Se actualizarán {total_cotizaciones} cotizaciones...'
        )
        
        actualizadas = 0
        errores = 0
        
        for cotizacion in cotizaciones:
            try:
                tipo_cambio_anterior = cotizacion.tipo_cambio
                nuevo_tipo_cambio = cotizacion.actualizar_tipo_cambio()
                cotizacion.save(update_fields=['tipo_cambio'])
                
                self.stdout.write(
                    f'✅ {cotizacion.numero_cotizacion}: {tipo_cambio_anterior} → {nuevo_tipo_cambio}'
                )
                actualizadas += 1
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'❌ Error actualizando {cotizacion.numero_cotizacion}: {e}'
                    )
                )
                errores += 1
        
        # Resumen
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'✅ Actualizadas: {actualizadas}'))
        if errores > 0:
            self.stdout.write(self.style.ERROR(f'❌ Errores: {errores}'))
        
        self.stdout.write('Proceso completado.')