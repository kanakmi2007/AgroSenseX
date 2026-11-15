with open('templates/dashboard.html', encoding='utf-8') as f:
    lines = f.readlines()

import re

stack = []
for line_num, line in enumerate(lines, start=1):
    # find open and close tags
    # ignore comments
    line_clean = re.sub(r'<!--.*?-->', '', line)
    # find tokens like <div ...> or </div>
    tokens = re.findall(r'<(/?[a-zA-Z0-9]+)([^>]*)>', line_clean)
    for tag, attrs in tokens:
        tl = tag.lower()
        if tl == 'div':
            stack.append((line_num, line.strip()))
        elif tl == '/div':
            if stack:
                stack.pop()
            else:
                print(f"Extra </div> at line {line_num}")

print(f"Remaining unclosed <div> tags count: {len(stack)}")
for line_num, l in stack:
    print(f"  Line {line_num}: {l[:100]}")

