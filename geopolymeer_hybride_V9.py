
import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("Hybrid Geopolymer Optimizer (V9 - GGBFS Fixed via CaO-based Ideal Ratios)")

st.markdown("This app fixes GGBFS input and derives all other components (Metapor, NaOH, sodium silicate, water) based on ideal molar ratios. Starting point: CaO from GGBFS.")

MW = {"SiO2": 60.08, "Al2O3": 101.96, "Na2O": 61.98, "NaOH": 40.00, "H2O": 18.015, "CaO": 56.08}

metapor = {"SiO2": 0.57, "Al2O3": 0.265}
ggbs = {"CaO": 0.424}

ideal = {
    "Ca/Si": 0.8,
    "Si/Al": 3.0,
    "(Ca+Na)/Al": 1.5,
    "H2O/Na2O": 12.5,
    "H2O/SiO2": 0.225
}

st.header("1. Input: GGBFS mass (fixed)")
m_ggbs = st.number_input("GGBFS (g)", value=200.0)

# Calculate mol Ca from fixed GGBFS
mol_Ca = (m_ggbs * ggbs["CaO"]) / MW["CaO"]
mol_Si = mol_Ca / ideal["Ca/Si"]
mol_Al = mol_Si / ideal["Si/Al"]
mol_Na2O = max(((ideal["(Ca+Na)/Al"] * mol_Al) - mol_Ca) / 2, 0)
mol_H2O = mol_Na2O * ideal["H2O/Na2O"]

# Component masses
m_MK = (mol_Al * MW["Al2O3"]) / (2 * metapor["Al2O3"])
mol_Si_mk = (m_MK * metapor["SiO2"]) / MW["SiO2"]
mol_Si_needed_from_silicate = mol_Si - mol_Si_mk
mol_Na2O_silicate = mol_Si_needed_from_silicate / 2.5
m_sil = (mol_Si_needed_from_silicate * MW["SiO2"] + mol_Na2O_silicate * MW["Na2O"]) / 0.335
m_NaOH = (mol_Na2O - mol_Na2O_silicate) * MW["Na2O"] / 0.5
m_H2O_total = mol_H2O * MW["H2O"]
m_H2O_from_NaOH = m_NaOH * 0.5
m_H2O_from_sil = m_sil * 0.665
m_H2O_extra = m_H2O_total - m_H2O_from_NaOH - m_H2O_from_sil

# Safe output
components = {
    "GGBFS (fixed)": m_ggbs,
    "Metapor": round(m_MK, 1) if m_MK > 0 else "n.v.t.",
    "NaOH 50%": round(m_NaOH, 1) if m_NaOH > 0 else "n.v.t.",
    "Sodium Silicate (33.5%)": round(m_sil, 1) if m_sil > 0 else "n.v.t.",
    "Extra Water": round(m_H2O_extra, 1) if m_H2O_extra > 0 else "n.v.t."
}

st.header("2. Optimized Mix Design")
st.write(pd.DataFrame.from_dict(components, orient="index", columns=["Mass (g)"]))

# Calculate molar ratios again
ratios = {
    "Ca/Si": mol_Ca / mol_Si if mol_Si else "n.v.t.",
    "Si/Al": mol_Si / mol_Al if mol_Al else "n.v.t.",
    "Na/Al": (2 * mol_Na2O) / mol_Al if mol_Al else "n.v.t.",
    "H2O/Na2O": mol_H2O / mol_Na2O if mol_Na2O else "n.v.t.",
    "H2O/SiO2": mol_H2O / mol_Si if mol_Si else "n.v.t.",
    "(Ca+Na)/Al": (mol_Ca + 2 * mol_Na2O) / mol_Al if mol_Al else "n.v.t."
}

descriptions = {
    "Ca/Si": "C-A-S-H formation (strength)",
    "Si/Al": "Polymer network density",
    "Na/Al": "Alkalinity and reactivity",
    "H2O/Na2O": "Efflorescence control",
    "H2O/SiO2": "Workability / pressability",
    "(Ca+Na)/Al": "Total charge balance in network"
}

st.header("3. Molar Ratios and Assessment")
df_ratios = pd.DataFrame({
    "Ratio": list(ratios.keys()),
    "Value": [round(ratios[k], 2) if isinstance(ratios[k], float) else ratios[k] for k in ratios],
    "Ideal": [ideal[k] if k in ideal else "-" for k in ratios],
    "Explanation": [descriptions[k] for k in ratios]
})
st.dataframe(df_ratios)

# Risk and pressability messages
st.header("4. Efflorescence Risk and Workability")
if isinstance(ratios["Na/Al"], float) and isinstance(ratios["H2O/Na2O"], float):
    if ratios["Na/Al"] <= 1.0 and ratios["H2O/Na2O"] <= 13:
        st.success("Efflorescence Risk: LOW ✅")
    else:
        st.warning("Efflorescence Risk: HIGH ⚠️")
else:
    st.info("Efflorescence risk: not evaluated")

if isinstance(ratios["H2O/SiO2"], float):
    if ratios["H2O/SiO2"] < 0.18:
        st.error("Pressability: Poor (too dry)")
    elif ratios["H2O/SiO2"] <= 0.26:
        st.success("Pressability: Good (earth moist)")
    else:
        st.warning("Pressability: Moderate to wet")
else:
    st.info("Pressability: not evaluated")
