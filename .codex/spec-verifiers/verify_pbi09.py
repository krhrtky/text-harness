#!/usr/bin/env python3
"""PBI-09 documentation, public metadata, license, and security release oracle."""
from __future__ import annotations
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TESTS = tuple(Path(f"tests/release/{name}.contract.test.mjs") for name in ("docs", "license", "security", "commands"))
REQUIRED_TITLES = (
    "REL-DOC-01 README has exact install update usage and CLI commands",
    "REL-DOC-02 README enumerates D H S rules exits ranges and limitations",
    "REL-DOC-03 all documentation links resolve to approved targets",
    "REL-LIC-01 LICENSE is the unmodified official Apache 2.0 text",
    "REL-LIC-02 copyright and public repository metadata are exact",
    "REL-LIC-03 dependency license counts and lock hash are reproducible",
    "REL-LIC-04 dev-only duplicate TypeScript notices produce no distributable root NOTICE",
    "REL-SEC-01 tracked secret scan has zero findings",
    "REL-SEC-02 dependency audit has zero unresolved high or critical",
    "REL-CMD-01 package release commands exist and reject unknown modes",
    "REL-CMD-02 documented setup install and upgrade syntax matches executable usage",
    "REL-CI-01 release contract CI is exact least-privilege and credential-free",
)
REQUIRED = (
    Path("README.md"), Path("LICENSE"), Path("SECURITY.md"), Path("CONTRIBUTING.md"), Path("CHANGELOG.md"),
    Path("scripts/verify-release.mjs"), *TESTS,
    Path("docs/release-evidence/release-input.json"), Path("docs/release-evidence/dependency-license-scan.json"),
    Path("docs/release-evidence/security-scan.json"), Path(".github/workflows/release-contract.yml"),
)
UNCHANGED_HASHES = {
    Path("pnpm-lock.yaml"): "f5cc3eea2d7a5c7e04810e44f6d31798094437e54bdfa519112788bdb0f773ba",
    Path("pnpm-workspace.yaml"): "d115dc6c83ba283a7d17146ad456056f3f70b003edb8c312a52880b48b034001",
    Path("AGENTS.md"): "5a28eb473c66cb2a0f08229e1ecdb134284ccd9d7655dc0f7a5a38e869846838",
    Path("scripts/text-harness-setup"): "b252a154665092dd1fa7cd25e9369bb9b2f2a0a513c2daf2f3b43ec562e09216",
}
DELIVERY_HASHES = {
    Path("README.md"): "5a0e0b85110919040fe3342f7f00bcd178b256ee27cbfaaed7c307df238bf405",
    Path("LICENSE"): "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30",
    Path("SECURITY.md"): "1a1c8be7fdd847d56a5d78b7bc9701c9613adc3aec2ec3e662c0ab78b970504e",
    Path("CONTRIBUTING.md"): "88e49663bcfd061a85380e32a195d9786ba017e9f3b42229e5206256a7be2374",
    Path("CHANGELOG.md"): "44d608182c8f3540ab9abdd0ba6991db34ac63c3c00db66edd2f51a80bbcfda0",
    Path("package.json"): "aaaca4013b1553336b859b4fcf2a54eeb625181d7b10c16a735645565683ea43",
    Path("scripts/verify-release.mjs"): "784f878dff9f78b67be9be154b8792f49da6bf2958da3e75a4aa736219385910",
    Path("tests/release/docs.contract.test.mjs"): "fb930208fe218c30f8e4b5e849a31ea25d73c16df6c86c1b101567fd8e9c7184",
    Path("tests/release/license.contract.test.mjs"): "16a30b8c426b3956c1c5a6807d7e64c047ecfb85294e434c9f5b5a444f0cbd1f",
    Path("tests/release/security.contract.test.mjs"): "3a1f6872283c1b97e89c1d643907c358038055d64ac1587bfa244f97f758f859",
    Path("tests/release/commands.contract.test.mjs"): "fbf5778027b385d29b0f8414e89baa448a8cac700f9e2a60010dccbb5000e0a6",
    Path("docs/release-evidence/release-input.json"): "4e9869dce79955efb3c0f9e7cb8b10115fd8b40c60996e8f3e9190568809bed1",
    Path("docs/release-evidence/dependency-license-scan.json"): "d6ec9c707b98902dbff1d9ab42c581afb52eeb1bb39c9c0a727f4ab005b6d0b2",
    Path("docs/release-evidence/security-scan.json"): "b7adea144e9d7dd0747806451e2e0ad0af8fe6d2c98320520faca9c7fad32d43",
    Path(".github/workflows/release-contract.yml"): "29bb21410eb4336faca56dd77ce3eacce3d4a71c2624b31521506ba3223c3b63",
}
APACHE_SHA256 = "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30"
LOCK_SHA256 = "f5cc3eea2d7a5c7e04810e44f6d31798094437e54bdfa519112788bdb0f773ba"
NOTICE_SHA256 = "f5c708b59114507b8b27b48181b6883d106bbca0c1634bbee45b5e344237b66b"

