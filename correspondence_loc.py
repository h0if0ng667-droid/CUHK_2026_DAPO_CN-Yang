import json
import re
from collections import defaultdict

def generate_loc_array(input_json_path):
    with open(input_json_path, 'r', encoding='utf-8') as f:
        records = json.load(f)

    loc_groups = defaultdict(list)
    for rec in records:
        lat = rec.get('latitude')
        lon = rec.get('longitude')
        if lat is None or lon is None:
            continue          # 跳过没有坐标的记录
        key = (round(lat, 4), round(lon, 4))
        loc_groups[key].append(rec)

    locs = []
    for (lat, lon), group in loc_groups.items():
        institutions = set()
        country = group[0].get('country', 'Unknown')
        desc_list = []

        for rec in group:
            inst = rec.get('institution', '')
            if inst:
                institutions.add(inst)

            person = rec.get('person', '')
            title = rec.get('title', '')
            year = rec.get('year')
            desc = f"{person} - {title}" + (f" ({year})" if year else "")
            desc_list.append(desc)

        # 去重描述（同一封信可能多人）
        desc_list = list(set(desc_list))
        # 按年份排序
        def extract_year(d):
            m = re.search(r'\((\d{4})\)$', d)
            return int(m.group(1)) if m else 9999
        desc_list.sort(key=extract_year)

        loc_obj = {
            "name": " / ".join(sorted(institutions)) if institutions else "Unknown",
            "lat": lat,
            "lon": lon,
            "country": country,
            "count": len(desc_list),
            "desc": desc_list
        }
        locs.append(loc_obj)

    locs.sort(key=lambda x: (x['country'], x['name']))
    return locs

if __name__ == '__main__':
    locs_array = generate_loc_array(r"C:\Users\D3NG_\Desktop\DAPO2026\letters_geocoded_updated.json")
    # 输出为格式化的 JavaScript 数组字符串
    print(json.dumps(locs_array, indent=2, ensure_ascii=False))