import unittest
import json
import socket
import threading
import time
from src.radio_simulator import RadioSim

class ConnectionTest(unittest.TestCase):
    _frequencies = [
            120.255,
            120.255,
            121.100,
            121.100,
            120.255,
            128.750
        ]
    _clients: list[socket.socket] = []

    def setUp(self) -> None:
        return super().setUp()
    
    def start_test(self) -> None:
        RadioSim.start('localhost', 15100)

        try:

            for index in range(6):
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                print(str("Test:").ljust(50, '.') + f"Socket {index} created!")
                client.connect(('localhost', 15100))
                print(str("Test:").ljust(50, '.') + f"Socket {index} connected!")
                client.sendall(ConnectionTest.get_settings_message(self._frequencies[index]))
                print(str("Test:").ljust(50, '.') + f"Socket {index} sent settings!")
                response = client.recv(1024)
                print(str("Test:").ljust(50, '.') + f"Received response: {response.decode('utf-8')}")

                if response != b'OK':

                    raise Exception("Repsonse not expected!")
                
                self._clients.append(client)


        except Exception as e:
            print(e)

        return

    def close_test(self):
        print("Closing connections!")
        
        try:

            for index, client in enumerate(self._clients):
                client.sendall(ConnectionTest.get_disconnect_message())
                client.shutdown(socket.SHUT_RDWR)
                client.close()

        except Exception as e:
            print(f"Error: {e}")

        print("Stopping RadioSim")
        RadioSim.stop()

    
    def test_01(self) -> None:
        self.start_test()
        #time.sleep(5)
        
        
        self._clients[0].setblocking(True)
        self._clients[1].setblocking(True)
        self._clients[2].settimeout(5)
        self._clients[3].settimeout(5)
        self._clients[4].setblocking(True)
        self._clients[5].settimeout(5)

        print("Sending Data!")
        self._clients[0].sendall(str("Test").encode('utf-8'))
        print(str("Test:").ljust(50, '.') + f"Socket {1} receiving!")
        self.assertEqual(b"Test", self._clients[1].recv(1024))
        print(str("Test:").ljust(50, '.') + f"Socket {4} receiving!")
        self.assertEqual(b"Test", self._clients[4].recv(1024))
        print(str("Test:").ljust(50, '.') + f"Waiting for timeouts")
        self.assertRaises(TimeoutError, self._clients[2].recv, 1024)
        self.assertRaises(TimeoutError, self._clients[3].recv, 1024)
        self.assertRaises(TimeoutError, self._clients[5].recv, 1024)

        self._clients[3].sendall(ConnectionTest.get_settings_message(self._frequencies[0]))
        self.assertEqual(b"OK", self._clients[3].recv(1024))
        print("Sending Data!")
        self._clients[0].sendall(str("Test").encode('utf-8'))
        print(str("Test:").ljust(50, '.') + f"Socket {1} receiving!")
        self.assertEqual(b"Test", self._clients[1].recv(1024))
        print(str("Test:").ljust(50, '.') + f"Socket {3} receiving!")
        self.assertEqual(b"Test", self._clients[3].recv(1024))
        print(str("Test:").ljust(50, '.') + f"Socket {4} receiving!")
        self.assertEqual(b"Test", self._clients[4].recv(1024))
        print(str("Test:").ljust(50, '.') + f"Waiting for timeouts")
        self.assertRaises(TimeoutError, self._clients[2].recv, 1024)
        self.assertRaises(TimeoutError, self._clients[5].recv, 1024)

        print("received!")
            
        self.close_test()
        
        return
            
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
        message_bytes = message.encode()

        return message_bytes


