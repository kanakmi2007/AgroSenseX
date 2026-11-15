import ast

with open('app.py', encoding='utf-8') as f:
    code = f.read()

tree = ast.parse(code)
imports = set()
names = set()

for node in ast.walk(tree):
    if isinstance(node, ast.Import):
        for n in node.names:
            imports.add(n.name)
    elif isinstance(node, ast.ImportFrom):
        for n in node.names:
            imports.add(n.name)
    elif isinstance(node, ast.Name):
        names.add(node.id)

print("Imported names:", imports)
for imp in imports:
    # check if used
    count = code.count(imp)
    print(f"  {imp}: used {count} times in app.py")

