import pika


# 连接RabbitMQ服务器
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# 声明exchange
channel.exchange_declare(exchange='logs', exchange_type='fanout')

result = channel.queue_declare(queue='', exclusive=True)  # 消费者断开时， 队列立即删除

queue_name = result.method.queue

channel.queue_bind(queue=queue_name, exchange='logs')

def callback(ch, method, property, body):
    # body = body.decode("utf-8")
    print("[x] {}".format(body))

# 接收消息
channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

print('[*] Waiting for logs. To exit press CTRL+C')

channel.start_consuming()
