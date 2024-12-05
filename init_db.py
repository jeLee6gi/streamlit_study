import argparse
import os
import sqlite3

import munch


def main(config_path):
    # parse the config file
    config = munch.Munch.fromYAML(open(config_path))

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
