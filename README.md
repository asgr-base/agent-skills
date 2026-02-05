# ASGR Agent Skills

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Agent%20Skills-purple)](https://code.claude.com)

Claude Code および Agent Skills 標準に対応したスキルコレクションです。

## クイックスタート

### Claude Code プラグインとしてインストール

```bash
/plugin marketplace add asgr-base/agent-skills
```

### 特定のスキルをインストール

```bash
/plugin install jp-law-verification@asgr-agent-skills
```

### 手動インストール

```bash
# リポジトリをクローン
git clone https://github.com/asgr-base/agent-skills.git

# 必要なスキルを ~/.claude/skills/ にコピー
cp -r agent-skills/skills/jp-law-verification ~/.claude/skills/
```

## スキル一覧

| スキル名 | 説明 | 依存関係 |
|---------|------|---------|
| [jp-law-verification](skills/jp-law-verification/) | e-Gov法令APIで日本の法令を検索・確認 | e-gov-law MCP |
| [claude-mem-guide](skills/claude-mem-guide/) | claude-memプラグインのセットアップ・トラブルシューティング | claude-mem plugin |

### 使用例

**jp-law-verification**:
- 「所得税法第183条を確認して」
- 「源泉徴収のタイミングについて法的根拠を教えて」

**claude-mem-guide**:
- 「claude-memが動作しない」
- 「hookの設定方法を教えて」

## ディレクトリ構成

```
agent-skills/
├── .claude-plugin/
│   └── manifest.json      # Claude Code プラグイン設定
├── skills/
│   ├── jp-law-verification/
│   │   ├── SKILL.md       # スキル定義
│   │   └── README.md      # 詳細ドキュメント
│   └── claude-mem-guide/
│       ├── SKILL.md       # スキル定義
│       └── README.md      # 詳細ドキュメント
├── CONTRIBUTING.md        # 貢献ガイドライン
├── LICENSE
└── README.md
```

## 貢献

貢献を歓迎します！詳細は [CONTRIBUTING.md](CONTRIBUTING.md) をご覧ください。

## ライセンス

Apache License 2.0 - 詳細は [LICENSE](LICENSE) を参照してください。

## 関連リンク

- [Agent Skills 仕様](https://agentskills.io/)
- [Claude Code ドキュメント](https://code.claude.com/docs)
- [Anthropic Skills リポジトリ](https://github.com/anthropics/skills)