def sha(path: Path) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()

def fail(message: str) -> int:
    print("PBI09_FAIL " + message)
    return 1

def release_input_paths() -> list[Path]:
    roots = [Path("package.json"), Path("pnpm-lock.yaml"), Path("pnpm-workspace.yaml")]
    for directory in ("packages/readability-core", "packages/textlint-adapter", "skills/readability-review"):
        roots.extend(path.relative_to(ROOT) for path in (ROOT / directory).rglob("*") if path.is_file() and "node_modules" not in path.parts)
    return sorted(set(roots), key=lambda path: path.as_posix())

def release_input_contract() -> tuple[dict[str, str], str]:
    entries = {path.as_posix(): sha(path) for path in release_input_paths()}
    payload = "".join(f"{path}\0{digest}\n" for path, digest in entries.items()).encode()
    return entries, hashlib.sha256(payload).hexdigest()

def evidence_errors() -> list[str]:
    errors: list[str] = []
    release = json.loads((ROOT / "docs/release-evidence/release-input.json").read_text())
    licenses = json.loads((ROOT / "docs/release-evidence/dependency-license-scan.json").read_text())
    security = json.loads((ROOT / "docs/release-evidence/security-scan.json").read_text())
    entries, digest = release_input_contract()
    if release.get("schemaVersion") != 1 or release.get("algorithm") != "sha256(path\\0contentSha256\\n)" or release.get("paths") != entries or release.get("releaseInputSha256") != digest: errors.append("release-input")
    common = (licenses.get("releaseInputSha256") == digest and security.get("releaseInputSha256") == digest)
    if not common: errors.append("evidence-subject")
    if licenses.get("command") != "mise x node@24.19.0 -- corepack pnpm licenses list --json" or licenses.get("lockSha256") != LOCK_SHA256: errors.append("license-command-lock")
    if licenses.get("licenseVersionCounts") != {"Apache-2.0": 2, "BSD-2-Clause": 2, "MIT": 72}: errors.append("license-counts")
    notice = licenses.get("noticeScan", {})
    expected_paths = [
        "node_modules/.pnpm/@typescript+typescript-darwin-arm64@7.0.2/node_modules/@typescript/typescript-darwin-arm64/NOTICE.txt",
        "node_modules/.pnpm/typescript@7.0.2/node_modules/typescript/NOTICE.txt",
    ]
    if notice.get("installedPaths") != expected_paths or notice.get("uniqueSha256") != [NOTICE_SHA256] or notice.get("distributableRetentionObligations") != 0 or notice.get("rootNoticeExpected") is not False: errors.append("notice-scope")
    if (ROOT / "NOTICE").exists(): errors.append("unnecessary-root-notice")
    if security.get("secretScan", {}).get("findings") != 0 or security.get("dependencyAudit", {}).get("unresolvedHigh") != 0 or security.get("dependencyAudit", {}).get("unresolvedCritical") != 0: errors.append("security-findings")
    if security.get("secretScan", {}).get("command") != "git grep -nEI <secret-patterns> -- tracked files" or security.get("dependencyAudit", {}).get("command") != "mise x node@24.19.0 -- corepack pnpm audit --audit-level high": errors.append("security-commands")
    for value in (licenses.get("evaluatedAt"), security.get("evaluatedAt")):
        if not isinstance(value, str) or not re.fullmatch(r"2026-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}[+-][0-9]{2}:[0-9]{2}", value): errors.append("evaluated-at")
    return errors

