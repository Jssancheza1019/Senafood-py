from django.db import models
from django.utils import timezone
from datetime import date


class Inventario(models.Model):
    id_inventario                = models.AutoField(primary_key=True)
    nombre                       = models.CharField(max_length=255, blank=True, null=True)
    idproducto                   = models.IntegerField(blank=True, null=True)
    ubicacion                    = models.CharField(max_length=255, blank=True, null=True)
    stocktotal                   = models.IntegerField(db_column='stockTotal', blank=True, null=True)
    costouni                     = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    valor_total                  = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    capacidad_maxima             = models.IntegerField()
    alerta_minimos               = models.IntegerField()
    responsable                  = models.CharField(max_length=255, blank=True, null=True)
    ultima_revision              = models.DateField(blank=True, null=True)
    observaciones                = models.CharField(max_length=500, blank=True, null=True)
    usuario_ultima_actualizacion = models.BigIntegerField(blank=True, null=True)
    create_at                    = models.DateTimeField(blank=True, null=True)
    update_at                    = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed  = False
        db_table = 'inventario'

    def __str__(self):
        return self.nombre or f'Inventario #{self.id_inventario}'

    @property
    def en_alerta(self):
        if self.stocktotal is not None and self.alerta_minimos is not None:
            return self.stocktotal <= self.alerta_minimos
        return False


class InventarioDiario(models.Model):
    id_inventario_diario = models.AutoField(primary_key=True)
    fecha                = models.DateField(default=date.today)
    realizado_por        = models.IntegerField()          # id del usuario
    nombre_responsable   = models.CharField(max_length=255, blank=True, null=True)
    observaciones        = models.CharField(max_length=500, blank=True, null=True)
    total_productos      = models.IntegerField(default=0)
    total_diferencias    = models.IntegerField(default=0)
    create_at            = models.DateTimeField(default=timezone.now)

    class Meta:
        managed  = True
        db_table = 'inventario_diario'
        ordering = ['-fecha', '-create_at']

    def __str__(self):
        return f'Inventario {self.fecha} — {self.nombre_responsable}'


class DetalleInventarioDiario(models.Model):
    id_detalle        = models.AutoField(primary_key=True)
    inventario_diario = models.ForeignKey(
        InventarioDiario,
        on_delete=models.CASCADE,
        related_name='detalles',
        db_column='id_inventario_diario'
    )
    id_producto       = models.IntegerField()
    nombre_producto   = models.CharField(max_length=255)
    categoria         = models.CharField(max_length=255, blank=True, null=True)
    stock_anterior    = models.IntegerField(default=0)
    stock_fisico      = models.IntegerField(default=0)
    diferencia        = models.IntegerField(default=0)   # stock_fisico - stock_anterior
    alerta_minimos    = models.IntegerField(default=5)
    costo_unitario    = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado_anterior   = models.CharField(max_length=50, blank=True, null=True)
    estado_nuevo      = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed  = True
        db_table = 'detalle_inventario_diario'

    def __str__(self):
        return f'{self.nombre_producto} — {self.inventario_diario.fecha}'

    @property
    def tiene_diferencia(self):
        return self.diferencia != 0

    @property
    def diferencia_clase(self):
        if self.diferencia > 0:
            return 'text-success'
        elif self.diferencia < 0:
            return 'text-danger'
        return 'text-muted'