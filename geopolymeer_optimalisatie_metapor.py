
import streamlit as st
import pandas as pd

st.title("Geopolymeer Mix - Optimalisatie voor Aardvochtige Persmix")

st.markdown("Voer de massa Metapor® in en ontvang automatische massa-voorstellen voor NaOH-oplossing, natriumsilicaat en water op basis van ideale molaire ratio's voor aardvochtige mengsels met lage uitbloei.")

# Literatuurwaarden molgewichten
molgewichten = {
    "SiO2": 60.08,
    "Al2O3": 101.96,
    "Na2O": 61.98,
    "NaOH": 40.00,
    "H2O": 18.015
}

# Chemische samenstelling Metapor
metapor = {"SiO2": 0.57, "Al2O3": 0.265, "Na2O": 0.09}

# Ideale molverhoudingen
ideaal = {
    "Si/Al": 3.0,
    "Na/Al": 0.9,
    "H2O/Na2O": 12.5,
    "H2O/SiO2": 0.225,
    "SiO2/Na2O": 1.75
}

st.header("1. Invoer Metapor®")

massa_mk = st.number_input("Massa Metapor® (g)", value=300.0)

# Stap 1: mol Al berekenen
mol_Al = (massa_mk * metapor["Al2O3"]) / (molgewichten["Al2O3"] / 2)

# Stap 2: ideale molverhoudingen toepassen
mol_Si = mol_Al * ideaal["Si/Al"]
mol_Na = mol_Al * ideaal["Na/Al"]
mol_Na2O = mol_Si / ideaal["SiO2/Na2O"]
mol_H2O = mol_Na2O * ideaal["H2O/Na2O"]

# Stap 3: massa's berekenen
massa_NaOH_puur = mol_Na * molgewichten["NaOH"]
massa_NaOH_50 = massa_NaOH_puur / 0.5

mol_Si_sil = mol_Si - ((massa_mk * metapor["SiO2"]) / molgewichten["SiO2"])
mol_Na2O_sil = mol_Si_sil / 2.5
massa_silicaat = mol_Si_sil * molgewichten["SiO2"] + mol_Na2O_sil * molgewichten["Na2O"]

massa_H2O = mol_H2O * molgewichten["H2O"]
massa_Na2O = mol_Na2O * molgewichten["Na2O"]

st.header("2. Massa-suggesties op basis van ideale ratio's")

st.write(pd.DataFrame({
    "Component": ["NaOH 50% oplossing", "Natriumsilicaat (MR=2.5)", "Extra water"],
    "Voorgestelde massa (g)": [round(massa_NaOH_50, 1), round(massa_silicaat, 1), round(massa_H2O, 1)]
}))

st.header("3. Berekende ratio's (bij ideale samenstelling)")

# Werkelijke molen met deze verhoudingen
mol_Si_total = mol_Si
mol_Na2O_total = mol_Na2O
mol_H2O_total = mol_H2O

si_al = mol_Si_total / mol_Al
na_al = (2 * mol_Na2O_total) / mol_Al
h2o_na2o = mol_H2O_total / mol_Na2O_total
h2o_sio2 = mol_H2O_total / mol_Si_total
sio2_na2o = mol_Si_total / mol_Na2O_total

df_ratios = pd.DataFrame({
    "Ratio": ["Si/Al", "Na/Al", "H₂O/Na₂O", "H₂O/SiO₂", "SiO₂/Na₂O"],
    "Waarde": [si_al, na_al, h2o_na2o, h2o_sio2, sio2_na2o],
    "Ideaal": [ideaal["Si/Al"], ideaal["Na/Al"], ideaal["H2O/Na2O"], ideaal["H2O/SiO2"], ideaal["SiO2/Na2O"]]
})
df_ratios["Afwijking (%)"] = abs((df_ratios["Waarde"] - df_ratios["Ideaal"]) / df_ratios["Ideaal"] * 100).round(1)

st.dataframe(df_ratios.style.format({"Waarde": "{:.2f}", "Ideaal": "{:.2f}"}))

# Risico op uitbloei inschatten
aantal_afwijkingen = sum(df_ratios["Afwijking (%)"] > 10)
if aantal_afwijkingen == 0:
    risico = 5
elif aantal_afwijkingen == 1:
    risico = 15
else:
    risico = 30

st.header("4. Risico op uitbloei")
st.metric(label="Inschatting risico uitbloei", value=f"{risico} %", delta=None)
