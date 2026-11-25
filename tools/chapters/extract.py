# chapters_raw.json + marine images -> chapters.json (name, line, status, colors)
import json, re, os, sys, html
import numpy as np
from PIL import Image

LEGIONS = ['Ultramarines','Dark Angels','Blood Angels','Space Wolves','Imperial Fists','White Scars','Raven Guard','Iron Hands','Salamanders']
ALIASES = {'Black Templars':'Imperial Fists','Crimson Fists':'Imperial Fists','Novamarines':'Ultramarines','Flesh Tearers':'Blood Angels'}

def line_of(name, s):
    for L in LEGIONS:
        if name.startswith(L): return L
    if re.search(r'Primogenitor', s) and 'Ultramarines' in s: return 'Ultramarines'
    pat = r'(successor|lineage|gene-?seed|descend\w*|scions?|progenitor|genetic\w*|bloodline|sons of|offshoot|Founding (?:Successor )?Chapter of|Chapter of the|line of|stock|heritage|derived)[^.]{0,90}?(' + '|'.join(LEGIONS + list(ALIASES)) + ')'
    m = re.search(pat, s, flags=re.I)
    if m:
        L = m.group(2); L = next(x for x in LEGIONS + list(ALIASES) if x.lower() == L.lower())
        return ALIASES.get(L, L)
    return None

def status_of(s):
    first = re.split(r'(?<=[a-z0-9)])\. ', s, maxsplit=1)[0]
    loyal_first = re.search(r'Loyalist|First Founding', first) and not re.search(r'formerly Loyalist', first, re.I)
    if not loyal_first and not re.search(r'penance|returned to the fold|redeemed', s, re.I) and re.search(r'Excommunicate Traitoris|formerly Loyalist|(?:is|are|was|were) an? Renegade|became corrupted|were corrupted|was corrupted|turned to Chaos|fell to Chaos|renounced their vows', s, re.I):
        return 'renegade'
    if re.search(r'recreated|re-?founded|rebuilt|reformed|penance', s, re.I): return 'loyal'
    if re.search(r'(?<!nearly )(?<!almost )(?<!homeworld was )(?<!home world was )(?:destroyed|extinct|annihilated|wiped out)|no longer exists|last (?:Astartes|Battle-Brother)|lost with all hands|disbanded|were all slain', s, re.I)        and not re.search(r'(?:nearly|almost) (?:driven to )?(?:extinction|extinct|destroyed|wiped out)', s, re.I): return 'lost'
    return 'loyal'

# --- colours ---
def srgb2lin(c): c = c/255.0; return np.where(c <= 0.04045, c/12.92, ((c+0.055)/1.055)**2.4)
def lin2srgb(x): x = np.clip(x,0,1); return np.where(x <= 0.0031308, 12.92*x, 1.055*x**(1/2.4)-0.055)*255
M1 = np.array([[0.4122214708,0.5363325363,0.0514459929],[0.2119034982,0.6806995451,0.1073969566],[0.0883024619,0.2817188376,0.6299787005]])
M2 = np.array([[0.2104542553,0.7936177850,-0.0040720468],[1.9779984951,-2.4285922050,0.4505937099],[0.0259040371,0.7827717662,-0.8086757660]])
def rgb2lab(rgb): return np.cbrt(srgb2lin(rgb) @ M1.T) @ M2.T
def lab2hex(lab):
    i2 = np.linalg.inv(M2); i1 = np.linalg.inv(M1)
    lms = (lab @ i2.T) ** 3; rgb = lin2srgb(lms @ i1.T)
    return '#' + ''.join(f'{int(round(v)):02x}' for v in rgb)

def kmeans(X, k, it=25, seed=1):
    rng = np.random.default_rng(seed)
    C = X[rng.choice(len(X), k, replace=False)]
    for _ in range(it):
        d = ((X[:,None,:]-C[None])**2).sum(-1); a = d.argmin(1)
        for j in range(k):
            if (a==j).any(): C[j] = X[a==j].mean(0)
    return C, a

