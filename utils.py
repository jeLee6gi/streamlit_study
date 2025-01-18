import time

import streamlit as st


# source: https://discuss.streamlit.io/t/question-about-scroll-event/59333/6
scroll_to_top_js = """
<script>
    var body = window.parent.document.querySelector(".main");
    console.log(body);
    body.scrollTop = 0;
</script>
"""


# source: https://discuss.streamlit.io/t/question-about-scroll-event/59333/6
def next_on_click(pages):
    def callback():
        pages.next()
        temp = st.empty()
        with temp:
            st.components.v1.html(scroll_to_top_js)
            time.sleep(0.3)  # To make sure the script can execute before being deleted
        temp.empty()

    return callback


def get_attention_indices_offsets(num_instances, num_attention):
    """This function equally spaces out the required number of attention checks
    over the number of instances and returns their indices
    """
    attention_indices = set(
        [
            round((num_instances) / (num_attention + 1) * (i + 1) + (1 * i))
            for i in range(num_attention)
        ]
    )

    attention_offset = 0
    attention_offsets = []
    for i in range(num_instances + num_attention):
        attention_offsets.append(attention_offset)
        if i in attention_indices:
            attention_offset += 1

    return attention_indices, attention_offsets
