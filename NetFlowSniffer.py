import sqlite3
from datetime import datetime, timezone
from scapy.layers import netflow
from scapy.layers.netflow import NetflowHeaderV9
from scapy.all import IP, UDP,  sniff, Ether #importing all doesnt work, but doing this, does??

def init_database():
    conn = sqlite3.connect('RouterDatabase.db')
    cursor = conn.cursor()

	#Creates the netflow table
    cursor.execute('''CREATE TABLE IF NOT EXISTS netflow (
						id INTEGER PRIMARY KEY,
						date TEXT,
						time TEXT,
						router_ip TEXT,
						num_packets INTEGER,
						source_ip TEXT,
						destination_ip TEXT,
						protocol TEXT,
						source_port INTEGER,
						destination_port INTEGER
					)''')
    conn.commit()
    conn.close()

def extract_netflow_info(packet):
    if NetflowHeaderV9 in packet and netflow.NetflowDataflowsetV9 in packet:
        netflow_header = packet[NetflowHeaderV9]
        flowset = packet[netflow.NetflowDataflowsetV9]


        for record in flowset.records:
            try: #This section extracts the fields from the netflow, to make them input in the database
                datetimes = packet[NetflowHeaderV9].unixSecs
                date_time = datetime.fromtimestamp(datetimes)
                date = date_time.date()
                time = date_time.time()
                router_ip = packet[IP].src
                num_packets = packet[NetflowHeaderV9].count
                source_ip = packet[IP].src
                destination_ip = packet[IP].dst
                protocol = packet[IP].proto
                source_port = packet[UDP].sport
                destination_port = packet[UDP].dport

                #the part below will store the netflow packet in the database, then prints it
                con = sqlite3.connect("RouterDatabase.db")
                cur = con.cursor()
                con.execute("INSERT INTO netflow(date, time, router_ip, num_packets, source_ip, destination_ip, protocol, source_port, destination_port) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) ",
                            (str(date), str(time), str(router_ip), num_packets, str(source_ip), str(destination_ip), str(protocol), str(source_port), str(destination_port) ))
                print("date\t\ttime\t\tip\t\tnumofpackets\tsource\t\tdest.\t\tprot.\tsourcept\tdestpt")
                print(date, "\t", time, "\t", router_ip, "\t", num_packets, "\t\t", source_ip,"\t", destination_ip,"\t", protocol,"\t", source_port,"\t\t", destination_port)
                con.commit()
                cur.close()
                con.close()

            except AttributeError as x:
                print(f"Error in parsing record: {x}")

if __name__ == "__main__":
    init_database()
    print("Starting NetFlow packet capture...")
    sniff(prn=extract_netflow_info, store=0, filter="udp and port 2055", iface="virbr0") #starts scapy using the function, on port 2055 udp, on interface virbr0