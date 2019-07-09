# RabbitMQ(Python实现)

## 安装

1. 安装[erlang](https://www.erlang.org/downloads)
2. 安装[rabbitmq-server](https://www.rabbitmq.com/download.html)

## demo

(使用pika 1.0.1)

### hello world

[官方文档](https://www.rabbitmq.com/tutorials/tutorial-one-python.html)

从一个命名队列中发送和接收消息

```bash
# 接收消息
python receive.py
```

```bash
# 发送消息
python send.py
```

### Work Queues

[官方文档](https://www.rabbitmq.com/tutorials/tutorial-two-python.html)

创建一个`Work Queues`用于分配耗时任务给多个`workers`

#### 1. 循环调度(Round-robin dispatching)

开启多个终端运行多个`worker`

```bash
# 接收消息
python worker.py
```

```bash
# 下发耗时任务
python new_task.py
```

#### 2. 消息确认(Message acknowledgment)

`消息确认`： 任务运行成功会给`RabbitMQ`一个`ack`， 表示任务完成

默认情况下`消息确认`是打开状态。之前指定`auto_ack=True`把它关闭。现在将其移除。

```python
def callback(ch, method, property, body):
    body = body.decode("utf-8")
    print("[x] Received {}".format(body))
    time.sleep(body.count('.'))
    print("[x] Done")
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(queue='hello', on_message_callback=callback)
```

**注意：**不要忘了`basic_ack`,否则`RabbitMQ`会占用越来越多的内存，官方解释:

```txt
It's a common mistake to miss the basic_ack. It's an easy error, but the consequences are serious. Messages will be redelivered when your client quits (which may look like random redelivery), but RabbitMQ will eat more and more memory as it won't be able to release any unacked messages.
```

打印出`Unacked messages`：

```bash
# linux
sudo rabbitmqctl list_queues name messages_ready messages_unacknowledged

# windows
rabbitmqctl.bat list_queues name messages_ready messages_unacknowledged
```

#### 3. 消息持久化(Message durability)

为了确保信息不会丢失， 必须把`队列(queue`)和`消息(message)`设为持久化。否则， `RabbitMQ`退出或崩溃时， 所有`队列`和`消息`都会丢失。

- 队列持久化
  
    ```python
    channel.queue_declare(queue='task_queue', durable=True)
    ```

- 消息持久化

    ```python
    channel.basic_publish(
        exchange='', routing_key='task_queue', body=message,
        properties=pika.BasicProperties(
            delivery_mode=2, # make message persistent
        )
    )
    ```

    **注意:** `RabbitMQ`收到消息，到保存到硬盘之间有一个很小的时间间隔， 所以消息持久化并不能完全保证不会丢失。

#### 3. 公平调度(Fair dispatch)

使用`basic.qos`方法，并设置`prefetch_count=1`，告诉`RabbitMQ`同一时刻，不要发送超过一条消息给一个worker， 直到它已经处理了上一条消息并作出了响应。这样，`RabbitMQ`就会把消息分发给下一个空闲的worker。

其他链接:

[Top 10 Uses For A Message Queue](https://blog.iron.io/top-10-uses-for-message-queue/?spref=tw)
