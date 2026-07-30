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

WOLONG_OUTER_PALACES = [4, 9, 2, 7, 6, 1, 8, 3]
WOLONG_FLYING_PATH = [5, 6, 7, 8, 9, 1, 2, 3, 4]
WOLONG_NUM_TO_STEM = {1: "癸", 2: "丁", 3: "丙", 4: "乙", 5: "戊", 6: "己", 7: "庚", 8: "辛", 9: "壬", 0: "甲"}
WOLONG_ORIGINAL_GATES = {1: "休门", 8: "生门", 3: "伤门", 4: "杜门", 9: "景门", 2: "死门", 7: "惊门", 6: "开门"}
WOLONG_CLOCKWISE_GATES = ["景门", "死门", "惊门", "开门", "休门", "生门", "伤门", "杜门"]
cung_to_gua = {1: "坎", 2: "坤", 3: "震", 4: "巽", 5: "", 6: "乾", 7: "兑", 8: "艮", 9: "离"}

solar_term_ju = {
    "冬至":[1,7,4], "小寒":[2,8,5], "大寒":[3,9,6], "立春":[8,5,2], "雨水":[9,6,3], "惊蛰":[1,7,4],
    "春分":[3,9,6], "清明":[4,1,7], "谷雨":[5,2,8], "立夏":[4,1,7], "小满":[5,2,8], "芒种":[6,3,9],
    "夏至":[9,3,6], "小暑":[8,2,5], "大暑":[7,1,4], "立秋":[2,5,8], "处暑":[1,4,7], "白露":[9,3,6],
    "秋分":[7,1,4], "寒露":[6,9,3], "霜降":[5,8,2], "立冬":[6,9,3], "小雪":[5,8,2], "大雪":[4,7,1]
}
wolong_jq_order = ["大雪", "冬至", "小寒", "大寒", "立春", "雨水", "惊蛰", "春分", "清明", "谷雨", "立夏", "小满", "芒种", "夏至", "小暑", "大暑", "立秋", "处暑", "白露", "秋分", "寒露", "霜降", "立冬", "小雪"]

THIEN_THOI_DICT = {
    "甲": {"甲": "〇", "乙": "〇", "丙": "〇", "丁": "〇", "戊": "✕", "己": "✕", "庚": "✕", "辛": "✕", "壬": "✕", "癸": "〇"},
    "乙": {"甲": "〇", "乙": "✕", "丙": "〇", "丁": "〇", "戊": "〇", "己": "〇", "庚": "✕", "辛": "✕", "壬": "✕", "癸": "✕"},
    "丙": {"甲": "〇", "乙": "〇", "丙": "✕", "丁": "✕", "戊": "〇", "己": "✕", "庚": "✕", "辛": "〇", "壬": "✕", "癸": "〇"},
    "丁": {"甲": "〇", "乙": "〇", "丙": "〇", "丁": "〇", "戊": "〇", "己": "✕", "庚": "〇", "辛": "〇", "壬": "〇", "癸": "✕"},
    "戊": {"甲": "✕", "乙": "〇", "丙": "〇", "丁": "〇", "戊": "✕", "己": "〇", "庚": "✕", "辛": "✕", "壬": "〇", "癸": "〇"},
    "己": {"甲": "〇", "乙": "〇", "丙": "〇", "丁": "✕", "戊": "✕", "己": "✕", "庚": "✕", "辛": "✕", "壬": "✕", "癸": "✕"},
    "庚": {"甲": "✕", "乙": "✕", "丙": "✕", "丁": "〇", "戊": "✕", "己": "✕", "庚": "✕", "辛": "✕", "壬": "✕", "癸": "✕"},
    "辛": {"甲": "✕", "乙": "✕", "丙": "〇", "丁": "✕", "戊": "✕", "己": "✕", "庚": "✕", "辛": "✕", "壬": "〇", "癸": "✕"},
    "壬": {"甲": "✕", "乙": "〇", "丙": "〇", "丁": "〇", "戊": "〇", "己": "✕", "庚": "✕", "辛": "✕", "壬": "✕", "癸": "✕"},
    "癸": {"甲": "〇", "乙": "✕", "丙": "✕", "丁": "✕", "戊": "✕", "己": "✕", "庚": "✕", "辛": "✕", "壬": "✕", "癸": "✕"}
}

