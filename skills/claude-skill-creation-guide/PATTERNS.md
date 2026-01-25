# 一般的なパターン集

## Two-Instance Skillパターン

スキル作成時に2つのClaudeインスタンスを使用する効果的なパターン:

```
┌─────────────────────────────┬─────────────────────────────┐
│       Claude A              │       Claude B              │
│   (スキル作成エージェント)  │   (スキルテストエージェント)│
│                             │                             │
│ - スキル構造設計            │ - 実際のタスクでテスト      │
│ - コンテンツ作成            │ - ギャップ特定              │
│ - 改善反復                  │ - フィードバック提供        │
└─────────────────────────────┴─────────────────────────────┘
              │                           │
              └───────────┬───────────────┘
                          │
                          ▼
                   観察に基づく改善
```

### ワークフロー

1. **Claude Aとタスク完了**: スキルなしで問題を解決、再利用パターンを特定
2. **Claude Aにスキル作成依頼**: 簡潔さをレビュー
3. **Claude Bでテスト**: 実際のタスクでスキルを使用
4. **観察に基づき改善**: Claude Bの動作を分析し、Claude Aで修正

### 観察ポイント

- スキルがトリガーされるか
- 指示に従っているか
- 参照ファイルにアクセスしているか
- エラーからリカバリできるか

---

## モデル選択ガイドライン

スキル開発の各フェーズで適切なモデルを選択:

| フェーズ | 推奨モデル | 理由 |
|----------|-----------|------|
| スキル設計 | Sonnet/Opus | 構造理解が必要 |
| コンテンツ作成 | Sonnet | バランス良好 |
| 簡単なテスト | Haiku | 高速・低コスト |
| 複雑なテスト | Sonnet | 実際の使用に近い |
| 最終検証 | Opus | 厳格な評価 |
| エッジケース検証 | Haiku | スキルの堅牢性確認 |

### モデル別の特性

- **Haiku**: 明確な指示に従う能力が高い、曖昧な指示は苦手
- **Sonnet**: バランスの取れた推論、コーディングに最適
- **Opus**: 深い推論、複雑なコンテキスト理解

**Tip**: Haikuでうまく機能するスキルは、より大きなモデルでも確実に機能します。

---

## テンプレートパターン

出力フォーマットのテンプレートを提供します。必要性に応じて厳格さを調整します。

### 厳格な要件の場合（APIレスポンスやデータフォーマット）

````markdown
## Report structure

ALWAYS use this exact template structure:

```markdown
# [Analysis Title]

## Executive summary
[One-paragraph overview of key findings]

## Key findings
- Finding 1 with supporting data
- Finding 2 with supporting data
- Finding 3 with supporting data

## Recommendations
1. Specific actionable recommendation
2. Specific actionable recommendation
```
````

### 柔軟なガイダンスの場合（適応が有用な時）

````markdown
## Report structure

Here is a sensible default format, but use your best judgment based on the analysis:

```markdown
# [Analysis Title]

## Executive summary
[Overview]

## Key findings
[Adapt sections based on what you discover]

## Recommendations
[Tailor to the specific context]
```

Adjust sections as needed for the specific analysis type.
````

## 例パターン

出力品質が例を見ることに依存するスキルでは、通常のプロンプティングと同様に入力/出力ペアを提供します：

````markdown
## Commit message format

Generate commit messages following these examples:

**Example 1:**
Input: Added user authentication with JWT tokens
Output:
```
feat(auth): implement JWT-based authentication

Add login endpoint and token validation middleware
```

**Example 2:**
Input: Fixed bug where dates displayed incorrectly in reports
Output:
```
fix(reports): correct date formatting in timezone conversion

Use UTC timestamps consistently across report generation
```

**Example 3:**
Input: Updated dependencies and refactored error handling
Output:
```
chore: update dependencies and refactor error handling

- Upgrade lodash to 4.17.21
- Standardize error response format across endpoints
```

Follow this style: type(scope): brief description, then detailed explanation.
````

例は、説明だけよりも望ましいスタイルと詳細レベルをClaudeが理解するのに役立ちます。

## コンテンツガイドライン

### 時間依存情報を避ける

時間経過で古くなる情報を含めないでください：

❌ 悪い例（時間依存）:
```markdown
If you're doing this before August 2025, use the old API.
After August 2025, use the new API.
```

✅ 良い例（「古いパターン」セクション使用）:
```markdown
## Current method

Use the v2 API endpoint: `api.example.com/v2/messages`

## Old patterns

<details>
<summary>Legacy v1 API (deprecated 2025-08)</summary>

The v1 API used: `api.example.com/v1/messages`

This endpoint is no longer supported.
</details>
```

