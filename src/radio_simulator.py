from collections import deque
import json
import time
import threading
from typing import Callable
import socket

class RadioSim:

    class Client:

        def __init__(self, socket, address) -> None:
            self._client_socket = socket
            self._address = address
            self._lock = threading.Lock()
            self._frequency = 0
            self._message_queue: deque = deque()

            return

        def set_settings(self, settings: dict) -> None:
            
            if "Frequency" in settings:
                frequency = settings["Frequency"]
                self.frequency = frequency

            return
        
        def message_available(self) -> bool:

            return bool(self._message_queue)
        
        def popleft_message(self) -> bytearray:

            if not self._message_queue:

                raise ValueError("List is empty!")

            with self._lock:

                return self._message_queue.popleft()

        def push_message(self, message: bytearray) -> None:
            self._lock.acquire()
            self._client_socket.sendall(message)
            self._lock.release()

            return


    _instance = None
    _lock: threading.Lock = threading.Lock()
    _running = False
    _threads: list[threading.Thread] = []
    _clients: list[Client] = []

    def __new__(cls, *args, **kwargs):

        if not cls.__instance:

            with cls._lock:

                if not cls.__instance:

                    cls.__instance = super(RadioSim, cls).__new__(cls, *args, **kwargs)

                
            
        return cls.__instance
    
    @classmethod
    def start(cls, ip: str, port: int) -> None:

        if cls._read_running():

            return

        if not isinstance(port, int):

            raise TypeError(f"Port must be of type integer. Provided Type: {type(port)}")
        
        if port <= 0:

            raise ValueError("Port must be greater than 0!")
        
        cls._write_running(True)
        cls._connection_request_thread = threading.Thread(target = cls._handle_connection_requests, args = (ip, port))
        cls._connection_request_thread.start()

        return
    
    @classmethod
    def stop(cls) -> None:
        """
        Blocking call to stop all communication and close sockets
        """

        if cls._read_running():

            cls._write_running(False)
            number_of_threads = len(cls._threads)

            for index, thread in enumerate(cls._threads[:]):
                thread.join()
                cls._threads.remove(thread)

            cls._connection_request_thread.join()

        return

    def register_participant(self, frequency: float, send_function: Callable[[str], None]) -> int:
        """
        Register a new participant on ether. 
        """

        if not isinstance(frequency, float):

            raise TypeError(f'(f"Parameter frequency must be of type float. Provided type: {type(frequency)}')

    @classmethod
    def _handle_connection_requests(cls, ip: str, port: int) -> None:

        radio_socket_address = (ip, port)
        radio_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        radio_socket.bind((ip, port))
        radio_socket.listen(1)
        radio_socket.settimeout(0.25)

        while cls._read_running():

            try:
                new_client_socket, new_client_address = radio_socket.accept()
                new_client_thread = threading.Thread(target = cls._handle_connection, args = (new_client_socket, new_client_address))
                new_client_thread.start()
                cls._threads.append(new_client_thread)

            except TimeoutError:

                continue

            except Exception as e:
                print(f"Exception message: {e}")


        radio_socket.close()

        return
    
    @classmethod
    def _handle_connection(cls, client_socket: socket.socket, address: socket.AddressInfo) -> None:

        if not isinstance(client_socket, socket.socket):

            raise TypeError(f'(f"Parameter client_socket must be of type socket.socket. Provided type: {type(client_socket)}')

        client_socket.settimeout(0.25)
        client = RadioSim.Client(client_socket, address)
        cls._clients.append(client)
        
        while cls._read_running():
            client._lock.acquire()

            try:
                data_received = client_socket.recv(4096)
                message_received = data_received.decode('utf-8')
                settings_prefix = "RadioSim - Settings"
                disconnect_prefix = "RadioSim - Disconnect"
                if message_received.startswith(settings_prefix):

                    try:
                        settings = json.loads(message_received[len(settings_prefix):])
                        client.set_settings(settings)
                        client_socket.sendall(b'OK')

                    except:
                        pass

                elif message_received.startswith(disconnect_prefix):

                    break

                else:
                    cls._radio_message(client, data_received)
                    

            except TimeoutError as e:
                pass

            client._lock.release()
                
        client_socket.close()

        return
    
    @classmethod
    def _read_running(cls) -> bool:

        return cls._running

    @classmethod
    def _write_running(cls, value: bool) -> None:

        if not isinstance(value, bool):
        
            raise TypeError(f"Parameter value must be of type bool. Provided type: {type(value)}")

        with cls._lock:

            cls._running = value

        return

    def unregister_participant(self):
        pass

    @classmethod
    def _radio_message(cls, sender: Client, data: bytearray) -> None:
        print("Radio_message received data!")

        with cls._lock:

            for client in cls._clients:
                print(client.frequency)

                if not client == sender:

                    if client.frequency == sender.frequency:
                        client.push_message(data)

        
        return