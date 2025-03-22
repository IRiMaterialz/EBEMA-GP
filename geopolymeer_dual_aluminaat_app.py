
import streamlit as st
import pandas as pd

st.title("Geopolymeer Mix Calculator - Aardvochtige Toepassing")

st.markdown("Keuze uit Metapor® Metakaolin en Ecocem GGBS als aluminaatbron. Inclusief natriumsilicaat (MR = 2.5) en 50% NaOH-oplossing. Doel: aardvochtige persklare mix met hoge sterkte en minimale uitbloei.")

# Molgewichten
molgewichten = {
    "SiO2": 60.08,
    "Al2O3": 101.96,
    "Na2O": 61.98,
    "NaOH": 40.00,
    "H2O": 18.015
}

# Chemische samenstelling Metapor
metapor = {"SiO2": 0.57, "Al2O3": 0.265, "Na2O": 0.09}
# Chemische samenstelling GGBS
ggbs = {"SiO2": 0.365, "Al2O3": 0.104, "Na2O": 0.005}  # aangenomen max 0.5% Na2Oeqv

st.header("1. Massa-invoer (g)")

massa_mk = st.number_input("Metapor® Metakaolin", value=0.0)
massa_ggbs = st.number_input("Ecocem GGBS", value=0.0)
massa_naoh_50 = st.number_input("50% NaOH-oplossing", value=200.0)
massa_silicaat = st.number_input("Natriumsilicaat oplossing (MR = 2.5)", value=300.0)
massa_water = st.number_input("Extra water", value=50.0)
massa_plastificeerder = st.number_input("Plastificeerder (optioneel)", value=0.0)
massa_stabilisator = st.number_input("Stabilisator (optioneel)", value=0.0)
massa_vulstof1 = st.number_input("Vulstof 1 (optioneel)", value=0.0)
massa_vulstof2 = st.number_input("Vulstof 2 (optioneel)", value=0.0)

# Berekening molen per component
def bereken_mol(massa, oxiden):
    mol_Si = (massa * oxiden["SiO2"]) / molgewichten["SiO2"]
    mol_Al = (massa * oxiden["Al2O3"]) / (molgewichten["Al2O3"] / 2)
    mol_Na2O = (massa * oxiden["Na2O"]) / molgewichten["Na2O"]
    return mol_Si, mol_Al, mol_Na2O

mol_Si_mk, mol_Al_mk, mol_Na2O_mk = bereken_mol(massa_mk, metapor)
mol_Si_ggbs, mol_Al_ggbs, mol_Na2O_ggbs = bereken_mol(massa_ggbs, ggbs)

mol_Si_total = mol_Si_mk + mol_Si_ggbs
mol_Al_total = mol_Al_mk + mol_Al_ggbs
mol_Na2O_aluminaat = mol_Na2O_mk + mol_Na2O_ggbs

# NaOH oplossing
massa_naoh_puur = massa_naoh_50 * 0.5
mol_NaOH = massa_naoh_puur / molgewichten["NaOH"]
mol_Na2O_naoh = mol_NaOH / 2

# Silicaat (MR = 2.5)
mol_Na2O_sil = massa_silicaat / (molgewichten["SiO2"] * 2.5 + molgewichten["Na2O"])
mol_Si_sil = mol_Na2O_sil * 2.5

# Waterberekening
mol_H2O_naoh = (massa_naoh_50 * 0.5) / molgewichten["H2O"]
mol_H2O_extra = massa_water / molgewichten["H2O"]
mol_H2O = mol_H2O_naoh + mol_H2O_extra

# Totale molen
mol_Si_total += mol_Si_sil
mol_Na2O_total = mol_Na2O_aluminaat + mol_Na2O_naoh + mol_Na2O_sil

# Ratio's
si_al = mol_Si_total / mol_Al_total if mol_Al_total else 0
na_al = (2 * mol_Na2O_total) / mol_Al_total if mol_Al_total else 0
h2o_na2o = mol_H2O / mol_Na2O_total if mol_Na2O_total else 0
h2o_sio2 = mol_H2O / mol_Si_total if mol_Si_total else 0
sio2_na2o = mol_Si_total / mol_Na2O_total if mol_Na2O_total else 0

st.header("2. Belangrijke ratio's")
st.write(pd.DataFrame({
    "Ratio": ["Si/Al", "Na/Al", "H₂O/Na₂O", "H₂O/SiO₂", "SiO₂/Na₂O"],
    "Waarde": [round(si_al, 3), round(na_al, 3), round(h2o_na2o, 3), round(h2o_sio2, 3), round(sio2_na2o, 3)]
}))

st.header("3. Molwaarden totaal")
st.write(pd.DataFrame({
    "Component": ["mol Si", "mol Al", "mol Na₂O", "mol H₂O"],
    "Mol": [round(mol_Si_total, 3), round(mol_Al_total, 3), round(mol_Na2O_total, 3), round(mol_H2O, 3)]
}))

# Aardvochtigheid controleren (grove schatting water/bindmiddel)
massa_vast = massa_mk + massa_ggbs + massa_naoh_puur + massa_silicaat + massa_plastificeerder + massa_stabilisator + massa_vulstof1 + massa_vulstof2
water_binder_ratio = (massa_naoh_50 * 0.5 + massa_water) / massa_vast if massa_vast else 0

st.header("4. Aardvochtigheid beoordeling")
if water_binder_ratio < 0.15:
    st.success(f"Aardvochtig bereik: {round(water_binder_ratio,3)} - Geschikt voor persen.")
elif water_binder_ratio < 0.25:
    st.warning(f"Licht vochtig: {round(water_binder_ratio,3)} - mogelijk geschikt, test aanbevolen.")
else:
    st.error(f"Te nat: {round(water_binder_ratio,3)} - niet geschikt voor persen.")
