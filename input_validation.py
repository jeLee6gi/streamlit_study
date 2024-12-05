from collections import defaultdict as dd

import streamlit as st


class Validator:
    def __init__(self):
        self.conditions = dd(list)

    def add(self, page_number, condition):
        self.conditions[page_number].append(condition)

    def __call__(self, page_number, button_text, **kwargs):
        for con in self.conditions[page_number]:
            if not con():
                return st.button(
                    button_text,
                    key="foo",
                    type="primary",
                    use_container_width=True,
                    disabled=True,
                    **kwargs,
                )

        return st.button(
            button_text, key="bar", type="primary", use_container_width=True, **kwargs
        )
