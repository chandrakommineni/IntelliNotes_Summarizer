#
# This seems to be a common issue amongst new Streamlit users, so I wrote a mini-tutorial app to explain how widgets 
# are used with initialized values and how to make them stick using session state and callbacks.
# 
# There are three ways:
#
# (1) The most basic where the initial value is not given but the widget is always reset, 
# (2) Where it’s initialized but there are issues getting the return value to stick, and finally 
# (3) Overcoming all issues with session state and callbacks.
# 
# (I think the issue in the second case is a Streamlit bug).
#

import streamlit as st

demos = ['Demo 1', 'Demo 2', 'Demo 3']
demo_descriptions = {
    'Demo 1': 'Number input without value initializer & without callback',
    'Demo 2': 'Number input with value initializer & without callback',
    'Demo 3': 'Number input with value initializer & with callback'
}
demo_summary = {
    'Demo 1': 'Since there is no `value` initializer for the number input widgets, their return value is bound immediately (and correctly) '
              'to their corresponding session state variable. However, whenever the widgets are remounted on rerun their values are reset, '
              'which might be undesirable.',
    'Demo 2': 'To overcome the _value reset_ problem in demo 1 we use a `value` initializer for the number inputs. However, the return value '
              'is NOT picked up properly. It seems the number input widget is remounted with the session state initializer value before '
              'its return value is bound! This causes the _double press_ issue where you have to click twice to get the value to stick!',
    'Demo 3': 'To overcome the _double press_ problem in demo 2, we use an `on_change` callback to update the session state `value` for these number input widgets '
              'from the widget\'s auto-created session state value, using the widget\'s key to access this value. The callback is called _before_ the widget is remounted on re-run. '
              'Therefore, when the number input widget is remounted it will have with the correct session state initializer value, and so its return value will also be correct! '
              'This solution eliminates the _double press_ issue!',
}

demo = st.sidebar.radio(label="Select a demo", options=demos)

if demo == demos[0]:
    st.subheader(demo_descriptions[demo])
    st.sidebar.write(demo_descriptions[demo])
    st.markdown(f'##### {demo_summary[demo]}')
    with st.echo(code_location='below'):
        if 'A1' not in st.session_state:
            st.session_state.A1 = 0
        if 'B1' not in st.session_state:
            st.session_state.B1 = 0

        radio = st.radio(label="", label_visibility="hidden", options=["Set A1", "Set B1", "Add them"], horizontal=True)

        if radio == "Set A1":
            st.session_state.A1 = st.number_input(
                label="What is A1?",
                min_value=0, max_value=100,
                key='num_A1'
            )
            st.write(f"You set A1 to {st.session_state.A1}")
        elif radio == "Set B1":
            st.session_state.B1 = st.number_input(
                label="What is B1?",
                min_value=0, max_value=100,
                key='num_B1'
            )
            st.write(f"You set B1 to {st.session_state.B1}")
        elif radio == "Add them":
            st.write(f"A1 = {st.session_state.A1} and B1 = {st.session_state.B1}")
            button = st.button("Add A1 and B1")
            if button:
                st.write(f"A1 + B1 = {st.session_state.A1 + st.session_state.B1}")

if demo == demos[1]:
    st.subheader(demo_descriptions[demo])
    st.sidebar.write(demo_descriptions[demo])
    st.markdown(f'##### {demo_summary[demo]}')

    with st.echo(code_location='below'):
        if 'A2' not in st.session_state:
            st.session_state.A2 = 0
        if 'B2' not in st.session_state:
            st.session_state.B2 = 0

        radio = st.radio(label="", label_visibility="hidden", options=["Set A2", "Set B2", "Add them"], horizontal=True)

        if radio == "Set A2":
            st.session_state.A2 = st.number_input(
                label="What is A2?",
                min_value=0, max_value=100,
                value=st.session_state.A2,
                key='num_A2'
            )
            st.write(f"You set A2 to {st.session_state.A2}")
        elif radio == "Set B2":
            st.session_state.B2 = st.number_input(
                label="What is B2?",
                min_value=0, max_value=100,
                value=st.session_state.B2,
                key='num_B2'
            )
            st.write(f"You set B2 to {st.session_state.B2}")
        elif radio == "Add them":
            st.write(f"A2 = {st.session_state.A2} and B2 = {st.session_state.B2}")
            button = st.button("Add A2 and B2")
            if button:
                st.write(f"A2 + B2 = {st.session_state.A2 + st.session_state.B2}")

if demo == demos[2]:
    st.subheader(demo_descriptions[demo])
    st.sidebar.write(demo_descriptions[demo])
    st.markdown(f'##### {demo_summary[demo]}')

    with st.echo(code_location='below'):
        if 'A3' not in st.session_state:
            st.session_state.A3 = 0
        if 'B3' not in st.session_state:
            st.session_state.B3 = 0

        def _set_num_A3_cb():
            st.session_state.A3 = st.session_state.num_A3
        def _set_num_B3_cb():
            st.session_state.B3 = st.session_state.num_B3

        radio = st.radio(label="", label_visibility="hidden", options=["Set A3", "Set B3", "Add them"], horizontal=True)

        if radio == "Set A3":
            st.session_state.A3 = st.number_input(
                label="What is A3?",
                min_value=0, max_value=100,
                value=st.session_state.A3,
                on_change=_set_num_A3_cb,
                key='num_A3'
            )
            st.write(f"You set A3 to {st.session_state.A3}")
        elif radio == "Set B3":
            st.session_state.B3 = st.number_input(
                label="What is B3?",
                min_value=0, max_value=100,
                value=st.session_state.B3,
                on_change=_set_num_B3_cb,
                key='num_B3'
            )
            st.write(f"You set B3 to {st.session_state.B3}")
        elif radio == "Add them":
            st.write(f"A3 = {st.session_state.A3} and B3 = {st.session_state.B3}")
            button = st.button("Add A3 and B3")
            if button:
                st.write(f"A3 + B3 = {st.session_state.A3 + st.session_state.B3}")