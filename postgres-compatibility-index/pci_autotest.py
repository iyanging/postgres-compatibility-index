import json
import os
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum

import psycopg2
import psycopg2._psycopg
import psycopg2.errors
from tabulate import tabulate


def get_connection(host: str, port: int, user: str, password: str, dbname: str):
    """Establish and return a PostgreSQL connection."""
    return psycopg2.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        dbname=dbname,
    )


class UndefinedType: ...


Undefined = UndefinedType()


@dataclass(kw_only=True)
class Feature:
    name: str
    exams: "list[Examination]"

    def test(self, cursor: psycopg2._psycopg.cursor) -> "Support":
        supports: list[Support] = []

        for exam in self.exams:
            try:
                cursor.execute(exam.statement)
                result = cursor.fetchone()

            except psycopg2.errors.Error as e:
                if (
                    isinstance(e, psycopg2.errors.ProgrammingError)
                    and str(e) == "no results to fetch"
                    and exam.expect is Undefined
                ):
                    this_support = Support.FULL

                else:
                    this_support = Support.NO

            else:
                if not isinstance(exam.expect, UndefinedType):
                    if str(result) == exam.expect:
                        this_support = Support.FULL
                    else:
                        this_support = Support.NO

                else:
                    this_support = Support.FULL

            if this_support == Support.NO:
                return Support.NO

            else:
                supports.append(this_support)

        if all(s == Support.FULL for s in supports):
            return Support.FULL

        else:
            return Support.PARTIAL


@dataclass
class Examination:
    statement: str
    expect: str | UndefinedType = field(default=Undefined)


class Support(float, Enum):
    NO = 0.0
    PARTIAL = 0.5
    FULL = 1.0


