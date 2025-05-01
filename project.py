import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from urllib.request import urlopen
import json
with urlopen('https://raw.githubusercontent.com/febian01/project/refs/heads/main/countries.geo.json') as response:
    countries = json.load(response)

st.set_page_config(layout="wide")

# Get DFs, data cleaning, and show the DFs all in one DF
df_gini = pd.read_csv('https://raw.githubusercontent.com/febian01/project/refs/heads/main/gini.csv')
df_gini = df_gini.drop('990179-annotations', axis=1)
df_gini = df_gini.drop('Code', axis=1)

df_fdi = pd.read_csv('https://raw.githubusercontent.com/febian01/project/refs/heads/main/fdi.csv')
df_fdi = df_fdi.rename(columns={"Foreign direct investment, net inflows (% of GDP)": 'FDI'})
df_fdi = df_fdi.drop('Code', axis=1)

df_tourism = pd.read_csv('https://raw.githubusercontent.com/febian01/project/refs/heads/main/tourism.csv')
df_tourism = df_tourism.rename(columns={'Inbound arrivals of tourists': 'Tourists'})
df_tourism = df_tourism.drop('Code', axis=1)

df_all = pd.merge(left=df_tourism, left_on=['Year', 'Entity'], right=df_fdi, right_on=['Year', 'Entity'], how='outer')
df_all = pd.merge(left=df_all, left_on=['Year', 'Entity'], right=df_gini, right_on=['Year', 'Entity'], how='outer')


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


#Select some countries
country_multiselect = st.multiselect('Select a Country:', df_all['Entity'].drop_duplicates(), default='United States', max_selections=10)
years = st.slider('Select a range of years', 1963, 2023, (1980,2023))

## Country over time
st.header('Explore Data')
st.plotly_chart(px.line(df_all[df_all['Entity'].isin(country_multiselect)], x='Year', y='Gini coefficient', color='Entity'))
st.plotly_chart(px.line(df_all[df_all['Entity'].isin(country_multiselect)], x='Year', y='FDI', color='Entity'))
st.plotly_chart(px.line(df_all[df_all['Entity'].isin(country_multiselect)], x='Year', y='Tourists', color='Entity'))

st.plotly_chart(px.bar(df_all[df_all['Entity'].isin(country_multiselect)],
    x='Gini coefficient', 
    y='Entity',
    animation_frame='Year',
    range_x=[0,1]
))

## Categories against each other
st.plotly_chart(px.scatter(df_all,
    x='Tourists', 
    y='Gini coefficient',
    color='Entity'
))

st.plotly_chart(px.scatter(df_all,
    x='FDI', 
    y='Gini coefficient',
    range_x=(0,10),
    color='Entity'
))

### Rolling Averages **********8
df_fdi['Rolling'] = df_fdi.groupby('Entity').rolling(5)['FDI'].mean().reset_index(drop=True)
df_tourism['Rolling'] = df_tourism.groupby('Entity').rolling(5)['Tourists'].mean().reset_index(drop=True)

##Choropleth map by year
st.header('Choropeth Maps')
tab11, tab12, tab13 = st.tabs(["Gini Index", "Foreign Direct Investment", "Inbound Tourism"])
with tab11:
    slider_gini = st.slider("Select a Year:", min_value=1963, max_value=2023)
    fig = px.choropleth(df_gini[df_gini['Year'] == slider_gini], geojson=countries, locations=df_gini.loc[df_gini['Year'] == slider_gini, 'Entity'], color='Gini coefficient', locationmode='country names',range_color=(0,1))
    st.plotly_chart(fig)
with tab12:
    slider_fdi = st.slider("Select a Year:", min_value=1970, max_value=2023)
    fig = px.choropleth(df_fdi[df_fdi['Year'] == slider_fdi], geojson=countries, locations=df_fdi.loc[df_fdi['Year'] == slider_fdi, 'Entity'], color='FDI', locationmode='country names', range_color=(0,10))
    st.plotly_chart(fig)
with tab13:
    slider_tourism = st.slider("Select a Year:", min_value=1995, max_value=2022)
    fig = px.choropleth(df_tourism[df_tourism['Year'] == slider_tourism], geojson=countries, locations=df_tourism.loc[df_tourism['Year'] == slider_tourism, 'Entity'], color='Tourists', locationmode='country names')
    st.plotly_chart(fig)
