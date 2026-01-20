####################
# Para gerir os grupos de usuarios permitidos
########################

from django.contrib.auth.models import Group
from django.http import HttpResponse
from usuarios.models import CustomUser


def grupos_permitidos(grupos):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            # Verificação 1: Usuário autenticado
            if not request.user.is_authenticated:
                return HttpResponse("""
                <!DOCTYPE html>
                <html lang="pt-br">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Não Autenticado</title>
                    <script src="https://cdn.tailwindcss.com"></script>
                    <script>
                        tailwind.config = {
                            theme: {
                                extend: {
                                    colors: {
                                        primary: '#8B5A9F',
                                        secondary: '#B19CD9',
                                        accent: '#E8D5F2',
                                        dark: '#2D1B40'
                                    }
                                }
                            }
                        }
                    </script>
                </head>
                <body class="bg-accent min-h-screen flex items-center justify-center">
                    <div class="bg-white rounded-2xl shadow-2xl p-10 max-w-md w-full text-center border-t-8 border-primary">
                        <div class="flex justify-center mb-4">
                            <svg class="w-16 h-16 text-primary" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01M21 12c0 4.97-4.03 9-9 9s-9-4.03-9-9 4.03-9 9-9 9 4.03 9 9z" />
                            </svg>
                        </div>
                        <h1 class="text-2xl font-bold text-primary mb-2">Sessão Expirada</h1>
                        <p class="text-gray-700 mb-4">
                            Sua sessão expirou ou você não está autenticado.
                        </p>
                        <a href="/login/" class="inline-block mt-4 px-6 py-2 rounded-lg bg-primary text-white font-semibold hover:bg-secondary transition">Fazer Login</a>
                    </div>
                </body>
                </html>
                """, status=401)
            
            # Verificação 2: Usuário está ativo no banco de dados
            try:
                usuario = CustomUser.objects.only('id', 'is_active').get(
                    id=request.user.id
                )
                
                if not usuario.is_active:
                    return HttpResponse("""
                    <!DOCTYPE html>
                    <html lang="pt-br">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Usuário Desativado</title>
                        <script src="https://cdn.tailwindcss.com"></script>
                        <script>
                            tailwind.config = {
                                theme: {
                                    extend: {
                                        colors: {
                                            primary: '#8B5A9F',
                                            secondary: '#B19CD9',
                                            accent: '#E8D5F2',
                                            dark: '#2D1B40'
                                        }
                                    }
                                }
                            }
                        </script>
                    </head>
                    <body class="bg-accent min-h-screen flex items-center justify-center">
                        <div class="bg-white rounded-2xl shadow-2xl p-10 max-w-md w-full text-center border-t-8 border-red-600">
                            <div class="flex justify-center mb-4">
                                <svg class="w-16 h-16 text-red-600" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01M21 12c0 4.97-4.03 9-9 9s-9-4.03-9-9 4.03-9 9-9 9 4.03 9 9z" />
                                </svg>
                            </div>
                            <h1 class="text-2xl font-bold text-red-600 mb-2">Acesso Revogado</h1>
                            <p class="text-gray-700 mb-4">
                                Sua conta foi desativada.<br>
                                Entre em contato com o administrador do sistema.
                            </p>
                            <a href="/logout/" class="inline-block mt-4 px-6 py-2 rounded-lg bg-red-600 text-white font-semibold hover:bg-red-700 transition">Fazer Logout</a>
                        </div>
                    </body>
                    </html>
                    """, status=403)
                    
            except CustomUser.DoesNotExist:
                return HttpResponse("""
                <!DOCTYPE html>
                <html lang="pt-br">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Usuário Não Encontrado</title>
                    <script src="https://cdn.tailwindcss.com"></script>
                    <script>
                        tailwind.config = {
                            theme: {
                                extend: {
                                    colors: {
                                        primary: '#8B5A9F',
                                        secondary: '#B19CD9',
                                        accent: '#E8D5F2',
                                        dark: '#2D1B40'
                                    }
                                }
                            }
                        }
                    </script>
                </head>
                <body class="bg-accent min-h-screen flex items-center justify-center">
                    <div class="bg-white rounded-2xl shadow-2xl p-10 max-w-md w-full text-center border-t-8 border-red-600">
                        <h1 class="text-2xl font-bold text-red-600 mb-2">Erro de Sistema</h1>
                        <p class="text-gray-700 mb-4">
                            Seu usuário não foi encontrado no banco de dados.
                        </p>
                        <a href="/logout/" class="inline-block mt-4 px-6 py-2 rounded-lg bg-red-600 text-white font-semibold hover:bg-red-700 transition">Fazer Logout</a>
                    </div>
                </body>
                </html>
                """, status=403)
            
            # Verificação 3: Pertence aos grupos permitidos
            if request.user.groups.filter(name__in=grupos).exists():
                return view_func(request, *args, **kwargs)
            
            # Usuário ativo mas sem permissão de grupo
            html = """
            <!DOCTYPE html>
            <html lang="pt-br">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Acesso Negado</title>
                <script src="https://cdn.tailwindcss.com"></script>
                <script>
                    tailwind.config = {
                        theme: {
                            extend: {
                                colors: {
                                    primary: '#8B5A9F',
                                    secondary: '#B19CD9',
                                    accent: '#E8D5F2',
                                    dark: '#2D1B40'
                                }
                            }
                        }
                    }
                </script>
            </head>
            <body class="bg-accent min-h-screen flex items-center justify-center">
                <div class="bg-white rounded-2xl shadow-2xl p-10 max-w-md w-full text-center border-t-8 border-primary">
                    <div class="flex justify-center mb-4">
                        <svg class="w-16 h-16 text-primary" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01M21 12c0 4.97-4.03 9-9 9s-9-4.03-9-9 4.03-9 9-9 9 4.03 9 9z" />
                        </svg>
                    </div>
                    <h1 class="text-2xl font-bold text-primary mb-2">Acesso Negado</h1>
                    <p class="text-gray-700 mb-4">
                        Você não tem permissão para acessar esta página.<br>
                        Entre em contato com o administrador do sistema.
                    </p>
                    <a href="/" class="inline-block mt-4 px-6 py-2 rounded-lg bg-primary text-white font-semibold hover:bg-secondary transition">Voltar para o início</a>
                </div>
            </body>
            </html>
            """
            return HttpResponse(html, status=403)
            
        _wrapped_view.__name__ = view_func.__name__
        return _wrapped_view
    return decorator