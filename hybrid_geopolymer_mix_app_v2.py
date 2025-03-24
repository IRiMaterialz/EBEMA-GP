
import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("Hybrid Geopolymer Mix Design – Theoretical vs Practical")

st.markdown("""
This tool designs a **hybrid geopolymer mix** based on fixed GGBFS input.  
It calculates the required masses of Metapor, NaOH (50%), sodium silicate (MR = 3.3, 33.5% solids), and water  
to meet **ideal molar ratios** for strength, durability, efflorescence resistance, and workability.  
After that, it allows **comparison with your practical mix**.
""")

MW = {"SiO2": 60.08, "Al2O3": 101.96, "Na2O": 61.98, "NaOH": 40.00, "H2O": 18.015, "CaO": 56.08}

metapor = {"SiO2": 0.57, "Al2O3": 0.265, "Na2O": 0.09, "CaO": 0.0}
ggbs = {"SiO2": 0.365, "Al2O3": 0.104, "Na2O": 0.005, "CaO": 0.424}

ideal = {
    "Si/Al": 3.0,
    "Na/Al": 0.9,
    "SiO2/Na2O": 1.75,
    "H2O/Na2O": 12.5,
    "H2O/SiO2": 0.225,
    "Ca/Si": 0.8,
    "(Ca+Na)/Al": 1.5
}

desc = {
    "Si/Al": "Network structure – strength and viscosity",
    "Na/Al": "Alkalinity – solubility and efflorescence risk",
    "SiO2/Na2O": "Activator modulus – gel formation",
    "H2O/Na2O": "Activator dilution – efflorescence risk",
    "H2O/SiO2": "Workability – affects pressability",
    "Ca/Si": "C-A-S-H/C-S-H gel – early/final strength",
    "(Ca+Na)/Al": "Total activation capacity – structural formation"
}

st.header("1. Input GGBFS mass (fixed)")
m_ggbs = st.number_input("Fixed GGBFS mass (g)", value=200.0)

def oxide_mol(m, ox):
    return {
        "Si": (m * ox["SiO2"]) / MW["SiO2"],
        "Al": (m * ox["Al2O3"]) / (MW["Al2O3"] / 2),
        "Na2O": (m * ox["Na2O"]) / MW["Na2O"],
        "Ca": (m * ox["CaO"]) / MW["CaO"]
    }

mol_GGBS = oxide_mol(m_ggbs, ggbs)
mol_Ca = mol_GGBS["Ca"]

# From ideal Ca/Si -> mol_Si -> mol_Al -> mol_Na2O -> mol_H2O
mol_Si = mol_Ca / ideal["Ca/Si"]
mol_Al = mol_Si / ideal["Si/Al"]
mol_Na2O = max(((ideal["(Ca+Na)/Al"] * mol_Al) - mol_Ca) / 2, 0)
mol_H2O = mol_Na2O * ideal["H2O/Na2O"]

# Back calculate masses
m_MK = (mol_Al * MW["Al2O3"]) / (2 * metapor["Al2O3"])
mol_Si_base = oxide_mol(m_MK, metapor)["Si"] + mol_GGBS["Si"]
mol_Si_needed = max((mol_Si - mol_Si_base), 0)
m_sil = (mol_Si_needed / 2.5) * (MW["SiO2"] * 2.5 + MW["Na2O"]) / 0.335
m_naoh = (mol_Na2O * MW["Na2O"]) / 0.5
m_water_total = mol_H2O * MW["H2O"]
m_water_extra = m_water_total - (m_naoh * 0.5 + m_sil * 0.665)

# Recalculate molar input with new masses
mol_MK_calc = oxide_mol(m_MK, metapor)
mol_Si_total = mol_MK_calc["Si"] + mol_GGBS["Si"] + mol_Si_needed
mol_Na2O_total = mol_MK_calc["Na2O"] + mol_GGBS["Na2O"] + mol_Na2O
mol_Al_total = mol_MK_calc["Al"] + mol_GGBS["Al"]
mol_Ca_total = mol_Ca
mol_H2O_total = mol_H2O

