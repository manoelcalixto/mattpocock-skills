import { readFile, writeFile } from "node:fs/promises";

const packagePath = new URL("../package.json", import.meta.url);
const pluginPath = new URL("../.codex-plugin/plugin.json", import.meta.url);

const packageJson = JSON.parse(await readFile(packagePath, "utf8"));
const pluginJson = JSON.parse(await readFile(pluginPath, "utf8"));

pluginJson.version = packageJson.version;

await writeFile(pluginPath, `${JSON.stringify(pluginJson, null, 2)}\n`, "utf8");
