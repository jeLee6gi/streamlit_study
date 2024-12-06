import argparse
import os
import sqlite3

from munch import Munch


def main(config_path):
    """Creates a new empty database for the study implemented in config_path

    This database keeps track of known mappings between user_id and their
    assigned instance_ids in a table called `mapping` as well as the
    participant completion status in a table called `participant_status`
    """
    # parse the config file to get the configured db path
    config = Munch.fromYAML(open(config_path))

    # don't create the database if the file already exists
    assert not os.path.exists(config.paths.db)
    con = sqlite3.connect(config.paths.db)

    with con:
        cur = con.cursor()

        # create empty mapping table
        cur.execute("CREATE TABLE mapping(user_id TEXT, instance_ids JSON1)")

        # create pre-filled data table
        cur.execute("CREATE TABLE participant_status(user_id TEXT, status TEXT)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("config_path")

    args = parser.parse_args()

    main(args.config_path)
