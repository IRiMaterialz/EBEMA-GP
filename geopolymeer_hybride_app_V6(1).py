
import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("Hybride Geopolymeer Optimalisatie (MK + GGBFS)")

st.markdown("Deze tool ondersteunt hybride systemen met metakaolin en GGBFS. Molaire verhoudingen worden vergeleken met literatuurwaarden voor sterkte, uitbloei en persbaarheid.")

MW = {"SiO2": 60.08, "Al2O3": 101.96, "Na2O": 61.98, "NaOH": 40.00, "H2O": 18.015, "CaO": 56.08}

# Chemische samenstelling
metapor = {"SiO2": 0.57, "Al2O3": 0.265, "Na2O": 0.09, "CaO": 0.0}
ggbs = {"SiO2": 0.365, "Al2O3": 0.104, "Na2O": 0.005, "CaO": 0.424}

# Ideale verhoudingen (gebaseerd op literatuur voor hybride systemen)
ideaal = {
    "Si/Al": 3.0,
    "Na/Al": 0.9,
    "SiO2/Na2O": 1.75,
    "H2O/Na2O": 12.5,
    "H2O/SiO2": 0.225,
    "Ca/Si": 0.8,
    "(Ca+Na)/Al": 1.5
}

st.header("1. Massa-invoer (g)")
massa_metapor = st.number_input("Metapor", value=300.0)
massa_ggbs = st.number_input("Ecocem GGBFS", value=200.0)
massa_naoh = st.number_input("NaOH 50% oplossing", value=200.0)
massa_silicaat = st.number_input("Natriumsilicaatoplossing (33,5% vastestof)", value=300.0)
massa_water = st.number_input("Extra toegevoegd water", value=30.0)

# Hulpberekening: molberekening per oxide
def oxide_mol(m, ox):
    return {
        "Si": (m * ox["SiO2"]) / MW["SiO2"],
        "Al": (m * ox["Al2O3"]) / (MW["Al2O3"] / 2),
        "Na2O": (m * ox["Na2O"]) / MW["Na2O"],
        "Ca": (m * ox["CaO"]) / MW["CaO"]
    }

mol_MK = oxide_mol(massa_metapor, metapor)
mol_GGBS = oxide_mol(massa_ggbs, ggbs)

mol_Si_base = mol_MK["Si"] + mol_GGBS["Si"]
mol_Al = mol_MK["Al"] + mol_GGBS["Al"]
mol_Ca = mol_MK["Ca"] + mol_GGBS["Ca"]
mol_Na2O_base = mol_MK["Na2O"] + mol_GGBS["Na2O"]

# Activatoren
mol_NaOH = (massa_naoh * 0.5) / MW["NaOH"]
mol_Na2O_NaOH = mol_NaOH / 2

mol_Na2O_sil = (massa_silicaat * 0.335) / (MW["SiO2"] * 2.5 + MW["Na2O"])
mol_Si_sil = mol_Na2O_sil * 2.5

# Water: 50% van NaOH, 66.5% van silicaat, + toegevoegd water
massa_H2O = (massa_naoh * 0.5) + (massa_silicaat * 0.665) + massa_water
mol_H2O = massa_H2O / MW["H2O"]

# Totalen
mol_Si = mol_Si_base + mol_Si_sil
mol_Na2O = mol_Na2O_base + mol_Na2O_NaOH + mol_Na2O_sil

# Ratio’s
ratios = {
    "Si/Al": mol_Si / mol_Al if mol_Al else 0,
    "Na/Al": (2 * mol_Na2O) / mol_Al if mol_Al else 0,
    "SiO2/Na2O": mol_Si / mol_Na2O if mol_Na2O else 0,
    "H2O/Na2O": mol_H2O / mol_Na2O if mol_Na2O else 0,
    "H2O/SiO2": mol_H2O / mol_Si if mol_Si else 0,
    "Ca/Si": mol_Ca / mol_Si if mol_Si else 0,
    "(Ca+Na)/Al": (mol_Ca + 2 * mol_Na2O) / mol_Al if mol_Al else 0
}

# Toelichtingen
toelichting = {
    "Si/Al": "Structuurbepalend – beïnvloedt sterkte en viscositeit",
    "Na/Al": "Alkaliniteit – beïnvloedt oplosbaarheid en risico op uitbloei",
    "SiO2/Na2O": "Modulus van activator – beïnvloedt gelvorming",
    "H2O/Na2O": "Verdunning activator – risico op uitbloei bij hoge waarde",
    "H2O/SiO2": "Verwerkbaarheid – beïnvloedt persbaarheid (aardvochtig)",
    "Ca/Si": "Sterktevorming – essentieel voor C-A-S-H/C-S-H gels",
    "(Ca+Na)/Al": "Totale activatorcapaciteit – netwerkvorming"
}

st.header("2. Molaire verhoudingen en interpretatie")
df = pd.DataFrame({
    "Ratio": list(ratios.keys()),
    "Waarde": [round(ratios[k], 2) for k in ratios],
    "Ideaal": [ideaal[k] for k in ratios],
    "Afwijking (%)": [round(abs(ratios[k] - ideaal[k]) / ideaal[k] * 100) for k in ratios],
    "Toelichting": [toelichting[k] for k in ratios]
})
st.dataframe(df)
