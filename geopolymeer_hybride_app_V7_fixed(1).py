
import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("Hybrid Geopolymer Optimization (MK + GGBFS)")

st.markdown("This tool supports hybrid systems using Metakaolin and GGBFS. Molar ratios are compared with literature values for strength, efflorescence risk, and workability. Negative values are prevented; efflorescence risk takes priority, followed by pressability.")

MW = {"SiO2": 60.08, "Al2O3": 101.96, "Na2O": 61.98, "NaOH": 40.00, "H2O": 18.015, "CaO": 56.08}

metapor = {"SiO2": 0.57, "Al22O3": 0.265, "Na2O": 0.09, "CaO": 0.0}
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

st.header("1. Input mass (g)")
m_mk = st.number_input("Metapor", value=300.0)
m_ggbs = st.number_input("Ecocem GGBFS", value=200.0)
m_naoh = st.number_input("NaOH 50% solution", value=200.0)
m_sil = st.number_input("Sodium silicate (33.5% solids)", value=300.0)
m_water = st.number_input("Extra added water", value=30.0)

def oxide_mol(m, ox):
    return {
        "Si": (m * ox["SiO2"]) / MW["SiO2"],
        "Al": (m * ox["Al2O3"]) / (MW["Al2O3"] / 2),
        "Na2O": (m * ox["Na2O"]) / MW["Na2O"],
        "Ca": (m * ox["CaO"]) / MW["CaO"]
    }

mol_MK = oxide_mol(m_mk, metapor)
mol_GGBS = oxide_mol(m_ggbs, ggbs)

mol_Si_base = mol_MK["Si"] + mol_GGBS["Si"]
mol_Al = mol_MK["Al"] + mol_GGBS["Al"]
mol_Ca = mol_MK["Ca"] + mol_GGBS["Ca"]
mol_Na2O_base = mol_MK["Na2O"] + mol_GGBS["Na2O"]

mol_NaOH = (m_naoh * 0.5) / MW["NaOH"]
mol_Na2O_NaOH = mol_NaOH / 2

mol_Na2O_sil = (m_sil * 0.335) / (MW["SiO2"] * 2.5 + MW["Na2O"])
mol_Si_sil = mol_Na2O_sil * 2.5

m_H2O = (m_naoh * 0.5) + (m_sil * 0.665) + m_water
mol_H2O = m_H2O / MW["H2O"]

mol_Si = mol_Si_base + mol_Si_sil
mol_Na2O = mol_Na2O_base + mol_Na2O_NaOH + mol_Na2O_sil

ratios = {
    "Si/Al": mol_Si / mol_Al if mol_Al else 0,
    "Na/Al": (2 * mol_Na2O) / mol_Al if mol_Al else 0,
    "SiO2/Na2O": mol_Si / mol_Na2O if mol_Na2O else 0,
    "H2O/Na2O": mol_H2O / mol_Na2O if mol_Na2O else 0,
    "H2O/SiO2": mol_H2O / mol_Si if mol_Si else 0,
    "Ca/Si": mol_Ca / mol_Si if mol_Si else 0,
    "(Ca+Na)/Al": (mol_Ca + 2 * mol_Na2O) / mol_Al if mol_Al else 0
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

st.header("2. Molar ratios")
df = pd.DataFrame({
    "Ratio": list(ratios),
    "Value": [round(ratios[k], 2) for k in ratios],
    "Ideal": [ideal[k] for k in ratios],
    "Deviation (%)": [round(abs(ratios[k] - ideal[k]) / ideal[k] * 100) for k in ratios],
    "Explanation": [desc[k] for k in ratios]
})
st.dataframe(df)

st.header("3. Optimization (Metapor fixed)")
if st.button("Optimize"):
    mol_Al_opt = mol_Al
    mol_Si_opt = mol_Al_opt * ideal["Si/Al"]
    mol_Ca_opt = mol_Si_opt * ideal["Ca/Si"]
    mol_Na2O_opt = max(((ideal["(Ca+Na)/Al"] * mol_Al_opt) - mol_Ca_opt) / 2, 0)
    mol_H2O_opt = mol_Na2O_opt * ideal["H2O/Na2O"]

    m_NaOH_pure_opt = mol_Na2O_opt * MW["Na2O"]
    m_NaOH_opt = m_NaOH_pure_opt / 0.5
    m_sil_opt = max((mol_Si_opt - mol_Si_base), 0) / 2.5 * (MW["SiO2"] * 2.5 + MW["Na2O"]) / 0.335
    m_GGBS_opt = (mol_Ca_opt * MW["CaO"]) / ggbs["CaO"]
    m_H2O_opt = mol_H2O_opt * MW["H2O"]
    m_H2O_extra_opt = m_H2O_opt - (m_NaOH_opt * 0.5 + m_sil_opt * 0.665)

    if any(x < 0 for x in [m_GGBS_opt, m_sil_opt, m_H2O_extra_opt]):
        st.error("Optimization failed due to negative calculated mass.")
    else:
        st.subheader("Optimized mass proportions (g)")
        st.write(pd.DataFrame({
            "Component": ["Metapor", "GGBFS", "NaOH 50%", "Sodium Silicate", "Extra Water"],
            "Mass": [round(m_mk, 1), round(m_GGBS_opt, 1), round(m_NaOH_opt, 1), round(m_sil_opt, 1), round(m_H2O_extra_opt, 1)]
        }))

        final_ratios = {
            "Si/Al": mol_Si_opt / mol_Al_opt,
            "Na/Al": (2 * mol_Na2O_opt) / mol_Al_opt,
            "SiO2/Na2O": mol_Si_opt / mol_Na2O_opt,
            "H2O/Na2O": mol_H2O_opt / mol_Na2O_opt,
            "H2O/SiO2": mol_H2O_opt / mol_Si_opt,
            "Ca/Si": mol_Ca_opt / mol_Si_opt,
            "(Ca+Na)/Al": (mol_Ca_opt + 2 * mol_Na2O_opt) / mol_Al_opt
        }

        st.subheader("Optimized molar ratios")
        st.write(pd.DataFrame({
            "Ratio": list(final_ratios),
            "Value": [round(final_ratios[k], 2) for k in final_ratios],
            "Ideal": [ideal[k] for k in final_ratios],
            "Explanation": [desc[k] for k in final_ratios]
        }))

        st.subheader("4. Efflorescence Risk")
        risk = "Low" if final_ratios["Na/Al"] <= 1.0 and final_ratios["H2O/Na2O"] <= 13 else "High"
        st.warning(f"Estimated risk: {risk}")

        st.subheader("5. Pressability Assessment")
        if final_ratios["H2O/SiO2"] < 0.18:
            score = "3 = Poor (too dry)"
        elif 0.18 <= final_ratios["H2O/SiO2"] <= 0.26:
            score = "1 = Good (earth moist)"
        else:
            score = "2 = Moderate (wet)"
        st.info(f"Pressability score: {score}")
