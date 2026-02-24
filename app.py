import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

# Konfiguracja czcionek dla wykresów
matplotlib.rcParams['font.family'] = 'DejaVu Sans'

st.set_page_config(
    page_title="Bayes — Dynastic Onomastics v28",
    layout="wide"
)

# --- TYTUŁ I OPIS ---
st.title("Bayesian Calculator for Dynastic Naming Strategies (v28)")
st.markdown(
    "**Andrzej Jaskuła 2026** — Probabilistic model for the name Świętopełk (son of Mieszko I). "
    "Accompanying software for the article: *Dynastic Naming Strategies in Central Europe (9th–14th Centuries)*. "
    "**Updated Sample: n=280** (including Carolingians)."
)

st.markdown("---")

# --- OPIS MODELU (Expandable) ---
with st.expander("ℹ️ About this model / O modelu"):
    st.markdown("""
    **EN:** This Bayesian calculator estimates the posterior probability P(H|D) for four hypotheses regarding the origin of the name Świętopełk:
    - **Mg**: Maternal genealogical (Mojmirid grandmother).
    - **O**: Paternal (unidentified ancestor).
    - **Sp**: Political/Alliance prestige (territorial eponym).
    - **R**: Dynastic (newly coined/traditional).
    
    **PL:** Model oblicza posterior dla czterech hipotez dotyczących imienia Świętopełk:
    - **Mg**: Babka Mojmirowiczówna (linia matczyna).
    - **O**: Nieznany przodek ojcowski.
    - **Sp**: Deklaracja polityczna (eponimat Moraw).
    - **R**: Imię rodowe/nowe.
    """)

# --- ZAKŁADKI ---
tab1, tab2, tab3 = st.tabs(["🧮 Calculator", "📊 Sensitivity Analysis", "📖 Article Scenarios"])

# ==============================================================================
# ZAKŁADKA 1 — KALKULATOR GŁÓWNY
# ==============================================================================
with tab1:
    col_prior, col_lik, col_wynik = st.columns([1, 1, 2])

    with col_prior:
        st.subheader("1. Priors / Priory P(H)")
        podproba = st.selectbox(
            "Select reference data / Wybierz dane (v28):",
            [
                "Full sample / Cała próba n=280 (A)",
                "10th Century only / Tylko X wiek (Xw)",
                "LOO (excluding Piasts)",
                "Unconditional / Bezwarunkowy (H)",
                "Custom / Własne"
            ]
        )

        # Definicje priorów z artykułu v28 (Tabela 10)
        defaults = {
            "Full sample / Cała próba n=280 (A)": (0.552, 0.393, 0.005, 0.050),
            "10th Century only / Tylko X wiek (Xw)": (0.417, 0.450, 0.005, 0.128),
            "LOO (excluding Piasts)": (0.356, 0.470, 0.005, 0.169),
            "Unconditional / Bezwarunkowy (H)": (0.085, 0.812, 0.045, 0.058),
            "Custom / Własne": (0.400, 0.400, 0.100, 0.100),
        }

        d_mg, d_o, d_sp, d_r = defaults[podproba]

        pr_mg = st.slider("Prior Mg", 0.0, 1.0, d_mg, 0.001)
        pr_o  = st.slider("Prior O", 0.0, 1.0, d_o, 0.001)
        pr_sp = st.slider("Prior Sp", 0.0, 1.0, d_sp, 0.001)
        pr_r  = st.slider("Prior R", 0.0, 1.0, d_r, 0.001)

        suma = pr_mg + pr_o + pr_sp + pr_r
        pmg, po, psp, pr = pr_mg/suma, pr_o/suma, pr_sp/suma, pr_r/suma

    with col_lik:
        st.subheader("2. Likelihoods / P(D|H)")
        l_mg = st.slider("P(D|Mg) - Mojmirid heritage", 0.1, 1.0, 0.75, 0.05)
        l_o  = st.slider("P(D|O) - Paternal chance", 0.01, 0.5, 0.10, 0.01)
        l_sp = st.slider("P(D|Sp) - Political claim", 0.01, 0.5, 0.07, 0.01)
        l_r  = st.slider("P(D|R) - Dynastic chance", 0.01, 0.5, 0.02, 0.01)

    with col_wynik:
        st.subheader("3. Results / Wyniki P(H|D)")
        
        # Obliczenia Bayesa
        num = [pmg*l_mg, po*l_o, psp*l_sp, pr*l_r]
        mianownik = sum(num)
        posteriors = [n/mianownik for n in num]

        res_df = pd.DataFrame({
            "Hypothesis": ["Mg (Mojmirid)", "O (Paternal)", "Sp (Political)", "R (Dynastic)"],
            "Posterior": [f"{p:.1%}" for p in posteriors]
        })
        st.table(res_df)

        # Wykres
        fig, ax = plt.subplots(figsize=(6, 4))
        colors = ["#2ecc71", "#3498db", "#e67e22", "#e74c3c"]
        ax.bar(res_df["Hypothesis"], posteriors, color=colors)
        ax.set_ylim(0, 1.0)
        ax.set_ylabel("Probability")
        st.pyplot(fig)

# ==============================================================================
# ZAKŁADKA 2 — ANALIZA WRAŻLIWOŚCI
# ==============================================================================
with tab2:
    st.subheader("Sensitivity Analysis Matrix (Post. Mg)")
    st.write("Wpływ zmiany P(D|Mg) oraz Prioru Mg na wynik końcowy (Posterior).")
    
    pdmg_range = [0.4, 0.5, 0.6, 0.7, 0.75]
    priors_range = [0.085, 0.356, 0.417, 0.552] # Unconditional, LOO, 10th C, Full n=280
    
    matrix = []
    for pm in priors_range:
        row = []
        for lm in pdmg_range:
            # Uproszczony model dla macierzy (pozostałe priory proporcjonalnie)
            n_mg = pm * lm
            n_oth = (1-pm) * 0.08 # średni waży likelihood dla O/Sp/R
            row.append(f"{n_mg/(n_mg+n_oth):.1%}")
        matrix.append(row)
    
    df_matrix = pd.DataFrame(matrix, index=priors_range, columns=pdmg_range)
    st.table(df_matrix)
    st.caption("Priors on Y-axis (Mg), Likelihoods on X-axis P(D|Mg).")

# ==============================================================================
# ZAKŁADKA 3 — SCENARIUSZE
# ==============================================================================
with tab3:
    st.subheader("Reproduction of Article Scenarios (Table 10)")
    st.markdown("""
    - **Scenario A (Full Empirical n=280)**: Prior Mg = 0.552, P(D|Mg) = 0.75 -> **Post. Mg = 91%**
    - **Scenario LOO (Leave-one-out)**: Prior Mg = 0.356, P(D|Mg) = 0.75 -> **Post. Mg = 84%**
    - **Scenario Xw (10th Century)**: Prior Mg = 0.417, P(D|Mg) = 0.75 -> **Post. Mg = 87%**
    - **Scenario H (Unconditional)**: Prior Mg = 0.085, P(D|Mg) = 0.75 -> **Post. Mg = 43%** (Ojcowska H_O dominuje)
    """)

st.markdown("---")
st.caption("© 2026 Andrzej Jaskuła | Research Software for 'Early Medieval Europe' | DOI: 10.5281/zenodo.18741761")
