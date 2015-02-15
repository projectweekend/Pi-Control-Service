**Why I made this**

This project started because I had an external web server and I wanted it to get some data from sensors on a Raspberry Pi in my apartment. I didn't want to mess with a bunch of stupid networking, so that the two could talk to each other. Instead, I decided to take advantage of [RabbitMQ](https://www.rabbitmq.com/). Messaging queues, like RabbitMQ, are a common tactic for letting separate application components communicate in a simple, scalable way. It's also a great fit for controlling the Raspberry Pi in many [Internet of Things](http://en.wikipedia.org/wiki/Internet_of_Things) type projects.

**What it does**

Using the GPIO service (`pi_control_service.GPIOService`) you have access to the Raspberry Pi's digital GPIO pins. You can turn pins on and off as well as read their values. Using the custom action service (`pi_control_service.CustomActionService`) you can call methods on an "actions" class you implement. This allows you to do just about anything, like: access [I2C](http://en.wikipedia.org/wiki/I%C2%B2C), [SPI](http://en.wikipedia.org/wiki/Serial_Peripheral_Interface_Bus), or the serial port, and issue system commands.


## Install it

```
pip install Pi-Control-Service
```

## GPIO service

The GPIO service (`pi_control_service.GPIOService`) exposes access to the Raspberry Pi's digital GPIO pins. Using it you can turn pins on and off as well as read their values. The next two sections cover specifics of its configuration and usage.

### Configuring the GPIO service

A config file, written in [YAML](http://en.wikipedia.org/wiki/YAML), is used to define the initial pin setup. If a pin is not defined here it will not be available to **Pi-Control-Service**. You can save this file anywhere. You will provide a path to the file in your code. The following snippet shows an example configuration file:

```yaml
18:
  mode: OUT
  initial: HIGH
23:
  mode: OUT
  initial: LOW
```

* Add a numbered element for each pin to enable
* `mode` - This controls whether the pin will be used for input or output. Accepted values are: `IN`, `OUT`. (Required)
* `initial` - This controls the starting value of the pin. Accepted values are: `LOW`, `HIGH`. (Optional - defaults to `LOW`)

### Starting the GPIO service

This part runs on your Raspberry Pi. It initializes the desired GPIO pins, connects to RabbitMQ and starts listening for messages.

```python
from pi_control_service import GPIOService


# The RabbitMQ connection string
RABBIT_URL='some_actual_connection_string'

# A unique string you make up to identify a single Raspberry Pi
DEVICE_KEY='my_awesome_raspberry_pi'

# Path to the config file referenced in the section above
PIN_CONFIG = '/path/to/config/file.yml'

gpio_service = GPIOService(
    rabbit_url=RABBIT_URL,
    device_key=DEVICE_KEY,
    pin_config=PIN_CONFIG)

gpio_service.start()
```

**Note:**
In addition to the example above, the `GPIOService` class takes an optional argument `reconnect_attempts`. This is in integer represneting the number of times to attempt reconnection with RabbitMQ. These attempts will be made if the connection to RabbitMQ is interrupted after the `start()` method is called.


### Using the GPIO service

For convenience there is a [client library](https://github.com/projectweekend/Pi-Control-Client) you can install and use on the computer that will be remotely controlling a Raspberry Pi. The same `RABBIT_URL` and `DEVICE_KEY` values referenced in the section above are also used to connect the client.

#### Installing the client

```
pip install Pi-Control-Client
```

#### Using the client

```python
from pi_control_client import GPIOClient

# The RabbitMQ connection string (must match the one used when starting the service)
RABBIT_URL='some_actual_connection_string'

# A unique string you make up to identify a single Raspberry Pi (must match the one used when starting the service)
DEVICE_KEY='my_awesome_raspberry_pi'

pins_client = GPIOClient(rabbit_url=RABBIT_URL)

# Get all pins config
result = pins_client.read_config(DEVICE_KEY)

# Get a pin config
result = pins_client.read_config(DEVICE_KEY, 18)

# Turn a pin on
pins_client.on(DEVICE_KEY, 18)

# Turn a pin off
pins_client.off(DEVICE_KEY, 18)

# Read a pin value
result = pins_client.read_value(DEVICE_KEY, 18)
```

If you are already familar with RabbitMQ, you can implement your own client using any language. Things to know:

* The exchange name is: `gpio_service`
* The `DEVICE_KEY` value is the routing key
* The JSON messages sent to the broker should be formatted like the following examples:


#### Turn a pin on
```json
{
    "pin": 18,
    "action": "on"
}
```


#### Turn a pin off
```json
{
    "pin": 18,
    "action": "off"
}
```


#### Read a pin value
```json
{
    "pin": 18,
    "action": "read"
}
```


#### Read config for all pins
```json
{
    "action": "get_config"
}
```


#### Read config for one pin
```json
{
    "pin": 18,
    "action": "get_config"
}
```


## Custom action service

The custom action service (`pi_control_service.CustomActionService`) allows you to call methods on a special "actions" class that you define. Using it, the possibilities are almost limitless.


### Starting the custom action service

This part runs on your Raspberry Pi. It connects to RabbitMQ and starts listening for messages.

```python
import subprocess

from pi_control_service import CustomActionService


# The RabbitMQ connection string
RABBIT_URL='some_actual_connection_string'

# A unique string you make up to identify a single Raspberry Pi
DEVICE_KEY='my_awesome_raspberry_pi'

# This class contains all the custom actions that the service will expose
class Actions(object):

    def hello_world(self):
        return {'message': "I do what I want!"}

    def cpu_temp(self):
        return subprocess.check_output(["/opt/vc/bin/vcgencmd", "measure_temp"])


custom_actions = CustomActionService(
    rabbit_url=RABBIT_URL,
    device_key=DEVICE_KEY,
    actions=Actions())

custom_actions.start()
```

### Using the custom action service

For convenience there is a [client library](https://github.com/projectweekend/Pi-Control-Client) you can install and use on the computer that will be remotely controlling a Raspberry Pi. The same `RABBIT_URL` and `DEVICE_KEY` values referenced in the section above are also used to connect the client.


#### Installing the client

```
pip install Pi-Control-Client
```


#### Using the client

```python
from pi_control_client import CustomActionClient

# The RabbitMQ connection string (must match the one used when starting the service)
RABBIT_URL='some_actual_connection_string'

# A unique string you make up to identify a single Raspberry Pi (must match the one used when starting the service)
DEVICE_KEY='my_awesome_raspberry_pi'

actions_client = CustomActionClient(rabbit_url=RABBIT_URL)

# Call a custom action
result = actions_client.call(DEVICE_KEY, 'name_of_action_method')
```

If you are already familar with RabbitMQ, you can implement your own client using any language. Things to know:

* The exchange name is: `custom_action_service`
* The `DEVICE_KEY` value is the routing key
* The JSON messages sent to the broker should be formatted like the following examples:


#### Call an action
```json
{
    "action": "name_of_action_method"
}
```
