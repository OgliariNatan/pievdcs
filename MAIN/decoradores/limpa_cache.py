"""

    Módulo de decoradores para limpeza/Consulta de cache.


"""


from django.core.cache import cache



def mostra_cache(self, nameCache = None):
    if nameCache:
        return cache.get(nameCache)
    else:
        return cache.keys('*')


def limpa_cache(self, nameCache):
    cache.delete(nameCache)
    
    
def exclui_cache(self):
    cache.clear()
