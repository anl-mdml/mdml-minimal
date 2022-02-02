import os
from adc_sdk.client import ADCClient
import argparse
parser = argparse.ArgumentParser(description="Argparse")
parser.add_argument('-i', dest="user_id", required=True, help="ADC User ID")
parser.add_argument('-l', dest="level", required=True, choices=['read','write','access'],help="access level")
args = parser.parse_args()   

# Upload to Argonne Data Cloud                
client = ADCClient(os.environ['ADC_ACCESS_TOKEN'])

# MDML Study - U3R1ZHlOb2RlOjMx
client.set_permissions('U3R1ZHlOb2RlOjMx', args.user_id, "read")