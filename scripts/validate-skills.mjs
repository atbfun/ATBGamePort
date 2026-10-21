#!/usr/bin/env node
// Validates repository invariants:
// 1. .claude-plugin/plugin.json and .claude-plugin/marketplace.json structure
// 2. Every registered skill has SKILL.md with valid frontmatter (name, description) and agents/openai.yaml
// 3. Every relative link in skills/**/*.md resolves to an existing file on disk
// 4. Every skill is referenced in README.md, README.zh-CN.md, and skills/README.md

import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const repo = join(dirname(fileURLToPath(import.meta.url)), "..");
const errors = [];

function checkJson(relPath, requiredKeys) {
  const fullPath = join(repo, relPath);
  if (!existsSync(fullPath)) {
    errors.push(`Missing required manifest: ${relPath}`);
    return null;
  }
  try {
    const parsed = JSON.parse(readFileSync(fullPath, "utf8"));
    for (const key of requiredKeys) {
      if (!(key in parsed)) {
        errors.push(`Missing key "${key}" in ${relPath}`);
      }
    }
    return parsed;
  } catch (err) {
    errors.push(`Invalid JSON in ${relPath}: ${err.message}`);
    return null;
  }
}

function parseFrontmatter(content, relPath) {
  const match = content.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n/);
  if (!match) {
    errors.push(`${relPath} is missing YAML frontmatter (--- ... ---)`);
    return {};
  }
  const fields = {};
  for (const line of match[1].split(/\r?\n/)) {
    const kv = line.match(/^([a-zA-Z0-9_-]+)\s*:\s*(.+)$/);
    if (kv) {
      fields[kv[1]] = kv[2].trim().replace(/^['"]|['"]$/g, "");
    }
  }
  return fields;
}

function checkRelativeLinks(mdPath, relPath) {
  const content = readFileSync(mdPath, "utf8");
  // Strip fenced code blocks before scanning markdown links
  const withoutCodeBlocks = content.replace(/```[\s\S]*?```/g, "");
  const linkRegex = /\[[^\]]+\]\(([^)]+)\)/g;
  let match;
  while ((match = linkRegex.exec(withoutCodeBlocks)) !== null) {
    const rawTarget = match[1].trim().split("#")[0];
    if (
      !rawTarget ||
      rawTarget.startsWith("http://") ||
      rawTarget.startsWith("https://") ||
      rawTarget.startsWith("mailto:")
    ) {
      continue;
    }
    const resolved = resolve(dirname(mdPath), rawTarget);
    if (!existsSync(resolved)) {
      errors.push(`Broken relative link in ${relPath}: "${match[1]}" -> ${resolved} does not exist`);
    }
  }
}

const plugin = checkJson(".claude-plugin/plugin.json", [
  "name",
  "version",
  "description",
  "repository",
  "skills",
]);
checkJson(".claude-plugin/marketplace.json", [
  "name",
  "owner",
  "description",
  "plugins",
]);

if (plugin && Array.isArray(plugin.skills)) {
  for (const skillRel of plugin.skills) {
    const cleanRel = skillRel.replace(/^\.\//, "");
    const skillDir = join(repo, cleanRel);
    const skillName = cleanRel.split("/").pop();
    const skillMd = join(skillDir, "SKILL.md");
    const openaiYaml = join(skillDir, "agents", "openai.yaml");

    if (!existsSync(skillMd)) {
      errors.push(`Missing SKILL.md for registered skill: ${cleanRel}/SKILL.md`);
    } else {
      const content = readFileSync(skillMd, "utf8");
      const fm = parseFrontmatter(content, `${cleanRel}/SKILL.md`);
      if (!fm.name) {
        errors.push(`${cleanRel}/SKILL.md frontmatter is missing "name"`);
      } else if (fm.name !== skillName) {
        errors.push(
          `${cleanRel}/SKILL.md frontmatter name "${fm.name}" does not match folder name "${skillName}"`,
        );
      }
      if (!fm.description || fm.description.length < 20) {
        errors.push(`${cleanRel}/SKILL.md frontmatter has missing or too-short "description"`);
      }
    }

    if (!existsSync(openaiYaml)) {
      errors.push(`Missing Codex UI metadata: ${cleanRel}/agents/openai.yaml`);
    } else {
      const yamlContent = readFileSync(openaiYaml, "utf8");
      if (!yamlContent.includes("display_name:") || !yamlContent.includes("short_description:")) {
        errors.push(`${cleanRel}/agents/openai.yaml must define display_name and short_description`);
      }
    }

    if (existsSync(skillDir) && statSync(skillDir).isDirectory()) {
      for (const entry of readdirSync(skillDir)) {
        if (entry.endsWith(".md")) {
          checkRelativeLinks(join(skillDir, entry), `${cleanRel}/${entry}`);
        }
      }
    }

    for (const docFile of ["README.md", "README.zh-CN.md", "skills/README.md", `docs/${skillName}.md`]) {
      const fullDoc = join(repo, docFile);
      if (!existsSync(fullDoc)) {
        errors.push(`Missing required documentation file: ${docFile}`);
      } else {
        const docContent = readFileSync(fullDoc, "utf8");
        if (!docContent.includes(skillName)) {
          errors.push(`${docFile} does not reference skill "${skillName}"`);
        }
        checkRelativeLinks(fullDoc, docFile);
      }
    }
  }
}

if (errors.length > 0) {
  console.error("Skill repository validation failed:");
  for (const err of errors) {
    console.error(`  - ${err}`);
  }
  process.exit(1);
}

console.log("All skill repository validations passed!");
