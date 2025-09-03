
from pathlib import Path
import os
import locale

from dotenv import load_dotenv

# Carrega o arquivo .env
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')  # Configura o locale para português do Brasil


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', "False")  # Updated to use config

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS').split(',')


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",# Mensagens de feedback
    "django.contrib.staticfiles",# Arquivos estáticos
    'corsheaders', # Para acesso cruzado
    'dbbackup', #Para realizar backup
    'smart_selects',#Para selecionar os municipios
    'rest_framework', #Para criação de API
    'MAIN',  # Aplicação principal
    'seguranca_publica', #Segurança pública
    'usuarios.apps.UsuariosConfig', #Usuarios autorizados
    'sistema_justica', #Sistemas de justica
    'municipio', #sistema municipal
    
    # Mensageiro CRIAR
    
    
]


#E-mail
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
# EMAIL_PORT = os.getenv('EMAIL_PORT', 587)
# EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', True).lower() in ['true', '1', 't']
# EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')  # E-mail do remetente
# EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')  # Senha ou token do remetente


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    'corsheaders.middleware.CorsMiddleware',  # Middleware para CORS
    'MAIN.middleware.logs_pers.APILogMiddleware',  # Middleware personalizado para logs
]

# define aonde sera armagenado as mensagens
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'


ASGI_APPLICATION = 'pievdcs.MAIN.asgi.application' 
ROOT_URLCONF = "MAIN.urls"
USE_DJANGO_JQUERY = True
SMART_SELECTS_INCLUDE_JQUERY = True

CSRF_TRUSTED_ORIGINS = [
    'https://www.redecontraaviolencia.org',
    'https://redecontraaviolencia.org',
    'http://62.72.9.77',
    'http://www.redecontraaviolencia.org',
    'http://redecontraaviolencia.org'
]



TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "MAIN/templates"),
            os.path.join(BASE_DIR, "Seguranca_publica/templates"),
            os.path.join(BASE_DIR, "sistema_justica/templates"),
            os.path.join(BASE_DIR, "municipio/templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "MAIN.wsgi.application"


# Database


DATABASES = {
    "default": {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DATABASE_NAME'),
        'USER': os.getenv('DATABASE_USER'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'HOST': os.getenv('DATABASE_HOST', default='localhost'),  # Updated to use config
        'PORT': os.getenv('DATABASE_PORT', default='5432'),  # Updated to use config
        'OPTIONS' : {
            "application_name": "pievdcs",
            "connect_timeout": 30,
            "client_encoding": "utf8",
            #'timezone': 'America/Sao_Paulo',
        }
    }
}


# Password validation


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

#DESABILITA O FRAMEWORK REST
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
}


# Internationalization


LANGUAGE_CODE = "pt-BR"

TIME_ZONE = "America/Sao_Paulo"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)


STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
    os.path.join(BASE_DIR, "MAIN/static"),
    os.path.join(BASE_DIR, "usuarios/static"),
    os.path.join(BASE_DIR, "seguranca_publica/static"),
    os.path.join(BASE_DIR, "sistema_justica/static"),
    os.path.join(BASE_DIR, "municipio/static"),
]


MEDIA_URL = '/img_home/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'img_home')  # Pasta para armazenar imagens carregadas

# Default primary key field type


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = '/login/'  # URL para redirecionar usuários não autenticados
LOGIN_REDIRECT_URL = '/home/'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True #Fecha a seção quando fecha o navegador
SESSION_COOKIE_NAME = 'sistema_justica_session'  # Nome do cookie de sessão
SESSION_COOKIE_AGE = 9000  # x minutos em segundos
SESSION_SAVE_EVERY_REQUEST = False  # Só renova se houver atividade

CSRF_COOKIE_HTTPONLY = True       # Impede acesso via JavaScript (aumenta a segurança)
SESSION_COOKIE_SAMESITE = 'Lax' # não aceita cookie de terceiros
#SESSION_COOKIE_SECURE = True #Só transmite informação se for seguro 'https'


AUTH_USER_MODEL = 'usuarios.CustomUser'


#configurar logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'debug_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'debug.log'),
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'error.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['debug_file', 'error_file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}