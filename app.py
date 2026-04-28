import math
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

# =========================
# CONFIG
# =========================
matplotlib.rcParams["font.family"] = "DejaVu Sans"

st.set_page_config(
    page_title="Bayesian Calculator for Dynastic Naming Strategies",
    layout="wide"
)

APP_TITLE = "Bayesian Calculator for Dynastic Naming Strategies"
APP_SUBTITLE = (
    "Research software accompanying the article on dynastic naming strategies "
    "and the case of Świętopełk, son of Mieszko I."
)

AUTHOR = "Andrzej Jaskuła"
ORCID = "0000-0001-8705-8384"

# Uzupełnij, jeśli chcesz:
APP_URL = "https://piast-naming-calculator-tnyvtnqqrfpnmykwl9yfpr.streamlit.app/"
GITHUB_URL = "https://github.com/Natfarri/piast-naming-calculator"
ZENODO_DOI = "10.5281/zenodo.18741761"

# =========================
# CORE DATA FROM ARTICLE / SUPPLEMENT
# =========================

# Wartości dokładne z suplementu (Table S5)
# P(D|O)=0.10 i P(D|R)=0.02 są stałe we wszystkich scenariuszach tabelarycznych.
SCENARIOS = {
    "A — empirical baseline": {
        "priors": {"Mg": 0.552, "O": 0.393, "Sp": 0.005, "R": 0.050},
        "likelihoods": {"Mg": 0.75, "O": 0.10, "Sp": 0.07, "R": 0.02},
        "expected_post_mg": 0.91,
        "note": "Scenariusz bazowy z Table S5."
    },
    "A1 — empirical, P(D|Mg)=0.60": {
        "priors": {"Mg": 0.552, "O": 0.393, "Sp": 0.005, "R": 0.050},
        "likelihoods": {"Mg": 0.60, "O": 0.10, "Sp": 0.07, "R": 0.02},
        "expected_post_mg": 0.89,
        "note": "Obniżone P(D|Mg) o 20%."
    },
    "A2 — empirical, P(D|Mg)=0.50": {
        "priors": {"Mg": 0.552, "O": 0.393, "Sp": 0.005, "R": 0.050},
        "likelihoods": {"Mg": 0.50, "O": 0.10, "Sp": 0.07, "R": 0.02},
        "expected_post_mg": 0.87,
        "note": "Obniżone P(D|Mg) o 33%."
    },
    "A3 — empirical, P(D|Mg)=0.40": {
        "priors": {"Mg": 0.552, "O": 0.393, "Sp": 0.005, "R": 0.050},
        "likelihoods": {"Mg": 0.40, "O": 0.10, "Sp": 0.07, "R": 0.02},
        "expected_post_mg": 0.84,
        "note": "Dolna granica empiryczna."
    },
    "B — empirical cautious": {
        "priors": {"Mg": 0.490, "O": 0.435, "Sp": 0.025, "R": 0.050},
        "likelihoods": {"Mg": 0.70, "O": 0.10, "Sp": 0.07, "R": 0.02},
        "expected_post_mg": 0.88,
        "note": "Sp ×5 względem empirycznego."
    },
    "Asp — empirical with P(D|Sp)=0.30": {
        "priors": {"Mg": 0.552, "O": 0.393, "Sp": 0.005, "R": 0.050},
        "likelihoods": {"Mg": 0.75, "O": 0.10, "Sp": 0.30, "R": 0.02},
        "expected_post_mg": 0.91,
        "note": "P(D|Sp) podniesione 4×."
    },
    "LOO — leave-one-out, P(D|Mg)=0.75": {
        "priors": {"Mg": 0.362, "O": 0.466, "Sp": 0.005, "R": 0.167},
        "likelihoods": {"Mg": 0.75, "O": 0.10, "Sp": 0.07, "R": 0.02},
        "expected_post_mg": 0.84,
        "note": "Bez Piastów w klasie odniesienia."
    },
    "LOO — leave-one-out, P(D|Mg)=0.50": {
        "priors": {"Mg": 0.362, "O": 0.466, "Sp": 0.005, "R": 0.167},
        "likelihoods": {"Mg": 0.50, "O": 0.10, "Sp": 0.07, "R": 0.02},
        "expected_post_mg": 0.78,
        "note": "LOO + obniżone P(D|Mg)."
    },
    "C — conservative (Sp×30)": {
        "priors": {"Mg": 0.432, "O": 0.368, "Sp": 0.150, "R": 0.050},
        "likelihoods": {"Mg": 0.75, "O": 0.10, "Sp": 0.07, "R": 0.02},
        "expected_post_mg": 0.87,
        "note": "Test odporności, Sp podniesione 30×."
    },
    "D — skeptical (Sp×50)": {
        "priors": {"Mg": 0.230, "O": 0.470, "Sp": 0.250, "R": 0.050},
        "likelihoods": {"Mg": 0.75, "O": 0.10, "Sp": 0.10, "R": 0.02},
        "expected_post_mg": 0.70,
        "note": "Scenariusz sceptyczny."
    },
    "E — very skeptical (Sp×60)": {
        "priors": {"Mg": 0.130, "O": 0.520, "Sp": 0.300, "R": 0.050},
        "likelihoods": {"Mg": 0.75, "O": 0.10, "Sp": 0.10, "R": 0.02},
        "expected_post_mg": 0.54,
        "note": "Scenariusz bardzo sceptyczny."
    },
    "F — extreme skeptical (Sp×70)": {
        "priors": {"Mg": 0.079, "O": 0.521, "Sp": 0.350, "R": 0.050},
        "likelihoods": {"Mg": 0.75, "O": 0.10, "Sp": 0.15, "R": 0.02},
        "expected_post_mg": 0.36,
        "note": "Scenariusz ekstremalnie sceptyczny."
    },
    "G — maximal skeptical (Sp×80)": {
        "priors": {"Mg": 0.058, "O": 0.492, "Sp": 0.400, "R": 0.050},
        "likelihoods": {"Mg": 0.75, "O": 0.10, "Sp": 0.22, "R": 0.02},
        "expected_post_mg": 0.24,
        "note": "Scenariusz maksymalnie sceptyczny."
    },
    "H — unconditional, P(D|Mg)=0.75": {
        "priors": {"Mg": 0.082, "O": 0.816, "Sp": 0.041, "R": 0.061},
        "likelihoods": {"Mg": 0.75, "O": 0.10, "Sp": 0.07, "R": 0.02},
        "expected_post_mg": 0.42,
        "note": "Prior bezwarunkowy z n=245."
    },
    "H1 — unconditional, P(D|Mg)=0.50": {
        "priors": {"Mg": 0.082, "O": 0.816, "Sp": 0.041, "R": 0.061},
        "likelihoods": {"Mg": 0.50, "O": 0.10, "Sp": 0.07, "R": 0.02},
        "expected_post_mg": 0.32,
        "note": "Prior bezwarunkowy + minimalne P(D|Mg)."
    },
    "Xw — 10th century, class-based": {
        "priors": {"Mg": 0.417, "O": 0.450, "Sp": 0.005, "R": 0.128},
        "likelihoods": {"Mg": 0.75, "O": 0.10, "Sp": 0.07, "R": 0.02},
        "expected_post_mg": 0.87,
        "note": "Prior z podpróby X wieku."
    },
    "Xw1 — 10th century, unconditional": {
        "priors": {"Mg": 0.130, "O": 0.620, "Sp": 0.039, "R": 0.211},
        "likelihoods": {"Mg": 0.75, "O": 0.10, "Sp": 0.07, "R": 0.02},
        "expected_post_mg": 0.59,
        "note": "Prior bezwarunkowy z podpróby X wieku."
    },
}

