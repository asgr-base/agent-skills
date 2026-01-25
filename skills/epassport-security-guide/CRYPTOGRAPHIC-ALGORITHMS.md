# 暗号アルゴリズム詳細リファレンス

## 1. 署名アルゴリズム

### 1.1 RSA（Rivest-Shamir-Adleman）

#### 概要

| 項目 | 内容 |
|------|------|
| **種別** | 公開鍵暗号方式 |
| **基盤** | 大きな合成数の素因数分解困難性 |
| **用途** | デジタル署名、鍵交換 |
| **ICAO要件** | 2048bit以上（推奨4096bit） |

#### RSA署名方式

| 方式 | OID | ICAO | 特徴 |
|------|-----|------|------|
| **RSASSA-PKCS1-v1_5** | 1.2.840.113549.1.1.x | 推奨 | 決定的、広く実装 |
| **RSASSA-PSS** | 1.2.840.113549.1.1.10 | 許可 | 確率的、より安全 |

#### OID一覧（RSASSA-PKCS1-v1_5）

| アルゴリズム | OID |
|-------------|-----|
| sha256WithRSAEncryption | 1.2.840.113549.1.1.11 |
| sha384WithRSAEncryption | 1.2.840.113549.1.1.12 |
| sha512WithRSAEncryption | 1.2.840.113549.1.1.13 |

#### RSA鍵長と有効期限の関係

| 鍵長 | セキュリティビット | 推奨有効期限 |
|------|------------------|-------------|
| 2048bit | 112bit | 2030年まで |
| 3072bit | 128bit | 2030年以降 |
| 4096bit | 140bit | 長期運用向け |

### 1.2 ECDSA（Elliptic Curve Digital Signature Algorithm）

#### 概要

| 項目 | 内容 |
|------|------|
| **種別** | 楕円曲線暗号 |
| **基盤** | 楕円曲線上の離散対数問題 |
| **利点** | RSAより短い鍵長で同等のセキュリティ |
| **ICAO要件** | 256bit以上 |

#### ICAO許可曲線

| 曲線名 | サイズ | セキュリティビット | 備考 |
|--------|--------|------------------|------|
| **brainpoolP256r1** | 256bit | 128bit | 推奨 |
| **brainpoolP384r1** | 384bit | 192bit | 推奨 |
| **brainpoolP512r1** | 512bit | 256bit | 推奨 |
| NIST P-256 | 256bit | 128bit | 許可（Named Curve注意） |
| NIST P-384 | 384bit | 192bit | 許可 |
| NIST P-521 | 521bit | 256bit | 許可 |

#### ICAO特有の楕円曲線要件

IMPORTANT: ICAO 9303はNamed Curvesの使用を禁止

```
【必須要件】
✅ 楕円曲線パラメータを明示的に記述（Explicit）
✅ 点形式は非圧縮形式（Uncompressed）
❌ Named Curves（OIDによる参照）は不可
```

#### 明示的パラメータの構造

```asn1
ECParameters ::= SEQUENCE {
    version   INTEGER,
    fieldID   FieldID,           -- 体のタイプ（素体 or 二元体）
    curve     Curve,             -- a, b パラメータ
    base      ECPoint,           -- ベースポイント G
    order     INTEGER,           -- 位数 n
    cofactor  INTEGER OPTIONAL   -- 補因子 h
}
```

### 1.3 DSA（Digital Signature Algorithm）

| 項目 | 内容 |
|------|------|
| **状態** | 許可（非推奨） |
| **要件** | 2048bit以上 |
| **備考** | 新規実装にはECDSA推奨 |

## 2. ハッシュアルゴリズム

### 2.1 SHA-2ファミリー

| アルゴリズム | 出力サイズ | ブロックサイズ | OID | ICAO |
|-------------|-----------|---------------|-----|------|
| **SHA-224** | 224bit | 512bit | 2.16.840.1.101.3.4.2.4 | 許可 |
| **SHA-256** | 256bit | 512bit | 2.16.840.1.101.3.4.2.1 | 推奨 |
| **SHA-384** | 384bit | 1024bit | 2.16.840.1.101.3.4.2.2 | 許可 |
| **SHA-512** | 512bit | 1024bit | 2.16.840.1.101.3.4.2.3 | 許可 |

### 2.2 非推奨アルゴリズム

| アルゴリズム | 状態 | 理由 |
|-------------|------|------|
| **SHA-1** | 非推奨 | 衝突攻撃の実証（2017年） |
| **MD5** | 禁止 | 衝突攻撃が容易 |

### 2.3 用途別ハッシュ要件

| 用途 | 最小要件 | 推奨 |
|------|---------|------|
| SOD署名 | SHA-224 | SHA-256 |
| データグループハッシュ | SHA-224 | SHA-256 |
| 証明書署名 | SHA-256 | SHA-256 |
| BAC鍵導出 | SHA-1 | - |

## 3. 対称暗号アルゴリズム

### 3.0 プロトコル別暗号化方式（BAC/PACE/EAC）

