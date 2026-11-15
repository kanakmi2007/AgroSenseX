import re
import html.parser

class ProblemChecker(html.parser.HTMLParser):
    def __init__(self, filename):
        super().__init__()
        self.filename = filename
        self.problems = []
        self.tag_stack = []

    def handle_starttag(self, tag, attrs):
        attr_names = [a[0] for a in attrs]
        # check duplicate attributes
        seen = set()
        for name in attr_names:
            if name in seen:
                self.problems.append(f"{self.filename}:{self.getpos()[0]} Duplicate attribute '{name}' in <{tag}>")
            seen.add(name)
        # check empty or malformed href/src
        for name, val in attrs:
            if name in ('href', 'src') and val is None:
                self.problems.append(f"{self.filename}:{self.getpos()[0]} Attribute '{name}' has None value in <{tag}>")

for t in ['templates/dashboard.html', 'templates/soil_dashboard.html']:
    with open(t, encoding='utf-8') as f:
        content = f.read()
    # remove jinja blocks to parse html
    clean_html = re.sub(r'\{\{.*?\}\}|\{%.*?%\}', 'JINJA_TOKEN', content)
    parser = ProblemChecker(t)
    try:
        parser.feed(clean_html)
        print(f"{t}: HTML Parse OK, found {len(parser.problems)} problems")
        for p in parser.problems:
            print("  ", p)
    except Exception as e:
        print(f"{t}: HTML Parse Error: {e}")