# Zaokrąglenia zgodne z tekstem głównym artykułu
MAIN_TEXT_ROUNDED = {
    "Empirical baseline (rounded in main text)": {
        "priors": {"Mg": 0.53, "O": 0.40, "Sp": 0.005, "R": 0.065},
        "likelihoods": {"Mg": 0.75, "O": 0.10, "Sp": 0.07, "R": 0.02},
    }
}

CATEGORY_COUNTS = {
    "Total sample n": 280,
    "O": 200,
    "Mg": 20,
    "Mk": 19,
    "M (Mg+Mk)": 39,
    "R": 31,
    "S/Sp": 10,
    "Reference class n": 56,
}

CALIBRATION_CASES = [
    {
        "Case": "Bolesław Chrobry (Mieszko I × Dobrawa)",
        "Known": "Mg",
        "priors": {"Mg": 0.53, "O": 0.40, "Sp": 0.005, "R": 0.065},
        "likelihoods": {"Mg": 0.65, "O": 0.08, "Sp": 0.07, "R": 0.02},
        "expected_mg": 0.91,
        "expected_o": 0.08,
    },
    {
        "Case": "Imre / Heinrich (István I × Gizela)",
        "Known": "Mg",
        "priors": {"Mg": 0.53, "O": 0.40, "Sp": 0.005, "R": 0.065},
        "likelihoods": {"Mg": 0.70, "O": 0.03, "Sp": 0.07, "R": 0.02},
        "expected_mg": 0.97,
        "expected_o": 0.03,
    },
    {
        "Case": "Otto III (Otto II × Theophano)",
        "Known": "O",
        "priors": {"Mg": 0.53, "O": 0.40, "Sp": 0.005, "R": 0.065},
        "likelihoods": {"Mg": 0.03, "O": 0.90, "Sp": 0.07, "R": 0.02},
        "expected_mg": 0.04,
        "expected_o": 0.95,
    },
]

