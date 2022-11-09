from sysbus import sysbus
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import json
import argparse

parser = argparse.ArgumentParser(prog = "sysbus-influxdb")
parser.add_argument("--org")
parser.add_argument("--token")
parser.add_argument("--bucket", default="livebox")
parser.add_argument("--influxurl", default="http://localhost:8086")

if not sysbus.load_conf():
    raise RuntimeError("Couldn't load sysbus config")
if not sysbus.auth():
    raise RuntimeError("Couldn't auth")

mibs = sysbus.requete('NeMo.Intf.data:getMIBs', { "traverse": "all" })
#print(json.dumps(mibs))

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
        print(p)
