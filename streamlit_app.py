
import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# =====================================================
# BIO-SIM | VIRTUAL ORGANISM LAB
# =====================================================

st.set_page_config(
    page_title="BIO-SIM | Virtual Organism Lab",
    page_icon="🧬",
    layout="wide"
)

# ---------- 색상 ----------
BG = "#0B1220"
PANEL = "#151F30"
PANEL2 = "#1C2A3E"
TEXT = "#EAF1FA"
MUTED = "#91A2B8"
BLUE = "#55A6FF"
GREEN = "#35C9A5"
GRAY = "#A0ACBC"
ORANGE = "#F2B45B"
RED = "#F07878"

MODEL_NAMES = ["대조군", "가상 생물 A", "가상 생물 B"]
MODEL_COLORS = [GRAY, BLUE, GREEN]

FACTOR_NAMES = [
    "생애 단계", "온도", "습도", "조직 손상", "산소 농도"
]

FACTOR_COLORS = [GRAY, ORANGE, BLUE, RED, GREEN]


# =====================================================
# 1. 계산 모델
# =====================================================

def calculate(values, model):

    stress = {
        "생애 단계": values["나이"],

        "온도": min(
            abs(values["온도"] - 25) / 35 * 100,
            100
        ),

        "습도": min(
            abs(values["습도"] - 60) / 60 * 100,
            100
        ),

        "조직 손상": values["조직 손상"],

        "산소 농도": min(
            abs(values["산소 농도"] - 21) / 21 * 100,
            100
        )
    }

    weights = [
        {
            "생애 단계": .20,
            "온도": .18,
            "습도": .12,
            "조직 손상": .30,
            "산소 농도": .20
        },
        {
            "생애 단계": .15,
            "온도": .18,
            "습도": .12,
            "조직 손상": .14,
            "산소 농도": .20
        },
        {
            "생애 단계": .19,
            "온도": .12,
            "습도": .06,
            "조직 손상": .28,
            "산소 농도": .17
        }
    ][model]

    penalties = {
        name: stress[name] * weights[name]
        for name in FACTOR_NAMES
    }

    score = max(
        0,
        min(100, 100 - sum(penalties.values()))
    )

    return {
        "score": score,
        "penalties": penalties
    }


def calculate_all(values):

    return [
        calculate(values, i)
        for i in range(3)
    ]


# =====================================================
# 2. 자동 분석
# =====================================================

def make_analysis(results):

    scores = [r["score"] for r in results]

    best = int(np.argmax(scores))
    worst = int(np.argmin(scores))

    lines = []

    lines.append(
        f"가장 높은 생존 적합도 지수를 보인 모델은 "
        f"{MODEL_NAMES[best]}입니다. "
        f"({scores[best]:.1f}점)"
    )

    lines.append(
        f"가장 낮은 모델은 {MODEL_NAMES[worst]}이며, "
        f"두 모델의 점수 차이는 "
        f"{scores[best] - scores[worst]:.1f}점입니다."
    )

    lines.append("")
    lines.append("모델별 주요 영향 요인")

    for i, result in enumerate(results):

        factor = max(
            result["penalties"],
            key=result["penalties"].get
        )

        lines.append(
            f"• {MODEL_NAMES[i]}: "
            f"{factor} 조건의 불리한 영향이 "
            f"가장 크게 계산되었습니다."
        )

    return lines


# =====================================================
# 3. Plotly 그래프
# =====================================================

def create_charts(results):

    scores = [
        result["score"]
        for result in results
    ]

    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=(
            "생존 적합도 비교",
            "환경 요인별 영향 구성"
        ),
        horizontal_spacing=0.15
    )

    # 그래프 1: 생존 적합도
    fig.add_trace(
        go.Bar(
            x=MODEL_NAMES,
            y=scores,
            marker_color=MODEL_COLORS,
            text=[f"{s:.1f}" for s in scores],
            textposition="outside",
            textfont=dict(color=TEXT, size=13),
            name="생존 적합도",
            showlegend=False
        ),
        row=1,
        col=1
    )

    # 그래프 2: 환경 요인별 영향
    for i, factor in enumerate(FACTOR_NAMES):

        values = [
            result["penalties"][factor]
            for result in results
        ]

        fig.add_trace(
            go.Bar(
                x=MODEL_NAMES,
                y=values,
                name=factor,
                marker_color=FACTOR_COLORS[i]
            ),
            row=1,
            col=2
        )

    fig.update_layout(
        height=390,
        paper_bgcolor=PANEL,
        plot_bgcolor=PANEL,
        font=dict(
            color=TEXT,
            family="Arial, sans-serif",
            size=11
        ),
        margin=dict(l=25, r=25, t=65, b=35),
        barmode="stack",
        legend=dict(
            orientation="h",
            y=-0.22,
            x=0.5,
            xanchor="center",
            font=dict(color=MUTED)
        ),
        hoverlabel=dict(
            bgcolor=PANEL2,
            font_color=TEXT
        )
    )

    fig.update_yaxes(
        gridcolor="#29384D",
        zerolinecolor="#29384D",
        tickfont=dict(color=MUTED),
        row=1,
        col=1,
        range=[0, 110]
    )

    fig.update_yaxes(
        gridcolor="#29384D",
        zerolinecolor="#29384D",
        tickfont=dict(color=MUTED),
        row=1,
        col=2
    )

    fig.update_xaxes(
        tickfont=dict(color=TEXT),
        showgrid=False
    )

    return fig


