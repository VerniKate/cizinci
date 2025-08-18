import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Počet cizinců v ČR podle země původu v letech 2004 až 2024")

st.markdown("""
### Zdroj dat  
Data byla získána zpracováním dat dostupných na https://data.gov.cz/datove-sady z let 2004 až 2024.
""")

# Načtení dat
df = pd.read_csv("cizinci_complete.csv")

# Výběr země pro mapu
země = st.selectbox("Vyber zemi (pro mapu)", sorted(df['Země'].unique()))

# Společný slider pro roky
min_rok = int(df['Rok'].min())
max_rok = int(df['Rok'].max())
rozsah_let = st.slider("Vyber rozsah let", min_value=min_rok, max_value=max_rok, value=(min_rok, max_rok))

# Checkbox pro zapnutí/vypnutí animace
animace = st.checkbox("Zapnout animaci sloupcového grafu", value=True)

# Filtrování dat podle rozsahu let
df_filtered = df[(df['Rok'] >= rozsah_let[0]) & (df['Rok'] <= rozsah_let[1])]

# Filtrování pro mapu (země + roky)
df_map = df_filtered[df_filtered['Země'] == země]

# Mapa – choropleth podle roku
fig_map = px.choropleth(
    df_map,
    locations='Země_anglicky',
    locationmode='country names',
    color='Počet osob',
    hover_name='Země',
    animation_frame='Rok',
    title=f"Mapa: Počet osob z {země} v letech {rozsah_let[0]}–{rozsah_let[1]}",
    color_continuous_scale='Blues'
)
fig_map.update_layout(
    coloraxis_colorbar=dict(tickformat=',d'),
    geo=dict(projection_type="natural earth")
)
st.plotly_chart(fig_map)

# Sloupcový graf TOP 15 zemí pro každý rok
# Nejprve vybereme TOP 15 zemí pro každý rok
df_top15 = (
    df_filtered
    .groupby(['Rok', 'Země'], as_index=False)['Počet osob']
    .sum()
    .sort_values(['Rok', 'Počet osob'], ascending=[True, False])
    .groupby('Rok')
    .head(15)
)

# Vykreslení sloupcového grafu
if animace:
    fig_bar = px.bar(
        df_top15,
        x='Země',
        y='Počet osob',
        color='Země',
        animation_frame='Rok',
        title=f'TOP 15 zemí podle počtu cizinců v ČR ({rozsah_let[0]}–{rozsah_let[1]})',
        labels={'Počet osob': 'Počet osob', 'Země': 'Země'}
    )
    fig_bar.update_layout(
        yaxis=dict(tickformat=',d'),
        xaxis={'categoryorder': 'total descending'},
        updatemenus=[{
            "buttons": [
                {
                    "args": [None, {"frame": {"duration": 1000, "redraw": True},
                                    "fromcurrent": True, "transition": {"duration": 500}}],
                    "label": "▶️ Přehrát",
                    "method": "animate"
                },
                {
                    "args": [[None], {"frame": {"duration": 0, "redraw": False},
                                      "mode": "immediate",
                                      "transition": {"duration": 0}}],
                    "label": "⏸️ Zastavit",
                    "method": "animate"
                }
            ],
            "direction": "left",
            "pad": {"r": 10, "t": 87},
            "showactive": True,
            "type": "buttons",
            "x": 0.1,
            "xanchor": "right",
            "y": 0,
            "yanchor": "top"
        }]
    )
else:
    fig_bar = px.bar(
        df_top15,
        x='Země',
        y='Počet osob',
        color='Země',
        title=f'TOP 15 zemí podle počtu cizinců v ČR ({rozsah_let[0]}–{rozsah_let[1]})',
        labels={'Počet osob': 'Počet osob', 'Země': 'Země'}
    )
    fig_bar.update_layout(
        yaxis=dict(tickformat=',d'),
        xaxis={'categoryorder': 'total descending'}
    )

st.plotly_chart(fig_bar)

