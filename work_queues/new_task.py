import sys
import pika


# 连接RabbitMQ服务器
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# 声明持久队列
channel.queue_declare(queue='task_queue', durable=True)

# 发送消息
message = ' '.join(sys.argv[1:]) or 'Hello World!'

# 消息持久化
channel.basic_publish(
    exchange='', routing_key='task_queue', body=message,
    properties=pika.BasicProperties(
        delivery_mode=2, # make message persistent
    )
)

print('[x] Send {}'.format(message))
connection.close()
