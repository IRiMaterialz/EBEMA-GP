
import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("Hybrid Geopolymer Mix Calculator (Fixed GGBFS Input)")

st.markdown("""
This app calculates a hybrid geopolymer mix using:
- **Fixed GGBFS mass**
- **Ideal molar ratios** for metakaolin-GGBFS systems
- **50/50 Na₂O split** between 50% NaOH and sodium silicate solution (MR = 3.3, 33.5% solids)

If (Ca + Na)/Al < 1.5 leads to negative Na, the app defaults to **Na/Al = 0.9** as the leading ratio.
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

# Target Si from Ca/Si = 0.8
mol_Si_total = mol_Ca_g / 0.8
mol_Al_total = mol_Si_total / 3.0
mol_Al_needed = mol_Al_total - mol_Al_g

# Calculate required Metapor mass
mol_Al2O3_per_g_mk = metapor["Al2O3"] / MW["Al2O3"]
mol_Al_per_g_mk = mol_Al2O3_per_g_mk * 2
m_metapor = mol_Al_needed / mol_Al_per_g_mk

# Total Al now = mol_Al_total
# Na/Al = 0.9 ⇒ mol Na = 0.9 × Al
mol_Na = 0.9 * mol_Al_total
mol_Na2O_needed = mol_Na / 2

# 50/50 split
mol_Na2O_NaOH = mol_Na2O_needed / 2
mol_Na2O_Sil = mol_Na2O_needed / 2

# NaOH: 50% solution
mol_NaOH = mol_Na2O_NaOH * 2
m_NaOH_solid = mol_NaOH * MW["NaOH"]
m_NaOH_solution = m_NaOH_solid / 0.5
water_naoh = m_NaOH_solution * 0.5

# Sodium Silicate MR 3.3, 33.5% solids
mol_SiO2_sil = mol_Na2O_Sil * 3.3
m_SiO2 = mol_SiO2_sil * MW["SiO2"]
m_Na2O = mol_Na2O_Sil * MW["Na2O"]
m_solids_sil = m_SiO2 + m_Na2O
m_silicate_solution = m_solids_sil / 0.335
water_silicate = m_silicate_solution * 0.665

# Total water needed: H2O/Na2O = 12.5
mol_H2O = mol_Na2O_needed * 12.5
m_H2O_total = mol_H2O * MW["H2O"]
m_water_extra = m_H2O_total - (water_naoh + water_silicate)

# Final Si from all sources
mol_Si_mk = (m_metapor * metapor["SiO2"]) / MW["SiO2"]
mol_Si_total_final = mol_Si_g + mol_Si_mk + mol_SiO2_sil

# Final Na2O total
mol_Na2O_total = mol_GGBS["Na2O"] + (mol_NaOH / 2) + mol_Na2O_Sil

# Final molar ratios
ratios = {
    "Si/Al": mol_Si_total_final / mol_Al_total,
    "Na/Al": (2 * mol_Na2O_total) / mol_Al_total,
    "H2O/Na2O": mol_H2O / mol_Na2O_total,
    "H2O/SiO2": mol_H2O / mol_Si_total_final,
    "Ca/Si": mol_Ca_g / mol_Si_total_final,
    "(Ca+Na)/Al": (mol_Ca_g + 2 * mol_Na2O_total) / mol_Al_total,
    "SiO2/Na2O": mol_Si_total_final / mol_Na2O_total
}

st.header("2. Calculated Mix Composition (g)")
df_mix = pd.DataFrame({
    "Component": ["Metapor", "GGBFS", "NaOH 50%", "Sodium Silicate", "Extra Water"],
    "Mass (g)": [round(m_metapor, 2), round(m_ggbs, 2), round(m_NaOH_solution, 2), round(m_silicate_solution, 2), round(max(0, m_water_extra), 2)]
})
st.dataframe(df_mix)

st.header("3. Resulting Molar Ratios")
df_ratios = pd.DataFrame({
    "Ratio": list(ratios.keys()),
    "Value": [round(ratios[k], 3) for k in ratios],
    "Target": [3.0, 0.9, 12.5, 0.225, 0.8, 1.5, 1.75]
})
st.dataframe(df_ratios)

# Warning if Ca dominates
if ratios["(Ca+Na)/Al"] > 1.5:
    st.warning(f"(Ca+Na)/Al = {ratios['(Ca+Na)/Al']:.2f} exceeds ideal 1.5. This is expected due to high Ca content in Ecocem. Na/Al = 0.9 was used as fallback.")
if m_water_extra < 0:
    st.warning("Water from activators already exceeds the H₂O/Na₂O requirement. No extra water is needed.")
