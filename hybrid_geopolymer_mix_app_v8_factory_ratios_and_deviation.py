
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

ideal_ratios = {
    "Si/Al": "Network strength & gel structure",
    "Na/Al": "Alkalinity & activation level",
    "H2O/Na2O": "Workability & efflorescence risk",
    "H2O/SiO2": "Pressability & gel quality",
    "Ca/Si": "C-A-S-H vs N-A-S-H balance",
    "(Ca+Na)/Al": "Global activation index",
    "SiO2/Na2O": "Silicate modulus of activator"
}

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
m_water_extra = max(0, m_H2O_total - (water_naoh + water_silicate))

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

st.header("2. Lab Mix Design + Molar Ratios")
col1, col2 = st.columns(2)
with col1:
    st.markdown("**Theoretical Masses (g):**")
    st.write(pd.DataFrame({
        "Component": ["Metapor", "GGBFS", "NaOH 50%", "Sodium Silicate", "Extra Water"],
        "Mass (g)": [round(m_metapor, 2), round(m_ggbs, 2), round(m_NaOH_solution, 2), round(m_silicate_solution, 2), round(m_water_extra, 2)]
    }))
with col2:
    st.markdown("**Theoretical Molar Ratios:**")
    st.write(pd.DataFrame({
        "Ratio": list(ratios_lab),
        "Value": [round(ratios_lab[k], 3) for k in ratios_lab],
        "Explanation": [ideal_ratios[k] for k in ratios_lab]
    }))

st.header("3. Factory Mix Input")
st.markdown("Enter actual factory weights (initially set to 0):")

col1, col2 = st.columns(2)
with col1:
    m_metapor_f = st.number_input("Metapor (g)", value=0.0)
    m_naoh_f = st.number_input("NaOH 50% solution (g)", value=0.0)
with col2:
    m_silicate_f = st.number_input("Sodium Silicate solution (g)", value=0.0)
    m_water_f = st.number_input("Extra added water (g)", value=0.0)

# Compute factory ratios
ratios_factory = {
    "Si/Al": mol_Si_f / mol_Al_f if mol_Al_f else 0,
    "Na/Al": (2 * mol_Na2O_f) / mol_Al_f if mol_Al_f else 0,
    "H2O/Na2O": mol_H2O_f / mol_Na2O_f if mol_Na2O_f else 0,
    "H2O/SiO2": mol_H2O_f / mol_Si_f if mol_Si_f else 0,
    "Ca/Si": mol_Ca_f / mol_Si_f if mol_Si_f else 0,
    "(Ca+Na)/Al": (mol_Ca_f + 2 * mol_Na2O_f) / mol_Al_f if mol_Al_f else 0,
    "SiO2/Na2O": mol_Si_f / mol_Na2O_f if mol_Na2O_f else 0
}

st.header("4. Factory Mix Molar Ratios")
st.write(pd.DataFrame({
    "Ratio": list(ratios_factory),
    "Value": [round(ratios_factory[k], 3) for k in ratios_factory],
    "Explanation": [ideal_ratios[k] for k in ratios_factory]
}))

st.header("5. Deviation from Lab Mix (in %)")
df_compare = pd.DataFrame({
    "Ratio": list(ratios_lab.keys()),
    "Lab": [round(ratios_lab[k], 3) for k in ratios_lab],
    "Factory": [round(ratios_factory[k], 3) for k in ratios_factory],
    "Deviation (%)": [
        round(abs(ratios_factory[k] - ratios_lab[k]) / ratios_lab[k] * 100, 1) if ratios_lab[k] else 0
        for k in ratios_lab
    ]
})
st.dataframe(df_compare)
