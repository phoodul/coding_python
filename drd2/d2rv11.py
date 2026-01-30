import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================
# 0. UI 설정 (Navy & Lemon Theme)
# ==========================================
st.set_page_config(page_title="Neuro-Sim V11.0: Real-World Dynamics", layout="wide")

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
    def __init__(self, name, ki, pk_factor, intrinsic_activity, type_, color):
        self.name = name
        self.ki = ki
        self.pk_factor = pk_factor 
        self.intrinsic_activity = intrinsic_activity 
        self.type = type_
        self.color = color

DRUG_DB = {
    # Partial Agonist (Cyan 계열)
    "Aripiprazole (Oral)":   Drug("Aripiprazole",   0.5,  4.0, 0.25, "Partial Agonist", "#00BCD4"),
    "Abilify Maintena":      Drug("Abilify Maintena", 0.5, 0.18, 0.25, "Partial Agonist", "#26C6DA"),
    "Abilify Asimtufii":     Drug("Abilify Asimtufii", 0.5, 0.10, 0.25, "Partial Agonist", "#80DEEA"),
    
    # Antagonists (Red/Blue/Green/Purple/Orange)
    "Risperidone (Oral)":    Drug("Risperidone",    3.0,  2.5, 0.0, "Antagonist", "#D32F2F"), 
    "Olanzapine (Oral)":     Drug("Olanzapine",     20.0, 1.2, 0.0, "Antagonist", "#388E3C"), 
    "Quetiapine (Oral)":     Drug("Quetiapine",     300.0,0.6, 0.0, "Antagonist", "#7B1FA2"), 
    "Haloperidol (Oral)":    Drug("Haloperidol",    1.5,  3.0, 0.0, "Antagonist", "#5D4037"), 
    "Paliperidone (Oral)":   Drug("Paliperidone",   3.5,  2.3, 0.0, "Antagonist", "#E64A19"), 
    "Invega Sustenna":       Drug("Invega Sustenna", 3.5, 0.09, 0.0, "Antagonist", "#F57C00"),
    "Invega Trinza":         Drug("Invega Trinza",   3.5, 0.03, 0.0, "Antagonist", "#FB8C00"),
    "Invega Hafyera":        Drug("Invega Hafyera",  3.5, 0.015, 0.0, "Antagonist", "#FF9800"),
}

DOPAMINE_KI = 100.0
DOPAMINE_COLOR = "#FBC02D" # Gold
FREE_COLOR = "#E0E0E0" # Grey

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
    colors = []
    
    for d_name, dose in drug_doses.items():
        drug = DRUG_DB[d_name]
        conc = get_base_concentration(drug, dose, weight, gender) * sensitivity
        terms.append(conc / drug.ki)
        labels.append(d_name)
        intrinsics.append(drug.intrinsic_activity)
        is_antagonist.append(drug.type == "Antagonist")
        colors.append(drug.color)
        
    terms.append(dopamine_conc / DOPAMINE_KI)
    labels.append("Dopamine")
    intrinsics.append(1.0)
    is_antagonist.append(False)
    colors.append(DOPAMINE_COLOR)
    
    denominator = 1 + sum(terms)
    occupancies = [t / denominator for t in terms]
    
    phys_occ = []
    for l, o, c in zip(labels, occupancies, colors):
        phys_occ.append({'label': l, 'value': o*100, 'color': c})
    
    free_occ = (1/denominator)*100
    phys_occ.append({'label': 'Free', 'value': free_occ, 'color': FREE_COLOR})
    
    antagonist_sum = 0
    for occ, is_ant in zip(occupancies, is_antagonist):
        if is_ant: antagonist_sum += (occ * 100)
        
    bio_breakdown = []
    total_bio = 0
    
    for l, occ, act, c in zip(labels, occupancies, intrinsics, colors):
        if act > 0:
            signal = occ * act * epsilon * 100
            bio_breakdown.append({'label': l, 'value': signal, 'color': c})
            total_bio += signal
            
    return phys_occ, bio_breakdown, total_bio, antagonist_sum

