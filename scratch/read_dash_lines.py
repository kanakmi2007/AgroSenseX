with open('templates/dashboard.html', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(2735, 2765):
    if i < len(lines):
        print(f"{i+1}: {lines[i]}", end='')

