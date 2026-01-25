# ワークフローとフィードバックループ

## 複雑なタスクのワークフロー

複雑な操作を明確な順次ステップに分解します。特に複雑なワークフローでは、Claudeがコピーして進捗を追跡できるチェックリストを提供します。

### 例1: 研究統合ワークフロー（コード不要のスキル）

````markdown
## Research synthesis workflow

Copy this checklist and track your progress:

```
Research Progress:
- [ ] Step 1: Read all source documents
- [ ] Step 2: Identify key themes
- [ ] Step 3: Cross-reference claims
- [ ] Step 4: Create structured summary
- [ ] Step 5: Verify citations
```

**Step 1: Read all source documents**

Review each document in the `sources/` directory. Note the main arguments and supporting evidence.

**Step 2: Identify key themes**

Look for patterns across sources. What themes appear repeatedly? Where do sources agree or disagree?

**Step 3: Cross-reference claims**

For each major claim, verify it appears in the source material. Note which source supports each point.

**Step 4: Create structured summary**

Organize findings by theme. Include:
- Main claim
- Supporting evidence from sources
- Conflicting viewpoints (if any)

**Step 5: Verify citations**

Check that every claim references the correct source document. If citations are incomplete, return to Step 3.
````

### 例2: PDFフォーム入力ワークフロー（コード付きスキル）

````markdown
## PDF form filling workflow

Copy this checklist and check off items as you complete them:

```
Task Progress:
- [ ] Step 1: Analyze the form (run analyze_form.py)
- [ ] Step 2: Create field mapping (edit fields.json)
- [ ] Step 3: Validate mapping (run validate_fields.py)
- [ ] Step 4: Fill the form (run fill_form.py)
- [ ] Step 5: Verify output (run verify_output.py)
```

**Step 1: Analyze the form**

Run: `python scripts/analyze_form.py input.pdf`

This extracts form fields and their locations, saving to `fields.json`.

**Step 2: Create field mapping**

Edit `fields.json` to add values for each field.

**Step 3: Validate mapping**

Run: `python scripts/validate_fields.py fields.json`

Fix any validation errors before continuing.

**Step 4: Fill the form**

Run: `python scripts/fill_form.py input.pdf fields.json output.pdf`

**Step 5: Verify output**

Run: `python scripts/verify_output.py output.pdf`

If verification fails, return to Step 2.
````

## フィードバックループの実装

**一般的なパターン**: バリデータを実行 → エラーを修正 → 繰り返し

このパターンは出力品質を大幅に向上させます。

### 例1: スタイルガイドコンプライアンス（コード不要）

```markdown
## Content review process

1. Draft your content following the guidelines in STYLE_GUIDE.md
2. Review against the checklist:
   - Check terminology consistency
   - Verify examples follow the standard format
   - Confirm all required sections are present
3. If issues found:
   - Note each issue with specific section reference
   - Revise the content
   - Review the checklist again
4. Only proceed when all requirements are met
5. Finalize and save the document
```

### 例2: ドキュメント編集プロセス（コード付き）

```markdown
## Document editing process

1. Make your edits to `word/document.xml`
2. **Validate immediately**: `python ooxml/scripts/validate.py unpacked_dir/`
3. If validation fails:
   - Review the error message carefully
   - Fix the issues in the XML
   - Run validation again
4. **Only proceed when validation passes**
5. Rebuild: `python ooxml/scripts/pack.py unpacked_dir/ output.docx`
6. Test the output document
```

## 条件付きワークフローパターン

決定ポイントを通じてClaudeをガイドします：

```markdown
## Document modification workflow

1. Determine the modification type:

   **Creating new content?** → Follow "Creation workflow" below
   **Editing existing content?** → Follow "Editing workflow" below

2. Creation workflow:
   - Use docx-js library
   - Build document from scratch
   - Export to .docx format

3. Editing workflow:
   - Unpack existing document
   - Modify XML directly
   - Validate after each change
   - Repack when complete
```

**Tip**: ワークフローが大きく複雑になった場合は、別ファイルに移動し、タスクに応じて適切なファイルを読むようClaudeに指示します。

## 検証可能な中間出力の作成

Claudeが複雑でオープンエンドなタスクを実行する場合、ミスを犯す可能性があります。「計画-検証-実行」パターンは、まずClaudeに構造化形式で計画を作成させ、実行前にスクリプトでその計画を検証することで、早期にエラーをキャッチします。

### 例

スプレッドシートに基づいてPDFの50個のフォームフィールドを更新するようClaudeに依頼するとします。検証なしでは：

- 存在しないフィールドを参照
- 競合する値を作成
- 必須フィールドを見逃す
- 更新を誤って適用

### 解決策

ワークフローに中間`changes.json`ファイルを追加し、変更を適用する前に検証：

**分析 → 計画ファイル作成 → 計画検証 → 実行 → 確認**

### このパターンが機能する理由

- **早期にエラーをキャッチ**: 検証は変更が適用される前に問題を発見
- **機械検証可能**: スクリプトが客観的な検証を提供
- **可逆的な計画**: Claudeは元のファイルに触れずに計画を繰り返すことができる
- **明確なデバッグ**: エラーメッセージが特定の問題を指摘

### 使用タイミング

- バッチ操作
- 破壊的変更
- 複雑な検証ルール
- 重要性の高い操作

### 実装のヒント

検証スクリプトを詳細なエラーメッセージを出力するように作成：

```
"Field 'signature_date' not found. Available fields: customer_name, order_total, signature_date_signed"
```

これによりClaudeが問題を修正しやすくなります。

---

**参照元**: [SKILL.md](SKILL.md)
