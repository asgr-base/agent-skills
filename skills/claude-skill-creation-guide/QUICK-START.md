# スキル作成クイックスタート

初心者向けの最小限のスキル作成手順。5分で最初のスキルを作成できます。

## 方法1: スクリプトで初期化（推奨）

### Step 1: 依存関係インストール

```bash
pip install pyyaml
```

### Step 2: スキル初期化

```bash
cd ~/.claude/skills/claude-skill-creation-guide
python scripts/init_skill.py my-first-skill --path ~/.claude/skills
```

生成されるファイル:
```
~/.claude/skills/my-first-skill/
├── SKILL.md              # テンプレート（TODO項目あり）
├── scripts/example.py    # サンプルスクリプト
├── references/api_reference.md
└── assets/example_asset.txt
```

### Step 3: SKILL.mdを編集

TODO項目を埋め、不要なファイル/フォルダを削除。

### Step 4: バリデーション

```bash
python scripts/quick_validate.py ~/.claude/skills/my-first-skill
```

### Step 5: テスト

新しいClaudeセッションでスキルをトリガーするタスクを実行。

---

## 方法2: 手動作成

```bash
mkdir -p ~/.claude/skills/my-first-skill
```

`~/.claude/skills/my-first-skill/SKILL.md` を作成:

```yaml
---
name: my-first-skill
description: Does X when user asks about Y. Use when user mentions Z.
---

# My First Skill

## Instructions

1. First, do this
2. Then, do that
3. Finally, verify the result
```

---

## よくある問題と対策

| 問題 | 対策 |
|------|------|
| スキルがトリガーされない | descriptionにキーワードを追加 |
| 指示が無視される | ALWAYS, MUSTなどの強調表現を使用 |
| 情報が不足 | 参照ファイルを追加 |
| バリデーションエラー | フロントマターは`name`, `description`のみ使用 |

## 配布用パッケージ化

```bash
python scripts/package_skill.py ~/.claude/skills/my-first-skill ./dist
# -> ./dist/my-first-skill.skill が作成される
```

## 次のステップ

1. **詳細を学ぶ**: [SKILL.md](SKILL.md) - 完全なガイド
2. **パターンを参照**: [PATTERNS.md](PATTERNS.md) - 一般的なパターン集
3. **評価を作成**: [EVALUATION.md](EVALUATION.md) - 評価駆動開発

---

**参照元**: [SKILL.md](SKILL.md)
