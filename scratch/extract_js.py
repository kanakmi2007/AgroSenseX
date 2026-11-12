with open('templates/soil_dashboard.html', encoding='utf-8') as f:
    text = f.read()

import re
scripts = re.findall(r'<script>(.*?)</script>', text, re.DOTALL)
print(f'Found {len(scripts)} inline script block(s)')

with open('scratch/inline_script.js', 'w', encoding='utf-8') as f:
    # replace Jinja template strings with mock numbers
    js = scripts[0]
    js = js.replace("{{ soil.moisture }}", "35")
    js = js.replace("{{ soil.ph }}", "6.8")
    js = js.replace("{{ soil.temperature }}", "28")
    js = js.replace("{{ soil.npk.N }}", "45")
    js = js.replace("{{ soil.npk.P }}", "32")
    js = js.replace("{{ soil.npk.K }}", "38")
    f.write(js)

print('Extracted script to scratch/inline_script.js')

