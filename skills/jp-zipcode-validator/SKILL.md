---
name: jp-zipcode-validator
description: Validate Japanese postal codes against addresses using ZipCloud API
version: 1.1.0
author: claude_code
createDate: 2025-12-27
updateDate: 2026-01-25
---

# JP Zipcode Validator Skill

## Purpose

This skill validates Japanese postal codes against addresses using the ZipCloud API (based on Japan Post official data). It can detect mismatches, missing prefectures, and kanji errors in address data.

## Skill Activation

Activate this skill when the user requests to:
- "郵便番号と住所を検証して"
- "郵便番号のチェックをして"
- "Validate postal codes"
- "Check zipcode accuracy"

## Features

1. **Postal Code Validation**: Verifies if postal codes match the provided addresses
2. **Address Parsing**: Extracts prefecture, city, and town from addresses
3. **Error Detection**: Identifies:
   - Missing prefectures
   - Mismatched postal codes and addresses
   - Kanji errors in town names
4. **CSV Processing**: Reads CSV files with address data and generates validation reports
5. **Auto-correction Suggestions**: Provides expected addresses based on postal codes

## Input Format

CSV file with the following columns:
- 名前 (Name)
- 郵便番号 (Postal Code)
- 住所 (Address)

## Output

1. **Console Report**: Displays validation results with:
   - Match/mismatch status
   - Expected addresses for mismatches
   - Summary statistics
2. **CSV Report**: Generates a detailed CSV file with validation results

## Usage Instructions

### Step 1: Prepare the Script

Copy `validate_zipcode.py` to the working directory where the CSV file is located.

### Step 2: Run Validation

```bash
cd /path/to/csv/directory
python3 validate_zipcode.py
```

The script will:
1. Read the input CSV file (e.g., `住所一覧.csv`)
2. Validate each postal code against its address
3. Display results in the console
4. Save a detailed report to `検証結果_郵便番号.csv`

### Step 3: Review Results

The validation report includes:
- **総件数**: Total number of records
- **一致**: Number of matches
- **不一致**: Number of mismatches
- **不一致データの詳細**: Detailed list of mismatches with expected addresses

### Step 4: Fix Issues (if needed)

Common issues and fixes:
1. **Missing Prefecture**: Add the prefecture name (e.g., "埼玉県") to the address
2. **Kanji Errors**: Correct town name kanji based on the expected address
3. **Wrong Postal Code**: Update the postal code to match the address

## Technical Details

### API Used

- **ZipCloud API**: https://zipcloud.ibsnet.co.jp/api/search
- **Data Source**: Japan Post official postal code database
- **Rate Limiting**: Built-in 0.1-second delay between requests
- **Caching**: Responses are cached to reduce API calls

### Address Parsing Logic

The script uses regex to extract:
- Prefecture: `^(北海道|東京都|大阪府|京都府|.{2,3}県)`
- City: `^(.+?[市区町村]|.+?郡.+?[町村])`
- Town: Remaining part after city

### Validation Logic

1. Normalize postal code (remove hyphens, convert full-width to half-width)
2. Fetch official address from API
3. Compare input address with official address:
   - Prefecture: Exact match
   - City: Exact match
   - Town: Partial match (allows house numbers)

## Example

### Input CSV

```csv
名前,郵便番号,住所
行平 直子,357-0021,飯能市双柳17-2
小嶋 こま江,198-0052,東京都青梅市長渕1-958-1
```

### Validation Output

```
[1] 行平 直子
    郵便番号: 357-0021
    住所: 飯能市双柳17-2
    ✗ 郵便番号と住所が一致しません
    期待される住所: 埼玉県飯能市双柳

[2] 小嶋 こま江
    郵便番号: 198-0052
    住所: 東京都青梅市長渕1-958-1
    ✗ 郵便番号と住所が一致しません
    期待される住所: 東京都青梅市長淵
```

### Fixes

1. Row 1: Add "埼玉県" → `埼玉県飯能市双柳17-2`
2. Row 2: Fix kanji "渕" → "淵" → `東京都青梅市長淵1-958-1`

## Important Guidelines

1. **Always use ZipCloud API**: Do not use offline CSV files unless necessary
2. **Respect rate limits**: The script includes built-in delays (0.1s per request)
3. **Verify matches carefully**: Partial matches may not be errors if house numbers are included
4. **Backup before fixing**: Always create a backup CSV before making corrections
5. **Run re-validation**: After fixing issues, re-run validation to confirm 100% match rate

## Error Handling

- **API connection errors**: Displayed with error message, validation continues
- **Invalid postal codes**: Flagged as "郵便番号が7桁ではありません"
- **Postal code not found**: Flagged as "郵便番号が見つかりません"
- **Address mismatch**: Shows expected addresses from postal code

## Tool Usage

Required tools for this skill:

- **Bash**: To run the Python validation script
- **Read**: To read the input CSV file
- **Write**: To create the validation report CSV
- **Python**: To execute the validation logic

## Files

- `validate_zipcode.py`: Main validation script (located in this skill folder)

## Activation Example

```
User: 郵便番号と住所が一致しているか確認してください
Assistant: [Activates zipcode-validator skill and runs validation]
```

## Version History

- **1.0.0** (2025-12-27): Initial version
  - ZipCloud API integration
  - CSV validation support
  - Auto-correction suggestions
