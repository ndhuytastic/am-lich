import streamlit as st
import sxtwl
from datetime import datetime, timedelta, timezone, date

st.set_page_config(page_title="Kỳ Môn Độn Giáp - Ngọa Long", layout="wide", initial_sidebar_state="collapsed")

# ==========================================
# 1. DỮ LIỆU CƠ BẢN & HẰNG SỐ CHÂN TRUYỀN
# ==========================================
thien_can = "甲乙丙丁戊己庚辛壬癸"
dia_chi = "子丑寅卯辰巳午未申酉戌亥"
luc_nghi = ["戊", "己", "庚", "辛", "壬", "癸", "丁", "丙", "乙"]

WOLONG_OUTER_PALACES = [4, 9, 2, 7, 6, 1, 8, 3] # Tốn, Ly, Khôn, Đoài, Càn, Khảm, Cấn, Chấn
WOLONG_FLYING_PATH = [5, 6, 7, 8, 9, 1, 2, 3, 4]
WOLONG_STEM_TO_NUM = {"癸": 1, "丁": 2, "丙": 3, "乙": 4, "戊": 5, "己": 6, "庚": 7, "辛": 8, "壬": 9, "甲": 0}
WOLONG_NUM_TO_STEM = {v: k for k, v in WOLONG_STEM_TO_NUM.items()}
WOLONG_ORIGINAL_GATES = {1: "休门", 8: "生门", 3: "伤门", 4: "杜门", 9: "景门", 2: "死门", 7: "惊门", 6: "开门"}
WOLONG_CLOCKWISE_GATES = ["景门", "死门", "惊门", "开门", "休门", "生门", "伤门", "杜门"]

solar_term_ju = {
    "冬至":[1,7,4], "小寒":[2,8,5], "大寒":[3,9,6], "立春":[8,5,2], "雨水":[9,6,3], "惊蛰":[1,7,4],
    "春分":[3,9,6], "清明":[4,1,7], "谷雨":[5,2,8], "立夏":[4,1,7], "小满":[5,2,8], "芒种":[6,3,9],
    "夏至":[9,3,6], "小暑":[8,2,5], "大暑":[7,1,4], "立秋":[2,5,8], "处暑":[1,4,7], "白露":[9,3,6],
    "秋分":[7,1,4], "寒露":[6,9,3], "霜降":[5,8,2], "立冬":[6,9,3], "小雪":[5,8,2], "大雪":[4,7,1]
}
wolong_jq_order = ["大雪", "冬至", "小寒", "大寒", "立春", "雨水", "惊蛰", "春分", "清明", "谷雨", "立夏", "小满", "芒种", "夏至", "小暑", "大暑", "立秋", "处暑", "白露", "秋分", "寒露", "霜降", "立冬", "小雪"]
cung_to_gua = {1: "坎", 2: "坤", 3: "震", 4: "巽", 5: "", 6: "乾", 7: "兑", 8: "艮", 9: "离"}

# ==========================================
# 2. LOGIC TÍNH LỊCH & ĐỘN CỤC CHUẨN XÁC
# ==========================================
def get_wushu_dun(day_stem, hour_branch):
    day_idx = thien_can.index(day_stem) % 5
    hour_idx = dia_chi.index(hour_branch)
    start_stem_idx = (day_idx * 2) % 10
    target_stem_idx = (start_stem_idx + hour_idx) % 10
    return thien_can[target_stem_idx]

def get_xun_leader(can, chi):
    idx_can, idx_chi = thien_can.index(can), dia_chi.index(chi)
    chi_tuan = dia_chi[(idx_chi - idx_can) % 12]
    return {"子":"戊", "戌":"己", "申":"庚", "午":"辛", "辰":"壬", "寅":"癸"}[chi_tuan]