古いパターンセクションはメインコンテンツを乱雑にせずに歴史的コンテキストを提供します。

### 一貫した用語を使用

1つの用語を選び、スキル全体で使用します：

✅ 良い例（一貫性）:

- 常に "API endpoint"
- 常に "field"
- 常に "extract"

❌ 悪い例（不一貫）:

- "API endpoint", "URL", "API route", "path"を混在
- "field", "box", "element", "control"を混在
- "extract", "pull", "get", "retrieve"を混在

一貫性はClaudeが指示を理解し従うのに役立ちます。

## アンチパターン回避

### Windowsスタイルのパスを避ける

ファイルパスには常にフォワードスラッシュを使用、Windowsでも：

- ✓ **良い**: `scripts/helper.py`, `reference/guide.md`
- ✗ **避ける**: `scripts\helper.py`, `reference\guide.md`

Unixスタイルのパスはすべてのプラットフォームで機能しますが、Windowsスタイルのパスはunixシステムでエラーを引き起こします。

### 過剰な選択肢の提供を避ける

必要でない限り複数のアプローチを提示しない：

````markdown
❌ 悪い例（多すぎる選択肢）:
"You can use pypdf, or pdfplumber, or PyMuPDF, or pdf2image, or..."

✅ 良い例（デフォルトを提供し、エスケープハッチ付き）:
"Use pdfplumber for text extraction:
```python
import pdfplumber
```

For scanned PDFs requiring OCR, use pdf2image with pytesseract instead."
````

## セキュリティ考慮事項

### 信頼できるソースのみを使用

**強く推奨**: 以下のスキルのみを使用

- 自分で作成したスキル
- Anthropicから入手したスキル

スキルは指示とコードを通じてClaudeに新しい能力を提供します。これにより強力になりますが、悪意のあるスキルがツールを呼び出したり、スキルの記載目的と一致しない方法でコードを実行するようClaudeを指示する可能性もあります。

### 主要なセキュリティ考慮事項

- **徹底的な監査**: スキルにバンドルされているすべてのファイルをレビュー：SKILL.md、スクリプト、画像、その他のリソース。予期しないネットワーク呼び出し、ファイルアクセスパターン、スキルの記載目的と一致しない操作など、異常なパターンを探す

- **外部ソースはリスク**: 外部URLからデータを取得するスキルは特にリスクが高い。取得されたコンテンツに悪意のある指示が含まれる可能性があるため。時間経過で外部依存関係が変更されると、信頼できるスキルでも侵害される可能性がある

- **ツールの誤用**: 悪意のあるスキルは有害な方法でツール（ファイル操作、bashコマンド、コード実行）を呼び出すことができる

- **データ露出**: 機密データへのアクセスを持つスキルは、外部システムに情報を漏洩するように設計される可能性がある

- **ソフトウェアのインストールと同様に扱う**: 信頼できるソースからのスキルのみを使用。機密データまたは重要な操作へのアクセスを持つ本番システムにスキルを統合する際は特に注意

---

## 追加のアンチパターン

### 深すぎる参照階層

❌ 悪い例:
```
SKILL.md → advanced.md → details.md → specifics.md
```

✅ 良い例:
```
SKILL.md ─┬─ advanced.md
          ├─ details.md
          └─ specifics.md
```

**参照は常に1レベルの深さに保つ**

### 曖昧な指示

❌ 悪い例:
```markdown
- パフォーマンスに気をつける
- セキュリティを考慮する
```

✅ 良い例:
```markdown
- MUST: N+1クエリを避ける（eager loadingを使用）
- NEVER: ユーザー入力をサニタイズせずにSQLに渡さない
```

### 自明な説明

❌ 悪い例:
```markdown
PDF（Portable Document Format）は、ドキュメントを
プラットフォーム非依存で表現するためのファイル形式です。
```

Claudeは既にPDFが何かを知っています。スキルに固有の情報のみを含めてください。

### 評価なしの開発

❌ 悪い例:
1. スキルを書く
2. 完成と仮定
3. 問題が発生してから修正

✅ 良い例:
1. ギャップを特定
2. 評価を作成
3. 最小限のスキルを書く
4. 評価で検証
5. 反復

---

## 関連ガイド

| ファイル | 内容 |
|----------|------|
| [SKILL.md](SKILL.md) | メインガイド |
| [claude-code-guide](../claude-code-guide/SKILL.md) | Claude Code機能全般 |

---

**参照元**: [SKILL.md](SKILL.md)
