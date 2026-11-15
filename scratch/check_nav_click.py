with open('templates/dashboard.html', encoding='utf-8') as f:
    text = f.read()

pos = text.find('function handleNavClick')
if pos != -1:
    print(text[pos:pos+1500])
else:
    print('handleNavClick not found as function')
    # search for handleNavClick
    for line in text.splitlines():
        if 'handleNavClick' in line:
            print(line)

