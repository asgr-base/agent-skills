---
name: claude-mem-guide
description: claude-mem plugin guide for persistent memory across Claude Code sessions. Setup, troubleshooting, search usage, worker management. Use when user mentions claude-mem, persistent memory, session memory, or memory search.
---

# claude-mem ガイド

## 概要

claude-memはClaude Codeの永続メモリプラグイン。セッション間でコンテキストを自動保持し、過去の作業履歴を検索可能にする。

## クイックリファレンス

| 問題 | 解決策 |
|------|--------|
| localhost:37777にアクセスできない | ワーカー未起動 → `worker-cli.js start` |
| "Bun is required" エラー | Bunインストール後、PATH設定を確認 |
| MCPツールがエラー | ワーカー起動後、Claude Code再起動 |
| メモリが記録されない | hooks設定確認（VSCode/Cursor環境では手動設定が必要） |
| hookでbunが見つからない | `~/.zshenv`にPATH設定を追加 |

## インストール

```bash
# 1. プラグイン追加
/plugin marketplace add thedotmack/claude-mem
/plugin install claude-mem  # user scope推奨

# 2. Bun インストール（未インストールの場合）
curl -fsSL https://bun.sh/install | bash

# 3. PATH設定（重要：非対話シェルでも読み込まれるよう ~/.zshenv に追加）
echo 'export BUN_INSTALL="$HOME/.bun"' >> ~/.zshenv
echo 'export PATH="$BUN_INSTALL/bin:$PATH"' >> ~/.zshenv

# 4. ワーカー起動
source ~/.zshenv
PLUGIN_DIR=$(ls -d ~/.claude/plugins/cache/thedotmack/claude-mem/*/ | head -1)
node ${PLUGIN_DIR}scripts/worker-cli.js start

# 5. Claude Code再起動
```

## VSCode/Cursor環境でのhooks設定

IMPORTANT: VSCode/Cursor環境では、プラグインのhooksが自動で統合されない。`~/.claude/settings.json`に手動でhooksを追加する必要がある。

### hooks設定の追加

