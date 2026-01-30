import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================
# 0. UI 스타일링 (Lemon & Navy Theme)
# ==========================================
st.set_page_config(page_title="Neuro-Sim V5: Circadian & Phasic Dynamics", layout="wide")

st.markdown("""
<style>
    /* 전체 앱 배경 및 폰트 */
    .stApp {
        background-color: #f8f9fa;
        color: #000080; /* Navy default */
    }
    
    /* 헤더 스타일 */
    h1, h2, h3 {
        color: #000080 !important; /* Navy */
        font-family: 'Segoe UI', sans-serif;
    }
    
    /* 슬라이더 컨트롤 박스 스타일링 (Pale Lemon Background) */
    .control-box {
        background-color: #FFFACD; /* Pale Lemon */
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #F0E68C; /* Darker Yellow border */
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    
    /* 슬라이더 라벨 텍스트 색상 강제 지정 */
    .stSlider label {
        color: #000080 !important; /* Navy Blue */
        font-weight: bold;
        font-size: 16px;
    }
    
    /* Metric 박스 스타일 */
    div[data-testid="stMetric"] {
        background-color: white;
        border-radius: 8px;
        padding: 10px;
        border: 1px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. 약물 데이터베이스
# ==========================================

class Drug:
    def __init__(self, name, ki, pk_factor, type_, category="Oral"):
        self.name = name
        self.ki = ki
        self.pk_factor = pk_factor 
        self.type = type_
        self.category = category 

DRUG_DB = {
    # Oral
    "Risperidone (Oral)":    Drug("Risperidone",    3.0,  2.5, "Antagonist"),
    "Olanzapine (Oral)":     Drug("Olanzapine",     20.0, 1.2, "Antagonist"),
    "Aripiprazole (Oral)":   Drug("Aripiprazole",   0.5,  4.0, "Partial Agonist"),
    "Quetiapine (Oral)":     Drug("Quetiapine",     300.0,0.6, "Antagonist"),
    "Clozapine (Oral)":      Drug("Clozapine",      180.0,0.8, "Antagonist"),
    "Haloperidol (Oral)":    Drug("Haloperidol",    1.5,  3.0, "Antagonist"),
    "Paliperidone (Oral)":   Drug("Paliperidone",   3.5,  2.3, "Antagonist"),
    "Blonanserin (Oral)":    Drug("Blonanserin",    0.8,  3.5, "Antagonist"),
    "Lurasidone (Oral)":     Drug("Lurasidone",     2.0,  1.8, "Antagonist"),
    "Ziprasidone (Oral)":    Drug("Ziprasidone",    4.0,  1.5, "Antagonist"),
    "Chlorpromazine (Oral)": Drug("Chlorpromazine", 30.0, 0.1, "Antagonist"),
    "Fluphenazine (Oral)":   Drug("Fluphenazine",   1.2,  3.2, "Antagonist"),
    "Levomepromazine (Oral)":Drug("Levomepromazine",25.0, 0.12,"Antagonist"),
    # LAI
    "Abilify Maintena (Month)": Drug("Abilify Maintena", 0.5, 0.18, "Partial Agonist", "LAI"),
    "Abilify Asimtufii (2Mo)":  Drug("Abilify Asimtufii", 0.5, 0.10, "Partial Agonist", "LAI"),
    "Invega Sustenna (1Mo)":    Drug("Invega Sustenna", 3.5, 0.09, "Antagonist", "LAI"),
    "Invega Trinza (3Mo)":      Drug("Invega Trinza",   3.5, 0.03, "Antagonist", "LAI"),
    "Invega Hafyera (6Mo)":     Drug("Invega Hafyera",  3.5, 0.015, "Antagonist", "LAI"),
}

DOPAMINE_KI = 100.0

# ==========================================
# 2. 로직 함수
# ==========================================

def get_base_concentration(drug, dose, weight, gender):
    weight_adj = 70.0 / weight
    gender_adj = 1.15 if gender == '여성' else 1.0
    return dose * drug.pk_factor * weight_adj * gender_adj

def calculate_sensitivity_polypharmacy(history_list, weight, gender):
    total_term_sum = 0.0
    for item in history_list:
        drug = DRUG_DB[item['drug']]
        base_conc = get_base_concentration(drug, item['dose'], weight, gender)
        total_term_sum += (base_conc / drug.ki)
    if total_term_sum == 0: return 1.0
    sensitivity = 4.0 / total_term_sum
    return sensitivity

def calculate_occupancy(drug_doses, sensitivity, p_weight, p_gender, dopamine_conc):
    """
    특정 도파민 농도 하에서의 점유율을 계산하여 반환
    Returns: (labels, occupancies, total_drug_occ, partial_occ, antagonist_occ, colors)
    """
    terms = []
    labels = []
    
    # 1. Drugs
    for d_name, dose in drug_doses.items():
        drug = DRUG_DB[d_name]
        conc = get_base_concentration(drug, dose, p_weight, p_gender) * sensitivity
        terms.append(conc / drug.ki)
        labels.append(d_name)
    
    # 2. Dopamine
    terms.append(dopamine_conc / DOPAMINE_KI)
    labels.append("Dopamine")
    
    # 3. Calculate
    denominator = 1 + sum(terms)
    occupancies = [(t / denominator) * 100 for t in terms]
    
    return labels, occupancies

def plot_bar_chart(ax, labels, occupancies, title):
    """Matplotlib Bar Chart Drawing Helper"""
    BOLD_COLORS = ['#D32F2F', '#1976D2', '#388E3C', '#7B1FA2', '#E64A19', '#0097A7', '#5D4037', '#C2185B']
    plot_colors = [BOLD_COLORS[i % len(BOLD_COLORS)] for i in range(len(labels)-1)]
    plot_colors.append('#FBC02D') # Dopamine Color
    
    left_pos = 0
    # Drugs & Dopamine
    for label, occ, color in zip(labels, occupancies, plot_colors):
        if occ > 0.1:
            ax.barh(0, occ, left=left_pos, color=color, edgecolor='white', height=0.6, label=label)
            if occ > 5:
                t_col = 'black' if label == "Dopamine" else 'white'
                ax.text(left_pos + occ/2, 0, f"{occ:.1f}%", ha='center', va='center', 
                        color=t_col, fontweight='bold', fontsize=9)
            left_pos += occ
            
    # Free Receptor
    free = 100 - left_pos
    if free > 0:
        ax.barh(0, free, left=left_pos, color='#E0E0E0', edgecolor='#BDBDBD', height=0.6, label="Free")
        if free > 5:
            ax.text(left_pos + free/2, 0, f"Free\n{free:.1f}%", ha='center', va='center', color='#424242', fontsize=9)
            
    ax.set_xlim(0, 100)
    ax.set_yticks([])
    ax.set_title(title, fontsize=12, fontweight='bold', color='#000080')
    ax.axvline(x=80, color='black', linestyle='--', linewidth=1.5)

# ==========================================
# 3. Main Streamlit UI
# ==========================================

st.title("🧠 Neuro-Sim V5: Bio-Rhythm & Phasic Dynamics")
st.markdown("도파민의 **일주기 리듬(Circadian Rhythm)**과 **급성 스트레스(Phasic)** 상황을 구분하여 시뮬레이션합니다.")

# --- STEP 1: Calibration ---
with st.expander("🛠️ Step 1. 환자 캘리브레이션 (EPS 과거력)", expanded=False):
    c1, c2 = st.columns([1, 2])
    with c1:
        p_weight = st.number_input("체중 (kg)", 30.0, 150.0, 70.0)
        p_gender = st.radio("성별", ["남성", "여성"], horizontal=True)
    with c2:
        if 'history_drugs' not in st.session_state:
            st.session_state.history_drugs = [{'drug': 'Risperidone (Oral)', 'dose': 4.0}]
        
        for i, item in enumerate(st.session_state.history_drugs):
            cols = st.columns([3, 2, 1])
            with cols[0]:
                item['drug'] = st.selectbox(f"약물 {i+1}", list(DRUG_DB.keys()), index=list(DRUG_DB.keys()).index(item['drug']), key=f"h_d_{i}")
            with cols[1]:
                item['dose'] = st.number_input("용량(mg)", 0.0, 2000.0, float(item['dose']), key=f"h_v_{i}")
            with cols[2]:
                if st.button("X", key=f"del_{i}"):
                    st.session_state.history_drugs.pop(i)
                    st.rerun()
        if st.button("+ 약물 추가"):
            st.session_state.history_drugs.append({'drug': 'Olanzapine (Oral)', 'dose': 5.0})
            st.rerun()

    sensitivity = calculate_sensitivity_polypharmacy(st.session_state.history_drugs, p_weight, p_gender)
    st.info(f"📐 보정된 환자 민감도(Sensitivity): **{sensitivity:.2f}**")

# --- STEP 2: Simulation Controls ---
st.divider()
st.header("Step 2. 처방 및 도파민 상태 설정")

col_left, col_right = st.columns([1, 2])

# [Left Panel] 약물 입력창 (Pale Lemon Box)
with col_left:
    st.markdown('<div class="control-box">', unsafe_allow_html=True)
    st.markdown("### 💊 약물 처방 입력")
    
    current_drugs = st.multiselect("처방 약물 선택", list(DRUG_DB.keys()), 
                                   default=["Risperidone (Oral)", "Abilify Maintena (Month)"])
    
    current_doses = {}
    for d_name in current_drugs:
        is_lai = DRUG_DB[d_name].category == "LAI"
        max_val = 2000.0 if is_lai or "Quetiapine" in d_name else 40.0
        step_val = 10.0 if max_val > 100 else 0.5
        
        current_doses[d_name] = st.slider(f"{d_name} (mg)", 0.0, max_val, 0.0, step_val)
    st.markdown('</div>', unsafe_allow_html=True)

# [Right Panel] 도파민 상태 및 그래프
with col_right:
    # 도파민 모드 선택
    st.markdown("### 🧠 환자의 도파민 상태 (Dopamine State)")
    mode = st.radio("상태 모드 선택", ["🟢 정상/안정기 (Tonic - Circadian Rhythm)", "🔴 급성/스트레스기 (Phasic - Stress Storm)"], horizontal=True)
    
    if "정상" in mode:
        # Circadian Rhythm Settings
        st.markdown("일주기 리듬에 따라 아침(최고치)과 밤(최저치)의 점유율 변화를 비교합니다.")
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            dop_morning = st.slider("☀️ 아침 (Active Peak) nM", 20.0, 80.0, 40.0)
        with col_d2:
            dop_night = st.slider("🌙 취침 전 (Resting Trough) nM", 5.0, 20.0, 10.0)
            
        # Plotting (Side by Side)
        if current_drugs:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 3.5))
            
            # Morning Chart
            lab1, occ1 = calculate_occupancy(current_doses, sensitivity, p_weight, p_gender, dop_morning)
            plot_bar_chart(ax1, lab1, occ1, f"☀️ Morning (Dopamine {dop_morning}nM)")
            
            # Night Chart
            lab2, occ2 = calculate_occupancy(current_doses, sensitivity, p_weight, p_gender, dop_night)
            plot_bar_chart(ax2, lab2, occ2, f"🌙 Bedtime (Dopamine {dop_night}nM)")
            
            # Legend (Shared)
            handles, labels = ax1.get_legend_handles_labels()
            fig.legend(handles, labels, loc='lower center', bbox_to_anchor=(0.5, -0.15), ncol=4, frameon=False)
            
            st.pyplot(fig)
            
            # Insight Message
            drug_occ_m = sum(occ1[:-1])
            drug_occ_n = sum(occ2[:-1])
            diff = drug_occ_n - drug_occ_m
            st.info(f"💡 **임상 노트:** 밤에는 도파민 농도가 떨어져 약물의 상대적 점유율이 **{diff:.1f}% 상승**합니다. "
                    f"이 시간대에 EPS나 정좌불능(Akathisia) 호소가 늘어날 수 있습니다.")

    else:
        # Phasic Stress Mode
        st.error("⚠️ **Warning:** 급성 스트레스 상황에서는 도파민이 폭발적으로 분비됩니다 (Phasic Burst).")
        dop_phasic = st.slider("💥 Phasic Dopamine Level (nM)", 100.0, 1000.0, 200.0, 50.0)
        
        if current_drugs:
            fig, ax = plt.subplots(figsize=(10, 3))
            lab, occ = calculate_occupancy(current_doses, sensitivity, p_weight, p_gender, dop_phasic)
            plot_bar_chart(ax, lab, occ, f"💥 Acute Stress (Dopamine {dop_phasic}nM)")
            
            handles, labels = ax.get_legend_handles_labels()
            ax.legend(handles, labels, bbox_to_anchor=(0., 1.15, 1., .102), loc='lower left', ncol=4, mode="expand", frameon=False)
            
            st.pyplot(fig)
            
            drug_occ = sum(occ[:-1])
            if drug_occ < 60:
                st.warning(f"⚠️ 도파민이 너무 강력하여 약물 점유율이 {drug_occ:.1f}%로 떨어졌습니다. 증상 조절을 위해 용량 증량이 필요할 수 있습니다.")

# --- Bottom: Detail Table ---
if current_drugs:
    with st.expander("📊 상세 약동학 수치 보기"):
        # Create consolidated table
        data_rows = []
        for d_name in current_drugs:
            drug = DRUG_DB[d_name]
            base_c = get_base_concentration(drug, current_doses[d_name], p_weight, p_gender) * sensitivity
            data_rows.append([d_name, f"{current_doses[d_name]} mg", f"{base_c:.2f} nM", f"{drug.ki} nM"])
        
        df = pd.DataFrame(data_rows, columns=["약물", "용량", "보정 농도(nM)", "Ki(친화력)"])
        st.table(df)