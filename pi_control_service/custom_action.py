from pika_pack import RPCBlockingListener

from mixins import ServiceUtils


def not_hidden_method(method_name):
    return not (method_name.startswith('_') or method_name.startswith('__'))


class CustomActionService(ServiceUtils, RPCBlockingListener):

    def __init__(self, rabbit_url, device_key, actions):
        self._actions = actions
        self._allowed_actions = filter(not_hidden_method, dir(self._actions))
        super(CustomActionService, self).__init__(
            rabbit_url=rabbit_url,
            exchange='custom_action_service',
            routing_key=device_key,
            request_action=self._perform_custom_action)

    def _perform_custom_action(self, instruction):
        try:
            if instruction['action'] not in self._allowed_actions:
                return self._error("'action' must be one of: {0}".format(', '.join(self._allowed_actions)))
        except KeyError:
            return self._error("'action' must be defined")

        try:
            return self._response(getattr(self._actions, instruction['action'])())
        except Exception as e:
            return self._error(e.message)
