import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const skillsRoot = path.join(root, "skills");
const contract = fs.readFileSync(
  path.join(root, ".agents", "request-user-input.md"),
  "utf8",
);
const pointer = "./REQUEST-USER-INPUT.md";
let synced = 0;

for (const bucket of fs.readdirSync(skillsRoot, { withFileTypes: true })) {
  if (!bucket.isDirectory() || bucket.name === "deprecated") continue;

  const bucketPath = path.join(skillsRoot, bucket.name);
  for (const skill of fs.readdirSync(bucketPath, { withFileTypes: true })) {
    if (!skill.isDirectory()) continue;

    const skillPath = path.join(bucketPath, skill.name);
    const sourcePath = path.join(skillPath, "SKILL.md");
    if (!fs.existsSync(sourcePath)) continue;

    const source = fs.readFileSync(sourcePath, "utf8");
    if (!source.includes(pointer)) continue;

    fs.writeFileSync(path.join(skillPath, "REQUEST-USER-INPUT.md"), contract);
    synced += 1;
  }
}

console.log(`Synchronized ${synced} Decision prompt contracts.`);
