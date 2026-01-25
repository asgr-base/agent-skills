# プラットフォーム別の利用

スキルは複数のプラットフォームで利用可能ですが、それぞれ異なる特性があります。

## プラットフォーム比較

| プラットフォーム | スキルの共有範囲 | ネットワーク | パッケージインストール |
|------------------|------------------|--------------|------------------------|
| **Claude API** | 組織全体 | なし | 不可（事前インストールのみ） |
| **Claude.ai** | 個人のみ | 設定による | 可能（npm, PyPI） |
| **Claude Code** | Personal/Project | 完全アクセス | ローカルのみ推奨 |
| **Agent SDK** | ファイルシステムベース | 設定による | 設定による |

## Claude API

### スキルのアップロード

`/v1/skills`エンドポイントでスキルをアップロード:

```bash
curl -X POST https://api.anthropic.com/v1/skills \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -F "skill=@my-skill.zip"
```

### 制約

- ネットワークアクセスなし
- 事前インストールされたパッケージのみ使用可能
- 組織全体で共有

## Claude.ai

### スキルのアップロード

1. 設定 > Features に移動
2. Skills セクションでzipファイルをアップロード

### 制約

- 個人のみで使用
- ネットワークアクセスは設定による（完全/部分/なし）
- npm, PyPI, GitHubからパッケージインストール可能

## Claude Code

### スキルの配置

```bash
# ユーザーレベル（全プロジェクト共通）
~/.claude/skills/my-skill/SKILL.md

# プロジェクトレベル（特定プロジェクトのみ）
.claude/skills/my-skill/SKILL.md
```

### 特徴

- 完全なネットワークアクセス
- ローカル環境でのパッケージインストール
- ファイルシステムへの完全アクセス
- Git統合

### 推奨事項

- ローカルパッケージのみ使用（グローバルインストールを避ける）
- プロジェクト固有のスキルは`.claude/skills/`に配置
- 共通スキルは`~/.claude/skills/`に配置

## Agent SDK

### スキルの有効化

`allowed_tools`に`"Skill"`を含める:

```python
from anthropic import Agent

agent = Agent(
    allowed_tools=["Skill", "Read", "Write", "Bash"],
    skills_path="./skills"
)
```

### 特徴

- ファイルシステムベースのスキル管理
- プログラマティックなスキル制御
- カスタム権限設定

## 注意事項

### スキルの同期

**重要**: スキルはプラットフォーム間で自動同期されません。

各プラットフォームで個別に管理が必要:
- Claude APIでアップロードしたスキルはClaude Codeで自動利用不可
- Claude Codeのスキルは手動でエクスポート/インポートが必要

### ランタイム環境の確認

スキル内でランタイム環境を確認する場合:

```python
import os

# Claude Code環境の検出
is_claude_code = os.environ.get("CLAUDE_CODE") == "1"

# ネットワークアクセスの確認
try:
    import requests
    requests.get("https://api.example.com", timeout=1)
    has_network = True
except:
    has_network = False
```

---

**参照元**: [SKILL.md](SKILL.md)
