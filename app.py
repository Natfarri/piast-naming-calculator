import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

matplotlib.rcParams["font.family"] = "DejaVu Sans"

st.set_page_config(
    page_title="Bayesian Calculator for Dynastic Naming Strategies",
    layout="wide",
)

# =========================================================
# CONSTANTS — FINAL ARTICLE / ONLINE SUPPLEMENT VERSION
# =========================================================

BASELINE_PRESET = "A — Full empirical n=280 / Pełna próba empiryczna n=280"

PRESETS = {
    "A — Full empirical n=280 / Pełna próba empiryczna n=280": {
        "pr_mg": 0.552,
        "pr_o": 0.393,
        "pr_sp": 0.005,
        "pr_r": 0.050,
        "lk_mg": 0.75,
        "lk_o": 0.10,
        "lk_sp": 0.07,
        "lk_r": 0.02,
    },
    "LOO — Excluding Piasts / Bez Piastów": {
        "pr_mg": 0.362,
        "pr_o": 0.466,
        "pr_sp": 0.005,
        "pr_r": 0.167,
        "lk_mg": 0.75,
        "lk_o": 0.10,
        "lk_sp": 0.07,
        "lk_r": 0.02,
    },
    "Xw — 10th century / Tylko X wiek": {
        "pr_mg": 0.417,
        "pr_o": 0.450,
        "pr_sp": 0.005,
        "pr_r": 0.128,
        "lk_mg": 0.75,
        "lk_o": 0.10,
        "lk_sp": 0.07,
        "lk_r": 0.02,
    },
    "H — Unconditional / Bezwarunkowy": {
        "pr_mg": 0.082,
        "pr_o": 0.816,
        "pr_sp": 0.041,
        "pr_r": 0.061,
        "lk_mg": 0.75,
        "lk_o": 0.10,
        "lk_sp": 0.07,
        "lk_r": 0.02,
    },
    "Custom / Własne wartości": {
        "pr_mg": 0.400,
        "pr_o": 0.400,
        "pr_sp": 0.100,
        "pr_r": 0.100,
        "lk_mg": 0.75,
        "lk_o": 0.10,
        "lk_sp": 0.07,
        "lk_r": 0.02,
    },
}

SCENARIO_TABLE = pd.DataFrame(
    [
        ["A", 0.552, 0.75, 0.005, 0.07, 0.393, 0.050, "91%"],
        ["A1", 0.552, 0.60, 0.005, 0.07, 0.393, 0.050, "89%"],
        ["A2", 0.552, 0.50, 0.005, 0.07, 0.393, 0.050, "87%"],
        ["A3", 0.552, 0.40, 0.005, 0.07, 0.393, 0.050, "84%"],
        ["B", 0.490, 0.70, 0.025, 0.07, 0.435, 0.050, "88%"],
        ["Asp", 0.552, 0.75, 0.005, 0.30, 0.393, 0.050, "91%"],
        ["LOO", 0.362, 0.75, 0.005, 0.07, 0.466, 0.167, "84%"],
        ["LOO (0.50)", 0.362, 0.50, 0.005, 0.07, 0.466, 0.167, "78%"],
        ["C", 0.432, 0.75, 0.150, 0.07, 0.368, 0.050, "87%"],
        ["D", 0.230, 0.75, 0.250, 0.10, 0.470, 0.050, "70%"],
        ["E", 0.130, 0.75, 0.300, 0.10, 0.520, 0.050, "54%"],
        ["F", 0.079, 0.75, 0.350, 0.15, 0.521, 0.050, "36%"],
        ["G", 0.058, 0.75, 0.400, 0.22, 0.492, 0.050, "24%"],
        ["H", 0.082, 0.75, 0.041, 0.07, 0.816, 0.061, "42%"],
        ["H1", 0.082, 0.50, 0.041, 0.07, 0.816, 0.061, "32%"],
        ["Xw", 0.417, 0.75, 0.005, 0.07, 0.450, 0.128, "87%"],
        ["Xw1", 0.130, 0.75, 0.039, 0.07, 0.620, 0.211, "59%"],
    ],
    columns=[
        "Scenario",
        "Prior Mg",
        "P(D|Mg)",
        "Prior Sp",
        "P(D|Sp)",
        "Prior O",
        "Prior R",
        "Posterior Mg",
    ],
)