ratios_theo = {
    "Si/Al": mol_Si_total / mol_Al_total if mol_Al_total else 0,
    "Na/Al": (2 * mol_Na2O_total) / mol_Al_total if mol_Al_total else 0,
    "SiO2/Na2O": mol_Si_total / mol_Na2O_total if mol_Na2O_total else 0,
    "H2O/Na2O": mol_H2O_total / mol_Na2O_total if mol_Na2O_total else 0,
    "H2O/SiO2": mol_H2O_total / mol_Si_total if mol_Si_total else 0,
    "Ca/Si": mol_Ca_total / mol_Si_total if mol_Si_total else 0,
    "(Ca+Na)/Al": (mol_Ca_total + 2 * mol_Na2O_total) / mol_Al_total if mol_Al_total else 0
}

st.subheader("Theoretical Mix Design (masses in grams)")
st.dataframe(pd.DataFrame({
    "Component": ["Metapor", "GGBFS", "NaOH 50%", "Sodium Silicate", "Extra Water"],
    "Mass (g)": [round(m_MK, 1), round(m_ggbs, 1), round(m_naoh, 1), round(m_sil, 1), round(m_water_extra, 1)]
}))

st.subheader("Theoretical Molar Ratios")
df_theo_ratios = pd.DataFrame({
    "Ratio": list(ratios_theo),
    "Value": [round(ratios_theo[k], 2) for k in ratios_theo],
    "Ideal": [ideal[k] for k in ratios_theo],
    "Explanation": [desc[k] for k in ratios_theo]
})
st.dataframe(df_theo_ratios)

st.divider()
st.header("2. Practical Mix Input")
m_mk_p = st.number_input("Metapor", value=round(m_MK, 1))
m_ggbs_p = st.number_input("GGBFS", value=round(m_ggbs, 1))
m_naoh_p = st.number_input("NaOH 50% solution", value=round(m_naoh, 1))
m_sil_p = st.number_input("Sodium silicate (33.5% solids)", value=round(m_sil, 1))
m_water_p = st.number_input("Extra added water", value=round(m_water_extra, 1))

mol_MK_p = oxide_mol(m_mk_p, metapor)
mol_GGBS_p = oxide_mol(m_ggbs_p, ggbs)

mol_Si_base_p = mol_MK_p["Si"] + mol_GGBS_p["Si"]
mol_Al_p = mol_MK_p["Al"] + mol_GGBS_p["Al"]
mol_Ca_p = mol_MK_p["Ca"] + mol_GGBS_p["Ca"]
mol_Na2O_base_p = mol_MK_p["Na2O"] + mol_GGBS_p["Na2O"]
mol_NaOH_p = (m_naoh_p * 0.5) / MW["NaOH"]
mol_Na2O_NaOH_p = mol_NaOH_p / 2
mol_Na2O_sil_p = (m_sil_p * 0.335) / (MW["SiO2"] * 2.5 + MW["Na2O"])
mol_Si_sil_p = mol_Na2O_sil_p * 2.5
mol_Si_p = mol_Si_base_p + mol_Si_sil_p
mol_Na2O_p = mol_Na2O_base_p + mol_Na2O_NaOH_p + mol_Na2O_sil_p
m_H2O_p = (m_naoh_p * 0.5) + (m_sil_p * 0.665) + m_water_p
mol_H2O_p = m_H2O_p / MW["H2O"]

ratios_p = {
    "Si/Al": mol_Si_p / mol_Al_p if mol_Al_p else 0,
    "Na/Al": (2 * mol_Na2O_p) / mol_Al_p if mol_Al_p else 0,
    "SiO2/Na2O": mol_Si_p / mol_Na2O_p if mol_Na2O_p else 0,
    "H2O/Na2O": mol_H2O_p / mol_Na2O_p if mol_Na2O_p else 0,
    "H2O/SiO2": mol_H2O_p / mol_Si_p if mol_Si_p else 0,
    "Ca/Si": mol_Ca_p / mol_Si_p if mol_Si_p else 0,
    "(Ca+Na)/Al": (mol_Ca_p + 2 * mol_Na2O_p) / mol_Al_p if mol_Al_p else 0
}

st.subheader("3. Practical vs Theoretical Molar Ratios")
df_ratios = pd.DataFrame({
    "Ratio": list(ratios_p),
    "Practical": [round(ratios_p[k], 2) for k in ratios_p],
    "Theoretical": [round(ratios_theo[k], 2) for k in ratios_p],
    "Ideal": [ideal[k] for k in ratios_p],
    "Deviation (%)": [round(abs(ratios_p[k] - ideal[k]) / ideal[k] * 100, 1) for k in ratios_p],
    "Explanation": [desc[k] for k in ratios_p]
})
st.dataframe(df_ratios)