COHEN_KAPPA_SUMMARY = {
    "Sample size": 30,
    "Agreement": "27/30",
    "Cohen's kappa": 0.87,
    "Interpretation": "almost perfect agreement (Landis–Koch scale)",
    "Caution": (
        "The coding test was not fully blind; the LLM should be treated as an auxiliary tool, "
        "not a substitute for an independent human coder."
    ),
}

# =========================
# HELPERS
# =========================
def normalize_priors(priors: dict) -> dict:
    total = sum(priors.values())
    if total <= 0:
        return priors
    return {k: v / total for k, v in priors.items()}

def bayes_posteriors(priors: dict, likelihoods: dict) -> dict:
    priors = normalize_priors(priors)
    numerators = {k: priors[k] * likelihoods[k] for k in priors}
    denominator = sum(numerators.values())
    if denominator == 0:
        return {k: 0.0 for k in priors}
    return {k: numerators[k] / denominator for k in priors}

def pct(x: float, digits: int = 1) -> str:
    return f"{x * 100:.{digits}f}%"

def pp_diff(a: float, b: float) -> str:
    return f"{(a - b) * 100:+.1f} pp"

def odds_against_rest(posts: dict, key: str) -> float:
    focal = posts[key]
    rest = max(1e-12, 1 - focal)
    return focal / rest

def scenario_to_row(name: str, cfg: dict) -> dict:
    posts = bayes_posteriors(cfg["priors"], cfg["likelihoods"])
    expected = cfg["expected_post_mg"]
    return {
        "Scenario": name,
        "Prior Mg": cfg["priors"]["Mg"],
        "Prior O": cfg["priors"]["O"],
        "Prior Sp": cfg["priors"]["Sp"],
        "Prior R": cfg["priors"]["R"],
        "P(D|Mg)": cfg["likelihoods"]["Mg"],
        "P(D|O)": cfg["likelihoods"]["O"],
        "P(D|Sp)": cfg["likelihoods"]["Sp"],
        "P(D|R)": cfg["likelihoods"]["R"],
        "Posterior Mg (computed)": posts["Mg"],
        "Posterior Mg (article)": expected,
        "Δ": posts["Mg"] - expected,
        "Posterior O": posts["O"],
        "Posterior Sp": posts["Sp"],
        "Posterior R": posts["R"],
        "Note": cfg["note"],
    }