def plot_dual_graph(ax_top, ax_bottom, phys_occ, bio_breakdown, total_bio, title, antagonist_sum):
    # Top: Physical
    left = 0
    for item in phys_occ:
        val = item['value']
        ax_top.barh(0, val, left=left, color=item['color'], height=0.6, label=item['label'], edgecolor='white')
        if val > 10: 
            text_col = 'black' if item['label'] in ['Dopamine', 'Free'] else 'white'
            ax_top.text(left + val/2, 0, f"{val:.0f}%", ha='center', va='center', color=text_col, fontweight='bold', fontsize=9)
        left += val
            
    ax_top.axvline(x=80, color='red', linestyle='--', linewidth=1.5)
    ax_top.set_xlim(0, 100)
    ax_top.set_yticks([])
    ax_top.set_title(title, fontsize=11, fontweight='bold', color='#000080', pad=10)
    
    ant_color = 'red' if antagonist_sum > 80 else 'black'
    ax_top.text(102, 0, f"Antagonist\n{antagonist_sum:.0f}%", fontsize=8, color=ant_color, va='center')

    # Bottom: Biological (Stacked)
    ax_bottom.barh(0, 100, color='#f0f0f0', height=0.6)
    ax_bottom.axvline(x=30, color='orange', linestyle='-', linewidth=2) 
    
    bio_left = 0
    for item in bio_breakdown:
        val = item['value']
        ax_bottom.barh(0, val, left=bio_left, color=item['color'], height=0.6, edgecolor='white')
        bio_left += val
    
    text_x = bio_left + 2 if bio_left < 90 else bio_left - 10
    text_col = 'black' if bio_left < 90 else 'white'
    ax_bottom.text(text_x, 0, f"{total_bio:.1f}%", va='center', fontweight='bold', fontsize=10, color=text_col)
    
    ax_bottom.set_xlim(0, 100)
    ax_bottom.set_yticks([])
    ax_bottom.set_xlabel("Biological Output (%)", fontsize=9)
    
    if total_bio > 30:
        ax_bottom.text(32, 0.4, "Psychosis!", color='orange', fontsize=8, fontweight='bold')

# ==========================================
# 3. Streamlit Main
# ==========================================

st.title("🧠 Neuro-Sim V11.0: Real-World Dynamics")

# --- Step 1: Calibration ---
with st.expander("🛠️ Step 1. 환자 민감도 설정", expanded=False):
    c1, c2 = st.columns([1, 2])
    with c1:
        p_weight = st.number_input("체중 (kg)", 30.0, 150.0, 70.0, step=1.0, format="%.1f")
        p_gender = st.radio("성별", ["남성", "여성"], horizontal=True)
    with c2:
        if 'history' not in st.session_state: st.session_state.history = [{'drug': 'Risperidone (Oral)', 'dose': 4.0}]
        for i, item in enumerate(st.session_state.history):
            cc1, cc2, cc3 = st.columns([3, 2, 1])
            with cc1: item['drug'] = st.selectbox(f"약물 {i+1}", list(DRUG_DB.keys()), index=0, key=f"h_d_{i}")
            with cc2: item['dose'] = st.number_input("용량(mg)", 0.0, 2000.0, float(item['dose']), step=0.5, format="%.1f", key=f"h_v_{i}")
            with cc3: 
                if st.button("X", key=f"del_{i}"): st.session_state.history.pop(i); st.rerun()
        if st.button("+ 추가"): st.session_state.history.append({'drug': 'Olanzapine (Oral)', 'dose': 5.0}); st.rerun()
    sensitivity = calculate_sensitivity(st.session_state.history, p_weight, p_gender)
    st.info(f"📐 Sensitivity: **{sensitivity:.2f}**")

# --- Step 2: Desensitized State ---
st.header("Step 2. 만성 조현병 ($\epsilon=50\%$)")

st.markdown('<div class="control-box">', unsafe_allow_html=True)
current_drugs = st.multiselect("처방 약물 선택", list(DRUG_DB.keys()), default=["Risperidone (Oral)", "Aripiprazole (Oral)"])
current_doses = {}
cols = st.columns(len(current_drugs)) if current_drugs else [st]

