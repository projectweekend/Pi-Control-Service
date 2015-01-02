import os
import json
import pika

from rpc import RPCService
from pi_pin_manager import PinManager


RABBIT_URL = os.getenv('RABBIT_URL', None)
assert RABBIT_URL

DEVICE_KEY = os.getenv('DEVICE_KEY', None)
assert DEVICE_KEY

PIN_CONFIG = os.getenv('PIN_CONFIG', None)
assert PIN_CONFIG


class GPIOService(RPCService):

    def __init__(self, rabbit_url, device_key, pin_config):
        super(GPIOService, self).__init__(
            rabbit_url=rabbit_url,
            queue_name='gpio_service',
            device_key=device_key)
        self.pins = PinManager(config_file=pin_config)

    def _handle_request(self, ch, method, props, body):
        response = self._perform_gpio_action(instruction=json.loads(body))
        ch.basic_publish(
            exchange='',
            routing_key=props.reply_to,
            properties=pika.BasicProperties(correlation_id=props.correlation_id),
            body=json.dumps(response))
        ch.basic_ack(delivery_tag = method.delivery_tag)

    def _perform_gpio_action(self, instruction):
        result = {'error': 1, 'pin': instruction['pin'], 'response': "An error occurred"}
        try:
            result['response'] = getattr(self.pins, instruction['action'])(int(instruction['pin']))
            result['error'] = 0
        except AttributeError:
            result['response'] = "'{0}' is not a valid 'action'".format(instruction['action'])
        except ValueError:
            result['response'] = "'pin' value must be an integer"
        except:
            pass
        return result

    def stop(self):
        super(GPIOService, self).stop()
        self.pins.cleanup()


def main():
    gpio_service = GPIOService(
        rabbit_url=RABBIT_URL,
        device_key=DEVICE_KEY,
        pin_config=PIN_CONFIG)
    gpio_service.start()


if __name__ == '__main__':
    main()
