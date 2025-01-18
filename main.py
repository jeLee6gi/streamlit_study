import argparse
from functools import partial
import logging
import os

from munch import Munch
import streamlit as st
import streamlit_survey as ss

import data
import content
import input_validation
import utils

logging.basicConfig(
    format="[%(asctime)s  %(levelname)s  %(name)s  %(funcName)16s()]:  %(message)s",
    datefmt="%d.%m. %H:%M:%S",
    level=logging.INFO,
)


def surveyflow(config, config_path, user_id, instances, attentions):
    survey = ss.StreamlitSurvey(config.study.title)

    # restore session state
    if not survey.data:
        os.makedirs(f"results/{config_path}/", exist_ok=True)
        try:
            survey.from_json(f"results/{config_path}/{user_id}.json")
        except:
            pass

    validator = input_validation.Validator()

    num_pages = (
        len(content.intro)
        + len(instances)
        + config.data.attention_per_annotator
        + len(content.outro)
    )

    pages = survey.pages(
        num_pages,
        on_submit=lambda: st.markdown(
            f"<div style='text-align: center'>Thank you for your participation, your responses have been recorded.</div>\n\n<div style='text-align: center'>Please click the following link or use completion code <b>{config.study.completion_code}</b> to finish the study:</div>\n\n<div style='text-align: center'><b><a href=https://app.prolific.com/submissions/complete?cc={config.study.completion_code}>complete study</a></b></div>",
            unsafe_allow_html=True,
        ),
    )

    # replace the next and submit buttons with input validated ones
    pages.next_button = lambda pages: validator(
        pages.current, "Next", on_click=utils.next_on_click(pages)
    )
    pages.submit_button = lambda pages: validator(pages.current, "Submit")

    # pages.prev_button = lambda pages: st.button(
    #     "Previous", type="primary", on_click=pages.previous()
    # )

    with pages:
        if pages.current < len(content.intro):
            intro_index = pages.current
            content.intro[intro_index](config, survey, validator, pages.current)
        elif (
            pages.current
            < len(content.intro) + len(instances) + config.data.attention_per_annotator
        ):
            instance_index = pages.current - len(content.intro)
            attention_indices, attention_offsets = utils.get_attention_indices_offsets(
                len(instances), config.data.attention_per_annotator
            )
            if instance_index in attention_indices:
                content.attention_page(
                    config,
                    survey,
                    validator,
                    attention_offsets[instance_index],
                    attentions[attention_offsets[instance_index]],
                )
            else:
                content.instance_page(
                    config,
                    survey,
                    validator,
                    instance_index - attention_offsets[instance_index],
                    instances[instance_index - attention_offsets[instance_index]],
                )
        elif pages.current < len(content.intro) + len(
            instances
        ) + config.data.attention_per_annotator + len(content.outro):
            outro_index = pages.current - (
                len(content.intro)
                + len(instances)
                + config.data.attention_per_annotator
            )
            content.outro[outro_index](config, survey, validator, pages.current)

    # save session state
    survey.to_json(f"results/{config_path}/{user_id}.json")


def main(config_path):
    # parse the config file
    config = Munch.fromYAML(open(config_path))

    # Prolific provides the user id as parameter in the URL
    user_id = st.query_params["PROLIFIC_PID"]

    dataset = data.load_jsonl(config.paths.dataset)

    # get the instances assigned to user_id or assign them if they are new.
    instances = data.get_user_instances(config, dataset, user_id)
    attentions = data.get_attention_instances(config)

    # run the main survey
    surveyflow(config, config_path, user_id, instances, attentions)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("config_path")

    args = parser.parse_args()

    main(args.config_path)
