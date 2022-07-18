# CHANGE these lines as necessary
export MDML_HOST="broker"
export MDML_SCHEMA_HOST="schema-registry"

export KAFKA_DATA_PATH="/home/jelias/anl-mdml/mdml-minimal/kafka/data"

export ZOOKEEPER_DATA_PATH="/home/jelias/anl-mdml/mdml-minimal/zookeeper/data"
export ZOOKEEPER_LOG_PATH="/home/jelias/anl-mdml/mdml-minimal/zookeeper/log"

export POSTGRES_DATA_PATH="/home/jelias/anl-mdml/mdml-minimal/postgres"

export MDML_GRAFANA_SECRET="password"
export MDML_GRAFDB_SECRET="password"
export MDML_GRAFDB_ROOT_SECRET="password"
export POSTGRES_PASSWORD="password"

sudo rm $KAFKA_DATA_PATH/meta.properties

