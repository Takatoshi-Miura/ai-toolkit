---
allowed-tools: Bash(git:*)
argument-hint: [commit-hash-1] [commit-hash-2]
description: 指定した2つのコミットを1つにまとめる
---

以下の2つのコミットを1つにまとめて：

$1
$2

手順：
1. `git reset --soft HEAD~2` で2つのコミットをリセット
2. `git status` でステージされた変更を確認
3. 適切なコミットメッセージで再コミット
4. `git log --oneline -5` で結果を確認