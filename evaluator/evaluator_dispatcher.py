from abc import *
import threading
from queue import Queue


# ****** Unique dispatcher side ******
class EvaluatorDispatcher(threading.Thread):
    __metaclass__ = ABCMeta

    def __init__(self, config):
        super().__init__()
        self.registered_list = {}
        self.config = config
        self.keep_running = True
        self.is_setup_correctly = False

    def notify_registered_evaluator_clients(self, symbol, data):
        for target_evaluator in self.registered_list[symbol]:
            target_evaluator.add_to_queue(data)

    def register_client(self, symbol, client):
        if symbol in self.registered_list:
            self.registered_list[symbol].append(client)
        else:
            self.registered_list[symbol] = [client]

    @abstractmethod
    def dispatch_notification_to_clients(self, data):
        raise NotImplementedError("dispatch_notification_to_clients not implemented")

    @abstractmethod
    def run(self):
        raise NotImplementedError("run not implemented")

    @abstractmethod
    def get_is_setup_correctly(self):
        return self.is_setup_correctly

    def stop(self):
        self.keep_running = False


# ****** Implementation side ******
class EvaluatorDispatcherClient:
    __metaclass__ = ABCMeta

    def __init__(self):
        self.dispatcher = None
        self.is_computing = False
        self.queue = Queue()

    @abstractmethod
    def receive_notification_data(self, data) -> None:
        raise NotImplementedError("receive_notification_data not implemented")

    @staticmethod
    @abstractmethod
    def get_dispatcher_class():
        raise NotImplementedError("get_dispatcher_class not implemented")

    def set_dispatcher(self, dispatcher):
        self.dispatcher = dispatcher

    def add_to_queue(self, data):
        self.queue.put(data)
        self.notify_received_data()

    def notify_received_data(self):
        if not self.is_computing:
            self.is_computing = True
            threading.Thread(target=self.process_queue).start()

    def process_queue(self):
        try:
            while not self.queue.empty():
                self.receive_notification_data(self.queue.get())
        finally:
            self.is_computing = False

    def is_client_to_this_dispatcher(self, dispatcher_instance):
        return self.get_dispatcher_class() == dispatcher_instance.__class__