CALIBRATION_TABLE = pd.DataFrame(
    [
        ["Bolesław Chrobry", "Mg", 0.65, 0.08, "91%", "8%"],
        ["Imre / Heinrich", "Mg", 0.70, 0.03, "97%", "3%"],
        ["Otto III", "O", 0.03, 0.90, "4%", "95%"],
    ],
    columns=["Case", "Known answer", "P(D|Mg)", "P(D|O)", "Post. Mg", "Post. O"],
)

DATA_SUMMARY = pd.DataFrame(
    [
        ["Total sample / Cała próba", 280],
        ["O", 200],
        ["Mg", 20],
        ["Mk", 19],
        ["M = Mg+Mk", 39],
        ["R", 31],
        ["S/Sp", 10],
        ["Reference class / Klasa odniesienia", 56],
    ],
    columns=["Category", "Value"],
)

KAPPA_TEXT = """
Coding-consistency summary / Podsumowanie zgodności kodowania:
n = 30, agreements = 27/30, Cohen’s κ = 0.87.
This reflects definitional consistency within the article’s current framework,
but should be interpreted cautiously and not as a substitute for a fully blinded
human inter-coder validation.

Test zgodności kodowania:
n = 30, zgodności = 27/30, κ Cohena = 0,87.
Wynik wspiera spójność definicji operacyjnych w obecnej wersji artykułu,
ale nie zastępuje pełnej, zaślepionej walidacji przez drugiego ludzkiego kodera.
"""

# =========================================================
# STATE HELPERS
# =========================================================

PARAM_KEYS = ["pr_mg", "pr_o", "pr_sp", "pr_r", "lk_mg", "lk_o", "lk_sp", "lk_r"]


def load_preset(preset_name: str) -> None:
    """Load preset values into both slider and numeric widgets."""
    values = PRESETS[preset_name]
    for key in PARAM_KEYS:
        val = float(values[key])
        st.session_state[f"{key}_sld"] = val
        st.session_state[f"{key}_num"] = val


def init_state() -> None:
    """Initialize app state once."""
    if "initialized" not in st.session_state:
        load_preset(BASELINE_PRESET)
        st.session_state["preset_choice"] = BASELINE_PRESET
        st.session_state["initialized"] = True


def sync_from_slider(key: str) -> None:
    st.session_state[f"{key}_num"] = st.session_state[f"{key}_sld"]


def sync_from_num(key: str) -> None:
    st.session_state[f"{key}_sld"] = st.session_state[f"{key}_num"]


init_state()

# =========================================================
# HEADER
# =========================================================

st.title("Bayesian Calculator for Dynastic Naming Strategies")
st.markdown(
    """
**Andrzej Jaskuła (2026)**  
Interactive research software accompanying the article on dynastic naming strategies and the case of **Świętopełk, son of Mieszko I**.

**Interaktywne oprogramowanie badawcze** towarzyszące artykułowi o strategiach nazewniczych dynastii i przypadkowi **Świętopełka, syna Mieszka I**.

**Final empirical basis / Ostateczna podstawa empiryczna:** `n = 280`  
**Reference class / Klasa odniesienia:** `n = 56`
"""
)

st.info(
    """
This version is aligned with the final article and Online Supplement.
Main-text rounded values (e.g. 0.53) are distinguished from exact scenario-table values used in the Supplement (e.g. 0.552).

Ta wersja jest zgodna z ostateczną wersją artykułu i suplementu.
Wartości zaokrąglone z tekstu głównego (np. 0,53) są odróżnione od wartości dokładnych z tabel scenariuszy w suplemencie (np. 0,552).
"""
)

# =========================================================
# TABS
# =========================================================

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "🧮 Calculator / Kalkulator",
        "📊 Article scenarios / Scenariusze z artykułu",
        "🧪 Calibration & κ / Kalibracja i κ",
        "📚 Data summary / Podsumowanie danych",
    ]
)

# =========================================================
# TAB 1 — CALCULATOR
# =========================================================

