# 設定ファイル仕様

このドキュメントは `~/.feedly/config.json` の仕様を定義します。

## ファイル配置

```
~/.feedly/
├── token          # APIトークン（必須）
└── config.json    # 設定ファイル（必須）
```

**重要**: 設定ファイルはスキル外（`~/.feedly/`）に配置。スキル本体には個人設定を含めない。

## 設定スキーマ

```json
{
  "token_file": "~/.feedly/token",
  "output_dir": "Project/FeedlyReports",
  "fetch_count": 100,
  "time_range_hours": 24,

  "scoring": {
    "weights": {
      "engagement": 0.30,
      "relevance": 0.40,
      "freshness": 0.20,
      "source_trust": 0.10
    },
    "thresholds": {
      "must_read": 80,
      "should_read": 60,
      "optional": 40
    }
  },

  "categories": [
    {
      "name": "カテゴリ表示名",
      "slug": "category-slug",
      "stream_id": "user/YOUR_USER_ID/category/CategoryName",
      "keywords": ["keyword1", "keyword2"],
      "trusted_sources": {
        "example.com": 80
      }
    }
  ],

  "deduplication": {
    "title_similarity_threshold": 0.7,
    "content_similarity_threshold": 0.8,
    "time_window_hours": 48
  },

  "report": {
    "max_articles_per_category": 20,
    "include_summary": true,
    "include_related": true,
    "language": "ja"
  }
}
```

## フィールド説明

### 基本設定

| フィールド | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| `token_file` | string | Yes | トークンファイルパス |
| `output_dir` | string | Yes | レポート出力先（プロジェクトルートからの相対パス） |
| `fetch_count` | int | No | カテゴリあたりの取得記事数（デフォルト: 100） |
| `time_range_hours` | int | No | 取得対象期間（デフォルト: 24時間） |

### scoring

| フィールド | 説明 |
|-----------|------|
| `weights.engagement` | 注目度の重み（0-1） |
| `weights.relevance` | キーワード関連度の重み（0-1） |
| `weights.freshness` | 鮮度の重み（0-1） |
| `weights.source_trust` | ソース信頼度の重み（0-1） |
| `thresholds.must_read` | MUST READの閾値（0-100） |
| `thresholds.should_read` | SHOULD READの閾値（0-100） |
| `thresholds.optional` | OPTIONALの閾値（0-100） |

### categories[]

| フィールド | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| `name` | string | Yes | 表示名 |
| `slug` | string | Yes | ファイル名用識別子（英数字・ハイフン） |
| `stream_id` | string | Yes | Feedly Stream ID |
| `keywords` | string[] | Yes | 関連度判定用キーワード |
| `trusted_sources` | object | No | ソース別信頼度（0-100） |

### deduplication

| フィールド | 説明 |
|-----------|------|
| `title_similarity_threshold` | タイトル類似度の閾値（0-1） |
| `content_similarity_threshold` | 本文類似度の閾値（0-1） |
| `time_window_hours` | 重複検出の時間窓 |

## Stream IDの取得方法

1. https://feedly.com にログイン
2. 対象カテゴリをクリック
3. URLから取得:
   ```
   https://feedly.com/i/category/user/xxxx-xxxx-xxxx/category/MyCategory
                                   └─────────────── Stream ID ───────────────┘
   ```

4. または API で取得:
   ```bash
   curl -H "Authorization: Bearer $(cat ~/.feedly/token)" \
        "https://api.feedly.com/v3/categories" | jq '.[].id'
   ```

## 設定例のパターン

### 仕事重視

```json
"weights": {
  "engagement": 0.20,
  "relevance": 0.50,
  "freshness": 0.20,
  "source_trust": 0.10
}
```

### 速報重視

```json
"weights": {
  "engagement": 0.40,
  "relevance": 0.20,
  "freshness": 0.30,
  "source_trust": 0.10
}
```

---

**Last Updated**: 2026-02-03