# =====================================================
# 4. 디자인 CSS
# =====================================================

st.markdown("""
<style>

.stApp {
    background: #0B1220;
    color: #EAF1FA;
}

[data-testid="stSidebar"] {
    background: #151F30;
    border-right: 1px solid #26364B;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] label {
    color: #EAF1FA !important;
}

.block-container {
    max-width: 1500px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

h1, h2, h3, p {
    color: #EAF1FA;
}

.metric-card {
    background: linear-gradient(
        145deg,
        #1C2A3E,
        #151F30
    );
    border: 1px solid #30425A;
    border-radius: 15px;
    padding: 18px;
    min-height: 125px;
}

.metric-label {
    color: #91A2B8;
    font-size: 13px;
    margin-bottom: 8px;
}

.metric-number {
    font-size: 32px;
    font-weight: 700;
    margin-bottom: 5px;
}

.metric-caption {
    color: #91A2B8;
    font-size: 11px;
}

.section-label {
    color: #35C9A5;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2px;
    margin-bottom: 5px;
}

.panel {
    background: #151F30;
    border: 1px solid #293B52;
    border-radius: 15px;
    padding: 20px;
    margin-bottom: 15px;
}

.analysis-box {
    background: #151F30;
    border-left: 4px solid #35C9A5;
    border-radius: 10px;
    padding: 20px;
    line-height: 1.9;
}

div[data-testid="stMetric"] {
    background: #1C2A3E;
    border: 1px solid #30425A;
    border-radius: 13px;
    padding: 15px;
}

div[data-testid="stMetricValue"] {
    color: #35C9A5;
}

.stButton button {
    border-radius: 9px;
    border: 1px solid #35C9A5;
    background: #1C2A3E;
    color: #35C9A5;
}

hr {
    border-color: #293B52;
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# 5. 상단 헤더
# =====================================================

header_left, header_right = st.columns([3, 1])

with header_left:

    st.markdown(
        """
        <div class="section-label">
        VIRTUAL ORGANISM LAB
        </div>
        <h1 style="font-size:39px; margin-bottom:0;">
        🧬 BIO-SIM
        </h1>
        <p style="color:#91A2B8;">
        복합 환경 조건에 따른 가상 생물의 생존 적합도 분석
        </p>
        """,
        unsafe_allow_html=True
    )

with header_right:

    st.markdown(
        """
        <div style="
        text-align:right;
        padding-top:20px;
        color:#35C9A5;
        font-size:12px;
        letter-spacing:2px;">
        ● SIMULATION ACTIVE
        </div>
        """,
        unsafe_allow_html=True
    )

st.divider()


# =====================================================
# 6. 환경 설정 슬라이더
# =====================================================

st.sidebar.markdown(
    """
    <div style="
    color:#35C9A5;
    font-size:11px;
    font-weight:bold;
    letter-spacing:2px;">
    ENVIRONMENT CONTROL
    </div>
    <h2 style="margin-top:5px;">
    환경 조건 설정
    </h2>
    <p style="color:#91A2B8;font-size:12px;">
    분석할 환경 변수를 조절하세요.
    </p>
    """,
    unsafe_allow_html=True
)

st.sidebar.divider()

age = st.sidebar.slider(
    "생애 단계 지수",
    0, 100, 30, 1
)

temp = st.sidebar.slider(
    "온도 (℃)",
    -10, 50, 25, 1
)

humidity = st.sidebar.slider(
    "습도 (%)",
    0, 100, 60, 1
)

damage = st.sidebar.slider(
    "조직 손상 (%)",
    0, 100, 20, 1
)

oxygen = st.sidebar.slider(
    "산소 농도 (%)",
    0.0, 30.0, 21.0, 0.5
)

st.sidebar.divider()

st.sidebar.caption(
    "※ 생애 단계 지수는 실제 연령이 아닌 "
    "가상 모델의 입력값입니다."
)

if st.sidebar.button(
    "기본 조건으로 초기화",
    use_container_width=True
):

    for key in [
        "생애 단계 지수",
        "온도 (℃)",
        "습도 (%)",
        "조직 손상 (%)",
        "산소 농도 (%)"
    ]:
        if key in st.session_state:
            del st.session_state[key]

    st.rerun()


values = {
    "나이": age,
    "온도": temp,
    "습도": humidity,
    "조직 손상": damage,
    "산소 농도": oxygen
}


# =====================================================
# 7. 결과 계산
# =====================================================

results = calculate_all(values)

scores = [
    result["score"]
    for result in results
]


# =====================================================
# 8. 환경 조건 요약
# =====================================================

st.markdown(
    '<div class="section-label">CURRENT ENVIRONMENT</div>',
    unsafe_allow_html=True
)

condition_cols = st.columns(5)

conditions = [
    ("생애 단계", f"{age}"),
    ("온도", f"{temp}℃"),
    ("습도", f"{humidity}%"),
    ("조직 손상", f"{damage}%"),
    ("산소 농도", f"{oxygen:g}%")
]

for col, (name, value) in zip(condition_cols, conditions):

    with col:
        st.metric(name, value)


st.write("")


# =====================================================
# 9. 생존 적합도 카드
# =====================================================

st.markdown(
    '<div class="section-label">SURVIVAL SUITABILITY</div>',
    unsafe_allow_html=True
)

st.subheader("생물체별 생존 적합도")

metric_cols = st.columns(3)

for i, col in enumerate(metric_cols):

    with col:

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">
                MODEL 0{i+1} · {MODEL_NAMES[i]}
                </div>
                <div class="metric-number"
                style="color:{MODEL_COLORS[i]};">
                {scores[i]:.1f}
                </div>
                <div class="metric-caption">
                SURVIVAL SUITABILITY INDEX
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


st.write("")


# =====================================================
# 10. 그래프
# =====================================================

st.markdown(
    '<div class="section-label">DATA VISUALIZATION</div>',
    unsafe_allow_html=True
)

st.subheader("Simulation Analysis")

st.caption(
    "현재 설정된 모든 환경 조건을 동시에 반영한 계산 결과입니다."
)

fig = create_charts(results)

st.plotly_chart(
    fig,
    use_container_width=True,
    config={"displayModeBar": False}
)


# =====================================================
# 11. 자동 분석
# =====================================================

st.markdown(
    '<div class="section-label">SIMULATION INSIGHT</div>',
    unsafe_allow_html=True
)

st.subheader("자동 분석 결과")

analysis = make_analysis(results)

for line in analysis:

    if line == "":
        st.write("")
    else:
        st.markdown(
            f"""
            <div style="
            color:#DCE7F5;
            padding:5px 0;
            font-size:14px;">
            {line}
            </div>
            """,
            unsafe_allow_html=True
        )


# =====================================================
# 12. 모델 설명
# =====================================================

with st.expander("가상 생물 모델 및 계산의 한계"):

    st.markdown("""
    **대조군**

    별도의 강화 특성을 가정하지 않은 기준 모델입니다.

    **가상 생물 A**

    아홀로틀의 조직 재생 관련 특성과
    벌거숭이두더지쥐의 세포 유지 관련 특성을
    추상화한 모델입니다.

    **가상 생물 B**

    곰벌레의 건조 스트레스 대응 특성과
    바퀴벌레의 환경 적응 관련 특성을
    추상화한 모델입니다.

    ---

    **모델의 한계**

    본 프로그램의 계산식과 가중치는 탐구를 위해 설정한 가정값입니다.
    실제 생물학적 측정값이나 검증된 생존 예측식이 아니며,
    생존 적합도 지수는 실제 생존 확률을 의미하지 않습니다.
    """)


st.divider()

st.markdown(
    """
    <div style="
    text-align:center;
    color:#71839B;
    font-size:11px;
    padding:10px;">
    BIO-SIM · VIRTUAL ORGANISM LAB · EDUCATIONAL SIMULATION
    </div>
    """,
    unsafe_allow_html=True
)
