# Off-Market Retail Property Scrape — Summary

- Run timestamp (UTC): 2026-04-28T19:12:34.478524+00:00
- Total raw candidates collected: **1000**
- Total valid properties after filter+dedupe: **50**
- Total rejected: **0**

## Source breakdown
- `la_pais`: 50

## Off-market signal breakdown
- `owner_held_retail`: 50

## Rejection reasons

## Notable filtering / scoring logic
- Strict retail filter using a regex over property_type/subtype/notes.
- Hard size cap at 20,000 sqft.
- Geography filter against configured target states.
- Dedupe key: APN > address+city+state > name+city > source URL.
- Confidence score weighted by off-market signal (tax-defaulted > FDIC OREO > GSA surplus > government auction > withdrawn/expired > assessor-only).
- Records sorted by confidence_score then completeness_score.
- Robots.txt is checked per-host before every request; disallowed URLs are skipped.
- All adapter failures are caught so partial runs still produce output.