with tab1:
    st.subheader("Editable Bayesian calculator / Edytowalny kalkulator bayesowski")

    st.markdown(
        """
You can:
- load one of the article presets,
- edit all priors and likelihoods manually,
- test alternative dynastic corpora,
- use both sliders and numeric boxes.

Możesz:
- wczytać jeden z presetów z artykułu,
- ręcznie edytować wszystkie priory i likelihoody,
- testować inne zestawy dynastii,
- korzystać równocześnie z suwaków i pól liczbowych.
"""
    )

    top1, top2, top3 = st.columns([2, 1, 1])

    with top1:
        preset_choice = st.selectbox(
            "Preset / Preset",
            list(PRESETS.keys()),
            key="preset_choice",
        )

    with top2:
        if st.button("Load selected preset / Wczytaj preset", use_container_width=True):
            load_preset(preset_choice)
            st.rerun()

    with top3:
        if st.button("Restore baseline A / Przywróć bazowy A", use_container_width=True):
            st.session_state["preset_choice"] = BASELINE_PRESET
            load_preset(BASELINE_PRESET)
            st.rerun()

    col_prior, col_lik, col_result = st.columns([1.15, 1.15, 1.7])

    # ---------------------------
    # Priors
    # ---------------------------
    with col_prior:
        st.markdown("### 1. Priors / Priory P(H)")
        st.caption(
            "Raw priors may sum to any value; the app renormalizes them automatically to 1.0. / "
            "Surowe priory mogą sumować się do dowolnej wartości; aplikacja automatycznie normalizuje je do 1,0."
        )

        prior_specs = [
            ("pr_mg", "Prior Mg", 0.0, 1.0, 0.001),
            ("pr_o", "Prior O", 0.0, 1.0, 0.001),
            ("pr_sp", "Prior Sp", 0.0, 1.0, 0.001),
            ("pr_r", "Prior R", 0.0, 1.0, 0.001),
        ]

        for key, label, minv, maxv, step in prior_specs:
            st.markdown(f"**{label}**")
            c1, c2 = st.columns([2.2, 1])
            with c1:
                st.slider(
                    label,
                    min_value=minv,
                    max_value=maxv,
                    step=step,
                    key=f"{key}_sld",
                    label_visibility="collapsed",
                    on_change=sync_from_slider,
                    args=(key,),
                )
            with c2:
                st.number_input(
                    f"{label} value",
                    min_value=minv,
                    max_value=maxv,
                    step=step,
                    format="%.3f",
                    key=f"{key}_num",
                    label_visibility="collapsed",
                    on_change=sync_from_num,
                    args=(key,),
                )

    # ---------------------------
    # Likelihoods
    # ---------------------------
    with col_lik:
        st.markdown("### 2. Likelihoods / P(D|H)")
        st.caption(
            "You may keep article defaults or enter your own values derived from another dynastic corpus. / "
            "Możesz zachować wartości z artykułu albo wpisać własne, wyprowadzone z innego korpusu dynastycznego."
        )

        likelihood_specs = [
            ("lk_mg", "P(D|Mg)", 0.0, 1.0, 0.01),
            ("lk_o", "P(D|O)", 0.0, 1.0, 0.01),
            ("lk_sp", "P(D|Sp)", 0.0, 1.0, 0.01),
            ("lk_r", "P(D|R)", 0.0, 1.0, 0.01),
        ]

        for key, label, minv, maxv, step in likelihood_specs:
            st.markdown(f"**{label}**")
            c1, c2 = st.columns([2.2, 1])
            with c1:
                st.slider(
                    label,
                    min_value=minv,
                    max_value=maxv,
                    step=step,
                    key=f"{key}_sld",
                    label_visibility="collapsed",
                    on_change=sync_from_slider,
                    args=(key,),
                )
            with c2:
                st.number_input(
                    f"{label} value",
                    min_value=minv,
                    max_value=maxv,
                    step=step,
                    format="%.3f",
                    key=f"{key}_num",
                    label_visibility="collapsed",
                    on_change=sync_from_num,
                    args=(key,),
                )

    # ---------------------------
    # Results
    # ---------------------------
    with col_result:
        st.markdown("### 3. Results / Wyniki P(H|D)")

        raw_priors = {
            "Mg": float(st.session_state["pr_mg_num"]),
            "O": float(st.session_state["pr_o_num"]),
            "Sp": float(st.session_state["pr_sp_num"]),
            "R": float(st.session_state["pr_r_num"]),
        }

        likelihoods = {
            "Mg": float(st.session_state["lk_mg_num"]),
            "O": float(st.session_state["lk_o_num"]),
            "Sp": float(st.session_state["lk_sp_num"]),
            "R": float(st.session_state["lk_r_num"]),
        }

        raw_sum = sum(raw_priors.values())

        if raw_sum <= 0:
            st.error("Sum of priors must be greater than zero. / Suma priorów musi być większa od zera.")
        else:
            priors = {k: v / raw_sum for k, v in raw_priors.items()}

            numerators = {
                h: priors[h] * likelihoods[h]
                for h in ["Mg", "O", "Sp", "R"]
            }
            denominator = sum(numerators.values())

            if denominator <= 0:
                st.error("The sum of weighted likelihoods must be greater than zero. / Suma ważonych likelihoodów musi być większa od zera.")
            else:
                posteriors = {h: numerators[h] / denominator for h in numerators}

                norm_df = pd.DataFrame(
                    {
                        "Hypothesis / Hipoteza": ["Mg", "O", "Sp", "R"],
                        "Raw prior / Surowy prior": [
                            raw_priors["Mg"],
                            raw_priors["O"],
                            raw_priors["Sp"],
                            raw_priors["R"],
                        ],
                        "Normalized prior / Prior po normalizacji": [
                            priors["Mg"],
                            priors["O"],
                            priors["Sp"],
                            priors["R"],
                        ],
                        "Likelihood": [
                            likelihoods["Mg"],
                            likelihoods["O"],
                            likelihoods["Sp"],
                            likelihoods["R"],
                        ],
                        "Posterior": [
                            posteriors["Mg"],
                            posteriors["O"],
                            posteriors["Sp"],
                            posteriors["R"],
                        ],
                    }
                )

                display_df = norm_df.copy()
                for col in ["Raw prior / Surowy prior", "Normalized prior / Prior po normalizacji", "Likelihood", "Posterior"]:
                    display_df[col] = display_df[col].map(lambda x: f"{x:.3f}" if col != "Posterior" else f"{x:.1%}")

                st.metric("Raw sum of priors / Surowa suma priorów", f"{raw_sum:.3f}")
                st.dataframe(display_df, use_container_width=True, hide_index=True)

                fig, ax = plt.subplots(figsize=(7, 4))
                x = ["Mg", "O", "Sp", "R"]
                y = [posteriors["Mg"], posteriors["O"], posteriors["Sp"], posteriors["R"]]
                ax.bar(x, y)
                ax.set_ylim(0, 1.0)
                ax.set_ylabel("Posterior probability / Prawdopodobieństwo a posteriori")
                ax.set_title("Posterior distribution / Rozkład posteriorów")
                st.pyplot(fig)

                st.success(
                    f"Current Posterior Mg / Bieżący Posterior Mg: **{posteriors['Mg']:.1%}**"
                )

                st.markdown(
                    """
**Interpretation / Interpretacja**  
The calculator accepts article-based presets, but you may also enter your own priors and likelihoods derived from another corpus of dynasties.  
Kalkulator przyjmuje presety z artykułu, ale możesz również wpisać własne priory i likelihoody wyprowadzone z innego korpusu dynastii.
"""
                )

