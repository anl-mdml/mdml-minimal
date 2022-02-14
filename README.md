# mdml-minimal
Minimal working version of the MDML with Kafka (additional services from Confluent), Grafana, Postgres, and two custom services for collecting and replaying experimental data. 

## Installation
* clone this repo and cd into it
* run `source init_dirs.sh`
* edit `set_env.sh` file for your host's configuration
* run `source set_env.sh`
* run `docker-compose up`

## Getting started
Use the tutorial Jupyter Notebook in the python_scripts/examples folder to start interacting with your MDML instance. Remember to change the connection configuration parameters. Check out the [Read the Docs](https://mdml-client.readthedocs.io/en/latest/index.html) for the [MDML's Python client](https://github.com/anl-mdml/MDML_Client).

## PostgreSQL
A Postgres DB is included in the MDML for use with Kafka Connectors. A Kafka Connector routes messages streamed in Kafka to external storage solutions or vice versa. If a schema is registered to a topic, messages on that topic can automatically be inserted into Postgres database tables. One caveat being that the message's structure is a dictionary where all of the values in the dictionary are numbers, strings, or booleans - no lists or nested dictionaries.

## Grafana
Go to http://YOUR_HOST:3000/login and log in as `admin` with the password you configured in `set_env.sh`. Create a new data source and configure it to pull from the Postgres database. Now, assuming a connector has been created for your data topics, Grafana can query the Postgres table containing the Kafka streaming data. This allows the creation of real-time data monitoring dashboards. 

## Kafka Connectors
Use the scripts provided in the `python_scripts/administration` folder to manage connectors for your data topics. You will need a JDBC connector to link Postgres and Kafka. Check out all of the free, community and licensed Kafka Connectors at [Confluent Hub](https://www.confluent.io/hub/).