class Catalog:
    class DataTypes:
        PrimitiveTypes = Feature(
            name="Primitive Types",
            exams=[Examination("CREATE TABLE test_primitive (id INT, name TEXT);")],
        )
        ComplexTypes = Feature(
            name="Complex Types",
            exams=[Examination("CREATE TYPE test_complex AS (x INT, y TEXT);")],
        )
        JSONB = Feature(
            name="JSONB",
            exams=[Examination("CREATE TABLE test_jsonb (data JSONB);")],
        )
        GeospatialTypes = Feature(
            name="Geospatial Types",
            exams=[
                Examination(
                    "CREATE EXTENSION IF NOT EXISTS postgis; CREATE TABLE test_geo (geom GEOMETRY);"
                )
            ],
        )
        CustomTypes = Feature(
            name="Custom Types",
            exams=[
                Examination("CREATE TYPE mood AS ENUM ('happy', 'sad', 'neutral');")
            ],
        )
        FullTextSearch = Feature(
            name="Full-Text Search",
            exams=[Examination("CREATE TABLE test_fts (content TSVECTOR);")],
        )
        Vector = Feature(
            name="Vector",
            exams=[
                Examination(
                    "CREATE EXTENSION IF NOT EXISTS vector; CREATE TABLE test_vector (embedding VECTOR(3));"
                )
            ],
        )

    class DDLFeatures:
        Schemas = Feature(
            name="Schemas",
            exams=[
                Examination(
                    "DROP SCHEMA IF EXISTS test_schema CASCADE; CREATE SCHEMA test_schema;"
                )
            ],
        )
        Sequences = Feature(
            name="Sequences",
            exams=[Examination("CREATE SEQUENCE test_seq START 1;")],
        )
        Views = Feature(
            name="Views",
            exams=[Examination("CREATE VIEW test_view AS SELECT 1 AS col;")],
        )
        MaterializedViews = Feature(
            name="Materialized Views",
            exams=[
                Examination("CREATE MATERIALIZED VIEW test_matview AS SELECT 1 AS col;")
            ],
        )

    class SQLFeatures:
        CTEs = Feature(
            name="CTEs",
            exams=[Examination("WITH cte AS (SELECT 1 AS val) SELECT * FROM cte;")],
        )
        Upsert = Feature(
            name="Upsert",
            exams=[
                Examination(
                    "CREATE TABLE test_upsert (id INT PRIMARY KEY, data TEXT); INSERT INTO test_upsert VALUES (1, 'test') ON CONFLICT (id) DO UPDATE SET data = 'updated';"
                )
            ],
        )
        WindowFunctions = Feature(
            name="Window Functions",
            exams=[
                Examination("SELECT ROW_NUMBER() OVER (PARTITION BY 1 ORDER BY 1);")
            ],
        )
        Subqueries = Feature(
            name="Subqueries",
            exams=[
                Examination("SELECT * FROM (SELECT 1) AS sub WHERE 1 = (SELECT 1);")
            ],
        )

    class ProceduralFeatures:
        StoredProcedures = Feature(
            name="Stored Procedures",
            exams=[
                Examination(
                    "CREATE PROCEDURE test_proc() LANGUAGE SQL AS $$ SELECT 1; $$; CALL test_proc();"
                )
            ],
        )
        Functions = Feature(
            name="Functions",
            exams=[
                Examination(
                    "DROP FUNCTION IF EXISTS test_func();CREATE FUNCTION test_func() RETURNS INT LANGUAGE SQL AS $$ SELECT 1; $$; SELECT test_func();"
                ),
                Examination(
                    "DROP FUNCTION IF EXISTS test_func_plpgsql();CREATE FUNCTION test_func_plpgsql() RETURNS void LANGUAGE plpgsql AS $$ begin null; end; $$; SELECT test_func_plpgsql();"
                ),
            ],
        )
        Triggers = Feature(
            name="Triggers",
            exams=[
                Examination(
                    "CREATE TABLE test_trig (id INT); CREATE FUNCTION test_trigger() RETURNS TRIGGER LANGUAGE plpgsql AS $$ BEGIN RETURN NEW; END; $$; CREATE TRIGGER trg BEFORE INSERT ON test_trig FOR EACH ROW EXECUTE FUNCTION test_trigger();"
                )
            ],
        )

    class TransactionFeatures:
        ACIDCompliance = Feature(
            name="ACID Compliance",
            exams=[
                Examination(
                    "BEGIN; INSERT INTO test_primitive VALUES (1, 'test'); ROLLBACK;"
                )
            ],
        )
        IsolationLevels = Feature(
            name="Isolation Levels",
            exams=[
                Examination(
                    "BEGIN; SET TRANSACTION ISOLATION LEVEL SERIALIZABLE; SET TRANSACTION ISOLATION LEVEL READ COMMITTED; ROLLBACK;"
                )
            ],
        )
        NestedTransactions = Feature(
            name="Nested Transactions",
            exams=[Examination("BEGIN; SAVEPOINT sp; RELEASE SAVEPOINT sp;")],
        )
        RowLevelLocking = Feature(
            name="Row-Level Locking",
            exams=[Examination("SELECT * FROM test_primitive FOR UPDATE;")],
        )

    class Extensions:
        ExtensionSupport = Feature(
            name="Extension Support",
            exams=[
                Examination("CREATE EXTENSION IF NOT EXISTS pg_trgm;"),
                Examination(
                    "select coalesce((select 1 from pg_available_extensions where name ='pg_trgm'),0)",
                    "(1,)",
                ),
            ],
        )
        ForeignDataWrappers = Feature(
            name="Foreign Data Wrappers",
            exams=[
                Examination("CREATE EXTENSION IF NOT EXISTS postgres_fdw;"),
                Examination(
                    "select coalesce((select 1 from pg_available_extensions where name ='postgres_fdw'),0)",
                    "(1,)",
                ),
            ],
        )

    class Performance:
        IndexTypes = Feature(
            name="Index Types",
            exams=[
                Examination(
                    "CREATE INDEX test_btree ON test_primitive USING btree (id);"
                ),
                Examination("CREATE INDEX test_gin ON test_jsonb USING gin (data);"),
                Examination("CREATE INDEX test_gist ON test_fts USING gist (content);"),
                Examination(
                    "CREATE INDEX test_hash ON test_primitive USING hash (id);"
                ),
            ],
        )
        # TODO:
        # Partitioning = Feature(
        #     name="Partitioning",
        #     exams=[
        #         Examination(
        #             """CREATE TABLE test_part (id INT) PARTITION BY RANGE (id);
        #                         CREATE TABLE test_part1 PARTITION OF test_part FOR VALUES FROM (1) TO (100);
        #                         CREATE TABLE test_part2 PARTITION OF test_part FOR VALUES FROM (101) TO (200);
        #                         ANALYZE test_part;
        #                         EXPLAIN (FORMAT JSON) SELECT * FROM test_part WHERE id = 150;""",
        #             expect=lambda x: "test_part2" in json.dumps(x[0])
        #             and "test_part1" not in json.dumps(x[0]),
        #         )
        #     ],
        # )
        ParallelQueryExecution = Feature(
            name="Parallel Query Execution",
            exams=[
                Examination(
                    "SET max_parallel_workers = 4; SET max_parallel_workers_per_gather=4; SELECT COUNT(*) FROM generate_series(1, 50000) t(id);"
                )
            ],
        )
        # TODO:
        # UnloggedTable = Feature(
        #     name="Unlogged Table",
        #     exams=[
        #         Examination(
        #             """DROP TABLE IF EXISTS unlogged_pci_demo;
        #                         CREATE UNLOGGED TABLE unlogged_pci_demo(n int primary key,flag char,text text);
        #                         SELECT pg_current_wal_lsn() FROM pg_stat_database WHERE datname=current_database();"""
        #         ),
        #         Examination(
        #             """INSERT INTO unlogged_pci_demo SELECT generate_series, 'N',lpad('x',generate_series,'x') FROM generate_series(1,10000);
        #                         SELECT (pg_wal_lsn_diff(pg_current_wal_lsn(),%s)) FROM pg_stat_database WHERE datname=current_database();""",
        #             expect=lambda x: x[0] < 50000,
        #         ),
        #     ],
        # )

    class Constraints:
        ForeignKey = Feature(
            name="Foreign Key",
            exams=[
                Examination(
                    "CREATE TABLE parent (id INT PRIMARY KEY); CREATE TABLE child (parent_id INT , CONSTRAINT fk_customer FOREIGN KEY(parent_id) REFERENCES parent(id));"
                )
            ],
        )
        Check = Feature(
            name="Check",
            exams=[Examination("CREATE TABLE test_check (id INT CHECK (id > 0));")],
        )
        NotNull = Feature(
            name="Not Null",
            exams=[Examination("CREATE TABLE test_notnull (id INT NOT NULL);")],
        )
        Unique = Feature(
            name="Unique",
            exams=[Examination("CREATE TABLE test_unique (id INT UNIQUE);")],
        )
        Exclusion = Feature(
            name="Exclusion",
            exams=[
                Examination(
                    "CREATE EXTENSION IF NOT EXISTS btree_gist; CREATE TABLE test_exclusion (id int, t text, ts tstzrange, EXCLUDE USING gist ((CASE WHEN t ='A' THEN true END) WITH =,ts WITH &&));"
                )
            ],
        )

    class Security:
        RoleManagement = Feature(
            name="Role Management",
            exams=[Examination("CREATE ROLE test_role; DROP ROLE test_role;")],
        )
        GrantRevokePrivileges = Feature(
            name="GRANT/REVOKE Privileges",
            exams=[Examination("GRANT SELECT ON test_primitive TO PUBLIC;")],
        )
        RowLevelSecurity = Feature(
            name="Row-Level Security",
            exams=[
                Examination("ALTER TABLE test_primitive ENABLE ROW LEVEL SECURITY;")
            ],
        )

    class Replication:
        # TODO:
        # LogicalReplication = Feature(
        #     name="Logical Replication",
        #     exams=[
        #         Examination(
        #             "CREATE TABLE test_replication (id INT PRIMARY KEY, value TEXT); CREATE PUBLICATION test_pub FOR TABLE test_replication WHERE (id > 10 and value <>'UNKNOWN');"
        #         ),
        #         Examination(
        #             "SELECT pubname, puballtables, pubinsert, pubupdate, pubdelete FROM pg_publication WHERE pubname = 'test_pub';",
        #             expect=lambda x: x is not None and x[0] == "test_pub",
        #         ),
        #     ],
        # )
        ...

    @classmethod
    def get_category(cls, feature: Feature) -> str:
        for category_name, category in vars(cls).items():
            if not isinstance(category, type):
                continue

            for feat in vars(category).values():
                if not isinstance(feat, Feature):
                    continue

                if feat is feature:
                    return category_name

        raise ValueError("Cannot find feature: " + feature.name)