# =========================
# HEADER
# =========================
st.title(APP_TITLE)
st.markdown(
    f"**{AUTHOR}** · ORCID: {ORCID}  \n"
    f"{APP_SUBTITLE}"
)

st.info(
    "This app uses the **exact scenario values from the Online Supplement** "
    "(e.g. 0.552, 0.362, 0.082), while the main article body may display "
    "rounded values (e.g. 0.53, 0.40, 0.065) for readability."
)

with st.expander("About this app / O aplikacji", expanded=False):
    st.markdown(
        """
**EN**  
This calculator reproduces the Bayesian scenarios reported in the article and supplement
for the case of Świętopełk, son of Mieszko I. It includes:

- the exact scenario grid from Table S5,
- the rounded main-text baseline,
- internal calibration on three known cases (Table A3),
- coding-reliability summary (Table A4),
- the main empirical totals used in the article (n=280).

**PL**  
Kalkulator odtwarza scenariusze bayesowskie z artykułu i suplementu dla przypadku
Świętopełka, syna Mieszka I. Zawiera:

- dokładne scenariusze z Tabeli S5,
- zaokrąglenia użyte w tekście głównym,
- kalibrację wewnętrzną na trzech przypadkach znanych (Tabela A3),
- podsumowanie testu zgodności kodowania (Tabela A4),
- główne sumy empiryczne użyte w artykule (n=280).

**Model hypotheses**
- **Mg** — maternal genealogical
- **O** — paternal
- **Sp** — political / prestige eponym
- **R** — dynastic / new / rodowe
        """
    )

# =========================
# TABS
# =========================
tab1, tab2, tab3, tab4 = st.tabs(
    [
        "🧮 Calculator",
        "📊 Article scenarios",
        "🧪 Calibration & κ",
        "📚 Data summary"
    ]
)