def palette(path):
    im = Image.open(path).convert('RGBA'); im.thumbnail((150, 260))
    a = np.asarray(im).astype(float); rgb = a[...,:3]; alpha = a[...,3]
    h, w = alpha.shape
    # background: transparent, or the colour of the border (white/grey/scene) flooded from the edges
    mask = alpha > 200
    border = np.concatenate([rgb[0], rgb[-1], rgb[:,0], rgb[:,-1]])
    bmask = np.concatenate([mask[0], mask[-1], mask[:,0], mask[:,-1]])
    if bmask.mean() > 0.5:  # opaque image: flood the background from the edges, following gradients/texture
        bg = np.zeros((h, w), bool); bg[0] = bg[-1] = True; bg[:, 0] = bg[:, -1] = True
        bg &= mask
        for _ in range(600):
            grow = np.zeros_like(bg)
            for dy, dx in ((1,0),(-1,0),(0,1),(0,-1)):
                nb = np.roll(bg, (dy, dx), (0, 1)); nrgb = np.roll(rgb, (dy, dx), (0, 1))
                grow |= nb & (np.abs(rgb - nrgb).sum(-1) < 22)
            grow &= mask & ~bg
            if not grow.any(): break
            bg |= grow
        mask &= ~bg
    px = rgb[mask]
    if len(px) < 200: return None
    lab = rgb2lab(px)
    lab = lab[lab[:,0] > 0.12]  # outlines / deep shadows
    # cluster with lightness down-weighted and chroma boosted, so shadows and highlights of one paint stay together
    W = np.array([0.45, 1.6, 1.6])
    C, a = kmeans(lab * W, 8)
    # report a mid-tone of each cluster (median lightness, chroma of its more saturated half) rather than the mean
    cl = []
    for j in range(len(C)):
        m = a == j
        if not m.any(): continue
        g = lab[m]; ch = np.hypot(g[:,1], g[:,2])
        top = g[ch >= np.median(ch)]
        c = np.array([np.median(g[:,0]), top[:,1].mean(), top[:,2].mean()])
        cl.append([c, m.mean()])
    # merge shades of the same paint: close in hue/chroma, any lightness gap up to 0.22
    merged = True
    while merged:
        merged = False
        for i in range(len(cl)):
            for j in range(i+1, len(cl)):
                p, q = cl[i][0], cl[j][0]
                dab = np.hypot(p[1]-q[1], p[2]-q[2]); dl = abs(p[0]-q[0])
                cp, cq = np.hypot(p[1], p[2]), np.hypot(q[1], q[2])
                dh = abs((np.degrees(np.arctan2(p[2], p[1]) - np.arctan2(q[2], q[1]) * 180 / np.pi + 540) % 360) - 180)
                same_hue = min(cp, cq) > 0.035 and dh < 18 and dl < 0.4 and min(cp, cq) / max(cp, cq) > 0.3
                if dab < 0.035 and dl < 0.22 or dab < 0.02 and dl < 0.3 or same_hue:
                    wp, wq = cl[i][1], cl[j][1]
                    cl[i] = [(p*wp+q*wq)/(wp+wq), wp+wq]; cl.pop(j); merged = True; break
            if merged: break
    cl.sort(key=lambda c: -c[1])
    # a dark neutral on top is often shadows + weapons; prefer a clear coloured cluster as the armour
    c0 = cl[0][0]
    if c0[0] < 0.36 and np.hypot(c0[1], c0[2]) < 0.035 and cl[0][1] < 0.75:
        for k in range(1, len(cl)):
            ck = cl[k][0]
            if cl[k][1] >= 0.15 and np.hypot(ck[1], ck[2]) > 0.03 and ck[0] > 0.33:
                cl.insert(0, cl.pop(k)); SWAPPED.append(path); break
    return [[lab2hex(c), round(float(s), 3)] for c, s in cl if s >= 0.03][:6]

SWAPPED = []
rows = json.load(open(sys.argv[1], encoding='utf-8'))
out = []
for r in rows:
    pal = None
    if r['img'] and os.path.exists(r['img']):
        try: pal = palette(r['img'])
        except Exception as e: print('ERR', r['name'], e)
    out.append(dict(name=r['name'], line=line_of(r['name'], r['summary']), status=status_of(r['summary']), colors=pal, img=r['img']))
json.dump(out, open(sys.argv[2], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('swapped:', [os.path.basename(p) for p in SWAPPED])
from collections import Counter
print(len(out), 'with colors', sum(1 for o in out if o['colors']))
print(Counter(o['line'] for o in out)); print(Counter(o['status'] for o in out))
