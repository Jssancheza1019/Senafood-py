from django.db import models
from gestion.models import Usuario, Carrito
from pqrs.models import PQRSF

class Notificacion(models.Model):

    TIPOS = [
        ('pqrsf',    'PQRSF'),
        ('carrito',  'Carrito / Pedido'),
        ('sistema',  'Sistema'),
    ]

    id_notificacion = models.AutoField(primary_key=True)
    mensaje         = models.TextField()
    fechaenvio      = models.DateTimeField(db_column='fechaEnvio', auto_now_add=True)
    leida           = models.BooleanField(default=False)          # ✅ esencial para la campana
    tipo            = models.CharField(max_length=20, choices=TIPOS, default='sistema')  # ✅ para íconos

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='idUsuario')
    carrito = models.ForeignKey(Carrito, on_delete=models.SET_NULL, db_column='id_carrito',
                                null=True, blank=True)            # ✅ opcional
    pqrsf   = models.ForeignKey(PQRSF,   on_delete=models.SET_NULL,
                                null=True, blank=True, db_column='pqrsf_id')          # ✅ opcional

    class Meta:
        managed = True
        db_table = 'notificacion'
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-fechaenvio']                                # ✅ más recientes primero

    def __str__(self):
        return f"[{self.tipo}] Para {self.usuario.nombre}: {self.mensaje[:30]}..."