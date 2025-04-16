# PostgreSQL Compatibility Index (PCI)

This repository provides a standardized method to evaluate the compatibility of a database system with PostgreSQL using fixed feature categories and scoring rules.

PostgreSQL 17 is used for baseline.

A visualization of the up-to-date results can be found on "PG Sorecard"  :  [pgscorecard](https://pgscorecard.com/)

Origin story in a blog format => [drunkdba.medium.com/postgres-is-3cbae80c84a3](https://drunkdba.medium.com/postgres-is-3cbae80c84a3?source=friends_link&sk=995c021ce85ca67a3494551a1efb3de9)

[Philosophy behind "Postgres-Compatibility-Index"](https://drunkdba.medium.com/the-making-of-postgres-is-5034c0dc4639?source=friends_link&sk=701e1db2c908fb22d3afdc8dc41f0f2e)

Update: In response to a trademark notice from the PostgreSQL Community Association of Canada, domain has been changed from “Postgres.Is” to "pgscorecard.com"

## Methodology

The PCI evaluates a fixed set of PostgreSQL features across 12 categories. Each feature is scored as:
- `full` (1.0)
- `partial` (0.5)
- `no` (0.0)

The final PCI score is a weighted average of the scores for each category.


### Prerequisites
- Python 3.5+, psycopg2, postgresql client and working connection to the database to be tested.
- pip install tabulate
- Install postgis, pgvector extension to score more points as in some cases it will require pre-installation.

## Automated scoring
- Set environment variables or provide inline username, connection details of the database where tests are supposed to run.
- You will lose points for extensions that you do not install.
- python3 pci_autotest.py

### Example Output in Tabular Format

**PostgreSQL Compatibility Report**

**Overall Compatibility Score:** `85%`

#### Failed Features:

| **Category**          | **Feature**         |
|------------------------|---------------------|
| `data_types`          | `Vector`            |
| `procedural_features` | `Triggers`          |


## Manual mode example

Manual mode is not recommended unless connectivity issues and last option.

### CockroachDB
/pci/postgres-compatibility-index/postgres-compatibility-index$ python3 pci_calculator.py example_inputs/cockroach.json outputs/cockroachdb_report.txt
- PCI Score: 40.21%
- Detailed report saved to outputs/cockroachdb_report.txt

### DSQL
/pci/postgres-compatibility-index/postgres-compatibility-index$ python3 pci_calculator.py example_inputs/dsql.json outputs/dsql_report.txt
- PCI Score: 21.05%
- Detailed report saved to outputs/dsql_report.txt

### Yugabyte
/pci/postgres-compatibility-index/postgres-compatibility-index$ python3 pci_calculator.py example_inputs/yugabyte.json outputs/yugabytedb_report.txt
- PCI Score: 85.08%
- Detailed report saved to outputs/yugabytedb_report.txt

### AlloyDB
/pci/postgres-compatibility-index/postgres-compatibility-index$ python3 pci_calculator.py example_inputs/alloydb.json outputs/alloydb_report.txt
- PCI Score: 93.17%
- Detailed report saved to outputs/alloydb_report.txt
