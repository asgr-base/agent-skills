# Progressive Disclosure パターン詳細

## 概要

Progressive Disclosureは、Agent Skillsの最も重要な設計原則です。情報を3つのレベルで段階的に読み込むことで、コンテキストウィンドウを効率的に使用します。

## 3つのレベル

### Level 1: メタデータ（起動時に常に読み込み）

```yaml
---
name: pdf-processing
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
---
```

- **コスト**: 約100トークン/スキル
- **タイミング**: 起動時に全スキルのメタデータを読み込み
- **目的**: スキルの発見と選択

### Level 2: 指示（スキルがトリガーされた時）

````markdown
# PDF Processing

## Quick start

Use pdfplumber to extract text from PDFs:

```python
import pdfplumber
with pdfplumber.open("document.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```

For advanced form filling, see [FORMS.md](FORMS.md).
````

- **コスト**: 5,000トークン未満（推奨）
- **タイミング**: スキルが関連すると判断された時
- **目的**: タスク実行のための基本ガイダンス

### Level 3+: リソース（必要に応じて）

```
pdf-skill/
├── SKILL.md          # メイン指示
├── FORMS.md          # フォーム入力ガイド
├── REFERENCE.md      # API リファレンス
└── scripts/
    └── fill_form.py  # ユーティリティスクリプト
```

- **コスト**: 実質無制限（アクセスされるまで0トークン）
- **タイミング**: SKILL.md内で参照された時のみ
- **目的**: 詳細なリファレンス、実行可能コード

## Progressive Disclosureパターン

### パターン1: 高レベルガイドと参照

````markdown
---
name: pdf-processing
description: Extracts text and tables from PDF files, fills forms, and merges documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
---

# PDF Processing

## Quick start

Extract text with pdfplumber:
```python
import pdfplumber
with pdfplumber.open("file.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```

## Advanced features

**Form filling**: See [FORMS.md](FORMS.md) for complete guide
**API reference**: See [REFERENCE.md](REFERENCE.md) for all methods
**Examples**: See [EXAMPLES.md](EXAMPLES.md) for common patterns
````

Claudeは必要な時のみFORMS.md、REFERENCE.md、EXAMPLES.mdを読み込みます。

### パターン2: ドメイン別組織

複数ドメインを持つスキルでは、ドメインごとにコンテンツを整理します：

```
bigquery-skill/
├── SKILL.md (overview and navigation)
└── reference/
    ├── finance.md (revenue, billing metrics)
    ├── sales.md (opportunities, pipeline)
    ├── product.md (API usage, features)
    └── marketing.md (campaigns, attribution)
```

````markdown
# BigQuery Data Analysis

## Available datasets

**Finance**: Revenue, ARR, billing → See [reference/finance.md](reference/finance.md)
**Sales**: Opportunities, pipeline, accounts → See [reference/sales.md](reference/sales.md)
**Product**: API usage, features, adoption → See [reference/product.md](reference/product.md)
**Marketing**: Campaigns, attribution, email → See [reference/marketing.md](reference/marketing.md)

## Quick search

Find specific metrics using grep:

```bash
grep -i "revenue" reference/finance.md
grep -i "pipeline" reference/sales.md
grep -i "api usage" reference/product.md
```
````

### パターン3: 条件付き詳細

基本内容を表示し、高度な内容にリンク：

```markdown
# DOCX Processing

## Creating documents

Use docx-js for new documents. See [DOCX-JS.md](DOCX-JS.md).

## Editing documents

For simple edits, modify the XML directly.

**For tracked changes**: See [REDLINING.md](REDLINING.md)
**For OOXML details**: See [OOXML.md](OOXML.md)
```

Claude reads REDLINING.md or OOXML.md only when the user needs those features.

## 重要な制約

### 深くネストした参照を避ける

Claudeはネストした参照ファイルを部分的にしか読み込まない場合があります。`head -100`などでプレビューし、情報が不完全になる可能性があります。

**参照は常にSKILL.mdから1レベルの深さに保つ**

❌ 悪い例（深すぎる）:
```markdown
# SKILL.md
See [advanced.md](advanced.md)...

# advanced.md
See [details.md](details.md)...

# details.md
Here's the actual information...
```

✅ 良い例（1レベル）:
```markdown
# SKILL.md

**Basic usage**: [instructions in SKILL.md]
**Advanced features**: See [advanced.md](advanced.md)
**API reference**: See [reference.md](reference.md)
**Examples**: See [examples.md](examples.md)
```

### 長い参照ファイルには目次を含める

100行を超える参照ファイルには、先頭に目次を含めます。これにより、部分的な読み込みでもClaudeが利用可能な情報の全体像を把握できます。

```markdown
# API Reference

## Contents

- Authentication and setup
- Core methods (create, read, update, delete)
- Advanced features (batch operations, webhooks)
- Error handling patterns
- Code examples

## Authentication and setup
...

## Core methods
...
```

## Claudeの動作を観察する

スキルを反復する際、Claudeが実際にどのようにスキルを使用しているかに注目してください：

- **予期しない探索パス**: Claudeが予想外の順序でファイルを読む → 構造が直感的でない可能性
- **見逃された接続**: Claudeが重要なファイルへの参照を見逃す → リンクをより明示的にする
- **特定セクションへの過度な依存**: 同じファイルを繰り返し読む → その内容をメインSKILL.mdに含めるべきかも
- **無視されるコンテンツ**: バンドルしたファイルにアクセスしない → 不要か、シグナルが不十分

---

**参照元**: [SKILL.md](SKILL.md)
