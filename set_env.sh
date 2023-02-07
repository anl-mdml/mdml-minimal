# CHANGE these lines as necessary
export MDML_HOST=[HOST IP ADDRESS]
export MDML_SCHEMA_HOST=[HOST IP ADDRESS]

export KAFKA_DATA_PATH="[PATH TO REPO]/mdml-minimal/kafka/data"

export ZOOKEEPER_DATA_PATH="[PATH TO REPO]/mdml-minimal/zookeeper/data"
export ZOOKEEPER_LOG_PATH="[PATH TO REPO]/mdml-minimal/zookeeper/log"

export POSTGRES_DATA_PATH="[PATH TO REPO]/mdml-minimal/postgres"

export MDML_GRAFANA_SECRET="password"
export MDML_GRAFDB_SECRET="password"
export MDML_GRAFDB_ROOT_SECRET="password"
export POSTGRES_PASSWORD="password"

sudo rm -f $KAFKA_DATA_PATH/meta.properties

