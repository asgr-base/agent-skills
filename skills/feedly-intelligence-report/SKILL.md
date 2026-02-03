---
name: feedly-intelligence-report
description: Feedlyから記事を取得し、重複統合・関連度スコアリング・注目度ランキングを行いインテリジェンスレポートを生成。Feedly、RSS、ニュースレポート、記事まとめ関連の質問時に使用。
---

# Feedly Intelligence Report

Feedlyの記事を分析し、カテゴリ別のインテリジェンスレポートを生成するスキル。

## クイックリファレンス

| タスク | コマンド |
|--------|----------|
| 全カテゴリレポート | `/feedly-intelligence-report` |
| 特定カテゴリ | `/feedly-intelligence-report <slug>` |
| セットアップ確認 | `python scripts/feedly_fetch.py --test` |
| 記事を既読にする | `python scripts/feedly_fetch.py --mark-read /tmp/feedly_articles.json` |

## 前提条件

1. **Feedly Developer Access Token**: [SETUP.md](SETUP.md)参照
2. **設定ファイル**: `~/.feedly/config.json` を作成（[CONFIG.md](CONFIG.md)参照）

**重要**: 個人設定（カテゴリ、キーワード等）はスキル外の `~/.feedly/` に配置。

## ワークフロー

### 1. 記事取得

```bash
python scripts/feedly_fetch.py --config ~/.feedly/config.json --output /tmp/feedly_articles.json
```

**出力**: JSON形式の記事リスト（engagement, engagementRate含む）

### 2. 記事分析

取得した記事に対し以下を実行:

#### 重複・類似記事の統合
- タイトル類似度（Jaccard係数）で重複検出
- 同一ニュースの複数ソースをグループ化
- 代表記事を選定（engagementRate最高のもの）

#### スコアリング

| 指標 | 計算方法 | デフォルト重み |
|------|----------|----------------|
| 注目度 | `engagementRate` × 100 | 30% |
| 関連度 | カテゴリキーワードマッチ数 | 40% |
| 鮮度 | 24時間以内=100, 48時間=50, それ以上=25 | 20% |
| ソース信頼度 | 設定ファイルで定義 | 10% |

**総合スコア** = Σ(指標 × 重み)

#### ライン引き

| ライン | 条件 | 推奨アクション |
|--------|------|----------------|
| **MUST READ** | スコア ≥ 80 | 必読。詳細確認推奨 |
| **SHOULD READ** | 60 ≤ スコア < 80 | 時間があれば読む |
| **OPTIONAL** | 40 ≤ スコア < 60 | 興味があれば |
| **SKIP** | スコア < 40 | スキップ可 |

### 3. レポート生成

出力先: `Daily/YYYY-MM/YYYY-MM-DD（曜日）_feeds-report.md`

```
Daily/
└── YYYY-MM/
    └── YYYY-MM-DD（曜日）_feeds-report.md
```

**例**: `Daily/2026-02/2026-02-03（火）_feeds-report.md`

### 4. レポートフォーマット

```markdown
---
createDate: YYYY-MM-DD
author:
  - claude_code
tags:
  - "#feedly"
  - "#カテゴリslug"
---

# [カテゴリ名] インテリジェンスレポート

**生成日**: YYYY-MM-DD HH:MM
**対象期間**: 過去24時間
**記事数**: X件（重複統合後）

## MUST READ (X件)

### 1. [記事タイトル](URL)
- **スコア**: 85 | **注目度**: 2.3 | **ソース**: Example.com
- **要約**: 記事の要約を2-3文で
- **関連記事**: [類似記事1](URL), [類似記事2](URL)

## SHOULD READ (X件)
...

## 統計

| 指標 | 値 |
|------|-----|
| 取得記事数 | X |
| 重複統合数 | X |
| 平均engagementRate | X |
```

### 5. 既読確認（ユーザー確認必須）

レポート生成後、**必ずユーザーに確認**してから既読処理を行う。

```
YOU MUST: レポート生成後、以下の質問をユーザーに表示:

「レポートを生成しました。取得した{N}件の記事をFeedlyで既読にしますか？」

- 選択肢1: はい、既読にする
- 選択肢2: いいえ、未読のまま
```

ユーザーが「はい」を選択した場合のみ実行:

```bash
python scripts/feedly_fetch.py --mark-read /tmp/feedly_articles.json
```

**注意**:
- 既読にするのは取得したJSONファイル内の記事のみ
- 一度既読にすると元に戻せない
- レポートに含まれなかった記事（SKIPカテゴリ）も既読になる

## エラーハンドリング

| エラー | 対処 |
|--------|------|
| トークン期限切れ | [SETUP.md](SETUP.md)の手順で再取得 |
| API制限超過 | 翌日まで待つ |
| カテゴリ未設定 | `~/.feedly/config.json` を確認 |
| 設定ファイルなし | [CONFIG.md](CONFIG.md)を参照して作成 |
| 既読マーク失敗 | トークン権限を確認（readとwriteの両方が必要） |

## 注意事項

- **APIリクエスト制限**: 月間100,000リクエストまで（無料プラン）
- **トークン有効期限**: 3ヶ月（自動延長なし）。Web Access Tokenは1週間程度
- **engagement未取得**: 一部記事はengagement情報なし（0として扱う）
- **URL取得**: はてブ等の集約サイト経由の場合、`canonicalUrl`がnullになることがある。その場合は`alternate[0].href`または`originId`から元記事URLを取得

## 詳細リファレンス

| ファイル | 内容 |
|----------|------|
| [SETUP.md](SETUP.md) | APIトークン取得・環境構築 |
| [CONFIG.md](CONFIG.md) | 設定ファイル仕様 |
| [scripts/feedly_fetch.py](scripts/feedly_fetch.py) | Feedly API操作スクリプト |
| [config-sample.json](config-sample.json) | 設定ファイルのサンプル |

---

**Version**: 1.3.0
**Last Updated**: 2026-02-03
