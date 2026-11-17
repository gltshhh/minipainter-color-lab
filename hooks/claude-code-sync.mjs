#!/usr/bin/env node
// Claude Code PostToolUse hook for minipainter Color Lab.
//
// When Claude marks a paint as owned or unowned through the minipainter MCP server,
// this rebuilds data.js and index.html so the local page is current right away.
//
// Optional: if you also host Color Lab as a claude.ai Artifact, set COLOR_LAB_ARTIFACT_URL
// and the hook asks Claude to republish it after the change, so the page on your phone
// shows the new paints too.
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
let summary;
try {
  const out = execFileSync(process.execPath, [join(root, 'build.mjs')], { encoding: 'utf8' });
  summary = (out.split('\n').find(l => l.startsWith('Owned:')) || 'rebuilt').trim();
} catch (e) {
  summary = 'build failed: ' + String(e.stderr || e.message).trim();
}

let context = `minipainter Color Lab data rebuilt after an inventory change (${summary}).`;
const artifact = process.env.COLOR_LAB_ARTIFACT_URL;
if (artifact) {
  context += ` When this batch of inventory changes is done, republish the Color Lab artifact once (not after every paint): ` +
    `Artifact publish with file_path ${join(root, 'app.html')}, url ${artifact}, ` +
    `files {"data.js": "${join(root, 'data.js').replace(/\\/g, '/')}"}.`;
}
process.stdout.write(JSON.stringify({ hookSpecificOutput: { hookEventName: 'PostToolUse', additionalContext: context } }));
