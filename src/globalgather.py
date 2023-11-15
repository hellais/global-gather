from collections import defaultdict

import streamlit as st
import pandas as pd
import numpy as np
import pycountry

from datasources.safety import get_safety_crime_index

PASSPORT_INDEX_CSV = "https://raw.githubusercontent.com/ilyankou/passport-index-dataset/master/passport-index-matrix-iso2.csv"

st.title('Global Gather')
st.subheader('Your assistant to an inclusive international event')

@st.cache_data
def load_safety_crime():
    return pd.DataFrame(get_safety_crime_index())

@st.cache_data
def load_passport_index():
    return pd.read_csv(PASSPORT_INDEX_CSV)

def get_country_name(alpha_2):
    cc = pycountry.countries.get(alpha_2=alpha_2)
    if cc:
        return cc.name
    return ''

def make_destination_df(df_passport_index, df_participants):
    good_values = [
        '7-360',
        'visa free',
        'visa on arrival',
        'e-visa',
        '-1'
    ]
    bad_values = [
        'visa required',
        'covid ban',
        'no admission',
        'Hayya Entry Permit'
    ]
    freetravel_dst_map = defaultdict(set)
    for _, row in df_passport_index.iterrows():
        src_cc = row['Passport']
        for key in row.keys():
            if key == 'Passport':
                continue
            if row[key] in bad_values:
                continue
            freetravel_dst_map[key].add(src_cc)

    src_cc_list = list(df_participants['alpha_2'])

    ok_list = []
    for dst_cc, ok_cc_set in freetravel_dst_map.items():
        ok_count = 0
        for ok_cc in ok_cc_set:
            ok_count += src_cc_list.count(ok_cc)
        ok_list.append(
            {'visa_free_count': ok_count, 'country_code': dst_cc}
        )

    df_scores = pd.DataFrame(ok_list)
    df_scores['country_name'] = df_scores['country_code'].apply(get_country_name)
    return df_scores

if 'df_scores' not in st.session_state:
    st.session_state['df_scores'] = None

data_load_state = st.text('Loading data...')
data = load_safety_crime()
data_load_state.text("Done! (using st.cache_data)")

df_passport_index = load_passport_index()
df_participant_list = pd.DataFrame(
    [
        {"name": "Jane Doe", "alpha_2": "IT"},
    ]
)

edited_df = st.data_editor(df_participant_list, num_rows="dynamic")

def calculate_score(name):
    st.session_state.df_scores = make_destination_df(df_passport_index, edited_df)

st.button('Calculate passport index', on_click=calculate_score, args=[''])

if st.session_state.df_scores is not None:
    st.write(st.session_state.df_scores)

if st.checkbox('Show passport index'):
    st.subheader('Passport index')
    st.write(df_passport_index)