# Continue with schema creation, PCI calculations, and detailed reporting (same structure as earlier).
def calculate_pci(
    features: dict[str, dict[str, Support]],
) -> tuple[float, list[tuple[str, str]]]:
    """
    Calculate the PCI score based on feature test results.
    """
    total_score = 0
    total_weight = sum(len(category) for category in features.values())
    failed_tests: list[tuple[str, str]] = []

    for category, feature_list in features.items():
        category_score = 0

        for feature in feature_list:
            result = features[category][feature]
            category_score += result

            if result == Support.NO:
                failed_tests.append((category, feature))

        total_score += category_score

    percentage = total_score / total_weight * 100

    return round(percentage, 2), failed_tests


def print_summary(pci_score: float, failed_tests: list[tuple[str, str]]) -> None:
    """Print a detailed summary of the PCI results."""
    print("\n==================== PCI SUMMARY REPORT ====================")
    print(f"Overall PCI Score: {pci_score}%\n")

    if failed_tests:
        print("Failed Features:\n")
        print(tabulate(failed_tests, headers=["Category", "Feature"], tablefmt="grid"))
    else:
        print("All features passed successfully!\n")
    print("==========================================================\n")


def main():
    tests = [
        Catalog.DataTypes.PrimitiveTypes,
        Catalog.DataTypes.ComplexTypes,
        Catalog.DataTypes.JSONB,
        # Catalog.DataTypes.GeospatialTypes,
        Catalog.DataTypes.CustomTypes,
        Catalog.DataTypes.FullTextSearch,
        # Catalog.DataTypes.Vector,
        Catalog.DDLFeatures.Schemas,
        Catalog.DDLFeatures.Sequences,
        Catalog.DDLFeatures.Views,
        Catalog.DDLFeatures.MaterializedViews,
        Catalog.SQLFeatures.CTEs,
        Catalog.SQLFeatures.Upsert,
        Catalog.SQLFeatures.WindowFunctions,
        Catalog.SQLFeatures.Subqueries,
        Catalog.ProceduralFeatures.StoredProcedures,
        Catalog.ProceduralFeatures.Functions,
        Catalog.ProceduralFeatures.Triggers,
        Catalog.Performance.IndexTypes,
        Catalog.Performance.ParallelQueryExecution,
        Catalog.Constraints.ForeignKey,
        Catalog.Constraints.Check,
        Catalog.Constraints.NotNull,
        Catalog.Constraints.Unique,
        Catalog.Constraints.Exclusion,
        Catalog.Security.RoleManagement,
        Catalog.Security.GrantRevokePrivileges,
        Catalog.Security.RowLevelSecurity,
        Catalog.TransactionFeatures.ACIDCompliance,
        Catalog.TransactionFeatures.IsolationLevels,
        Catalog.TransactionFeatures.NestedTransactions,
        Catalog.TransactionFeatures.RowLevelLocking,
    ]

    # PostgreSQL connection parameters from environment variables or defaults
    PG_HOST = os.getenv("PG_HOST", "localhost")
    PG_PORT = os.getenv("PG_PORT", 5432)
    PG_USER = os.getenv("PG_USER", "postgres")
    PG_PASSWORD = os.getenv("PG_PASSWORD", "postgres")
    PG_DBNAME = os.getenv("PG_DBNAME", "compat_test")

    connection = get_connection(PG_HOST, int(PG_PORT), PG_USER, PG_PASSWORD, PG_DBNAME)
    connection.autocommit = True
    cursor = connection.cursor()

    cursor.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")

    # Run tests
    pci_results: dict[str, dict[str, Support]] = defaultdict(dict)
    for feature in tests:
        pci_results[Catalog.get_category(feature)][feature.name] = feature.test(cursor)

    pci_results = dict(pci_results)

    print(pci_results)
    # Calculate PCI score
    pci_score, failed_tests = calculate_pci(pci_results)
    print_summary(pci_score, failed_tests)

    # Save results
    with open("pci_report.json", "w") as report_file:
        json.dump(
            {"pci_score": pci_score, "details": pci_results}, report_file, indent=4
        )

    print("PCI testing completed. Report saved as 'pci_report.json'.")

    cursor.close()
    connection.close()


if __name__ == "__main__":
    main()