# =========================================================
# TAB 2 — ARTICLE SCENARIOS
# =========================================================

with tab2:
    st.subheader("Exact article scenarios / Dokładne scenariusze z artykułu")
    st.markdown(
        """
This table reproduces the scenario framework used in the final article and Online Supplement (Table S5).  
Tabela odtwarza układ scenariuszy użyty w ostatecznej wersji artykułu i suplementu (Tabela S5).
"""
    )
    st.dataframe(SCENARIO_TABLE, use_container_width=True, hide_index=True)

# =========================================================
# TAB 3 — CALIBRATION & KAPPA
# =========================================================

with tab3:
    st.subheader("Internal calibration / Kalibracja wewnętrzna")
    st.dataframe(CALIBRATION_TABLE, use_container_width=True, hide_index=True)

    st.markdown("### Coding consistency / Zgodność kodowania")
    st.info(KAPPA_TEXT)

# =========================================================
# TAB 4 — DATA SUMMARY
# =========================================================

with tab4:
    st.subheader("Empirical summary / Podsumowanie empiryczne")
    st.dataframe(DATA_SUMMARY, use_container_width=True, hide_index=True)

    st.markdown(
        """
**Note / Uwaga**  
Main-text prose may use rounded values for readability, while the scenario engine follows exact values from the Supplement.  
Tekst główny może używać wartości zaokrąglonych dla czytelności, natomiast silnik scenariuszy korzysta z wartości dokładnych z suplementu.
"""
    )

st.markdown("---")
st.caption(
    "© 2026 Andrzej Jaskuła | Bayesian Calculator for Dynastic Naming Strategies | DOI: 10.5281/zenodo.18741761"
)
