from django.db import models

class Vitima(models.Model):
    nome = models.CharField(max_length=100)
    idade = models.IntegerField()
    endereco = models.TextField()

    def __str__(self):
        return self.nome