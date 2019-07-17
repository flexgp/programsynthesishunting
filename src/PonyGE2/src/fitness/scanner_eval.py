from algorithm.parameters import params
from fitness.base_ff_classes.base_ff import base_ff
from fitness.TCPScanner import TCPScanner

import math



class scanner_eval(base_ff):


    def __init__(self):
        # Initialise base fitness function class.
        super().__init__()
        self.scanner = TCPScanner(1)
        self.ip_range = '128.52.191.0'
        self.maximise = True


        if params['MULTICORE']:
            print("Warming: Multicore is not supported with progsys "
                  "as fitness function.\n"
                  "Fitness function only allows sequential evaluation.")

    def evaluate(self, ind, **kwargs):
        print(ind.phenotype)
        parameters = eval(ind.phenotype)
        num_ips = int(parameters[0])
        ports = parameters[1]
        ip_wait = int(parameters[2]) / 1000
        port_wait = int(parameters[3]) / 1000
        retries = int(parameters[4])

        cidr_notation = self.ip_range + "/" + str(32 - round(math.log2(num_ips)))
        print(num_ips, cidr_notation, ports, ip_wait, port_wait, retries)
        self.scanner.scan_ips(cidr_notation, ports_os=ports, wait_btw_ports=port_wait, wait_btw_ips=ip_wait, retries=retries)
        num_open_ports = self.scanner.get_num_open_ports()
        self.scanner.clear_scan_dic()

        num_unique_ip_port = num_ips * self.scanner.get_num_ports(ports)

        return num_open_ports / num_unique_ip_port

