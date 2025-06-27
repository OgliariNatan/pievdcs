import logging

logger = logging.getLogger(__name__)


class APILogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        self.log_request(request, response)
        return response

    def log_request(self, request, response):
        try:
            # Obter o endereço IP do usuário
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
                print(f'\n----------\nIP do usuário: {ip}')
            else:
                ip = request.META.get('REMOTE_ADDR')

            # Logar as informações
            logger.info(f'Requisição: {request.method} {request.path} | IP: {ip} | Status: {response.status_code}')
        except Exception as e:
            logger.error(f'Erro ao logar requisição: {e}')


class RequestLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else 'Anon'
        ip = request.META.get('REMOTE_ADDR', '')
        
        logger = logging.getLogger('')
        logger.info(
            'Nova requisição recebida',
            extra={
                'remote_addr': ip,
                'user': str(user)
            }
        )
        return self.get_response(request)