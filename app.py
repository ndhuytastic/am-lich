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

GATE_TO_TRIGRAM = {"休门": "地", "生门": "雷", "伤门": "火", "杜门": "泽", "景门": "天", "死门": "风", "惊门": "水", "开门": "山"}
TRIGRAM_BIN = {"地": [0,0,0], "山": [0,0,1], "水": [0,1,0], "风": [0,1,1], "雷": [1,0,0], "火": [1,0,1], "泽": [1,1,0], "天": [1,1,1]}
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
    ("天","天"): (1,"Bát Thuần Càn"), ("地","地"): (2,"Bát Thuần Khôn"), ("水","雷"): (3,"Thủy Lôi Truân"), ("山","水"): (4,"Sơn Thủy Mông"),
    ("水","天"): (5,"Thủy Thiên Nhu"), ("天","水"): (6,"Thiên Thủy Tụng"), ("地","水"): (7,"Địa Thủy Sư"), ("水","地"): (8,"Thủy Địa Tỷ"),
    ("风","天"): (9,"Phong Thiên T.Súc"), ("天","泽"): (10,"Thiên Trạch Lý"), ("地","天"): (11,"Địa Thiên Thái"), ("天","地"): (12,"Thiên Địa Bĩ"),
    ("天","火"): (13,"T.Hỏa Đồng Nhân"), ("火","天"): (14,"Hỏa Thiên Đ.Hữu"), ("地","山"): (15,"Địa Sơn Khiêm"), ("雷","地"): (16,"Lôi Địa Dự"),
    ("泽","雷"): (17,"Trạch Lôi Tùy"), ("山","风"): (18,"Sơn Phong Cổ"), ("地","泽"): (19,"Địa Trạch Lâm"), ("风","地"): (20,"Phong Địa Quan"),
    ("火","雷"): (21,"Hỏa Lôi Phệ Hạp"), ("山","火"): (22,"Sơn Hỏa Bí"), ("山","地"): (23,"Sơn Địa Bác"), ("地","雷"): (24,"Địa Lôi Phục"),
    ("天","雷"): (25,"T.Lôi Vô Vọng"), ("山","天"): (26,"Sơn Thiên Đ.Súc"), ("山","雷"): (27,"Sơn Lôi Di"), ("泽","风"): (28,"Trạch Phong Đ.Quá"),
    ("水","水"): (29,"Bát Thuần Khảm"), ("火","火"): (30,"Bát Thuần Ly"), ("泽","山"): (31,"Trạch Sơn Hàm"), ("雷","风"): (32,"Lôi Phong Hằng"),
    ("天","山"): (33,"Thiên Sơn Độn"), ("雷","天"): (34,"Lôi Thiên Đ.Tráng"), ("火","地"): (35,"Hỏa Địa Tấn"), ("地","火"): (36,"Địa Hỏa Minh Di"),
    ("风","火"): (37,"Phong Hỏa G.Nhân"), ("火","泽"): (38,"Hỏa Trạch Khuê"), ("水","山"): (39,"Thủy Sơn Kiển"), ("雷","水"): (40,"Lôi Thủy Giải"),
    ("山","泽"): (41,"Sơn Trạch Tổn"), ("风","雷"): (42,"Phong Lôi Ích"), ("泽","天"): (43,"Trạch Thiên Quải"), ("天","风"): (44,"Thiên Phong Cấu"),
    ("泽","地"): (45,"Trạch Địa Tụy"), ("地","风"): (46,"Địa Phong Thăng"), ("泽","水"): (47,"Trạch Thủy Khốn"), ("水","风"): (48,"Thủy Phong Tỉnh"),
    ("泽","火"): (49,"Trạch Hỏa Cách"), ("火","风"): (50,"Hỏa Phong Đỉnh"), ("雷","雷"): (51,"Bát Thuần Chấn"), ("山","山"): (52,"Bát Thuần Cấn"),
    ("风","山"): (53,"Phong Sơn Tiệm"), ("雷","泽"): (54,"Lôi Trạch Q.Muội"), ("雷","火"): (55,"Lôi Hỏa Phong"), ("火","山"): (56,"Hỏa Sơn Lữ"),
    ("风","风"): (57,"Bát Thuần Tốn"), ("泽","泽"): (58,"Bát Thuần Đoài"), ("风","水"): (59,"Phong Thủy Hoán"), ("水","泽"): (60,"Thủy Trạch Tiết"),
    ("风","泽"): (61,"P.Trạch T.Phu"), ("雷","山"): (62,"Lôi Sơn Tiểu Quá"), ("水","火"): (63,"Thủy Hỏa Ký Tế"), ("火","水"): (64,"Hỏa Thủy Vị Tế")
}

