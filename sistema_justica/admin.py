from django.contrib import admin
from .models.base import Vitima_dados, Agressor_dados, Filhos_dados

# Register your models here.

class FilhosInlineMae(admin.TabularInline):
    model = Filhos_dados
    fk_name = 'nome_mae'
    extra = 1
    verbose_name = "Filho"

class FilhosInlinePai(admin.TabularInline):
    model = Filhos_dados
    fk_name = 'nome_pai'
    extra = 1
    verbose_name = "Filho"

@admin.register(Vitima_dados)
class VitimaAdmin(admin.ModelAdmin):
    inlines = [FilhosInlineMae]

@admin.register(Agressor_dados)
class AgressorAdmin(admin.ModelAdmin):
    inlines = [FilhosInlinePai]

admin.site.register(Filhos_dados)