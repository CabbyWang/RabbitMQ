import time
import pika


# 连接RabbitMQ服务器
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# 声明队列
channel.queue_declare(queue='hello')

def callback(ch, method, property, body):
    # body = body.decode("utf-8")
    print("[x] Received {}".format(body))
    time.sleep(body.count(b'.'))
    print("[x] Done")
    ch.basic_ack(delivery_tag=method.delivery_tag)

# 接收消息
channel.basic_qos(prefetch_count=1)  # 一个worker预先载入一个消息
channel.basic_consume(queue='hello', on_message_callback=callback)

print('[*] Waiting for messages. To exit press CTRL+C')

channel.start_consuming()
