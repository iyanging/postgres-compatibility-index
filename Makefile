SELF_PATH := $(abspath $(lastword $(MAKEFILE_LIST)))
SELF_DIR := $(dir $(SELF_PATH))

test_postgres:
	PG_HOST=localhost \
	PG_PORT=5432 \
	PG_USER=postgres \
	PG_PASSWORD=postgres \
	PG_DBNAME=compat_test \
	uv run --directory ${SELF_DIR} ${SELF_DIR}/postgres-compatibility-index/pci_autotest.py

test_kingbase:
	PG_HOST=localhost \
	PG_PORT=54321 \
	PG_USER=postgres \
	PG_PASSWORD=postgres \
	PG_DBNAME=compat_test \
	uv run --directory ${SELF_DIR} ${SELF_DIR}/postgres-compatibility-index/pci_autotest.py
