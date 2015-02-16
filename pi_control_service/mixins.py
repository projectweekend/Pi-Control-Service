class ServiceUtils(object):

    @staticmethod
    def _error(response):
        return {'error': 1, 'response': response}

    @staticmethod
    def _response(response):
        return {'error': 0, 'response': response}
