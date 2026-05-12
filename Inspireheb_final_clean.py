import pandas as pd
import re

# ============================================================
# 1. 作者国籍数据库（基于公开学术资料手工整理）
#    格式：出生国/主要工作国（如有双重国籍）
# ============================================================

NATIONALITY_DB = {
    # ===== 杨振宁本人（多种拼写变体）=====
    'yang, chen ning':   'China/USA',
    'yang, chen-ning':   'China/USA',
    'yang, c.n.':        'China/USA',

    # ===== 杨振平（杨振宁之弟）=====
    'yang, c.p.':        'China',
    'yang, chen ping':   'China',
    'yang, chen-ping':   'China',

    # ===== 长期合作者 =====
    'chou, t.t.':        'China/USA',       # 仇松柏，Georgia Tech
    'lee, t.d.':         'China/USA',       # 李政道
    'wu, tai tsun':      'China/USA',       # 吴大峻
    'wu, tai-tsun':      'China/USA',
    'wu, t.t.':          'China/USA',
    'wu, a.c.t.':        'China/USA',       # 吴爱慈
    'wu, c.s.':          'China/USA',       # 吴健雄
    'nieh, h.t.':        'China/USA',       # 聂华桐
    'nieh, hwa-tung':    'China/USA',
    'mills, robert l.':  'USA',             # Robert Mills
    'mills, r.l.':       'USA',

    # ===== 中国合作者 =====
    'ge, mo-lin':        'China',           # 葛墨林
    'he, yang-hui':      'China/UK',        # 何杨辉
    'you, yi-zhuang':    'China',           # 尤亦庄
    'gu, chao-hao':      'China',           # 谷超豪
    'hu, he-sheng':      'China',           # 胡和生
    'li, da-qian':       'China',           # 李大潜
    'shen, chun-li':     'China',           # 沈纯理
    'xin, yuan-long':    'China',           # 忻元龙
    'wang, ling-lie':    'China',           # 王令隽
    'tu, tung-sheng':    'China',           # 屠东升
    'dong, shao-jing':   'China',           # 董绍静
    'zhou, x.w.':        'China',
    'chan, y.w.':         'China',
    'leung, a.f.':       'China',
    'young, k.':         'China',           # 杨纲凯 (Hong Kong)
    'wang, j.m.':        'China/USA',

    # ===== 华裔美国物理学家 =====
    'chao, alexander w.':  'China/USA',     # 赵午
    'chao, alexander wu':  'China/USA',
    'chao, a.w.':          'China/USA',
    'huang, kerson':       'China/USA',     # 黄克孙
    'yen, e.':             'China/USA',

    # ===== 日本 =====
    'kazama, yoichi':    'Japan',           # 风间洋一

    # ===== 韩国 =====
    'cho, y.m.':         'South Korea',
    'hong, j.b.':        'South Korea',
    'lee, b.w.':         'South Korea/USA', # 李辉昭 (Benjamin Lee)

    # ===== 美国 =====
    'goldhaber, alfred s.': 'USA',
    'goldhaber, m.':     'USA',             # Maurice Goldhaber (生于奥地利)
    'good, m.l.':        'USA',
    'quigg, c.':         'USA',             # Chris Quigg
    'byers, n.':         'USA',             # Nina Byers
    'treiman, s.b.':     'USA',             # Sam Treiman
    'oakes, r.j.':       'USA',
    'sutherland, b.':    'USA',             # Bill Sutherland
    'bernstein, j.':     'USA',             # Jeremy Bernstein
    'primakoff, h.':     'USA',             # Henry Primakoff
    'markstein, p.':     'USA',
    'snow, g.a.':        'USA',
    'sternheimer, r.m.': 'USA',
    'feldman, d.':       'USA',
    'rosenbluth, m.':    'USA',             # Marshall Rosenbluth
    'luttinger, j.m.':   'USA',
    'chew, geoffrey f.': 'USA',
    'goldberger, m.l.':  'USA',
    'case, k.m.':        'USA',
    'feinberg, g.':      'USA',
    'schwinger, j.':     'USA',
    'low, f.':           'USA',             # Francis Low
    'serber, r.':        'USA',
    'feynman, r.p.':     'USA',
    'oppenheimer, j.r.': 'USA',
    'marshak, r.e.':     'USA',
    'gell-mann, m.':     'USA',
    'schwartz, m.':      'USA',             # Melvin Schwartz
    'lederman, l.m.':    'USA',
    'barkas, w.h.':      'USA',
    'pless, i.':         'USA',
    'shutt, r.p.':       'USA',
    'walker, w.d.':      'USA',
    'williams, r.w.':    'USA',
    'osborne, l.s.':     'USA',
    'collins, g.b.':     'USA',
    'wright, w.e.':      'USA',
    'kaplon, m.f.':      'USA',
    'fry, w.f.':         'USA',
    'galonsky, a.':      'USA',
    'terwilliger, k.m.': 'USA',
    'ross, m.h.':        'USA',

    # ===== 欧洲出生、后移居美国 =====
    'fermi, e.':         'Italy/USA',       # Enrico Fermi
    'steinberger, j.':   'Germany/USA',     # Jack Steinberger
    'steinberger, j.h.': 'Germany/USA',
    'oehme, r.':         'Germany/USA',     # Reinhard Oehme
    'karplus, robert':   'Austria/USA',     # Robert Karplus
    'dresden, max':      'Netherlands/USA',
    'wigner, eugene p.': 'Hungary/USA',
    'breit, g.':         'Russia/USA',      # Gregory Breit
    'frauenfelder, h.':  'Switzerland/USA',
    'wentzel, c.':       'Germany/USA',     # Gregor Wentzel

    # ===== 欧洲 =====
    'dirac, paul a.m.':  'UK',
    'peierls, r.e.':     'Germany/UK',
    'skinner, h.w.b.':   'UK',
    'dalitz, r.h.':      'Australia/UK',
    'zichichi, a.':      'Italy',
    'ferrara, s.':       'Italy',
    'piccioni, o.':      'Italy/USA',
    'kleinert, h.':      'Germany',
    'martin, andre':     'France',
    "d'espagnat, b.":    'France',
    'benecke, j.':       'Germany',

    # ===== 其他 =====
    'tiomno, j.':        'Brazil',          # Jayme Tiomno
    'kabir, p.k.':       'India',           # P.K. Kabir
    'markov, m.a.':      'Russia',          # Moisei Markov
    'salam':             'Pakistan',        # Abdus Salam

    # ===== 不确定 =====
    'abbud, f.':         'Unknown',
    'leavitt':           'Unknown',
    'powell':            'UK',              # 可能是 C.F. Powell
    'sands':             'USA',
    'klein':             'Sweden',          # 可能是 Oskar Klein
    'fierz':             'Switzerland',     # Markus Fierz
}


