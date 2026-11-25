# Parse saved Fandom "Pictorial List of Space Marine Chapters" pages -> chapters_raw.json
import re, json, sys, os, html
root = sys.argv[1]  # space_marines folder
out = sys.argv[2]
rows = []
for fn in sorted(os.listdir(root)):
    if not fn.endswith('.html'): continue
    s = open(os.path.join(root, fn), encoding='utf-8').read()
    s = s[s.find('mw-parser-output'):]
    for tr in re.findall(r'<tr>(.*?)</tr>', s, flags=re.S):
        tds = re.findall(r'<td[^>]*>(.*?)</td>', tr, flags=re.S)
        if len(tds) < 4: continue
        def img(td):
            m = re.search(r'<img[^>]*src="\./([^"]+)"', td)
            return os.path.join(root, html.unescape(m.group(1))) if m else None
        def text(td):
            t = re.sub(r'<noscript>.*?</noscript>', '', td, flags=re.S)
            t = re.sub(r'<[^>]+>', '', t)
            return re.sub(r'\s+', ' ', html.unescape(t)).strip()
        name = text(tds[2])
        if not name: continue
        k = re.search(r'data-image-key="([^"]+)"', tds[0])
        im = img(tds[0])
        if (not im or 'Unavailable' in im) and k and 'Unavailable' not in k.group(1):
            p = os.path.join(os.path.dirname(out) or '.', 'img', html.unescape(k.group(1)) + '.png')
            im = p if os.path.exists(p) else None
        if im and 'Unavailable' in im: im = None
        rows.append(dict(name=name, img=im, summary=text(tds[3])))
json.dump(rows, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(rows), 'with image:', sum(1 for r in rows if r['img'] and os.path.exists(r['img'])))
