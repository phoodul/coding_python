import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================
# 0. UI 테마 설정 (Professional Navy & Lemon)
# ==========================================
st.set_page_config(page_title="Neuro-Sim V6: Biological Output Model", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; color: #000080; }
    h1, h2, h3 { color: #000080 !important; font-family: 'Segoe UI', bold; }
    .control-box {
        background-color: #FFFACD; padding: 20px; border-radius: 15px;
        border: 2px solid #F0E68C; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .metric-box {
        background-color: white; border: 1px solid #ddd; border-radius: 8px; padding: 15px;
        text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. 약물 및 시나리오 데이터베이스
# ==========================================

class Drug:
    def __init__(self, name, ki, pk_factor, intrinsic_activity, type_, category="Oral"):
        self.name = name
        self.ki = ki
        self.pk_factor = pk_factor 
        self.intrinsic_activity = intrinsic_activity # 내인성 활성 (0.0 ~ 1.0)
        self.type = type_
        self.category = category 

DRUG_DB = {
    # Partial Agonist (Intrinsic Activity ~ 0.25)
    "Aripiprazole (Oral)":   Drug("Aripiprazole",   0.5,  4.0, 0.25, "Partial Agonist"),
    "Abilify Maintena":      Drug("Abilify Maintena", 0.5, 0.18, 0.25, "Partial Agonist", "LAI"),
    
    # Antagonists (Intrinsic Activity = 0.0)
    "Risperidone (Oral)":    Drug("Risperidone",    3.0,  2.5, 0.0, "Antagonist"),
    "Olanzapine (Oral)":     Drug("Olanzapine",     20.0, 1.2, 0.0, "Antagonist"),
    "Quetiapine (Oral)":     Drug("Quetiapine",     300.0,0.6, 0.0, "Antagonist"),
    "Haloperidol (Oral)":    Drug("Haloperidol",    1.5,  3.0, 0.0, "Antagonist"),
    "Paliperidone (Oral)":   Drug("Paliperidone",   3.5,  2.3, 0.0, "Antagonist"),
    "Invega Sustenna":       Drug("Invega Sustenna", 3.5, 0.09, 0.0, "Antagonist", "LAI"),
    "Invega Trinza":         Drug("Invega Trinza",   3.5, 0.03, 0.0, "Antagonist", "LAI"),
}

DOPAMINE_KI = 100.0

# ==========================================
# 2. 핵심 계산 로직 (물리적 점유율 -> 생물학적 출력)
# ==========================================

def get_base_concentration(drug, dose, weight, gender):
    weight_adj = 70.0 / weight
    gender_adj = 1.15 if gender == '여성' else 1.0
    return dose * drug.pk_factor * weight_adj * gender_adj

def calculate_physics_and_biology(drug_doses, sensitivity, p_weight, p_gender, dopamine_conc, efficiency_epsilon):
    """
    Returns: 
    1. physics_data: {label: occupancy_percent}
    2. bio_output_percent: 최종 생물학적 신호 강도 (%)
    """
    terms = []
    labels = []
    intrinsic_activities = [] # 각 성분의 고유 활성도
    
    # 1. Drugs
    for d_name, dose in drug_doses.items():
        drug = DRUG_DB[d_name]
        conc = get_base_concentration(drug, dose, p_weight, p_gender) * sensitivity
        term = conc / drug.ki
        
        terms.append(term)
        labels.append(d_name)
        intrinsic_activities.append(drug.intrinsic_activity)
    
    # 2. Dopamine
    dop_term = dopamine_conc / DOPAMINE_KI
    terms.append(dop_term)
    labels.append("Dopamine")
    intrinsic_activities.append(1.0) # 도파민은 100% 활성
    
    # 3. Physics (Occupancy)
    denominator = 1 + sum(terms)
    occupancies = [t / denominator for t in terms] # 0.0 ~ 1.0 fraction
    
    physics_data = dict(zip(labels, [occ * 100 for occ in occupancies]))
    physics_data["Free"] = (1 / denominator) * 100
    
    # 4. Biology (Signal Output)
    # Signal = Efficiency * Sum(Occupancy * Intrinsic_Activity)
    # *참고: 도파민의 Autoreceptor 억제 효과는 '정상인' 시나리오에서 efficiency_epsilon 값으로 조절됨
    
    raw_signal_sum = 0
    for occ, act in zip(occupancies, intrinsic_activities):
        raw_signal_sum += occ * act
        
    final_bio_output = raw_signal_sum * efficiency_epsilon * 100
    
    return physics_data, final_bio_output

# ==========================================
# 3. Streamlit UI
# ==========================================

st.title("🧠 Neuro-Sim V6: Integrated Dopamine Model")
st.markdown("""
**물리적 점유율(Occupancy)**과 **생물학적 출력(Biological Output)**을 분리하여 시뮬레이션합니다.
선생님의 **'Low-Base, High-Ceiling'** 이론에 기반합니다.
""")

# --- [Step 1] 환자 병리 시나리오 선택 ---
st.header("Step 1. 환자 병리 상태 (Pathology Scenario)")

c_mode, c_info = st.columns([1, 2])

with c_mode:
    scenario = st.radio("환자 상태 선택", 
                        ["🟢 정상인 (Normal)", 
                         "🟡 조현병: 만성/음성 (Chronic/Desensitized)", 
                         "🔴 도파민 초민감성 (Supersensitivity/TD)"])

# 시나리오별 파라미터 설정 (선생님의 이론 적용)
if "정상인" in scenario:
    epsilon = 0.3  # 50% 점유 -> 15% 출력이 되도록 보정 (Autoreceptor effect)
    base_dopamine = 20.0
    st_msg = "정상 상태입니다. 자가 수용체 기전으로 출력이 억제(Low-Base)됩니다."
elif "조현병" in scenario:
    epsilon = 0.37 # 이론값 37%
    base_dopamine = 40.0 # 기저 농도 높음
    st_msg = "만성 조현병 상태입니다. 수용체가 탈감작(Down-regulation)되어 효율이 37%로 떨어져 있습니다."
else:
    epsilon = 2.0  # 이론값 200%
    base_dopamine = 20.0
    st_msg = "초민감성 상태입니다. 수용체 효율이 200%로 폭증하여 작은 자극에도 과도한 출력이 발생합니다."

with c_info:
    st.info(f"💡 **설정값:** {st_msg} (수용체 효율 $\epsilon$ = {epsilon*100:.0f}%)")


# --- [Step 2] 처방 및 상황 입력 ---
st.divider()
st.header("Step 2. 처방 및 도파민 자극 설정")

col_left, col_right = st.columns([1, 1.2])

with col_left:
    st.markdown('<div class="control-box">', unsafe_allow_html=True)
    st.markdown("### 💊 약물 처방")
    
    current_drugs = st.multiselect("약물 선택", list(DRUG_DB.keys()), default=["Risperidone (Oral)"])
    current_doses = {}
    
    for d in current_drugs:
        max_v = 1000.0 if "Maintena" in d or "Sustenna" in d else 20.0
        step_v = 10.0 if max_v > 100 else 0.5
        current_doses[d] = st.slider(f"{d} (mg)", 0.0, max_v, 2.0 if max_v<100 else 150.0, step_v)
        
    st.markdown("---")
    st.markdown("### ⚡ 도파민 자극 수준")
    dopamine_conc = st.slider("현재 도파민 농도 (nM)", 10.0, 300.0, base_dopamine, 
                              help="20:기저, 40:만성높음, 150:Phasic폭발, 250:돌파성홍수")
    st.markdown('</div>', unsafe_allow_html=True)

# --- [Step 3] 시뮬레이션 및 시각화 ---
with col_right:
    # 계산 수행 (감수성 Sensitivity는 1.0으로 고정하거나 이전 단계에서 가져옴. 여기선 1.0 가정)
    phys_data, bio_output = calculate_physics_and_biology(
        current_doses, 1.0, 70.0, "남성", dopamine_conc, epsilon
    )
    
    # 1. 생물학적 출력 (Biological Output Gauge)
    st.subheader("📊 Biological Output (생물학적 출력)")
    
    # 게이지 바 생성 (Matplotlib)
    fig_bio, ax_bio = plt.subplots(figsize=(10, 1.5))
    
    # 배경 (임계값 표시)
    ax_bio.barh(0, 100, color='#f0f0f0', height=0.5) # 전체 배경
    
    # 임계 구간 표시
    ax_bio.axvline(x=15, color='green', linestyle=':', alpha=0.5) # 0-point
    ax_bio.text(15, 0.35, "Zero-Point(15%)", color='green', fontsize=8, ha='center')
    
    ax_bio.axvline(x=30, color='orange', linestyle='--', alpha=0.5) # Threshold
    ax_bio.text(30, -0.35, "Psychosis Threshold(30%)", color='orange', fontsize=8, ha='center')
    
    ax_bio.axvline(x=80, color='red', linestyle='--', alpha=0.5) # Max
    ax_bio.text(80, 0.35, "Max Reward(80%)", color='red', fontsize=8, ha='center')

    # 실제 출력 값 그리기
    bar_color = 'green' if bio_output < 30 else ('orange' if bio_output < 60 else 'red')
    ax_bio.barh(0, bio_output, color=bar_color, height=0.5, edgecolor='black')
    
    # 값 표시
    ax_bio.text(bio_output + 1, 0, f"{bio_output:.1f}%", va='center', fontweight='bold', fontsize=12)
    
    ax_bio.set_xlim(0, 100)
    ax_bio.set_yticks([])
    ax_bio.set_title("Net Signal Intensity (뇌가 느끼는 실제 신호)", fontsize=10, color='#000080')
    
    st.pyplot(fig_bio)
    
    # 2. 결과 해석 메시지
    if bio_output < 15:
        st.warning("⚠️ **Low State:** 출력이 0점(15%) 미만입니다. 무의욕, 우울, 또는 정좌불능(Akathisia) 위험.")
    elif 15 <= bio_output < 30:
        st.success("✅ **Stable:** 출력이 평온한 각성 범위(15~30%)에 있습니다. (치료 목표)")
    elif 30 <= bio_output < 60:
        st.warning("⚠️ **Warning:** 정신병적 임계값(30%)을 초과했습니다. 불안, 초조, 경미한 양성 증상.")
    else:
        st.error("🚨 **Critical:** 출력이 매우 높습니다(>60%). 급성 정신증, 환청, 망상 또는 심각한 TD.")

    # 3. 물리적 점유율 (Stacked Bar) - V5 스타일
    st.subheader("🧪 Physical Receptor Occupancy (물리적 점유율)")
    
    fig_phys, ax_phys = plt.subplots(figsize=(10, 1.5))
    
    left = 0
    # 색상 매핑
    colors = {'Dopamine': '#FBC02D', 'Free': '#E0E0E0'} 
    drug_colors = ['#D32F2F', '#1976D2', '#388E3C', '#7B1FA2'] # Red, Blue, Green, Purple
    
    # 약물 그리기
    idx = 0
    for label, val in phys_data.items():
        if label == "Free" or label == "Dopamine": continue
        c = drug_colors[idx % len(drug_colors)]
        ax_phys.barh(0, val, left=left, color=c, height=0.6, label=label)
        if val > 5: ax_phys.text(left + val/2, 0, f"{val:.1f}%", ha='center', va='center', color='white', fontweight='bold')
        left += val
        idx += 1
        
    # 도파민 그리기
    dop_val = phys_data.get("Dopamine", 0)
    if dop_val > 0:
        ax_phys.barh(0, dop_val, left=left, color=colors['Dopamine'], height=0.6, label='Dopamine')
        if dop_val > 5: ax_phys.text(left + dop_val/2, 0, f"{dop_val:.1f}%", ha='center', va='center', fontweight='bold')
        left += dop_val
        
    # Free 그리기
    free_val = phys_data.get("Free", 0)
    if free_val > 0:
        ax_phys.barh(0, free_val, left=left, color=colors['Free'], height=0.6, label='Free')
        
    ax_phys.set_xlim(0, 100)
    ax_phys.set_yticks([])
    ax_phys.legend(bbox_to_anchor=(0., 1.15, 1., .102), loc='lower left', ncol=4, mode="expand", frameon=False)
    
    st.pyplot(fig_phys)

# --- [Step 4] 데이터 테이블 ---
st.divider()
with st.expander("📝 상세 수치 분석표"):
    # 물리적 점유율 데이터
    df_phys = pd.DataFrame(list(phys_data.items()), columns=["Ligand", "Occupancy (%)"])
    st.dataframe(df_phys.T)
    
    st.markdown(f"""
    **수식 검증:**
    - **Total Signal** = $\epsilon$ ({epsilon}) × [ (Dopamine_Occ × 1.0) + (Drug_Occ × Intrinsic_Act) ]
    - **Current Result:** {bio_output:.2f}%
    """)