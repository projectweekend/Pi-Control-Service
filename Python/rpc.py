import json
import pika


class RPCService(object):

    def __init__(self, rabbit_url, queue_name, device_key):
        self.rabbit_url = rabbit_url
        self.queue_name = queue_name
        self.device_key = device_key
        self.connection = pika.BlockingConnection(pika.URLParameters(self.rabbit_url))
        self._setup_channel()

    def _setup_channel(self):
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name)
        self.channel.exchange_declare(exchange=self.device_key, type='direct')
        self.channel.queue_bind(exchange=self.device_key, queue=self.queue_name)
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self._handle_request, queue=self.queue_name)

    def _handle_request(self, ch, method, props, body):
        response = {}
        ch.basic_publish(
            exchange='',
            routing_key=props.reply_to,
            properties=pika.BasicProperties(correlation_id=props.correlation_id),
            body=json.dumps(response))
        ch.basic_ack(delivery_tag = method.delivery_tag)

    def start(self):
        try:
            self.channel.start_consuming()
        except:
            self.stop()
            raise

    def stop(self):
        self.channel.stop_consuming()
        self.connection.close()
