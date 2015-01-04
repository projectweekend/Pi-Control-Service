from rpc import RPCService


def not_hidden_method(method_name):
    return not (method_name.startswith('_') or method_name.startswith('__'))


class CustomActionService(RPCService):

    def __init__(self, rabbit_url, device_key, actions):
        self.actions = actions
        self.allowed_actions = filter(not_hidden_method, dir(self.actions))
        super(CustomActionService, self).__init__(
            rabbit_url=rabbit_url,
            queue_name='custom_action_service',
            device_key=device_key,
            request_action=self._perform_custom_action)

    def _perform_custom_action(self, instruction):
        result = {'error': 1, 'action': instruction['action'], 'response': "An error occurred"}

        if instruction['action'] not in self.allowed_actions:
            result['response'] = "'action' must be one of: {0}".format(', '.join(self.allowed_actions))
            return result

        try:
            result['response'] = getattr(self.actions, instruction['action'])()
            result['error'] = 0
        except Exception as e:
            result['response'] = e.message

        return result
