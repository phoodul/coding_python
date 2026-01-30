import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================
# 0. UI 설정 (Navy & Lemon Theme)
# ==========================================
st.set_page_config(page_title="Neuro-Sim V7.2: Window Collapse", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; color: #000080; }
    h1, h2, h3, h4, h5 { color: #000080 !important; font-family: 'Segoe UI', bold; }
    .control-box {
        background-color: #FFFACD; padding: 20px; border-radius: 15px;
        border: 2px solid #F0E68C; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px;
    }
    .phasic-box {
        background-color: #ffebee; padding: 15px; border-radius: 10px; border: 1px solid #ef9a9a; margin-top: 10px;
    }
    .legend-box {
        background-color: #e8f4f8; border-left: 5px solid #000080; padding: 15px; margin-top: 20px;
    }
    .stSlider label { color: #000080 !important; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. 약물 데이터베이스
# ==========================================

class Drug:
    def __init__(self, name, ki, pk_factor, intrinsic_activity, type_, category="Oral"):
        self.name = name
        self.ki = ki
        self.pk_factor = pk_factor 
        self.intrinsic_activity = intrinsic_activity 
        self.type = type_
        self.category = category 

DRUG_DB = {
    # Partial Agonist (Intrinsic Activity = 0.25)
    "Aripiprazole (Oral)":   Drug("Aripiprazole",   0.5,  4.0, 0.25, "Partial Agonist"),
    "Abilify Maintena":      Drug("Abilify Maintena", 0.5, 0.18, 0.25, "Partial Agonist", "LAI"),
    "Abilify Asimtufii":     Drug("Abilify Asimtufii", 0.5, 0.10, 0.25, "Partial Agonist", "LAI"),
    
    # Antagonists (Intrinsic Activity = 0.0)
    "Risperidone (Oral)":    Drug("Risperidone",    3.0,  2.5, 0.0, "Antagonist"),
    "Olanzapine (Oral)":     Drug("Olanzapine",     20.0, 1.2, 0.0, "Antagonist"),
    "Quetiapine (Oral)":     Drug("Quetiapine",     300.0,0.6, 0.0, "Antagonist"),
    "Haloperidol (Oral)":    Drug("Haloperidol",    1.5,  3.0, 0.0, "Antagonist"),
    "Paliperidone (Oral)":   Drug("Paliperidone",   3.5,  2.3, 0.0, "Antagonist"),
    "Invega Sustenna":       Drug("Invega Sustenna", 3.5, 0.09, 0.0, "Antagonist", "LAI"),
    "Invega Trinza":         Drug("Invega Trinza",   3.5, 0.03, 0.0, "Antagonist", "LAI"),
    "Invega Hafyera":        Drug("Invega Hafyera",  3.5, 0.015, 0.0, "Antagonist", "LAI"),
}

DOPAMINE_KI = 100.0

# ==========================================
# 2. 계산 로직
# ==========================================

def get_base_concentration(drug, dose, weight, gender):
    weight_adj = 70.0 / weight
    gender_adj = 1.15 if gender == '여성' else 1.0
    return dose * drug.pk_factor * weight_adj * gender_adj

def calculate_sensitivity(history_list, weight, gender):
    total_term_sum = 0.0
    for item in history_list:
        drug = DRUG_DB[item['drug']]
        base_conc = get_base_concentration(drug, item['dose'], weight, gender)
        total_term_sum += (base_conc / drug.ki)
    if total_term_sum == 0: return 1.0
    return 4.0 / total_term_sum

def calculate_simulation(drug_doses, sensitivity, weight, gender, dopamine_conc, epsilon):
    terms = []
    labels = []
    intrinsics = []
    is_antagonist = []
    
    # Drugs
    for d_name, dose in drug_doses.items():
        drug = DRUG_DB[d_name]
        conc = get_base_concentration(drug, dose, weight, gender) * sensitivity
        terms.append(conc / drug.ki)
        labels.append(d_name)
        intrinsics.append(drug.intrinsic_activity)
        is_antagonist.append(drug.type == "Antagonist")
        
    # Dopamine
    terms.append(dopamine_conc / DOPAMINE_KI)
    labels.append("Dopamine")
    intrinsics.append(1.0)
    is_antagonist.append(False)
    
    # Physics Calculation
    denominator = 1 + sum(terms)
    occupancies = [t / denominator for t in terms] # fraction
    
    phys_occ = dict(zip(labels, [o*100 for o in occupancies]))
    phys_occ['Free'] = (1/denominator)*100
    
    # Antagonist Sum Calculation (EPS Line Check)
    antagonist_sum = 0
    for occ, is_ant in zip(occupancies, is_antagonist):
        if is_ant: antagonist_sum += (occ * 100)
        
    # Biology Calculation
    raw_signal = 0
    for occ, act in zip(occupancies, intrinsics):
        raw_signal += occ * act
        
    bio_output = raw_signal * epsilon * 100
    
    return phys_occ, bio_output, antagonist_sum

def plot_dual_graph(ax_top, ax_bottom, phys_occ, bio_output, title, antagonist_sum):
    # --- Top: Physical Occupancy ---
    left = 0
    colors = ['#D32F2F', '#1976D2', '#388E3C', '#7B1FA2', '#E64A19'] # Red, Blue, Green, Purple
    c_idx = 0
    
    for label, val in phys_occ.items():
        if label in ['Dopamine', 'Free']: continue
        c = '#00BCD4' if "Aripiprazole" in label or "Abilify" in label else colors[c_idx % 5]
        if "Aripiprazole" not in label and "Abilify" not in label: c_idx += 1
        
        ax_top.barh(0, val, left=left, color=c, height=0.6, label=label)
        # 텍스트 라벨 (공간이 너무 작으면 생략)
        if val > 8: 
            ax_top.text(left + val/2, 0, f"{val:.0f}", ha='center', va='center', color='white', fontweight='bold', fontsize=8)
        left += val
        
    dop_val = phys_occ.get('Dopamine', 0)
    ax_top.barh(0, dop_val, left=left, color='#FBC02D', height=0.6) # Gold
    if dop_val > 5: ax_top.text(left + dop_val/2, 0, "DA", ha='center', va='center', fontsize=8)
    left += dop_val
    
    free_val = phys_occ.get('Free', 0)
    ax_top.barh(0, free_val, left=left, color='#E0E0E0', height=0.6)
    
    # EPS Threshold Line (80%)
    ax_top.axvline(x=80, color='red', linestyle='--', linewidth=1.5)
    
    ax_top.set_xlim(0, 100)
    ax_top.set_yticks([])
    ax_top.set_title(title, fontsize=10, fontweight='bold', color='#000080')
    
    if antagonist_sum > 80:
        ax_top.text(98, 0.45, "EPS!", color='red', fontsize=8, fontweight='bold', ha='right')
    else:
        ax_top.text(98, 0.45, f"Ant: {antagonist_sum:.0f}%", fontsize=7, ha='right')

    # --- Bottom: Biological Output ---
    ax_bottom.barh(0, 100, color='#f0f0f0', height=0.5)
    ax_bottom.axvline(x=30, color='orange', linestyle='-', linewidth=2) 
    
    bar_color = 'green' if bio_output < 30 else 'red'
    ax_bottom.barh(0, bio_output, color=bar_color, height=0.5)
    ax_bottom.text(bio_output + 1, 0, f"{bio_output:.1f}%", va='center', fontweight='bold', fontsize=9)
    
    ax_bottom.set_xlim(0, 100)
    ax_bottom.set_yticks([])
    ax_bottom.set_xlabel("Bio Output (%)", fontsize=8)

# ==========================================
# 3. Streamlit Main
# ==========================================

st.title("🧠 Neuro-Sim V7.2: Therapeutic Window Collapse")

# --- Step 1: Calibration (유지) ---
with st.expander("🛠️ Step 1. 환자 민감도 설정 (EPS 과거력)", expanded=False):
    c1, c2 = st.columns([1, 2])
    with c1:
        p_weight = st.number_input("체중 (kg)", 30.0, 150.0, 70.0)
        p_gender = st.radio("성별", ["남성", "여성"], horizontal=True)
    with c2:
        if 'history' not in st.session_state:
            st.session_state.history = [{'drug': 'Risperidone (Oral)', 'dose': 4.0}]
        for i, item in enumerate(st.session_state.history):
            cc1, cc2, cc3 = st.columns([3, 2, 1])
            with cc1: item['drug'] = st.selectbox(f"약물 {i+1}", list(DRUG_DB.keys()), index=0, key=f"h_d_{i}")
            with cc2: item['dose'] = st.number_input("용량(mg)", 0.0, 2000.0, float(item['dose']), key=f"h_v_{i}")
            with cc3: 
                if st.button("X", key=f"del_{i}"): st.session_state.history.pop(i); st.rerun()
        if st.button("+ 추가"): st.session_state.history.append({'drug': 'Olanzapine (Oral)', 'dose': 5.0}); st.rerun()
    sensitivity = calculate_sensitivity(st.session_state.history, p_weight, p_gender)
    st.info(f"📐 Sensitivity: **{sensitivity:.2f}**")

# --- Step 2: Desensitized State (Epsilon 50%) ---
st.header("Step 2. 만성 조현병 (Desensitization: $\epsilon=50\%$)")

st.markdown("도파민 150nM에서 Output 30%를 맞추기 위해 **수용체 효율 50%**로 설정.")

# 약물 입력
st.markdown('<div class="control-box">', unsafe_allow_html=True)
current_drugs = st.multiselect("처방 약물 선택", list(DRUG_DB.keys()), default=["Risperidone (Oral)"])
current_doses = {}
cols = st.columns(len(current_drugs)) if current_drugs else [st]
for idx, d in enumerate(current_drugs):
    with cols[idx]:
        max_v = 1000.0 if "Maintena" in d or "Sustenna" in d or "Hafyera" in d else 30.0
        current_doses[d] = st.slider(f"{d} (mg)", 0.0, max_v, 4.0 if max_v<100 else 150.0)
st.markdown('</div>', unsafe_allow_html=True)

# Tonic Graph
c_day, c_night = st.columns(2)
with c_day:
    phys_d, bio_d, ant_d = calculate_simulation(current_doses, sensitivity, p_weight, p_gender, 40.0, 0.5)
    fig_d, (ax1, ax2) = plt.subplots(2, 1, figsize=(6, 2.0), gridspec_kw={'height_ratios': [1, 1]})
    plot_dual_graph(ax1, ax2, phys_d, bio_d, "☀️ Tonic Day (40nM)", ant_d)
    st.pyplot(fig_d)
with c_night:
    phys_n, bio_n, ant_n = calculate_simulation(current_doses, sensitivity, p_weight, p_gender, 20.0, 0.5)
    fig_n, (ax3, ax4) = plt.subplots(2, 1, figsize=(6, 2.0), gridspec_kw={'height_ratios': [1, 1]})
    plot_dual_graph(ax3, ax4, phys_n, bio_n, "🌙 Tonic Night (20nM)", ant_n)
    st.pyplot(fig_n)

# Phasic Graph
st.markdown('<div class="phasic-box">', unsafe_allow_html=True)
phasic_conc = st.slider("💥 Phasic Dopamine Level (nM)", 100.0, 1000.0, 150.0, help="Step 3에도 이 농도가 적용됩니다.")
phys_p, bio_p, ant_p = calculate_simulation(current_doses, sensitivity, p_weight, p_gender, phasic_conc, 0.5)
fig_p, (ax_p1, ax_p2) = plt.subplots(2, 1, figsize=(8, 2.5), gridspec_kw={'height_ratios': [1, 1]})
plot_dual_graph(ax_p1, ax_p2, phys_p, bio_p, f"💥 Phasic Burst ({phasic_conc}nM) @ Eff 50%", ant_p)
st.pyplot(fig_p)
st.markdown('</div>', unsafe_allow_html=True)

# --- Step 3: Supersensitivity State ---
st.divider()
st.header("Step 3. 도파민 초민감성 (Supersensitivity)")
st.markdown("⚠️ **Therapeutic Window Collapse:** EPS 위험(Tonic)과 정신병 위험(Phasic)이 공존하는 구간 확인.")

# Type A: 150%
st.subheader("Type A: 효율 150% (경도)")
col_a_tonic, col_a_phasic = st.columns([2, 1])

# A-Tonic (Day/Night)
with col_a_tonic:
    c1, c2 = st.columns(2)
    # Day
    p_150_d, b_150_d, a_150_d = calculate_simulation(current_doses, sensitivity, p_weight, p_gender, 40.0, 1.5)
    fig1, (ax1, ax2) = plt.subplots(2, 1, figsize=(5, 2.0), gridspec_kw={'height_ratios': [1, 1]})
    plot_dual_graph(ax1, ax2, p_150_d, b_150_d, "☀️ Tonic Day (40nM)", a_150_d)
    c1.pyplot(fig1)
    # Night
    p_150_n, b_150_n, a_150_n = calculate_simulation(current_doses, sensitivity, p_weight, p_gender, 20.0, 1.5)
    fig2, (ax3, ax4) = plt.subplots(2, 1, figsize=(5, 2.0), gridspec_kw={'height_ratios': [1, 1]})
    plot_dual_graph(ax3, ax4, p_150_n, b_150_n, "🌙 Tonic Night (20nM)", a_150_n)
    c2.pyplot(fig2)

# A-Phasic
with col_a_phasic:
    p_150_p, b_150_p, a_150_p = calculate_simulation(current_doses, sensitivity, p_weight, p_gender, phasic_conc, 1.5)
    fig3, (ax5, ax6) = plt.subplots(2, 1, figsize=(5, 2.5), gridspec_kw={'height_ratios': [1, 1]}) # 조금 더 크게
    plot_dual_graph(ax5, ax6, p_150_p, b_150_p, f"💥 Phasic ({phasic_conc}nM)", a_150_p)
    st.pyplot(fig3)
    if b_150_p > 30: st.error(f"Output: {b_150_p:.1f}% (Psychosis)")

st.divider()

# Type i: 200%
st.subheader("Type i: 효율 200% (중증)")
col_b_tonic, col_b_phasic = st.columns([2, 1])

# i-Tonic (Day/Night)
with col_b_tonic:
    c3, c4 = st.columns(2)
    # Day
    p_200_d, b_200_d, a_200_d = calculate_simulation(current_doses, sensitivity, p_weight, p_gender, 40.0, 2.0)
    fig4, (ax7, ax8) = plt.subplots(2, 1, figsize=(5, 2.0), gridspec_kw={'height_ratios': [1, 1]})
    plot_dual_graph(ax7, ax8, p_200_d, b_200_d, "☀️ Tonic Day (40nM)", a_200_d)
    c3.pyplot(fig4)
    # Night
    p_200_n, b_200_n, a_200_n = calculate_simulation(current_doses, sensitivity, p_weight, p_gender, 20.0, 2.0)
    fig5, (ax9, ax10) = plt.subplots(2, 1, figsize=(5, 2.0), gridspec_kw={'height_ratios': [1, 1]})
    plot_dual_graph(ax9, ax10, p_200_n, b_200_n, "🌙 Tonic Night (20nM)", a_200_n)
    c4.pyplot(fig5)

# i-Phasic
with col_b_phasic:
    p_200_p, b_200_p, a_200_p = calculate_simulation(current_doses, sensitivity, p_weight, p_gender, phasic_conc, 2.0)
    fig6, (ax11, ax12) = plt.subplots(2, 1, figsize=(5, 2.5), gridspec_kw={'height_ratios': [1, 1]})
    plot_dual_graph(ax11, ax12, p_200_p, b_200_p, f"💥 Phasic ({phasic_conc}nM)", a_200_p)
    st.pyplot(fig6)
    if b_200_p > 30: st.error(f"Output: {b_200_p:.1f}% (Psychosis)")

# --- Legend ---
st.divider()
st.markdown("""
<div class="legend-box">
    <h4>📝 결과 해석 가이드 (Window Collapse)</h4>
    <p><b>Step 3의 Type i(효율 200%)를 주목하십시오.</b></p>
    <ul>
        <li><b>Tonic 그래프(좌측)의 상단:</b> 약물 용량이 충분하다면 <b><span style="color:red">붉은 점선(EPS 80%)</span></b>을 넘어 EPS 위험이 보일 것입니다.</li>
        <li><b>Phasic 그래프(우측)의 하단:</b> 그럼에도 불구하고, <b><span style="color:orange">주황색 실선(Psychosis 30%)</span></b>을 뚫고 나가는 붉은 바(Output)를 볼 수 있습니다.</li>
    </ul>
    <p>👉 이는 <b>"EPS가 올 정도로 약을 많이 썼는데도, 스트레스 상황에서는 정신병 증상이 재발하는"</b> 초민감성 정신증(Supersensitivity Psychosis)의 전형적인 패턴입니다.</p>
</div>
""", unsafe_allow_html=True)