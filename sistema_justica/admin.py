from django.contrib import admin
from django import forms
from .models.base import Vitima_dados, Agressor_dados, Filhos_dados, Municipio
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