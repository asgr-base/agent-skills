# X.509/PKI 詳細リファレンス

## 1. 概要

### 1.1 PKI（Public Key Infrastructure）とは

| 項目 | 内容 |
|------|------|
| **目的** | デジタル証明書による信頼基盤の構築 |
| **規格** | ITU-T X.509、RFC 5280 |
| **適用範囲** | TLS/SSL、S/MIME、コード署名、ePassport等 |

### 1.2 信頼モデル

```
【階層型PKI】

ルートCA（Trust Anchor）
  │ 自己署名
  │
  ├── 中間CA
  │     │
  │     └── エンドエンティティ証明書
  │
  └── 中間CA
        │
        └── エンドエンティティ証明書
```

## 2. X.509証明書構造

### 2.1 証明書フォーマット

```asn1
Certificate ::= SEQUENCE {
    tbsCertificate       TBSCertificate,
    signatureAlgorithm   AlgorithmIdentifier,
    signatureValue       BIT STRING
}

TBSCertificate ::= SEQUENCE {
    version         [0]  EXPLICIT Version DEFAULT v1,
    serialNumber         CertificateSerialNumber,
    signature            AlgorithmIdentifier,
    issuer               Name,
    validity             Validity,
    subject              Name,
    subjectPublicKeyInfo SubjectPublicKeyInfo,
    issuerUniqueID  [1]  IMPLICIT UniqueIdentifier OPTIONAL,
    subjectUniqueID [2]  IMPLICIT UniqueIdentifier OPTIONAL,
    extensions      [3]  EXPLICIT Extensions OPTIONAL
}
```

### 2.2 基本フィールド

| フィールド | 説明 | 例 |
|-----------|------|-----|
| **version** | 証明書バージョン（v1=0, v2=1, v3=2） | v3 (2) |
| **serialNumber** | 発行者内で一意のシリアル番号 | 1234567890 |
| **signature** | 署名アルゴリズム | sha256WithRSAEncryption |
| **issuer** | 発行者DN（Distinguished Name） | C=JP, O=Example, CN=CA |
| **validity** | 有効期間（notBefore, notAfter） | 2024/01/01 - 2025/01/01 |
| **subject** | 主体者DN | C=JP, O=Example, CN=Server |
| **subjectPublicKeyInfo** | 公開鍵情報 | RSA 2048bit |

### 2.3 DN（Distinguished Name）属性

| 属性 | OID | 説明 |
|------|-----|------|
| **CN** | 2.5.4.3 | Common Name |
| **O** | 2.5.4.10 | Organization |
| **OU** | 2.5.4.11 | Organizational Unit |
| **C** | 2.5.4.6 | Country（2文字ISO 3166） |
| **ST** | 2.5.4.8 | State or Province |
| **L** | 2.5.4.7 | Locality |
| **serialNumber** | 2.5.4.5 | Serial Number（DN属性） |

## 3. 拡張フィールド（Extensions）

### 3.1 主要拡張一覧

| 拡張 | OID | Critical | 用途 |
|------|-----|----------|------|
| **Basic Constraints** | 2.5.29.19 | Yes | CA/エンドエンティティ判別 |
| **Key Usage** | 2.5.29.15 | Yes | 鍵の使用目的 |
| **Extended Key Usage** | 2.5.29.37 | No | 拡張用途（TLS、コード署名等） |
| **Subject Key Identifier** | 2.5.29.14 | No | 主体者鍵識別子 |
| **Authority Key Identifier** | 2.5.29.35 | No | 発行者鍵識別子 |
| **Subject Alternative Name** | 2.5.29.17 | No | 代替名（DNS名、IPアドレス等） |
| **CRL Distribution Points** | 2.5.29.31 | No | CRL取得URL |
| **Authority Information Access** | 1.3.6.1.5.5.7.1.1 | No | OCSP、CA証明書URL |

### 3.2 Basic Constraints

```asn1
BasicConstraints ::= SEQUENCE {
    cA                  BOOLEAN DEFAULT FALSE,
    pathLenConstraint   INTEGER (0..MAX) OPTIONAL
}
```

| 値 | 意味 |
|----|------|
| `cA=TRUE` | CA証明書 |
| `cA=FALSE` | エンドエンティティ証明書 |
| `pathLenConstraint=0` | 直下のエンドエンティティのみ署名可能 |
| `pathLenConstraint=1` | 1階層の中間CAまで許可 |

### 3.3 Key Usage

| ビット | 名称 | 用途 |
|--------|------|------|
| 0 | digitalSignature | デジタル署名 |
| 1 | nonRepudiation | 否認防止 |
| 2 | keyEncipherment | 鍵暗号化（RSA鍵交換） |
| 3 | dataEncipherment | データ暗号化 |
| 4 | keyAgreement | 鍵合意（DH） |
| 5 | keyCertSign | 証明書署名（CA用） |
| 6 | cRLSign | CRL署名 |
| 7 | encipherOnly | 暗号化のみ |
| 8 | decipherOnly | 復号のみ |

### 3.4 Extended Key Usage

| OID | 名称 | 用途 |
|-----|------|------|
| 1.3.6.1.5.5.7.3.1 | serverAuth | TLSサーバー認証 |
| 1.3.6.1.5.5.7.3.2 | clientAuth | TLSクライアント認証 |
| 1.3.6.1.5.5.7.3.3 | codeSigning | コード署名 |
| 1.3.6.1.5.5.7.3.4 | emailProtection | S/MIME |
| 1.3.6.1.5.5.7.3.8 | timeStamping | タイムスタンプ |

### 3.5 Subject Alternative Name（SAN）