cung_to_gua = {1: "坎", 2: "坤", 3: "震", 4: "巽", 5: "", 6: "乾", 7: "兑", 8: "艮", 9: "离"}

# ==========================================
# 2. LOGIC TÍNH LỊCH & MỆNH CUNG
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
    hb_idx = dia_chi.index(hour_branch)
    if day_branch in ["子", "午", "卯", "酉"]: start_star = 1 if dun_type == "阳遁" else 9
    elif day_branch in ["辰", "戌", "丑", "未"]: start_star = 4 if dun_type == "阳遁" else 6
    else: start_star = 7 if dun_type == "阳遁" else 3

    if dun_type == "阳遁": return (start_star + hb_idx - 1) % 9 + 1
    else:
        res = (start_star - hb_idx) % 9
        return 9 if res == 0 else res

def calc_menh_cung(b_year, b_lunar_y, b_lunar_m):
    y_sum = sum(int(d) for d in str(b_lunar_y))
    star_y = 11 - (y_sum % 9 or 9)
    if star_y <= 0: star_y += 9

    b_y_branch = dia_chi[(b_lunar_y - 4) % 12]
    if b_y_branch in ["子", "午", "卯", "酉"]: start_m = 8
    elif b_y_branch in ["辰", "戌", "丑", "未"]: start_m = 5
    else: start_m = 2
    
    star_m = (start_m - (b_lunar_m - 1)) % 9
    if star_m == 0: star_m = 9

    yin_path = [5, 6, 7, 8, 9, 1, 2, 3, 4]
    for i in range(9):
        val = (star_y - i) % 9
        if val == 0: val = 9
        if val == star_m:
            mc = yin_path[i]
            return 2 if mc == 5 else mc

