# claude-insight-reflect

Claude Code Insightレポートを分析し、示唆をプロジェクト設定（CLAUDE.md）に反映するスキル。

## 概要

Claude Codeの`/insights`コマンドで生成された使用状況レポートから：
- 改善提案を抽出
- プロジェクト設定ファイル（CLAUDE.md）に反映
- 関連スキルのSKILL.mdを更新

これにより、**使用パターンの分析 → ルールの改善**というフィードバックループを構築できます。

## 機能

| 機能 | 説明 |
|------|------|
| レポート翻訳 | 英語レポートをローカル言語に翻訳 |
| 示唆抽出 | 「試すべき機能」「カスタムスキル」等のセクションから改善点を特定 |
| CLAUDE.md更新 | 汎用ルールをプロジェクト設定に追加 |
| スキル更新 | スキル固有の改善を該当SKILL.mdに反映 |

## インストール

### 方法1: ディレクトリをコピー

```bash
# スキルディレクトリにコピー
cp -r claude-insight-reflect ~/.claude/skills/
```

### 方法2: シンボリックリンク

```bash
# リポジトリをクローン後、シンボリックリンクを作成
ln -s /path/to/claude-insight-reflect ~/.claude/skills/claude-insight-reflect
```

## 使用方法

### 基本的な使い方

```
/claude-insight-reflect
```

Claude Codeに上記を入力すると、以下のワークフローが実行されます：

1. **レポート確認**: `.claude/usage-data/`内の最新レポートを特定
2. **翻訳**（任意）: 英語レポートをローカル言語に翻訳
3. **示唆分析**: レポートから改善提案を抽出
4. **反映確認**: ユーザーに反映する項目を確認
5. **ファイル更新**: CLAUDE.mdまたは関連SKILL.mdを更新

### オプション

```
/claude-insight-reflect --report-only    # レポート生成・翻訳のみ
/claude-insight-reflect --apply-only     # 既存レポートから示唆反映のみ
```

## 前提条件

- Claude Code CLI（`claude`コマンド）がインストール済み
- プロジェクトに`CLAUDE.md`が存在
- レポート保存用の`.claude/usage-data/`ディレクトリ

## ディレクトリ構造

```
.claude/
├── skills/
│   └── claude-insight-reflect/
│       ├── SKILL.md      # スキル定義
│       └── README.md     # このファイル
└── usage-data/
    ├── report-YYYYMMDD.html       # オリジナルレポート
    └── report-YYYYMMDD-xx.html    # 翻訳版レポート
```

## カスタマイズ

### 翻訳言語の変更

SKILL.mdの「レポートの日本語翻訳」セクションを編集し、対象言語を変更できます。

### 反映先の追加

SKILL.mdの「反映基準」セクションを編集し、独自の反映ルールを追加できます。

## ライセンス

MIT License

## 関連リンク

- [Claude Code公式ドキュメント](https://docs.anthropic.com/claude-code)
- [Claude Code Skills](https://docs.anthropic.com/claude-code/skills)
