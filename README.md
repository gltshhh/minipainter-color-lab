# minipainter Color Lab

**GUI color lab for [minipainter](https://github.com/ArturSkowronski/minipainter)**, the open-source miniature paint inventory and paint collection tracker. Color Lab reads minipainter's database (1,600+ paints from Citadel, Army Painter, Vallejo and AK) together with the paints you have marked as owned, and turns them into a local color-theory workbench: mixing recipes from your own paints, closest equivalents across brands (for example Citadel to Vallejo or Army Painter), and a check of what paints you are missing.

It is made for people starting out in the hobby. New painters tend to buy paints they do not need, reach for black and white to shade everything, and pick schemes by guesswork. Color Lab answers the practical questions with the paints you actually own:

- Can I mix this color, and in what ratio?
- Do I really need that dark brown, or do I already have two?
- What paints am I missing, and which brand's paint is closest to the one in a tutorial?
- Which three colors work together on this model, and how do I shade them?

Along the way it teaches the theory behind the answers: hue, value and saturation, why mixing dulls color, complementary colors, warm light and cool shadow, and the 60/30/10 rule.

This is an independent community project, not part of minipainter. The interface is in Polish (the app is called "Pracownia barw").

## What it does

- **Koło i mieszanie (wheel and mixer).** Your paints plotted on an OKLCH color wheel. Click any color and get mixing recipes from the paints you own, such as "3 parts Macragge Blue + 1 part Corax White", with a target vs. result swatch and a closeness rating. Mixing uses a single-constant Kubelka–Munk pigment model rather than RGB averaging, so blue and yellow give a dull dark green, as they do on a real palette.
- **Przed zakupem (before you buy).** Look up any catalog paint or hex code. It tells you whether you already own something nearly identical, whether you can mix it yourself, and how many paints you have in the same color group, such as dark browns.
- **Schematy (schemes).** Pick a main color and a harmony: monochrome, analogous, complementary, split-complementary or triadic. You get a 60/30/10 set built from your own paints, a shield preview, and two shaded spheres that compare black-and-white shading with cool shadows and warm highlights.
- **Kolekcja (collection).** A value scale of your paints with a grayscale toggle, hue coverage with the gaps you can or cannot mix, and the full list.
- **Podstawy (basics).** Short lessons, each linked to the tool where you can try it.

## Setup

Requires Node.js 18+ and minipainter.

```bash
npm install -g minipainter
mpaint inventory own citadel/abaddon-black   # mark the paints you own
node build.mjs                               # writes data.js and index.html
```

Then open `index.html` in a browser. Nothing runs on a server, and the page needs no internet connection apart from loading web fonts.

Run `node build.mjs` again whenever your inventory changes.

### Options

| Flag | Default |
|---|---|
| `--catalog <dir>` | `<npm root -g>/minipainter/data/catalog`, or a local `node_modules/minipainter` |
| `--inventory <file>` | `$MINIPAINTER_INVENTORY`, else `~/.minipainting/inventory.json` |
| `--extras <file>` | `./extras.json` |

### Keep it in sync automatically (Claude Code)

minipainter ships an MCP server, so you can manage your collection by talking to Claude ("I just bought Rhinox Hide and Nuln Oil"). Color Lab includes a Claude Code hook that rebuilds the page whenever Claude changes your inventory through that server. Add paints in chat, refresh the page, and they are on the wheel.

1. Register the minipainter MCP server in your project (`.mcp.json`):

   ```json
   {
     "mcpServers": {
       "minipainter": { "command": "minipainter-mcp" }
     }
   }
   ```

   On Windows, use `"command": "node"` with `"args": ["<npm root -g>/minipainter/src/mcp-server.mjs"]` instead.

2. Add the hook to `.claude/settings.json` in the same project, with the path to your Color Lab checkout:

   ```json
   {
     "hooks": {
       "PostToolUse": [
         {
           "matcher": "mcp__minipainter__inventory_mark_owned|mcp__minipainter__inventory_mark_unowned",
           "hooks": [
             { "type": "command", "command": "node /path/to/minipainter-color-lab/hooks/claude-code-sync.mjs", "timeout": 60 }
           ]
         }
       ]
     }
   }
   ```

3. Restart Claude Code. You can review or disable the hook under `/hooks`.

**Using it on your phone, for example in a store.** A local file does not travel with you. If you use claude.ai, ask Claude Code to publish `app.html` with `data.js` as a private Artifact, then add its link to the same settings file:

```json
{ "env": { "COLOR_LAB_ARTIFACT_URL": "https://claude.ai/artifact/..." } }
```

With that set, the hook also asks Claude to republish the Artifact after each batch of inventory changes, so the page you open on your phone is always current.

The hook runs only in Claude Code. If you change your inventory another way (the `mpaint` CLI, the TUI, or Claude Desktop), run `node build.mjs` yourself.

### Paints missing from the catalog

Put them in `extras.json` (see `extras.example.json`) with a hex color. They show up in your collection and in mixing recipes. Add `"owned": false` to add a paint to the catalog instead (search, equivalents, shopping list), for example a whole range minipainter does not ship yet.

## Files

| File | Role |
|---|---|
| `app.html` | the app: markup, styles, and script |
| `build.mjs` | builds `data.js` from minipainter and wraps `app.html` into `index.html` |
| `hooks/claude-code-sync.mjs` | Claude Code hook that rebuilds after inventory changes made through MCP |
| `data.js`, `index.html` | generated from your own collection, not committed |

## Accuracy

Catalog colors are approximate reference values, and the mixing model simplifies real pigments. Treat a recipe as a starting point: mix a few drops on a wet palette, try it on a test model, and adjust by eye.

## Credits

Paint catalog and inventory: [minipainter](https://github.com/ArturSkowronski/minipainter) by Artur Skowroński (MIT). Color space: [OKLab](https://bottosson.github.io/posts/oklab/) by Björn Ottosson.
