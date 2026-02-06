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
| メモリが記録されない | LLM API設定確認 |
| hookでbunが見つからない | `~/.zshenv`にPATH設定を追加 |
| memorySessionId not yet captured | claudeプロバイダーに切り替え |
| **hookが二重発火する** | **settings.jsonからhooksを削除（プラグイン有効化時は自動登録）** |
| **Generator aborted / CPU暴走** | **ワーカー停止 → キュークリア → ワーカー再起動** |

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
node ${PLUGIN_DIR}scripts/worker-cli.js start

# 5. Claude Code再起動
```

**注意**: `$PLUGIN_DIR`はプラグインのインストール先に置き換える。確認方法：

```bash
# marketplaces配置の場合
ls ~/.claude/plugins/marketplaces/thedotmack/plugin/

# cache配置の場合
ls -d ~/.claude/plugins/cache/thedotmack/claude-mem/*/
```

## LLM API設定（必須）

Summary/Observationの生成にはLLMが必要。以下の3つのプロバイダーから選択する。

### プロバイダー比較

| プロバイダー | 認証方式 | コスト | memorySessionIdバグ |
|-------------|---------|--------|---------------------|
| **claude** | Claude Code CLI（ローカル実行） | Claude Max: 追加費用なし / API: 従量課金 | なし |
| gemini | Google AI Studio APIキー | 無料枠あり（レート制限注意） | あり（Issue #623） |
| openrouter | OpenRouter APIキー | 従量課金 | あり（Issue #623） |

### claudeプロバイダー（推奨）

ローカルのClaude Code CLIを経由してLLMを呼び出す。外部APIキーやプロキシサーバーは不要。

- **Claude Maxサブスクリプション**: 追加費用なし
- **Anthropic APIキー**: 従量課金

```json
{
  "CLAUDE_MEM_PROVIDER": "claude",
  "CLAUDE_MEM_MODEL": "claude-sonnet-4-5"
}
```

### Geminiプロバイダー

[Google AI Studio](https://aistudio.google.com/apikey)でAPIキーを取得して設定。

```json
{
  "CLAUDE_MEM_PROVIDER": "gemini",
  "CLAUDE_MEM_GEMINI_API_KEY": "AIza...",
  "CLAUDE_MEM_GEMINI_MODEL": "gemini-2.0-flash"
}
```

**注意**: 無料枠にはレート制限がある。429エラーが発生する場合はモデル変更またはclaudeプロバイダーへの切り替えを検討。

### OpenRouterプロバイダー

```json
{
  "CLAUDE_MEM_PROVIDER": "openrouter",
  "CLAUDE_MEM_OPENROUTER_API_KEY": "sk-or-...",
  "CLAUDE_MEM_OPENROUTER_MODEL": "anthropic/claude-sonnet-4-5"
}
```

### memorySessionIdバグについて（Issue #623）

Gemini/OpenRouterはstatelessプロバイダーのため、`memorySessionId`を返さず無限クラッシュリカバリーループが発生する場合がある。claudeプロバイダーでは発生しない。

**ワークアラウンド**（Gemini/OpenRouterを使い続ける場合）:

```bash
# stuck queueとセッションをリセット
sqlite3 ~/.claude-mem/claude-mem.db "DELETE FROM pending_messages;"
sqlite3 ~/.claude-mem/claude-mem.db "UPDATE sdk_sessions SET status = 'failed' WHERE memory_session_id IS NULL OR memory_session_id = '';"
# ワーカー再起動
node ${PLUGIN_DIR}scripts/worker-cli.js restart
```

**関連**: [Issue #623](https://github.com/thedotmack/claude-mem/issues/623) / [PR #615](https://github.com/thedotmack/claude-mem/pull/615)

## hooks設定

### プラグイン有効化時（推奨）

`enabledPlugins`でプラグインを有効化すると、hooksはプラグインが自動登録する。

```json
{
  "enabledPlugins": {
    "claude-mem@thedotmack": true
  }
}
```

**WARNING**: この場合、`~/.claude/settings.json`にhooksを手動追加してはならない。プラグインのhooksとsettings.jsonのhooksが**両方同時に実行され、二重発火**が発生する。二重発火はDB不整合（FOREIGN KEY constraint failed）→ Generator abortedの連鎖 → CPU暴走を引き起こす。

### プラグイン無効化時のみ手動設定

プラグインを無効化した状態でhooksのみ使いたい場合に限り、`~/.claude/settings.json`に手動で追加する（`$PLUGIN_DIR`は実際のパスに置き換え）：

```json
{
  "enabledPlugins": {
    "claude-mem@thedotmack": false
  },
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

### 各hookの役割

| Hook | 機能 |
|------|------|
| `SessionStart` | コンテキスト生成、ユーザーメッセージ準備 |
| `UserPromptSubmit` | セッション初期化（session_id取得） |
| `PostToolUse` | ツール使用後にobservation記録 |
| `Stop` | ターン終了時にサマリー生成 |

## ディレクトリ構成

| パス | 内容 |
|------|------|
| `~/.claude-mem/` | データディレクトリ |
| `~/.claude-mem/settings.json` | 設定ファイル |
| `~/.claude-mem/logs/` | ログファイル |
| `~/.claude-mem/claude-mem.db` | SQLiteデータベース |
| `~/.claude/plugins/` | プラグイン本体（marketplacesまたはcache配下） |

## ワーカー管理

```bash
node ${PLUGIN_DIR}scripts/worker-cli.js start    # 起動
node ${PLUGIN_DIR}scripts/worker-cli.js stop     # 停止
node ${PLUGIN_DIR}scripts/worker-cli.js restart  # 再起動
node ${PLUGIN_DIR}scripts/worker-cli.js status   # 状態確認

# ポート確認
lsof -i :37777
```

## 動作確認

```bash
# ヘルスチェック
curl -s http://localhost:37777/api/health

# 統計確認（observations数、sessions数等）
curl -s http://localhost:37777/api/stats

# ログでhook動作確認
cat ~/.claude-mem/logs/claude-mem-$(date +%Y-%m-%d).log | grep -E "HOOK|INIT_COMPLETE"
```

### 正常動作の指標

| 項目 | 確認方法 |
|------|---------|
| ワーカー起動 | `lsof -i :37777` でプロセスが表示 |
| セッション初期化 | ログに`INIT_COMPLETE`が記録 |
| observation記録 | `api/stats`で`observations`が増加 |
| hook実行 | ログに`[HOOK ]`エントリが記録 |

## MCPツール（3層検索）

トークン節約のため、3層ワークフローに従う。

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

## セッション再開

### 自動コンテキスト注入

新しいセッションを開始すると、SessionStartフックが過去のコンテキストを自動注入する。

| 注入データ | デフォルト設定 |
|-----------|--------------|
| 最近のobservations | 50件 (`CLAUDE_MEM_CONTEXT_OBSERVATIONS`) |
| 過去のセッションサマリー | 10件 (`CLAUDE_MEM_CONTEXT_SESSION_COUNT`) |

キーワードを含めて依頼するだけで関連コンテキストが活用される：

```
前回のAPI設計作業の続きをお願いします。
```

### 3層Progressive Disclosure

| 層 | 内容 | アクセス方法 |
|----|------|-------------|
| 第1層 | observationのタイトル、トークンコスト推定 | 自動表示 |
| 第2層 | 詳細検索（概念、ファイル、タイプ、キーワード） | MCPツールで検索 |
| 第3層 | 完全な履歴・ソースコード | 直接アクセス |

### /clearコマンド

`/clear`を使用してもセッションは継続。コンテキストが再注入され、observationキャプチャも継続。

### コンテキスト注入設定

| 設定 | デフォルト | 説明 |
|------|-----------|------|
| `CLAUDE_MEM_CONTEXT_OBSERVATIONS` | 50 | 参照observations最大数 |
| `CLAUDE_MEM_CONTEXT_FULL_COUNT` | 5 | 詳細narrative取得数 |
| `CLAUDE_MEM_CONTEXT_SESSION_COUNT` | 10 | 参照セッション数 |
| `CLAUDE_MEM_CONTEXT_SHOW_LAST_SUMMARY` | true | 最後のsummary表示 |

## 設定リファレンス（~/.claude-mem/settings.json）

| 設定 | デフォルト | 説明 |
|------|-----------|------|
| `CLAUDE_MEM_PROVIDER` | - | LLMプロバイダー（claude/gemini/openrouter） |
| `CLAUDE_MEM_MODEL` | claude-sonnet-4-5 | 使用モデル |
| `CLAUDE_MEM_WORKER_PORT` | 37777 | ワーカーポート |
| `CLAUDE_MEM_DATA_DIR` | ~/.claude-mem | データ保存先 |
| `CLAUDE_MEM_LOG_LEVEL` | INFO | ログレベル |
| `CLAUDE_MEM_SKIP_TOOLS` | (複数) | 記録除外ツール |

## Webインターフェース

http://localhost:37777 でリアルタイムメモリを確認可能。

## トラブルシューティング

### bunがPATHで見つからない

非対話シェル（hooks実行環境）では`~/.zshrc`が読み込まれない。`~/.zshenv`にPATH設定を追加：

```bash
export BUN_INSTALL="$HOME/.bun"
export PATH="$BUN_INSTALL/bin:$PATH"
```

### ワーカーが起動しない

```bash
# ログ確認
cat ~/.claude-mem/logs/claude-mem-$(date +%Y-%m-%d).log | tail -50

# Bunバージョン確認
$HOME/.bun/bin/bun --version
```

### hookが二重発火する

**症状**: ログで`INIT_COMPLETE`が同一タイムスタンプで2回記録される。PROMPTが重複して記録される。

**原因**: `enabledPlugins`でプラグインを有効化した状態で、`~/.claude/settings.json`にhooksも手動設定している。プラグインのhooksとsettings.jsonのhooksが両方実行される。

**解決策**: `~/.claude/settings.json`からhooksセクションを削除する。プラグイン有効化時はhooksは自動登録される。

### Generator aborted / CPU暴走

**症状**: ログに`Generator aborted`が大量発生。bunプロセスがCPU 200%以上を消費。

**原因**: FOREIGN KEY constraint failedやhook二重発火により処理キューが破損し、無限リトライループが発生。

**解決策**:

```bash
# 1. ワーカー停止
pkill -f "worker-service"
pkill -9 -f "bun.*claude-mem"

# 2. キュークリア
sqlite3 ~/.claude-mem/claude-mem.db "DELETE FROM pending_messages;"

# 3. ワーカー再起動
node ${PLUGIN_DIR}scripts/worker-cli.js start
```

### observationsが記録されない

1. LLM API設定が正しいか確認（プロバイダー・認証情報）
2. ログで`INIT_COMPLETE`が記録されているか確認
3. ログで`Generator aborted`が発生していないか確認

### Generator exited unexpectedly

LLM APIの認証情報が未設定または無効。`~/.claude-mem/settings.json`でプロバイダーとAPIキーを確認。

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

## 完全アンインストール

```bash
# 1. ワーカー停止
node ${PLUGIN_DIR}scripts/worker-cli.js stop

# 2. プラグイン無効化
/plugin disable claude-mem

# 3. データ・設定削除
rm -rf ~/.claude-mem/

# 4. プラグイン本体削除
rm -rf ~/.claude/plugins/marketplaces/thedotmack/
rm -rf ~/.claude/plugins/cache/thedotmack/

# 5. hooks設定を~/.claude/settings.jsonから削除
```

## 関連リソース

- [GitHub - thedotmack/claude-mem](https://github.com/thedotmack/claude-mem)
- ログ: `~/.claude-mem/logs/`
- 設定: `~/.claude-mem/settings.json`

---

**Version**: 2.1.0
**Last Updated**: 2026-02-06

**更新履歴**:
- v2.1.0 (2026-02-06): hooks二重発火問題の警告を追加。プラグイン有効化時はsettings.jsonにhooksを追加しないことを明記。Generator aborted/CPU暴走のトラブルシューティングを追加。
- v2.0.0 (2026-02-06): 汎用公開向けに全体リライト。claudeプロバイダーがローカルClaude Code CLI経由で動作することを明確化。プロバイダー比較を整理。完全アンインストール手順を追加。
- v1.5.0 (2026-02-05): プロバイダー比較を追加。Issue #623ワークアラウンドを追加。