for idx, d in enumerate(current_drugs):
    with cols[idx]:
        max_v = 1000.0 if "Maintena" in d or "Sustenna" in d or "Hafyera" in d else 30.0
        step_v = 1.0 if max_v > 100 else 0.5
        current_doses[d] = st.slider(f"{d} (mg)", 0.0, max_v, 2.0 if max_v<100 else 1.0, step=step_v, format="%.1f")

st.markdown('</div>', unsafe_allow_html=True)

has_aripiprazole = any("Aripiprazole" in d or "Abilify" in d for d in current_drugs if current_doses[d] > 0)

if current_drugs:
    legend_cols = st.columns(len(current_drugs) + 2)
    for idx, d_name in enumerate(current_drugs):
        color = DRUG_DB[d_name].color
        legend_cols[idx].markdown(f"<span style='color:{color}'>■</span> {d_name}", unsafe_allow_html=True)
    legend_cols[-2].markdown(f"<span style='color:{DOPAMINE_COLOR}'>■</span> Dopamine", unsafe_allow_html=True)
    legend_cols[-1].markdown(f"<span style='color:{FREE_COLOR}'>■</span> Free", unsafe_allow_html=True)

fig_height = 3.0
c_day, c_night = st.columns(2)
with c_day:
    phys_d, bio_bd_d, bio_d, ant_d = calculate_simulation(current_doses, sensitivity, p_weight, p_gender, 40.0, 0.5)
    fig_d, (ax1, ax2) = plt.subplots(2, 1, figsize=(6, fig_height))
    plot_dual_graph(ax1, ax2, phys_d, bio_bd_d, bio_d, "☀️ Tonic Day (40nM)", ant_d)
    plt.subplots_adjust(hspace=0.5)
    st.pyplot(fig_d)
with c_night:
    phys_n, bio_bd_n, bio_n, ant_n = calculate_simulation(current_doses, sensitivity, p_weight, p_gender, 20.0, 0.5)
    fig_n, (ax3, ax4) = plt.subplots(2, 1, figsize=(6, fig_height))
    plot_dual_graph(ax3, ax4, phys_n, bio_bd_n, bio_n, "🌙 Tonic Night (20nM)", ant_n)
    plt.subplots_adjust(hspace=0.5)
    st.pyplot(fig_n)

st.markdown('<div class="phasic-box">', unsafe_allow_html=True)
phasic_conc = st.slider("💥 Phasic Dopamine Level (nM)", 100.0, 1000.0, 150.0, step=10.0)
phys_p, bio_bd_p, bio_p, ant_p = calculate_simulation(current_doses, sensitivity, p_weight, p_gender, phasic_conc, 0.5)
fig_p, (ax_p1, ax_p2) = plt.subplots(2, 1, figsize=(8, fig_height))
plot_dual_graph(ax_p1, ax_p2, phys_p, bio_bd_p, bio_p, f"💥 Phasic ({phasic_conc}nM)", ant_p)
plt.subplots_adjust(hspace=0.5)
st.pyplot(fig_p)
st.markdown('</div>', unsafe_allow_html=True)

# --- Step 3: Supersensitivity State ---
st.divider()
st.header("Step 3. 도파민 초민감성 (Supersensitivity)")

# [NEW] Aripiprazole Logic: 110% / 120%
if has_aripiprazole:
    eff_a = 1.1 # 110%
    eff_b = 1.2 # 120%
    st.info("🧪 **Aripiprazole Effect:** 아리피프라졸 사용으로 초민감성이 완화되었으나, 완전 정상화(100%)가 아닌 **110% ~ 120%** 수준으로 시뮬레이션합니다. (Breakthrough 가능성 반영)")
else:
    eff_a = 1.5
    eff_b = 2.0
    st.warning("⚠️ **High Risk:** 아리피프라졸 미사용 상태. 수용체 효율이 **150% ~ 200%**로 매우 높습니다.")

