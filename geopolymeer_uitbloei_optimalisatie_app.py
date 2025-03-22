
import streamlit as st
import pandas as pd

st.title("Geopolymeer Optimalisatie voor Aardvochtige, Uitbloei-arme Mengsels")

st.markdown("Voer de massa's in van alle componenten. De app berekent automatisch de relevante molaire ratio's en vergelijkt ze met literatuurwaarden. Je kunt daarna kiezen om de mengverhoudingen te optimaliseren (behalve Metapor).")

# Molgewichten
MW = {
    "SiO2": 60.08,
    "Al2O3": 101.96,
    "Na2O": 61.98,
    "NaOH": 40.00,
    "H2O": 18.015
}

# Samenstelling Metapor en GGBS
metapor = {"SiO2": 0.57, "Al2O3": 0.265, "Na2O": 0.09}
ggbs = {"SiO2": 0.365, "Al2O3": 0.104, "Na2O": 0.005}

# Ideale ratio’s uit literatuur (voor aardvochtige, uitbloei-arme mengsels)
ideaal = {
    "Si/Al": 3.0,
    "Na/Al": 0.9,
    "SiO2/Na2O": 1.75,
    "H2O/Na2O": 12.5,
    "H2O/SiO2": 0.225
}

st.header("1. Massa-invoer (g)")

# Basiscomponenten
massa_metapor = st.number_input("Metapor", value=300.0)
massa_ggbs = st.number_input("Ecocem GGBS", value=0.0)
massa_naoh_50 = st.number_input("NaOH 50% oplossing", value=200.0)
massa_silicaat = st.number_input("Natriumsilicaat (MR 2.5)", value=300.0)
massa_water = st.number_input("Extra water", value=50.0)

# Additieven
massa_plastificeerder = st.number_input("Plastificeerder", value=0.0)
massa_stabilisator = st.number_input("Stabilisator", value=0.0)
massa_anti_efflorescent = st.number_input("Additief tegen uitbloei", value=0.0)

# Vulstoffen
vulstoffen = []
for i in range(1, 5):
    vulstoffen.append(st.number_input(f"Vulstof {i}", value=0.0))

# Berekeningen
def oxide_mol(mass, comp):
    mol_Si = (mass * comp["SiO2"]) / MW["SiO2"]
    mol_Al = (mass * comp["Al2O3"]) / (MW["Al2O3"] / 2)
    mol_Na2O = (mass * comp["Na2O"]) / MW["Na2O"]
    return mol_Si, mol_Al, mol_Na2O

mol_Si_mp, mol_Al_mp, mol_Na2O_mp = oxide_mol(massa_metapor, metapor)
mol_Si_gg, mol_Al_gg, mol_Na2O_gg = oxide_mol(massa_ggbs, ggbs)

mol_Si_base = mol_Si_mp + mol_Si_gg
mol_Al = mol_Al_mp + mol_Al_gg
mol_Na2O_base = mol_Na2O_mp + mol_Na2O_gg

# NaOH
massa_naoh_puur = massa_naoh_50 * 0.5
mol_NaOH = massa_naoh_puur / MW["NaOH"]
mol_Na2O_naoh = mol_NaOH / 2

# Natriumsilicaat
mol_Na2O_sil = massa_silicaat / (MW["SiO2"] * 2.5 + MW["Na2O"])
mol_Si_sil = mol_Na2O_sil * 2.5

# Water
mol_H2O = (massa_naoh_50 * 0.5 + massa_water) / MW["H2O"]

# Totalen
mol_Si = mol_Si_base + mol_Si_sil
mol_Na2O = mol_Na2O_base + mol_Na2O_naoh + mol_Na2O_sil

# Ratio’s
si_al = mol_Si / mol_Al if mol_Al else 0
na_al = (2 * mol_Na2O) / mol_Al if mol_Al else 0
sio2_na2o = mol_Si / mol_Na2O if mol_Na2O else 0
h2o_na2o = mol_H2O / mol_Na2O if mol_Na2O else 0
h2o_sio2 = mol_H2O / mol_Si if mol_Si else 0

# Tabel originele berekening
st.header("2. Molaire ratio's")
df = pd.DataFrame({
    "Ratio": ["Si/Al", "Na/Al", "SiO2/Na2O", "H2O/Na2O", "H2O/SiO2"],
    "Waarde": [si_al, na_al, sio2_na2o, h2o_na2o, h2o_sio2],
    "Ideaal": [ideaal["Si/Al"], ideaal["Na/Al"], ideaal["SiO2/Na2O"], ideaal["H2O/Na2O"], ideaal["H2O/SiO2"]]
})
df["Afwijking (%)"] = abs((df["Waarde"] - df["Ideaal"]) / df["Ideaal"] * 100).round(1)
st.dataframe(df.style.format({"Waarde": "{:.2f}", "Ideaal": "{:.2f}"}))

# Optimalisatie op basis van Metapor
st.header("3. Optimalisatie op basis van ideale ratio's")
if st.button("Optimaliseer hoeveelheden (behoud Metapor)"):
    mol_Al_opt = mol_Al
    mol_Si_opt = mol_Al_opt * ideaal["Si/Al"]
    mol_Na2O_opt = mol_Si_opt / ideaal["SiO2/Na2O"]
    mol_H2O_opt = mol_Na2O_opt * ideaal["H2O/Na2O"]

    # Herbereken massa’s
    massa_NaOH_puur_opt = (mol_Al_opt * ideaal["Na/Al"]) * MW["NaOH"]
    massa_NaOH_50_opt = massa_NaOH_puur_opt / 0.5

    mol_Si_sil_opt = mol_Si_opt - mol_Si_base
    mol_Na2O_sil_opt = mol_Si_sil_opt / 2.5
    massa_silicaat_opt = mol_Si_sil_opt * MW["SiO2"] + mol_Na2O_sil_opt * MW["Na2O"]

    massa_H2O_opt = mol_H2O_opt * MW["H2O"]

    st.subheader("Suggestie op basis van ideale ratio's")
    st.write(pd.DataFrame({
        "Component": ["NaOH 50%", "Natriumsilicaat MR2.5", "Extra water"],
        "Massa (g)": [round(massa_NaOH_50_opt, 1), round(massa_silicaat_opt, 1), round(massa_H2O_opt, 1)]
    }))
