SELF_PATH := $(abspath $(lastword $(MAKEFILE_LIST)))
SELF_DIR := $(dir $(SELF_PATH))

test_postgres: PG_HOST=localhost
test_postgres: PG_PORT=54320
test_postgres: PG_USER=postgres
test_postgres: PG_PASSWORD=postgres
test_postgres: PG_DBNAME=compat_test
test_postgres:
	- PGPASSWORD=${PG_PASSWORD} createdb -h ${PG_HOST} -p ${PG_PORT} -U ${PG_USER} ${PG_DBNAME}

	PG_HOST=${PG_HOST} \
	PG_PORT=${PG_PORT} \
	PG_USER=${PG_USER} \
	PG_PASSWORD=${PG_PASSWORD} \
	PG_DBNAME=${PG_DBNAME} \
	uv run --directory ${SELF_DIR} ${SELF_DIR}/postgres-compatibility-index/pci_autotest.py

benchmark_postgres: PG_HOST=localhost
benchmark_postgres: PG_PORT=54320
benchmark_postgres: PG_USER=postgres
benchmark_postgres: PG_PASSWORD=postgres
benchmark_postgres: PG_DBNAME=pgbench
benchmark_postgres:
	- PGPASSWORD=${PG_PASSWORD} createdb -h ${PG_HOST} -p ${PG_PORT} -U ${PG_USER} ${PG_DBNAME}

	PGPASSWORD=${PG_PASSWORD} pgbench -i -I dtpfgv -h ${PG_HOST} -p ${PG_PORT} -U ${PG_USER} -d ${PG_DBNAME}
	PGPASSWORD=${PG_PASSWORD} pgbench -c 5 -j 5 -M prepared -T 30 -h ${PG_HOST} -p ${PG_PORT} -U ${PG_USER} -d ${PG_DBNAME}

test_polardb: PG_HOST=localhost
test_polardb: PG_PORT=54321
test_polardb: PG_USER=postgres
test_polardb: PG_PASSWORD=postgres
test_polardb: PG_DBNAME=compat_test
test_polardb:
	- PGPASSWORD=${PG_PASSWORD} createdb -h ${PG_HOST} -p ${PG_PORT} -U ${PG_USER} ${PG_DBNAME}

	PG_HOST=${PG_HOST} \
	PG_PORT=${PG_PORT} \
	PG_USER=${PG_USER} \
	PG_PASSWORD=${PG_PASSWORD} \
	PG_DBNAME=${PG_DBNAME} \
	uv run --directory ${SELF_DIR} ${SELF_DIR}/postgres-compatibility-index/pci_autotest.py

benchmark_polardb: PG_HOST=localhost
benchmark_polardb: PG_PORT=54321
benchmark_polardb: PG_USER=postgres
benchmark_polardb: PG_PASSWORD=postgres
benchmark_polardb: PG_DBNAME=pgbench
benchmark_polardb:
	- PGPASSWORD=${PG_PASSWORD} createdb -h ${PG_HOST} -p ${PG_PORT} -U ${PG_USER} ${PG_DBNAME}

	PGPASSWORD=${PG_PASSWORD} pgbench -i -I dtpfgv -h ${PG_HOST} -p ${PG_PORT} -U ${PG_USER} -d ${PG_DBNAME}
	PGPASSWORD=${PG_PASSWORD} pgbench -c 5 -j 5 -M prepared -T 30 -h ${PG_HOST} -p ${PG_PORT} -U ${PG_USER} -d ${PG_DBNAME}

test_kingbase: PG_HOST=localhost
test_kingbase: PG_PORT=54322
test_kingbase: PG_USER=postgres
test_kingbase: PG_PASSWORD=postgres
test_kingbase: PG_DBNAME=compat_test
test_kingbase:
	- PGPASSWORD=${PG_PASSWORD} createdb -h ${PG_HOST} -p ${PG_PORT} -U ${PG_USER} ${PG_DBNAME}

	PG_HOST=${PG_HOST} \
	PG_PORT=${PG_PORT} \
	PG_USER=${PG_USER} \
	PG_PASSWORD=${PG_PASSWORD} \
	PG_DBNAME=${PG_DBNAME} \
	uv run --directory ${SELF_DIR} ${SELF_DIR}/postgres-compatibility-index/pci_autotest.py

benchmark_kingbase: PG_HOST=localhost
benchmark_kingbase: PG_PORT=54322
benchmark_kingbase: PG_USER=postgres
benchmark_kingbase: PG_PASSWORD=postgres
benchmark_kingbase: PG_DBNAME=pgbench
benchmark_kingbase:
	- PGPASSWORD=${PG_PASSWORD} createdb -h ${PG_HOST} -p ${PG_PORT} -U ${PG_USER} ${PG_DBNAME}

	PGPASSWORD=${PG_PASSWORD} pgbench -i -I dtpfgv -h ${PG_HOST} -p ${PG_PORT} -U ${PG_USER} -d ${PG_DBNAME}
	PGPASSWORD=${PG_PASSWORD} pgbench -c 5 -j 5 -M prepared -T 30 -h ${PG_HOST} -p ${PG_PORT} -U ${PG_USER} -d ${PG_DBNAME}

test_mogdb: PG_HOST=localhost
test_mogdb: PG_PORT=54324
test_mogdb: PG_USER=mogdb
test_mogdb: PG_PASSWORD=Enmo@123
test_mogdb: PG_DBNAME=compat_test
test_mogdb:
	- PGPASSWORD=${PG_PASSWORD} psql -h ${PG_HOST} -p ${PG_PORT} -U ${PG_USER} -c "CREATE DATABASE ${PG_DBNAME} DBCOMPATIBILITY='PG' ENCODING='UTF8'"

	PG_HOST=${PG_HOST} \
	PG_PORT=${PG_PORT} \
	PG_USER=${PG_USER} \
	PG_PASSWORD=${PG_PASSWORD} \
	PG_DBNAME=${PG_DBNAME} \
	uv run --directory ${SELF_DIR} ${SELF_DIR}/postgres-compatibility-index/pci_autotest.py

benchmark_mogdb: PG_HOST=localhost
benchmark_mogdb: PG_PORT=54324
benchmark_mogdb: PG_USER=mogdb
benchmark_mogdb: PG_PASSWORD=Enmo@123
benchmark_mogdb: PG_DBNAME=pgbench
benchmark_mogdb:
	- PGPASSWORD=${PG_PASSWORD} psql -h ${PG_HOST} -p ${PG_PORT} -U ${PG_USER} -c "CREATE DATABASE ${PG_DBNAME} DBCOMPATIBILITY='PG' ENCODING='UTF8'"

	PGPASSWORD=${PG_PASSWORD} pgbench -i -I dtpfgv -h ${PG_HOST} -p ${PG_PORT} -U ${PG_USER} -d ${PG_DBNAME}
	PGPASSWORD=${PG_PASSWORD} pgbench -c 5 -j 5 -M prepared -T 30 -h ${PG_HOST} -p ${PG_PORT} -U ${PG_USER} -d ${PG_DBNAME}