# ============================================================
# 2. 名字匹配函数
# ============================================================

def normalize_name(name):
    """标准化作者名字"""
    name = name.strip().lower()
    name = re.sub(r'\s+', ' ', name)
    return name


def lookup_nationality(author_name):
    """查找作者国籍，支持模糊匹配"""
    norm = normalize_name(author_name)

    # 1) 精确匹配
    if norm in NATIONALITY_DB:
        return NATIONALITY_DB[norm]

    # 2) 按 "姓, 名首字母" 模糊匹配
    parts = norm.split(',', 1)
    if len(parts) == 2:
        last = parts[0].strip()
        first = parts[1].strip()
        if first:
            prefix = f"{last}, {first[0]}"
            for key, val in NATIONALITY_DB.items():
                if key.startswith(prefix):
                    return val

    # 3) 仅按姓匹配（可能不准确，标注来源）
    if len(parts) >= 1:
        last = parts[0].strip()
        for key, val in NATIONALITY_DB.items():
            if key.startswith(last + ','):
                return val + ' (?)'

    return 'Unknown'


# ============================================================
# 3. 主处理流程
# ============================================================

def process_csv(input_file="C:\\Users\\D3NG_\\Desktop\\yang_cn_inspire.csv",
                output_file='yang_cn_cleaned.csv'):
    
    df = pd.read_csv(input_file)
    print(f"读取 {len(df)} 条记录")

    # 提取 title 和 authors
    df_out = df[['title', 'authors']].copy()

    # --- 为每篇文章的每位作者标注国籍 ---
    def annotate_nationalities(authors_str):
        """返回格式: 'Author1 (国籍); Author2 (国籍); ...' """
        if pd.isna(authors_str) or authors_str.strip() == '':
            return ''
        
        authors = [a.strip() for a in authors_str.split(';')]
        results = []
        for author in authors:
            if not author or '(+' in author:  # 跳过 "... (+3 more)"
                results.append(author)
                continue
            nat = lookup_nationality(author)
            results.append(f"{author} ({nat})")
        return '; '.join(results)

    # --- 仅列出涉及的国家（去重）---
    def get_countries(authors_str):
        """返回该论文涉及的所有国家（去重）"""
        if pd.isna(authors_str) or authors_str.strip() == '':
            return ''
        
        authors = [a.strip() for a in authors_str.split(';')]
        countries = set()
        for author in authors:
            if not author or '(+' in author:
                continue
            nat = lookup_nationality(author)
            if nat != 'Unknown':
                # "China/USA" → 拆成 China, USA
                for c in nat.replace(' (?)', '').split('/'):
                    countries.add(c.strip())
        return ', '.join(sorted(countries))

    # 新增两列
    df_out['author_nationalities'] = df_out['authors'].apply(annotate_nationalities)
    df_out['countries_involved'] = df_out['authors'].apply(get_countries)

    # 保存
    df_out.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"✅ 已保存到 {output_file}")
    print(f"   列: {list(df_out.columns)}")

    # --- 统计 Unknown 的作者 ---
    all_unknowns = set()
    for authors_str in df['authors'].dropna():
        for author in authors_str.split(';'):
            author = author.strip()
            if author and '(+' not in author:
                if lookup_nationality(author) == 'Unknown':
                    all_unknowns.add(author)
    
    if all_unknowns:
        print(f"\n⚠️  以下 {len(all_unknowns)} 位作者国籍未知，需手动补充：")
        for name in sorted(all_unknowns):
            print(f"   - {name}")

    return df_out


# ============================================================
# 4. 运行
# ============================================================
if __name__ == '__main__':
    df_result = process_csv()
    
    # 展示前 10 行
    print("\n" + "=" * 80)
    print("前 10 条记录预览：")
    print("=" * 80)
    for i, row in df_result.head(10).iterrows():
        print(f"\n[{i+1}] {row['title'][:70]}...")
        print(f"    Authors: {row['authors']}")
        print(f"    Nationalities: {row['author_nationalities']}")
        print(f"    Countries: {row['countries_involved']}")