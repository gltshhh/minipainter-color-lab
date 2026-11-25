# Download missing marine thumbnails (150px) from the Fandom CDN into img/
import re, os, html, json, urllib.request, time, sys
root = sys.argv[1]; os.makedirs('img', exist_ok=True)
got = 0
for fn in sorted(os.listdir(root)):
    if not fn.endswith('.html'): continue
    s = open(os.path.join(root, fn), encoding='utf-8').read(); s = s[s.find('mw-parser-output'):]
    for tr in re.findall(r'<tr>(.*?)</tr>', s, flags=re.S):
        tds = re.findall(r'<td[^>]*>(.*?)</td>', tr, flags=re.S)
        if len(tds) < 4: continue
        td = tds[0]
        if re.search(r'src="\./', td) or 'Unavailable' in td: continue
        m = re.search(r'data-image-key="([^"]+)"', td)
        u = re.search(r'(https://static\.wikia\.nocookie\.net/warhammer40k/images/[^"?]+/revision/latest)', td)
        if not (m and u): continue
        key = html.unescape(m.group(1)); dest = os.path.join('img', key + '.png')
        if os.path.exists(dest): continue
        url = u.group(1) + '/scale-to-width-down/150?format=png'
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'minipainter-color-lab chapter color sampler'})
            open(dest, 'wb').write(urllib.request.urlopen(req, timeout=30).read()); got += 1
        except Exception as e: print('ERR', key, e)
        time.sleep(0.3)
print('downloaded', got)
