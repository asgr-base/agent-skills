# PKI基盤詳細リファレンス

## 1. ePassport PKI概要

### 1.1 信頼モデル

ePassportは**2層の証明書チェーン**を使用：

```
                    ┌─────────────────┐
                    │  Trust Anchor   │
                    │（検証者の信頼基盤）│
                    └────────┬────────┘
                             │ 信頼
                             ▼
┌────────────────────────────────────────────────────┐
│                      CSCA                          │
│        (Country Signing Certificate Authority)     │
│                                                    │
│  ・各国政府が管理するルートCA                        │
│  ・自己署名証明書                                   │
│  ・ICAO PKDまたは二国間交換で配布                    │
└────────────────────┬───────────────────────────────┘
                     │ 署名
                     ▼
┌────────────────────────────────────────────────────┐
│                      DSC                           │
│           (Document Signer Certificate)            │
│                                                    │
│  ・CSCAが署名                                       │
│  ・パスポート製造時に割当                            │
│  ・SOD（Security Object）に埋込                     │
└────────────────────┬───────────────────────────────┘
                     │ 署名
                     ▼
┌────────────────────────────────────────────────────┐
│                      SOD                           │
│           (Security Object Document)               │
│                                                    │
│  ・データグループのハッシュリスト                     │
│  ・各パスポートのICチップに格納                      │
└────────────────────────────────────────────────────┘
```

### 1.2 証明書種別一覧

| 証明書 | 署名者 | 用途 | PA必須度 |
|--------|--------|------|---------|
| **CSCA** | 自己署名 | ルートCA、DSC署名 | 必須 |
| **DSC** | CSCA | SOD署名 | 必須 |
| **CSCA Link** | 旧CSCA | 鍵更新時の信頼継承 | 条件付き |
| **MLSC** | CSCA | Master List署名 | 任意 |
| **DLSC** | CSCA | Deviation List署名 | 任意 |

## 2. CSCA証明書

### 2.1 証明書プロファイル

| フィールド | 要件 |
|-----------|------|
| **Version** | v3 (2) |
| **Signature Algorithm** | RSA 2048+, ECDSA 256+ |
| **Validity** | 推奨3-5年、最大15年 |
| **Subject** | C=国コード, O=政府名, CN=CA名 |
| **Issuer** | Subject と同一（自己署名） |

### 2.2 必須拡張フィールド

| 拡張 | OID | Critical | 値 |
|------|-----|----------|-----|
| **Basic Constraints** | 2.5.29.19 | Yes | `cA=TRUE, pathLenConstraint=0` |
| **Key Usage** | 2.5.29.15 | Yes | `keyCertSign, cRLSign` |
| **Subject Key Identifier** | 2.5.29.14 | No | 公開鍵のSHA-1ハッシュ |
| **Authority Key Identifier** | 2.5.29.35 | No | SKIと同一 |

### 2.3 CSCA証明書例（ASN.1構造）

```
Certificate ::= SEQUENCE {
    tbsCertificate      TBSCertificate,
    signatureAlgorithm  AlgorithmIdentifier,
    signatureValue      BIT STRING
}

TBSCertificate ::= SEQUENCE {
    version         [0] EXPLICIT Version DEFAULT v1,
    serialNumber        CertificateSerialNumber,
    signature           AlgorithmIdentifier,
    issuer              Name,           -- C=JP, O=Government of Japan, CN=Japan Passport CA
    validity            Validity,       -- notBefore, notAfter
    subject             Name,           -- issuerと同一
    subjectPublicKeyInfo SubjectPublicKeyInfo,
    extensions      [3] EXPLICIT Extensions
}
```

## 3. DSC証明書

### 3.1 証明書プロファイル

| フィールド | 要件 |
|-----------|------|
| **Version** | v3 (2) |
| **Signature Algorithm** | CSCAと同等以上 |
| **Validity** | 推奨3ヶ月、最大10年 |
| **Subject** | 国、組織、シリアル番号 |
| **Issuer** | CSCAのSubject |

### 3.2 必須拡張フィールド

| 拡張 | OID | Critical | 値 |
|------|-----|----------|-----|
| **Basic Constraints** | 2.5.29.19 | No | `cA=FALSE` または省略 |
| **Key Usage** | 2.5.29.15 | Yes | `digitalSignature` |
| **Subject Key Identifier** | 2.5.29.14 | No | 公開鍵ハッシュ |
| **Authority Key Identifier** | 2.5.29.35 | No | CSCAの公開鍵ハッシュ |

