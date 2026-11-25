# Chapter colors tool

Builds `chapters.json` (the "Chapter colors" mode in Schemes) from the Warhammer 40k Wiki's
*Pictorial List of Space Marine Chapters* ([A–L](https://warhammer40k.fandom.com/wiki/Pictorial_List_of_Space_Marine_Chapters_(A-L)),
[M–Z](https://warhammer40k.fandom.com/wiki/Pictorial_List_of_Space_Marine_Chapters_(M-Z))). The wiki content is
[CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/), and so is the resulting `chapters.json`.
No wiki text or images go into the file: only chapter names, an inferred gene-seed line and status, and sampled colors.

Needs Python 3 with Pillow and NumPy.

1. Save both list pages in a browser ("Web page, complete") into one folder, e.g. `space_marines/`.
   The wiki loads images only when you scroll to them, so most thumbnails are missing from the save; step 3 fills the gaps.
2. `python parse.py <folder> chapters_raw.json`: the tables, one row per chapter (name, illustration, summary).
3. `python fetch.py <folder>`: downloads the missing 150 px illustrations into `img/`. Then run step 2 again.
4. `python extract.py chapters_raw.json chapters_auto.json`: colors, gene-seed line and status.
5. `python sheet.py 0 40 check.png`: optional contact sheet (illustration next to its colors) to check the result by eye.
6. `python export.py ../../chapters.json`, then `node build.mjs` in the project folder.

How the colors are sampled: the background is flooded from the image edges (following gradients and paper texture) and removed,
outlines and deep shadows are dropped, the rest is clustered with k-means in OKLab with lightness down-weighted, clusters of the
same hue are merged, and each color gets its share in percent. A dark neutral cluster on top (usually shadows and weapons) gives way
to a clear colored cluster with at least 15% share. The app treats the first color as the armor.

The gene-seed line is the first of the nine loyal First Founding legions named next to words like "successor", "gene-seed" or
"Founding Chapter of". A chapter counts as renegade only when the first sentence of its summary does not call it Loyalist and the
summary says Excommunicate Traitoris, formerly Loyalist, corrupted and similar. It counts as lost when the summary says destroyed,
extinct or wiped out (not "nearly wiped out").

`img/`, `chapters_raw.json`, `chapters_auto.json` and contact sheets are working files and stay out of git.
