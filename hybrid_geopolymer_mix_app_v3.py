
import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("Hybrid Geopolymer Mix Design – Ideal vs Practical")

st.markdown("""
This app calculates a hybrid geopolymer mix with **GGBFS as fixed input**  
and a 50/50 split of required Na₂O from **NaOH (50%)** and **sodium silicate solution** (MR = 3.3, 33.5% solids).  
It compares ideal molar ratios from literature with practical values you enter.
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

# Step 1: Derive ideal molar needs
mol_Si = mol_Ca / ideal["Ca/Si"]
mol_Al = mol_Si / ideal["Si/Al"]
mol_Na2O = max(((ideal["(Ca+Na)/Al"] * mol_Al) - mol_Ca) / 2, 0)
mol_H2O = mol_Na2O * ideal["H2O/Na2O"]

# Step 2: 50/50 Na2O split
mol_Na2O_naoh = mol_Na2O * 0.5
mol_Na2O_sil = mol_Na2O * 0.5

# NaOH (50%) mass
m_naoh_sol = (mol_Na2O_naoh * MW["Na2O"]) / 0.5

# Sodium silicate MR=3.3 → mol_Na2O_sil supports 3.3 mol SiO2 per mol Na2O
mol_Si_sil = mol_Na2O_sil * 3.3
solid_mass_sil = mol_Si_sil * MW["SiO2"] + mol_Na2O_sil * MW["Na2O"]
m_sil_sol = solid_mass_sil / 0.335

# Water in NaOH (50%) and sodium silicate (66.5%)
water_naoh = m_naoh_sol * 0.5
water_sil = m_sil_sol * 0.665
water_total = mol_H2O * MW["H2O"]
water_extra = water_total - (water_naoh + water_sil)

# Step 3: Metapor to provide remaining Al
mol_MK = {"Al": mol_Al}
m_MK = (mol_Al * MW["Al2O3"]) / (2 * metapor["Al2O3"])

# Total mols from mix
mol_MK_full = oxide_mol(m_MK, metapor)
mol_Si_total = mol_MK_full["Si"] + mol_GGBS["Si"] + mol_Si_sil
mol_Na2O_total = mol_MK_full["Na2O"] + mol_GGBS["Na2O"] + mol_Na2O
mol_Al_total = mol_Al
mol_H2O_total = water_total

ratios_theo = {
    "Si/Al": mol_Si_total / mol_Al_total if mol_Al_total else 0,
    "Na/Al": (2 * mol_Na2O_total) / mol_Al_total if mol_Al_total else 0,
    "SiO2/Na2O": mol_Si_total / mol_Na2O_total if mol_Na2O_total else 0,
    "H2O/Na2O": mol_H2O_total / mol_Na2O_total if mol_Na2O_total else 0,
    "H2O/SiO2": mol_H2O_total / mol_Si_total if mol_Si_total else 0,
    "Ca/Si": mol_Ca / mol_Si_total if mol_Si_total else 0,
    "(Ca+Na)/Al": (mol_Ca + 2 * mol_Na2O_total) / mol_Al_total if mol_Al_total else 0
}

st.subheader("Theoretical Mix Design")
st.dataframe(pd.DataFrame({
    "Component": ["Metapor", "GGBFS", "NaOH 50%", "Sodium Silicate", "Extra Water"],
    "Mass (g)": [round(m_MK, 1), round(m_ggbs, 1), round(m_naoh_sol, 1), round(m_sil_sol, 1), round(water_extra, 1)]
}))

st.subheader("Theoretical Molar Ratios")
df_theo = pd.DataFrame({
    "Ratio": list(ratios_theo),
    "Value": [round(ratios_theo[k], 2) for k in ratios_theo],
    "Ideal": [ideal[k] for k in ratios_theo],
    "Explanation": [desc[k] for k in ratios_theo]
})
st.dataframe(df_theo)