def get_wolong_calendar_data(lunar_month, lunar_day):
    m_offset = (lunar_month - 11) % 12
    abs_day = m_offset * 30 + (lunar_day - 1)
    
    can_chi_idx = (45 + abs_day) % 60
    wl_can = thien_can[can_chi_idx % 10]
    wl_chi = dia_chi[can_chi_idx % 12]
    
    jq_idx = abs_day // 15
    wl_jieqi = wolong_jq_order[jq_idx % 24]
    
    day_in_jq = abs_day % 15
    if day_in_jq < 5: wl_yuan = "上"
    elif day_in_jq < 10: wl_yuan = "中"
    else: wl_yuan = "下"
    
    if 1 <= jq_idx % 24 <= 12: wl_dun = "阳遁"
    else: wl_dun = "阴遁"
        
    return wl_can, wl_chi, wl_jieqi, wl_yuan, wl_dun

# ==========================================
# 3. HỆ THỐNG LẬP QUẺ CHÂN TRUYỀN
# ==========================================
def lap_que_wolong(can_ngay, hoa_giap_gio, dun_type, ju_num):
    can_gio, chi_gio = hoa_giap_gio[0], hoa_giap_gio[1]
    
    cung_data = {i: {'dia': '', 'mon': '', 'thien': '', 'is_dia_bold': False, 'is_thien_bold': False} for i in range(1, 10)}
    
    # --- BƯỚC 3: DỰNG ĐỊA BÀN ---
    trung_cung_val = (10 - ju_num) if dun_type == "阳遁" else ju_num
    step_dir = 1 if dun_type == "阳遁" else -1

    dia_ban = {}
    current_val = trung_cung_val
    for cung in WOLONG_FLYING_PATH:
        can_tai_cung = WOLONG_NUM_TO_STEM.get(current_val, "")
        dia_ban[cung] = can_tai_cung
        cung_data[cung]['dia'] = can_tai_cung
        current_val += step_dir
        if current_val > 9: current_val = 1
        if current_val < 1: current_val = 9

    luc_nghi_gio = get_xun_leader(can_gio, chi_gio)
    p_circle = [c for c, can in dia_ban.items() if can == luc_nghi_gio][0]
    p_hour_stem = [c for c, can in dia_ban.items() if can == can_gio]
    p_hour_stem = p_hour_stem[0] if p_hour_stem else 5

# --- BƯỚC 4: DỰNG THIÊN BÀN (ĐÃ FIX LỖI TRUNG CUNG) ---
    p_hour_stem = [c for c, can in dia_ban.items() if can == can_gio]
    p_hour_stem = p_hour_stem[0] if p_hour_stem else 5

    if p_circle == 5:
        # Nếu Tướng kẹt ở Trung cung: 8 cung ngoài giữ nguyên như Địa Bàn
        for i in WOLONG_OUTER_PALACES: 
            cung_data[i]['thien'] = dia_ban[i]
            
        # Tướng bay ra đè lên Can Giờ
        if p_hour_stem != 5:
            cung_data[p_hour_stem]['thien'] = luc_nghi_gio
    else:
        # Xoay vòng 8 cung ngoài
        idx_source = WOLONG_OUTER_PALACES.index(p_circle)
        idx_target = WOLONG_OUTER_PALACES.index(p_hour_stem) if p_hour_stem != 5 else idx_source
        offset = (idx_target - idx_source) % 8
        
        for i in range(8):
            cung_hien_tai = WOLONG_OUTER_PALACES[i]
            cung_nguon = WOLONG_OUTER_PALACES[(i - offset) % 8]
            cung_data[cung_hien_tai]['thien'] = dia_ban[cung_nguon]

    # LUẬT CHÂN TRUYỀN: TRUNG CUNG LUÔN LUÔN TRỐNG THIÊN BÀN
    cung_data[5]['thien'] = ""

    # Bật cờ (flag) in đậm cho Thiên/Địa Can thay vì dùng ◯
    cung_data[p_hour_stem]['is_thien_bold'] = True
    cung_data[p_circle]['is_dia_bold'] = True

    # --- BƯỚC 5: AN BÁT MÔN ---
    if p_circle == 5:
        for p, door in WOLONG_ORIGINAL_GATES.items(): cung_data[p]['mon'] = door
    else:
        g_start = WOLONG_ORIGINAL_GATES[p_circle]
        s_steps = thien_can.index(can_gio) + 1
        
        seq = [1,2,3,4,5,6,7,8,9] if dun_type == "阳遁" else [9,8,7,6,5,4,3,2,1]
        idx_start = seq.index(p_circle)
        p_land = seq[(idx_start + s_steps - 1) % 9]

        if p_land == 5:
            for p, door in WOLONG_ORIGINAL_GATES.items(): cung_data[p]['mon'] = door
        else:
            idx_land_palace = WOLONG_OUTER_PALACES.index(p_land)
            idx_gate_start = WOLONG_CLOCKWISE_GATES.index(g_start)
            for i in range(8):
                cung_dich = WOLONG_OUTER_PALACES[(idx_land_palace + i) % 8]
                cua_se_dat = WOLONG_CLOCKWISE_GATES[(idx_gate_start + i) % 8]
                cung_data[cung_dich]['mon'] = cua_se_dat

    return cung_data

