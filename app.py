import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="The Relationship Audit",
    page_icon="💘",
    layout="wide",
)


# ============================================================
# STYLING
# ============================================================

st.markdown(
    """
    <style>

    .block-container {
        max-width: 1180px;
        padding-top: 3rem;
        padding-bottom: 4rem;
    }

    h1, h2, h3 {
        letter-spacing: -0.03em;
    }

    div[data-testid="stMetric"] {
        border: 1px solid rgba(128,128,128,.22);
        border-radius: 18px;
        padding: 1.1rem;
        background: rgba(128,128,128,.05);
    }

    div[data-testid="stButton"] button {
        border-radius: 14px;
        min-height: 3.2rem;
        font-weight: 700;
    }

    .stProgress > div > div > div > div {
        border-radius: 20px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DATA
# ============================================================

CATEGORIES = [
    "Emotional Safety",
    "Trust",
    "Communication",
    "Romance / Affection",
    "Sex / Physical Chemistry",
    "Intellectual Connection",
    "Fun / Adventure",
    "Support for Goals / Career",
    "Finances",
    "Friendships / Social Life",
    "Peace vs. Anxiety",
    "Consistency / Reliability",
    "Conflict Resolution",
    "How I Felt About Myself",
]

DESCRIPTIONS = {
    "Emotional Safety":
        "Did you feel emotionally safe, accepted, respected, and able to be vulnerable?",

    "Trust":
        "Could you trust them and feel secure in the relationship without constantly questioning their intentions?",

    "Communication":
        "Could you communicate openly, honestly, and effectively with each other?",

    "Romance / Affection":
        "Did you feel wanted, loved, pursued, and emotionally connected?",

    "Sex / Physical Chemistry":
        "How positively did the sexual and physical connection affect the relationship?",

    "Intellectual Connection":
        "Did you feel mentally stimulated, understood, and able to connect through ideas and conversation?",

    "Fun / Adventure":
        "Did the relationship add fun, laughter, excitement, spontaneity, or memorable experiences to your life?",

    "Support for Goals / Career":
        "Did they support your ambitions, growth, education, career, and personal goals?",

    "Finances":
        "Did the relationship have a positive or negative effect on your financial well-being and stability?",

    "Friendships / Social Life":
        "Did the relationship support a healthy social life and your connections with other people?",

    "Peace vs. Anxiety":
        "Did the relationship generally bring you peace, or did it create stress, uncertainty, and anxiety?",

    "Consistency / Reliability":
        "Could you depend on them to show up consistently and follow through?",

    "Conflict Resolution":
        "When problems happened, were you able to resolve them in a healthy and productive way?",

    "How I Felt About Myself":
        "Did you generally like who you were and how you felt about yourself while you were in this relationship?",
}

SCORE_LABELS = {
    -2: "Strongly Negative",
    -1: "Somewhat Negative",
    0: "Neutral / Mixed",
    1: "Positive",
    2: "Strongly Positive",
}

CORE_HEALTH_CATEGORIES = [
    "Emotional Safety",
    "Trust",
    "Communication",
    "Peace vs. Anxiety",
    "Consistency / Reliability",
    "Conflict Resolution",
]


# ============================================================
# SESSION STATE
# ============================================================

if "relationships" not in st.session_state:
    st.session_state.relationships = []

if "latest_result" not in st.session_state:
    st.session_state.latest_result = None

if "audit_active" not in st.session_state:
    st.session_state.audit_active = False

if "audit_name" not in st.session_state:
    st.session_state.audit_name = ""

if "question_index" not in st.session_state:
    st.session_state.question_index = 0

if "current_scores" not in st.session_state:
    st.session_state.current_scores = {}

if "show_result" not in st.session_state:
    st.session_state.show_result = False


# ============================================================
# FUNCTIONS
# ============================================================

def score_display(score):
    if score > 0:
        return f"+{score}"

    return str(score)


def impact_interpretation(score):

    if score >= 21:
        return (
            "Exceptional Positive Impact",
            "This relationship appears to have added substantial value across nearly every area of your life.",
        )

    elif score >= 12:
        return (
            "Strong Positive Impact",
            "Overall, this relationship appears to have contributed meaningfully to your happiness and well-being.",
        )

    elif score >= 5:
        return (
            "Moderately Positive Impact",
            "The relationship had more positive effects than negative ones, although there were meaningful areas of weakness.",
        )

    elif score >= -4:
        return (
            "Mixed Impact",
            "The positives and negatives were relatively balanced. The individual category scores matter more than the total here.",
        )

    elif score >= -11:
        return (
            "Moderately Negative Impact",
            "The relationship appears to have taken more from your life than it added overall.",
        )

    elif score >= -20:
        return (
            "Strong Negative Impact",
            "This relationship appears to have negatively affected several important areas of your life.",
        )

    else:
        return (
            "Severe Negative Impact",
            "The relationship appears to have had a deeply negative impact across many areas of your life.",
        )


def impact_label(score):
    return impact_interpretation(score)[0]


def health_label(score):

    if score >= 85:
        return "Very Healthy"

    elif score >= 70:
        return "Healthy"

    elif score >= 55:
        return "Mixed"

    elif score >= 40:
        return "Concerning"

    elif score >= 25:
        return "Unhealthy"

    return "Very Unhealthy"


def calculate_health(scores):

    weights = {
        category: 2
        if category in CORE_HEALTH_CATEGORIES
        else 1
        for category in CATEGORIES
    }

    weighted_total = sum(
        scores[category] * weights[category]
        for category in CATEGORIES
    )

    minimum = sum(
        -2 * weights[category]
        for category in CATEGORIES
    )

    maximum = sum(
        2 * weights[category]
        for category in CATEGORIES
    )

    normalized = (
        (weighted_total - minimum)
        / (maximum - minimum)
    ) * 100

    return round(normalized)


def verdict(score):

    if score >= 21:
        return (
            "Yeah… that was actually really good. 🥹",
            "By your own ratings, this relationship had an unusually positive effect on your life.",
        )

    elif score >= 12:
        return (
            "Okay, this one was GOOD. 💚",
            "The relationship added significantly more than it took away.",
        )

    elif score >= 5:
        return (
            "More good than bad. 🙂",
            "There were real strengths here, even if the relationship wasn't perfect.",
        )

    elif score >= -4:
        return (
            "It's complicated. 😭",
            "The positives and negatives were pretty balanced. The category scores matter more than the total here.",
        )

    elif score >= -11:
        return (
            "The math is starting to math. 😬",
            "There were good parts, but overall the relationship appears to have cost you more than it gave you.",
        )

    elif score >= -20:
        return (
            "Yeah… this was not good for you. 🚩",
            "Several important areas of your life were negatively affected.",
        )

    return (
        "Baby, stand UP. 😭🚨",
        "By your own ratings, this relationship had a deeply negative effect across your life.",
    )


def save_relationship(name, scores):

    scores_copy = scores.copy()

    impact = sum(
        scores_copy.values()
    )

    health = calculate_health(
        scores_copy
    )

    relationship = {
        "name": name,
        "scores": scores_copy,
        "impact": impact,
        "health": health,
    }

    st.session_state.relationships.append(
        relationship
    )

    return relationship

def start_new_audit():

    st.session_state.audit_active = False

    st.session_state.audit_name = ""

    st.session_state.question_index = 0

    st.session_state.current_scores = {}

    st.session_state.show_result = False

    st.session_state.latest_result = None


def build_single_heatmap(relationship):

    values = [
        relationship["scores"][category]
        for category in CATEGORIES
    ]

    figure = go.Figure(
        data=go.Heatmap(
            z=[
                values
            ],
            x=[
                relationship["name"]
            ],
            y=CATEGORIES,
            zmin=-2,
            zmax=2,
            colorscale=[
                [0.00, "#ef9a9a"],
                [0.25, "#f8c5c5"],
                [0.50, "#f6df98"],
                [0.75, "#c7e8d0"],
                [1.00, "#8fd0a7"],
            ],
            text=[
                [
                    score_display(value)
                    for value in values
                ]
            ],
            texttemplate="%{text}",
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Score: %{z}<extra></extra>"
            ),
            showscale=False,
        )
    )

    figure.update_layout(
        height=560,
        margin=dict(
            l=20,
            r=20,
            t=10,
            b=20,
        ),
    )

    return figure


def build_comparison_heatmap(relationships):

    z_values = []

    for category in CATEGORIES:

        row = [
            relationship["scores"][category]
            for relationship in relationships
        ]

        z_values.append(row)

    text_values = [
        [
            score_display(value)
            for value in row
        ]
        for row in z_values
    ]

    figure = go.Figure(
        data=go.Heatmap(
            z=z_values,
            x=[
                relationship["name"]
                for relationship in relationships
            ],
            y=CATEGORIES,
            zmin=-2,
            zmax=2,
            colorscale=[
                [0.00, "#ef9a9a"],
                [0.25, "#f8c5c5"],
                [0.50, "#f6df98"],
                [0.75, "#c7e8d0"],
                [1.00, "#8fd0a7"],
            ],
            text=text_values,
            texttemplate="%{text}",
            hovertemplate=(
                "<b>%{x}</b><br>"
                "%{y}<br>"
                "Score: %{z}"
                "<extra></extra>"
            ),
            showscale=False,
        )
    )

    figure.update_layout(
        height=700,
        margin=dict(
            l=20,
            r=20,
            t=10,
            b=20,
        ),
    )

    return figure


def biggest_difference(relationships):

    biggest = {
        "category": None,
        "gap": -1,
        "high_name": None,
        "high_score": None,
        "low_name": None,
        "low_score": None,
    }

    for category in CATEGORIES:

        scores = [
            (
                relationship["name"],
                relationship["scores"][category],
            )
            for relationship in relationships
        ]

        highest = max(
            scores,
            key=lambda item: item[1],
        )

        lowest = min(
            scores,
            key=lambda item: item[1],
        )

        gap = highest[1] - lowest[1]

        if gap > biggest["gap"]:

            biggest = {
                "category": category,
                "gap": gap,
                "high_name": highest[0],
                "high_score": highest[1],
                "low_name": lowest[0],
                "low_score": lowest[1],
            }

    return biggest
# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div style="text-align: center; padding-top: 0.5rem;">
        <h1 style="margin-bottom: 0.3rem;">The Relationship Audit</h1>
        <h2 style="margin-top: 0;">Was It Actually Good? 💘</h2>
        <p style="font-size: 1.05rem; margin-bottom: 0.35rem;">
            Chemistry tells you how it felt. This tells you how the relationship actually affected your life.
        </p>
        <p style="opacity: 0.65; margin-top: 0;">
            Rate it honestly. See the patterns. Compare what shaped you.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

# ============================================================
# NAVIGATION
# ============================================================

analyze_tab, compare_tab, patterns_tab = st.tabs(
    [
        "💘 Audit",
        "⚖️ Compare",
        "🪞 What Does This Say About Me?",
    ]
)


# ============================================================
# AUDIT TAB
# ============================================================

with analyze_tab:

    # --------------------------------------------------------
    # START SCREEN
    # --------------------------------------------------------

    if (
        not st.session_state.audit_active
        and not st.session_state.show_result
    ):

        st.header("Let's audit the relationship.")

        st.write(
            "Think about how the relationship actually affected "
            "your life — not just how strongly you felt about them."
        )

        audit_name = st.text_input(
            "Who are we auditing?",
            placeholder="Enter a name or nickname",
        )

        st.caption(
            "You'll answer 14 questions. "
            "There are no right answers."
        )

        if st.button(
            "Start the Audit →",
            type="primary",
            use_container_width=True,
        ):

            if not audit_name.strip():

                st.warning(
                    "Enter a name or nickname first."
                )

            else:

                st.session_state.audit_name = (
                    audit_name.strip()
                )

                st.session_state.audit_active = True

                st.session_state.question_index = 0

                st.session_state.current_scores = {}

                st.rerun()


    # --------------------------------------------------------
    # QUESTION SCREEN
    # --------------------------------------------------------

    elif st.session_state.audit_active:

        index = st.session_state.question_index

        category = CATEGORIES[index]

        progress = (
            (index + 1)
            / len(CATEGORIES)
        )

        st.progress(progress)

        st.caption(
            f"QUESTION {index + 1} OF {len(CATEGORIES)}"
        )

        st.header(category)

        st.write(
            DESCRIPTIONS[category]
        )

        st.write("")

        previous_value = (
            st.session_state.current_scores.get(
                category,
                0,
            )
        )

        selected_score = st.radio(
            "Choose the answer that feels most accurate:",
            options=[
                -2,
                -1,
                0,
                1,
                2,
            ],
            index=[
                -2,
                -1,
                0,
                1,
                2,
            ].index(previous_value),
            format_func=lambda value: (
                f"{score_display(value)}  —  "
                f"{SCORE_LABELS[value]}"
            ),
            key=f"audit_question_{index}",
        )

        st.write("")

        back_col, next_col = st.columns(2)

        with back_col:

            if index > 0:

                if st.button(
                    "← Back",
                    use_container_width=True,
                ):

                    st.session_state.current_scores[
                        category
                    ] = selected_score

                    st.session_state.question_index -= 1

                    st.rerun()

        with next_col:

            if index < len(CATEGORIES) - 1:

                if st.button(
                    "Next →",
                    type="primary",
                    use_container_width=True,
                ):

                    st.session_state.current_scores[
                        category
                    ] = selected_score

                    st.session_state.question_index += 1

                    st.rerun()

            else:

                if st.button(
                    "See My Audit →",
                    type="primary",
                    use_container_width=True,
                ):

                    st.session_state.current_scores[
                        category
                    ] = selected_score

                    result = save_relationship(
                        st.session_state.audit_name,
                        st.session_state.current_scores,
                    )

                    st.session_state.latest_result = result

                    st.session_state.audit_active = False

                    st.session_state.show_result = True

                    st.rerun()


    # --------------------------------------------------------
    # RESULTS SCREEN
    # --------------------------------------------------------

    elif st.session_state.show_result:

        result = (
            st.session_state.latest_result
        )

        impact = result["impact"]

        health = result["health"]

        verdict_title, verdict_text = verdict(
            impact
        )

        st.caption("THE VERDICT")

        st.header(verdict_title)

        st.write(verdict_text)

        st.write("")

        impact_col, health_col = st.columns(2)

        with impact_col:

            st.metric(
                "Relationship Impact",
                score_display(impact),
                help=(
                    "How much the relationship added to "
                    "or took away from your life overall. "
                    "Possible range: -28 to +28."
                ),
            )

            st.caption(
                impact_label(impact)
            )

        with health_col:

            st.metric(
                "Relationship Health",
                f"{health}%",
                help=(
                    "A weighted score that gives additional "
                    "importance to core relationship fundamentals."
                ),
            )

            st.caption(
                health_label(health)
            )

        st.info(
            "💡 **Impact vs. Health:** Impact asks whether the "
            "relationship made your life better or worse overall. "
            "Health looks more closely at the fundamentals — "
            "things like safety, trust, communication, peace, "
            "consistency, and conflict resolution."
        )


        # ----------------------------------------------------
        # STRONGEST / WEAKEST
        # ----------------------------------------------------

        scores = result["scores"]

        highest_score = max(
            scores.values()
        )

        lowest_score = min(
            scores.values()
        )

        strongest = [
            category
            for category, value in scores.items()
            if value == highest_score
        ]

        weakest = [
            category
            for category, value in scores.items()
            if value == lowest_score
        ]

        left, right = st.columns(2)

        with left:

            st.subheader("💚 Strongest Areas")

            for category in strongest[:4]:

                st.success(
                    f"{category}: "
                    f"{score_display(scores[category])} "
                    f"({SCORE_LABELS[scores[category]]})"
                )

        with right:

            st.subheader("🚩 Weakest Areas")

            for category in weakest[:4]:

                if scores[category] < 0:

                    st.error(
                        f"{category}: "
                        f"{score_display(scores[category])} "
                        f"({SCORE_LABELS[scores[category]]})"
                    )

                else:

                    st.warning(
                        f"{category}: "
                        f"{score_display(scores[category])} "
                        f"({SCORE_LABELS[scores[category]]})"
                    )


        # ----------------------------------------------------
        # CORE FLAGS
        # ----------------------------------------------------

        serious_flags = [
            category
            for category in CORE_HEALTH_CATEGORIES
            if scores[category] == -2
        ]

        if serious_flags:

            st.warning(
                "🚨 **Don't let the total score hide this:** "
                "You rated these core relationship fundamentals "
                "as strongly negative: "
                + ", ".join(serious_flags)
                + "."
            )


        # ----------------------------------------------------
        # SCORECARD
        # ----------------------------------------------------

        st.subheader(
            f"{result['name']}'s Scorecard"
        )

        st.plotly_chart(
            build_single_heatmap(
                result
            ),
            use_container_width=True,
        )

        st.write("")


        # ----------------------------------------------------
        # ACTIONS
        # ----------------------------------------------------

        another_col, compare_col = st.columns(2)

        with another_col:

            if st.button(
                "💘 Audit Another Relationship",
                use_container_width=True,
            ):

                start_new_audit()

                st.rerun()

        with compare_col:

            if len(
                st.session_state.relationships
            ) >= 2:

                st.success(
                    "⚖️ Comparison unlocked! "
                    "Open the **Compare** tab above."
                )

            else:

                st.info(
                    "Audit one more relationship "
                    "to unlock comparison."
                )


# ============================================================
# COMPARE TAB
# ============================================================

with compare_tab:

    st.header("Compare Relationships")

    st.write(
        "Chemistry can make two relationships feel equally intense. "
        "Putting the actual impact side by side tells a different story."
    )

    if len(
        st.session_state.relationships
    ) < 2:

        st.info(
            "Audit at least two relationships "
            "to unlock comparison."
        )

    else:

        relationships = (
            st.session_state.relationships
        )

        st.plotly_chart(
            build_comparison_heatmap(
                relationships
            ),
            use_container_width=True,
        )

        ranking = sorted(
            relationships,
            key=lambda relationship: (
                relationship["impact"]
            ),
            reverse=True,
        )

        st.subheader(
            "Relationship Ranking"
        )

        ranking_data = []

        for position, relationship in enumerate(
            ranking,
            start=1,
        ):

            ranking_data.append(
                {
                    "Rank": position,
                    "Person": relationship["name"],
                    "Impact":
                        score_display(
                            relationship["impact"]
                        ),
                    "Health":
                        f'{relationship["health"]}%',
                }
            )

        st.dataframe(
            pd.DataFrame(ranking_data),
            hide_index=True,
            use_container_width=True,
        )

        winner = ranking[0]

        st.success(
            f"🏆 **{winner['name']}** currently has the "
            f"strongest overall impact at "
            f"**{score_display(winner['impact'])}** "
            f"with a **{winner['health']}%** health score."
        )

        difference = biggest_difference(
            relationships
        )

        st.subheader(
            "Where They Differ Most"
        )

        st.info(
            f"**{difference['category']}** has the largest "
            f"gap at **{difference['gap']} points**. "
            f"{difference['high_name']} scored "
            f"**{score_display(difference['high_score'])}**, "
            f"while {difference['low_name']} scored "
            f"**{score_display(difference['low_score'])}**."
        )


        # ----------------------------------------------------
        # CATEGORY WINNERS
        # ----------------------------------------------------

        st.subheader(
            "Category Breakdown"
        )

        category_rows = []

        for category in CATEGORIES:

            category_scores = {
                relationship["name"]:
                    relationship["scores"][category]
                for relationship in relationships
            }

            best_score = max(
                category_scores.values()
            )

            winners = [
                name
                for name, value
                in category_scores.items()
                if value == best_score
            ]

            category_rows.append(
                {
                    "Category": category,
                    "Highest Score":
                        score_display(best_score),
                    "Highest Rated":
                        ", ".join(winners),
                }
            )

        st.dataframe(
            pd.DataFrame(category_rows),
            hide_index=True,
            use_container_width=True,
        )
        # ============================================================
# PATTERNS TAB
# ============================================================

with patterns_tab:

    st.header(
        "🪞 What Does This Say About Me?"
    )

    st.write(
        "One relationship tells you about that relationship. "
        "Several relationships can start revealing patterns "
        "in what you repeatedly experience, value, tolerate, "
        "or struggle with."
    )

    if len(
        st.session_state.relationships
    ) < 2:

        st.info(
            "Audit at least two relationships "
            "before looking for recurring patterns."
        )

    else:

        averages = {}

        for category in CATEGORIES:

            values = [
                relationship["scores"][category]
                for relationship
                in st.session_state.relationships
            ]

            averages[category] = (
                sum(values)
                / len(values)
            )

        sorted_patterns = sorted(
            averages.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        strongest_patterns = (
            sorted_patterns[:3]
        )

        weakest_patterns = (
            sorted_patterns[-3:]
        )

        left, right = st.columns(2)

        with left:

            st.subheader(
                "💚 What Tends to Go Well"
            )

            for category, average in strongest_patterns:

                st.success(
                    f"{category}: "
                    f"average {average:+.1f}"
                )

        with right:

            st.subheader(
                "👀 Recurring Trouble Spots"
            )

            for category, average in weakest_patterns:

                if average < 0:

                    st.error(
                        f"{category}: "
                        f"average {average:+.1f}"
                    )

                else:

                    st.warning(
                        f"{category}: "
                        f"average {average:+.1f}"
                    )

        st.subheader(
            "Patterns Worth Thinking About"
        )

        positive_patterns = [
            category
            for category, average
            in averages.items()
            if average >= 1
        ]

        negative_patterns = [
            category
            for category, average
            in averages.items()
            if average <= -1
        ]

        if positive_patterns:

            st.success(
                "Across your relationships, these areas "
                "tend to be strengths: "
                + ", ".join(positive_patterns)
                + "."
            )

        if negative_patterns:

            st.error(
                "Across your relationships, these areas "
                "repeatedly struggle: "
                + ", ".join(negative_patterns)
                + "."
            )

        if not negative_patterns:

            st.info(
                "None of the categories currently average "
                "strongly negative across your relationships."
            )

        st.caption(
            "Patterns are reflection prompts — not diagnoses "
            "or proof that any single trait defines your relationships."
        )


# ============================================================
# SAVED RELATIONSHIPS
# ============================================================

if st.session_state.relationships:

    st.divider()

    with st.expander(
        f"🗂️ Relationships Audited "
        f"({len(st.session_state.relationships)})"
    ):

        for index, relationship in enumerate(
            st.session_state.relationships
        ):

            name_col, impact_col, health_col, remove_col = (
                st.columns(
                    [3, 1, 1, 1]
                )
            )

            with name_col:

                st.write(
                    f"**{relationship['name']}**"
                )

            with impact_col:

                st.write(
                    score_display(
                        relationship["impact"]
                    )
                )

            with health_col:

                st.write(
                    f"{relationship['health']}%"
                )

            with remove_col:

                if st.button(
                    "Remove",
                    key=f"remove_{index}",
                ):

                    st.session_state.relationships.pop(
                        index
                    )

        

                    if (
                        st.session_state.latest_result
                        and
                        st.session_state.latest_result["name"]
                        == relationship["name"]
                    ):

                        start_new_audit()

                    st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "The Relationship Audit is a self-reflection tool. "
    "It is not a clinical, diagnostic, or scientifically validated "
    "relationship assessment."
)