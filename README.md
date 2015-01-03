Want to control a Raspberry Pi from anywhere? **Pi-Control-Service** makes that easy by listening for and responding to simple JSON messages. You only need these two things:

* A [RabbitMQ](https://www.rabbitmq.com/) connection string.
* An Internet connection.

**What Can I Control?**

In this early iteration of **Pi-Control-Service** you have access basic digital GPIO. You can turn pins on or off and read their current status. I am working to expand this by allowing you to implement custom commands that can be triggered. Using these you will be able do just about anything, like: access [I2C](http://en.wikipedia.org/wiki/I%C2%B2C), [SPI](http://en.wikipedia.org/wiki/Serial_Peripheral_Interface_Bus), or the serial port, and issue system commands. Stay tuned.


### Install it

```
pip install Pi-Control-Service
```

### Configure it

A config file, written in [YAML](http://en.wikipedia.org/wiki/YAML), is used to define the initial pin setup. If a pin is not defined here it will not be available to **Pi-Control-Service**. The following snippet shows an example configuration file:

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

### Use it (Start the GPIO service on a Raspberry Pi)

```python
from pi_control import GPIOService


# The RabbitMQ connection string
RABBIT_URL='some_actual_connection_string'

# A unique string you make up to identify the single Raspberry Pi
DEVICE_KEY='raspberry_pi_coffee_maker'

# Path to the config file references in the section above
PIN_CONFIG = '/path/to/config/file.yml'

gpio_service = GPIOService(rabbit_url=RABBIT_URL, device_key=DEVICE_KEY, pin_config=PIN_CONFIG)
gpio_service.start()
```

### Use it (Send the GPIO service commands)

TODO: Add information about `GPIOClient`...

If you feel like learning a lot more about RabbitMQ, you can actually use any language or RabbitMQ library to create a client to communicate with your Raspberry Pi. It doesn't have to be Python at all. All you need to do is:

* Connect to the RabbitMQ server using the same value as `RABBIT_URL` referenced above.
* Bind to a direct exchange named using the value from `DEVICE_KEY`.
* Start sending properly formed JSON messages to the queue.


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
