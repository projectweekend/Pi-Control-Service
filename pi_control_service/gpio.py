from pika_pack import RPCBlockingConsumer
from pi_pin_manager import PinManager

from mixins import ServiceUtils


ALLOWED_ACTIONS = ('on', 'off', 'read', 'get_config')


class GPIOControlService(ServiceUtils, RPCBlockingConsumer):

    def __init__(self, rabbit_url, device_key, pin_config):
        self._pins = PinManager(config_file=pin_config)
        super(GPIOControlService, self).__init__(
            rabbit_url=rabbit_url,
            exchange='gpio_control',
            routing_key=device_key,
            request_action=self._perform_gpio_action)

    def _perform_gpio_action(self, instruction):
        try:
            if instruction['action'] not in ALLOWED_ACTIONS:
                return self._error("'action' must be one of: {0}".format(', '.join(ALLOWED_ACTIONS)))
        except KeyError:
            return self._error("'action' must be defined")

        try:
            return self._response(getattr(self._pins, instruction['action'])(int(instruction['pin'])))
        except ValueError:
            return self._error("'pin' value must be an integer")
        except KeyError:
            try:
                return self._response(getattr(self._pins, instruction['action'])())
            except Exception as e:
                return self._error(e.message)
        except Exception as e:
            return self._error(e.message)

    def stop(self):
        self._pins.cleanup()
        super(GPIOControlService, self).stop()
