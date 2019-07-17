import socket
import threading
import random
import ipaddress
import time

class TCPScanner:

    def __init__(self, timeout):
        self.timeout = timeout
        self.scan_dic = {}
        self.os_port_dic = {"linux": [20, 21, 22, 23, 25, 80, 111, 443, 445, 631, 993, 995],
                            "windows": [135, 137, 138, 139, 445],
                            "mac": [22, 445, 548, 631]}

    def set_timeout(self, new_timeout):
        self.timeout = new_timeout

    def TCP_connect(self, ip, port_number, retries):
        TCPsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        TCPsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        TCPsock.settimeout(self.timeout)
        count = 0
        while count <= retries:
            try:
                TCPsock.connect((ip, port_number))
                self.scan_dic[ip + ":" + str(port_number)] = 'Listening'
                break
            except:
                self.scan_dic[ip + ":" + str(port_number)] = 'No Response'
                count += 1

    def scan_ports(self, host_ip, ports_os, wait_btw_ports, retries):
        """
        :param host_ip: ip to scan ports of
        :param ports_os: "all", "mac", "windows", "linux", "random"
        :param ports: list of a ports to scan, ports associated with ports_os will also be scanned
        :return:
        """
        ports = []
        if ports_os == "all":
            for key in self.os_port_dic:
                ports.extend(self.os_port_dic[key])
        elif ports_os == "random":
            for x in range(100):
                ports.append(random.randint(0, 65535))
        elif ports_os in self.os_port_dic:
            ports.extend(self.os_port_dic[ports_os])

        threads = []  # To run TCP_connect concurrently
        # Spawning threads to scan ports
        num_ports = len(ports)
        for i in range(num_ports):
            t = threading.Thread(target=self.TCP_connect, args=(host_ip, ports[i], retries))
            threads.append(t)

        # Starting threads
        for i in range(num_ports):
            threads[i].start()
            time.sleep(wait_btw_ports)

        # Locking the script until all threads complete
        for i in range(num_ports):
            threads[i].join()

        print("Ports scanned: " + str(ports))
        return self.scan_dic

    def scan_ips(self, ip_string, ports_os="all", wait_btw_ips=.001, wait_btw_ports=.001, retries=0):
        self.clear_scan_dic()
        ip_network = ipaddress.ip_network(ip_string, strict=False)
        for ip in ip_network:
            self.scan_ports(str(ip), ports_os, wait_btw_ports, retries)
            time.sleep(wait_btw_ips)

        return self.scan_dic

    def print_results(self):
        for key in self.scan_dic:
            if self.scan_dic[key] == 'Listening':
                print(key + ' is ' + 'open and listening')

    def get_num_open_ports(self):
        count = 0
        for key in self.scan_dic:
            if self.scan_dic[key] == 'Listening':
                count += 1
        return count

    def clear_scan_dic(self):
        self.scan_dic = {}

    def get_num_ports(self, ports_os):
        num_ports = 0
        if ports_os == "all":
            for key in self.os_port_dic:
                num_ports += len(self.os_port_dic[key])
        elif ports_os == "random":
            num_ports = 100
        elif ports_os in self.os_port_dic:
            num_ports = len(self.os_port_dic[ports_os])
        return num_ports