#!/usr/bin/env node
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const repo = join(dirname(fileURLToPath(import.meta.url)), "..");

function testVerifyHeadlessStderrLoggingAndStageHook() {
  const pySource = readFileSync(
    join(repo, "skills/atb-game-porting/scripts/verify-headless.py"),
    "utf8",
  );
  assert.ok(
    pySource.includes('"--enable-logging=stderr"'),
    "verify-headless.py must pass --enable-logging=stderr to Chrome to capture console errors",
  );

  const audioVerifyDoc = readFileSync(
    join(repo, "skills/atb-game-porting/AUDIO-AND-VERIFICATION.md"),
    "utf8",
  );
  assert.ok(
    audioVerifyDoc.includes("atb_verify_stage"),
    "AUDIO-AND-VERIFICATION.md must document the ?atb_verify_stage=initial|gameplay|stage2 URL hook",
  );
}

function testValidateSkillsChecksReadmeRelativeLinks() {
  const validatorSource = readFileSync(join(repo, "scripts/validate-skills.mjs"), "utf8");
  assert.ok(
    validatorSource.includes("checkRelativeLinks(fullDoc, docFile)"),
    "validate-skills.mjs must validate relative links in README.md, README.zh-CN.md, skills/README.md, and docs/",
  );
}

function testTargetReadmeProvenanceSpecExists() {
  const migrateTemplate = readFileSync(
    join(repo, "skills/atb-game-porting/MIGRATE-TEMPLATE.md"),
    "utf8",
  );
  assert.ok(
    migrateTemplate.includes("Original Game Profile") &&
      migrateTemplate.includes("Porting Provenance") &&
      migrateTemplate.includes("AI Model"),
    "MIGRATE-TEMPLATE.md must specify target/<game>/README.md with Original Game Profile, Porting Provenance, and AI Model",
  );

  const audioVerify = readFileSync(
    join(repo, "skills/atb-game-porting/AUDIO-AND-VERIFICATION.md"),
    "utf8",
  );
  assert.ok(
    audioVerify.includes("target/<game_name>/README.md") &&
      audioVerify.includes("AI Model") &&
      audioVerify.includes("Original Game Profile"),
    "AUDIO-AND-VERIFICATION.md must require checking target/<game_name>/README.md with AI Model and Original Game Profile",
  );
}

testVerifyHeadlessStderrLoggingAndStageHook();
testValidateSkillsChecksReadmeRelativeLinks();
testTargetReadmeProvenanceSpecExists();
console.log("3/3 repository tests passed!");
