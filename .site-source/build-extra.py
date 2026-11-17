from pathlib import Path
import base64, hashlib, json, lzma, re, struct
root = Path(__file__).resolve().parent.parent
parts = [root / '.race-source' / f'part-{i:02d}.txt' for i in range(1, 7)]
if not all(p.is_file() for p in parts):
    raise SystemExit(0)
raw = lzma.decompress(base64.b64decode(''.join(p.read_text().strip() for p in parts), validate=True))
assert hashlib.sha256(raw).hexdigest() == 'b59de58331f4c203cbcc87c7da323db892d46923bf73a09be1d259a8940e81df'
n = struct.unpack('<I', raw[:4])[0]
m = json.loads(raw[4:4+n]); pos = 4+n
old = ''.join((root / '.site-source' / f'part-{i:02d}.txt').read_text().strip() for i in range(1, 5))
base = json.loads(lzma.decompress(base64.b64decode(old)))['base']
assert hashlib.sha256(base.encode()).hexdigest() == '2f8fe6bd53a72357ba68031a7aa792b51c9467308677e7b463441697cfcf31c7'
def patch(text, operations):
    lines = text.splitlines(keepends=True)
    return ''.join(''.join(lines[p[0]:p[1]]) if len(p)==2 else p[0] for p in operations)
t = {'18': patch(base, m['patch18'])}; t['75'] = patch(t['18'], m['patch75'])
def number():
    global pos
    v = shift = 0
    while True:
        b = raw[pos]; pos += 1; v |= (b & 127) << shift
        if b < 128: return -(v//2)-1 if v & 1 else v//2
        shift += 7
        assert shift <= 70
pages = {}
for d in m['profiles']:
    end = pos + d['bytes']; bits = [0, 0]; points = []
    for _ in range(d['points']):
        row = []
        for i in range(2):
            bits[i] += number(); row.append(struct.unpack('<d', struct.pack('<Q', bits[i]))[0])
        points.append(row)
    assert pos == end
    r = d['race']; original = t[r].replace('__FT_PROFILE__', json.dumps(points, separators=(',', ':')))
    assert hashlib.sha256(original.encode()).hexdigest() == m['sha'][r]
    pages[r] = original
assert pos == len(raw)
for r in ['54', '40']: pages[r] = (root / f'ft{r}.html').read_text()
css = '<style id="race-navigation-style">.ft-race-navigation{display:flex;justify-content:space-between;flex-wrap:wrap;gap:10px;padding:11px 16px;background:#11221b;color:#e6f0e3;font:13px/1.5 sans-serif}.ft-race-navigation a{display:inline-block;color:#e6f0e3;text-decoration:none;padding:6px 10px;border-radius:7px;white-space:nowrap}.ft-race-navigation a:hover{background:#ffffff16}.ft-race-navigation a:focus-visible{outline:2px solid #bce991;outline-offset:3px}.ft-race-navigation .ft-active{background:#bce991;color:#132018;font-weight:700}.ft-race-navigation div{display:flex;flex-wrap:wrap;gap:4px;max-width:100%}</style>'
scripts = lambda s: re.findall(r'<script\b[^>]*>.*?</script>', s, re.S|re.I)
for r, before in pages.items():
    text = re.sub(r'<style id="race-navigation-style">.*?</style>\n?', '', before, flags=re.S)
    text = re.sub(r'<nav class="ft-race-navigation".*?</nav>\n?', '', text, flags=re.S)
    links = ''.join('<a href="ft'+k+'.html"'+(' class="ft-active" aria-current="page"' if k==r else '')+'>'+k+'K 配速表</a>' for k in ['75','54','40','18'])
    nav = '<nav class="ft-race-navigation" aria-label="賽事組別導覽"><a href="index.html">← 返回組別選擇</a><div>'+links+'</div></nav>'
    assert text.count('<body>') == 1 and text.count('</head>') == 1
    text = text.replace('</head>', css+'\n</head>', 1).replace('<body>', '<body>\n'+nav, 1)
    assert scripts(text) == scripts(before)
    pages[r] = text
index = (root / 'index.html').read_text()
c54 = re.search(r'<a class="card ft54".*?</a>', index, re.S).group()
c40 = re.search(r'<a class="card ft40".*?</a>', index, re.S).group()
for r, distance, gain, start in [('75','76.16','+4,281','04:00'),('18','18.27','+810','08:00')]:
    if 'href="ft'+r+'.html"' not in index:
        card = c54.replace('ft54','ft'+r).replace('54K',r+'K').replace('>54<','>'+r+'<').replace('53.47',distance).replace('+2,721',gain).replace('08:30',start)
        if r=='75': card = card.replace('<span>手機桌布 JPEG</span>', '<span>手機桌布 JPEG</span><span>匯出 CSV</span>')
        index = index.replace(c54,card+'\n'+c54,1) if r=='75' else index.replace(c40,c40+'\n'+card,1)
index = index.replace('Formosa Trail 54K / 40K','Formosa Trail 75K / 54K / 40K / 18K').replace('兩個組別各自使用獨立的配速計算器','四個組別各自使用獨立的配速計算器').replace('沿用 FT54 Pace-0.4 與 FT40 Pace-0.1','沿用 FT75 Pace-0.1、FT54 Pace-0.4、FT40 Pace-0.1 與 FT18 Pace-0.2')
if '.ft75{' not in index:
    index = index.replace('</style>','.ft75{--accent:#c5b4ff;background:linear-gradient(145deg,#282139,#11211e)}.ft18{--accent:#97d9f8;background:linear-gradient(145deg,#172d36,#11211e)}</style>',1)
if 'href="USER_GUIDE_LINE.txt"' not in index:
    index = index.replace('</footer>','<a href="USER_GUIDE_LINE.txt">四組使用說明</a></footer>',1)
assert re.findall(r'<a class="card ft(\d+)"',index) == ['75','54','40','18']
guide = (root / '.race-source' / 'LINE_GUIDE.txt').read_text()
for r, text in pages.items(): (root / f'ft{r}.html').write_text(text,encoding='utf-8')
(root / 'index.html').write_text(index,encoding='utf-8')
(root / 'USER_GUIDE_LINE.txt').write_text(guide,encoding='utf-8')
(root / 'README.md').write_text('# Formosa Trail 四組配速計算器\n\n75K：FT75 Pace-0.1；54K：FT54 Pace-0.4；40K：FT40 Pace-0.1；18K：FT18 Pace-0.2。\n\n計算程式未修改，只整合首頁與組別導覽。來源完整性及 JavaScript 一致性由建置程式檢查。\n\n修改 .race-source 或 .site-source 的來源及還原程式後會自動建置，產生的 HTML 會被重建覆寫。Pages Source 請使用 GitHub Actions；部署成功才表示已上線。\n\n## 使用說明\n\n'+guide,encoding='utf-8')
