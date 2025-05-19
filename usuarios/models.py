from django.db import models

# Create your models here.
class Vitima(models.Model):
    id_vitima = models.AutoField(primary_key=True, verbose_name="ID da Vítima",)
    nome = models.CharField(max_length=255)
    cpf = models.CharField(max_length=14, unique=True)
    endereco = models.TextField()
    telefone = models.CharField(max_length=15)
    qtd_filhos = models.IntegerField(default=0)

    def __str__(self):
        return self.nome