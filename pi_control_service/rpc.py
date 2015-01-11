import json
import pika


class RPCService(object):

    def __init__(self, rabbit_url, user_key, device_key, request_action):
        self.rabbit_url = rabbit_url
        self.user_key = user_key
        self.device_key = device_key
        self.request_action = request_action
        self.connection = pika.BlockingConnection(pika.URLParameters(self.rabbit_url))
        self._setup_channel()

    def _setup_channel(self):
        self.channel = self.connection.channel()

        result = self.channel.queue_declare(
            auto_delete=True,
            arguments={'x-message-ttl': 10000})

        self.channel.exchange_declare(exchange=self.user_key, type='direct')
        self.channel.queue_bind(
            queue=result.method.queue,
            exchange=self.user_key,
            routing_key=self.device_key)
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self._handle_request, queue=result.method.queue)

    def _handle_request(self, ch, method, props, body):
        response = self.request_action(json.loads(body))
        ch.basic_publish(
            exchange='',
            routing_key=props.reply_to,
            properties=pika.BasicProperties(correlation_id=props.correlation_id),
            body=json.dumps(response))
        ch.basic_ack(delivery_tag = method.delivery_tag)

    def _error(self, response):
        return {'error': 1, 'response': response}

    def _response(self, response):
        return {'error': 0, 'response': response}

    def start(self):
        try:
            self.channel.start_consuming()
        except:
            self.stop()
            raise

    def stop(self):
        self.channel.stop_consuming()
        self.connection.close()
