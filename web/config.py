import sys
sys.path.append('/home/pi/NOMAD/')
from network import get_ip

LOCAL_DNS_HOST = str(get_ip())
LOCAL_DNS_PORT = '5000'