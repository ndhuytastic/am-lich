import streamlit as st
import sxtwl
from datetime import datetime, timedelta, timezone, date
import warnings

warnings.filterwarnings('ignore')
st.set_page_config(page_title="Kỳ Môn Hojo Ikkou", layout="wide", initial_sidebar_state="collapsed")

# ==========================================
# 1. DỮ LIỆU CƠ BẢN & HẰNG SỐ CHÂN TRUYỀN (HỒNG PHÁI)
# ==========================================
thien_can = "甲乙丙丁戊己庚辛壬癸"
dia_chi = "子丑寅卯辰巳午未申酉戌亥"
luc_nghi = ["戊", "己", "庚", "辛", "壬", "癸", "丁", "丙", "乙"]

WOLONG_OUTER_PALACES = [4, 9, 2, 7, 6, 1, 8, 3] # Vòng xoay Bát Thần
WOLONG_FLYING_PATH = [5, 6, 7, 8, 9, 1, 2, 3, 4] # Vòng Lạc Thư Phi Bàn
WOLONG_NUM_TO_STEM = {1: "癸", 2: "丁", 3: "丙", 4: "乙", 5: "戊", 6: "己", 7: "庚", 8: "辛", 9: "壬", 0: "甲"}
WOLONG_ORIGINAL_GATES = {1: "休门", 8: "生门", 3: "伤门", 4: "杜门", 9: "景门", 2: "死门", 7: "惊门", 6: "开门"}
WOLONG_CLOCKWISE_GATES = ["景门", "死门", "惊门", "开门", "休门", "生门", "伤门", "杜门"]

ORIGINAL_STARS = {1: "天蓬", 2: "天芮", 3: "天冲", 4: "天辅", 5: "天禽", 6: "天心", 7: "天柱", 8: "天任", 9: "天英"}
DEITIES = ["值符", "螣蛇", "太阴", "六合", "勾陈", "朱雀", "九地", "九天"] # Dùng Câu Trần, Chu Tước

solar_term_ju = {
    "冬至":[1,7,4], "小寒":[2,8,5], "大寒":[3,9,6], "立春":[8,5,2], "雨水":[9,6,3], "惊蛰":[1,7,4],
    "春分":[3,9,6], "清明":[4,1,7], "谷雨":[5,2,8], "立夏":[4,1,7], "小满":[5,2,8], "芒种":[6,3,9],
    "夏至":[9,3,6], "小暑":[8,2,5], "大暑":[7,1,4], "立秋":[2,5,8], "处暑":[1,4,7], "白露":[9,3,6],
    "秋分":[7,1,4], "寒露":[6,9,3], "霜降":[5,8,2], "立冬":[6,9,3], "小雪":[5,8,2], "大雪":[4,7,1]
}
wolong_jq_order = ["大雪", "冬至", "小寒", "大寒", "立春", "雨水", "惊蛰", "春分", "清明", "谷雨", "立夏", "小满", "芒种", "夏至", "小暑", "大暑", "立秋", "处暑", "白露", "秋分", "寒露", "霜降", "立冬", "小雪"]

# TỪ ĐIỂN QUẺ DỊCH (Cho Trung Cung)
GATE_TO_TRIGRAM = {"休门": "地", "生门": "雷", "伤门": "火", "杜门": "泽", "景门": "天", "死门": "风", "惊门": "水", "开门": "山"}
TRIGRAM_BIN = {"地": [0,0,0], "山": [0,0,1], "水": [0,1,0], "风": [0,1,1], "雷": [1,0,0], "火": [1,0,1], "泽": [1,1,0], "天": [1,1,1]}
BIN_TO_TRIGRAM = {tuple(v): k for k, v in TRIGRAM_BIN.items()}
TRIGRAM_UNICODE = {"天": "☰", "泽": "☱", "火": "☲", "雷": "☳", "风": "☴", "水": "☵", "山": "☶", "地": "☷"}

