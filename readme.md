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

### 工作队列(Work Queues)

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

### 发布/订阅(Pulish/Subscribe)

分发一个消息给多个消费者(consumer)。

RabbitMQ消息模型的核心理念是：发布者(producer)不会直接发送任何消息给队列
。事实上，发布者甚至不知道消息是否已经被投递到队列。

#### 1. 交换机(Exchange)

交换机类型： 直连交换机(direct)，主题交换机(topic)，头交换机(headers)，扇形交换机(fanout)。

这里使用扇形交换机，把消息发送给它所绑定的所有队列。

```python
channel.exchange_declare(exchange='logs', exchange_type='fanout')
```

```bash
sudo rabbitmqctl list_exchanges  # 列出服务器上所有的交换机
```

#### 2. 临时队列(Temporary queues)

```python
result = channel.queue_declare(queue='', exclusive=True)  # 消费者断开时， 队列立即删除

queue_name = result.method.queue  # 队列名
```

#### 3. 绑定(Bindings)

将队列绑定到交换机上

```python
channel.queue_bind(queue=queue_name, exchange='logs')
```

```bash
sudo rabbitmqctl list_bindings  # 查看存在的队列绑定
```

### 路由(Routing)

在广播的基础上新增功能--订阅消息的一个子集。例如，只输出error日志，或者全部日志输出。

这里使用直连交换机，把消息发送给绑定它的队列。绑定的时候可以带上一个额外的`routing_key`。

- 发送`routing_key`为error的日志

    ```python
    channel.basic_publish(
        exchange='direct_logs',
        routing_key='error',
        body='message'
    )
    ```

- 订阅`routing_key`为error的日志

    ```python
    channel.queue_bind(
        queue=queue_name,
        exchange='direct_logs',
        routing_key='error'
    )
    ```

**绑定值`routing_key`的意义取决于交换机`exchange`的类型, 扇形交换机(fanout exchanges)会忽略这个值**

其他链接:

[Top 10 Uses For A Message Queue](https://blog.iron.io/top-10-uses-for-message-queue/?spref=tw)
