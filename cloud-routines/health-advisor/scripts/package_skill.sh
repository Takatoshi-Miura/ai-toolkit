#!/usr/bin/env bash
# Claude.aiにアップロードするスキルzipを作成する
#
# Usage: bash scripts/package_skill.sh [出力先ディレクトリ（既定: ~/Downloads）]
#
# 含める: SKILL.md / WORKFLOW-*.md / CONFIG.md / SETUP.md / references/ / scripts/ / assets/
# 含めない: input/（健康診断PDF・feedback）・output/・.claude/・README.md・キャッシュ類
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SKILL_NAME="$(basename "$SKILL_DIR")"
OUT_DIR="${1:-$HOME/Downloads}"
OUT_ZIP="$OUT_DIR/$SKILL_NAME.zip"

mkdir -p "$OUT_DIR"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

mkdir -p "$STAGE/$SKILL_NAME"
cd "$SKILL_DIR"
for item in SKILL.md WORKFLOW-*.md CONFIG.md SETUP.md references scripts assets; do
  [ -e "$item" ] || { echo "見つかりません: $item" >&2; exit 1; }
  cp -R "$item" "$STAGE/$SKILL_NAME/"
done
find "$STAGE" \( -name '__pycache__' -o -name '.DS_Store' -o -name '*.pyc' \) -prune -exec rm -rf {} +

# Claude.aiが受け付けるfrontmatterは name/description/license/allowed-tools/metadata/compatibility のみ。
# ローカル専用の項目（user-invocable・disable-model-invocation）と、ローカルのコネクタIDつきツール名を除く
python3 - "$STAGE/$SKILL_NAME/SKILL.md" <<'PY'
import re, sys
path = sys.argv[1]
text = open(path, encoding="utf-8").read()
m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
if not m:
    sys.exit("SKILL.mdにfrontmatterがありません")
allowed = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}
lines = []
for line in m.group(1).splitlines():
    key = line.split(":", 1)[0].strip()
    if not line.startswith((" ", "\t")) and key not in allowed:
        continue
    if key == "allowed-tools":
        tools = [t.strip() for t in line.split(":", 1)[1].split(",")]
        line = "allowed-tools: " + ", ".join(t for t in tools if t and not t.startswith("mcp__"))
    lines.append(line)
fm = "\n".join(lines)
desc = re.search(r"^description:\s*(.*)$", fm, re.M)
if not re.search(r"^name:\s*[a-z0-9-]{1,64}\s*$", fm, re.M) or not desc or len(desc.group(1)) > 1024:
    sys.exit("frontmatterの name / description が不正です")
open(path, "w", encoding="utf-8").write(f"---\n{fm}\n---\n" + text[m.end():])
PY

rm -f "$OUT_ZIP"
(cd "$STAGE" && zip -qr "$OUT_ZIP" "$SKILL_NAME")
echo "作成しました: $OUT_ZIP"
zipinfo -1 "$OUT_ZIP"