# =========================
# TAB 1 — CALCULATOR
# =========================
with tab1:
    st.subheader("Interactive Bayesian calculator")

    preset_names = list(SCENARIOS.keys()) + list(MAIN_TEXT_ROUNDED.keys()) + ["Custom"]
    preset = st.selectbox("Preset / Zestaw startowy", preset_names, index=0)

    if preset in SCENARIOS:
        base_priors = SCENARIOS[preset]["priors"].copy()
        base_liks = SCENARIOS[preset]["likelihoods"].copy()
        preset_note = SCENARIOS[preset]["note"]
    elif preset in MAIN_TEXT_ROUNDED:
        base_priors = MAIN_TEXT_ROUNDED[preset]["priors"].copy()
        base_liks = MAIN_TEXT_ROUNDED[preset]["likelihoods"].copy()
        preset_note = "Rounded values shown in the main text."
    else:
        base_priors = {"Mg": 0.53, "O": 0.40, "Sp": 0.005, "R": 0.065}
        base_liks = {"Mg": 0.75, "O": 0.10, "Sp": 0.07, "R": 0.02}
        preset_note = "Custom settings."

    st.caption(preset_note)

    col1, col2, col3 = st.columns([1.2, 1.2, 1.6])

    with col1:
        st.markdown("#### Priors / Priory")
        pr_mg = st.number_input("Prior Mg", min_value=0.0, max_value=1.0, value=float(base_priors["Mg"]), step=0.001, format="%.3f")
        pr_o  = st.number_input("Prior O",  min_value=0.0, max_value=1.0, value=float(base_priors["O"]),  step=0.001, format="%.3f")
        pr_sp = st.number_input("Prior Sp", min_value=0.0, max_value=1.0, value=float(base_priors["Sp"]), step=0.001, format="%.3f")
        pr_r  = st.number_input("Prior R",  min_value=0.0, max_value=1.0, value=float(base_priors["R"]),  step=0.001, format="%.3f")

        priors = normalize_priors({"Mg": pr_mg, "O": pr_o, "Sp": pr_sp, "R": pr_r})
        st.write("Normalized priors / Priory po normalizacji:")
        st.dataframe(pd.DataFrame([priors]).rename_axis("set").reset_index(drop=True), use_container_width=True)

    with col2:
        st.markdown("#### Likelihoods / P(D|H)")
        lk_mg = st.number_input("P(D|Mg)", min_value=0.0, max_value=1.0, value=float(base_liks["Mg"]), step=0.01, format="%.2f")
        lk_o  = st.number_input("P(D|O)",  min_value=0.0, max_value=1.0, value=float(base_liks["O"]),  step=0.01, format="%.2f")
        lk_sp = st.number_input("P(D|Sp)", min_value=0.0, max_value=1.0, value=float(base_liks["Sp"]), step=0.01, format="%.2f")
        lk_r  = st.number_input("P(D|R)",  min_value=0.0, max_value=1.0, value=float(base_liks["R"]),  step=0.01, format="%.2f")

        likelihoods = {"Mg": lk_mg, "O": lk_o, "Sp": lk_sp, "R": lk_r}
        st.write("Likelihood vector:")
        st.dataframe(pd.DataFrame([likelihoods]).rename_axis("set").reset_index(drop=True), use_container_width=True)

    with col3:
        st.markdown("#### Results / Wyniki")
        posts = bayes_posteriors(priors, likelihoods)

        c1, c2 = st.columns(2)
        c1.metric("Posterior Mg", pct(posts["Mg"], 1))
        c2.metric("Odds Mg vs. rest", f"{odds_against_rest(posts, 'Mg'):.2f}:1")

        result_df = pd.DataFrame({
            "Hypothesis": ["Mg", "O", "Sp", "R"],
            "Posterior": [posts["Mg"], posts["O"], posts["Sp"], posts["R"]],
            "Posterior (%)": [pct(posts["Mg"], 1), pct(posts["O"], 1), pct(posts["Sp"], 1), pct(posts["R"], 1)],
        })

        st.dataframe(result_df, use_container_width=True, hide_index=True)

        fig, ax = plt.subplots(figsize=(7, 4))
        ax.bar(result_df["Hypothesis"], result_df["Posterior"])
        ax.set_ylim(0, 1)
        ax.set_ylabel("Posterior probability")
        ax.set_title("Posterior distribution")
        st.pyplot(fig)

    st.markdown("---")
    st.markdown(
        """
**Interpretive reminder**  
The calculator is a formal aid, not a substitute for source criticism.
In the article, the **working scenario** is the leave-one-out estimate (**LOO**),
while the empirical baseline (**A**) and unconditional scenarios (**H/H1**) define
the upper and lower bounds of the reported range.
        """
    )

