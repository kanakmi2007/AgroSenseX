with open('templates/dashboard.html', encoding='utf-8') as f:
    text = f.read()

pos = text.find('function switchTab')
if pos != -1:
    print(text[pos:pos+1500])