### 3.3 オプション拡張フィールド

| 拡張 | OID | 用途 |
|------|-----|------|
| **CRL Distribution Points** | 2.5.29.31 | CRL取得URL |
| **Private Key Usage Period** | 2.5.29.16 | 秘密鍵使用期間 |
| **Document Type List** | 2.23.136.1.1.6.2 | 署名対象文書種別 |

## 4. CSCA Link証明書

### 4.1 目的

CSCAの**鍵更新（Key Rollover）**時に使用。旧CSCAから新CSCAへの信頼継承を実現。

```
【CSCA鍵更新シナリオ】

旧CSCA (2015-2030)                    新CSCA (2025-2040)
     │                                      │
     ├── DSC群 (2015-2025発行)               ├── DSC群 (2025年以降発行)
     │                                      │
     └── CSCA Link証明書 ─────────────────────┘
           Subject: 新CSCA
           Issuer: 旧CSCA
```

### 4.2 検証者の対応

```
【CSCA Link検証フロー】

1. DSCのIssuerがCSCA Linkの場合
   └── CSCA Link証明書の検証
       └── 旧CSCAの公開鍵でLink証明書を検証
           └── Link証明書内の新CSCA公開鍵でDSCを検証
```

## 5. CRL（Certificate Revocation List）

### 5.1 CRLプロファイル

| フィールド | 要件 |
|-----------|------|
| **Version** | v2 (1) |
| **Signature Algorithm** | CSCAと同一 |
| **Issuer** | CSCAのSubject |
| **This Update** | 発行日時 |
| **Next Update** | 最大90日後 |

### 5.2 CRL拡張フィールド

| 拡張 | OID | 用途 |
|------|-----|------|
| **Authority Key Identifier** | 2.5.29.35 | 発行CA特定 |
| **CRL Number** | 2.5.29.20 | シーケンス番号 |
| **Delta CRL Indicator** | 2.5.29.27 | 差分CRL（オプション） |

### 5.3 CRL検証フロー

```
【CRL検証手順】

Step 1: CRL取得
  ├── ICAO PKDから事前取得（推奨）
  ├── DSC内CDPから動的取得
  └── BSIから取得（ドイツのみ）

Step 2: CRL署名検証
  └── CSCAの公開鍵でCRL署名を検証

Step 3: 有効期限確認
  └── thisUpdate ≤ 現在時刻 ≤ nextUpdate

Step 4: DSCシリアル番号照合
  ├── CRL内に存在 → 失効
  └── CRL内に不存在 → 有効
```

### 5.4 失効理由コード

| コード | 名称 | 説明 |
|--------|------|------|
| 0 | unspecified | 理由未指定 |
| 1 | keyCompromise | 秘密鍵漏洩 |
| 2 | cACompromise | CA秘密鍵漏洩 |
| 3 | affiliationChanged | 所属変更 |
| 4 | superseded | 新証明書に置換 |
| 5 | cessationOfOperation | 運用停止 |
| 6 | certificateHold | 一時停止 |

## 6. Master List

### 6.1 構造

```
【Master List（CMS SignedData形式）】

ContentInfo {
    contentType: signedData (1.2.840.113549.1.7.2)
    content: SignedData {
        version: 3
        digestAlgorithms: { sha256 }
        encapContentInfo: {
            eContentType: id-icao-cscaMasterList (2.23.136.1.1.2)
            eContent: CscaMasterList {
                version: 0
                certList: SEQUENCE OF Certificate {
                    CSCA証明書1,
                    CSCA証明書2,
                    ...
                }
            }
        }
        certificates: { MLSC証明書 }
        signerInfos: { 署名情報 }
    }
}
```

### 6.2 取得ソース

| ソース | カバー率 | 商用利用 | 備考 |
|--------|---------|---------|------|
| **BSI** | 112カ国 | 可 | 無料、推奨 |
| **ICAO PKD** | 107カ国 | 条件付き | Pilot参加必要 |
| **二国間交換** | 個別 | - | 非参加国対応 |

## 7. SOD（Security Object Document）

### 7.1 構造

