from pathlib import Path
import base64, hashlib, json, lzma, re

root = Path(__file__).resolve().parent.parent
parts = [root / '.site-source' / f'part-{i:02d}.txt' for i in range(1, 5)]
assert all(p.is_file() for p in parts), 'Missing source part'
encoded = ''.join(p.read_text().strip() for p in parts)
assert len(encoded) == 40520, 'Invalid source size'
bundle = json.loads(lzma.decompress(base64.b64decode(encoded, validate=True)))
base = bundle['base']
lines = base.splitlines(keepends=True)
other = ''.join(''.join(lines[p[0]:p[1]]) if len(p) == 2 else p[0] for p in bundle['patch'])
css = '<style id="race-navigation-style">.ft-race-navigation{display:flex;justify-content:space-between;flex-wrap:wrap;gap:10px;padding:11px 16px;background:#11221b;color:#e6f0e3;font:13px/1.5 sans-serif}.ft-race-navigation a{display:inline-block;color:#e6f0e3;text-decoration:none;padding:6px 10px;border-radius:7px}.ft-race-navigation a:hover{background:#ffffff16}.ft-race-navigation a:focus-visible{outline:2px solid #bce991;outline-offset:3px}.ft-race-navigation .ft-active{background:#bce991;color:#132018;font-weight:700}</style>'
for race, template in [('54', base), ('40', other)]:
    profile = bundle['profiles'][race]
    if isinstance(profile, dict):
        x = y = 0
        values = []
        assert len(profile['dx']) == len(profile['dy'])
        for dx, dy in zip(profile['dx'], profile['dy']):
            x += dx
            y += dy
            sx = f'{x / 1e9:.9f}'.rstrip('0').rstrip('.') if x else '0.0'
            values.append('[' + sx + ',' + str(y) + ']')
        profile = '[' + ','.join(values) + ']'
    original = template.replace('__FT_PROFILE__', profile)
    assert hashlib.sha256(original.encode()).hexdigest() == bundle['sha'][race], 'Original source checksum mismatch'
    assert original.count('<body>') == 1 and original.count('</head>') == 1
    links = ''.join('<a href="ft' + r + '.html"' + (' class="ft-active" aria-current="page"' if r == race else '') + '>' + r + 'K 配速表</a>' for r in ['54', '40'])
    nav = '<nav class="ft-race-navigation" aria-label="賽事組別導覽"><a href="index.html">← 返回組別選擇</a><div>' + links + '</div></nav>'
    result = original.replace('</head>', css + '\n</head>', 1).replace('<body>', '<body>\n' + nav, 1)
    assert result.replace(css + '\n', '', 1).replace('\n' + nav, '', 1) == original
    scripts = lambda text: re.findall(r'<script\b[^>]*>.*?</script>', text, re.S | re.I)
    assert scripts(result) == scripts(original)
    (root / ('ft' + race + '.html')).write_text(result, encoding='utf-8')
