from time import sleep
from sysbus import sysbus
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import json
import argparse

parser = argparse.ArgumentParser(prog = "sysbus-influxdb")
parser.add_argument("--single", action="store_true")
parser.add_argument("--org")
parser.add_argument("--token")
parser.add_argument("--bucket", default="livebox")
parser.add_argument("--influxurl", default="http://localhost:8086")
parser.add_argument("--delay", type=int, default=60)
args = parser.parse_args()

if not sysbus.load_conf():
    raise RuntimeError("Couldn't load sysbus config")

def auth():
    if not sysbus.auth():
        raise RuntimeError("Couldn't auth")

def postPoints(writeApi, bucket):
    mibs = sysbus.requete('NeMo.Intf.data:getMIBs', { "traverse": "all" })

    wlanvap = mibs["status"]["wlanvap"]

    for intf in mibs["status"]["wlanvap"]:
        for mac in wlanvap[intf]["AssociatedDevice"]:
            dev = wlanvap[intf]["AssociatedDevice"][mac]
            p = Point("devices")
            p.tag("mac", mac)
            p.tag("interface", intf)
            p.field("DownlinkRate", dev["LastDataDownlinkRate"])
            p.field("UplinkRate", dev["LastDataUplinkRate"])
            p.field("SignalStrength", dev["SignalStrength"])
            p.field("Noise", dev["Noise"])
            p.field("Inactive", dev["Inactive"])
            writeApi.write(bucket=bucket, record=p)

client = InfluxDBClient(url=args.influxurl, token=args.token, org=args.org)
writeApi = client.write_api(write_options=SYNCHRONOUS)

auth()
if args.single:
    postPoints(writeApi, args.bucket)
else:
    while True:
        postPoints(writeApi, args.bucket)
        sleep(args.delay)

