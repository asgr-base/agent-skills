---
name: claude-skill-creation-guide
description: Claude Code Agent Skillsの作成・管理に関する包括的なガイド。スキル開発のベストプラクティス、設計原則、実装パターンを提供。スキル作成、SKILL.md、Progressive Disclosure関連の質問時に使用。
version: 2.1.0
author: claude_code
createDate: 2025-12-27
updateDate: 2026-01-25
---

# Claude Code Agent Skills 作成ガイド

## クイックリファレンス

| 問題 | 解決策 |
|------|--------|
| descriptionが曖昧 | 機能+使用タイミングを含める |
| SKILL.mdが長すぎる | 500行未満に、詳細は別ファイルへ |
| スキルがトリガーされない | descriptionにキーワード追加 |
| 参照ファイルが読まれない | 1レベルの深さに保つ |
| 指示が無視される | 強調表現（ALWAYS, MUST）を使用 |
| コードが繰り返しエラー | フィードバックループパターン適用 |
| トークンコストが高い | Progressive Disclosure適用 |

## コア設計原則

### 1. Progressive Disclosure（段階的開示）

| Level | 読み込みタイミング | トークンコスト | 内容 |
|-------|-------------------|----------------|------|
| **Level 1** | 起動時（常に） | ~100トークン/スキル | `name`と`description` |
| **Level 2** | スキルがトリガーされた時 | 5,000トークン未満推奨 | SKILL.md本文 |
| **Level 3+** | 必要に応じて | 実質無制限 | 参照ファイル、スクリプト |

**詳細**: [PROGRESSIVE-DISCLOSURE.md](PROGRESSIVE-DISCLOSURE.md)

### 2. 簡潔さが鍵

**Claudeは既に非常に賢い**ことを前提に、Claudeが知らない情報のみを追加。

### 3. 適切な自由度の設定

| 自由度 | 適用場面 | 例 |
|--------|----------|-----|
| **高** | 複数アプローチが有効 | コードレビュー |
| **中** | 推奨パターンあり | レポート生成 |
| **低** | 一貫性重要 | DBマイグレーション |

## スキル作成ワークフロー

### 推奨フロー

| フェーズ | ツール | 説明 |
|----------|--------|------|
| **1. 初期化** | `scripts/init_skill.py` | テンプレートでスキル作成 |
| **2. 設計・開発** | SKILL.md + 参照ファイル | Progressive Disclosure適用 |
| **3. バリデーション** | `scripts/quick_validate.py` | フロントマター・構造チェック |
| **4. パッケージ化** | `scripts/package_skill.py` | .skillファイル作成（配布用） |
| **5. 評価・反復** | [EVALUATION.md](EVALUATION.md) | Two-Instanceパターンでテスト |

### スクリプト使用方法

```bash
# 1. 新規スキル初期化
python scripts/init_skill.py my-new-skill --path ~/.claude/skills

# 2. バリデーション
python scripts/quick_validate.py ~/.claude/skills/my-new-skill

# 3. パッケージ化（配布用）
python scripts/package_skill.py ~/.claude/skills/my-new-skill ./dist
```

