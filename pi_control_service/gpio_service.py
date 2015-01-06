from rpc import RPCService
from pi_pin_manager import PinManager


ALLOWED_ACTIONS = ('on', 'off', 'read', 'get_config')


class GPIOService(RPCService):

    def __init__(self, rabbit_url, device_key, pin_config):
        self.pins = PinManager(config_file=pin_config)
        super(GPIOService, self).__init__(
            rabbit_url=rabbit_url,
            queue_name='gpio_service',
            device_key=device_key,
            request_action=self._perform_gpio_action)

    def _perform_gpio_action(self, instruction):
        result = {'error': 1, 'response': "An error occurred"}

        if instruction['action'] not in ALLOWED_ACTIONS:
            result['response'] = "'action' must be one of: {0}".format(', '.join(ALLOWED_ACTIONS))
            return result

        try:
            pin = instruction['pin']
        except KeyError:
            try:
                result['response'] = getattr(self.pins, instruction['action'])()
                result['error'] = 0
            except Exception as e:
                result['response'] = e.message
        else:
            try:
                result['response'] = getattr(self.pins, instruction['action'])(int(pin))
                result['error'] = 0
            except ValueError:
                result['response'] = "'pin' value must be an integer"
            except Exception as e:
                result['response'] = e.message

        return result

    def stop(self):
        self.pins.cleanup()
        super(GPIOService, self).stop()
