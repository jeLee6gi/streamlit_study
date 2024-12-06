import json
import logging
import os
from pathlib import Path
import random
import sqlite3

import pyrolific

# from pyrolific.api.studies import get_studies, export_study
from pyrolific.api.studies import export_study


logger = logging.getLogger(__name__)


STATUS_BAD = set(["RETURNED", "TIMED-OUT", "REJECTED"])


def load_jsonl(path: Path) -> list[str]:
    data = []
    with open(path) as h:
        for line in h:
            data.append(json.loads(line))

    return data


def get_frequencies(config, data, mapping, rejected):
    logger.info("calculating frequencies for least frequent sampling")
    frequencies = {}
    for instance in data:
        frequencies[instance[config.data.instance_id_key]] = 0

    for user_id, instance_ids in mapping.items():
        if user_id in rejected:
            logger.info("skipping rejected PROLIFIC_PID %s", user_id)
            continue
        logger.debug("adding PROLIFIC_PID %s to frequencies", user_id)
        for instance_id in instance_ids:
            frequencies[instance_id] += 1

    return frequencies


def get_sample(
    config,
    user_id: str,
    frequencies,
):
    logger.debug("starting least frequent sampling")
    sample = set()
    while len(sample) < config.data.instances_per_annotator:
        min_freq = min(frequencies.values())
        candidates = [
            instance_id
            for (instance_id, freq) in frequencies.items()
            if freq == min_freq
        ]
        logger.info("found %s candidates", len(candidates))
        if len(sample) + len(candidates) < config.data.instances_per_annotator:
            for candidate in candidates:
                sample.add(candidate)
                frequencies[candidate] += 1
        else:
            for candidate in random.sample(
                candidates, config.data.instances_per_annotator - len(sample)
            ):
                sample.add(candidate)
                frequencies[candidate] += 1

    assert len(sample) == config.data.instances_per_annotator
    return list(sample)


def load_token_from_file(path):
    with open(path) as h:
        return h.read().strip()


def get_demographics_from_api(config):
    _token = load_token_from_file(config.api.token_file)
    token = f"Token {_token}"

    logger.info("Query prolific API for demographics")
    client = pyrolific.AuthenticatedClient(
        base_url=config.api.url,
        token=token,
    )

    # list all studies
    # res = pyrolific.api.studies.get_studies.sync(client=client, authorization=token)
    # for x in res.results:
    #     print(f"{x.id} [{x.internal_name}] {x.name}")

    demographics = parse_demographics(
        pyrolific.api.studies.export_study.sync(
            config.api.study_id, client=client, authorization=token
        )
    )
    logger.debug("API demographics %s", demographics)

    return demographics


def get_rejected(config, participant_status):
    rejected = set()
    for user_id, status in participant_status.items():
        if status in STATUS_BAD:
            rejected.add(user_id)
    return rejected


def parse_demographics(string):
    participant_status = {}
    header = None
    for line in string.split("\n"):
        line = line.strip()
        if not line:
            continue
        _fields = line.split(",")
        if header is None:
            header = _fields
        else:
            fields = {h: f for h, f in zip(header, _fields)}
            participant_status[fields["Participant id"]] = fields["Status"]
    return participant_status


def get_user_instances(
    config, dataset, user_id: str, dry_run: bool = False
) -> list[str]:
    """Retrieve `instance_ids` from the dataset for the given `user_id`.

    This function makes use of:
    - The prolific Api to query the completion status of `user_id`s
    - A database to cache the mapping from known `user_id`s to their
      assigned `instance_ids` locally

    The logic is as follows:
    - If a `user_id` has been encountered before, retrieve the assigned
    `instance_ids` and return them
    - If a `user_id` is encountered for the first time,
      - query the prolific Api for the latest demgraphic data including
        study completion status
      - inform the sample the about rejected the `user_id`s and assign
        `instance_ids` to the requested `user_id`"""

    # assume the database already exists
    # maybe check for this earlier
    assert os.path.exists(config.paths.db)

    con = sqlite3.connect(config.paths.db)

    # keep db locked while figuring out the mapping for this user
    logger.debug("acquiring db lock")
    with con:
        logger.debug("db lock acquired")
        cur = con.cursor()

        # logger.debug('loading table "data" from DB')
        # res = cur.execute("SELECT bin_id, image_ids FROM data")
        # _data = res.fetchall()
        # data = {}
        # for _bin_id, _user_ids in _data:
        #     user_ids = json.loads(_user_ids)
        #     data[_bin_id] = user_ids

        logger.debug('loading table "mapping" from DB')
        res = cur.execute("SELECT user_id, instance_ids FROM mapping")
        _data = res.fetchall()
        mapping = {}
        for _user_id, _instance_ids in _data:
            instance_ids = json.loads(_instance_ids)
            mapping[_user_id] = instance_ids

        logger.debug('loading table "participant_status" from DB')
        res = cur.execute("SELECT user_id, status FROM participant_status")
        _data = res.fetchall()
        participant_status = {}
        for _user_id, _status in _data:
            participant_status[_user_id] = _status

        # logger.debug("loading rejected PROLIFIC_PIDS from `rejected.txt`")
        # rejected = set()
        # with open("/home/frgl/figure_caption_user_study/rejected.txt") as h:
        #     for line in h:
        #         line = line.strip()
        #         rejected_id, comment = line.split("#")
        #         rejected.add(rejected_id.strip())

        if user_id in mapping:
            logger.info("user_id '%s' found in db, loading sample", user_id)
            sample = mapping[user_id]
        else:
            logger.info("new user_id '%s', creating sample", user_id)
            try:
                _participant_status = get_demographics_from_api(config)
            except:
                pass
            else:
                participant_status = _participant_status
            rejected = get_rejected(config, participant_status)

            frequencies = get_frequencies(config, dataset, mapping, rejected)
            sample = get_sample(config, user_id, frequencies)

            if dry_run:
                logger.info("DRY RUN not saving to DB")
            else:
                logger.info("saving sample to db")
                # save the sample to the database
                cur.execute(
                    f"INSERT INTO mapping VALUES('{user_id}', '{json.dumps(sample)}')",
                )
                # TODO update participant_status in DB as well
                con.commit()
        # logger.debug("sample: %s", sample)
        logger.info(
            "sample stats: len %s, unique len %s, instances %s",
            len(sample),
            len(set(sample)),
            sample,
        )
    logger.debug("db lock released")

    return sample


def get_attention_instances(config):
    return [{"post id"}] * config.data.attention_per_annotator


def _test(db_path: str, user_id: str = "foo"):
    logging.basicConfig(
        format="[%(asctime)s  %(levelname)s  %(name)s  %(funcName)16s()]:  %(message)s",
        datefmt="%d.%m. %H:%M:%S",
        level=logging.DEBUG,
    )

    get_instances({"db_path": db_path}, user_id, dry_run=True)
