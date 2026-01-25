---
name: epassport-security-guide
description: ePassportセキュリティ・ICカード技術の包括ガイド。ICAO Doc 9303のPA/AA/CA/BAC/PACE、PKI（CSCA/DSC/CRL）に加え、基盤技術（X.509/PKI、ASN.1/TLV、ISO 7816 APDU、ISO 14443 NFC）を網羅。ePassport実装、ICカード開発、セキュリティ技術の質問・学習に使用。
version: 2.0.0
author: claude_code
createDate: 2026-01-21
updateDate: 2026-01-21
---

# ePassportセキュリティ・ICカード技術ガイド

## 概要

ePassport（電子パスポート）のセキュリティ技術と、その基盤となるICカード・暗号技術に関する包括ガイド。ICAO Doc 9303固有の知識から汎用的な基盤技術まで、階層的に解説します。

## 知識領域マップ

```
┌─────────────────────────────────────────────────────┐
│  ePassport専用（ICAO Doc 9303）                     │
│  ・セキュリティメカニズム（PA/AA/CA/BAC/PACE）      │
│  ・PKI（CSCA/DSC/CRL/Master List）                  │
│  ・LDS（DG1-DG16、EF.COM、EF.SOD）                 │
├─────────────────────────────────────────────────────┤
│  汎用基盤技術                                       │
│  ・X.509/PKI（証明書、証明書チェーン、失効）       │
│  ・ASN.1/TLV（データエンコーディング）             │
│  ・ISO 7816-4（ICカードAPDUコマンド）              │
│  ・ISO 14443（NFC非接触通信）                      │
│  ・暗号アルゴリズム（RSA、ECDSA、AES、SHA）       │
└─────────────────────────────────────────────────────┘
```

## クイックリファレンス

### ePassportセキュリティメカニズム

| メカニズム | 目的 | 必須/任意 |
|-----------|------|----------|
| **PA** | データ完全性・真正性検証 | 必須 |
| **AA** | ICチップのクローン検出 | 任意 |
| **CA** | セッション暗号化＋クローン検出 | 推奨 |
| **BAC** | ICチップへのアクセス制御 | 必須* |
| **PACE** | 安全なアクセス制御 | 推奨 |

*BACまたはPACEのいずれかが必須

### 基盤技術の適用範囲

| 技術 | ePassport | マイナンバー | クレジットカード | 交通系IC |
|------|-----------|-------------|-----------------|---------|
| X.509/PKI | ✅ | ✅ | ✅ | - |
| ASN.1/TLV | ✅ | ✅ | ✅ | ✅ |
| ISO 7816 APDU | ✅ | ✅ | ✅ | ✅ |
| ISO 14443 NFC | ✅ | ✅ | ✅ | ✅ |

## 使い方

### ePassport固有の質問

```
"PAとは何ですか？"
"BAC鍵導出の手順を説明して"
"CSCAとDSCの違いは？"
```

### 基盤技術の質問

```
"X.509証明書の拡張フィールドについて教えて"
"ASN.1のBERとDERの違いは？"
"APDUコマンドのSELECTの使い方は？"
"ISO 14443 Type AとType Bの違いは？"
```

### トラブルシューティング

```
"署名検証に失敗する原因は？"
"TLVパースでエラーが出る"
"NFCカード検出が不安定"
```

## 詳細リファレンス

### ePassport専用（ICAO Doc 9303）

| ファイル | 内容 |
|----------|------|
| [SECURITY-MECHANISMS.md](SECURITY-MECHANISMS.md) | PA/AA/CA/BAC/PACE詳細プロトコル |
| [PKI-INFRASTRUCTURE.md](PKI-INFRASTRUCTURE.md) | CSCA/DSC/CRL、Master List |
| [CRYPTOGRAPHIC-ALGORITHMS.md](CRYPTOGRAPHIC-ALGORITHMS.md) | ePassport暗号アルゴリズム詳細 |

### 汎用基盤技術

| ファイル | 内容 |
|----------|------|
| [X509-PKI-GUIDE.md](X509-PKI-GUIDE.md) | X.509証明書、証明書チェーン、CRL/OCSP |
| [ASN1-TLV-GUIDE.md](ASN1-TLV-GUIDE.md) | ASN.1、BER/DER、TLV構造 |
| [SMARTCARD-APDU-GUIDE.md](SMARTCARD-APDU-GUIDE.md) | ISO 7816-4 APDUコマンド |
| [NFC-ISO14443-GUIDE.md](NFC-ISO14443-GUIDE.md) | ISO 14443 NFC通信 |

### 共通

| ファイル | 内容 |
|----------|------|
| [GLOSSARY.md](GLOSSARY.md) | 用語集 |

## ICAO仕様の正確な参照

IMPORTANT: ICAO Doc 9303の詳細仕様確認にはNotebookLMを使用

```
"ICAOのノートブックでPA実装手順を確認して"
"ICAO仕様に基づいて証明書チェーン検証を説明して"
```

詳細: [notebooklm-research Skill](../notebooklm-research/SKILL.md)

## 参考文献

### 暗号学

| 書籍 | 著者 | 内容 |
|------|------|------|
| **暗号技術入門 第3版** | 結城浩 | 対称暗号、公開鍵暗号、デジタル署名、証明書、PKI等の基礎を網羅。図解が豊富で入門に最適。 |

### 規格・仕様

| 規格 | 内容 |
|------|------|
| ICAO Doc 9303 | ePassport国際規格 |
| ISO/IEC 7816 | ICカードコマンド規格 |
| ISO/IEC 14443 | 非接触ICカード規格 |
| RFC 5280 | X.509 PKI証明書・CRL |

## 注意事項

- ePassport部分はICAO Doc 9303 Edition 8（2021年）に基づく
- 基盤技術は各ISO/RFC規格に基づく
- 国別実装の差異はDeviation Listを参照

---
**Version**: 2.0.0 | **Last Updated**: 2026-01-21
