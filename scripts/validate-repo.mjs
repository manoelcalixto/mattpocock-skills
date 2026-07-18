import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import YAML from "yaml";

const root = process.cwd();
const errors = [];
const buckets = ["engineering", "productivity", "misc", "personal", "in-progress"];
const promotedBuckets = new Set(["engineering", "productivity"]);

const fail = (message) => errors.push(message);
const read = (relativePath) => fs.readFileSync(path.join(root, relativePath), "utf8");
const exists = (relativePath) => fs.existsSync(path.join(root, relativePath));
const listDirs = (relativePath) =>
  fs
    .readdirSync(path.join(root, relativePath), { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name)
    .filter((name) => exists(`${relativePath}/${name}/SKILL.md`))
    .sort();
const setEqual = (left, right) =>
  left.size === right.size && [...left].every((value) => right.has(value));
const reportSetDifference = (label, expected, actual) => {
  const missing = [...expected].filter((value) => !actual.has(value));
  const extra = [...actual].filter((value) => !expected.has(value));
  if (missing.length || extra.length) {
    fail(`${label}: missing=[${missing.join(", ")}], extra=[${extra.join(", ")}]`);
  }
};

const skills = [];
for (const bucket of buckets) {
  for (const name of listDirs(`skills/${bucket}`)) {
    const skillPath = `skills/${bucket}/${name}`;
    const contents = read(`${skillPath}/SKILL.md`);
    const match = contents.match(/^---\n([\s\S]*?)\n---/);
    if (!match) {
      fail(`${skillPath}/SKILL.md: missing YAML frontmatter`);
      continue;
    }

    let frontmatter;
    try {
      frontmatter = YAML.parse(match[1]);
    } catch (error) {
      fail(`${skillPath}/SKILL.md: invalid frontmatter: ${error.message}`);
      continue;
    }

    const keys = Object.keys(frontmatter ?? {}).sort();
    if (keys.join(",") !== "description,name") {
      fail(`${skillPath}/SKILL.md: frontmatter keys must be exactly name and description`);
    }
    if (frontmatter?.name !== name) {
      fail(`${skillPath}/SKILL.md: name ${JSON.stringify(frontmatter?.name)} does not match folder ${name}`);
    }
    if (typeof frontmatter?.description !== "string" || !frontmatter.description.trim()) {
      fail(`${skillPath}/SKILL.md: description must be a non-empty string`);
    }

    const metadataPath = `${skillPath}/agents/openai.yaml`;
    if (!exists(metadataPath)) {
      fail(`${metadataPath}: missing`);
      continue;
    }

    let metadata;
    try {
      metadata = YAML.parse(read(metadataPath));
    } catch (error) {
      fail(`${metadataPath}: invalid YAML: ${error.message}`);
      continue;
    }

    const displayName = metadata?.interface?.display_name;
    const shortDescription = metadata?.interface?.short_description;
    const defaultPrompt = metadata?.interface?.default_prompt;
    if (typeof displayName !== "string" || !displayName.trim()) {
      fail(`${metadataPath}: interface.display_name is required`);
    }
    if (
      typeof shortDescription !== "string" ||
      shortDescription.length < 25 ||
      shortDescription.length > 64
    ) {
      fail(`${metadataPath}: interface.short_description must be 25-64 characters`);
    }
    if (typeof defaultPrompt !== "string" || !defaultPrompt.includes(`$${name}`)) {
      fail(`${metadataPath}: interface.default_prompt must mention $${name}`);
    }

    const policy = metadata?.policy;
    if (policy !== undefined) {
      if (
        Object.keys(policy).join(",") !== "allow_implicit_invocation" ||
        policy.allow_implicit_invocation !== false
      ) {
        fail(`${metadataPath}: the only supported policy is allow_implicit_invocation: false`);
      }
    }

    skills.push({
      bucket,
      name,
      path: skillPath,
      userInvoked: policy?.allow_implicit_invocation === false,
    });
  }
}

if (skills.length !== 38) {
  fail(`expected 38 active skills, found ${skills.length}`);
}

const promoted = skills.filter((skill) => promotedBuckets.has(skill.bucket));
if (promoted.length !== 23) {
  fail(`expected 23 promoted skills, found ${promoted.length}`);
}
const promotedPaths = new Set(promoted.map((skill) => skill.path));
const promotedNames = new Set(promoted.map((skill) => skill.name));

const packageJson = JSON.parse(read("package.json"));
const plugin = JSON.parse(read(".codex-plugin/plugin.json"));
const changesetsConfig = JSON.parse(read(".changeset/config.json"));
if (plugin.name !== "mattpocock-skills") fail("plugin name must be mattpocock-skills");
if (plugin.version !== packageJson.version) {
  fail(`plugin version ${plugin.version} does not match package version ${packageJson.version}`);
}
if (plugin.repository !== "https://github.com/manoelcalixto/mattpocock-skills") {
  fail("plugin repository must point to the fork");
}
if (changesetsConfig.changelog?.[1]?.repo !== "manoelcalixto/mattpocock-skills") {
  fail("Changesets changelog repository must point to the fork");
}
if (!Array.isArray(plugin.skills)) fail("plugin skills must be an explicit array");
const manifestPaths = new Set(
  (plugin.skills ?? []).map((skillPath) => skillPath.replace(/^\.\//, "")),
);
reportSetDifference("plugin promoted set", promotedPaths, manifestPaths);
if ((plugin.interface?.defaultPrompt ?? []).length > 3) {
  fail("plugin interface.defaultPrompt supports at most three entries");
}
for (const prompt of plugin.interface?.defaultPrompt ?? []) {
  if (typeof prompt !== "string" || prompt.length > 128) {
    fail("every plugin default prompt must be a string no longer than 128 characters");
  }
}

const marketplace = JSON.parse(read(".agents/plugins/marketplace.json"));
if (marketplace.name !== "manoelcalixto") fail("marketplace name must be manoelcalixto");
if (marketplace.plugins?.length !== 1) fail("marketplace must expose exactly one plugin");
const marketplacePlugin = marketplace.plugins?.[0];
if (marketplacePlugin?.name !== "mattpocock-skills") fail("marketplace plugin name is incorrect");
if (
  marketplacePlugin?.source?.source !== "local" ||
  marketplacePlugin?.source?.path !== "./"
) {
  fail("marketplace plugin must use the repository root as a local source");
}
if (
  marketplacePlugin?.policy?.installation !== "AVAILABLE" ||
  marketplacePlugin?.policy?.authentication !== "ON_INSTALL"
) {
  fail("marketplace policies must be AVAILABLE and ON_INSTALL");
}

const topReadmeLinks = new Set(
  [...read("README.md").matchAll(/\.\/skills\/(engineering|productivity)\/([^/]+)\/SKILL\.md/g)].map(
    (match) => `skills/${match[1]}/${match[2]}`,
  ),
);
reportSetDifference("top-level README promoted set", promotedPaths, topReadmeLinks);
const topReadme = read("README.md");
for (const skill of skills.filter((candidate) => !promotedBuckets.has(candidate.bucket))) {
  if (topReadme.includes(skill.name)) {
    fail(`README.md: non-promoted skill ${skill.name} must not appear`);
  }
}

const guardrailSkill = read("skills/misc/codex-git-guardrails/SKILL.md");
if (!guardrailSkill.includes(".codex/config.toml") || !guardrailSkill.includes("~/.codex/config.toml")) {
  fail("codex-git-guardrails must configure project and global config.toml hooks");
}
if (guardrailSkill.includes("hooks.json")) {
  fail("codex-git-guardrails must not direct users to hooks.json");
}

for (const bucket of buckets) {
  const bucketSkills = skills.filter((skill) => skill.bucket === bucket);
  const readme = read(`skills/${bucket}/README.md`);
  const linkedNames = new Set(
    [...readme.matchAll(/\.\/([^/]+)\/SKILL\.md/g)].map((match) => match[1]),
  );
  reportSetDifference(
    `${bucket} README skill set`,
    new Set(bucketSkills.map((skill) => skill.name)),
    linkedNames,
  );

  if (promotedBuckets.has(bucket)) {
    const userHeading = readme.indexOf("## User-invoked");
    const modelHeading = readme.indexOf("## Model-invoked");
    if (userHeading === -1 || modelHeading === -1 || userHeading > modelHeading) {
      fail(`skills/${bucket}/README.md: expected User-invoked then Model-invoked sections`);
    } else {
      for (const skill of bucketSkills) {
        const linkIndex = readme.indexOf(`./${skill.name}/SKILL.md`);
        const listedAsUser = linkIndex > userHeading && linkIndex < modelHeading;
        if (listedAsUser !== skill.userInvoked) {
          fail(`skills/${bucket}/README.md: ${skill.name} is in the wrong invocation section`);
        }
      }
    }
  }
}

const docsPaths = new Set();
for (const bucket of promotedBuckets) {
  for (const filename of fs.readdirSync(path.join(root, "docs", bucket))) {
    if (filename.endsWith(".md")) docsPaths.add(`skills/${bucket}/${filename.slice(0, -3)}`);
  }
}
reportSetDifference("promoted docs set", promotedPaths, docsPaths);
for (const skill of promoted) {
  const docPath = `docs/${skill.bucket}/${skill.name}.md`;
  const contents = read(docPath);
  if (!contents.includes("codex plugin marketplace add manoelcalixto/mattpocock-skills")) {
    fail(`${docPath}: missing fork marketplace install command`);
  }
  if (!contents.includes("codex plugin add mattpocock-skills@manoelcalixto")) {
    fail(`${docPath}: missing fork plugin install command`);
  }
  if (!contents.includes(`type \`$${skill.name}\``)) {
    fail(`${docPath}: quickstart must tell the reader to type $${skill.name}`);
  }
  const expectedSource =
    `https://github.com/manoelcalixto/mattpocock-skills/tree/main/${skill.path}`;
  if (!contents.includes(expectedSource)) fail(`${docPath}: source link must point to the fork`);
}

for (const forbiddenPath of [
  "CLAUDE.md",
  ".claude-plugin",
  "skills/misc/git-guardrails-claude-code",
  "skills/in-progress/claude-handoff",
]) {
  if (exists(forbiddenPath)) fail(`${forbiddenPath}: legacy path must not exist`);
}
if (fs.lstatSync(path.join(root, "AGENTS.md")).isSymbolicLink()) {
  fail("AGENTS.md must be a canonical regular file, not a symlink");
}

const tracked = spawnSync(
  "git",
  ["ls-files", "--cached", "--others", "--exclude-standard", "-z"],
  { cwd: root, encoding: "utf8" },
);
if (tracked.status !== 0) {
  fail(`git ls-files failed: ${tracked.stderr.trim()}`);
} else {
  const textExtensions = new Set([".md", ".yaml", ".yml", ".json", ".sh", ".mjs"]);
  const activeFiles = tracked.stdout
    .split("\0")
    .filter(Boolean)
    .filter((file) => exists(file))
    .filter((file) => textExtensions.has(path.extname(file)))
    .filter((file) => !file.startsWith("skills/deprecated/"))
    .filter((file) => file !== "CHANGELOG.md")
    .filter((file) => file !== "package-lock.json")
    .filter((file) => file !== "scripts/validate-repo.mjs")
    .filter((file) => file !== ".agents/adr/0002-ship-as-a-claude-code-plugin.md");

  const skillPattern = [...promotedNames, ...skills.map((skill) => skill.name)]
    .sort((a, b) => b.length - a.length)
    .map((name) => name.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"))
    .join("|");
  const slashInvocation = new RegExp(
    `(^|[^A-Za-z0-9._/\\-])/(${skillPattern})(?![A-Za-z0-9/\\-])`,
    "m",
  );

  for (const file of activeFiles) {
    const contents = read(file);
    if (/claude/i.test(contents)) fail(`${file}: active content still references Claude`);
    const slashMatch = contents.match(slashInvocation);
    if (slashMatch) fail(`${file}: use $${slashMatch[2]} instead of /${slashMatch[2]}`);
  }
}

const hookScript = path.join(root, "skills/misc/codex-git-guardrails/scripts/block-dangerous-git.sh");
const syntaxCheck = spawnSync("bash", ["-n", hookScript], { encoding: "utf8" });
if (syntaxCheck.status !== 0) fail(`git guardrail syntax failed: ${syntaxCheck.stderr.trim()}`);
const blocked = spawnSync("bash", [hookScript], {
  input: '{"tool_input":{"command":"git push origin main"}}',
  encoding: "utf8",
});
if (blocked.status !== 2 || !blocked.stderr.includes("BLOCKED")) {
  fail("git guardrail must block dangerous input with exit code 2 and a stderr reason");
}
const safe = spawnSync("bash", [hookScript], {
  input: '{"tool_input":{"command":"git status"}}',
  encoding: "utf8",
});
if (safe.status !== 0) fail("git guardrail must allow safe git commands");

if (errors.length) {
  console.error(`Validation failed with ${errors.length} error(s):`);
  for (const error of errors) console.error(`- ${error}`);
  process.exit(1);
}

console.log(`Validated ${skills.length} active skills (${promoted.length} promoted).`);
console.log("Codex plugin, fork marketplace, docs, READMEs, policies, versions, and hooks are consistent.");
