import fs from "node:fs";

const packageJson = JSON.parse(fs.readFileSync("package.json", "utf8"));
const manifestPath = ".codex-plugin/plugin.json";
const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));

manifest.version = packageJson.version;
fs.writeFileSync(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`);
