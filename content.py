import streamlit as st
import streamlit_survey as ss


def _introduction(config, *args, **kwargs):
    """Intro 1: Welcome and high-level introduction
    - purpose of the study
    - compensation
    - estimated time to complete
    - meta-study at the end?
    - consent and withdrawal of consent
    """
    st.title("Introduction")
    st.write(
        f"""Thank your for your interest in our study on ...

In the following you will be presented with ... and asked to ...

You can withdraw your consent at any time during the study.

Your successful participation will be rewarded with ...€

..."""
    )


def _guidelines(config, *args, **kwargs):
    """Intro 2: Description of task and annotation guidelines"""
    st.title("Guidelines")
    st.write(f"""Just do everything correctly, ok?""")


def _example(config, *args, **kwargs):
    """Intro 3: One or more examples to illustrate how to apply the annotation
    guidelines in practice
    """
    st.title("Example")
    st.write(f"""This is an example of our annotation guidelines in practice""")


def _consent(config, survey, validator, current_page, *args, **kwargs):
    """Intro 4: Ask participant for consent"""
    st.title("Consent")
    st.write("I have read and understood the instructions.")
    consent_1 = survey.radio(
        "consent_1",
        options=["No", "Yes"],
        index=0,
        label_visibility="collapsed",
        horizontal=True,
    )
    validator.add(current_page, lambda: consent_1 == "Yes")

    st.write("I want to participate in this research and continue with the study.")
    consent_2 = survey.radio(
        "consent_2",
        options=["No", "Yes"],
        index=0,
        label_visibility="collapsed",
        horizontal=True,
    )
    validator.add(current_page, lambda: consent_2 == "Yes")


def _exit_survey(config, survey, validator, current_page, *args, **kwargs):
    """Outro 1: exit survey about the study"""
    st.title("Exit survey")


def instance_page(config, survey, validator, current_page, instance, *args, **kwargs):
    st.title("Instance page")
    st.write(current_page)


def attention_page(config, survey, validator, current_page, instance, *args, **kwargs):
    st.title("Attention page")
    st.write(current_page)


intro = [_introduction, _guidelines, _example, _consent]
outro = [_exit_survey]
