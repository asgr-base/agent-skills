#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
郵便番号と住所の整合性検証スクリプト
ZipCloud APIを使用（日本郵便公式データベース）
"""

import csv
import re
import requests
import time
from typing import Dict, List, Tuple
import os

class ZipcodeValidator:
    def __init__(self, use_api=True):
        """
        郵便番号バリデータの初期化

        Args:
            use_api: APIを使用する場合True
        """
        self.use_api = use_api
        self.api_url = "https://zipcloud.ibsnet.co.jp/api/search"
        self.cache = {}
        print("ZipCloud API（日本郵便公式データ）を使用して検証します")

    def get_address_from_api(self, zipcode_clean: str) -> List[Dict]:
        """
        APIから郵便番号に対応する住所を取得

        Args:
            zipcode_clean: 正規化された郵便番号（7桁）

        Returns:
            住所情報のリスト
        """
        # キャッシュチェック
        if zipcode_clean in self.cache:
            return self.cache[zipcode_clean]

        try:
            response = requests.get(
                self.api_url,
                params={'zipcode': zipcode_clean},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            if data['status'] != 200:
                return []

            addresses = []
            for result in data.get('results', []):
                addresses.append({
                    'pref': result['address1'],
                    'city': result['address2'],
                    'town': result['address3'],
                    'full_address': f"{result['address1']}{result['address2']}{result['address3']}"
                })

            # キャッシュに保存
            self.cache[zipcode_clean] = addresses

            # API負荷軽減のため0.1秒待機
            time.sleep(0.1)

            return addresses

        except requests.exceptions.RequestException as e:
            print(f"    API接続エラー: {str(e)}")
            return []

    def normalize_zipcode(self, zipcode: str) -> str:
        """郵便番号を正規化（ハイフン削除、全角→半角）"""
        # 全角を半角に変換
        zipcode = zipcode.translate(str.maketrans('０１２３４５６７８９', '0123456789'))
        # ハイフンを削除
        zipcode = re.sub(r'[-−‐]', '', zipcode)
        return zipcode

    def normalize_address(self, address: str) -> str:
        """住所を正規化（全角スペース削除、統一）"""
        # 全角スペースを削除
        address = address.replace('　', '').replace(' ', '')
        # 都道府県名を抽出
        return address

    def extract_address_parts(self, address: str) -> Tuple[str, str, str]:
        """
        住所から都道府県、市区町村、町域を抽出

        Returns:
            (都道府県, 市区町村, 町域) のタプル
        """
        address = self.normalize_address(address)

        # 都道府県のパターン
        pref_pattern = r'^(北海道|東京都|大阪府|京都府|.{2,3}県)'
        pref_match = re.match(pref_pattern, address)

        if not pref_match:
            return ('', '', address)

        pref = pref_match.group(1)
        remaining = address[len(pref):]

        # 市区町村のパターン
        city_pattern = r'^(.+?[市区町村]|.+?郡.+?[町村])'
        city_match = re.match(city_pattern, remaining)

        if not city_match:
            return (pref, '', remaining)

        city = city_match.group(1)
        town = remaining[len(city):]

        return (pref, city, town)

    def validate(self, zipcode: str, address: str) -> Dict:
        """
        郵便番号と住所の整合性を検証

        Args:
            zipcode: 郵便番号
            address: 住所

        Returns:
            検証結果の辞書
        """
        zipcode_clean = self.normalize_zipcode(zipcode)

        # 郵便番号が7桁でない場合
        if len(zipcode_clean) != 7:
            return {
                'valid': False,
                'status': 'invalid_zipcode',
                'message': f'郵便番号が7桁ではありません: {zipcode}',
                'zipcode': zipcode,
                'address': address
            }

        # APIから住所を取得
        zipcode_addresses = self.get_address_from_api(zipcode_clean)

        # 郵便番号が見つからない場合
        if not zipcode_addresses:
            return {
                'valid': False,
                'status': 'zipcode_not_found',
                'message': f'郵便番号が見つかりません: {zipcode}',
                'zipcode': zipcode,
                'address': address
            }

        # 住所から都道府県、市区町村、町域を抽出
        pref_input, city_input, town_input = self.extract_address_parts(address)

        # 一致する住所を探す
        for addr_data in zipcode_addresses:
            pref_match = pref_input == addr_data['pref']
            city_match = city_input == addr_data['city']

            # 町域は部分一致で判定（番地などが含まれるため）
            town_match = (
                town_input in addr_data['town'] or
                addr_data['town'] in town_input or
                town_input == '' or
                addr_data['town'] == '以下に掲載がない場合'
            )

            if pref_match and city_match and town_match:
                return {
                    'valid': True,
                    'status': 'match',
                    'message': '一致しました',
                    'zipcode': zipcode,
                    'address': address,
                    'official_address': addr_data['full_address']
                }

        # 一致しない場合
        return {
            'valid': False,
            'status': 'address_mismatch',
            'message': '郵便番号と住所が一致しません',
            'zipcode': zipcode,
            'input_address': address,
            'expected_addresses': [a['full_address'] for a in zipcode_addresses],
            'parsed_input': f"都道府県:{pref_input}, 市区町村:{city_input}, 町域:{town_input}"
        }


def validate_csv(input_csv: str, output_csv: str = None):
    """
    CSVファイルの郵便番号と住所を検証

    Args:
        input_csv: 入力CSVファイルパス
        output_csv: 出力CSVファイルパス（省略時は結果を画面表示）
    """
    validator = ZipcodeValidator()

    print(f"\nCSVファイルを検証しています: {input_csv}")
    print("=" * 80)

    results = []

    with open(input_csv, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)

        for i, row in enumerate(reader, 1):
            name = row.get('名前', '')
            zipcode = row.get('郵便番号', '')
            address = row.get('住所', '')

            print(f"\n[{i}] {name}")
            print(f"    郵便番号: {zipcode}")
            print(f"    住所: {address}")

            result = validator.validate(zipcode, address)
            result['name'] = name
            result['row_number'] = i
            results.append(result)

            if result['valid']:
                print(f"    ✓ {result['message']}")
                print(f"    公式住所: {result['official_address']}")
            else:
                print(f"    ✗ {result['message']}")
                if result['status'] == 'address_mismatch':
                    print(f"    入力解析: {result['parsed_input']}")
                    print(f"    期待される住所:")
                    for addr in result['expected_addresses']:
                        print(f"      - {addr}")

    # サマリー表示
    print("\n" + "=" * 80)
    print("検証結果サマリー")
    print("=" * 80)

    total = len(results)
    valid_count = sum(1 for r in results if r['valid'])
    invalid_count = total - valid_count

    print(f"総件数: {total}件")
    print(f"一致: {valid_count}件 ({valid_count/total*100:.1f}%)")
    print(f"不一致: {invalid_count}件 ({invalid_count/total*100:.1f}%)")

    # 不一致の詳細
    if invalid_count > 0:
        print(f"\n不一致データの詳細:")
        print("-" * 80)
        for r in results:
            if not r['valid']:
                print(f"[{r['row_number']}] {r['name']}")
                print(f"    郵便番号: {r['zipcode']}")
                print(f"    住所: {r.get('address', r.get('input_address', ''))}")
                print(f"    理由: {r['message']}")
                if r['status'] == 'address_mismatch':
                    print(f"    期待される住所: {', '.join(r['expected_addresses'][:2])}")
                print()

    # CSV出力
    if output_csv:
        with open(output_csv, 'w', encoding='utf-8-sig', newline='') as f:
            fieldnames = ['行番号', '名前', '郵便番号', '住所', '検証結果', 'メッセージ', '公式住所']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for r in results:
                writer.writerow({
                    '行番号': r['row_number'],
                    '名前': r['name'],
                    '郵便番号': r['zipcode'],
                    '住所': r.get('address', r.get('input_address', '')),
                    '検証結果': '○' if r['valid'] else '×',
                    'メッセージ': r['message'],
                    '公式住所': r.get('official_address', ', '.join(r.get('expected_addresses', [])[:2]))
                })

        print(f"\n検証結果を保存しました: {output_csv}")

    return results


if __name__ == '__main__':
    # 検証実行（CSVファイル名は適宜変更してください）
    results = validate_csv(
        '住所一覧.csv',
        '検証結果_郵便番号.csv'
    )
