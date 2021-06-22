import socket
import sys
import http.client
import time

msg = [
    'M-SEARCH * HTTP/1.1',
    'Host: 239.255.255.250:1900',
    'ST: upnp:rootdevice',
    'Man: "ssdp:discover"',
    'MX: 1',
    ''
]

if(len(sys.argv) == 4):
    flag=sys.argv[1]
    value=sys.argv[2]
    action=sys.argv[3].lower()
    tag=""
#    print("ARGS: ",flag,value,action)
    if(flag=='-c'):
        tag='X-H4-Chip: '+value[-6:].upper()
    elif(flag=='-i'):
        tag="http://"+value+":80/we"
#    elif(flag=='-n'):
#        tag='X-H4-Chip: '
    elif(flag=="-d"):
        tag='X-H4-Device: '+value
    else:
        print("Unknown flag ",flag)
        exit(1)

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s.settimeout(5)
    s.sendto('\r\n'.join(msg).encode(), ('239.255.255.250', 1900))
    spin=True
    while(spin):
        data, addr = s.recvfrom(32*1024)
        udp=data.decode("utf-8").split('\r\n')
        for u in udp:
            if(u.find(tag) != -1):
                ip = "{}".format(*addr)
                conn = http.client.HTTPConnection(ip, 80)
                conn.request("GET","/rest/h4/"+action)
                spin=False
                time.sleep(0.5)
else:
    print("H4/Plugins device actuator (c) 2021 Phil bowles\n")
#    print("Usage: actuate.py [-c] [-i] [-n] [-d] searchvalue [ON|OFF|TOGGLE]")
    print("Usage: actuate.py [-c] [-i] [-d] searchvalue [on|off|toggle]")
    print("Flags (exactly one must present):\n")
    print("c searchvalue is chip ID")
    print("i searchvalue is IP address")
#    print("n searchvalue is UPNP friendly name")
    print("d searchvalue is H4 device name\n")