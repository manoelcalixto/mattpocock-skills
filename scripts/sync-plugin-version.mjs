#!/usr/bin/env node
// Copies package.json's version into both plugin manifests.
// Runs as part of `npm run version`, immediately after `changeset version`.
// With --check it changes nothing and exits 1 if any version differs.

import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const repo = join(dirname(fileURLToPath(import.meta.url)), "..");
const pluginPaths = [
  ".claude-plugin/plugin.json",
  "plugins/mattpocock-skills-codex/.codex-plugin/plugin.json",
];

const { version } = JSON.parse(readFileSync(join(repo, "package.json"), "utf8"));
const changes = pluginPaths.map((path) => {
  const pluginPath = join(repo, path);
  const source = readFileSync(pluginPath, "utf8");
  const plugin = JSON.parse(source);
  const updated = source.replace(
    /("version"\s*:\s*")[^"]*(")/,
    (_, prefix, suffix) => `${prefix}${version}${suffix}`,
  );

  if (JSON.parse(updated).version !== version) {
    throw new Error(`Could not find a version field to replace in ${path}.`);
  }

  return { path, pluginPath, plugin, updated };
});

const outOfSync = changes.filter(({ plugin }) => plugin.version !== version);
if (process.argv.includes("--check")) {
  for (const { path, plugin } of outOfSync) {
    console.error(`${path} version is ${plugin.version}, package.json is ${version}.`);
  }
  if (outOfSync.length > 0) {
    console.error("Run `node scripts/sync-plugin-version.mjs`.");
    process.exit(1);
  }
  console.log(`Both plugin manifests match package.json version ${version}`);
  process.exit(0);
}

for (const { path, pluginPath, plugin, updated } of changes) {
  if (plugin.version === version) {
    console.log(`${path} is ${version} (already in sync)`);
    continue;
  }
  writeFileSync(pluginPath, updated);
  console.log(`${path} version ${plugin.version} -> ${version}`);
}