| タイプ | 説明 | 例 |
|--------|------|-----|
| **dNSName** | DNS名 | www.example.com |
| **iPAddress** | IPアドレス | 192.168.1.1 |
| **rfc822Name** | メールアドレス | user@example.com |
| **uniformResourceIdentifier** | URI | https://example.com |

## 4. 証明書チェーン検証

### 4.1 検証フロー

```
【証明書チェーン検証】

Step 1: チェーン構築
  └── エンドエンティティ → 中間CA → ルートCA

Step 2: 各証明書の検証
  ├── 署名検証（上位CAの公開鍵で）
  ├── 有効期限確認
  ├── Basic Constraints確認
  ├── Key Usage確認
  └── パス長制約確認

Step 3: 失効確認
  ├── CRL検証
  └── OCSP検証（オプション）

Step 4: ルートCA信頼確認
  └── Trust Storeに存在するか
```

### 4.2 検証項目

| 項目 | 検証内容 |
|------|---------|
| **署名** | 上位CA公開鍵で署名検証 |
| **有効期限** | notBefore ≤ 現在時刻 ≤ notAfter |
| **Basic Constraints** | CA証明書はcA=TRUE |
| **Key Usage** | CA証明書はkeyCertSign必須 |
| **パス長** | pathLenConstraintを超えない |
| **失効** | CRL/OCSPで失効していない |
| **ポリシー** | Certificate Policies一致（オプション） |

## 5. CRL（Certificate Revocation List）

### 5.1 CRL構造

```asn1
CertificateList ::= SEQUENCE {
    tbsCertList          TBSCertList,
    signatureAlgorithm   AlgorithmIdentifier,
    signatureValue       BIT STRING
}

TBSCertList ::= SEQUENCE {
    version              Version OPTIONAL,
    signature            AlgorithmIdentifier,
    issuer               Name,
    thisUpdate           Time,
    nextUpdate           Time OPTIONAL,
    revokedCertificates  SEQUENCE OF SEQUENCE { ... } OPTIONAL,
    crlExtensions   [0]  EXPLICIT Extensions OPTIONAL
}
```

### 5.2 失効理由コード

| コード | 名称 | 説明 |
|--------|------|------|
| 0 | unspecified | 理由未指定 |
| 1 | keyCompromise | 秘密鍵漏洩 |
| 2 | cACompromise | CA秘密鍵漏洩 |
| 3 | affiliationChanged | 所属変更 |
| 4 | superseded | 新証明書に置換 |
| 5 | cessationOfOperation | 運用停止 |
| 6 | certificateHold | 一時停止 |

### 5.3 Delta CRL

| 種類 | 説明 |
|------|------|
| **Full CRL** | 全失効証明書を含む |
| **Delta CRL** | 前回からの差分のみ |

## 6. OCSP（Online Certificate Status Protocol）

### 6.1 概要

| 項目 | 内容 |
|------|------|
| **規格** | RFC 6960 |
| **目的** | リアルタイムの証明書状態確認 |
| **利点** | CRLより軽量、リアルタイム |

### 6.2 OCSPレスポンス状態

| 状態 | 説明 |
|------|------|
| **good** | 証明書は有効 |
| **revoked** | 証明書は失効 |
| **unknown** | 状態不明 |

## 7. 証明書フォーマット

### 7.1 エンコーディング形式

| 形式 | 拡張子 | 説明 |
|------|--------|------|
| **DER** | .der, .cer | バイナリ形式 |
| **PEM** | .pem, .crt | Base64 + ヘッダー/フッター |
| **PKCS#7** | .p7b, .p7c | 証明書チェーン格納 |
| **PKCS#12** | .p12, .pfx | 秘密鍵 + 証明書 |

### 7.2 PEM形式例

```
-----BEGIN CERTIFICATE-----
MIIDXTCCAkWgAwIBAgIJAJC1HiIAZAiUMA0GCSqGSIb3Qq0teleqaKzlN8LBRqTr
...（Base64エンコードされたDER）...
ynUyMpQzEPxpTx6kHXcQR5mOaGrV4V8DqNQo
-----END CERTIFICATE-----
```

## 8. OpenSSLコマンド例

### 8.1 証明書の表示

```bash
# PEM形式証明書の表示
openssl x509 -in cert.pem -text -noout

# DER形式証明書の表示
openssl x509 -in cert.der -inform DER -text -noout
```

### 8.2 証明書チェーン検証

```bash
# チェーン検証
openssl verify -CAfile ca.pem cert.pem

# 中間CA含むチェーン検証
openssl verify -CAfile root.pem -untrusted intermediate.pem cert.pem
```

### 8.3 CRL検証

```bash
# CRL表示
openssl crl -in crl.pem -text -noout

# CRLで失効確認
openssl verify -crl_check -CAfile ca.pem -CRLfile crl.pem cert.pem
```

## 9. ePassportでのPKI

ePassportでは以下の特殊なPKI構造を使用：

| 証明書 | 対応するX.509概念 |
|--------|------------------|
| CSCA | ルートCA |
| DSC | エンドエンティティ |
| CSCA Link | クロス証明書 |

詳細: [PKI-INFRASTRUCTURE.md](PKI-INFRASTRUCTURE.md)

---

**関連ドキュメント**:
- [ASN1-TLV-GUIDE.md](ASN1-TLV-GUIDE.md) - 証明書のエンコーディング
- [PKI-INFRASTRUCTURE.md](PKI-INFRASTRUCTURE.md) - ePassport PKI
- [GLOSSARY.md](GLOSSARY.md) - 用語定義
