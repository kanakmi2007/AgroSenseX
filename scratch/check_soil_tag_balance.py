with open('templates/soil_dashboard.html', encoding='utf-8') as f:
    text = f.read()

import re

tags = re.findall(r'<([a-zA-Z0-9]+)[^>]*>', text)
closing = re.findall(r'</([a-zA-Z0-9]+)>', text)
void_tags = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr', 'line', 'circle', 'polygon', 'path', 'rect'}

open_counts = {}
for t in tags:
    tl = t.lower()
    if tl not in void_tags:
        open_counts[tl] = open_counts.get(tl, 0) + 1

close_counts = {}
for t in closing:
    tl = t.lower()
    if tl not in void_tags:
        close_counts[tl] = close_counts.get(tl, 0) + 1

print("=== Tag balance in soil_dashboard.html ===")
for t, count in open_counts.items():
    cc = close_counts.get(t, 0)
    if count != cc:
        print(f"Tag <{t}>: open={count}, closed={cc} (diff: {count-cc})")

