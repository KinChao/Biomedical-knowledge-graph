from typedb.client import *
from schema.initialise import initialise_database
from Migrators.Uniprot.UniprotMigrator import migrate_uniprot
from timeit import default_timer as timer
import argparse


def migrator_parser():
    parser = argparse.ArgumentParser(
        description='Define bio_covid database and insert data by calling separate migrate scripts.')
    parser.add_argument("-n", "--num_threads", type=int,
                        help="Number of threads to enable multi-threading (default: 8)", default=8)
    parser.add_argument("-c", "--commit_batch", help="Sets the number of queries made per commit (default: 50)",
                        default=50)
    parser.add_argument("-d", "--database", help="Database name (default: bio-covid)", default="bio_covid")
    parser.add_argument("-f", "--force",
                        help="Force overwrite the database even if a database by this name already exists (default: False)",
                        default=False)
    parser.add_argument("-a", "--address", help="Server host address (default: localhost)", default="localhost")
    parser.add_argument("-p", "--port", help="Server port (default: 1729)", default="1729")
    parser.add_argument("-v", "--verbose", help="Verbosity (default: False)", default=False)
    return parser


NUM_PROTEINS = 1000000  # Total proteins to migrate (There are total of 20350 proteins)
NUM_DIS = 1000000  # Total diseases to migrate
NUM_DR = 1000000  # Total drug to migrate (32k total)
NUM_INT = 1000000  # Total drug-gene interactions to migrate (42k total)
NUM_PATH = 1000000  # Total pathway associations to migrate
NUM_TN = 1000000  # Total TissueNet being migrated
NUM_PA = 1000000  #  Total Tissues <> Genes to migrate
NUM_NER = 1000000  # Total number of publications (authors: 110k; journals: 1.7k; publications: 29k)
NUM_SEM = 1000000  # Total number of rows from Semmed to migrate

start = timer()
if __name__ == "__main__":
    parser = migrator_parser()
    args = parser.parse_args()

    # This is a global flag toggling counter and query printouts when we want to see less detail
    verbose = args.verbose

    uri = args.address + ":" + args.port
    client = TypeDB.core_client(uri)

    initialise_database(client, args.database, args.force)

    with client.session(args.database, SessionType.DATA) as session:
        migrate_uniprot(session, NUM_PROTEINS, args.num_threads, args.commit_batch)

# add tissueNet?
# add CORD-19?
end = timer()
time_in_sec = end - start
print("Elapsed time: " + str(time_in_sec) + " seconds.")
