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
            print("Received Settings")
            

            if "Frequency" in settings:
                print(f'Frequency: {settings["Frequency"]}')
                frequency = settings["Frequency"]
                self.frequency = frequency

            return
        
        def message_available(self) -> bool:
            return bool(self._message_queue)
        
        def popleft_message(self) -> bytearray:
            print("Message from queue requested!")

            if not self._message_queue:

                raise ValueError("List is empty!")

            with self._lock:

                return self._message_queue.popleft()

        def push_message(self, message: bytearray) -> None:
            print("Trying to push data!")

            self._lock.acquire()
            print("Got the key!")
            self._client_socket.sendall(message)
            print("Data pushed!")
            self._lock.release()

            return
            print("Pushing data into queue!")

            with self._lock:

                self._message_queue.append(message)

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
        print(str("RadioSim:").ljust(50, '.') + "Started")

        return
    
    @classmethod
    def stop(cls) -> None:
        """
        Blocking call to stop all communication and close sockets
        """
        print(str("RadioSim:").ljust(50, '.') + "stopping")

        if cls._read_running():

            cls._write_running(False)
            number_of_threads = len(cls._threads)

            for index, thread in enumerate(cls._threads[:]):
                print(str("RadioSim:").ljust(50, '.') + f"Waiting for thread {index+1} of {number_of_threads} to stop")
                thread.join()
                cls._threads.remove(thread)
                print(str("RadioSim:").ljust(50, '.') + f"Thread {index} of {number_of_threads} stopped")

            cls._connection_request_thread.join()

        print(str("RadioSim:").ljust(50, '.') + "stopped")

        return

    def register_participant(self, frequency: float, send_function: Callable[[str], None]) -> int:
        """
        Register a new participant on ether. 
        """

        # check, if frequency is correct
        if not isinstance(frequency, float):

            raise TypeError(f'(f"Parameter frequency must be of type float. Provided type: {type(frequency)}')
        
        # check signature of callable

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
                #radio_socket.close()

                print(f"Exception message: {e}")

                #raise Exception(e)
            

        radio_socket.close()

        return
    
    @classmethod
    def _handle_connection(cls, client_socket: socket.socket, address: socket.AddressInfo) -> None:
        print(str("RadioSim:").ljust(50, '.') + f"Client {address} connected!")

        if not isinstance(client_socket, socket.socket):

            raise TypeError(f'(f"Parameter client_socket must be of type socket.socket. Provided type: {type(client_socket)}')

        
        client_socket.settimeout(0.25)
        print(str(f"Socket {client_socket.getpeername()}:").ljust(50, '.') + "Timeout set!")
        client = RadioSim.Client(client_socket, address)
        cls._clients.append(client)
        print(str(f"Socket {client_socket.getpeername()}:").ljust(50, '.') + "Included in list!")

        
        while cls._read_running():
            client._lock.acquire()

            try:
                data_received = client_socket.recv(4096)
                message_received = data_received.decode('utf-8')
                
                prefix = "RadioSim - Settings"

                if message_received.startswith("RadioSim - Settings"):
                    print("Received Settings!")

                    try:
                        settings = json.loads(message_received[len(prefix):])
                        client.set_settings(settings)
                        print("Sending response!")
                        client_socket.sendall(b'OK')
                        print("Response sent!")

                    except:
                        print("Didn't work!")

                elif message_received.startswith("RadioSim - Disconnect"):
                    print("Client disconnected!")

                    break

                else:
                    print("Giving data to radio_message")
                    cls._radio_message(client, data_received)
                    
                

            except TimeoutError as e:
                pass

                #continue

            client._lock.release()

            

            #print("Released the key!")
                
            

        client_socket.close()

        return
    
    @classmethod
    def _read_running(cls) -> bool:

        return cls._running

    @classmethod
    def _write_running(cls, value: bool) -> None:
        print(str("RadioSim:").ljust(50, '.') + f"Writing {value} to running")

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
                        print("Pushing message")
                        client.push_message(data)

        
        return


if __name__ == "__main__":

    def get_settings_message(value: float) -> bytearray:
        data = {
            "Frequency": value
        }

        json_data = json.dumps(data)
        message = "RadioSim - Settings" + json_data
        message_bytes = message.encode('utf-8')

        return message_bytes

    def get_disconnect_message() -> bytearray:
        message = "RadioSim - Disconnect"
        message_bytes = message.encode('utf-8')

        return message_bytes

    RadioSim.start('localhost', 15100)
    time.sleep(1)
    clients = []
    frequencies = [
        120.255,
        120.255,
        121.100,
        121.100,
        120.255,
        128.750
    ]

    try:

        for index in range(2):
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print(str("Test:").ljust(50, '.') + f"Socket {index} created!")
            client.connect(('localhost', 15100))
            print(str("Test:").ljust(50, '.') + f"Socket {index} connected!")
            client.sendall(get_settings_message(frequencies[index]))
            print(str("Test:").ljust(50, '.') + f"Socket {index} sent settings!")
            response = client.recv(1024)
            print(str("Test:").ljust(50, '.') + f"Received response: {response.decode('utf-8')}")

            if response != b'OK':

                raise Exception("Repsonse not expected!")
            
            clients.append(client)
            time.sleep(1)

        #try:
        #    data = client2.recv(16)

    except Exception as e:
        print(e)

    print("Sending Data!")


    clients[0].sendall(str("Test").encode('utf-8'))
    print("Receiving data")
    clients[1].settimeout(5)

    try:
        data = clients[1].recv(16)
        print("received!")

    except Exception as e:
        print("Exception during receiving data!")
        print(e)

    try:
        
        unittest.TestCase.assertEqual(b"Test", data)
        print("Passed!")

    except Exception as e:
        print(e)
        
    print("Closing connections!")

    try:

        for index, client in enumerate(clients):
            client.sendall(ConnectionTest.get_disconnect_message())
            client.shutdown(socket.SHUT_RDWR)
            client.close()

    except Exception as e:
        print(f"Error: {e}")

    print("Stopping RadioSim")
    RadioSim.stop()


                
            
