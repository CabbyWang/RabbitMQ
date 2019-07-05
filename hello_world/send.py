import pika


# 连接RabbitMQ服务器
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# 声明队列
channel.queue_declare(queue='hello')

# 发送消息
channel.basic_publish(exchange='', routing_key='hello', body='Hello World')
print("[x] send 'Hello World!")

connection.close()