```
【SOD（CMS SignedData形式）】

ContentInfo {
    contentType: signedData (1.2.840.113549.1.7.2)
    content: SignedData {
        version: 3
        digestAlgorithms: { sha256 }
        encapContentInfo: {
            eContentType: id-icao-ldsSecurityObject (2.23.136.1.1.1)
            eContent: LDSSecurityObject {
                version: 0
                hashAlgorithm: sha256
                dataGroupHashValues: SEQUENCE OF {
                    dataGroupNumber: 1,   -- DG1
                    dataGroupHashValue: OCTET STRING
                },
                {
                    dataGroupNumber: 2,   -- DG2
                    dataGroupHashValue: OCTET STRING
                },
                ...
            }
        }
        certificates: { DSC証明書 }
        signerInfos: { 署名情報 }
    }
}
```

### 7.2 LDS Security Object OID

| OID | 名称 |
|-----|------|
| 2.23.136.1.1.1 | id-icao-ldsSecurityObject |

## 8. ICAO PKD

### 8.1 概要

| 項目 | 内容 |
|------|------|
| **運営** | ICAO（国際民間航空機関） |
| **設立** | 2007年 |
| **参加国** | 107カ国（2025年時点） |
| **URL** | https://download.pkd.icao.int/ |

### 8.2 提供データ

| データ | 件数 | 用途 |
|--------|------|------|
| **CSCA** | 525件 | ルート証明書 |
| **DSC** | 29,916件 | 文書署名証明書 |
| **CRL** | 69カ国分 | 失効リスト |
| **Master List** | 各国分 | CSCAリスト |
| **Deviation List** | 各国分 | 逸脱リスト |

### 8.3 アクセス方式

| 方式 | プロトコル | 用途 |
|------|-----------|------|
| **LDAP** | ldap://ldap.icao.int | リアルタイム検索 |
| **LDIF** | HTTP | 一括ダウンロード |
| **Webポータル** | HTTPS | 手動ダウンロード |

## 9. 証明書検証実装

### 9.1 PA検証フロー

```
【Passive Authentication完全フロー】

Step 1: SODからDSC抽出
  └── SOD.certificates[0] → DSC

Step 2: CSCA取得
  ├── Master List検索（AKI照合）
  ├── ICAO PKD検索
  └── ローカルストア検索

Step 3: CRL取得・失効確認
  └── DSCシリアルがCRLに含まれないことを確認

Step 4: 証明書チェーン検証
  ├── DSC有効期限確認
  ├── CSCA有効期限確認
  ├── DSC署名検証（CSCA公開鍵使用）
  └── AKI/SKI一致確認

Step 5: SOD署名検証
  └── DSC公開鍵でSOD署名を検証

Step 6: データグループハッシュ検証
  └── 読取データのハッシュとSOD内ハッシュを比較
```

### 9.2 証明書非準拠への対応

多くの国のCSCA/DSCがICAO仕様に完全準拠していない現実があります：

| 問題 | 発生率 | 対応方針 |
|------|--------|---------|
| SKI欠落 | 高 | 公開鍵ハッシュで代替 |
| AKI欠落 | 高 | Issuer/Serialで代替 |
| BC pathLength不正 | 中 | 緩和して許容 |
| KU不正 | 中 | 最低限のビットのみ検証 |

### 9.3 証明書ストア設計

```
【推奨ストア構成】

/certificates/
├── csca/
│   ├── JP/
│   │   ├── current.cer
│   │   └── link/
│   │       └── 2020-2025.cer
│   ├── US/
│   └── ...
├── dsc/           -- オプション（SOD内から取得可能）
├── crl/
│   ├── JP.crl
│   ├── US.crl
│   └── ...
└── master-list/
    ├── bsi-master-list.ml
    └── icao-master-list.ml

【更新スケジュール】
・CSCA: 月次（新規追加時）
・CRL: 日次
・Master List: 週次
```

---

**関連ドキュメント**:
- [CRYPTOGRAPHIC-ALGORITHMS.md](CRYPTOGRAPHIC-ALGORITHMS.md) - 使用アルゴリズム
- [SECURITY-MECHANISMS.md](SECURITY-MECHANISMS.md) - PKI使用箇所
- [GLOSSARY.md](GLOSSARY.md) - 用語定義
