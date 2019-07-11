import sys
import pika


# 连接RabbitMQ服务器
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# 声明exchange
channel.exchange_declare(exchange='logs', exchange_type='fanout')

# 发送消息
message = ' '.join(sys.argv[1:]) or 'info: Hello World!'

channel.basic_publish(
    exchange='logs', routing_key='', body=message
)

print('[x] Send {}'.format(message))
connection.close()