col_a_tonic, col_a_phasic = st.columns([2, 1])
# Type A
st.subheader(f"Type A (효율 {eff_a*100:.0f}%)")
with col_a_tonic:
    c1, c2 = st.columns(2)
    p_150_d, bb_150_d, b_150_d, a_150_d = calculate_simulation(current_doses, sensitivity, p_weight, p_gender, 40.0, eff_a)
    fig1, (ax1, ax2) = plt.subplots(2, 1, figsize=(5, fig_height))
    plot_dual_graph(ax1, ax2, p_150_d, bb_150_d, b_150_d, "☀️ Tonic Day", a_150_d)
    plt.subplots_adjust(hspace=0.5)
    c1.pyplot(fig1)
    
    p_150_n, bb_150_n, b_150_n, a_150_n = calculate_simulation(current_doses, sensitivity, p_weight, p_gender, 20.0, eff_a)
    fig2, (ax3, ax4) = plt.subplots(2, 1, figsize=(5, fig_height))
    plot_dual_graph(ax3, ax4, p_150_n, bb_150_n, b_150_n, "🌙 Tonic Night", a_150_n)
    plt.subplots_adjust(hspace=0.5)
    c2.pyplot(fig2)

with col_a_phasic:
    p_150_p, bb_150_p, b_150_p, a_150_p = calculate_simulation(current_doses, sensitivity, p_weight, p_gender, phasic_conc, eff_a)
    fig3, (ax5, ax6) = plt.subplots(2, 1, figsize=(5, fig_height)) 
    plot_dual_graph(ax5, ax6, p_150_p, bb_150_p, b_150_p, f"💥 Phasic", a_150_p)
    plt.subplots_adjust(hspace=0.5)
    st.pyplot(fig3)

st.divider()

# Type i
st.subheader(f"Type i (효율 {eff_b*100:.0f}%)")
col_b_tonic, col_b_phasic = st.columns([2, 1])
with col_b_tonic:
    c3, c4 = st.columns(2)
    p_200_d, bb_200_d, b_200_d, a_200_d = calculate_simulation(current_doses, sensitivity, p_weight, p_gender, 40.0, eff_b)
    fig4, (ax7, ax8) = plt.subplots(2, 1, figsize=(5, fig_height))
    plot_dual_graph(ax7, ax8, p_200_d, bb_200_d, b_200_d, "☀️ Tonic Day", a_200_d)
    plt.subplots_adjust(hspace=0.5)
    c3.pyplot(fig4)
    
    p_200_n, bb_200_n, b_200_n, a_200_n = calculate_simulation(current_doses, sensitivity, p_weight, p_gender, 20.0, eff_b)
    fig5, (ax9, ax10) = plt.subplots(2, 1, figsize=(5, fig_height))
    plot_dual_graph(ax9, ax10, p_200_n, bb_200_n, b_200_n, "🌙 Tonic Night", a_200_n)
    plt.subplots_adjust(hspace=0.5)
    c4.pyplot(fig5)

with col_b_phasic:
    p_200_p, bb_200_p, b_200_p, a_200_p = calculate_simulation(current_doses, sensitivity, p_weight, p_gender, phasic_conc, eff_b)
    fig6, (ax11, ax12) = plt.subplots(2, 1, figsize=(5, fig_height))
    plot_dual_graph(ax11, ax12, p_200_p, bb_200_p, b_200_p, f"💥 Phasic", a_200_p)
    plt.subplots_adjust(hspace=0.5)
    st.pyplot(fig6)

# --- Legend ---
st.divider()
st.markdown("""
<div class="legend-box">
    <h4>✅ V11.0 임상적 수정</h4>
    <ul>
        <li><b>현실적인 아리피프라졸 작용:</b> 이제 아리피프라졸 병용 시 효율이 무조건 100%가 아니라 <b>110%(Type A), 120%(Type i)</b>로 설정됩니다.</li>
        <li><b>돌파성 증상 구현:</b> 이로 인해 스트레스(Phasic) 상황에서는 내인성 작용 총합이 <b>30%를 초과</b>하여 정신병 증상이 재발할 수 있음을 보여줍니다.</li>
    </ul>
</div>
""", unsafe_allow_html=True)