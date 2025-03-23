
import streamlit as st
import pandas as pd

st.title("Geopolymeer Optimalisatie voor Aardvochtige, Uitbloei-arme Mengsels")

st.markdown("Volledige waterinhoud wordt berekend uit NaOH 50%, natriumsilicaat (33,5% vast), en toegevoegde watermassa. Optimalisatie houdt Metapor constant.")

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

# Ideale ratio’s
ideaal = {
    "Si/Al": 3.0,
    "Na/Al": 0.9,
    "SiO2/Na2O": 1.75,
    "H2O/Na2O": 12.5,
    "H2O/SiO2": 0.225
}

st.header("1. Massa-invoer (g)")
massa_metapor = st.number_input("Metapor", value=300.0)
massa_ggbs = st.number_input("Ecocem GGBS", value=0.0)
massa_naoh_50 = st.number_input("NaOH 50% oplossing", value=200.0)
massa_silicaat = st.number_input("Natriumsilicaat (33,5% vastestof)", value=300.0)
massa_water = st.number_input("Extra water", value=50.0)

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

massa_naoh_puur = massa_naoh_50 * 0.5
mol_NaOH = massa_naoh_puur / MW["NaOH"]
mol_Na2O_naoh = mol_NaOH / 2

mol_Na2O_sil = (massa_silicaat * 0.335) / (MW["SiO2"] * 2.5 + MW["Na2O"])
mol_Si_sil = mol_Na2O_sil * 2.5

massa_H2O_total = massa_naoh_50 * 0.5 + massa_silicaat * 0.665 + massa_water
mol_H2O = massa_H2O_total / MW["H2O"]

mol_Si = mol_Si_base + mol_Si_sil
mol_Na2O = mol_Na2O_base + mol_Na2O_naoh + mol_Na2O_sil

si_al = mol_Si / mol_Al if mol_Al else 0
na_al = (2 * mol_Na2O) / mol_Al if mol_Al else 0
sio2_na2o = mol_Si / mol_Na2O if mol_Na2O else 0
h2o_na2o = mol_H2O / mol_Na2O if mol_Na2O else 0
h2o_sio2 = mol_H2O / mol_Si if mol_Si else 0

st.header("2. Molaire ratio's")
df = pd.DataFrame({
    "Ratio": ["Si/Al", "Na/Al", "SiO2/Na2O", "H2O/Na2O", "H2O/SiO2"],
    "Waarde": [si_al, na_al, sio2_na2o, h2o_na2o, h2o_sio2],
    "Ideaal": [ideaal["Si/Al"], ideaal["Na/Al"], ideaal["SiO2/Na2O"], ideaal["H2O/Na2O"], ideaal["H2O/SiO2"]]
})
df["Afwijking (%)"] = abs((df["Waarde"] - df["Ideaal"]) / df["Ideaal"] * 100).round(0).astype(int)
st.dataframe(df.style.format({"Waarde": "{:.2f}", "Ideaal": "{:.2f}"}))

st.header("3. Optimalisatie op basis van ideale ratio's")
if st.button("Optimaliseer hoeveelheden (behoud Metapor)"):
    mol_Al_opt = mol_Al
    mol_Si_opt = mol_Al_opt * ideaal["Si/Al"]
    mol_Na2O_opt = mol_Si_opt / ideaal["SiO2/Na2O"]
    mol_H2O_opt = mol_Na2O_opt * ideaal["H2O/Na2O"]

    massa_NaOH_puur_opt = (mol_Al_opt * ideaal["Na/Al"]) * MW["NaOH"]
    massa_naoh_50_opt = massa_NaOH_puur_opt / 0.5 if massa_NaOH_puur_opt else 0

    mol_Si_sil_opt = mol_Si_opt - mol_Si_base
    mol_Na2O_sil_opt = mol_Si_sil_opt / 2.5
    massa_silicaat_opt = (mol_Si_sil_opt * MW["SiO2"] + mol_Na2O_sil_opt * MW["Na2O"]) / 0.335

    # Check dat massa_naoh_50_opt beschikbaar is
    if 'massa_naoh_50_opt' in locals() and 'massa_silicaat_opt' in locals():
        massa_H2O_opt = mol_H2O_opt * MW["H2O"]
        massa_H2O_extra_opt = massa_H2O_opt - (massa_naoh_50_opt * 0.5 + massa_silicaat_opt * 0.665)
    else:
        massa_H2O_extra_opt = 0.0

    si_al_opt = mol_Si_opt / mol_Al_opt if mol_Al_opt else 0
    na_al_opt = (2 * mol_Na2O_opt) / mol_Al_opt if mol_Al_opt else 0
    sio2_na2o_opt = mol_Si_opt / mol_Na2O_opt if mol_Na2O_opt else 0
    h2o_na2o_opt = mol_H2O_opt / mol_Na2O_opt if mol_Na2O_opt else 0
    h2o_sio2_opt = mol_H2O_opt / mol_Si_opt if mol_Si_opt else 0

    st.subheader("Geoptimaliseerde massaverhoudingen")
    st.write(pd.DataFrame({
        "Component": ["Metapor", "GGBS", "NaOH 50%", "Natriumsilicaat", "Extra water"],
        "Massa (g)": [round(massa_metapor, 1), 0.0, round(massa_naoh_50_opt, 1), round(massa_silicaat_opt, 1), round(massa_H2O_extra_opt, 1)]
    }))

    st.write(pd.DataFrame({
        "Ratio": ["Si/Al", "Na/Al", "SiO2/Na2O", "H2O/Na2O", "H2O/SiO2"],
        "Geoptimaliseerd": [si_al_opt, na_al_opt, sio2_na2o_opt, h2o_na2o_opt, h2o_sio2_opt],
        "Ideaal": [ideaal["Si/Al"], ideaal["Na/Al"], ideaal["SiO2/Na2O"], ideaal["H2O/Na2O"], ideaal["H2O/SiO2"]]
    }).style.format({"Geoptimaliseerd": "{:.2f}", "Ideaal": "{:.2f}"}))

aantal_afwijkingen = sum(df["Afwijking (%)"] > 10)
risico_uitbloei = "Laag (<10%)" if aantal_afwijkingen == 0 else "Matig (10-20%)" if aantal_afwijkingen == 1 else "Hoog (>20%)"
st.subheader("4. Risico op uitbloei")
st.success(f"Risico-inschatting: {risico_uitbloei}")

if h2o_sio2 < 0.18:
    score_persbaarheid = "3 (Slecht – te droog)"
elif 0.18 <= h2o_sio2 <= 0.26:
    score_persbaarheid = "1 (Goed – aardvochtig)"
else:
    score_persbaarheid = "2 (Matig – te nat)"

st.subheader("5. Persbaarheidsscore")
st.info(f"Persbaarheid: {score_persbaarheid}")
