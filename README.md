Want to control a Raspberry Pi from anywhere? Using **Pi-Control-Service** you only really need two things: a [RabbitMQ](https://www.rabbitmq.com/) connection string and an Internet connection.

**What Can I Control?**

This project is still very young. In this iteration you have access basic digital GPIO. You can turn pins on or off and read their current values. I am actively working to expand this by allowing you to implement custom commands that can be triggered. Using this format you will be able to do just about anything, like: access [I2C](http://en.wikipedia.org/wiki/I%C2%B2C), [SPI](http://en.wikipedia.org/wiki/Serial_Peripheral_Interface_Bus), or the serial port, and issue system commands. Stay tuned.


### Install it

```
pip install Pi-Control-Service
```

### GPIO service

The GPIO service (`pi_control_service.GPIOService`) exposes access to the Raspberry Pi's digital GPIO pins. Using it you can turn pins on and off as well as read their values. The next two sections cover specifics of its configuration and usage.

#### Configuring the GPIO service

A config file, written in [YAML](http://en.wikipedia.org/wiki/YAML), is used to define the initial pin setup. If a pin is not defined here it will not be available to **Pi-Control-Service**. You can save this file anywhere. You will provide a path for the module to access it in your code. The following snippet shows an example configuration file:

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

#### Starting the GPIO service

```python
from pi_control_service import GPIOService


# The RabbitMQ connection string
RABBIT_URL='some_actual_connection_string'

# A unique string you make up to identify a single Raspberry Pi
DEVICE_KEY='raspberry_pi_coffee_maker'

# Path to the config file referenced in the section above
PIN_CONFIG = '/path/to/config/file.yml'

gpio_service = GPIOService(
    rabbit_url=RABBIT_URL,
    device_key=DEVICE_KEY,
    pin_config=PIN_CONFIG)

gpio_service.start()
```

#### Using the GPIO service

For convenience there is a client library you can install and use on the computer that will be remotely controlling a Raspberry Pi. The same `RABBIT_URL` and `DEVICE_KEY` values referenced in the section above are also used to connect the client.

##### Installing the client

```
pip install Pi-Control-Client
```

##### Using the client

```python
from pi_control_client import GPIOClient

# The RabbitMQ connection string (must match the one used when starting the service)
RABBIT_URL='some_actual_connection_string'

# A unique string you make up to identify a single Raspberry Pi (must match the one used when starting the service)
DEVICE_KEY='raspberry_pi_coffee_maker'

pins_client = GPIOClient(rabbit_url=RABBIT_URL, device_key=DEVICE_KEY)

# Turn a pin on
pins_client.on(18)

# Turn a pin off
pins_client.off(18)

# Read a pin value
result = pins_client.read(18)
```

If you are already familar with RabbitMQ, you can implement your own client using any language. Things to know:

* The queue name is: `gpio_service`
* The queue should bind to a direct exchange name matching the `DEVICE_KEY` value
* The JSON messages sent to the broker should be formatted like:


##### Turn a pin on
```json
{
    "pin": 18,
    "action": "on"
}
```


##### Turn a pin off
```json
{
    "pin": 18,
    "action": "off"
}
```


##### Read a pin value
```json
{
    "pin": 18,
    "action": "read"
}
```