EVAL_DICT = {
    "风": {"泽":"〇", "天":"△", "风":"✕", "火":"〇", "水":"△", "雷":"〇", "地":"✕", "山":"〇"},
    "天": {"泽":"✕", "天":"△", "风":"✕", "火":"〇", "水":"✕", "雷":"△", "地":"✕", "山":"✕"},
    "水": {"泽":"✕", "天":"✕", "风":"✕", "火":"〇", "水":"✕", "雷":"✕", "地":"〇", "山":"✕"},
    "泽": {"泽":"△", "天":"✕", "风":"✕", "火":"✕", "水":"✕", "雷":"✕", "地":"〇", "山":"〇"},
    "山": {"泽":"△", "天":"〇", "风":"✕", "火":"✕", "水":"✕", "雷":"〇", "地":"✕", "山":"✕"},
    "火": {"泽":"✕", "天":"〇", "风":"〇", "火":"✕", "水":"✕", "雷":"△", "地":"〇", "山":"✕"},
    "地": {"泽":"〇", "天":"〇", "风":"〇", "火":"✕", "水":"✕", "雷":"〇", "地":"△", "山":"△"},
    "雷": {"泽":"✕", "天":"△", "风":"〇", "火":"〇", "水":"〇", "雷":"△", "地":"〇", "山":"✕"}
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

# ==========================================
# 2. LOGIC LỊCH & QUẺ CHÂN TRUYỀN
# ==========================================
def calculate_correct_ju(nguyen, can_gio, chi_gio, tiet_khi):
    base_ju_dict = {"夏至":9,"小暑":7,"大暑":6,"立秋":5,"处暑":6,"白露":5,"秋分":4,"寒露":9,"霜降":8,"立冬":7,"小雪":2,"大雪":1,"冬至":1,"小寒":3,"大寒":4,"立春":5,"雨水":4,"惊蛰":5,"春分":6,"清明":1,"谷雨":2,"立夏":3,"小满":8,"芒种":9}
    yin_dun_terms = ["夏至", "小暑", "大暑", "立秋", "处暑", "白露", "秋分", "寒露", "霜降", "立冬", "小雪", "大雪"]
    dun_type = -1 if tiet_khi in yin_dun_terms else 1
    tuan_index = ((thien_can.index(can_gio) - dia_chi.index(chi_gio)) % 12) // 2
    nguyen_multiplier = 0 if nguyen == "上" else 1 if nguyen == "中" else 2
    raw_ju = base_ju_dict[tiet_khi] + (dun_type * (tuan_index + 6 * nguyen_multiplier))
    return (raw_ju - 1) % 9 + 1

def get_wushu_dun(day_stem, hour_branch):
    return thien_can[((thien_can.index(day_stem) % 5) * 2 + dia_chi.index(hour_branch)) % 10]

def get_xun_leader(can, chi):
    return {"子":"戊", "戌":"己", "申":"庚", "午":"辛", "辰":"壬", "寅":"癸"}[dia_chi[(dia_chi.index(chi) - thien_can.index(can)) % 12]]

def get_wolong_calendar_data(lunar_month, lunar_day):
    abs_day = ((lunar_month - 11) % 12) * 30 + (lunar_day - 1)
    wl_jieqi = wolong_jq_order[abs_day // 15 % 24]
    day_in_jq = abs_day % 15
    wl_yuan = "上" if day_in_jq < 5 else "中" if day_in_jq < 10 else "下"
    wl_dun = "阳遁" if 1 <= (abs_day // 15 % 24) <= 12 else "阴遁"
    return thien_can[(45 + abs_day) % 10], dia_chi[(45 + abs_day) % 12], wl_jieqi, wl_yuan, wl_dun

def get_hour_nine_star(day_branch, hour_branch, dun_type):
    hb_idx = dia_chi.index(hour_branch) 
    start_star = 1 if day_branch in ["子","午","卯","酉"] else (4 if day_branch in ["辰","戌","丑","未"] else 7)
    if dun_type == "阴遁": start_star = 7 if day_branch in ["辰","戌","丑","未"] else (4 if day_branch in ["寅","申","巳","亥"] else 1)
    res = (start_star + hb_idx) % 9 if dun_type == "阳遁" else (start_star - hb_idx) % 9
    return 9 if res == 0 else res

def calc_menh_cung(b_lunar_y, b_lunar_m):
    star_y = 11 - (sum(int(d) for d in str(b_lunar_y)) % 9 or 9)
    if star_y <= 0: star_y += 9
    b_y_branch = dia_chi[(b_lunar_y - 4) % 12]
    start_m = 8 if b_y_branch in ["子","午","卯","酉"] else (5 if b_y_branch in ["辰","戌","丑","未"] else 2)
    star_m = (start_m - (b_lunar_m - 1)) % 9 or 9
    yin_path = [5, 6, 7, 8, 9, 1, 2, 3, 4]
    for i in range(9):
        val = (star_y - i) % 9 or 9
        if val == star_m:
            mc = yin_path[i]
            if mc == 5:
                if b_lunar_m in [1, 2, 3]: return 6, True
                elif b_lunar_m in [4, 5, 6]: return 4, True
                elif b_lunar_m in [7, 8, 9]: return 8, True
                else: return 2, True
            return mc, False 
            
def tinh_tuan_khong_gio(hoa_giap):
    idx_tuan_dau = (dia_chi.index(hoa_giap[1]) - thien_can.index(hoa_giap[0])) % 12
    chi_to_cung = {"子":1, "丑":8, "寅":8, "卯":3, "辰":4, "巳":4, "午":9, "未":2, "申":2, "酉":7, "戌":6, "亥":6}
    return [chi_to_cung[dia_chi[(idx_tuan_dau - 2) % 12]], chi_to_cung[dia_chi[(idx_tuan_dau - 1) % 12]]]

# ==========================================
# 3. LẬP BÀN TOÁN HỌC (THẤU PHÁI / HOJO IKKOU)
# ==========================================
def lap_que_wolong(can_gio, chi_gio, dun_type, ju_num, chi_ngay, user_dt):
    cung_data = {i: {'dia': '', 'mon': '', 'thien': '', 'sao': '', 'than': '', 'hour_star': '', 'ngua': ''} for i in range(1, 10)}
    
    # 1. ĐỊA BÀN
    current_val = (10 - ju_num) if dun_type == "阳遁" else ju_num
    step_dir = 1 if dun_type == "阳遁" else -1
    dia_ban = {}
    for cung in WOLONG_FLYING_PATH:
        can = WOLONG_NUM_TO_STEM.get(current_val, "")
        dia_ban[cung] = can
        cung_data[cung]['dia'] = can
        current_val += step_dir
        if current_val > 9: current_val = 1
        elif current_val < 1: current_val = 9

    luc_nghi_gio = get_xun_leader(can_gio, chi_gio)
    p_circle = [c for c, can in dia_ban.items() if can == luc_nghi_gio][0] # Nơi chứa Tuần thủ Địa bàn
    p_hour_stem = [c for c, can in dia_ban.items() if can == can_gio][0]

    # MÃ CHI
    map_ngua = {"子":"寅", "丑":"亥", "寅":"申", "卯":"巳", "辰":"寅", "巳":"亥", "午":"申", "未":"巳", "申":"寅", "酉":"亥", "戌":"申", "亥":"巳"}
    cung_data[{"寅":8, "巳":4, "申":2, "亥":6}[map_ngua[chi_gio]]]['ngua'] = "马"

    # 2. THIÊN BÀN CAN (Phi Thuận)
    if p_circle == 5:
        for i in WOLONG_OUTER_PALACES: cung_data[i]['thien'] = dia_ban[i]
        if p_hour_stem != 5: cung_data[p_hour_stem]['thien'] = luc_nghi_gio
    else:
        idx_source = WOLONG_OUTER_PALACES.index(p_circle)
        idx_target = WOLONG_OUTER_PALACES.index(p_hour_stem) if p_hour_stem != 5 else idx_source
        offset = (idx_target - idx_source) % 8
        for i in range(8):
            cung_data[WOLONG_OUTER_PALACES[i]]['thien'] = dia_ban[WOLONG_OUTER_PALACES[(i - offset) % 8]]
    cung_data[5]['thien'] = dia_ban[5] if p_hour_stem == 5 else "" # Hiển thị Mậu/Kỷ ở 5 nếu cần

    # 3. BÁT MÔN (Nếu Cung 5 -> Phục Ngâm)
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

    # 4. CỬU TINH (Phi Thuận 1->9)
    luoshu_9 = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    idx_base_star = luoshu_9.index(p_circle)
    idx_target_star = luoshu_9.index(p_hour_stem)
    shift_for_star = (idx_target_star - idx_base_star) % 9
    for i in range(1, 10):
        idx_new = (luoshu_9.index(i) + shift_for_star) % 9
        cung_data[luoshu_9[idx_new]]['sao'] = ORIGINAL_STARS[i]
    cung_data[5]['sao'] = "" # Ẩn hiển thị sao trung cung

    # 5. BÁT THẦN (Neo Địa Bàn Tuần Thủ, Ký cung Âm 8 Dương 2)
    anchor_palace = p_circle
    if p_circle == 5:
        anchor_palace = 2 if dun_type == "阳遁" else 8
    idx_anchor = WOLONG_OUTER_PALACES.index(anchor_palace)
    for i in range(8):
        cung_data[WOLONG_OUTER_PALACES[(idx_anchor + i) % 8]]['than'] = DEITIES[i]
    cung_data[5]['than'] = ""

    # HOUR STAR
    curr_star = get_hour_nine_star(chi_ngay, chi_gio, dun_type)
    for cung in WOLONG_FLYING_PATH:
        cung_data[cung]['hour_star'] = curr_star
        curr_star = 1 if curr_star == 9 else curr_star + 1

    slot = (user_dt.minute // 20) + 1
    if user_dt.hour % 2 == 0: slot += 3
    
    return cung_data, p_circle, slot

# ==========================================
# 4. MODULE PHÂN TÍCH CÁCH CỤC (Cập nhật chuẩn Hojo Ikkou)
# ==========================================
def qimen_analyzer_hojo(cung_data, can_tuan, truc_su_door):
    FORMATION_RANKS = {
        "天遁": 1, "地遁": 1, "人遁": 1, "神遁": 1, "鬼遁": 1,
        "大格": 1, "小格": 1, "刑格": 1, "戦格": 1, "飛宮格": 1, "伏宮格": 1, 
        "青竜逃走": 1, "白虎猖狂": 1, "熒惑入白": 1, "太白入熒": 1, "朱雀投江": 1, "螣蛇妖嬌": 1,
        "青竜返首": 2, "飛鳥跌穴": 2, "玉女守門": 2, "乙奇得使": 2, "丙奇得使": 2, "丁奇得使": 2, 
        "竜遁": 2, "虎遁": 2, "風遁": 2, "雲遁": 2, 
        "乙奇入墓": 2, "丙奇入墓": 2, "丁奇入墓": 2,
        "干伏吟": 2, "干反吟": 2, 
        "乙奇昇殿": 3, "丙奇昇殿": 3, "丁奇昇殿": 3,
        "星門伏吟": 3, "星門反吟": 3, "八門受制": 3, "六儀撃刑": 3
    }
    
    cung_status = {i: [] for i in range(1, 10)}
    cung_3_elements = {i: [] for i in range(1, 10)} 

    # Dict Cát Hung
    than_cung_data = {'值符':{1:'吉',2:'吉',3:'吉',4:'吉',5:'凶',6:'吉',7:'吉',8:'吉',9:'吉'}, '螣蛇':{1:'凶',2:'凶',3:'凶',4:'凶',5:'凶',6:'凶',7:'凶',8:'凶',9:'凶'}, '太阴':{1:'吉',2:'吉',3:'吉',4:'吉',5:'凶',6:'吉',7:'吉',8:'吉',9:'吉'}, '六合':{1:'吉',2:'吉',3:'吉',4:'吉',5:'凶',6:'吉',7:'吉',8:'吉',9:'吉'}, '勾陈':{1:'凶',2:'凶',3:'凶',4:'凶',5:'凶',6:'凶',7:'凶',8:'凶',9:'凶'}, '朱雀':{1:'凶',2:'凶',3:'凶',4:'凶',5:'凶',6:'凶',7:'凶',8:'凶',9:'凶'}, '九地':{1:'吉',2:'吉',3:'吉',4:'吉',5:'凶',6:'吉',7:'吉',8:'吉',9:'吉'}, '九天':{1:'吉',2:'吉',3:'吉',4:'吉',5:'凶',6:'吉',7:'吉',8:'吉',9:'吉'}}
    mon_sao_data = {'休门':{'天蓬':'凶','天芮':'吉','天冲':'吉','天辅':'吉','天禽':'凶','天心':'吉','天柱':'吉','天任':'吉','天英':'凶'}, '生门':{'天蓬':'吉','天芮':'凶','天冲':'吉','天辅':'吉','天禽':'凶','天心':'吉','天柱':'吉','天任':'凶','天英':'吉'}, '伤门':{'天蓬':'凶','天芮':'凶','天冲':'凶','天辅':'凶','天禽':'凶','天心':'凶','天柱':'凶','天任':'凶','天英':'凶'}, '杜门':{'天蓬':'凶','天芮':'凶','天冲':'凶','天辅':'凶','天禽':'凶','天心':'凶','天柱':'凶','天任':'凶','天英':'凶'}, '景门':{'天蓬':'凶','天芮':'吉','天冲':'吉','天辅':'吉','天禽':'凶','天心':'吉','天柱':'吉','天任':'吉','天英':'凶'}, '死门':{'天蓬':'凶','天芮':'凶','天冲':'凶','天辅':'凶','天禽':'凶','天心':'凶','天柱':'凶','天任':'凶','天英':'凶'}, '惊门':{'天蓬':'凶','天芮':'凶','天冲':'凶','天辅':'凶','天禽':'凶','天心':'凶','天柱':'凶','天任':'凶','天英':'凶'}, '开门':{'天蓬':'吉','天芮':'吉','天冲':'吉','天辅':'凶','天禽':'凶','天心':'凶','天柱':'吉','天任':'吉','天英':'吉'}}
    can_can_data = {'甲':{'甲':'吉','乙':'吉','丙':'吉','丁':'吉','戊':'凶','己':'吉','庚':'大凶','辛':'凶','壬':'凶','癸':'吉'}, '乙':{'甲':'吉','乙':'凶','丙':'吉','丁':'吉','戊':'吉','己':'吉','庚':'凶','辛':'大凶','壬':'吉','癸':'凶'}, '丙':{'甲':'吉','乙':'吉','丙':'凶','丁':'吉','戊':'吉','己':'吉','庚':'大凶','辛':'吉','壬':'吉','癸':'凶'}, '丁':{'甲':'吉','乙':'吉','丙':'吉','丁':'吉','戊':'吉','己':'凶','庚':'吉','辛':'凶','壬':'吉','癸':'大凶'}, '戊':{'甲':'凶','乙':'吉','丙':'吉','丁':'吉','戊':'凶','己':'凶','庚':'凶','辛':'凶','壬':'吉','癸':'凶'}, '己':{'甲':'凶','乙':'吉','丙':'凶','丁':'凶','戊':'吉','己':'凶','庚':'凶','辛':'凶','壬':'凶','癸':'凶'}, '庚':{'甲':'大凶','乙':'凶','丙':'大凶','丁':'吉','戊':'凶','己':'大凶','庚':'大凶','辛':'凶','壬':'大凶','癸':'大凶'}, '辛':{'甲':'凶','乙':'大凶','丙':'凶','丁':'吉','戊':'凶','己':'凶','庚':'凶','辛':'凶','壬':'凶','癸':'凶'}, '壬':{'甲':'凶','乙':'凶','丙':'凶','丁':'吉','戊':'吉','己':'凶','庚':'凶','辛':'吉','壬':'凶','癸':'凶'}, '癸':{'甲':'吉','乙':'凶','丙':'吉','丁':'大凶','戊':'吉','己':'凶','庚':'大凶','辛':'凶','壬':'凶','癸':'凶'}}

    # Hàm quy đổi Giáp
    def get_actual(can): return '甲' if can == can_tuan else can

    for p, d in cung_data.items():
        if p == 5: continue 
        
        # Lấy Can thực để in ra UI
        raw_t = d['thien']
        raw_d = d['dia']
        if not raw_t or not raw_d: continue

        # Quy đổi thành Giáp để Tra Cứu
        t_can = get_actual(raw_t)
        d_can = get_actual(raw_d)
        
        mon, sao, than, phi_tinh = d['mon'], d['sao'], d['than'], d['hour_star']

        # 1. CÁC CÁCH CỤC CÁT
        if t_can == '甲' and d_can == '丙': cung_status[p].append(("青竜返首", "#CC0000"))
        if t_can == '丙' and d_can == '甲': cung_status[p].append(("飛鳥跌穴", "#CC0000"))
        if truc_su_door and t_can == '丁' and mon == truc_su_door: cung_status[p].append(("玉女守門", "#CC0000"))
        
        if t_can == '乙' and p == 3: cung_status[p].append(("乙奇昇殿", "#CC0000"))
        if t_can == '丙' and p == 9: cung_status[p].append(("丙奇昇殿", "#CC0000"))
        if t_can == '丁' and p == 7: cung_status[p].append(("丁奇昇殿", "#CC0000")) # Đinh vào Tây 7
        
        if t_can == '乙' and d_can == '己': cung_status[p].append(("乙奇得使", "#CC0000"))
        if t_can == '丙' and d_can == '戊': cung_status[p].append(("丙奇得使", "#CC0000"))
        if t_can == '丁' and d_can == '壬': cung_status[p].append(("丁奇得使", "#CC0000"))
        
        if t_can == '丙' and d_can == '戊' and mon == "生门": cung_status[p].append(("天遁", "#CC0000"))
        if t_can == '乙' and d_can == '己' and mon == "开门": cung_status[p].append(("地遁", "#CC0000"))
        if t_can == '丁' and mon == "休门" and than == "太阴": cung_status[p].append(("人遁", "#CC0000"))
        if t_can == '丙' and mon == "生门" and than == "九天": cung_status[p].append(("神遁", "#CC0000"))
        if t_can == '丁' and mon == "开门" and than == "九地": cung_status[p].append(("鬼遁", "#CC0000"))
        if (t_can == '乙' and mon == "开门") or (t_can == '乙' and p == 6 and mon in ["休门", "生门"]): cung_status[p].append(("竜遁", "#CC0000"))
        if (t_can == '乙' and mon == "生门") or (t_can == '乙' and p == 8 and mon in ["休门", "开门"]): cung_status[p].append(("虎遁", "#CC0000"))
        if t_can == '乙' and p == 4 and mon in ["休门", "生门", "开门"]: cung_status[p].append(("風遁", "#CC0000"))
        if t_can == '乙' and p == 2 and mon in ["休门", "生门", "开门"]: cung_status[p].append(("雲遁", "#CC0000"))

        # 2. CÁC CÁCH CỤC HUNG
        if (t_can == '己' and p == 2) or (t_can == '辛' and p == 9) or (t_can == '壬' and p == 4) or (t_can == '癸' and p == 4) or (t_can == '戊' and p == 3) or (t_can == '庚' and p == 8): 
            cung_status[p].append(("六儀撃刑", "#000000"))
            
        if t_can == '乙' and p == 2: cung_status[p].append(("乙奇入墓", "#000000"))
        if t_can == '丙' and p == 6: cung_status[p].append(("丙奇入墓", "#000000"))
        if t_can == '丁' and p == 6: cung_status[p].append(("丁奇入墓", "#000000"))
        
        if t_can == '庚' and d_can == '癸': cung_status[p].append(("大格", "#000000"))
        if t_can == '庚' and d_can == '壬': cung_status[p].append(("小格", "#000000"))
        if t_can == '庚' and d_can == '己': cung_status[p].append(("刑格", "#000000"))
        if t_can == '庚' and d_can == '庚': cung_status[p].append(("戦格", "#000000"))
        
        if t_can == '庚' and d_can == '甲': cung_status[p].append(("伏宮格", "#000000"))
        if t_can == '甲' and d_can == '庚': cung_status[p].append(("飛宮格", "#000000"))
        
        if t_can == '乙' and d_can == '辛': cung_status[p].append(("青竜逃走", "#000000"))
        if t_can == '辛' and d_can == '乙': cung_status[p].append(("白虎猖狂", "#000000"))
        if t_can == '丙' and d_can == '庚': cung_status[p].append(("熒惑入白", "#000000"))
        if t_can == '庚' and d_can == '丙': cung_status[p].append(("太白入熒", "#000000"))
        if t_can == '丁' and d_can == '癸': cung_status[p].append(("朱雀投江", "#000000"))
        if t_can == '癸' and d_can == '丁': cung_status[p].append(("螣蛇妖嬌", "#000000"))

        # Bát Môn Thụ Chế (4 trường hợp chuẩn)
        if (mon == "休门" and p == 9) or (mon == "景门" and p == 7) or (mon == "生门" and p == 1) or (mon == "开门" and p == 3):
            cung_status[p].append(("八門受制", "#000000"))

        # Can Phục Ngâm / Phản Ngâm (Định nghĩa mới)
        if t_can == d_can and t_can not in ['甲', '丁']: cung_status[p].append(("干伏吟", "#000000"))
        if (t_can, d_can) in [('戊','辛'), ('辛','戊'), ('己','壬'), ('壬','己'), ('庚','癸'), ('癸','庚')]:
            cung_status[p].append(("干反吟", "#000000"))

        # Tinh Môn Phục Ngâm / Phản Ngâm (Xét trên từng cặp Cung)
        sao_mon_goc = {"天蓬":"休门", "天芮":"死门", "天冲":"伤门", "天辅":"杜门", "天心":"开门", "天柱":"惊门", "天任":"生门", "天英":"景门"}
        mon_doi_xung = {"休门":"景门", "死门":"生门", "伤门":"惊门", "杜门":"开门", "开门":"杜门", "惊门":"伤门", "生门":"死门", "景门":"休门"}
        
        if sao in sao_mon_goc:
            if mon == sao_mon_goc[sao]: cung_status[p].append(("星門伏吟", "#000000"))
            elif mon == mon_doi_xung[sao_mon_goc[sao]]: cung_status[p].append(("星門反吟", "#000000"))

        # 3. TRA 3 YẾU TỐ GÓC PHẢI (Có dùng Giáp)
        if t_can in can_can_data and d_can in can_can_data[t_can]: cung_3_elements[p].append(can_can_data[t_can][d_can])
        if mon in mon_sao_data and sao in mon_sao_data[mon]: cung_3_elements[p].append(mon_sao_data[mon][sao])
        if than in than_cung_data and phi_tinh in than_cung_data[than]: cung_3_elements[p].append(than_cung_data[than][phi_tinh])

    # Sắp xếp theo Rank
    for p in cung_status:
        cung_status[p].sort(key=lambda x: FORMATION_RANKS.get(x[0], 99))
        formatted_list = []
        for raw_name, color in cung_status[p]:
            rank = FORMATION_RANKS.get(raw_name)
            if rank: display_name = f"<span style='font-size: 0.8em; font-weight: normal; color: #666;'>({rank})</span> {raw_name}"
            else: display_name = raw_name
            formatted_list.append((display_name, color))
        cung_status[p] = formatted_list

    return cung_status, cung_3_elements

# ==========================================
# 5. GIAO DIỆN HTML RENDER (Kết hợp Quẻ Dịch & Grid Mới)
# ==========================================
def render_html_table(cung_data, tk_gio, menh_cung, p_circle, hao_dong, cung_status, cung_3_elements):
    # Xử lý Quẻ Dịch ở Trung Cung
    upper_gate = cung_data[menh_cung]['mon'] if cung_data[menh_cung]['mon'] else "休门"
    lower_gate = cung_data[p_circle]['mon'] if cung_data[p_circle]['mon'] else "生门"
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
        .qmdj-table { border-collapse: collapse; width: 100%; max-width: 510px; min-width: 400px; height: 430px; table-layout: fixed; font-family: sans-serif; margin: 0 auto; background: #fff;}
        .qmdj-td { border: 1px solid #aaa; width: 33.33%; position: relative; vertical-align: top; padding: 10px; }
        .cell-main {
            display: grid; grid-template-columns: auto auto 1fr; grid-template-rows: 22px 22px 22px;   
            column-gap: 15px; row-gap: 6px; height: 100%; min-height: 85px; align-content: start; margin-top: 5px; margin-left: 5px; 
        }
        .item-than  { grid-column: 1 / span 2; grid-row: 1; font-size: 15px; color: #222; text-align: left; }
        .item-tinh  { grid-column: 1; grid-row: 2; font-size: 15px; color: #222; text-align: left; }
        .item-mon   { grid-column: 1; grid-row: 3; font-size: 15px; color: #222; text-align: left; }
        .item-thien { grid-column: 2; grid-row: 2; font-size: 16px; color: #b30000; text-align: left; font-weight: bold;}
        .item-dia   { grid-column: 2; grid-row: 3; font-size: 16px; color: #b30000; text-align: left; font-weight: bold;}
        .top-right-indicators { position: absolute; top: 3px; right: 4px; display: flex; flex-direction: row; gap: 4px; color: #444; }
        .horse-icon { font-size: 14px; font-weight: bold; }
        .void-icon { font-size: 20px; font-weight: normal; line-height: 0.8; margin-top: -2px; }
        .bottom-left-phitinh { position: absolute; bottom: 3px; left: 5px; font-size: 15px; color: #555; font-weight: bold; }
        .right-panel { position: absolute; right: 5px; top: 22px; display: flex; flex-direction: column; align-items: flex-end; text-align: right; font-size: 11px;}
        .bottom-right-panel { position: absolute; right: 5px; bottom: 3px; display: flex; flex-direction: column; align-items: flex-end; text-align: right; font-size: 11px;}
        .combo-item { color: #555; font-weight: 500; margin-bottom: 2px; }
        .formation-item { margin-top: 1px; font-weight: bold; letter-spacing: 1px; color: #000; }
    </style>
    <table class="qmdj-table">
    """

    for row in luoi_lac_thu:
        html += "<tr>"
        for p in row:
            d = cung_data[p]
            phi_tinh_html = f"<div class='bottom-left-phitinh'>{d['hour_star']}</div>"
            bg_color = "#fff3cd" if p == menh_cung else "transparent"
            
            if p == 5:
                html += f"""
                <td class="qmdj-td" style="background-color: {bg_color}; text-align: center;">
                    {phi_tinh_html} 
                    <div style="display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100%;">
                        {hex_html}
                    </div>
                    <div style="position: absolute; bottom: 6px; right: 6px; font-size: 18px; font-weight: bold; color: #b30000;">{d['dia']}</div>
                </td>"""
            else:
                indicators = []
                if d.get('ngua'): indicators.append("<span class='horse-icon'>马</span>")
                if p in tk_gio: indicators.append("<span class='void-icon'>○</span>")
                indicator_html = f"<div class='top-right-indicators'>{''.join(indicators)}</div>" if indicators else ""
                
                combos_html = "".join([f"<div class='combo-item'>{c}</div>" for c in cung_3_elements[p]])
                form_html = "".join([f"<div class='formation-item' style='color:{f_color};'>{f_name}</div>" for f_name, f_color in cung_status[p]])
                right_panel_html = f"<div class='right-panel'>{combos_html}</div>"
                bottom_right_html = f"<div class='bottom-right-panel'>{form_html}</div>"
                
                html += f"""
                <td class="qmdj-td" style="background-color: {bg_color};">
                    {indicator_html}
                    {phi_tinh_html}
                    {right_panel_html}
                    {bottom_right_html}
                    <div class="cell-main">
                        <div class="item-than">{d['than']}</div>
                        <div class="item-tinh">{d['sao']}</div>
                        <div class="item-mon"><span>{d['mon']}</span></div>
                        <div class="item-thien">{d['thien']}</div>
                        <div class="item-dia">{d['dia']}</div>
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

col1, col2, col3, col4, col5, col6 = st.columns([1.1, 0.8, 0.8, 1.2, 0.7, 0.7])
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

wl_ju = calculate_correct_ju(wl_yuan, can_gio, chi_gio, wl_jieqi)

# Tính Mệnh Cung
b_dt = datetime.combine(birth_date, datetime.min.time()).replace(hour=birth_hour, minute=birth_minute)
b_actual_date = b_dt.date() + timedelta(days=1) if b_dt.hour >= 23 else b_dt.date()
b_day_obj = sxtwl.fromSolar(b_actual_date.year, b_actual_date.month, b_actual_date.day)
menh_cung, _ = calc_menh_cung(b_day_obj.getLunarYear(), b_day_obj.getLunarMonth()) 

# TÍNH TOÁN BÀN LÕI
data, p_circle, hao_dong = lap_que_wolong(can_gio, chi_gio, wl_dun, wl_ju, wl_chi, user_dt)

# XỬ LÝ CÁCH CỤC
can_tuan = get_xun_leader(can_gio, chi_gio)
truc_su_door = data[p_circle]['mon'] # Cửa gốc của Cung Địa Bàn chứa Tuần Thủ
cung_st, cung_3_el = qimen_analyzer_hojo(data, can_tuan, truc_su_door)
tk_gio = tinh_tuan_khong_gio(hoa_giap_hien_tai)

bazi_chuoi = f"农历 {lunar_m}月 {lunar_d}日 | {wl_can}{wl_chi} | {wl_jieqi} {wl_yuan}元"
title = f"<h3 style='margin-bottom:8px; font-family:sans-serif; color: #1a1a1a; font-weight: normal; font-size: 18px; text-align: center;'>{bazi_chuoi}</h3>"
sub_title = f"<h4 style='margin-top:0px; margin-bottom:15px; font-family:sans-serif; color: #555; font-weight: normal; font-size: 16px; text-align: center;'>{hoa_giap_hien_tai}时 | {wl_dun}{wl_ju}局</h4>"
qimen_board_html = render_html_table(data, tk_gio, menh_cung, p_circle, hao_dong, cung_st, cung_3_el)

combined_html = f"""<div style="display: flex; flex-direction: column; align-items: center; width: 100%; padding-top: 10px;"><div style="display: flex; flex-direction: column; align-items: center; width: 100%; max-width: 510px;">{title}{sub_title}{qimen_board_html}</div></div>"""
st.components.v1.html(combined_html, height=550, scrolling=True)


# ==========================================
# 7. MODULE SCAN: DỤNG SỰ (TÌM KIẾM)
# ==========================================
st.markdown("---")
st.markdown("<h3 style='text-align: center; color: #333; font-family: sans-serif; margin-bottom: 20px;'>DỤNG SỰ</h3>", unsafe_allow_html=True)

huong_list = {"": None, "坎 (337.5 - 22.5)": 1, "艮 (22.5 - 67.5)": 8, "震 (67.5 - 112.5)": 3, "巽 (112.5 - 157.5)": 4, "離 (157.5 - 202.5)": 9, "坤 (202.5 - 247.5)": 2, "兌 (247.5 - 292.5)": 7, "乾 (292.5 - 337.5)": 6}
can_list = ["", "甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
mon_list = ["", "休门", "生门", "伤门", "杜门", "景门", "死门", "惊门", "开门"]
tinh_list = ["", "天蓬", "天芮", "天冲", "天辅", "天禽", "天心", "天柱", "天任", "天英"]
than_list = ["", "值符", "螣蛇", "太阴", "六合", "勾陈", "朱雀", "九地", "九天"]
cat_cach_list = ["", "青竜返首", "飛鳥跌穴", "玉女守門", "乙奇昇殿", "丙奇昇殿", "丁奇昇殿", "乙奇得使", "丙奇得使", "丁奇得使", "天遁", "地遁", "人遁", "神遁", "鬼遁", "竜遁", "虎遁", "風遁", "雲遁"]

with st.container():
    c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
    loc_huong = c1.selectbox("方向 (Hướng)", options=list(huong_list.keys()))
    loc_thien_can = c2.selectbox("天盤 (Thiên Bàn)", options=can_list)
    loc_dia_can = c3.selectbox("地盤 (Địa Bàn)", options=can_list)
    loc_mon = c4.selectbox("八門 (Bát Môn)", options=mon_list)
    loc_tinh = c5.selectbox("九星 (Cửu Tinh)", options=tinh_list)
    loc_than = c6.selectbox("九神 (Cửu Thần)", options=than_list)
    loc_cat_cach = c7.selectbox("吉格 (Cát Cách)", options=cat_cach_list)

if st.button("TÌM KIẾM", use_container_width=True):
    with st.spinner('Đang quét dữ liệu tương lai...'):
        results_normal = []
        current_scan_dt = user_dt.replace(minute=0, second=0, microsecond=0)
        loops = 0
        
        while loops < 4320: # Quét giới hạn
            if len(results_normal) >= 10: break
            loops += 1
            current_scan_dt += timedelta(hours=2)
            
            s_date = current_scan_dt.date() + timedelta(days=1) if current_scan_dt.hour >= 23 else current_scan_dt.date()
            c_gio_idx = 0 if current_scan_dt.hour >= 23 else (current_scan_dt.hour + 1) // 2 % 12
            c_gio_scan = dia_chi[c_gio_idx]
            
            s_obj = sxtwl.fromSolar(s_date.year, s_date.month, s_date.day)
            lm_scan = s_obj.getLunarMonth()
            ld_scan = s_obj.getLunarDay()
            
            wl_can_s, wl_chi_s, wl_jieqi_s, wl_yuan_s, wl_dun_s = get_wolong_calendar_data(lm_scan, ld_scan)
            can_gio_scan = get_wushu_dun(wl_can_s, c_gio_scan)
            wl_ju_s = calculate_correct_ju(wl_yuan_s, can_gio_scan, c_gio_scan, wl_jieqi_s)
            
            scan_data, p_circle_scan, _ = lap_que_wolong(can_gio_scan, c_gio_scan, wl_dun_s, wl_ju_s, wl_chi_s, current_scan_dt)
            
            can_tuan_scan = get_xun_leader(can_gio_scan, c_gio_scan)
            ts_door_scan = scan_data[p_circle_scan]['mon']
            cung_st_scan, _ = qimen_analyzer_hojo(scan_data, can_tuan_scan, ts_door_scan)
            
            end_scan_dt = current_scan_dt + timedelta(hours=1, minutes=59)
            time_str = f"{current_scan_dt.strftime('%d/%m %H:%M')} - {end_scan_dt.strftime('%H:%M')}"
            
            is_match = False
            target_palace = huong_list[loc_huong]
            
            # Helper tra cứu Giáp trong Scanner
            def check_match(p):
                d = scan_data[p]
                t_chk = '甲' if d['thien'] == can_tuan_scan else d['thien']
                d_chk = '甲' if d['dia'] == can_tuan_scan else d['dia']
                
                if loc_thien_can and t_chk != loc_thien_can: return False
                if loc_dia_can and d_chk != loc_dia_can: return False
                if loc_mon and d['mon'] != loc_mon: return False
                if loc_tinh and d['sao'] != loc_tinh: return False
                if loc_than and d['than'] != loc_than: return False
                if loc_cat_cach:
                    if not any(loc_cat_cach in item[0] for item in cung_st_scan[p]): return False
                return True

            if target_palace:
                if target_palace != 5:
                    is_match = check_match(target_palace)
            else:
                for p in range(1, 10):
                    if p == 5: continue
                    if check_match(p):
                        is_match = True
                        target_palace = p
                        break
                        
            if is_match:
                ten_cung = [k for k, v in huong_list.items() if v == target_palace][0]
                results_normal.append((time_str, f"{wl_dun_s} {wl_ju_s}局 | Giờ {can_gio_scan}{c_gio_scan}", ten_cung))

        if results_normal:
            st.success(f"**TÌM THẤY {len(results_normal)} KẾT QUẢ:**")
            for idx, (t_str, c_str, cung_str) in enumerate(results_normal):
                h_text = f" | Hướng: {cung_str}" if cung_str else ""
                st.write(f"{idx+1}. {t_str} | {c_str}{h_text}")
        else:
            st.warning("Không tìm thấy thời điểm nào thỏa mãn điều kiện.")
