# ASN.1/TLV 詳細リファレンス

## 1. 概要

### 1.1 ASN.1（Abstract Syntax Notation One）とは

| 項目 | 内容 |
|------|------|
| **目的** | データ構造の抽象的な記述 |
| **規格** | ITU-T X.680-X.683 |
| **適用範囲** | X.509証明書、LDAP、SNMP、ICカード等 |

### 1.2 エンコーディングルール

| ルール | 説明 | 用途 |
|--------|------|------|
| **BER** | Basic Encoding Rules | 汎用、柔軟 |
| **DER** | Distinguished Encoding Rules | 一意性保証、署名用 |
| **CER** | Canonical Encoding Rules | ストリーミング向け |
| **PER** | Packed Encoding Rules | 帯域効率重視 |

## 2. TLV（Tag-Length-Value）構造

### 2.1 基本構造

```
┌──────────┬──────────┬──────────────────┐
│   Tag    │  Length  │      Value       │
│ (1-n B)  │ (1-n B)  │    (0-n B)       │
└──────────┴──────────┴──────────────────┘
```

### 2.2 Tag構造

```
【1バイトタグ】
┌─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┐
│ b8  │ b7  │ b6  │ b5  │ b4  │ b3  │ b2  │ b1  │
├─────┴─────┼─────┼─────┴─────┴─────┴─────┴─────┤
│   Class   │ P/C │         Tag Number          │
└───────────┴─────┴─────────────────────────────┘

Class:
  00 = Universal（汎用）
  01 = Application（アプリケーション固有）
  10 = Context-specific（文脈依存）
  11 = Private（私用）

P/C:
  0 = Primitive（プリミティブ）
  1 = Constructed（構造型）
```

### 2.3 Length構造

| 形式 | 説明 | 範囲 |
|------|------|------|
| **Short Form** | 1バイト、最上位ビット=0 | 0-127バイト |
| **Long Form** | 最上位ビット=1、後続バイト数を示す | 128バイト以上 |
| **Indefinite** | 0x80、EOC(00 00)で終端 | BERのみ |

```
【Length例】

短縮形:
  0x05 → 5バイト
  0x7F → 127バイト

長形式:
  0x81 0x80 → 128バイト（81=長形式1バイト）
  0x82 0x01 0x00 → 256バイト（82=長形式2バイト）
  0x83 0x01 0x00 0x00 → 65536バイト
```

## 3. Universal タグ一覧

### 3.1 プリミティブ型

| タグ | 名称 | 説明 |
|------|------|------|
| 0x01 | BOOLEAN | 真偽値 |
| 0x02 | INTEGER | 整数 |
| 0x03 | BIT STRING | ビット列 |
| 0x04 | OCTET STRING | オクテット列 |
| 0x05 | NULL | 空 |
| 0x06 | OBJECT IDENTIFIER | OID |
| 0x0C | UTF8String | UTF-8文字列 |
| 0x13 | PrintableString | 印字可能文字列 |
| 0x14 | T61String | Teletex文字列 |
| 0x16 | IA5String | ASCII文字列 |
| 0x17 | UTCTime | UTC時刻 |
| 0x18 | GeneralizedTime | 一般化時刻 |

### 3.2 構造型

| タグ | 名称 | 説明 |
|------|------|------|
| 0x30 | SEQUENCE | 順序付きリスト |
| 0x31 | SET | 順序なしリスト |

### 3.3 Context-specificタグ

```
Context-specific（文脈依存）タグ:
  [0] = 0xA0（構造型）または 0x80（プリミティブ）
  [1] = 0xA1 または 0x81
  [2] = 0xA2 または 0x82
  ...
```

## 4. BER vs DER

### 4.1 主な違い

| 項目 | BER | DER |
|------|-----|-----|
| **Length形式** | Short/Long/Indefinite | 最短形式のみ |
| **BOOLEAN** | 0以外=TRUE | 0xFF=TRUE |
| **BIT STRING** | 不使用ビット0可 | 末尾の不使用ビット0 |
| **SET順序** | 任意 | タグ値昇順 |
| **一意性** | なし | 保証 |

### 4.2 DER制約

```
【DER必須ルール】

1. Lengthは最短形式
   ✅ 0x05（5バイト）
   ❌ 0x81 0x05（無駄な長形式）

2. BOOLEANはFALSE=0x00、TRUE=0xFF
   ✅ 01 01 FF（TRUE）
   ❌ 01 01 01（BERでは許可）

3. Indefinite Length禁止
   ❌ 30 80 ... 00 00

4. SET要素はタグ値昇順
   ✅ 02 ... 04 ... 06 ...
   ❌ 06 ... 02 ... 04 ...
```

