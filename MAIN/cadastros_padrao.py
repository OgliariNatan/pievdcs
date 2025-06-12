from sistema_justica.models.base import Agressor_dados, Vitima_dados
'''
Cadastros padrões, em caso de exclusões.

'''
def agressor_padrao():
    return Agressor_dados.objects.get_or_create(nome="Apagado")[0].id


def vitima_padrao():
    return Vitima_dados.objects.get_or_create(nome='Apagada')[0].id