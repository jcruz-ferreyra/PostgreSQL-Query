import argparse
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine


def make_query(query=None, query_file=False, dest_filename=None, save=False):
    assert query, "No query provided"

    main_path = Path.cwd() / ".."

    # check if destination and temp folders exists. create them if not.
    if not os.path.isdir(main_path / "data"):
        os.makedirs(main_path / "data")
    if not os.path.isdir(main_path / "source"):
        print("python script should be located in 'source' folder")

    # -- ENVIRONMENT VARIABLES --
    # load environment variables with python-dotenv module.
    load_dotenv()

    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_pass = os.getenv("DB_PASS")

    # -- SCRIPT --
    # create engine to make the connection with the database.
    engine = create_engine(
        f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    )
    # read the sql script into a pandas dataframe.
    print("Starting query\n")
    if query_file:
        query_reader = open(main_path / f"source/{query}", "r")
        query = query_reader.read()

    df_query = pd.read_sql_query(query, engine)

    if save:
        print("Saving result\n")

        dest_filename_split = dest_filename.rsplit("/", 1)
        if len(dest_filename_split) > 1:
            dest_folder = dest_filename_split[0]
            if not os.path.isdir(main_path / "data" / dest_folder):
                os.makedirs(main_path / "data" / dest_folder)

        # write query result into a csv file inside the destination folder.
        df_query.to_csv(main_path / f"data/{dest_filename}.csv", index=False)

    return df_query


if __name__ == "__main__":
    """python query.py --query-filename test --dest-filename test"""
    parser = argparse.ArgumentParser(
        description="Retrieve a query from a postgresql database and save results in csv format."
    )

    parser.add_argument(
        "--query",
        required=False,
        help="Query string",
        type=str,
    )
    parser.add_argument(
        "--query-filename",
        required=False,
        help="Name of the sql file",
        type=str,
    )
    parser.add_argument(
        "--dest-filename",
        required=False,
        help="Name of the sql file",
        type=str,
    )

    args = parser.parse_args()
    assert args.query or args.query_filename, "No query nor query filename provided"
    if args.query:
        query_file = False
    else:
        args.query = args.query_filename
        query_file = True

    if args.dest_filename:
        save = True
    else:
        save = False

    make_query(args.query, query_file, args.dest_filename, save)
