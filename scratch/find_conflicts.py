import os

conflict_markers = ['<<<<<<<', '=======', '>>>>>>>']

for root, dirs, files in os.walk('.'):
    if '.git' in root or 'node_modules' in root:
        continue
    for f in files:
        if f.endswith(('.html', '.py', '.css', '.js', '.json')):
            path = os.path.join(root, f)
            with open(path, encoding='utf-8', errors='ignore') as fp:
                lines = fp.readlines()
            for idx, line in enumerate(lines):
                for cm in conflict_markers:
                    if cm in line:
                        print(f"{path}:{idx+1} has conflict marker: {line.strip()[:60]}")

