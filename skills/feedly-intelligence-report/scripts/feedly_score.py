#!/usr/bin/env python3
"""
Feedly記事スコアリングスクリプト

4指標に基づいて記事をスコアリングし、優先度別レポートを生成:
- 注目度 (engagementRate)
- 関連度 (キーワードマッチ)
- 鮮度 (公開からの経過時間)
- ソース信頼度 (設定ファイルで定義)

Usage:
    python feedly_score.py --config ~/.feedly/config.json --input /tmp/feedly_articles.json --output /tmp/scored_report.md
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote

try:
    import requests
except ImportError:
    requests = None  # オプショナル依存


def expand_path(path: str) -> Path:
    """パスを展開（~ 対応）"""
    return Path(os.path.expanduser(path))


def get_japanese_weekday(date: datetime = None) -> str:
    """日本語の曜日を取得"""
    weekdays = ["月", "火", "水", "木", "金", "土", "日"]
    if date is None:
        date = datetime.now()
    return weekdays[date.weekday()]


def generate_default_output_path(base_dir: str = "Daily") -> str:
    """
    デフォルト出力パスを生成

    Format: {base_dir}/YYYY-MM/YYYY-MM-DD（曜日）_feeds-report.md
    Example: Daily/2026-02/2026-02-03（火）_feeds-report.md
    """
    now = datetime.now()
    year_month = now.strftime("%Y-%m")
    date_str = now.strftime("%Y-%m-%d")
    weekday = get_japanese_weekday(now)

    return f"{base_dir}/{year_month}/{date_str}（{weekday}）_feeds-report.md"


def load_config(config_file: str) -> dict:
    """設定ファイルを読み込む"""
    path = expand_path(config_file)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    return json.loads(path.read_text())


def load_articles(filepath: str) -> tuple[list, dict]:
    """
    JSONファイルから記事を読み込む

    Returns:
        tuple: (記事リスト, メタデータ)
    """
    path = expand_path(filepath)
    if not path.exists():
        return [], {}

    with open(path) as f:
        data = json.load(f)

    # 新形式（カテゴリ別）か旧形式（items直下）かを判定
    if "categories" in data:
        # 新形式: 全カテゴリの記事を統合
        all_articles = []
        for slug, cat_data in data["categories"].items():
            for article in cat_data.get("articles", []):
                article["_category_slug"] = slug
                article["_category_name"] = cat_data.get("name", slug)
                article["_category_keywords"] = cat_data.get("keywords", [])
                all_articles.append(article)
        return all_articles, data.get("metadata", {})
    else:
        # 旧形式
        return data.get("items", []), {}


def extract_url(article: dict) -> str:
    """記事URLを取得（優先順位: url > canonicalUrl > alternate > originId）"""
    # 既に抽出済みのurl
    if article.get("url"):
        return article["url"]
    if article.get("canonicalUrl"):
        return article["canonicalUrl"]
    alternate = article.get("alternate", [])
    if alternate and len(alternate) > 0:
        href = alternate[0].get("href")
        if href:
            return href
    return article.get("originId", "")


def extract_domain(url: str) -> str:
    """URLからドメインを抽出"""
    if not url:
        return ""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc.lower()
    except Exception:
        return ""


def is_paywalled(article: dict, paywalled_domains: list) -> bool:
    """記事がペイウォール付きかどうかを判定"""
    if not paywalled_domains:
        return False
    url = extract_url(article)
    domain = extract_domain(url)
    for pd in paywalled_domains:
        if pd.lower() in domain:
            return True
    return False


def hatena_entry_url(url: str) -> str:
    """はてなブックマークのエントリーページURLを生成"""
    if not url:
        return ""
    # https:// を除去して s/ プレフィックスを付ける
    if url.startswith("https://"):
        return f"https://b.hatena.ne.jp/entry/s/{url[8:]}"
    elif url.startswith("http://"):
        return f"https://b.hatena.ne.jp/entry/{url[7:]}"
    return ""


def normalize_title(title: str) -> str:
    """タイトルを正規化（重複検出用）"""
    for sep in [" | ", " - ", " -- ", "｜", "：", " :: "]:
        if sep in title:
            title = title.split(sep)[0]
    return title.strip()[:50]


# =============================================================================
# ソーシャルメトリクス取得（はてブ + Hacker News）
# =============================================================================

def fetch_hatena_bookmark_count(url: str) -> int:
    """
    はてなブックマーク数を取得

    Args:
        url: 記事URL

    Returns:
        ブックマーク数（エラー時は0）
    """
    if not requests:
        return 0
    try:
        api_url = f"https://bookmark.hatenaapis.com/count/entry?url={quote(url, safe='')}"
        resp = requests.get(api_url, timeout=5)
        if resp.status_code == 200:
            return int(resp.text) if resp.text.isdigit() else 0
    except Exception:
        pass
    return 0


def fetch_hn_points(url: str) -> tuple[int, str]:
    """
    Hacker News のポイント数とobjectIDを取得

    Args:
        url: 記事URL

    Returns:
        (ポイント数, objectID) のタプル（エラー時は (0, "")）
    """
    if not requests:
        return 0, ""
    try:
        api_url = f"https://hn.algolia.com/api/v1/search?query={quote(url, safe='')}&restrictSearchableAttributes=url&hitsPerPage=1"
        resp = requests.get(api_url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            hits = data.get("hits", [])
            if hits:
                points = hits[0].get("points", 0) or 0
                object_id = hits[0].get("objectID", "") or ""
                return points, object_id
    except Exception:
        pass
    return 0, ""


def hn_entry_url(object_id: str) -> str:
    """Hacker NewsのエントリーページURLを生成"""
    if not object_id:
        return ""
    return f"https://news.ycombinator.com/item?id={object_id}"


def fetch_social_metrics_for_articles(articles: list, max_workers: int = 10) -> dict:
    """
    複数記事のソーシャルメトリクスを並列取得

    Args:
        articles: 記事リスト
        max_workers: 並列ワーカー数

    Returns:
        {url: {"hatena": int, "hn": int}} の辞書
    """
    if not requests:
        print("Warning: requests not installed, skipping social metrics", file=sys.stderr)
        return {}

    urls = [extract_url(a) for a in articles if extract_url(a)]
    urls = list(set(urls))  # 重複除去

    print(f"Fetching social metrics for {len(urls)} URLs...", file=sys.stderr)

    metrics = {}

    def fetch_metrics(url: str) -> tuple:
        hatena = fetch_hatena_bookmark_count(url)
        hn_points, hn_id = fetch_hn_points(url)
        return url, {"hatena": hatena, "hn": hn_points, "hn_id": hn_id}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fetch_metrics, url): url for url in urls}
        for future in as_completed(futures):
            try:
                url, result = future.result()
                metrics[url] = result
            except Exception:
                pass

    # 統計を表示
    hatena_total = sum(m.get("hatena", 0) for m in metrics.values())
    hn_total = sum(m.get("hn", 0) for m in metrics.values())
    print(f"  → はてブ合計: {hatena_total}, HN合計: {hn_total}", file=sys.stderr)

    return metrics


def calculate_engagement_score(article: dict, social_metrics: dict = None) -> tuple[float, dict]:
    """
    注目度スコアを計算 (0-100) と内訳を返す

    複数指標を統合:
    - engagementRate (Feedly)
    - はてなブックマーク数
    - Hacker News ポイント

    スコア計算:
    - engagementRate: 5倍して正規化（最大50点）
    - はてブ: 1ブクマ=2点（最大40点）
    - HN: 1ポイント=0.5点（最大40点）
    - 合計を100点満点にクリップ

    Returns:
        tuple: (総合スコア, {"feedly": x, "hatena": y, "hn": z})
    """
    rate = article.get("engagement_rate") or article.get("engagementRate") or 0
    feedly_score = min(rate * 5, 50)

    # ソーシャルメトリクス
    url = extract_url(article)
    metrics = (social_metrics or {}).get(url, {})
    hatena_count = metrics.get("hatena", 0)
    hn_points = metrics.get("hn", 0)
    hn_id = metrics.get("hn_id", "")

    hatena_score = min(hatena_count * 2, 40)  # 20ブクマで40点
    hn_score = min(hn_points * 0.5, 40)  # 80ポイントで40点

    total = min(feedly_score + hatena_score + hn_score, 100)

    breakdown = {
        "feedly": round(feedly_score, 1),
        "hatena": hatena_count,
        "hn": hn_points,
        "hn_id": hn_id
    }

    return total, breakdown


def expand_with_synonyms(keywords: list, synonym_groups: list) -> list:
    """
    キーワードを類義語グループで展開

    Args:
        keywords: 元のキーワードリスト
        synonym_groups: 類義語グループのリスト（各グループは類義語のリスト）

    Returns:
        展開されたキーワードリスト（各要素は類義語セット）
    """
    expanded = []
    used_keywords = set()

    # 類義語グループに属するキーワードを展開
    for kw in keywords:
        if kw in used_keywords:
            continue

        kw_lower = kw.lower()
        found_group = None

        for group in synonym_groups:
            group_lower = [g.lower() for g in group]
            if kw_lower in group_lower:
                found_group = group
                break

        if found_group:
            # グループ全体を1つのマッチ対象として追加
            expanded.append(set(g.lower() for g in found_group))
            used_keywords.update(g.lower() for g in found_group)
        else:
            # 類義語グループに属さないキーワードは単独で追加
            expanded.append({kw_lower})
            used_keywords.add(kw_lower)

    return expanded


def calculate_relevance_score(
    article: dict,
    keywords: list,
    global_keywords: list = None,
    synonym_groups: list = None
) -> tuple[float, list]:
    """
    関連度スコアを計算 (0-100) とマッチしたキーワードを返す

    タイトルと本文でキーワード（類義語含む）マッチをカウント。
    タイトルマッチは重み2倍。
    1つでもマッチすれば基礎点を付与。

    Returns:
        tuple: (スコア, マッチしたキーワードのリスト)
    """
    if not keywords and not global_keywords:
        return 50, []  # キーワード未設定時はニュートラル

    all_keywords = list(set((keywords or []) + (global_keywords or [])))
    if not all_keywords:
        return 50, []

    # 類義語グループで展開
    keyword_sets = expand_with_synonyms(all_keywords, synonym_groups or [])

    title = article.get("title", "").lower()
    # contentはdictの場合がある（Feedly API形式）
    content_raw = article.get("content", "")
    if isinstance(content_raw, dict):
        content = content_raw.get("content", "").lower()
    else:
        content = str(content_raw).lower()

    title_matches = 0
    content_matches = 0
    matched_keywords = []

    def is_word_match(keyword: str, text: str) -> bool:
        """
        単語境界を考慮したキーワードマッチ

        英語キーワード: 単語境界(\b)でマッチ（ml が html にマッチしない）
        日本語キーワード: そのまま部分一致（単語境界の概念がない）
        短い英字（ai, ml等）: 日本語テキスト内では英字単語として独立している場合のみマッチ
        """
        # キーワードが日本語を含むかチェック
        keyword_has_japanese = any('\u3040' <= c <= '\u9fff' for c in keyword)

        if keyword_has_japanese:
            # 日本語キーワードは部分一致
            return keyword in text
        else:
            # 英字キーワード
            # テキストに日本語（ひらがな・カタカナ・漢字）が含まれるかチェック
            text_has_japanese = any(
                '\u3040' <= c <= '\u309f' or  # ひらがな
                '\u30a0' <= c <= '\u30ff' or  # カタカナ
                '\u4e00' <= c <= '\u9fff'     # 漢字
                for c in text
            )

            # 短い英字キーワード（ai, ml, it等）かつ日本語テキストの場合
            # 英字の塊として独立している場合のみマッチ（前後が英字でない）
            if len(keyword) <= 3 and keyword.isalpha() and text_has_japanese:
                # 日本語文字または文字列境界で囲まれた英字キーワードにマッチ
                # 例: 「先進的AI利活用」の「AI」にはマッチ、「Zaim」の「ai」にはマッチしない
                pattern = r'(?<![a-zA-Z])' + re.escape(keyword) + r'(?![a-zA-Z])'
                return bool(re.search(pattern, text, re.IGNORECASE))

            # それ以外は単語境界でマッチ
            pattern = r'\b' + re.escape(keyword) + r'\b'
            return bool(re.search(pattern, text, re.IGNORECASE))

    for kw_set in keyword_sets:
        # セット内のいずれかがマッチすればカウント
        title_matched_kw = None
        content_matched_kw = None

        for kw in kw_set:
            if is_word_match(kw.lower(), title) and not title_matched_kw:
                title_matched_kw = kw
            if is_word_match(kw.lower(), content) and not content_matched_kw:
                content_matched_kw = kw

        if title_matched_kw:
            title_matches += 1
            if title_matched_kw not in matched_keywords:
                matched_keywords.append(title_matched_kw)
        if content_matched_kw:
            content_matches += 1
            if content_matched_kw not in matched_keywords and content_matched_kw != title_matched_kw:
                matched_keywords.append(content_matched_kw)

    # スコア計算（改良版）
    # - 1つでもマッチすれば基礎点30
    # - マッチ数に応じて加点
    total_keyword_sets = len(keyword_sets)
    if total_keyword_sets == 0:
        return 50, []

    # タイトルマッチは2倍の重み
    total_matches = title_matches * 2 + content_matches
    max_possible = total_keyword_sets * 3

    # 基礎点 + マッチ率による加点
    if total_matches > 0:
        base_score = 30  # 1つでもマッチすれば基礎点
        match_bonus = (total_matches / max_possible) * 70  # 最大70点追加
        return min(base_score + match_bonus, 100), matched_keywords
    else:
        return 0, []  # マッチなしは0点


def calculate_freshness_score(article: dict) -> float:
    """
    鮮度スコアを計算 (0-100)

    - 24時間以内: 100
    - 48時間以内: 50
    - それ以上: 25
    """
    published = article.get("published", 0)
    if not published:
        return 25  # 公開日不明は低スコア

    # ミリ秒 → 秒に変換
    if published > 1e12:
        published = published / 1000

    now = datetime.now().timestamp()
    hours_ago = (now - published) / 3600

    if hours_ago <= 24:
        return 100
    elif hours_ago <= 48:
        return 50
    elif hours_ago <= 72:
        return 35
    else:
        return 25


def calculate_source_trust_score(article: dict, trusted_sources: dict) -> float:
    """
    ソース信頼度スコアを計算 (0-100)

    設定ファイルで定義された信頼度を使用。
    未定義のソースは50点。
    """
    source_title = article.get("source", {}).get("title", "")
    if not source_title:
        origin = article.get("origin", {})
        source_title = origin.get("title", "")

    # 部分一致でチェック
    for source_name, trust_value in trusted_sources.items():
        if source_name.lower() in source_title.lower():
            return trust_value * 100

    return 50  # デフォルト


def calculate_total_score(article: dict, config: dict, category_config: dict = None, social_metrics: dict = None) -> dict:
    """
    総合スコアを計算

    Args:
        article: 記事データ
        config: 設定
        category_config: カテゴリ設定（未使用、互換性のため残す）
        social_metrics: ソーシャルメトリクス {url: {"hatena": int, "hn": int}}

    Returns:
        dict: 各指標のスコアと総合スコア
    """
    weights = config.get("scoring", {}).get("weights", {
        "engagement": 0.30,
        "relevance": 0.40,
        "freshness": 0.20,
        "source_trust": 0.10
    })

    # グローバルキーワードを取得（全カテゴリ共通）
    global_keywords = config.get("global_keywords", [])

    # グローバル信頼ソースを取得（全カテゴリ共通）
    trusted_sources = config.get("trusted_sources", {})

    # 類義語グループを取得
    synonym_groups = config.get("synonym_groups", [])

    # 各指標を計算（engagementは内訳も取得）
    engagement, engagement_breakdown = calculate_engagement_score(article, social_metrics)
    relevance, matched_keywords = calculate_relevance_score(
        article,
        keywords=global_keywords,  # グローバルキーワードを使用
        synonym_groups=synonym_groups
    )
    freshness = calculate_freshness_score(article)
    source_trust = calculate_source_trust_score(article, trusted_sources)

    # 重み付け合計
    total = (
        engagement * weights.get("engagement", 0.30) +
        relevance * weights.get("relevance", 0.40) +
        freshness * weights.get("freshness", 0.20) +
        source_trust * weights.get("source_trust", 0.10)
    )

    return {
        "engagement": round(engagement, 1),
        "engagement_breakdown": engagement_breakdown,
        "relevance": round(relevance, 1),
        "freshness": round(freshness, 1),
        "source_trust": round(source_trust, 1),
        "total": round(total, 1),
        "matched_keywords": matched_keywords
    }


def categorize_priority(score: float, thresholds: dict) -> str:
    """スコアに基づいて優先度カテゴリを決定"""
    if score >= thresholds.get("must_read", 80):
        return "MUST READ"
    elif score >= thresholds.get("should_read", 60):
        return "SHOULD READ"
    elif score >= thresholds.get("optional", 40):
        return "OPTIONAL"
    else:
        return "SKIP"


def deduplicate_articles(articles: list) -> list:
    """タイトルの正規化で重複を除去（高スコアを優先）"""
    seen = {}
    for article in articles:
        title = article.get("title", "No Title")
        norm_title = normalize_title(title)

        if norm_title in seen:
            # より高いスコアの方を採用
            if article.get("_scores", {}).get("total", 0) > seen[norm_title].get("_scores", {}).get("total", 0):
                seen[norm_title] = article
        else:
            seen[norm_title] = article

    return list(seen.values())


def generate_markdown_report(articles: list, config: dict, output_path: str):
    """Markdownレポートを生成"""
    thresholds = config.get("scoring", {}).get("thresholds", {
        "must_read": 80,
        "should_read": 60,
        "optional": 40
    })

    # 優先度別にグループ化
    priority_groups = defaultdict(list)
    for article in articles:
        priority = article.get("_priority", "SKIP")
        priority_groups[priority].append(article)

    lines = []
    lines.append("---")
    lines.append(f"createDate: {datetime.now().strftime('%Y-%m-%d')}")
    lines.append("author:")
    lines.append("  - claude_code")
    lines.append("tags:")
    lines.append("  - \"#feedly\"")
    lines.append("  - \"#intelligence-report\"")
    lines.append("---")
    lines.append("")
    lines.append("# Feedly インテリジェンスレポート")
    lines.append("")
    lines.append(f"**生成日**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**記事数**: {len(articles)}件（重複除去後）")
    lines.append("")
    lines.append("## スコアリング基準")
    lines.append("")
    lines.append("### 総合スコア")
    lines.append("")
    lines.append("```")
    lines.append("総合スコア = 注目度×30% + 関連度×40% + 鮮度×20% + 信頼度×10%")
    lines.append("```")
    lines.append("")
    lines.append(f"**ライン引き**: MUST READ≧{thresholds['must_read']} / SHOULD READ≧{thresholds['should_read']} / OPTIONAL≧{thresholds['optional']}")
    lines.append("")
    lines.append("### 注目度 (0-100)")
    lines.append("")
    lines.append("| 指標 | 計算式 | 上限 |")
    lines.append("|------|--------|------|")
    lines.append("| Feedly | engagementRate × 5 | 50点 |")
    lines.append("| はてブ | ブックマーク数 × 2 | 40点 |")
    lines.append("| HN | points × 0.5 | 40点 |")
    lines.append("")
    lines.append("```")
    lines.append("注目度 = min(Feedly + はてブ + HN, 100)")
    lines.append("```")
    lines.append("")
    lines.append("### 関連度 (0-100)")
    lines.append("")
    lines.append("- キーワードマッチで計算（タイトルマッチは2倍の重み）")
    lines.append("- 1つ以上マッチ: 基礎点30 + マッチ率に応じて最大70点追加")
    lines.append("- マッチなし: 0点")
    lines.append("")
    lines.append("### 鮮度 (0-100)")
    lines.append("")
    lines.append("| 経過時間 | スコア |")
    lines.append("|----------|--------|")
    lines.append("| 24時間以内 | 100 |")
    lines.append("| 48時間以内 | 50 |")
    lines.append("| 72時間以内 | 35 |")
    lines.append("| それ以上 | 25 |")
    lines.append("")
    lines.append("### 信頼度 (0-100)")
    lines.append("")
    lines.append("- 設定ファイルで定義されたソース: 定義値 × 100")
    lines.append("- 未定義のソース: 50")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 各優先度グループを出力
    priority_order = ["MUST READ", "SHOULD READ", "OPTIONAL", "SKIP", "PAYWALLED"]

    for priority in priority_order:
        group = priority_groups.get(priority, [])
        if not group:
            continue

        lines.append(f"## {priority} ({len(group)}件)")
        lines.append("")
        lines.append("| # | 記事 | スコア | 注目 | Feedly | はてブ | HN | 関連 | 鮮度 | マッチKW | 読了 | 保存 |")
        lines.append("|---|------|--------|------|--------|--------|-----|------|------|----------|------|------|")

        for i, article in enumerate(group, 1):
            title = article.get("title", "No Title")[:50].replace("|", "｜")
            url = extract_url(article)
            scores = article.get("_scores", {})
            breakdown = scores.get("engagement_breakdown", {})
            feedly = breakdown.get("feedly", 0)
            hatena = breakdown.get("hatena", 0)
            hn = breakdown.get("hn", 0)
            hn_id = breakdown.get("hn_id", "")
            matched_kw = ", ".join(scores.get("matched_keywords", [])[:3])  # 最大3つ
            if matched_kw:
                matched_kw = matched_kw.replace("|", "｜")

            # はてブ数にリンクを付ける（1件以上の場合のみ）
            if hatena > 0 and url:
                hatena_url = hatena_entry_url(url)
                hatena_display = f"[{hatena}]({hatena_url})"
            else:
                hatena_display = str(hatena)

            # HNポイントにリンクを付ける（1件以上かつIDがある場合のみ）
            if hn > 0 and hn_id:
                hn_url = hn_entry_url(hn_id)
                hn_display = f"[{hn}]({hn_url})"
            else:
                hn_display = str(hn)

            if url:
                lines.append(
                    f"| {i} | [{title}]({url}) | **{scores.get('total', 0)}** | "
                    f"{scores.get('engagement', 0)} | {feedly} | {hatena_display} | {hn_display} | {scores.get('relevance', 0)} | "
                    f"{scores.get('freshness', 0)} | {matched_kw} | [ ] | [ ] |"
                )
            else:
                lines.append(
                    f"| {i} | {title} | **{scores.get('total', 0)}** | "
                    f"{scores.get('engagement', 0)} | {feedly} | {hatena_display} | {hn_display} | {scores.get('relevance', 0)} | "
                    f"{scores.get('freshness', 0)} | {matched_kw} | [ ] | [ ] |"
                )

        lines.append("")

    # 統計
    lines.append("---")
    lines.append("")
    lines.append("## 統計")
    lines.append("")
    lines.append("| 優先度 | 件数 |")
    lines.append("|--------|------|")
    for priority in priority_order:
        count = len(priority_groups.get(priority, []))
        lines.append(f"| {priority} | {count} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("**生成元**: feedly-intelligence-report skill")

    # 出力
    output = expand_path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines))

    return len(articles)


def main():
    parser = argparse.ArgumentParser(description="Score Feedly articles based on multiple metrics")
    parser.add_argument(
        "--config",
        default="~/.feedly/config.json",
        help="Path to config file (default: ~/.feedly/config.json)"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Input JSON file with fetched articles"
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output markdown file path (default: Daily/YYYY-MM/YYYY-MM-DD（曜日）_feeds-report.md)"
    )

    args = parser.parse_args()

    # 設定読み込み
    try:
        config = load_config(args.config)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # 出力パスを決定（未指定の場合はデフォルト生成）
    output_path = args.output
    if output_path is None:
        base_dir = config.get("output_dir", "Daily")
        output_path = generate_default_output_path(base_dir)

    # 記事読み込み
    articles, metadata = load_articles(args.input)
    if not articles:
        print("No articles found", file=sys.stderr)
        sys.exit(1)

    print(f"Loaded {len(articles)} articles", file=sys.stderr)

    # カテゴリ設定をslugでインデックス化
    category_configs = {cat["slug"]: cat for cat in config.get("categories", [])}

    # ソーシャルメトリクス取得（はてブ + HN）
    social_metrics = fetch_social_metrics_for_articles(articles)

    # スコアリング
    thresholds = config.get("scoring", {}).get("thresholds", {
        "must_read": 80,
        "should_read": 60,
        "optional": 40
    })
    paywalled_domains = config.get("paywalled_domains", [])

    for article in articles:
        cat_slug = article.get("_category_slug", "")
        cat_config = category_configs.get(cat_slug, {})

        scores = calculate_total_score(article, config, cat_config, social_metrics)
        article["_scores"] = scores

        # ペイウォール付きドメインの判定
        if is_paywalled(article, paywalled_domains):
            article["_priority"] = "PAYWALLED"
        else:
            article["_priority"] = categorize_priority(scores["total"], thresholds)

    # 重複除去
    articles = deduplicate_articles(articles)
    print(f"After deduplication: {len(articles)} articles", file=sys.stderr)

    # 総合スコアでソート
    articles.sort(key=lambda x: -x.get("_scores", {}).get("total", 0))

    # レポート生成
    count = generate_markdown_report(articles, config, output_path)
    print(f"Report generated: {output_path} ({count} articles)", file=sys.stderr)


if __name__ == "__main__":
    main()
