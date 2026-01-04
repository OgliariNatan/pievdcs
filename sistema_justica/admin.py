from django.contrib import admin
from django import forms
from .models.base import Vitima_dados, Agressor_dados, Filhos_dados, Municipio, Estado, Bairro, TipoDeViolencia
from .models.poder_judiciario import ComarcasPoderJudiciario
from .models.defensoria_publica import FormularioMedidaProtetiva
# admin.py
# Register your models here.

# Formulários personalizados para mostrar o calendário nos campos de data
class VitimaForm(forms.ModelForm):
    class Meta:
        model = Vitima_dados
        fields = '__all__'
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
        }

class AgressorForm(forms.ModelForm):
    class Meta:
        model = Agressor_dados
        fields = '__all__'
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
        }

class FilhosForm(forms.ModelForm):
    class Meta:
        model = Filhos_dados
        fields = '__all__'
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
        }

class FilhosInlineMae(admin.TabularInline):
    model = Filhos_dados
    fk_name = 'nome_mae'
    extra = 1
    verbose_name = "Filho"
    form = FilhosForm

class FilhosInlinePai(admin.TabularInline):
    model = Filhos_dados
    fk_name = 'nome_pai'
    extra = 1
    verbose_name = "Filho"
    form = FilhosForm

@admin.register(Vitima_dados)
class VitimaAdmin(admin.ModelAdmin):
    form = VitimaForm
    inlines = [FilhosInlineMae]

@admin.register(Agressor_dados)
class AgressorAdmin(admin.ModelAdmin):
    form = AgressorForm
    inlines = [FilhosInlinePai]

admin.site.register(Filhos_dados)

admin.site.register(Municipio)
@admin.register(Estado)
class EstadoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'sigla')
    search_fields = ('nome', 'sigla')
    ordering = ('nome',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('nome')
    
    
@admin.register(ComarcasPoderJudiciario)
class ComarcasPoderJudiciarioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'estado')
    search_fields = ('nome',)
    ordering = ('nome',)

@admin.register(FormularioMedidaProtetiva)
class DefensiriaPublicaFormulario(admin.ModelAdmin):
    list_display = ('ID', 'vitima', 'agressor')
    ordering = ('-ID',)

@admin.register(TipoDeViolencia)
class TipoDeViolenciaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao',)
    search_fields = ('nome',)

@admin.register(Bairro)
class BairroAdmin(admin.ModelAdmin):
    list_display = ('nome', 'municipio',)
    search_fields = ('nome',)