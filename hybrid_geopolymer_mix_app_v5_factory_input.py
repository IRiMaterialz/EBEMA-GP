
import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("Hybrid Geopolymer Mix Calculator – Lab vs. Factory")

st.markdown("""
This tool calculates a hybrid geopolymer mix using:
- **Fixed GGBFS input**
- **Ideal molar ratios**
- **50/50 Na₂O split** between NaOH 50% and sodium silicate (MR = 3.3)

It also lets you input the actual **factory mix**, calculates molar ratios from it, and **compares** both designs.
""")

# Constants
MW = {"SiO2": 60.08, "Al2O3": 101.96, "Na2O": 61.98, "NaOH": 40.00, "H2O": 18.015, "CaO": 56.08}
metapor = {"SiO2": 0.57, "Al2O3": 0.265, "Na2O": 0.09, "CaO": 0.0}
ggbs = {"SiO2": 0.365, "Al2O3": 0.104, "Na2O": 0.005, "CaO": 0.424}

st.header("1. Input: Fixed GGBFS Mass")
m_ggbs = st.number_input("Mass of Ecocem GGBFS (g)", value=100.0, step=10.0)

# Calculate oxide moles from GGBFS
def oxide_mol(m, ox):
    return {
        "Si": (m * ox["SiO2"]) / MW["SiO2"],
        "Al": (m * ox["Al2O3"]) / (MW["Al2O3"] / 2),
        "Na2O": (m * ox["Na2O"]) / MW["Na2O"],
        "Ca": (m * ox["CaO"]) / MW["CaO"]
    }

mol_GGBS = oxide_mol(m_ggbs, ggbs)
mol_Si_g = mol_GGBS["Si"]
mol_Al_g = mol_GGBS["Al"]
mol_Ca_g = mol_GGBS["Ca"]

# Ideal ratios
mol_Si_total = mol_Ca_g / 0.8
mol_Al_total = mol_Si_total / 3.0
mol_Al_needed = mol_Al_total - mol_Al_g

mol_Al2O3_per_g_mk = metapor["Al2O3"] / MW["Al2O3"]
mol_Al_per_g_mk = mol_Al2O3_per_g_mk * 2
m_metapor = mol_Al_needed / mol_Al_per_g_mk

mol_Na = 0.9 * mol_Al_total
mol_Na2O_needed = mol_Na / 2
mol_Na2O_NaOH = mol_Na2O_needed / 2
mol_Na2O_Sil = mol_Na2O_needed / 2

mol_NaOH = mol_Na2O_NaOH * 2
m_NaOH_solid = mol_NaOH * MW["NaOH"]
m_NaOH_solution = m_NaOH_solid / 0.5
water_naoh = m_NaOH_solution * 0.5

mol_SiO2_sil = mol_Na2O_Sil * 3.3
m_SiO2 = mol_SiO2_sil * MW["SiO2"]
m_Na2O = mol_Na2O_Sil * MW["Na2O"]
m_solids_sil = m_SiO2 + m_Na2O
m_silicate_solution = m_solids_sil / 0.335
water_silicate = m_silicate_solution * 0.665

mol_H2O = mol_Na2O_needed * 12.5
m_H2O_total = mol_H2O * MW["H2O"]
m_water_extra = m_H2O_total - (water_naoh + water_silicate)

# Final lab molar totals
mol_Si_mk = (m_metapor * metapor["SiO2"]) / MW["SiO2"]
mol_Si_total_final = mol_Si_g + mol_Si_mk + mol_SiO2_sil
mol_Na2O_total = mol_GGBS["Na2O"] + (mol_NaOH / 2) + mol_Na2O_Sil
mol_Al_total_final = mol_Al_total

ratios_lab = {
    "Si/Al": mol_Si_total_final / mol_Al_total_final,
    "Na/Al": (2 * mol_Na2O_total) / mol_Al_total_final,
    "H2O/Na2O": mol_H2O / mol_Na2O_total,
    "H2O/SiO2": mol_H2O / mol_Si_total_final,
    "Ca/Si": mol_Ca_g / mol_Si_total_final,
    "(Ca+Na)/Al": (mol_Ca_g + 2 * mol_Na2O_total) / mol_Al_total_final,
    "SiO2/Na2O": mol_Si_total_final / mol_Na2O_total
}

st.header("2. Lab Mix Composition")
df_mix = pd.DataFrame({
    "Component": ["Metapor", "GGBFS", "NaOH 50%", "Sodium Silicate", "Extra Water"],
    "Mass (g)": [round(m_metapor, 2), round(m_ggbs, 2), round(m_NaOH_solution, 2), round(m_silicate_solution, 2), round(max(0, m_water_extra), 2)]
})
st.dataframe(df_mix)

st.header("3. Factory Mix Input")
st.markdown("Enter actual weighed amounts in the factory (keep GGBFS fixed):")

col1, col2 = st.columns(2)
with col1:
    m_metapor_f = st.number_input("Metapor (g)", value=round(m_metapor, 2))
    m_naoh_f = st.number_input("NaOH 50% solution (g)", value=round(m_NaOH_solution, 2))
with col2:
    m_silicate_f = st.number_input("Sodium Silicate solution (g)", value=round(m_silicate_solution, 2))
    m_water_f = st.number_input("Extra added water (g)", value=round(max(0, m_water_extra), 2))

# Molar calculations from factory mix
mol_MK_f = oxide_mol(m_metapor_f, metapor)
mol_GGBS_f = oxide_mol(m_ggbs, ggbs)

mol_NaOH_f = (m_naoh_f * 0.5) / MW["NaOH"]
mol_Na2O_NaOH_f = mol_NaOH_f / 2

mol_Na2O_Sil_f = (m_silicate_f * 0.335 * 1 / (MW["SiO2"] * 3.3 + MW["Na2O"])) * MW["Na2O"]
mol_SiO2_Sil_f = mol_Na2O_Sil_f * 3.3

mol_Si_f = mol_MK_f["Si"] + mol_GGBS_f["Si"] + mol_SiO2_Sil_f
mol_Al_f = mol_MK_f["Al"] + mol_GGBS_f["Al"]
mol_Na2O_f = mol_MK_f["Na2O"] + mol_GGBS_f["Na2O"] + mol_Na2O_NaOH_f + mol_Na2O_Sil_f
mol_Ca_f = mol_GGBS_f["Ca"]
mol_H2O_f = (m_naoh_f * 0.5 + m_silicate_f * 0.665 + m_water_f) / MW["H2O"]

ratios_factory = {
    "Si/Al": mol_Si_f / mol_Al_f,
    "Na/Al": (2 * mol_Na2O_f) / mol_Al_f,
    "H2O/Na2O": mol_H2O_f / mol_Na2O_f,
    "H2O/SiO2": mol_H2O_f / mol_Si_f,
    "Ca/Si": mol_Ca_f / mol_Si_f,
    "(Ca+Na)/Al": (mol_Ca_f + 2 * mol_Na2O_f) / mol_Al_f,
    "SiO2/Na2O": mol_Si_f / mol_Na2O_f
}

st.header("4. Comparison: Lab vs Factory Ratios")
df_compare = pd.DataFrame({
    "Ratio": list(ratios_lab.keys()),
    "Lab": [round(ratios_lab[k], 3) for k in ratios_lab],
    "Factory": [round(ratios_factory[k], 3) for k in ratios_factory],
    "Deviation (%)": [round(abs(ratios_factory[k] - ratios_lab[k]) / ratios_lab[k] * 100, 1) if ratios_lab[k] else 0 for k in ratios_lab]
})
st.dataframe(df_compare)
