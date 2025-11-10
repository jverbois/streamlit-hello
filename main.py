import pandas as pd
import requests
import streamlit as st

st.title("Arbres de la ville de Namur")
st.write(
    "Petite application Streamlit de visualisation des données des arbres de la ville de Namur."
)


@st.cache_data()
def load_data_from_odwb():
    url = "https://www.odwb.be/api/explore/v2.1/catalog/datasets/namur-arbres/records?where=nom_simplifie IS NOT NULL and hauteur IS NOT NULL&limit=100"
    response = requests.get(url)
    return response.json()["results"]


odwb_data = load_data_from_odwb()
# Transforme les données JSON en un dataframe plat
data = pd.json_normalize(odwb_data)
# Affiche les données dans un tableau
st.dataframe(data)
# Affiche les arbres par localité
st.scatter_chart(
    data[data["hauteur"] > 0],
    x="acom_nom_m",
    y="hauteur",
    x_label="Localité",
    y_label="Hauteur (m)",
)

st.header("Filtres")
with st.container(horizontal=True):
    name_filter = st.selectbox(
        label="Type",
        index=None,
        placeholder="Tous",
        options=sorted(data["nom_simplifie"].dropna().unique().tolist()),
    )
    locality_filter = st.selectbox(
        label="Localité",
        index=None,
        placeholder="Toutes",
        options=sorted(data["acom_nom_m"].dropna().unique().tolist()),
    )
    min_height_filter = st.slider(
        label="Hauteur minimale (m)",
        min_value=0,
        max_value=int(data["hauteur"].max()),
        value=0,
    )


def filter_data(data, name=None, locality=None, min_height=0):
    # Commencer avec un masque qui sélectionne toutes les lignes
    mask = pd.Series([True] * len(data), index=data.index)
    # Appliquer le filtre par nom vernaculaire
    if name is not None:
        mask = mask & (data["nom_simplifie"] == name)
    # Appliquer le filtre par localité
    if locality is not None:
        mask = mask & (data["acom_nom_m"] == locality)
    # Appliquer le filtre par hauteur minimale
    if min_height > 0:
        mask = mask & (data["hauteur"] >= min_height)
    # Appliquer le masque final une seule fois
    return data[mask]


filtered_data = filter_data(
    data, name=name_filter, locality=locality_filter, min_height=min_height_filter
)
st.subheader(f"Nombre d'arbres dans la sélection : {len(filtered_data)}")
st.dataframe(filtered_data)