**注意**: スクリプトは [anthropics/skills](https://github.com/anthropics/skills) skill-creatorから取得。PyYAML依存（`pip install pyyaml`）。

## スキル構造

### 必須ファイル: SKILL.md

```yaml
---
name: your-skill-name
description: What this Skill does and when to use it
---

# Your Skill Name

## Instructions
[Clear, step-by-step guidance]
```

### YAMLフロントマター

**必須**:
| フィールド | 要件 |
|------------|------|
| `name` | 最大64文字、小文字・数字・ハイフンのみ |
| `description` | 最大1,024文字、機能+使用タイミング |

**オプション**: `license`, `allowed-tools`, `metadata`

**注意**: 公式バリデーターは上記5フィールドのみ許可。`version`, `author`等はローカル用途では使用可だが、パッケージ化時はエラーになる。

### 効果的なdescription

**重要**: 常に三人称で記述（システムプロンプトに注入されるため）

```yaml
# ✅ 良い例
description: Extract text from PDF files. Use when working with PDFs or document extraction.

# ❌ 悪い例
description: I can help you process Excel files
```

### フォルダ構造

```
skill-name/
├── SKILL.md              # メイン指示（500行未満）
├── REFERENCE.md          # 詳細リファレンス
└── scripts/
    └── validate.py       # ユーティリティスクリプト
```

## ワークフローとフィードバックループ

複雑な操作は明確な順次ステップに分解し、チェックリストを提供。

**フィードバックループパターン**: バリデータを実行 → エラーを修正 → 繰り返し

**詳細**: [WORKFLOWS.md](WORKFLOWS.md)

## 実行可能コードを含むスキル

### 基本原則

- **解決し、委ねない**: エラー条件を処理し、Claudeに委ねない
- **ユーティリティスクリプト**: 生成コードより信頼性が高く、トークン節約
- **実行意図を明確に**: "Run `script.py`"（実行） vs "See `script.py`"（参照）

**詳細**: [CODE-SKILLS.md](CODE-SKILLS.md)

## 評価と反復

### 評価駆動開発

1. **ギャップを特定**: スキルなしでタスク実行、失敗点を文書化
2. **評価を作成**: ギャップをテストする3シナリオを構築
3. **最小限の指示を書く**: 評価に合格する最小コンテンツのみ
4. **反復**: 評価実行、改善を繰り返す

### Two-Instance開発パターン

Claude A（スキル作成）とClaude B（スキル使用）で反復:
1. Claude Aとタスク完了 → 再利用パターン特定
2. Claude Aにスキル作成依頼 → 簡潔さレビュー
3. Claude Bでテスト → 観察に基づき改善

**詳細**: [EVALUATION.md](EVALUATION.md)

## Claude Code連携

スキルは以下のClaude Code機能と組み合わせて効果的に活用:

### Hooksとの組み合わせ

スキル使用時に自動処理を追加:
- **PreToolUse**: スキル実行前のバリデーション
- **PostToolUse**: スキル実行後のフォーマット

### Subagentsでの活用

サブエージェントにスキルのサブセットを割り当て、特化したタスクを委譲。

```yaml
---
name: code-reviewer
tools: Read, Glob, Grep
model: sonnet
---
```

### 詳細: [claude-code-guide](../claude-code-guide/SKILL.md)

## セキュリティ考慮事項

**強く推奨**: 自分で作成またはAnthropicから入手したスキルのみ使用

- 全ファイルを徹底監査（異常なネットワーク呼び出し、ファイルアクセスに注意）
- 外部URLからデータ取得するスキルは特にリスクが高い

## チェックリスト

### コア品質
- [ ] `description`が具体的でキーワードを含む
- [ ] SKILL.md本文が500行未満
- [ ] 追加詳細が別ファイルにある
- [ ] ファイル参照が1レベルの深さ

### コードとスクリプト
- [ ] エラー処理が明示的
- [ ] 検証/確認ステップを含む

### テスト
- [ ] 少なくとも3つの評価を作成
- [ ] 複数モデル（Haiku, Sonnet, Opus）でテスト済み

## 詳細リファレンス

| ファイル | 内容 |
|----------|------|
| [QUICK-START.md](QUICK-START.md) | 初心者向けクイックスタート |
| [PROGRESSIVE-DISCLOSURE.md](PROGRESSIVE-DISCLOSURE.md) | Progressive Disclosureパターン詳細 |
| [WORKFLOWS.md](WORKFLOWS.md) | ワークフローとフィードバックループ |
| [CODE-SKILLS.md](CODE-SKILLS.md) | 実行可能コードを含むスキル |
| [EVALUATION.md](EVALUATION.md) | 評価と反復的開発 |
| [PATTERNS.md](PATTERNS.md) | 一般的なパターン集 |
| [PLATFORMS.md](PLATFORMS.md) | プラットフォーム別の利用 |

## 関連スキル

| スキル | 用途 |
|--------|------|
| [claude-code-guide](../claude-code-guide/SKILL.md) | Claude Code全般の機能・設定 |
| [claude-md-guide](../claude-md-guide/SKILL.md) | CLAUDE.md作成・最適化 |

## 公式リソース

- [Agent Skills Overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [Skills Cookbook](https://platform.claude.com/cookbook/skills-notebooks-01-skills-introduction)
- [GitHub - anthropics/skills](https://github.com/anthropics/skills)

---

**Version**: 2.2.0
**Last Updated**: 2026-01-25

**更新履歴**:
- v2.2.0 (2026-01-25): skill-creator統合（init/validate/packageスクリプト追加）、フロントマター制限の注意追加
- v2.1.0 (2026-01-25): クイックリファレンス追加、Claude Code連携セクション追加、プラットフォーム情報分離、180行に圧縮
- v2.0.0 (2026-01-11): Progressive Disclosureに基づき500行以下にリファクタリング
- v1.0.0 (2025-12-27): 初版作成
