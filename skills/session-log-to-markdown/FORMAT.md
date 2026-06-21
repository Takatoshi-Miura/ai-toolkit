# 出力Markdownフォーマット仕様

`scripts/jsonl_to_markdown.py` が生成するMarkdownの構成。

## 単一セッション変換時

```markdown
# Session Log: <最初のQuestion冒頭40文字>

- Session ID: `<sessionId>`
- Project: `<cwd>`
- Branch: `<gitBranch>`
- 開始: `<最初のtimestamp>` / 終了: `<最後のtimestamp>`

---

## <timestamp> | Q1

### Question

> （ユーザー発言。ide_opened_file等のノイズタグは除去済み）

### Answer

（assistantのtextブロックを連結したもの）

**Tool calls:**

- `Read` `{"file_path": "/path/to/file.py"}`
  <details><summary>詳細</summary>

  入力: {"file_path": "/path/to/file.py"}

  結果:
  ```
  （先頭2000字。超える場合は「（以下省略）」を付記）
  ```
  </details>

---

## <timestamp> | Q2
...
```

## 複数セッション結合時（`--all` / `--since`〜`--until`）

セッションごとの本文（上記と同じ構造）を `\n\n` で連結する。各セッションは独立した `# Session Log: ...` 見出しを持つため、ファイル全体としては複数の大見出しが並ぶ形になる。

## 表現方針

- **ツール呼び出し**: CCLOGの「Progress（要約）/ ProgressFull（詳細）」の2段表現を、Markdown標準機能で代替する。要約1行（ツール名＋主要入力）の直後に `<details>` で入出力詳細を折りたたむ。GitHubやVS CodeのMarkdownビューアで標準サポートされており、読みやすさと情報の網羅性を両立する。
- **thinkingブロック**: デフォルトでは出力しない。ノイズになりやすく、要約の主旨（ユーザーとのやり取りの記録）から外れるため。
- **ツール結果が見つからない場合**: 「結果: (結果なし)」と明記し、処理は継続する。
- **長大なツール結果**: 先頭2000字でプレビューし、それ以上は「（以下省略）」と明記して切り捨てる。
