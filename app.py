import streamlit as st
import sxtwl
from datetime import datetime, timedelta, timezone, date

st.set_page_config(page_title="Kỳ Môn Độn Giáp - Ngọa Long", layout="wide", initial_sidebar_state="collapsed")

### ==========================================
### 1. DỮ LIỆU CƠ BẢN & HẰNG SỐ CHÂN TRUYỀN
### ==========================================
thien_can = "甲乙丙丁戊己庚辛壬癸"
dia_chi = "子丑寅卯辰巳午未申酉戌亥"
luc_nghi = ["戊", "己", "庚", "辛", "壬", "癸", "丁", "丙", "乙"]

WOLONG_OUTER_PALACES = [4-11]
WOLONG_FLYING_PATH = [4-12]
WOLONG_NUM_TO_STEM = {1: "癸", 2: "丁", 3: "丙", 4: "乙", 5: "戊", 6: "己", 7: "庚", 8: "辛", 9: "壬", 0: "甲"}
WOLONG_ORIGINAL_GATES = {1: "休门", 8: "生门", 3: "伤门", 4: "杜门", 9: "景门", 2: "死门", 7: "惊门", 6: "开门"}
WOLONG_CLOCKWISE_GATES = ["景门", "死门", "惊门", "开门", "休门", "生门", "伤门", "杜门"]

