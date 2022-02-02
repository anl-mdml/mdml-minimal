#!/usr/bin/env python

import argparse

def main(args):
    # get connectors with
    # curl GET http://merf.egs.anl.gov:8083/connector-plugins
    import os
    print(os.system(f"curl http://{args.server}:{args.port}/connector-plugins"))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Admin tool to list Kafka Connectors")
    parser.add_argument('-s', dest="server", required=True,
                        help="Kafka connect server")
    parser.add_argument('-p', dest="port", default=8083,
                        help="Kafka Connect port number")
    main(parser.parse_args())
