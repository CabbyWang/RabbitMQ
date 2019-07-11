import sys
import pika


# 连接RabbitMQ服务器
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# 声明exchange
channel.exchange_declare(exchange='direct_logs', exchange_type='direct')

# 发送消息
severity = sys.argv[1] if len(sys.argv) > 1 else 'info'
message = ' '.join(sys.argv[2:]) or 'Hello World!'

channel.basic_publish(
    exchange='direct_logs',
    routing_key=severity,
    body=message
)

print('[x] Send {}: {}'.format(severity, message))
connection.close()
