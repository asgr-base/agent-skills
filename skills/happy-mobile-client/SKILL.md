---
name: happy-mobile-client
description: Happy - Claude Code Mobile Clientのセットアップ、稼働状況確認、トラブルシューティングを支援。スマホからClaude Codeを操作する際の環境構築、QRコードペアリング、セッション管理、エラー対処方法を提供。Happyやモバイルクライアント、スマホからのClaude Code操作に関する質問時に使用。
version: 1.1.0
author: claude_code
createDate: 2026-01-15
updateDate: 2026-01-15
---

# Happy - Claude Code Mobile Client

HappyはClaude Codeをスマホ（iOS/Android）から操作できる無料のオープンソースクライアント。エンドツーエンド暗号化、音声コーディング、プッシュ通知対応。

## セットアップ

### 1. 前提条件

```bash
# Node.js、npm、Claude Codeを確認
node --version && npm --version && claude --version
```

### 2. インストール

```bash
# CLI
npm install -g happy-coder

# モバイルアプリ
# iOS: App Store「Happy: Codex & Claude Code App」
# Android: Google Play「Happy」
```

### 3. ペアリング

```bash
cd /path/to/project
happy  # QRコード表示→スマホでスキャン
```

## 基本コマンド

```bash
happy              # デフォルト起動（sonnet）
happy -m opus      # モデル指定
happy -p auto      # パーミッションモード
happy codex        # Codex経由
```

複数セッション並列実行可能（各セッションは独立したコンテキスト保持）。

## 稼働状況確認

```bash
# 自動チェックスクリプト
bash .claude/skills/happy-mobile-client/scripts/check_happy_status.sh

# 手動確認
ps aux | grep happy           # プロセス
lsof -i -P | grep happy       # ポート
```

## トラブルシューティング

### QRコード表示されない

```bash
claude auth login                           # 再認証
npm uninstall -g happy-coder && \
npm install -g happy-coder                  # 再インストール
```

### 接続エラー

```bash
ping google.com                             # ネットワーク確認
# macOS: システム設定 > ネットワーク > ファイアウォール
```

### モバイル接続不可

1. Happyを再起動してQRコード再表示
2. スマホアプリを再起動
3. ネットワーク接続を確認
4. アプリを再インストール

### パフォーマンス問題

```bash
export NODE_OPTIONS="--max-old-space-size=4096"
happy
```

**詳細**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)参照

## 主要機能

- **音声コーディング**: スマホから音声入力で指示
- **プッシュ通知**: 権限リクエスト、タスク完了、エラー時
- **会話履歴同期**: オフラインでもアクセス可能
- **E2E暗号化**: TweetNaCl（Signal同等）

## セキュリティ

- 公共Wi-Fi使用時はVPN経由推奨
- QRコードを他人に見せない
- 定期的に再認証（`claude auth login`）

## 追加リソース

- [REFERENCE.md](REFERENCE.md) - 高度な設定、API統合、パフォーマンス最適化
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - 詳細なエラー診断・解決策
- [EXAMPLES.md](EXAMPLES.md) - 使用シナリオと実践例
- [README.md](README.md) - スキル概要

## リンク

- 公式: https://happy.engineering/
- GitHub: https://github.com/slopus/happy
- App Store: https://apps.apple.com/us/app/happy-codex-claude-code-app/id6748571505

## チェックリスト

**セットアップ**:
- [ ] Node.js/npm/Claude Codeインストール済み
- [ ] happy-coderインストール済み
- [ ] モバイルアプリインストール済み
- [ ] QRコードでペアリング完了

**トラブル時**:
- [ ] Happyプロセス実行中
- [ ] ネットワーク接続正常
- [ ] ファイアウォール未ブロック
- [ ] Claude Code認証有効

---

**Version**: 1.1.0 | **Updated**: 2026-01-15
