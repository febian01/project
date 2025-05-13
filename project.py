import streamlit as st
import pandas as pd
import plotly.express as px
from urllib.request import urlopen
import json
with urlopen('https://raw.githubusercontent.com/febian01/project/refs/heads/main/countries.geo.json') as response:
    countries = json.load(response)

st.set_page_config(layout="wide")

# Get DFs, data cleaning, and show the DFs all in one DF
df_gini = pd.read_csv('https://raw.githubusercontent.com/febian01/project/refs/heads/main/gini_complete.csv')
df_gini = df_gini.drop('990179-annotations', axis=1)
df_gini = df_gini.drop('Code', axis=1)

df_fdi = pd.read_csv('https://raw.githubusercontent.com/febian01/project/refs/heads/main/fdi_complete.csv')
df_fdi = df_fdi.rename(columns={"Foreign direct investment, net inflows (% of GDP)": 'FDI'})
df_fdi = df_fdi.drop('Code', axis=1)

df_tourism = pd.read_csv('https://raw.githubusercontent.com/febian01/project/refs/heads/main/tourism_complete.csv')
df_tourism = df_tourism.rename(columns={'Inbound arrivals of tourists': 'Tourists'})
df_tourism = df_tourism.drop('Code', axis=1)

df_all = pd.merge(left=df_tourism, left_on=['Year', 'Entity'], right=df_fdi, right_on=['Year', 'Entity'], how='outer')
df_all = pd.merge(left=df_all, left_on=['Year', 'Entity'], right=df_gini, right_on=['Year', 'Entity'], how='outer')

st.header('Effects of Tourism and Federal Direct Investment(FDI) on Gini Coefficient')
st.subheader('By Kayleigh Wells and Febian Reyes Torres', divider="gray")
with st.expander('Source Data'):
    tab1, tab2, tab3, tab4 = st.tabs(["Gini Index", "Foreign Direct Investment", "Inbound Tourism", "All"])
    with tab1:
        df_gini
    with tab2:
        df_fdi
    with tab3:
        df_tourism
    with tab4: 
        df_all

st.text('The following data is taken from 8 countries with the largest Gini Coefficient difference between 2003 and 2023')

#Select countries to meausure
df_2003 = df_gini.dropna()[df_gini['Year'] == 2003].drop_duplicates(subset=['Entity'])
df_2003 = df_2003.pivot(index=['Entity'], columns='Year')
df_2023 = df_gini.dropna()[df_gini['Year'] == 2023].drop_duplicates(subset=['Entity'])
df_2023 = df_2023.pivot(index=['Entity'], columns='Year')
df_measured = df_2003.merge(df_2023, on='Entity')
df_measured['Diff'] = abs(df_measured['Gini coefficient'][2003] - df_measured['Gini coefficient'][2023])
df_measured = df_measured.reset_index()
df_measured = df_measured.nlargest(8, 'Diff')
df_measured = df_all[df_all['Entity'].isin(df_measured['Entity'])]


## Country over time
st.subheader('Gini Coefficient Over Time', divider="gray")
st.plotly_chart(px.line(df_measured, x='Year', y='Gini coefficient', color='Entity'))
st.subheader('FDI Over Time', divider="gray")
st.plotly_chart(px.line(df_measured, x='Year', y='FDI', color='Entity'))
st.subheader('Tourism Over Time', divider="gray")
st.plotly_chart(px.line(df_measured, x='Year', y='Tourists', color='Entity'))

st.subheader("Tourism's Effect on Gini Coefficient", divider="gray")
st.plotly_chart(px.scatter(df_measured,
    x='Tourists', 
    y='Gini coefficient',
    color='Entity',
    trendline='ols',
    trendline_scope="overall"
))
with st.expander('See more'):
    st.write('***')

st.subheader("FDI's Effect on Gini Coefficient", divider="gray")
st.plotly_chart(px.scatter(df_measured,
    x='FDI', 
    y='Gini coefficient',
    range_x=(0,10),
    color='Entity',
    trendline='ols',
    trendline_scope="overall"
))
with st.expander('See more'):
    st.write('***')

##Choropleth map by year
st.subheader('Choropeth Maps by Year', divider="gray")
tab11, tab12, tab13 = st.tabs(["Gini Index", "Foreign Direct Investment", "Inbound Tourism"])
with tab11:
    slider_gini = st.slider("Select a Year:", min_value=2003, max_value=2023, key='slider_gini')
    fig = px.choropleth(df_gini[df_gini['Year'] == slider_gini], geojson=countries, locations=df_gini.loc[df_gini['Year'] == slider_gini, 'Entity'], color='Gini coefficient', locationmode='country names',range_color=(0,1))
    st.plotly_chart(fig)
with tab12:
    slider_fdi = st.slider("Select a Year:", min_value=2003, max_value=2023, key='slider_fdi')
    fig = px.choropleth(df_fdi[df_fdi['Year'] == slider_fdi], geojson=countries, locations=df_fdi.loc[df_fdi['Year'] == slider_fdi, 'Entity'], color='FDI', locationmode='country names', range_color=(0,10))
    st.plotly_chart(fig)
with tab13:
    slider_tourism = st.slider("Select a Year:", min_value=2003, max_value=2023, key='slider_tourism')
    fig = px.choropleth(df_tourism[df_tourism['Year'] == slider_tourism], geojson=countries, locations=df_tourism.loc[df_tourism['Year'] == slider_tourism, 'Entity'], color='Tourists', locationmode='country names')
    st.plotly_chart(fig)
