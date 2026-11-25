# chapters_auto.json -> chapters.json (compact, read by build.mjs)
#   python export.py ../../chapters.json
import json, sys, datetime
d = json.load(open('chapters_auto.json', encoding='utf-8'))
out = [[c['name'], c['line'] or '', c['status'], [[h, round(s * 100)] for h, s in c['colors']]] for c in d if c['colors']]
meta = {
    'source': {
        'name': 'Warhammer 40k Wiki (Fandom): Pictorial List of Space Marine Chapters',
        'urls': ['https://warhammer40k.fandom.com/wiki/Pictorial_List_of_Space_Marine_Chapters_(A-L)',
                 'https://warhammer40k.fandom.com/wiki/Pictorial_List_of_Space_Marine_Chapters_(M-Z)'],
        'license': 'CC BY-SA 3.0',
        'license_url': 'https://creativecommons.org/licenses/by-sa/3.0/',
    },
    'license': 'CC BY-SA 3.0 (derived from the source above)',
    'method': 'Chapter names from the list tables. Gene-seed line and status inferred from the summary with keyword rules; '
              'no text is copied. Colors sampled from each chapter illustration: background removed by flood fill from the edges, '
              'k-means in OKLab with lightness down-weighted, shades of one hue merged, share in percent. Illustrations are not included.',
    'generated': datetime.date.today().isoformat(),
    'fields': ['name', 'gene-seed line ("" = unknown)', 'status: loyal | lost | renegade', '[[hex, share %], ...] largest first'],
    'chapters': out,
}
with open(sys.argv[1], 'w', encoding='utf-8') as f:
    json.dump({k: v for k, v in meta.items() if k != 'chapters'}, f, ensure_ascii=False, indent=1)
    f.seek(f.tell() - 2)  # reopen the object to append the compact list, one chapter per line
    f.write(',\n "chapters": [\n' + ',\n'.join(json.dumps(c, ensure_ascii=False, separators=(',', ':')) for c in out) + '\n ]\n}\n')
print(len(out))