# ==========================================
# 3. LẬP QUẺ CHÂN TRUYỀN & BÁT MÔN DỊCH
# ==========================================
def lap_que_wolong(can_ngay, chi_ngay, hoa_giap_gio, dun_type, ju_num, user_dt):
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
        can = WOLONG_NUM_TO_STEM.get(current_val, "")
        dia_ban[cung] = can
        cung_data[cung]['dia'] = can
        current_val += step_dir
        if current_val > 9: current_val = 1
        if current_val < 1: current_val = 9

    luc_nghi_gio = get_xun_leader(can_gio, chi_gio)
    p_circle = [c for c, can in dia_ban.items() if can == luc_nghi_gio][0]
    p_hour_stem = [c for c, can in dia_ban.items() if can == can_gio]
    p_hour_stem = p_hour_stem[0] if p_hour_stem else 5

    # 3.2 DỰNG THIÊN BÀN (Lưu giữ nguyên thuật toán ĐÚNG của bạn)
    if p_circle == 5:
        for i in WOLONG_OUTER_PALACES: cung_data[i]['thien'] = dia_ban[i]
        if p_hour_stem != 5: cung_data[p_hour_stem]['thien'] = luc_nghi_gio
    else:
        idx_source = WOLONG_OUTER_PALACES.index(p_circle)
        idx_target = WOLONG_OUTER_PALACES.index(p_hour_stem) if p_hour_stem != 5 else idx_source
        offset = (idx_target - idx_source) % 8
        for i in range(8):
            cung_data[WOLONG_OUTER_PALACES[i]]['thien'] = dia_ban[WOLONG_OUTER_PALACES[(i - offset) % 8]]

    cung_data[5]['thien'] = "" # Luật: Thiên Bàn Trung Cung trống

    for i in range(1, 10):
        if cung_data[i]['thien'] == luc_nghi_gio: cung_data[i]['is_thien_bold'] = True
        if cung_data[i]['dia'] == luc_nghi_gio: cung_data[i]['is_dia_bold'] = True

    # 3.3 AN BÁT MÔN (Lưu giữ nguyên thuật toán ĐÚNG của bạn)
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

    # 3.4 CỬU CUNG GIỜ & THIÊN THỜI
    center_hour_star = get_hour_nine_star(chi_ngay, chi_gio, dun_type)
    curr_star = center_hour_star
    for cung in WOLONG_FLYING_PATH:
        cung_data[cung]['hour_star'] = curr_star
        curr_star += step_dir
        if curr_star > 9: curr_star = 1
        if curr_star < 1: curr_star = 9

    for i in WOLONG_OUTER_PALACES:
        t_can = cung_data[i]['thien']
        d_can = cung_data[i]['dia']
        if not t_can or not d_can: continue
        
        if t_can == luc_nghi_gio and d_can == luc_nghi_gio:
            m1 = THIEN_THOI_DICT["甲"]["甲"]
            m2 = THIEN_THOI_DICT[luc_nghi_gio][luc_nghi_gio]
            cung_data[i]['thien_thoi'] = f"{m1}/{m2}"
        elif t_can == luc_nghi_gio:
            m1 = THIEN_THOI_DICT[d_can]["甲"]
            m2 = THIEN_THOI_DICT[d_can][luc_nghi_gio]
            cung_data[i]['thien_thoi'] = f"{m1}/{m2}"
        elif d_can == luc_nghi_gio:
            m1 = THIEN_THOI_DICT["甲"][t_can]
            m2 = THIEN_THOI_DICT[luc_nghi_gio][t_can]
            cung_data[i]['thien_thoi'] = f"{m1}/{m2}"
        else:
            cung_data[i]['thien_thoi'] = THIEN_THOI_DICT[d_can].get(t_can, "")

    slot = (user_dt.minute // 20) + 1
    if user_dt.hour % 2 == 0: slot += 3
    hao_dong = slot

    return cung_data, p_circle, hao_dong

# ==========================================
# 4. HÀM KIỂM TRA QUẺ & TÌM GIỜ ĐẠI CÁT
# ==========================================
def evaluate_hexagram(cung_data, menh_cung, p_circle, hao_dong):
    upper_gate = cung_data[menh_cung]['mon']
    lower_gate = cung_data[p_circle]['mon']
    upper_tri = GATE_TO_TRIGRAM.get(upper_gate, "天")
    lower_tri = GATE_TO_TRIGRAM.get(lower_gate, "地")
    
    orig_lines = TRIGRAM_BIN[lower_tri] + TRIGRAM_BIN[upper_tri]
    mut_lines = orig_lines.copy()
    mut_lines[hao_dong - 1] = 1 - mut_lines[hao_dong - 1]
    
    mut_lower = BIN_TO_TRIGRAM[tuple(mut_lines[:3])]
    mut_upper = BIN_TO_TRIGRAM[tuple(mut_lines[3:])]
    
    return EVAL_DICT.get(mut_upper, {}).get(mut_lower, "✕")

def find_good_times(start_dt, menh_cung, user_birth_star):
    found_dirs = {}
    minute_rounded = (start_dt.minute // 20) * 20
    curr_dt = start_dt.replace(minute=minute_rounded, second=0, microsecond=0)
    
    ops = {1:9, 9:1, 2:8, 8:2, 3:7, 7:3, 4:6, 6:4, 5:None}
    pha_map = {"子":9, "丑":2, "寅":2, "卯":7, "辰":6, "巳":6, "午":1, "未":8, "申":8, "酉":3, "戌":4, "亥":4}
    palace_names = {1:"Bắc", 8:"Đông Bắc", 3:"Đông", 4:"Đông Nam", 9:"Nam", 2:"Tây Nam", 7:"Tây", 6:"Tây Bắc"}
    
    for _ in range(2160): # Quét 30 ngày (20 phút / lần)
        if len(found_dirs) == 8: break
        
        if curr_dt.hour >= 23: actual_date = curr_dt.date() + timedelta(days=1); chi_gio_idx = 0 
        else: actual_date = curr_dt.date(); chi_gio_idx = (curr_dt.hour + 1) // 2 % 12
        curr_chi = dia_chi[chi_gio_idx]
        
        day_o = sxtwl.fromSolar(actual_date.year, actual_date.month, actual_date.day)
        wl_can, wl_chi, wl_jieqi, wl_yuan, wl_dun = get_wolong_calendar_data(day_o.getLunarMonth(), day_o.getLunarDay())
        
        curr_can = get_wushu_dun(wl_can, curr_chi)
        curr_hoa_giap = curr_can + curr_chi
        
        yuan_idx = 0 if wl_yuan == "上" else 1 if wl_yuan == "中" else 2
        base_ju = solar_term_ju[wl_jieqi][yuan_idx]
        
        # [ĐÃ FIX 1]: Toán học tính Cục Số (Ju) theo Bảng 4 của sách (Nhân 3)
        hour_stem_index = thien_can.index(curr_can)
        if wl_dun == "阳遁":
            curr_ju = (base_ju + (hour_stem_index * 3)) % 9
        else:
            curr_ju = (base_ju - (hour_stem_index * 3)) % 9
            
        if curr_ju <= 0: curr_ju += 9
        # ==========================================
            
        data, p_circle, hao_dong = lap_que_wolong(wl_can, wl_chi, curr_hoa_giap, wl_dun, curr_ju, curr_dt)
        
        if evaluate_hexagram(data, menh_cung, p_circle, hao_dong) == "〇":
            p_5 = None
            for i in range(1, 10):
                if data[i]['hour_star'] == 5: p_5 = i; break
            
            sat_list = []
            if p_5 and p_5 != 5: sat_list.extend([p_5, ops[p_5]]) 
            
            p_bm = None
            for i in range(1, 10):
                if data[i]['hour_star'] == user_birth_star: p_bm = i; break
            if p_bm and p_bm != 5: sat_list.extend([p_bm, ops[p_bm]]) 
                
            sat_list.append(pha_map[curr_chi]) 
            
            for p in WOLONG_OUTER_PALACES:
                if p in found_dirs: continue
                if data[p]['mon'] not in ["生门", "景门", "开门"]: continue
                if "〇" not in data[p]['thien_thoi'] or "✕" in data[p]['thien_thoi']: continue
                if p in sat_list: continue
                
                end_dt = curr_dt + timedelta(minutes=19, seconds=59)
                time_str = f"{curr_dt.strftime('%d/%m')} ({curr_dt.strftime('%H:%M')} - {end_dt.strftime('%H:%M')})"
                
                found_dirs[p] = {"dir": palace_names[p], "time": time_str, "door": data[p]['mon']}
        
        curr_dt += timedelta(minutes=20)
            
    return found_dirs

# ==========================================
# 5. GIAO DIỆN HTML RENDER 
# ==========================================
def render_html_table(cung_data, menh_cung, p_circle, hao_dong, user_birth_star):
    upper_gate = cung_data[menh_cung]['mon']
    lower_gate = cung_data[p_circle]['mon']
    upper_tri = GATE_TO_TRIGRAM.get(upper_gate, "天")
    lower_tri = GATE_TO_TRIGRAM.get(lower_gate, "地")
    
    orig_lines = TRIGRAM_BIN[lower_tri] + TRIGRAM_BIN[upper_tri]
    mut_lines = orig_lines.copy()
    mut_lines[hao_dong - 1] = 1 - mut_lines[hao_dong - 1]
    
    mut_lower = BIN_TO_TRIGRAM[tuple(mut_lines[:3])]
    mut_upper = BIN_TO_TRIGRAM[tuple(mut_lines[3:])]
    
    eval_res = EVAL_DICT.get(mut_upper, {}).get(mut_lower, "△")
    hex_info = HEX_NAME_DICT.get((mut_upper, mut_lower), (0, "Không rõ"))
    
    hex_html = f"""
        <div style="font-size:12px; font-weight:bold; color:#000; margin-bottom: 2px;">{hex_info[0]} {eval_res}</div>
        <div style="font-size:30px; line-height:0.9; color:#b30000; margin-bottom: 2px;">
            {TRIGRAM_UNICODE[mut_upper]}<br>{TRIGRAM_UNICODE[mut_lower]}
        </div>
        <div style="font-size:11px; font-weight:normal; color:#333;">{hex_info[1]}</div>
    """

    luoi_lac_thu = [[4, 9, 2], [3, 5, 7], [8, 1, 6]]
    html = """
    <style>
        .qmdj-table { border-collapse: collapse; width: 100%; max-width: 480px; min-width: 320px; height: 360px; table-layout: fixed; font-size: 15px; background-color: #fefefe; margin: 0 auto; border: 1px solid #bfbfbf; }
        .qmdj-td { border: 1px solid #bfbfbf; width: 33.33%; padding: 8px 4px 18px 4px; position: relative; vertical-align: top; overflow: visible; }
        .row-top, .row-bot { display: flex; align-items: center; justify-content: flex-start; }
        .item-left { width: 55px; text-align: left; margin-left: 2px; flex-shrink: 0; line-height: 1.2; font-weight: bold; color: #333; }
        .item-right { display: flex; align-items: center; flex-wrap: wrap; flex-grow: 1; gap: 2px 3px; line-height: 1.2; margin-left: 10px; color: #b30000; font-size: 18px; }
        .wolong-stem { display: inline-block; padding: 2px 4px; }
        .wolong-spacing { margin-top: 15px; margin-bottom: 25px; }
        .hour-star { position: absolute; top: 4px; right: 6px; color: #777; font-size: 13px; font-weight: bold; z-index: 10;}
        .star-highlight { display: inline-flex; align-items: center; justify-content: center; width: 20px; height: 20px; border: 2px dashed #0000FF; border-radius: 50%; color: #0000FF; }
        .thien-thoi-mark { position: absolute; bottom: 4px; right: 6px; color: #1a1a1a; font-size: 13px; font-weight: bold;}
    </style>
    <table class="qmdj-table">
    """

    for row in luoi_lac_thu:
        html += "<tr>"
        for p in row:
            d = cung_data[p]
            bg_color = "#e8e8e8" if p == menh_cung else "transparent"
            
            thien_weight = "bold" if d['is_thien_bold'] else "normal"
            dia_weight = "bold" if d['is_dia_bold'] else "normal"
            thien_html = f"<span style='font-weight: {thien_weight};'>{d['thien']}</span>"
            dia_html = f"<span style='font-weight: {dia_weight};'>{d['dia']}</span>"
            
            is_match = (d['hour_star'] == user_birth_star)
            h_star_val = d['hour_star']
            hour_star_html = f"<div class='hour-star'><span class='star-highlight'>{h_star_val}</span></div>" if is_match else f"<div class='hour-star'>{h_star_val}</div>"
                
            thien_thoi_html = f"<div class='thien-thoi-mark'>{d['thien_thoi']}</div>" if p != 5 else ""

            if p == 5:
                html += f"""
                <td class="qmdj-td" style="background-color: {bg_color}; text-align: center;">
                    <div style="display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100%;">
                        {hex_html}
                    </div>
                    <div style="position: absolute; bottom: 6px; right: 6px; font-size: 16px; font-weight: {dia_weight}; color: #b30000;">{d['dia']}</div>
                </td>"""
            else:
                html += f"""
                <td class="qmdj-td" style="background-color: {bg_color};">
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
# 6. STREAMLIT APP MAIN
# ==========================================
def get_current_vn_time(): return datetime.now(timezone(timedelta(hours=7)))
if "init_dt" not in st.session_state: st.session_state.init_dt = get_current_vn_time()

col1, col2, col3, col4, col5, col6 = st.columns([1.2, 0.8, 0.8, 1.2, 0.8, 0.8])
with col1: selected_date = st.date_input("Ngày Xem", value=st.session_state.init_dt.date(), min_value=date(1900, 1, 1), max_value=date(2100, 12, 31))
with col2: selected_hour = st.selectbox("Giờ Xem", options=list(range(24)), index=st.session_state.init_dt.hour)
with col3: selected_minute = st.selectbox("Phút Xem", options=list(range(60)), index=st.session_state.init_dt.minute)
with col4: birth_date = st.date_input("Ngày Sinh", value=date(1993, 1, 7), min_value=date(1900, 1, 1), max_value=date(2100, 12, 31))
with col5: birth_hour = st.selectbox("Giờ Sinh", options=list(range(24)), index=8)
with col6: birth_minute = st.selectbox("Phút Sinh", options=list(range(60)), index=15)

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

# [ĐÃ FIX 2]: Toán học tính Cục Số (Ju) theo Bảng 4 của sách (Nhân 3)
hour_stem_index = thien_can.index(can_gio)
if wl_dun == "阳遁":
    wl_ju = (base_ju + (hour_stem_index * 3)) % 9
else:
    wl_ju = (base_ju - (hour_stem_index * 3)) % 9
    
if wl_ju <= 0: wl_ju += 9
# ==========================================

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
    
    if found_dirs:
        st.success("Thời điểm Đại Cát gần nhất")
        for p in [1, 8, 3, 4, 9, 2, 7, 6]:
            if p in found_dirs:
                res = found_dirs[p]
                st.markdown(f"🧭 Hướng **{res['dir']}** 👉 {res['time']} (Cửa: {res['door']})")
            else:
                palace_names = {1:"Bắc", 8:"Đông Bắc", 3:"Đông", 4:"Đông Nam", 9:"Nam", 2:"Tây Nam", 7:"Tây", 6:"Tây Bắc"}
                st.markdown(f"🧭 Hướng **{palace_names[p]}** 👉 Không tìm thấy thời điểm đại cát trong 30 ngày tới.")
st.markdown("</div>", unsafe_allow_html=True)
