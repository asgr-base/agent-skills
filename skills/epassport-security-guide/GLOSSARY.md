# 暗号・PKI用語集

## A

### AA（Active Authentication）
ICチップの真正性を検証するメカニズム。チャレンジ-レスポンス方式でクローンを検出。

### AES（Advanced Encryption Standard）
米国標準の対称暗号アルゴリズム。ブロックサイズ128bit、鍵長128/192/256bit。PACE、CAで使用。

### AKI（Authority Key Identifier）
証明書拡張フィールド。発行者（上位CA）の公開鍵を識別。OID: 2.5.29.35

### ASN.1（Abstract Syntax Notation One）
データ構造を記述するための標準記法。証明書やSODの構造定義に使用。

## B

### BAC（Basic Access Control）
MRZ情報を使用したアクセス制御メカニズム。3DESベース。レガシー技術。

### Basic Constraints
証明書拡張フィールド。CA証明書かエンドエンティティ証明書かを示す。OID: 2.5.29.19

### brainpool曲線
ドイツBSIが設計した楕円曲線群。ICAO推奨。brainpoolP256r1, brainpoolP384r1, brainpoolP512r1。

## C

### CA（Chip Authentication）
ECDH鍵合意によるクローン検出とセッション暗号化を提供するメカニズム。

### CAN（Card Access Number）
PACEで使用される6桁のアクセス番号。パスポート表面に印刷。

### CDP（CRL Distribution Point）
CRLの取得URLを示す証明書拡張フィールド。OID: 2.5.29.31

### CMAC（Cipher-based MAC）
AESベースのメッセージ認証コード。NIST SP 800-38B。PACE、CAで使用。

### CMS（Cryptographic Message Syntax）
暗号化データの標準フォーマット。RFC 3852。SOD、Master Listで使用。

### CRL（Certificate Revocation List）
失効した証明書のリスト。CSCAが署名。90日以内の更新が必須。

### CSCA（Country Signing Certificate Authority）
各国政府が管理するルート証明書。自己署名。DSCを署名。

### CSCA Link証明書
CSCA鍵更新時に使用される証明書。旧CSCAが新CSCAを署名し信頼を継承。

### CVCA（Country Verifying Certificate Authority）
EACにおける検証国のルートCA。TAで使用。

## D

### DES（Data Encryption Standard）
旧式の対称暗号。単体では使用せず、3DESとして使用。

### 3DES（Triple DES）
DESを3回適用する暗号方式。BACで使用。レガシー技術。

### DG（Data Group）
ePassport ICチップ内のデータ格納単位。DG1（MRZ）、DG2（顔写真）等。

### DH（Diffie-Hellman）
鍵合意プロトコル。離散対数問題に基づく。CAで使用（RSA版）。

### DSC（Document Signer Certificate）
文書署名証明書。CSCAが署名。SODに埋め込み。

### DVCA（Document Verifying Certificate Authority）
EACにおける中間CA。CVCAとISの間。

## E

### EAC（Extended Access Control）
拡張アクセス制御。DG3（指紋）、DG4（虹彩）へのアクセスに必要。

### ECDH（Elliptic Curve Diffie-Hellman）
楕円曲線上の鍵合意プロトコル。CA、PACEで使用。

### ECDSA（Elliptic Curve Digital Signature Algorithm）
楕円曲線デジタル署名アルゴリズム。ICAO推奨。

### eMRTD（electronic Machine Readable Travel Document）
電子機械可読旅行文書。ePassportの正式名称。

### Explicit Parameters
楕円曲線パラメータを証明書内に明示的に記述する方式。ICAO必須。

## F

### Forward Secrecy
過去のセッション鍵が漏洩しても過去の通信が解読されない特性。CA、PACEで提供。

## H

### Hash（ハッシュ）
任意長データを固定長に変換する一方向関数。SHA-256等。

## I

### ICAO（International Civil Aviation Organization）
国際民間航空機関。ePassport規格（Doc 9303）を策定。

### IS（Inspection System）
検査システム。TAにおける読取端末の証明書。

## K

### KDF（Key Derivation Function）
共有秘密からセッション鍵を導出する関数。

### Key Usage
証明書拡張フィールド。鍵の使用目的を示す。OID: 2.5.29.15

## L

### LDS（Logical Data Structure）
ePassport ICチップのデータ構造仕様。ICAO 9303 Part 10。

### LDAP（Lightweight Directory Access Protocol）
ディレクトリサービスアクセスプロトコル。ICAO PKDへのアクセスに使用。

### LDIF（LDAP Data Interchange Format）
LDAPデータの交換フォーマット。PKDの一括ダウンロードに使用。

## M

### MAC（Message Authentication Code）
メッセージの完全性と認証を提供するコード。CMAC、Retail MAC等。

### Master List
信頼するCSCA証明書のリスト。MLSCが署名。

### MLSC（Master List Signer Certificate）
Master Listを署名する証明書。CSCAが署名。

### MRZ（Machine Readable Zone）
機械可読領域。パスポートの下部に印刷された2行または3行の文字列。

## N

### Named Curves
楕円曲線をOIDで参照する方式。ICAO禁止。

### NFC（Near Field Communication）
近距離無線通信。ePassport ICチップとの通信に使用。

## O

### OID（Object Identifier）
オブジェクト識別子。階層的な数値列でアルゴリズムや拡張を識別。

## P

### PA（Passive Authentication）
SOD署名検証によるデータ完全性・真正性検証。必須メカニズム。

### PACE（Password Authenticated Connection Establishment）
パスワードベースの安全なアクセス制御。BAC後継。

### PKD（Public Key Directory）
公開鍵ディレクトリ。ICAOが運営。CSCA、DSC、CRLを配布。

### PKI（Public Key Infrastructure）
公開鍵基盤。証明書による信頼チェーンを構築。

### PSS（Probabilistic Signature Scheme）
RSAの確率的署名方式。RSASSA-PSS。ICAO許可。

## R

### Retail MAC
ISO 9797-1 Algorithm 3。DESベースのMAC。BACで使用。

### RSA（Rivest-Shamir-Adleman）
公開鍵暗号方式。素因数分解困難性に基づく。

## S

### SHA（Secure Hash Algorithm）
NISTが設計したハッシュアルゴリズム群。SHA-256推奨。

### SKI（Subject Key Identifier）
証明書拡張フィールド。証明書の公開鍵を識別。OID: 2.5.29.14

### SM（Secure Messaging）
セキュアメッセージング。BAC/PACE/CA後の暗号化通信。

### SOD（Security Object Document）
セキュリティオブジェクト。データグループのハッシュリストとDSC署名を含む。

## T

### TA（Terminal Authentication）
端末認証。EACで読取端末の権限を検証。

### TRNG（True Random Number Generator）
真性乱数生成器。ハードウェアベースの乱数生成。

## X

### X.509
ITU-T勧告。公開鍵証明書の標準フォーマット。

---

## 数値・記号

### 2.5.29.x
X.509証明書拡張のOID接頭辞。

### 2.23.136.x
ICAO固有のOID接頭辞。

---

**関連ドキュメント**:
- [CRYPTOGRAPHIC-ALGORITHMS.md](CRYPTOGRAPHIC-ALGORITHMS.md) - アルゴリズム詳細
- [PKI-INFRASTRUCTURE.md](PKI-INFRASTRUCTURE.md) - PKI構造詳細
- [SECURITY-MECHANISMS.md](SECURITY-MECHANISMS.md) - メカニズム詳細
