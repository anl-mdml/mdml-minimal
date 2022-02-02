#!/usr/bin/env python

import argparse

def main(args):
    # delete connector with 
    # curl -X DELETE http://merf.egs.anl.gov:8083/connectors/<connector-name>
    import os
    os.system(f"curl -X DELETE http://{args.server}:{args.port}/connectors/{args.name}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Admin tool to delete a Kafka Connector")
    parser.add_argument('-n', dest="name", required=True,
                        help="Name of the Kafka connector to delete")
    parser.add_argument('-s', dest="server", required=True,
                        help="Kafka connect server")
    parser.add_argument('-p', dest="port", default=8083,
                        help="Kafka Connect port number")

    main(parser.parse_args())