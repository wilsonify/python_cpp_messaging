# Consumer
# (c) Mark Borg, August 2018
import logging
import sys
import pika
import cv2
import numpy as np
import queue
import threading
import time

AMQP_HOST = 'localhost'
AMQP_PORT = 32777


class RabbitMQ_consumer(threading.Thread):
    def __init__(self, name, host=AMQP_HOST, port=AMQP_PORT, exchange_name='my_exchange_1', exchange_type='direct',
                 routing_key='my_key_1', prefetch=3):
        threading.Thread.__init__(self)
        self.name = name
        self.host = host
        self.port = port
        self.exchange_name = exchange_name
        self.exchange_type = exchange_type
        self.routing_key = routing_key
        self.prefetch = prefetch
        self.channel = None
        self.queue = queue.Queue(10)  # internal message queue. Note that Queue is thread-safe.
        self.do_exit = False
        self.queue_name = 'tmp'

    def receive_callback(self, ch, method, properties, body):
        # callback function to handle received messages
        print(" [%s] Received message of length %d" % (self.name, len(body)))
        self.queue.put(body)

    def cancel_callback(self, method):
        # callback function to handle cancel event
        print(" [%s] cancelling...", self.name)

    # an exception class that can be raised by this consumer
    class EOT(Exception):
        def __init__(self, consumer_name):
            Exception.__init__(self, "EOT received by " + consumer_name)

    def run(self):

        # establish connection with the RabbitMQ server
        parameters = pika.ConnectionParameters(host=self.host, port=self.port)
        connection = pika.BlockingConnection(parameters)
        self.channel = connection.channel()

        # declare the exchange
        self.channel.exchange_declare(exchange=self.exchange_name, exchange_type=self.exchange_type)

        # a temporary queue is used (will exist only for this producer-consumer session)
        result = self.channel.queue_declare(queue='', exclusive=True)
        self.queue_name = result.method.queue
        print(' [%s] Binding with queue: %s' % (self.name, self.queue_name))

        # bind the consumer to the given queue
        self.channel.queue_bind(exchange=self.exchange_name, queue=self.queue_name, routing_key=self.routing_key)
        print(' [%s] routing key: %s' % (self.name, self.routing_key))

        # subscribe the callback function to the queue
        self.channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=self.receive_callback,
            auto_ack=True,
            exclusive=False,
            consumer_tag=None,
            arguments=None,

        )

        # specify quality of service
        # The client can request that messages be sent in advance so that when the client finishes
        # processing a message, the following message is already held locally, rather than needing
        # to be sent down the channel. Prefetching gives a performance improvement.
        self.channel.basic_qos(prefetch_count=self.prefetch)

        self.channel.add_on_cancel_callback(self.cancel_callback)

        # start consuming messages
        print(' [%s] Waiting for messages...' % self.name)
        self.channel.start_consuming()

        # shutdown
        print(" [%s] Closing down connections..." % self.name)
        # channel.stop_consuming()
        connection.close()

        print(" [%s] Finished" % self.name)

    def receive(self):
        if self.is_alive() == False:
            raise Exception(' [%s] thread not running!' % self.name)

        msg = self.queue.get()
        if (msg == b'\x04'):
            print(" [%s] Received EOT" % self.name)
            raise self.EOT(self.name)

        return msg

    def receive_image(self):
        msg = self.receive()
        img = cv2.imdecode(np.frombuffer(msg, np.uint8), cv2.IMREAD_COLOR)
        return img

    def exit(self):
        if self.is_alive() == False:
            raise Exception(' [%s] thread not running!' % self.name)

        print(" [%s] Exiting..." % self.name)
        self.channel.stop_consuming()


if __name__ == '__main__':

    if len(sys.argv) > 1 and sys.argv[1] == 'images':
        cons1 = RabbitMQ_consumer('Consumer1', 'localhost', 5672, 'my_exchange_1', 'direct', 'images', 3)
        cons1.start()

        while True:
            img_outer = cons1.receive_image()
            print('Received an image of size %dx%d' % (img_outer.shape[0], img_outer.shape[1]))

            # display the image
            cv2.namedWindow('Received image')  # create window for display
            cv2.imshow('Received image', img_outer)  ## Show image in the window
            cv2.waitKey(10)

        cv2.destroyAllWindows()
    else:
        cons1 = RabbitMQ_consumer('Consumer1', AMQP_HOST, AMQP_PORT, 'my_exchange_1', 'direct', 'text', 3)
        cons1.start()

        try:
            while True:
                msg_outer = cons1.receive()
                print('Received a message of length %d: %s' % (len(msg_outer), msg_outer))
        except KeyboardInterrupt:
            logging.exception("Keyboard Interrupt")

    print('Shutting down...')
    cons1.exit()
    cons1.join()

    print('Program finished')