# =========================
# TAB 2 — ARTICLE SCENARIOS
# =========================
with tab2:
    st.subheader("Exact reproduction of article / supplement scenarios")

    scenario_rows = [scenario_to_row(name, cfg) for name, cfg in SCENARIOS.items()]
    scenarios_df = pd.DataFrame(scenario_rows)

    display_df = scenarios_df.copy()
    display_df["Posterior Mg (computed)"] = display_df["Posterior Mg (computed)"].map(lambda x: pct(x, 1))
    display_df["Posterior Mg (article)"] = display_df["Posterior Mg (article)"].map(lambda x: pct(x, 1))
    display_df["Posterior O"] = display_df["Posterior O"].map(lambda x: pct(x, 1))
    display_df["Posterior Sp"] = display_df["Posterior Sp"].map(lambda x: pct(x, 1))
    display_df["Posterior R"] = display_df["Posterior R"].map(lambda x: pct(x, 1))
    display_df["Δ"] = scenarios_df["Δ"].map(lambda x: pp_diff(x, 0.0))

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.markdown("#### Rounded baseline used in the main article body")
    rounded_rows = []
    for name, cfg in MAIN_TEXT_ROUNDED.items():
        posts = bayes_posteriors(cfg["priors"], cfg["likelihoods"])
        rounded_rows.append({
            "Scenario": name,
            "Prior Mg": cfg["priors"]["Mg"],
            "Prior O": cfg["priors"]["O"],
            "Prior Sp": cfg["priors"]["Sp"],
            "Prior R": cfg["priors"]["R"],
            "P(D|Mg)": cfg["likelihoods"]["Mg"],
            "P(D|O)": cfg["likelihoods"]["O"],
            "P(D|Sp)": cfg["likelihoods"]["Sp"],
            "P(D|R)": cfg["likelihoods"]["R"],
            "Posterior Mg": pct(posts["Mg"], 1),
            "Posterior O": pct(posts["O"], 1),
            "Posterior Sp": pct(posts["Sp"], 1),
            "Posterior R": pct(posts["R"], 1),
        })
    st.dataframe(pd.DataFrame(rounded_rows), use_container_width=True, hide_index=True)

# =========================
# TAB 3 — CALIBRATION & KAPPA
# =========================
with tab3:
    st.subheader("Internal calibration (Table A3)")

    calib_rows = []
    for case in CALIBRATION_CASES:
        posts = bayes_posteriors(case["priors"], case["likelihoods"])
        calib_rows.append({
            "Case": case["Case"],
            "Known answer": case["Known"],
            "P(D|Mg)": case["likelihoods"]["Mg"],
            "P(D|O)": case["likelihoods"]["O"],
            "Posterior Mg (computed)": pct(posts["Mg"], 1),
            "Posterior Mg (article)": pct(case["expected_mg"], 1),
            "Posterior O (computed)": pct(posts["O"], 1),
            "Posterior O (article)": pct(case["expected_o"], 1),
        })

    st.dataframe(pd.DataFrame(calib_rows), use_container_width=True, hide_index=True)

    st.markdown("#### Coding-reliability summary (Table A4)")
    kappa_df = pd.DataFrame([COHEN_KAPPA_SUMMARY])
    st.dataframe(kappa_df, use_container_width=True, hide_index=True)

    st.warning(
        "Methodological note: the κ result can be reported as part of the current article apparatus, "
        "but it should be described cautiously. It supports definitional consistency, not definitive "
        "inter-coder reliability in the strict Q1 sense."
    )

# =========================
# TAB 4 — DATA SUMMARY
# =========================
with tab4:
    st.subheader("Empirical totals used in the article")

    counts_df = pd.DataFrame(
        [{"Measure": k, "Value": v} for k, v in CATEGORY_COUNTS.items()]
    )
    st.dataframe(counts_df, use_container_width=True, hide_index=True)

    st.markdown("#### Methodological constants")
    st.markdown(
        """
- Total empirical sample: **n = 280**
- Case study excluded from the base sample: **Świętopełk, son of Mieszko I**
- Reference class: **n = 56**
- Exact scenario grid: **Table S5**
- Internal calibration: **Table A3**
- Coding-consistency summary: **Table A4**
        """
    )

    st.markdown("#### Links")
    st.markdown(
        f"""
- App: {APP_URL}
- GitHub: {GITHUB_URL}
- Zenodo DOI: {ZENODO_DOI}
        """
    )

st.markdown("---")
st.caption(
    f"© 2026 {AUTHOR} · ORCID {ORCID} · "
    f"App: {APP_URL} · GitHub: {GITHUB_URL} · DOI: {ZENODO_DOI}"
)