# ==========================================
# 4. GIAO DIỆN HTML RENDER 
# ==========================================
def render_html_table(cung_data):
    luoi_lac_thu = [[4, 9, 2], [3, 5, 7], [8, 1, 6]]
    
    html = """
    <style>
        .qmdj-table { border-collapse: collapse; width: 100%; max-width: 480px; min-width: 320px; height: 360px; table-layout: fixed; font-size: 15px; background-color: #fefefe; margin: 0 auto; }
        .qmdj-td { border: 1px solid #bfbfbf; width: 33.33%; padding: 8px 4px 18px 4px; position: relative; vertical-align: top; overflow: visible; }
        .row-top, .row-bot { display: flex; align-items: center; justify-content: flex-start; }
        .item-left { width: 55px; text-align: left; margin-left: 2px; flex-shrink: 0; line-height: 1.2; font-weight: bold; color: #333; }
        .item-right { display: flex; align-items: center; flex-wrap: wrap; flex-grow: 1; gap: 2px 3px; line-height: 1.2; margin-left: 10px; color: #b30000; font-size: 18px; }
        .wolong-stem { display: inline-block; padding: 2px 4px; }
        .bagua-mark { position: absolute; bottom: 2px; right: 6px; color: #1a1a1a; font-size: 13px; z-index: 20; }
        .wolong-spacing { margin-top: 15px; margin-bottom: 25px; }
    </style>
    <table class="qmdj-table">
    """

    for row in luoi_lac_thu:
        html += "<tr>"
        for p in row:
            d = cung_data[p]
            gua_char = cung_to_gua[p]
            gua_html = f"<div class='bagua-mark'>{gua_char}</div>" if gua_char else ""

            thien_weight = "bold" if d['is_thien_bold'] else "normal"
            dia_weight = "bold" if d['is_dia_bold'] else "normal"

            thien_html = f"<span style='font-weight: {thien_weight};'>{d['thien']}</span>"
            dia_html = f"<span style='font-weight: {dia_weight};'>{d['dia']}</span>"
            
            if p == 5:
                # Xử lý riêng Trung Cung: Có thể Thiên Bàn rỗng
                tc_thien_html = f"<div style='font-size: 18px; font-weight: {thien_weight}; color: #b30000; text-align: center; margin-bottom: 30px;'>{d['thien']}</div>" if d['thien'] else ""
                html += f"""
                <td class="qmdj-td">
                    <div style="display: flex; flex-direction: column; justify-content: center; height: 100%;">
                        {tc_thien_html}
                        <div style="font-size: 16px; font-weight: {dia_weight}; color: #b30000; text-align: center;">{d['dia']}</div>
                    </div>
                </td>"""
            else:
                html += f"""
                <td class="qmdj-td">
                    {gua_html}
                    <div class="row-top wolong-spacing">
                        <div class="item-left"></div>
                        <div class="item-right"><span class="wolong-stem">{thien_html}</span></div>
                    </div>
                    <div class="row-bot">
                        <div class="item-left">{d['mon']}</div>
                        <div class="item-right"><span class="wolong-stem">{dia_html}</span></div>
                    </div>
                </td>"""
        html += "</tr>"
        
    html += "</table>"
    return html

