import re

for t in ['templates/dashboard.html', 'templates/soil_dashboard.html']:
    with open(t, encoding='utf-8') as f:
        content = f.read()
    ids = re.findall(r'\bid=[\'\"]([^\'\"]+)[\'\"]', content)
    seen = {}
    dupes = []
    for line_no, line in enumerate(content.splitlines(), start=1):
        line_ids = re.findall(r'\bid=[\'\"]([^\'\"]+)[\'\"]', line)
        for i in line_ids:
            if i in seen:
                dupes.append((i, seen[i], line_no))
            else:
                seen[i] = line_no
    print(f"\n{t}: Total IDs = {len(ids)}, Duplicate IDs = {len(dupes)}")
    for d in dupes:
        print(f"  Duplicate ID '{d[0]}' at lines {d[1]} and {d[2]}")

