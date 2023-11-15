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

def make_destination_df(df_passport_index, df_safety_crime, df_participants):
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
            {'visa_free_count': ok_count, 'alpha_2': dst_cc}
        )

    df_scores = pd.DataFrame(ok_list)
    df_scores['country_name'] = df_scores['alpha_2'].apply(get_country_name)
    return df_scores.merge(df_safety_crime, how='left', on='alpha_2')

data_load_state = st.markdown('**Loading data...**')
df_safety_crime = load_safety_crime()

df_passport_index = load_passport_index()
df_participant_list = pd.DataFrame(
    [
        {"name": "Jane Doe", "alpha_2": "IT"},
    ]
)
data_load_state.markdown("""
**Loaded!**

Populate the table below with your participant list and then click calculate destination scores to get the list of possible destinations.

**pro-tip**: you can copy paste the participant list from a spreadsheet
""")

edited_df = st.data_editor(df_participant_list, num_rows="dynamic")

if st.button('Calculate destination scores'):
    df_scores = make_destination_df(
            df_passport_index=df_passport_index,
            df_safety_crime=df_safety_crime,
            df_participants=edited_df
    )
    st.write(df_scores)

if st.checkbox('Show passport index'):
    st.subheader('Passport index')
    st.write(df_passport_index)
