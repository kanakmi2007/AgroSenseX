import re

for t in ['dashboard.html', 'soil_dashboard.html']:
    with open(f'templates/{t}', encoding='utf-8') as f:
        content = f.read()
    scripts = re.findall(r'<script(?:\s+[^>]*)?>(.*?)</script>', content, re.DOTALL)
    print(f"\n================ {t} ================")
    for idx, s in enumerate(scripts):
        # find jinja expressions
        jinja_tags = re.findall(r'(\{\{.*?\}\}|\{%.*?%\})', s)
        print(f"Script #{idx+1} has {len(jinja_tags)} Jinja tags:")
        for tag in set(jinja_tags):
            # check if it is inside quotes or unquoted
            pos = 0
            while True:
                p = s.find(tag, pos)
                if p == -1: break
                snippet = s[max(0, p-20):min(len(s), p+len(tag)+20)].replace('\n', ' ')
                print(f"  Context: ... {snippet} ...")
                pos = p + len(tag)