def docs_errors() -> list[str]:
    errors: list[str] = []
    readme = (ROOT / "README.md").read_text()
    sections = ("概要", "要件", "インストール", "更新", "使い方", "CLI", "設定", "ルール", "出力と終了コード", "制約", "開発", "セキュリティ", "ライセンス")
    if not all(re.search(rf"^#+\s+{re.escape(section)}\s*$", readme, re.MULTILINE) for section in sections): errors.append("readme-sections")
    terms = ("scripts/text-harness-setup --install", "git pull --ff-only origin main && scripts/text-harness-setup --upgrade --from <previous-release-tag>", "text-harness-report --input <path>", "D001", "D008", "H101", "H113", "S201", "S208", "UTF-16", "zero-based", "half-open", "Semantic", "hard error", "autofix", "Node 24.19.0", "pnpm 11.22.0")
    if not all(term in readme for term in terms): errors.append("readme-contract")
    all_docs = "\n".join((ROOT / path).read_text() for path in (Path("README.md"), Path("SECURITY.md"), Path("CONTRIBUTING.md"), Path("CHANGELOG.md")))
    for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", all_docs):
        if target.startswith("https://"):
            if not any(target.startswith(prefix) for prefix in ("https://github.com/krhrtky/text-harness", "https://www.apache.org/licenses/", "https://spdx.org/licenses/")): errors.append("external-link:" + target)
        elif target.startswith("#"):
            continue
        elif not (ROOT / target.split("#", 1)[0]).exists(): errors.append("broken-link:" + target)
    if "https://github.com/krhrtky/text-harness/security/advisories/new" not in (ROOT / "SECURITY.md").read_text(): errors.append("security-reporting")
    if "Copyright 2026 krhrtky" not in readme: errors.append("copyright")
    return errors

def package_errors() -> list[str]:
    package = json.loads((ROOT / "package.json").read_text())
    scripts = package.get("scripts", {})
    expected = {mode: f"node scripts/verify-release.mjs {mode.split(':', 1)[1] if ':' in mode else mode}" for mode in ("verify:docs", "verify:license", "verify:security", "verify:artifacts", "verify:release")}
    if any(scripts.get(name) != command for name, command in expected.items()): return ["package-scripts"]
    source = (ROOT / "scripts/verify-release.mjs").read_text()
    if not all(term in source for term in ("docs", "license", "security", "artifacts", "release", "unknown mode", "process.exitCode")): return ["release-script"]
    return []

def main() -> int:
    if not (ROOT / "README.md").is_file():
        print("PBI09_RED missing README.md")
        return 1
    missing = [str(path) for path in REQUIRED if not (ROOT / path).is_file()]
    if missing: return fail("missing " + ",".join(missing))
    drift = [str(path) for path, expected in UNCHANGED_HASHES.items() if sha(path) != expected]
    if drift: return fail("forbidden_path_drift " + ",".join(drift))
    delivery_drift = [str(path) for path, expected in DELIVERY_HASHES.items() if sha(path) != expected]
    if delivery_drift: return fail("delivery_artifact_drift " + ",".join(delivery_drift))
    if (ROOT / "LICENSE").stat().st_size != 11358 or sha(Path("LICENSE")) != APACHE_SHA256: return fail("apache-license")
    try: errors = docs_errors() + package_errors() + evidence_errors()
    except (json.JSONDecodeError, OSError) as error: return fail("artifact-json " + str(error))
    if errors: return fail("contract " + ",".join(errors))
    workflow = (ROOT / ".github/workflows/release-contract.yml").read_text()
    if not all(term in workflow for term in ("pull_request:", "permissions:", "contents: read", "24.19.0", "pnpm verify:release")) or any(term in workflow.lower() for term in ("secrets.", "api_key", "live model")): return fail("ci-contract")
    install = subprocess.run(("mise", "x", "node@24.19.0", "--", "corepack", "pnpm", "install", "--frozen-lockfile"), cwd=ROOT, text=True, capture_output=True)
    if install.returncode != 0: return fail(f"install_exit={install.returncode}")
    command = ("mise", "x", "node@24.19.0", "--", "corepack", "pnpm", "exec", "node", "--test", *(str(path) for path in TESTS))
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    output = result.stdout + result.stderr
    print(output, end="" if not output or output.endswith("\n") else "\n")
    if result.returncode != 0: return fail(f"test_exit={result.returncode}")
    plain = re.sub(r"\x1b\[[0-9;]*m", "", output)
    totals = {name: int(value) for name, value in re.findall(r"^(?:ℹ|#)\s+(tests|pass|fail)\s+(\d+)\s*$", plain, re.MULTILINE)}
    tests, passed, failed = totals.get("tests", -1), totals.get("pass", -1), totals.get("fail", -1)
    titles = sum(title in plain for title in REQUIRED_TITLES)
    if tests < 12 or passed != tests or failed != 0 or titles != 12: return fail(f"tests={tests} pass={passed} fail={failed} required_titles={titles}/12")
    print(f"PBI09_GREEN tests={tests} pass={passed} fail=0 required_titles=12 links=PASS commands=PASS license=PASS notice=ABSENT security=PASS")
    return 0

if __name__ == "__main__": raise SystemExit(main())