| プロトコル | 暗号化方式 | 備考 |
|-----------|-----------|------|
| **BAC** | 3DES（Triple DES） | レガシー、2027年以降は非推奨 |
| **PACE** | AES-128/256 | Forward Secrecy対応、2027年以降は実装必須 |
| **EAC** | AES-256（EACセッション後） | 政府機関専用、民間利用不可 |

### 3.1 AES（Advanced Encryption Standard）

| 項目 | 内容 |
|------|------|
| **ブロックサイズ** | 128bit |
| **鍵長** | 128/192/256bit |
| **モード** | CBC（BAC/PACE）、CMAC |

#### AES使用箇所

| プロトコル | 用途 | モード |
|-----------|------|--------|
| PACE | セキュアメッセージング | CBC |
| CA | セッション暗号化 | CBC |
| EAC | セッション暗号化 | AES-256 |

### 3.2 3DES（Triple DES）

| 項目 | 内容 |
|------|------|
| **ブロックサイズ** | 64bit |
| **鍵長** | 112bit（2キー）、168bit（3キー） |
| **状態** | レガシー（BAC用） |
| **使用プロトコル** | BAC |

IMPORTANT: 新規実装ではAESを使用。3DESはBAC後方互換のみ

## 4. 鍵導出関数（KDF）

### 4.1 BAC鍵導出

```
【BAC鍵導出手順】

Step 1: MRZ情報の結合
  K_seed = SHA-1(MRZ_info)[0:16]

  MRZ_info = 文書番号 || 生年月日 || 有効期限
            （各フィールドにチェックデジット付き）

Step 2: 派生鍵の生成
  K_enc = KDF(K_seed, 1)  -- 暗号化鍵
  K_mac = KDF(K_seed, 2)  -- MAC鍵

Step 3: KDF計算
  KDF(K, c) = SHA-1(K || counter)[0:16]
  counter = 00000001 (c=1) または 00000002 (c=2)
```

### 4.2 PACE鍵導出

```
【PACE鍵導出】

入力: 共有秘密 K（DH/ECDH結果）

K_enc = KDF(K, 1)  -- 暗号化鍵
K_mac = KDF(K, 2)  -- MAC鍵

KDF: SHA-256ベース（ICAO推奨）
```

## 5. メッセージ認証コード（MAC）

### 5.1 CMAC（Cipher-based MAC）

| 項目 | 内容 |
|------|------|
| **規格** | NIST SP 800-38B |
| **基盤** | AES |
| **用途** | PACE、CA |

### 5.2 Retail MAC（ISO 9797-1 Algorithm 3）

| 項目 | 内容 |
|------|------|
| **基盤** | DES/3DES |
| **用途** | BAC |
| **状態** | レガシー |

## 6. 鍵合意プロトコル

### 6.1 Diffie-Hellman（DH）

| 項目 | 内容 |
|------|------|
| **基盤** | 離散対数問題 |
| **用途** | AA、CA（オプション） |
| **要件** | 2048bit以上 |

### 6.2 ECDH（Elliptic Curve Diffie-Hellman）

| 項目 | 内容 |
|------|------|
| **基盤** | 楕円曲線上の離散対数問題 |
| **用途** | CA、PACE |
| **推奨曲線** | brainpoolP256r1以上 |

## 7. アルゴリズム選択ガイドライン

### 7.1 新規実装推奨

| 用途 | 推奨アルゴリズム |
|------|-----------------|
| 署名 | ECDSA（brainpoolP256r1） or RSA-4096 |
| ハッシュ | SHA-256 |
| 対称暗号 | AES-256 |
| 鍵合意 | ECDH（brainpoolP256r1） |
| MAC | CMAC-AES |

### 7.2 後方互換性

| レガシー | 対応 |
|---------|------|
| BAC（3DES） | 必須サポート（多くのパスポートで使用） |
| SHA-1（MRZ hash） | BAC互換のため必要 |
| RSA-2048 | サポート継続 |

## 8. 実装上の注意

### 8.1 楕円曲線の検証

```python
# 楕円曲線パラメータ検証の例
def validate_ec_params(cert):
    # 1. Named Curveでないことを確認
    if cert.public_key_algorithm.named_curve:
        raise ValidationError("Named Curve not allowed")

    # 2. 明示的パラメータの存在確認
    params = cert.public_key.ec_parameters
    if not all([params.field, params.curve, params.base, params.order]):
        raise ValidationError("Explicit parameters required")

    # 3. 点形式の確認（非圧縮）
    if params.base[0] != 0x04:
        raise ValidationError("Uncompressed point format required")
```

### 8.2 セキュリティ考慮事項

- **鍵長の定期見直し**: NISTガイドラインに従い更新
- **アルゴリズム移行**: SHA-1依存部分の段階的排除
- **サイドチャネル対策**: 定数時間実装の使用

---

**関連ドキュメント**:
- [SECURITY-MECHANISMS.md](SECURITY-MECHANISMS.md) - 各メカニズムでの使用方法
- [PKI-INFRASTRUCTURE.md](PKI-INFRASTRUCTURE.md) - 証明書での使用
- [GLOSSARY.md](GLOSSARY.md) - 用語定義
