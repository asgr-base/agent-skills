# 実行可能コードを含むスキル

## 解決し、委ねない

スキル用のスクリプトを書く際は、エラー条件を処理し、Claudeに委ねないでください。

✅ 良い例（エラーを明示的に処理）:
```python
def process_file(path):
    """Process a file, creating it if it doesn't exist."""
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        # Create file with default content instead of failing
        print(f"File {path} not found, creating default")
        with open(path, 'w') as f:
            f.write('')
        return ''
    except PermissionError:
        # Provide alternative instead of failing
        print(f"Cannot access {path}, using default")
        return ''
```

❌ 悪い例（Claudeに委ねる）:
```python
def process_file(path):
    # Just fail and let Claude figure it out
    return open(path).read()
```

## voodoo constants を避ける

設定パラメータは正当化され文書化されるべきです。根拠のない定数は避けてください（Ousterhout's law）。

✅ 良い例（自己文書化）:
```python
# HTTP requests typically complete within 30 seconds
# Longer timeout accounts for slow connections
REQUEST_TIMEOUT = 30

# Three retries balances reliability vs speed
# Most intermittent failures resolve by the second retry
MAX_RETRIES = 3
```

❌ 悪い例（マジックナンバー）:
```python
TIMEOUT = 47  # Why 47?
RETRIES = 5   # Why 5?
```

## ユーティリティスクリプトの提供

Claudeがスクリプトを書けるとしても、事前作成されたスクリプトには利点があります：

**利点**:

- 生成されたコードより信頼性が高い
- トークンを節約（コンテキストに含める必要なし）
- 時間を節約（コード生成不要）
- 使用間での一貫性を保証

**重要な区別**: 指示でClaudeが以下のどちらをすべきか明確にします：

- **スクリプトを実行**（最も一般的）: "Run `analyze_form.py` to extract fields"
- **参照として読む**（複雑なロジック用）: "See `analyze_form.py` for the field extraction algorithm"

### 例

````markdown
## Utility scripts

**analyze_form.py**: Extract all form fields from PDF

```bash
python scripts/analyze_form.py input.pdf > fields.json
```

Output format:
```json
{
  "field_name": {"type": "text", "x": 100, "y": 200},
  "signature": {"type": "sig", "x": 150, "y": 500}
}
```

**validate_boxes.py**: Check for overlapping bounding boxes

```bash
python scripts/validate_boxes.py fields.json
# Returns: "OK" or lists conflicts
```

**fill_form.py**: Apply field values to PDF

```bash
python scripts/fill_form.py input.pdf fields.json output.pdf
```
````

## ビジュアル分析の使用

入力を画像としてレンダリングできる場合、Claudeに分析させます：

````markdown
## Form layout analysis

1. Convert PDF to images:
   ```bash
   python scripts/pdf_to_images.py form.pdf
   ```

2. Analyze each page image to identify form fields
3. Claude can see field locations and types visually
````

Claudeの視覚機能がレイアウトや構造の理解を助けます。

## パッケージ依存関係

スキルはプラットフォーム固有の制限を持つコード実行環境で実行されます。

### プラットフォーム別の制約

| プラットフォーム | ネットワーク | パッケージインストール |
|------------------|--------------|------------------------|
| claude.ai | 設定による（完全/部分/なし） | 可能（npm, PyPI, GitHub） |
| Claude API | なし | 不可（事前インストールのみ） |
| Claude Code | 完全アクセス | ローカルのみ推奨 |

### 重要な考慮事項

- SKILL.mdに必要なパッケージをリスト
- [code execution tool documentation](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool)で利用可能であることを確認
- パッケージが利用可能であると仮定しない

````markdown
❌ 悪い例（インストールを前提）:
"Use the pdf library to process the file."

✅ 良い例（依存関係について明示）:
"Install required package: `pip install pypdf`

Then use it:
```python
from pypdf import PdfReader
reader = PdfReader("file.pdf")
```"
````

## 実行環境

スキルは、ファイルシステムアクセス、bashコマンド、コード実行機能を持つコード実行環境で実行されます。

### Claudeのスキルアクセス方法

1. **メタデータの事前読み込み**: 起動時、全スキルのYAMLフロントマターからnameとdescriptionがシステムプロンプトに読み込まれる
2. **オンデマンドファイル読み込み**: Claudeは必要に応じてbash Readツールを使用してSKILL.mdおよび他のファイルにアクセス
3. **効率的なスクリプト実行**: ユーティリティスクリプトは、その完全な内容をコンテキストに読み込まずにbash経由で実行可能。スクリプトの出力のみがトークンを消費
4. **大きなファイルにコンテキストペナルティなし**: 参照ファイル、データ、ドキュメントは実際に読み込まれるまでコンテキストトークンを消費しない

### 作成への影響

- **ファイルパスが重要**: Claudeはスキルディレクトリをファイルシステムのようにナビゲート。スラッシュ（`reference/guide.md`）を使用、バックスラッシュは使用しない
- **説明的なファイル名**: 内容を示す名前を使用：`form_validation_rules.md`、`doc2.md`ではなく
- **発見のための整理**: ドメインまたは機能ごとにディレクトリを構造化
  - 良い例: `reference/finance.md`, `reference/sales.md`
  - 悪い例: `docs/file1.md`, `docs/file2.md`
- **包括的なリソースのバンドル**: 完全なAPIドキュメント、豊富な例、大きなデータセットを含める；アクセスされるまでコンテキストペナルティなし
- **決定的な操作にはスクリプトを優先**: Claudeに検証コードを生成させるのではなく、`validate_form.py`を書く
- **実行意図を明確に**:
  - "Run `analyze_form.py` to extract fields"（実行）
  - "See `analyze_form.py` for the extraction algorithm"（参照として読む）
- **ファイルアクセスパターンのテスト**: 実際のリクエストでテストすることで、Claudeがディレクトリ構造をナビゲートできることを確認

## MCPツール参照

スキルがMCP（Model Context Protocol）ツールを使用する場合、「tool not found」エラーを避けるため、常に完全修飾ツール名を使用します。

**フォーマット**: `ServerName:tool_name`

**例**:
```markdown
Use the BigQuery:bigquery_schema tool to retrieve table schemas.
Use the GitHub:create_issue tool to create issues.
```

サーバープレフィックスがないと、特に複数のMCPサーバーが利用可能な場合にClaudeがツールを見つけられない可能性があります。

---

**参照元**: [SKILL.md](SKILL.md)
