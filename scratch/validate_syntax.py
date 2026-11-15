import ast
import re

print("=== 1. Checking Python Syntax in app.py ===")
try:
    with open('app.py', encoding='utf-8') as f:
        ast.parse(f.read(), filename='app.py')
    print("app.py: Valid Python Syntax (0 errors)")
except SyntaxError as e:
    print(f"app.py SyntaxError: {e}")

print("\n=== 2. Checking Jinja2 Template Syntax ===")
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('templates'))
templates = ['home.html', 'dashboard.html', 'soil_dashboard.html', 'index.html']
for t in templates:
    try:
        env.get_template(t)
        print(f"{t}: Valid Jinja2 Template Syntax (0 errors)")
    except Exception as e:
        print(f"{t} Jinja Error: {e}")

print("\n=== 3. Checking JavaScript blocks in templates ===")
for t in ['dashboard.html', 'soil_dashboard.html']:
    with open(f'templates/{t}', encoding='utf-8') as f:
        content = f.read()
    scripts = re.findall(r'<script(?:\s+[^>]*)?>(.*?)</script>', content, re.DOTALL)
    print(f"{t}: Found {len(scripts)} script block(s)")