# ==========================================
# 2. LOGIC TÍNH LỊCH
# ==========================================
def get_wushu_dun(day_stem, hour_branch):
    day_idx = thien_can.index(day_stem) % 5
    hour_idx = dia_chi.index(hour_branch)
    return thien_can[(day_idx * 2 + hour_idx) % 10]

def get_xun_leader(can, chi):
    idx_can, idx_chi = thien_can.index(can), dia_chi.index(chi)
    return {"子":"戊", "戌":"己", "申":"庚", "午":"辛", "辰":"壬", "寅":"癸"}[dia_chi[(idx_chi - idx_can) % 12]]

def get_wolong_calendar_data(lunar_month, lunar_day):
    abs_day = ((lunar_month - 11) % 12) * 30 + (lunar_day - 1)
    wl_can = thien_can[(45 + abs_day) % 10]
    wl_chi = dia_chi[(45 + abs_day) % 12]
    wl_jieqi = wolong_jq_order[abs_day // 15 % 24]
    day_in_jq = abs_day % 15
    wl_yuan = "上" if day_in_jq < 5 else "中" if day_in_jq < 10 else "下"
    wl_dun = "阳遁" if 1 <= (abs_day // 15 % 24) <= 12 else "阴遁"
    return wl_can, wl_chi, wl_jieqi, wl_yuan, wl_dun

def get_hour_nine_star(day_branch, hour_branch, dun_type):
    """Tính Cửu cung của giờ (Nhân hòa) từ Bảng 3"""
    hb_idx = dia_chi.index(hour_branch)
    if day_branch in ["子", "午", "卯", "酉"]: start_star = 1 if dun_type == "阳遁" else 1
    elif day_branch in ["辰", "戌", "丑", "未"]: start_star = 4 if dun_type == "阳遁" else 7
    else: start_star = 7 if dun_type == "阳遁" else 4

    if dun_type == "阳遁":
        return (start_star + hb_idx - 1) % 9 + 1
    else:
        res = (start_star - hb_idx) % 9
        return 9 if res == 0 else res

# ==========================================
# 3. LẬP QUẺ CHÂN TRUYỀN
# ==========================================
def lap_que_wolong(can_ngay, chi_ngay, hoa_giap_gio, dun_type, ju_num):
    can_gio, chi_gio = hoa_giap_gio[0], hoa_giap_gio[1]
    
    cung_data = {i: {
        'dia': '', 'mon': '', 'thien': '', 'is_dia_bold': False, 'is_thien_bold': False, 
        'hour_star': '', 'thien_thoi': ''
    } for i in range(1, 10)}
    
    # 3.1 DỰNG ĐỊA BÀN
    current_val = (10 - ju_num) if dun_type == "阳遁" else ju_num
    step_dir = 1 if dun_type == "阳遁" else -1

    dia_ban = {}
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

    # 3.2 DỰNG THIÊN BÀN (FIXED TRUNG CUNG)
    if p_circle == 5:
        for i in WOLONG_OUTER_PALACES: cung_data[i]['thien'] = dia_ban[i]
        if p_hour_stem != 5: cung_data[p_hour_stem]['thien'] = luc_nghi_gio
    else:
        idx_source = WOLONG_OUTER_PALACES.index(p_circle)
        idx_target = WOLONG_OUTER_PALACES.index(p_hour_stem) if p_hour_stem != 5 else idx_source
        offset = (idx_target - idx_source) % 8
        for i in range(8):
            cung_hien_tai = WOLONG_OUTER_PALACES[i]
            cung_nguon = WOLONG_OUTER_PALACES[(i - offset) % 8]
            cung_data[cung_hien_tai]['thien'] = dia_ban[cung_nguon]

    cung_data[5]['thien'] = "" # Trục chết

    for i in range(1, 10):
        if cung_data[i]['thien'] == luc_nghi_gio: cung_data[i]['is_thien_bold'] = True
        if cung_data[i]['dia'] == luc_nghi_gio: cung_data[i]['is_dia_bold'] = True

    # 3.3 AN BÁT MÔN
    if p_circle == 5:
        for p, door in WOLONG_ORIGINAL_GATES.items(): cung_data[p]['mon'] = door
    else:
        g_start = WOLONG_ORIGINAL_GATES[p_circle]
        s_steps = thien_can.index(can_gio) + 1
        seq = [1,2,3,4,5,6,7,8,9] if dun_type == "阳遁" else [9,8,7,6,5,4,3,2,1]
        p_land = seq[(seq.index(p_circle) + s_steps - 1) % 9]

        if p_land == 5:
            for p, door in WOLONG_ORIGINAL_GATES.items(): cung_data[p]['mon'] = door
        else:
            idx_land = WOLONG_OUTER_PALACES.index(p_land)
            idx_gate = WOLONG_CLOCKWISE_GATES.index(g_start)
            for i in range(8):
                cung_data[WOLONG_OUTER_PALACES[(idx_land + i) % 8]]['mon'] = WOLONG_CLOCKWISE_GATES[(idx_gate + i) % 8]

    # 3.4 TÍNH CỬU CUNG GIỜ BÓI (Bay thuận/nghịch theo Độn)
    center_hour_star = get_hour_nine_star(chi_ngay, chi_gio, dun_type)
    curr_star = center_hour_star
    for cung in WOLONG_FLYING_PATH:
        cung_data[cung]['hour_star'] = curr_star
        curr_star += step_dir
        if curr_star > 9: curr_star = 1
        if curr_star < 1: curr_star = 9

    # 3.5 TÍNH THIÊN THỜI (BẢNG 5 - Xử lý kép)
    for i in WOLONG_OUTER_PALACES:
        t_can = cung_data[i]['thien']
        d_can = cung_data[i]['dia']
        if not t_can or not d_can: continue
        
        if d_can == luc_nghi_gio:
            # Ghi rõ Giáp trước, Lục Nghi sau
            mark_giap = THIEN_THOI_DICT["甲"].get(t_can, "")
            mark_goc = THIEN_THOI_DICT[d_can].get(t_can, "")
            cung_data[i]['thien_thoi'] = f"甲:{mark_giap} <span style='font-weight:normal;color:#ccc;'>|</span> {d_can}:{mark_goc}"
        else:
            cung_data[i]['thien_thoi'] = THIEN_THOI_DICT[d_can].get(t_can, "")

    return cung_data

# ==========================================
# 4. GIAO DIỆN HTML RENDER 
# ==========================================
def render_html_table(cung_data, user_birth_star):
    luoi_lac_thu = [[4, 9, 2], [3, 5, 7], [8, 1, 6]]
    
    html = """
    <style>
        .qmdj-table { border-collapse: collapse; width: 100%; max-width: 480px; min-width: 320px; height: 360px; table-layout: fixed; font-size: 15px; background-color: #fefefe; margin: 0 auto; }
        .qmdj-td { border: 1px solid #bfbfbf; width: 33.33%; padding: 8px 4px 18px 4px; position: relative; vertical-align: top; overflow: visible; }
        .row-top, .row-bot { display: flex; align-items: center; justify-content: flex-start; }
        .item-left { width: 55px; text-align: left; margin-left: 2px; flex-shrink: 0; line-height: 1.2; font-weight: bold; color: #333; }
        .item-right { display: flex; align-items: center; flex-wrap: wrap; flex-grow: 1; gap: 2px 3px; line-height: 1.2; margin-left: 10px; color: #b30000; font-size: 18px; }
        .wolong-stem { display: inline-block; padding: 2px 4px; }
        .wolong-spacing { margin-top: 15px; margin-bottom: 25px; }
        
        .hour-star { position: absolute; top: 4px; right: 6px; color: #000; font-size: 14px; font-weight: bold; z-index: 10;}
        .star-highlight { display: inline-flex; align-items: center; justify-content: center; width: 22px; height: 22px; border: 2px solid #b30000; border-radius: 50%; color: #b30000; background-color: rgba(179,0,0,0.1); }
        .thien-thoi-mark { position: absolute; bottom: 4px; right: 6px; color: #1a1a1a; font-size: 14px; font-weight: bold;}
    </style>
    <table class="qmdj-table">
    """

    for row in luoi_lac_thu:
        html += "<tr>"
        for p in row:
            d = cung_data[p]
            thien_weight = "bold" if d['is_thien_bold'] else "normal"
            dia_weight = "bold" if d['is_dia_bold'] else "normal"

            thien_html = f"<span style='font-weight: {thien_weight};'>{d['thien']}</span>"
            dia_html = f"<span style='font-weight: {dia_weight};'>{d['dia']}</span>"
            
            # Highlight Cửu Cung Giờ Sinh
            is_match = (d['hour_star'] == user_birth_star)
            h_star_val = d['hour_star']
            if is_match:
                hour_star_html = f"<div class='hour-star'><span class='star-highlight'>{h_star_val}</span></div>"
            else:
                hour_star_html = f"<div class='hour-star'>{h_star_val}</div>"
                
            thien_thoi_html = f"<div class='thien-thoi-mark'>{d['thien_thoi']}</div>" if p != 5 else ""

            if p == 5:
                html += f"""
                <td class="qmdj-td">
                    {hour_star_html}
                    <div style="position: absolute; bottom: 6px; right: 6px; font-size: 16px; font-weight: {dia_weight}; color: #b30000;">{d['dia']}</div>
                </td>"""
            else:
                html += f"""
                <td class="qmdj-td">
                    {hour_star_html}
                    {thien_thoi_html}
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

st.markdown("<h4 style='text-align: center; margin-bottom: 2px;'>THÔNG TIN XEM BÓI</h4>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    selected_date = st.date_input("Ngày xem", value=st.session_state.init_dt.date(), min_value=date(1950, 1, 1), max_value=date(2050, 12, 31))
with col2:
    selected_hour = st.selectbox("Giờ xem", options=list(range(24)), index=st.session_state.init_dt.hour)
with col3:
    selected_minute = st.selectbox("Phút xem", options=list(range(60)), index=st.session_state.init_dt.minute)

st.markdown("<h4 style='text-align: center; margin-top: 15px; margin-bottom: 2px;'>THÔNG TIN NGƯỜI XEM</h4>", unsafe_allow_html=True)
col4, col5, col6 = st.columns(3)
with col4:
    birth_date = st.date_input("Ngày sinh", value=date(1990, 1, 1), min_value=date(1900, 1, 1), max_value=date(2050, 12, 31))
with col5:
    birth_hour = st.selectbox("Giờ sinh", options=list(range(24)), index=12)
with col6:
    birth_minute = st.selectbox("Phút sinh", options=list(range(60)), index=0)

# ----------------- XỬ LÝ LỊCH XEM -----------------
user_dt = datetime.combine(selected_date, datetime.min.time()).replace(hour=selected_hour, minute=selected_minute)
actual_date = user_dt.date() + timedelta(days=1) if user_dt.hour >= 23 else user_dt.date()
chi_gio_idx = 0 if user_dt.hour >= 23 else (user_dt.hour + 1) // 2 % 12
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

if wl_dun == "阳遁": wl_ju = (base_ju + hour_stem_offset - 1) % 9 + 1
else:
    wl_ju = (base_ju - hour_stem_offset - 1) % 9 + 1
    if wl_ju <= 0: wl_ju += 9

# ----------------- XỬ LÝ GIỜ SINH -----------------
b_dt = datetime.combine(birth_date, datetime.min.time()).replace(hour=birth_hour, minute=birth_minute)
b_actual_date = b_dt.date() + timedelta(days=1) if b_dt.hour >= 23 else b_dt.date()
b_chi_idx = 0 if b_dt.hour >= 23 else (b_dt.hour + 1) // 2 % 12
b_chi_gio = dia_chi[b_chi_idx]

b_day_obj = sxtwl.fromSolar(b_actual_date.year, b_actual_date.month, b_actual_date.day)
b_lunar_m = b_day_obj.getLunarMonth()
b_lunar_d = b_day_obj.getLunarDay()

b_wl_can, b_wl_chi, b_wl_jieqi, _, b_wl_dun = get_wolong_calendar_data(b_lunar_m, b_lunar_d)
user_birth_star = get_hour_nine_star(b_wl_chi, b_chi_gio, b_wl_dun)

# ----------------- RENDER BÀN -----------------
data = lap_que_wolong(wl_can, wl_chi, hoa_giap_hien_tai, wl_dun, wl_ju)

chuoi_cuc = f"{wl_dun}{wl_ju}局"
bazi_chuoi = f"农历 {lunar_m}月 {lunar_d}日 | {hoa_giap_hien_tai}时"

title = f"<h3 style='margin-bottom:8px; font-family:sans-serif; color: #1a1a1a; font-weight: normal; font-size: 18px; text-align: center;'>{bazi_chuoi}</h3>"
sub_title = f"<h4 style='margin-top:0px; margin-bottom:8px; font-family:sans-serif; color: #555; font-weight: normal; font-size: 16px; text-align: center;'>卧龙奇门 | {chuoi_cuc}</h4>"

qimen_board_html = render_html_table(data, user_birth_star)

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