`~/.claude/settings.json`に以下を追加：

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|clear|compact",
        "hooks": [
          {
            "type": "command",
            "command": "$HOME/.bun/bin/bun $PLUGIN_DIR/scripts/worker-service.cjs hook claude-code context",
            "timeout": 60000
          },
          {
            "type": "command",
            "command": "$HOME/.bun/bin/bun $PLUGIN_DIR/scripts/worker-service.cjs hook claude-code user-message",
            "timeout": 60000
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "$HOME/.bun/bin/bun $PLUGIN_DIR/scripts/worker-service.cjs hook claude-code session-init",
            "timeout": 60000
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": ".*",
        "hooks": [
          {
            "type": "command",
            "command": "$HOME/.bun/bin/bun $PLUGIN_DIR/scripts/worker-service.cjs hook claude-code observation",
            "timeout": 30000
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "$HOME/.bun/bin/bun $PLUGIN_DIR/scripts/worker-service.cjs hook claude-code summarize",
            "timeout": 120000
          }
        ]
      }
    ]
  }
}
```

**注意**: `$PLUGIN_DIR`は実際のパスに置き換える。例：`~/.claude/plugins/cache/thedotmack/claude-mem/9.0.12`

### 各hookの役割

| Hook | 機能 |
|------|------|
| `SessionStart` | コンテキスト生成、ユーザーメッセージ準備 |
| `UserPromptSubmit` | セッション初期化（session_id取得） |
| `PostToolUse` | ツール使用後にobservation記録 |
| `Stop` | セッション終了時にサマリー生成 |

## ディレクトリ構成

| パス | 内容 |
|------|------|
| `~/.claude-mem/` | データディレクトリ |
| `~/.claude-mem/settings.json` | claude-mem設定ファイル |
| `~/.claude-mem/logs/` | ログファイル |
| `~/.claude-mem/claude-mem.db` | SQLiteデータベース |
| `~/.claude/plugins/cache/thedotmack/claude-mem/` | プラグイン本体 |

## ワーカー管理

```bash
# プラグインディレクトリを取得
PLUGIN_DIR=$(ls -d ~/.claude/plugins/cache/thedotmack/claude-mem/*/ | head -1)

# ワーカーコマンド
node ${PLUGIN_DIR}scripts/worker-cli.js start    # 起動
node ${PLUGIN_DIR}scripts/worker-cli.js stop     # 停止
node ${PLUGIN_DIR}scripts/worker-cli.js restart  # 再起動
node ${PLUGIN_DIR}scripts/worker-cli.js status   # 状態確認

# ポート確認
lsof -i :37777
```

## 動作確認

### 1. ワーカー確認

```bash
curl -s http://localhost:37777/api/health
# 期待出力: {"status":"ok",...}
```

### 2. 統計確認

```bash
curl -s http://localhost:37777/api/stats
# 期待出力: {"worker":{...},"database":{"observations":N,"sessions":N,...}}
```

### 3. ログでhook動作確認

```bash
cat ~/.claude-mem/logs/claude-mem-$(date +%Y-%m-%d).log | grep -E "HOOK|INIT_COMPLETE"
# 期待出力: [HOOK ] → PostToolUse: ... / INIT_COMPLETE | sessionDbId=...
```

### 正常動作の指標

| 項目 | 確認方法 |
|------|---------|
| ワーカー起動 | `lsof -i :37777` でbunプロセスが表示 |
| セッション初期化 | ログに`INIT_COMPLETE`が記録 |
| observation記録 | `api/stats`で`observations`が増加 |
| hook実行 | ログに`[HOOK ]`エントリが記録 |

## MCPツール（3層検索）

IMPORTANT: トークン節約のため、必ず3層ワークフローに従うこと。

### 1. search（インデックス検索）

```
mcp__plugin_claude-mem_mcp-search__search
パラメータ: query, limit, project, type, obs_type, dateStart, dateEnd
```

軽量なインデックスを返す（~50-100トークン/結果）。まずこれで候補を絞る。

### 2. timeline（コンテキスト取得）

```
mcp__plugin_claude-mem_mcp-search__timeline
パラメータ: anchor (observation ID) または query, depth_before, depth_after
```

特定の観察の前後コンテキストを取得。

### 3. get_observations（詳細取得）

```
mcp__plugin_claude-mem_mcp-search__get_observations
パラメータ: ids (配列、必須)
```

フィルタ済みIDの完全な詳細を取得。最後に使用。

## 設定（~/.claude-mem/settings.json）

| 設定 | デフォルト | 説明 |
|------|-----------|------|
| `CLAUDE_MEM_MODEL` | claude-sonnet-4-5 | 圧縮用モデル |
| `CLAUDE_MEM_WORKER_PORT` | 37777 | ワーカーポート |
| `CLAUDE_MEM_DATA_DIR` | ~/.claude-mem | データ保存先 |
| `CLAUDE_MEM_LOG_LEVEL` | INFO | ログレベル |
| `CLAUDE_MEM_SKIP_TOOLS` | (複数) | 記録除外ツール |

## Webインターフェース

http://localhost:37777 でリアルタイムメモリを確認可能。

## セッション再開

### 自動引き継ぎ（推奨）

SessionStart hookが関連コンテキストを自動注入する。キーワードを含めて依頼するだけでOK。

```
前回のBizPICO API比較の続きをお願いします。
```

### 手動でSession Summaryを参照

1. http://localhost:37777 でWebインターフェースを開く
2. 再開したいセッションのSummaryをコピー
3. 新しいセッションで貼り付けて依頼

```
前回のセッションを再開します。

【Session Summary】
- INVESTIGATED: API 016, 017, 018の比較
- LEARNED: SDK版APIが対象、API 018は対象外
- COMPLETED: API比較分析完了
- NEXT STEPS: 次の指示待ち

続きを進めてください。
```

### コンテキスト注入設定（~/.claude-mem/settings.json）

| 設定 | デフォルト | 説明 |
|------|-----------|------|
| `CLAUDE_MEM_CONTEXT_OBSERVATIONS` | 50 | 参照observations最大数 |
| `CLAUDE_MEM_CONTEXT_FULL_COUNT` | 5 | 詳細narrative取得数 |
| `CLAUDE_MEM_CONTEXT_SESSION_COUNT` | 10 | 参照セッション数 |
| `CLAUDE_MEM_CONTEXT_SHOW_LAST_SUMMARY` | true | 最後のsummary表示 |

### データ構造

| データ | 内容 | 用途 |
|--------|------|------|
| **Session Summary** | INVESTIGATED/LEARNED/COMPLETED/NEXT_STEPS | セッション全体の要約 |
| **Observations** | 各ツール使用の詳細（facts, narrative, concepts） | 詳細なコンテキスト |

Session Summaryは要約なので、長い会話の詳細は含まれない。詳細が必要な場合は`search` → `get_observations`で取得。

## トラブルシューティング

### bunがPATHで見つからない

非対話シェル（hooks実行環境）では`~/.zshrc`が読み込まれない。`~/.zshenv`にPATH設定を追加：

```bash
# ~/.zshenv に追加
export BUN_INSTALL="$HOME/.bun"
export PATH="$BUN_INSTALL/bin:$PATH"
```

### ワーカーが起動しない

```bash
# ログ確認
cat ~/.claude-mem/logs/claude-mem-$(date +%Y-%m-%d).log | tail -50

# Bunパス確認
which bun || echo "Bunがインストールされていない"

# フルパスで確認
$HOME/.bun/bin/bun --version
```

### hooksが動作しない（VSCode/Cursor環境）

1. `~/.claude/settings.json`にhooksが設定されているか確認
2. bunのフルパスを使用しているか確認
3. プラグインディレクトリのパスが正しいか確認
4. Claude Codeを再起動

### observationsが記録されない

1. `UserPromptSubmit` hookが設定されているか確認（セッション初期化に必要）
2. ログで`INIT_COMPLETE`が記録されているか確認
3. `PostToolUse` hookが設定されているか確認

### MCPツールがタイムアウト

1. ワーカー起動確認: `lsof -i :37777`
2. 起動していなければ: `worker-cli.js start`
3. Claude Code再起動

### プライバシー制御

機密情報を記録から除外するには `<private>` タグを使用：

```
<private>
この内容は記録されない
</private>
```

## スキル

| スキル | 説明 |
|--------|------|
| `claude-mem:make-plan` | 実装計画作成 |
| `claude-mem:do` | サブエージェントで計画実行 |

## 関連リソース

- [GitHub - thedotmack/claude-mem](https://github.com/thedotmack/claude-mem)
- ログ: `~/.claude-mem/logs/`
- 設定: `~/.claude-mem/settings.json`

---

**Version**: 1.2.0
**Last Updated**: 2026-02-05
