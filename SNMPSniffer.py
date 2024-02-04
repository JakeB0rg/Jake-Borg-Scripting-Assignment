from scapy.all import *
import sqlite3
from scapy.all import SNMP, Ether, IP, UDP #both are needed for some reason
import datetime

def database(): #initiates database
    conn = sqlite3.connect('RouterDatabase.db')
    cursor = conn.cursor()

    #creating the links table
    cursor.execute('''CREATE TABLE IF NOT EXISTS LINKS (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT,
                        time TEXT,
                        router_ip TEXT,
                        interface_name TEXT,
                        state TEXT
                    )''')
    conn.commit()

    #creating the syslog table
    cursor.execute('''CREATE TABLE IF NOT EXISTS SYSLOG (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT,
                        time TEXT,
                        router_ip TEXT,
                        message TEXT
                    )''')
    conn.commit()
    conn.close()

def handle_snmp_trap(pkt): #this handles everything link related
    if SNMP in pkt:
        community = pkt[SNMP].community
        if community == b"SFN":  # Note the 'b' prefix for byte string
            if pkt[SNMP].PDU == 4:  # LinkUp
                date_time = str(packet.time)
                router_ip = packet[IP].src
                interface = pkt.sniffed_on
                state = 'Link Up'
                print("LinkUp SNMP trap received.")
                conn = sqlite3.connect('RouterDatabase.db')
                cursor = conn.cursor()
                cursor.execute('''INSERT INTO LINKS (trap_type, date, time, router_ip, interface, state) 
                                VALUES (?, ?, ?, ?, ?, ?)''', ('LinkUp', date_time.split('.')[0], date_time.split('.')[1], router_ip, interface, state))
                conn.commit()
                conn.close()

            elif pkt[SNMP].PDU == 5:  # LinkDown
                date_time = str(pkt.time)
                router_ip = pkt[IP].src
                interface = pkt.sniffed_on
                state = 'Link Down'
                print("LinkDown SNMP trap received.")
                conn = sqlite3.connect('RouterDatabase.db')
                cursor = conn.cursor()
                cursor.execute('''INSERT INTO LINKS (trap_type, date, time, router_ip, interface, state) 
                                VALUES (?, ?, ?, ?, ?, ?)''', ('LinkDown', date_time.split('.')[0], date_time.split('.')[1], router_ip, interface, state))
                conn.commit()
                conn.close()
            else:
                print(f"Unknown SNMP trap type {pkt[SNMP].PDU}.")

def handle_syslog(pkt): #handles syslog
    if UDP in pkt and pkt[UDP].dport == 514:
        message = pkt[Raw].load.decode('utf-8')
        print(f"Syslog message received: ", message)
        date_time = str(pkt.time)
        router_ip = pkt[IP].src
        conn = sqlite3.connect('RouterDatabase.db')
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO SYSLOG (date, time, router_ip, message) 
                                VALUES (?, ?, ?, ?)''', (date_time.split('.')[0], date_time.split('.')[1], router_ip, message))
        conn.commit()
        conn.close()

 

def main():
    database()
    iface = "virbr0" 
    sniff(filter="udp port 514 or udp port 162", prn=lambda pkt: handle_snmp_trap(pkt) if SNMP in pkt else handle_syslog(pkt), iface=iface)

if __name__ == "__main__":
    main()