from sistema_justica.models.base import Agressor_dados, Vitima_dados, Filhos_dados
'''
Cadastros padrões, em caso de exclusões.

'''
def agressor_padrao():
    '''
    Quando é excluido uma informação, em vez de apagar toda a dependencia substitui-se por valores pré-estabelicidos
    '''
    return Agressor_dados.objects.get_or_create(nome="Apagado")[0].id


def vitima_padrao():
    '''
    Quando é excluido uma informação, em vez de apagar toda a dependencia substitui-se por valores pré-estabelicidos
    '''
    return Vitima_dados.objects.get_or_create(nome='Apagada')[0].id


def filho_padrao():
    '''
    @input: None
    @output: Cadastro de Filho pré estabelicido
    Quando é excluido uma informação, em vez de apagar toda a dependencia substitui-se por valores pré-estabelicidos
    '''
    return Filhos_dados.objects.get_or_create(nome='Apagada')[0].id
