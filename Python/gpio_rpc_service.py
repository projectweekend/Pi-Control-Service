import os
import pika


RABBIT_URL = os.getenv('RABBIT_URL', None)
assert RABBIT_URL

QUEUE_NAME = os.getenv('QUEUE_NAME', None)
assert QUEUE_NAME

EXCHANGE_NAME = os.getenv('EXCHANGE_NAME', 'user_key')
assert EXCHANGE_NAME


def do_something():
	return "something"


def handle_request(ch, method, props, body):
	print(body)
	response = do_something()
	ch.basic_publish(
		exchange='',
		routing_key=props.reply_to,
		properties=pika.BasicProperties(correlation_id=props.correlation_id),
		body=response)
	ch.basic_ack(delivery_tag = method.delivery_tag)


connection = pika.BlockingConnection(pika.URLParameters(RABBIT_URL))

channel = connection.channel()
channel.queue_declare(queue=QUEUE_NAME)

channel.exchange_declare(exchange=EXCHANGE_NAME, type='direct')
channel.queue_bind(exchange=EXCHANGE_NAME, queue=QUEUE_NAME)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(handle_request, queue=QUEUE_NAME)

channel.start_consuming()