# [ĐÃ FIX 1]: Chuyển đổi dữ liệu Cục số (Ju) thành cấu trúc tra cứu chính xác theo Bảng 4 (Trang 234)
# Gồm 6 phần tử tương ứng với 6 Tuần (Giáp Tý -> Giáp Dần) trong 1 Nguyên
solar_term_ju = {
    "冬至": {"上": [4, 6, 8, 9, 11, 12], "中": [5-7, 9-11], "下": [4, 5, 7, 8, 10, 12]},
    "小寒": {"上": [4, 6-8, 11, 12], "中": [4-6, 9-11], "下": [5, 7-10, 12]},
    "大寒": {"上": [4, 7, 8, 10-12], "中": [4-6, 9, 11, 12], "下": [5-10]},
    "立春": {"上": [4-6, 9-11], "中": [5, 7-10, 12], "下": [4, 6-8, 11, 12]},
    "雨水": {"上": [4-6, 9, 11, 12], "中": [5-10], "下": [4, 7, 8, 10-12]},
    "惊蛰": {"上": [4, 6, 8, 9, 11, 12], "中": [5-7, 9-11], "下": [4, 5, 7, 8, 10, 12]},
    "春分": {"上": [4, 7, 8, 10-12], "中": [4-6, 9, 11, 12], "下": [5-10]},
    "清明": {"上": [4, 5, 7, 8, 10, 12], "中": [4, 6, 8, 9, 11, 12], "下": [5-7, 9-11]},
    "谷雨": {"上": [5, 7-10, 12], "中": [4, 6-8, 11, 12], "下": [4-6, 9-11]},
    "立夏": {"上": [4, 5, 7, 8, 10, 12], "中": [4, 6, 8, 9, 11, 12], "下": [5-7, 9-11]},
    "小满": {"上": [5, 7-10, 12], "中": [4, 6-8, 11, 12], "下": [4-6, 9-11]},
    "芒种": {"上": [5-10], "中": [4, 7, 8, 10-12], "下": [4-6, 9, 11, 12]},
    "夏至": {"上": [4, 5, 7, 8, 10, 12], "中": [5-7, 9-11], "下": [4, 6, 8, 9, 11, 12]},
    "小暑": {"上": [4, 7, 8, 10-12], "中": [5-10], "下": [4-6, 9, 11, 12]},
    "大暑": {"上": [4, 6-8, 11, 12], "中": [5, 7-10, 12], "下": [4-6, 9-11]},
    "立秋": {"上": [5-10], "中": [4-6, 9, 11, 12], "下": [4, 7, 8, 10-12]},
    "处暑": {"上": [5, 7-10, 12], "中": [4-6, 9-11], "下": [4, 6-8, 11, 12]},
    "白露": {"上": [4, 5, 7, 8, 10, 12], "中": [5-7, 9-11], "下": [4, 6, 8, 9, 11, 12]},
    "秋分": {"上": [4, 6-8, 11, 12], "中": [5, 7-10, 12], "下": [4-6, 9-11]},
    "寒露": {"上": [4, 6, 8, 9, 11, 12], "中": [4, 5, 7, 8, 10, 12], "下": [5-7, 9-11]},
    "霜降": {"上": [4-6, 9, 11, 12], "中": [4, 7, 8, 10-12], "下": [5-10]},
    "立冬": {"上": [4, 6, 8, 9, 11, 12], "中": [4, 5, 7, 8, 10, 12], "下": [5-7, 9-11]},
    "小雪": {"上": [4-6, 9, 11, 12], "中": [4, 7, 8, 10-12], "下": [5-10]},
    "大雪": {"上": [4-6, 9-11], "中": [4, 6-8, 11, 12], "下": [5, 7-10, 12]}
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

GATE_TO_TRIGRAM = {"休门": "地", "生门": "雷", "伤门": "火", "杜门": "泽", "景门": "天", "死门": "风", "惊门": "水", "开门": "山"}
TRIGRAM_BIN = {"地": , "山": [9], "水": [9], "风": [9], "雷": [9], "火": [9], "泽": [9], "天": [9]}
BIN_TO_TRIGRAM = {tuple(v): k for k, v in TRIGRAM_BIN.items()}
TRIGRAM_UNICODE = {"天": "☰", "泽": "☱", "火": "☲", "雷": "☳", "风": "☴", "水": "☵", "山": "☶", "地": "☷"}

EVAL_DICT = {
    "风": {"风":"〇", "火":"△", "地":"✕", "雷":"〇", "泽":"△", "山":"〇", "水":"✕", "天":"〇"},
    "天": {"风":"✕", "火":"△", "地":"✕", "雷":"〇", "泽":"✕", "山":"△", "水":"✕", "天":"✕"},
    "水": {"风":"✕", "火":"✕", "地":"✕", "雷":"〇", "泽":"✕", "山":"✕", "水":"〇", "天":"✕"},
    "泽": {"风":"△", "火":"✕", "地":"✕", "雷":"✕", "泽":"✕", "山":"✕", "水":"〇", "天":"〇"},
    "山": {"风":"△", "火":"〇", "地":"✕", "雷":"✕", "泽":"✕", "山":"〇", "水":"✕", "天":"✕"},
    "火": {"风":"✕", "火":"〇", "地":"〇", "雷":"✕", "泽":"✕", "山":"△", "水":"〇", "天":"✕"},
    "地": {"风":"〇", "火":"〇", "地":"〇", "雷":"✕", "泽":"✕", "山":"〇", "水":"△", "天":"△"},
    "雷": {"风":"✕", "火":"△", "地":"〇", "雷":"〇", "泽":"〇", "山":"△", "水":"〇", "天":"✕"}
}

HEX_NAME_DICT = {
    ("天","天"): (1,"Bát Thuần Càn"), ("地","地"): (2,"Bát Thuần Khôn"), ("水","雷"): (3,"Thủy Lôi Truân"), ("山","水"): (4,"Sơn Thủy Mông"), ("水","天"): (5,"Thủy Thiên Nhu"), ("天","水"): (6,"Thiên Thủy Tụng"), ("地","水"): (7,"Địa Thủy Sư"), ("水","地"): (8,"Thủy Địa Tỷ"), ("风","天"): (9,"Phong Thiên T.Súc"), ("天","泽"): (10,"Thiên Trạch Lý"), ("地","天"): (11,"Địa Thiên Thái"), ("天","地"): (12,"Thiên Địa Bĩ"), ("天","火"): (13,"T.Hỏa Đồng Nhân"), ("火","天"): (14,"Hỏa Thiên Đ.Hữu"), ("地","山"): (15,"Địa Sơn Khiêm"), ("雷","地"): (16,"Lôi Địa Dự"), ("泽","雷"): (17,"Trạch Lôi Tùy"), ("山","风"): (18,"Sơn Phong Cổ"), ("地","泽"): (19,"Địa Trạch Lâm"), ("风","地"): (20,"Phong Địa Quan"), ("火","雷"): (21,"Hỏa Lôi Phệ Hạp"), ("山","火"): (22,"Sơn Hỏa Bí"), ("山","地"): (23,"Sơn Địa Bác"), ("地","雷"): (24,"Địa Lôi Phục"), ("天","雷"): (25,"T.Lôi Vô Vọng"), ("山","天"): (26,"Sơn Thiên Đ.Súc"), ("山","雷"): (27,"Sơn Lôi Di"), ("泽","风"): (28,"Trạch Phong Đ.Quá"), ("水","水"): (29,"Bát Thuần Khảm"), ("火","火"): (30,"Bát Thuần Ly"), ("泽","山"): (31,"Trạch Sơn Hàm"), ("雷","风"): (32,"Lôi Phong Hằng"), ("天","山"): (33,"Thiên Sơn Độn"), ("雷","天"): (34,"Lôi Thiên Đ.Tráng"), ("火","地"): (35,"Hỏa Địa Tấn"), ("地","火"): (36,"Địa Hỏa Minh Di"), ("风","火"): (37,"Phong Hỏa G.Nhân"), ("火","泽"): (38,"Hỏa Trạch Khuê"), ("水","山"): (39,"Thủy Sơn Kiển"), ("雷","水"): (40,"Lôi Thủy Giải"), ("山","泽"): (41,"Sơn Trạch Tổn"), ("风","雷"): (42,"Phong Lôi Ích"), ("泽","天"): (43,"Trạch Thiên Quải"), ("天","风"): (44,"Thiên Phong Cấu"), ("泽","地"): (45,"Trạch Địa Tụy"), ("地","风"): (46,"Địa Phong Thăng"), ("泽","水"): (47,"Trạch Thủy Khốn"), ("水","风"): (48,"Thủy Phong Tỉnh"), ("泽","火"): (49,"Trạch Hỏa Cách"), ("火","风"): (50,"Hỏa Phong Đỉnh"), ("雷","雷"): (51,"Bát Thuần Chấn"), ("山","山"): (52,"Bát Thuần Cấn"), ("风","山"): (53,"Phong Sơn Tiệm"), ("雷","泽"): (54,"Lôi Trạch Q.Muội"), ("雷","火"): (55,"Lôi Hỏa Phong"), ("火","山"): (56,"Hỏa Sơn Lữ"), ("风","风"): (57,"Bát Thuần Tốn"), ("泽","泽"): (58,"Bát Thuần Đoài"), ("风","水"): (59,"Phong Thủy Hoán"), ("水","泽"): (60,"Thủy Trạch Tiết"), ("风","泽"): (61,"P.Trạch T.Phu"), ("雷","山"): (62,"Lôi Sơn Tiểu Quá"), ("水","火"): (63,"Thủy Hỏa Ký Tế"), ("火","水"): (64,"Hỏa Thủy Vị Tế")
}

cung_to_gua = {1: "坎", 2: "坤", 3: "震", 4: "巽", 5: "", 6: "乾", 7: "兑", 8: "艮", 9: "离"}

### ==========================================
### 2. LOGIC TÍNH LỊCH & MỆNH CUNG
### ==========================================
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
    hb_idx = dia_chi.index(hour_branch)
    if day_branch in ["子", "午", "卯", "酉"]:
        start_star = 1 if dun_type == "阳遁" else 9
    elif day_branch in ["辰", "戌", "丑", "未"]:
        start_star = 4 if dun_type == "阳遁" else 6
    else:
        start_star = 7 if dun_type == "阳遁" else 3

def calc_menh_cung(b_year, b_lunar_y, b_lunar_m):
    y_sum = sum(int(d) for d in str(b_lunar_y))
    star_y = 11 - (y_sum % 9 or 9)
    if star_y <= 0:
        star_y += 9

### ==========================================
### 3. LẬP QUẺ CHÂN TRUYỀN & BÁT MÔN DỊCH
### ==========================================
def lap_que_wolong(can_ngay, chi_ngay, hoa_giap_gio, dun_type, ju_num, user_dt):
    can_gio, chi_gio = hoa_giap_gio, hoa_giap_gio[9]

### ==========================================
### 4. HÀM KIỂM TRA QUẺ & TÌM GIỜ ĐẠI CÁT
### ==========================================
def evaluate_hexagram(cung_data, menh_cung, p_circle, hao_dong):
    upper_gate = cung_data[menh_cung]['mon']
    lower_gate = cung_data[p_circle]['mon']
    upper_tri = GATE_TO_TRIGRAM.get(upper_gate, "天")
    lower_tri = GATE_TO_TRIGRAM.get(lower_gate, "地")

def find_good_times(start_dt, menh_cung, user_birth_star):
    found_dirs = {}
    minute_rounded = (start_dt.minute // 20) * 20
    curr_dt = start_dt.replace(minute=minute_rounded, second=0, microsecond=0)

### ==========================================
### 5. GIAO DIỆN HTML RENDER
### ==========================================
def render_html_table(cung_data, menh_cung, p_circle, hao_dong, user_birth_star):
    upper_gate = cung_data[menh_cung]['mon']
    lower_gate = cung_data[p_circle]['mon']
    upper_tri = GATE_TO_TRIGRAM.get(upper_gate, "天")
    lower_tri = GATE_TO_TRIGRAM.get(lower_gate, "地")

### ==========================================
### 6. STREAMLIT APP MAIN
### ==========================================
def get_current_vn_time():
    return datetime.now(timezone(timedelta(hours=7)))

if "init_dt" not in st.session_state:
    st.session_state.init_dt = get_current_vn_time()

col1, col2, col3, col4, col5, col6 = st.columns([1.2, 0.8, 0.8, 1.2, 0.8, 0.8])
with col1:
    selected_date = st.date_input("Ngày Xem", value=st.session_state.init_dt.date(), min_value=date(1900, 1, 1), max_value=date(2100, 12, 31))
with col2:
    selected_hour = st.selectbox("Giờ Xem", options=list(range(24)), index=st.session_state.init_dt.hour)
with col3:
    selected_minute = st.selectbox("Phút Xem", options=list(range(60)), index=st.session_state.init_dt.minute)
with col4:
    birth_date = st.date_input("Ngày Sinh", value=date(1993, 1, 7), min_value=date(1900, 1, 1), max_value=date(2100, 12, 31))
with col5:
    birth_hour = st.selectbox("Giờ Sinh", options=list(range(24)), index=8)
with col6:
    birth_minute = st.selectbox("Phút Sinh", options=list(range(60)), index=15)

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

### ---------------------------------------------------
### [ĐÃ FIX 2]: Thuật toán lấy Cục số theo Bảng 4 Chuẩn
### ---------------------------------------------------

# B1: Lấy Tuần (Xun Leader) của Can Chi Giờ hiện tại
xun_leader = get_xun_leader(can_gio, chi_gio)

# B2: Ánh xạ vị trí của Tuần để lấy Index hàng (từ 0 đến 5)
xun_list = ["戊", "己", "庚", "辛", "壬", "癸"] 
row_index = xun_list.index(xun_leader)

# B3: Truy xuất trực tiếp Cục số (Ju) từ Data mảng 6 phần tử đã tạo bên trên
wl_ju = solar_term_ju[wl_jieqi][wl_yuan][row_index]

### ---------------------------------------------------

### ==========================================
b_dt = datetime.combine(birth_date, datetime.min.time()).replace(hour=birth_hour, minute=birth_minute)
b_actual_date = b_dt.date() + timedelta(days=1) if b_dt.hour >= 23 else b_dt.date()
b_chi_idx = 0 if b_dt.hour >= 23 else (b_dt.hour + 1) // 2 % 12
b_chi_gio = dia_chi[b_chi_idx]

b_day_obj = sxtwl.fromSolar(b_actual_date.year, b_actual_date.month, b_actual_date.day)
b_lunar_m = b_day_obj.getLunarMonth()

b_wl_can, b_wl_chi, _, _, b_wl_dun = get_wolong_calendar_data(b_lunar_m, b_day_obj.getLunarDay())
user_birth_star = get_hour_nine_star(dia_chi[b_day_obj.getDayGZ().dz], b_chi_gio, b_wl_dun)
menh_cung = calc_menh_cung(b_actual_date.year, b_day_obj.getLunarYear(), b_lunar_m)

data, p_circle, hao_dong = lap_que_wolong(wl_can, wl_chi, hoa_giap_hien_tai, wl_dun, wl_ju, user_dt)

bazi_chuoi = f"农历 {lunar_m}月 {lunar_d}日 | {hoa_giap_hien_tai}时"
title = f"<h3 style='margin-bottom:8px; font-family:sans-serif; color: #1a1a1a; font-weight: normal; font-size: 18px; text-align: center;'>{bazi_chuoi}</h3>"
sub_title = f"<h4 style='margin-top:0px; margin-bottom:8px; font-family:sans-serif; color: #555; font-weight: normal; font-size: 16px; text-align: center;'>卧龙奇门 | {wl_dun}{wl_ju}局</h4>"

qimen_board_html = render_html_table(data, menh_cung, p_circle, hao_dong, user_birth_star)

combined_html = f"""
<div style="display: flex; flex-direction: column; align-items: center; width: 100%; padding-top: 10px;">
    <div style="display: flex; flex-direction: column; align-items: center; width: 100%; max-width: 480px;">
        {title}
        {sub_title}
        {qimen_board_html}
    </div>
</div>
"""
st.components.v1.html(combined_html, height=520, scrolling=False)

st.markdown("<div style='max-width: 480px; margin: 0 auto;'>", unsafe_allow_html=True)
if st.button("🔍 Tìm Thời Điểm Đại Cát Gần Nhất (Cho 8 Hướng)", use_container_width=True):
    with st.spinner("Đang quét các mốc 20 phút tương lai..."):
        found_dirs = find_good_times(user_dt, menh_cung, user_birth_star)

st.markdown("</div>", unsafe_allow_html=True)
