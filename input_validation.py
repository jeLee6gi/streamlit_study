from collections import defaultdict as dd

import streamlit as st


class Validator:
    """Implements input validation which allows registering arbitrary boolean
    expressions which are supposed to hold for a given page number. If not all
    conditions evaluate to True for the given page, the next or submit button
    will be grayed out.

    Technically, an instance of this input validator is used to replace the
    functions that return the next and submit buttons and returns an enabled
    button if all conditions evaluate to True and a disabled button otherwise.
    """

    def __init__(self):
        self.conditions = dd(list)

    def add(self, page_number, condition):
        """Register a new condition for the given page number"""
        self.conditions[page_number].append(condition)

    def __call__(self, page_number, button_text, **kwargs):
        """When an instance of the input validator is called with a page number,
        evaluate all conditions that have been registered for this page number
        and return an enabled button if all conditions evaluate to True and a
        disabled button otherwise.
        """
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
