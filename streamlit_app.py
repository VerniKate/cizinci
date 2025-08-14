import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Počet cizinců v ČR podle země původu v letech 2004 až 2024")

st.markdown("""
### Zdroj dat
Data byla získána zpracováníním dat dostupných na https://data.gov.cz/datove-sady z let 2004 až 2024.
""")

# Načtení dat
df = pd.read_csv("cizinci_complete.csv")

# Výběr země
země = st.selectbox("Vyber zemi", sorted(df['Země'].unique()))

# Filtrování dat
df_filtered = df[df['Země'] == země]
# Mapa – choropleth podle roku
fig_map = px.choropleth(
    df_filtered,
    locations='Země_anglicky',  # ← změna tady
    locationmode='country names',
    color='Počet osob',
    hover_name='Země',
    animation_frame='Rok',
    title=f"Mapa: Počet osob z {země} v letech 2004–2024",
    color_continuous_scale='Blues'
)
fig_map.update_layout(
    coloraxis_colorbar=dict(
        tickformat=',d'  # formát pro celé čísla s oddělovačem tisíců
    )
)
fig_map.update_geos(projection_type="natural earth")


st.plotly_chart(fig_map)
# Sloupcový graf
fig_bar = px.bar(
    df_filtered,
    x='Rok',
    y='Počet osob',
    color='Počet osob',
    title=f'Počet osob z {země} v jednotlivých letech',
    labels={'Počet osob': 'Počet osob', 'Rok': 'Rok'}
)
fig_bar.update_layout(
    yaxis=dict(tickformat='d')
)
fig_bar.update_layout(yaxis=dict(tickformat=',d'))
st.plotly_chart(fig_bar)

