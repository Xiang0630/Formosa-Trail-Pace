from pathlib import Path
import base64, hashlib, json, lzma, re
root = Path(__file__).resolve().parent.parent
raw = lzma.decompress(base64.b64decode((root / '.site-source/mobile-save-update.txt').read_text().strip(), validate=True))
assert hashlib.sha256(raw).hexdigest() == 'ad483febc6f47bf7744e5c0ddfbed5aab6d04160ae49a58ebe52918a908a5561'
races = json.loads(raw)['races']
def sha(s): return hashlib.sha256(s.encode()).hexdigest()
def unwrap(s):
    s = re.sub(r'<style id="race-navigation-style">.*?</style>\n?', '', s, flags=re.S)
    return re.sub(r'<nav class="ft-race-navigation".*?</nav>\n?', '', s, flags=re.S)
def scripts(s): return re.findall(r'<script\b[^>]*>.*?</script>', s, re.S|re.I)
output = {}
for race, data in races.items():
    path = f'ft{race}.html'; before = (root / path).read_text()
    css = re.search(r'<style id="race-navigation-style">.*?</style>', before, re.S).group()
    nav = re.search(r'<nav class="ft-race-navigation".*?</nav>', before, re.S).group()
    original = unwrap(before)
    assert sha(original) == data['old_sha256'], path
    lines = original.splitlines(keepends=True)
    updated = ''.join(''.join(lines[p[0]:p[1]]) if len(p)==2 else p[0] for p in data['operations'])
    assert sha(updated) == data['new_sha256'], path
    assert f'FT{race} Pace-{data["new_version"]}' in updated
    assert updated.count('</head>') == 1 and updated.count('<body>') == 1
    page = updated.replace('</head>', css+'\n</head>', 1).replace('<body>', '<body>\n'+nav, 1)
    assert unwrap(page) == updated and scripts(page) == scripts(updated), path
    output[path] = page
for path in ['index.html', 'README.md']:
    text = (root / path).read_text()
    for race, data in races.items():
        text = text.replace(f'FT{race} Pace-{data["old_version"]}', f'FT{race} Pace-{data["new_version"]}')
        assert f'FT{race} Pace-{data["new_version"]}' in text
    if path == 'README.md':
        text += '\n\n## 手機儲存修正版維護\n\n新版由 .site-source/mobile-save-update.txt 與 build-mobile-save.py 還原，並驗證四份原始 HTML 的 SHA-256。更新這些新版時，必須一併更新差異套件，避免下次建置回復舊版。\n'
    output[path] = text
for path, text in output.items(): (root / path).write_text(text, encoding='utf-8')
