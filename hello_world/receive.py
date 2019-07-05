import pika


# 连接RabbitMQ服务器
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# 声明队列
channel.queue_declare(queue='hello')

def callback(ch, method, properties, body):
    print("[x] Received {}".format(body))


# 接收消息
channel.basic_consume(queue='hello', auto_ack=True, on_message_callback=callback)

print('[*] Waiting for messages. To exit press CTRL+C')

channel.start_consuming()