## 5. OID（Object Identifier）

### 5.1 OID構造

```
OID: 1.2.840.113549.1.1.11 (sha256WithRSAEncryption)

エンコーディング:
  最初の2オクテット: 40*X + Y（X=1, Y=2 → 42 = 0x2A）
  以降: 各コンポーネントを7ビット可変長でエンコード

06 09 2A 86 48 86 F7 0D 01 01 0B
│  │  └─────────────────────────┘
│  │           OID値
│  └── Length (9バイト)
└── Tag (OBJECT IDENTIFIER)
```

### 5.2 主要OID

| OID | 名称 |
|-----|------|
| 1.2.840.113549.1.1.1 | rsaEncryption |
| 1.2.840.113549.1.1.11 | sha256WithRSAEncryption |
| 1.2.840.10045.4.3.2 | ecdsa-with-SHA256 |
| 2.5.4.3 | commonName (CN) |
| 2.5.4.6 | countryName (C) |
| 2.5.4.10 | organizationName (O) |
| 2.5.29.14 | subjectKeyIdentifier |
| 2.5.29.15 | keyUsage |
| 2.5.29.19 | basicConstraints |
| 2.5.29.35 | authorityKeyIdentifier |

## 6. 実践的なTLVパース

### 6.1 証明書パース例

```
【X.509証明書の最上位構造】

30 82 03 A5        -- SEQUENCE, 933バイト
   30 82 02 8D     -- TBSCertificate (SEQUENCE)
      ...
   30 0D           -- signatureAlgorithm (SEQUENCE)
      06 09 ...    -- OID
      05 00        -- NULL
   03 82 01 01     -- signatureValue (BIT STRING)
      00 ...       -- パディング + 署名値
```

### 6.2 パースアルゴリズム

```python
def parse_tlv(data, offset=0):
    # Tag読み取り
    tag = data[offset]
    offset += 1

    # マルチバイトタグ（0x1F）
    if (tag & 0x1F) == 0x1F:
        while data[offset] & 0x80:
            offset += 1
        offset += 1

    # Length読み取り
    length = data[offset]
    offset += 1

    if length & 0x80:  # Long form
        num_bytes = length & 0x7F
        length = int.from_bytes(data[offset:offset+num_bytes], 'big')
        offset += num_bytes

    # Value取得
    value = data[offset:offset+length]

    return tag, length, value, offset + length
```

## 7. ICカードでのTLV

### 7.1 ICカード固有タグ

| タグ | 名称 | 用途 |
|------|------|------|
| 0x5F | アプリケーションデータ | 2バイトタグ接頭辞 |
| 0x7F | セキュリティデータ | 2バイトタグ接頭辞 |
| 0x61 | アプリケーションテンプレート | AID選択応答 |
| 0x6F | FCIテンプレート | ファイル制御情報 |

### 7.2 ePassportでのTLV

| タグ | 内容 |
|------|------|
| 0x61 | DG1テンプレート |
| 0x5F1F | MRZ情報 |
| 0x75 | 顔画像テンプレート |
| 0x5F2E | 顔画像データ |

## 8. デバッグツール

### 8.1 OpenSSL

```bash
# DERファイルをASN.1構造で表示
openssl asn1parse -in cert.der -inform DER

# PEMファイルをASN.1構造で表示
openssl asn1parse -in cert.pem

# オフセット指定でパース
openssl asn1parse -in cert.der -inform DER -offset 4 -length 100
```

### 8.2 オンラインツール

- [ASN.1 JavaScript decoder](https://lapo.it/asn1js/)
- [ASN.1 Playground](https://asn1.io/asn1playground/)

## 9. よくあるエラー

| エラー | 原因 | 対策 |
|--------|------|------|
| Invalid length | 不正なLength形式 | Long form判定確認 |
| Unexpected tag | 期待と異なるタグ | Context-specific確認 |
| Truncated data | データ不足 | Length分のデータ確認 |
| Invalid OID | OIDエンコードエラー | 7ビット可変長確認 |

---

**関連ドキュメント**:
- [X509-PKI-GUIDE.md](X509-PKI-GUIDE.md) - 証明書でのASN.1
- [SMARTCARD-APDU-GUIDE.md](SMARTCARD-APDU-GUIDE.md) - APDU内のTLV
- [GLOSSARY.md](GLOSSARY.md) - 用語定義
