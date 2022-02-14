# mdml-minimal
Minimal working version of the MDML with Kafka (Additional services from Confluent), Grafana, Postgres, and two custom services for collecting and replaying experimental data. 

## Installation
* clone the repo and cd into it
* `source init_dirs.sh`
* edit set_env.sh file to machine's configuration
* `source set_env.sh`
* `docker-compose up`

## Getting started
Use the tutorial Jupyter Notebook in the python_scripts/examples folder to start interacting with your MDML instance. Remember to change the connection configuration parameters.

## PostgreSQL
A Postgres DB is included in the MDML for use with Kafka Connectors. A Kafka Connector routes messages streamed in Kafka to external storage solutions or vice versa. If a schema is registered to a topic, messages on that topic can automatically be inserted into Postgres database tables. One caveat being that the message's structure is a dictionary where all of the values in the dictionary are numbers, strings, or booleans - no lists or nested dictionaries.

## Grafana
Go to http://YOUR_HOST:3000/login and log in as `admin` with the password you configured in `set_env.sh`. Create a new data source and configure it to pull from the Postgres database. Now, assuming a connector has been created for your data topics, Grafana can query the Postgres table containing the Kafka streaming data. This allows the creation of real-time data monitoring dashboards. 

## Kafka Connectors
Use the scripts provided in the `python_scripts/administration` folder to manage connectors for your data topics. You will need a JDBC connector to link Postgres and Kafka. Check out all of the free, community and licensed Kafka Connectors at [Confluent Hub](https://www.confluent.io/hub/).