# ==========================================
# 5. STREAMLIT APP MAIN
# ==========================================
def get_current_vn_time():
    return datetime.now(timezone(timedelta(hours=7)))

if "init_dt" not in st.session_state:
    st.session_state.init_dt = get_current_vn_time()

col1, col2, col3 = st.columns(3)
with col1:
    selected_date = st.date_input(
        "Ngày", 
        value=st.session_state.init_dt.date(),
        min_value=date(1950, 1, 1),
        max_value=date(2050, 12, 31)
    )
with col2:
    selected_hour = st.selectbox("Giờ", options=list(range(24)), index=st.session_state.init_dt.hour)
with col3:
    selected_minute = st.selectbox("Phút", options=list(range(60)), index=st.session_state.init_dt.minute)

user_dt = datetime.combine(selected_date, datetime.min.time()).replace(hour=selected_hour, minute=selected_minute)

if user_dt.hour >= 23:
    actual_date = user_dt.date() + timedelta(days=1)
    chi_gio_idx = 0 
else:
    actual_date = user_dt.date()
    chi_gio_idx = (user_dt.hour + 1) // 2 % 12

chi_gio = dia_chi[chi_gio_idx]

day_obj = sxtwl.fromSolar(actual_date.year, actual_date.month, actual_date.day)
lunar_m = day_obj.getLunarMonth()
lunar_d = day_obj.getLunarDay()

wl_can, wl_chi, wl_jieqi, wl_yuan, wl_dun = get_wolong_calendar_data(lunar_m, lunar_d)
can_gio = get_wushu_dun(wl_can, chi_gio)
hoa_giap_hien_tai = can_gio + chi_gio
    
yuan_idx = 0 if wl_yuan == "上" else 1 if wl_yuan == "中" else 2
base_ju = solar_term_ju[wl_jieqi][yuan_idx]
hour_stem_offset = {"甲":0, "己":0, "乙":1, "庚":1, "丙":2, "辛":2, "丁":3, "壬":3, "戊":4, "癸":4}[can_gio]

if wl_dun == "阳遁":
    wl_ju = (base_ju + hour_stem_offset - 1) % 9 + 1
else:
    wl_ju = (base_ju - hour_stem_offset - 1) % 9 + 1
    if wl_ju <= 0: wl_ju += 9

data = lap_que_wolong(wl_can, hoa_giap_hien_tai, wl_dun, wl_ju)

chuoi_cuc = f"{wl_dun}{wl_ju}局"
bazi_chuoi = f"农历 {lunar_m}月 {lunar_d}日 | {hoa_giap_hien_tai}时"

title = f"<h3 style='margin-bottom:8px; font-family:sans-serif; color: #1a1a1a; font-weight: normal; font-size: 18px; text-align: center;'>{bazi_chuoi}</h3>"
sub_title = f"<h4 style='margin-top:0px; margin-bottom:8px; font-family:sans-serif; color: #555; font-weight: normal; font-size: 16px; text-align: center;'>卧龙奇门 | {chuoi_cuc}</h4>"

qimen_board_html = render_html_table(data)

combined_html = f"""
    <div style="display: flex; flex-direction: column; align-items: center; width: 100%; padding-top: 10px;">
        <div style="display: flex; flex-direction: column; align-items: center; width: 100%; max-width: 480px;">
            {title}
            {sub_title}
            {qimen_board_html}
        </div>
    </div>
"""

st.components.v1.html(combined_html, height=550, scrolling=True)
