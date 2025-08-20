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

# Sloupcový graf TOP 20 zemí pro každý rok

# Vytvoření agregovaných dat podle roku a země
df_grouped = (
    df_filtered
    .groupby(['Rok', 'Země'], as_index=False)['Počet osob']
    .sum()
)

# Funkce pro vytvoření Top 20 + Ostatní pro každý rok
def top20_plus_others(df):
    result = []
    for rok in df['Rok'].unique():
        df_year = df[df['Rok'] == rok].sort_values(by='Počet osob', ascending=False)
        top20 = df_year.head(20)
        ostatni_sum = df_year.iloc[20:]['Počet osob'].sum()
        ostatni_row = pd.DataFrame({'Rok': [rok], 'Země': ['Ostatní'], 'Počet osob': [ostatni_sum]})
        result.append(pd.concat([top20, ostatni_row], ignore_index=True))
    return pd.concat(result, ignore_index=True)

# Aplikace funkce
df_top20 = top20_plus_others(df_grouped)

# Výpočet maximální hodnoty pro osu Y
max_y_top20 = max(2_500_000, df_top20['Počet osob'].max())

barvy = {země: '#1f77b4' for země in df_top20['Země'].unique() if země != 'Ostatní'}
barvy['Ostatní'] = '#7f7f7f'  # šedá pro Ostatní

unikatni_zeme = df_top20['Země'].unique()

# Automatické barvy z palety Plotly
barevna_paleta = px.colors.qualitative.Plotly

# Vytvoření mapy: každá země dostane jinou barvu, „Ostatní“ bude šedá
barvy = {}
i = 0
for zem in unikatni_zeme:
    if zem == 'Ostatní':
        barvy[zem] = '#7f7f7f'  # šedá
    else:
        barvy[zem] = barevna_paleta[i % len(barevna_paleta)]
        i += 1

# Vykreslení sloupcového grafu
if animace:
    fig_bar = px.bar(
        df_top20,
        x='Země',
        y='Počet osob',
        color='Země',
        animation_frame='Rok' if animace else None,
        title=f'TOP 20 zemí podle počtu cizinců v ČR ({rozsah_let[0]}–{rozsah_let[1]})',
        labels={'Počet osob': 'Počet osob', 'Země': 'Země'},
        color_discrete_map=barvy
    )

    fig_bar.update_layout(
        margin=dict(b=160),
        yaxis=dict(tickformat=',d', range=[0, max_y_top20]),
        xaxis=dict(
            tickangle=45,
            tickfont=dict(size=10),
            categoryorder='total descending'
        ),
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
            "pad": {"r": 10, "t": 0},
            "showactive": True,
            "type": "buttons",
            "x": 0.1,
            "xanchor": "right",
            "y": -0.3,
            "yanchor": "top"
        }]
    )
else:
    fig_bar = px.bar(
        df_top20,
        x='Země',
        y='Počet osob',
        color='Země',
        title=f'TOP 20 zemí podle počtu cizinců v ČR ({rozsah_let[0]}–{rozsah_let[1]})',
        labels={'Počet osob': 'Počet osob', 'Země': 'Země'}
    )
    fig_bar.update_layout(
        margin=dict(b=1000),
        yaxis=dict(tickformat=',d', range=[0, max_y_top20]),
        xaxis={'categoryorder': 'total descending'}
    )

st.plotly_chart(fig_bar)



