import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="BIO-SIM",
    page_icon="🧬",
    layout="wide"
)

# 디자인 설정
st.markdown("""
<style>
.stApp {
    background-color: #101827;
    color: #E8EEF7;
}
[data-testid="stSidebar"] {
    background-color: #192538;
}
div[data-testid="stMetric"] {
    background: #192538;
    border: 1px solid #34465F;
    border-radius: 14px;
    padding: 15px;
}
div[data-testid="stMetricValue"] {
    color: #35C9A5;
}
</style>
""", unsafe_allow_html=True)

MODEL_NAMES = ["대조군", "가상 생물 A", "가상 생물 B"]
MODEL_COLORS = ["#9AAAC0", "#55A6FF", "#35C9A5"]

FACTOR_NAMES = [
    "생애 단계", "온도", "습도", "조직 손상", "산소 농도"
]

FACTOR_COLORS = [
    "#9AAAC0", "#F2B45B", "#55A6FF", "#F07878", "#35C9A5"
]


# ----------------------------------
# 생존 적합도 계산
# ----------------------------------

def calculate(values, model):

    stress = {
        "생애 단계": values["나이"],
        "온도": min(abs(values["온도"] - 25) / 35 * 100, 100),
        "습도": min(abs(values["습도"] - 60) / 60 * 100, 100),
        "조직 손상": values["조직 손상"],
        "산소 농도": min(abs(values["산소 농도"] - 21) / 21 * 100, 100)
    }

    weights = [
        {
            "생애 단계": .20, "온도": .18, "습도": .12,
            "조직 손상": .30, "산소 농도": .20
        },
        {
            "생애 단계": .15, "온도": .18, "습도": .12,
            "조직 손상": .14, "산소 농도": .20
        },
        {
            "생애 단계": .19, "온도": .12, "습도": .06,
            "조직 손상": .28, "산소 농도": .17
        }
    ][model]

    penalties = {
        name: stress[name] * weights[name]
        for name in FACTOR_NAMES
    }

    score = max(0, min(100, 100 - sum(penalties.values())))

    return {
        "score": score,
        "penalties": penalties
    }


# ----------------------------------
# 자동 분석
# ----------------------------------

def make_analysis(results):

    scores = [r["score"] for r in results]

    best = int(np.argmax(scores))
    worst = int(np.argmin(scores))

    lines = [
        f"가장 높은 생존 적합도 지수를 보인 모델은 "
        f"{MODEL_NAMES[best]}입니다. ({scores[best]:.1f}점)",
        f"가장 낮은 모델은 {MODEL_NAMES[worst]}이며, "
        f"두 모델의 차이는 {scores[best] - scores[worst]:.1f}점입니다.",
        "",
        "모델별 주요 영향 요인:"
    ]

    for i, result in enumerate(results):

        factor = max(
            result["penalties"],
            key=result["penalties"].get
        )

        lines.append(
            f"• {MODEL_NAMES[i]}: {factor} 조건의 불리한 영향이 "
            f"가장 크게 계산되었습니다."
        )

    return "\n".join(lines)


# ----------------------------------
# 그래프
# ----------------------------------

def make_charts(results):

    fig, (ax1, ax2) = plt.subplots(
        1, 2,
        figsize=(12, 4.5),
        gridspec_kw={"width_ratios": [1, 1.35]}
    )

    fig.patch.set_facecolor("#192538")

    scores = [r["score"] for r in results]

    # 생존 적합도 비교
    ax1.set_facecolor("#192538")

    bars = ax1.bar(
        MODEL_NAMES,
        scores,
        color=MODEL_COLORS,
        width=0.56
    )

    ax1.set_title(
        "Survival Suitability",
        color="#E8EEF7"
    )

    ax1.set_ylim(0, 110)
    ax1.tick_params(colors="#E8EEF7")
    ax1.grid(axis="y", alpha=0.25)

    for bar, score in zip(bars, scores):
        ax1.text(
            bar.get_x() + bar.get_width() / 2,
            score + 2,
            f"{score:.1f}",
            ha="center",
            color="#E8EEF7"
        )

    # 환경 요인별 영향
    ax2.set_facecolor("#192538")

    bottom = np.zeros(3)

    for i, factor in enumerate(FACTOR_NAMES):

        vals = [
            r["penalties"][factor]
            for r in results
        ]

        ax2.bar(
            MODEL_NAMES,
            vals,
            bottom=bottom,
            label=factor,
            color=FACTOR_COLORS[i],
            width=0.56
        )

        bottom += np.array(vals)

    ax2.set_title(
        "Environmental Factor Contributions",
        color="#E8EEF7"
    )

    ax2.set_ylabel(
        "Reduction contribution",
        color="#9AAAC0"
    )

    ax2.tick_params(colors="#E8EEF7")
    ax2.grid(axis="y", alpha=0.25)

    legend = ax2.legend(
        fontsize=8,
        loc="upper right",
        frameon=False
    )

    for label in legend.get_texts():
        label.set_color("#E8EEF7")

    fig.tight_layout()

    return fig


