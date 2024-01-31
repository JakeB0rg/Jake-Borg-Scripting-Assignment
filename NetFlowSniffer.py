from scapy.all import *
import sqlite3
import datetime

# Database setup
conn = sqlite3.connect('router_database.db')
c = conn.cursor()

# Create table if not exists
c.execute('''CREATE TABLE IF NOT EXISTS netflow_data
             (id INTEGER PRIMARY KEY,
             date TEXT,
             time TEXT,
             router_ip TEXT,
             num_packets INTEGER,
             source_ip TEXT,
             dest_ip TEXT,
             protocol TEXT,
             source_port INTEGER,
             dest_port INTEGER)''')
conn.commit()

# Function to handle Netflow packets
def handle_netflow_packet(packet):
    if packet.haslayer(NetflowHeader):
        header = packet[NetflowHeader]
        if header.version == 9:
            for flowset in packet[NetflowPacket].templates:
                for flow in packet[NetflowPacket].templates[flowset]:
                    date = datetime.datetime.now().date()
                    time = datetime.datetime.now().time()
                    router_ip = packet[IP].src
                    num_packets = 0  # Adjust accordingly based on available fields
                    source_ip = flow.fields.get('ipv4_src_addr', 'Unknown')
                    dest_ip = flow.fields.get('ipv4_dst_addr', 'Unknown')
                    protocol = flow.fields.get('protocol', 'Unknown')
                    source_port = flow.fields.get('l4_src_port', 'Unknown')
                    dest_port = flow.fields.get('l4_dst_port', 'Unknown')

                    # Save data to database
                    c.execute("INSERT INTO netflow_data (date, time, router_ip, num_packets, source_ip, dest_ip, protocol, source_port, dest_port) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                              (date, time, router_ip, num_packets, source_ip, dest_ip, protocol, source_port, dest_port))
                    conn.commit()
                    print("[+] Data saved to database")

# Start sniffing Netflow packets
print("[*] Starting NetFlowSniffer.py...")
sniff(filter="udp and port 2055", prn=handle_netflow_packet, store=0)

# Close database connection
conn.close()