# ----------------------------------
# 프로그램 화면
# ----------------------------------

st.title("🧬 BIO-SIM")

st.markdown(
    '<p style="color:#35C9A5;letter-spacing:2px;">'
    'VIRTUAL ORGANISM RESPONSE SIMULATOR</p>',
    unsafe_allow_html=True
)

st.write(
    "복합 환경 조건에 따른 가상 생물의 생존 적합도 분석"
)

st.info(
    "모든 환경 조건을 동시에 반영합니다. "
    "계산 결과는 실제 생존 확률이 아닌 가상 모델의 비교 지수입니다."
)


# ----------------------------------
# 환경 설정 슬라이더
# ----------------------------------

st.sidebar.header("ENVIRONMENT SETTINGS")
st.sidebar.caption("분석할 환경 조건을 설정하세요.")

age = st.sidebar.slider(
    "나이 / 생애 단계 지수", 0, 100, 30
)

temp = st.sidebar.slider(
    "온도 (℃)", -10, 50, 25
)

humidity = st.sidebar.slider(
    "습도 (%)", 0, 100, 60
)

damage = st.sidebar.slider(
    "조직 손상 (%)", 0, 100, 20
)

oxygen = st.sidebar.slider(
    "산소 농도 (%)", 0.0, 30.0, 21.0, 0.5
)


values = {
    "나이": age,
    "온도": temp,
    "습도": humidity,
    "조직 손상": damage,
    "산소 농도": oxygen
}


# ----------------------------------
# 현재 환경 표시
# ----------------------------------

st.subheader("현재 환경 설정")

cols = st.columns(5)

condition_values = [
    ("생애 단계", f"{age}/100"),
    ("온도", f"{temp}℃"),
    ("습도", f"{humidity}%"),
    ("조직 손상", f"{damage}%"),
    ("산소 농도", f"{oxygen:g}%")
]

for col, (name, value) in zip(cols, condition_values):
    col.metric(name, value)


# ----------------------------------
# 결과 계산
# ----------------------------------

results = [
    calculate(values, i)
    for i in range(3)
]

st.subheader("생물체별 생존 적합도")

cols = st.columns(3)

for col, name, result in zip(cols, MODEL_NAMES, results):
    col.metric(
        name,
        f"{result['score']:.1f}점"
    )


# ----------------------------------
# 그래프 출력
# ----------------------------------

st.subheader("RESPONSE ANALYSIS")

st.caption(
    "현재 설정된 복합 환경에서 계산한 세 모델의 반응"
)

fig = make_charts(results)

st.pyplot(fig, use_container_width=True)

plt.close(fig)


# ----------------------------------
# 자동 분석 출력
# ----------------------------------

st.subheader("SIMULATION INSIGHT")

st.markdown(
    make_analysis(results)
)


# ----------------------------------
# 모델 설명 및 한계
# ----------------------------------

with st.expander("가상 모델의 구성과 해석상 주의점"):

    st.write(
        "대조군은 별도의 강화 특성을 가정하지 않은 기준 모델입니다. "
        "가상 생물 A는 아홀로틀의 조직 재생 관련 특성과 "
        "벌거숭이두더지쥐의 세포 유지 관련 특성을 추상화했습니다."
    )

    st.write(
        "가상 생물 B는 곰벌레의 건조 스트레스 대응 특성과 "
        "바퀴벌레의 환경 적응 관련 특성을 추상화했습니다."
    )

    st.warning(
        "각 조건의 가중치와 계산식은 탐구를 위해 설정한 가정값입니다. "
        "실제 생물학적 측정값이나 검증된 생존 예측식이 아닙니다."
    )

st.caption("BIO-SIM · Educational Virtual Simulation")
