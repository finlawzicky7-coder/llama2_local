# Off-Market Retail Property Scraper

A modular Python framework for assembling a clean dataset of small (≤ 20,000 sqft)
retail properties that are likely **off-market** — meaning the parcel is not
actively syndicated on the major CRE listing services. Default geography is
California (the user-supplied default), with optional fall-through to TX, FL,
AZ, NV, GA.

## What "off-market" means here

This scraper does **not** scrape the major CRE marketplaces (LoopNet, Crexi,
CoStar, BizBuySell, etc.). Their Terms of Service explicitly prohibit
automated collection. Instead the framework targets sources where the
asset is, by definition, not on a marketplace:

| Source                | Off-market signal                            | Status              |
| --------------------- | -------------------------------------------- | ------------------- |
| LA County PAIS (ArcGIS) | Owner-held retail parcel, not listed       | **Working**         |
| GSA realestatesales.gov | Federal surplus, GSA disposal              | Blocked by remote 503 in this run; re-runs may succeed |
| FDIC OREO             | Failed-bank receivership asset               | Blocked by remote 503 in this run |
| Bid4Assets county tax sales | County tax-defaulted parcels (CA R&T 3691) | Storefront returns 403; supply parcel CSV via env var (see below) |
| GovDeals / SBA        | Government collateral / surplus auction      | Blocked by remote 403 |

Every adapter respects `robots.txt` — see `retail_scraper/http.py`. The
framework will refuse to fetch any URL the host disallows.

## Layout

```
retail_scraper/
├── retail_scraper/
│   ├── __init__.py
│   ├── __main__.py            # `python -m retail_scraper`
│   ├── cli.py                 # argparse entry point
│   ├── config.py              # ScraperConfig
│   ├── http.py                # HTTP client w/ retries, throttle, robots.txt
│   ├── models.py              # PropertyRecord, RejectedCandidate
│   ├── pipeline.py            # filter, dedupe, score, rank
│   ├── output.py              # CSV / JSON / markdown writers
│   ├── runner.py              # orchestrator
│   └── adapters/
│       ├── base.py            # BaseAdapter ABC
│       ├── la_pais.py         # LA County Assessor — primary live source
│       ├── gsa_realestatesales.py
│       ├── fdic_ore.py
│       ├── bid4assets_county.py
│       └── sba_oreo.py
├── tests/
│   └── test_pipeline.py       # smoke tests for filter/dedupe/score
├── outputs/                   # CSV / JSON / SUMMARY produced here
├── logs/                      # per-run timestamped log file
├── requirements.txt
└── README.md
```

## Setup

```bash
cd retail_scraper
python -m pip install -r requirements.txt
```

Python 3.10+ recommended.

## Running

Default — CA, ≤ 20,000 sqft, target 50:

```bash
python -m retail_scraper
```

Override states / target size / count:

```bash
python -m retail_scraper --states CA TX FL --max-sqft 15000 --target 75
```

Disable specific adapters:

```bash
python -m retail_scraper --disable fdic_ore sba_oreo
```

Outputs land in `outputs/`:

* `retail_offmarket.csv` — final ranked records
* `retail_offmarket.json` — same records, JSON
* `retail_offmarket_rejected.csv` — anything filtered out, with reason
* `SUMMARY.md` — totals, source breakdown, signal breakdown, notes

A timestamped log is written to `logs/run-<UTC>.log`.

## Supplying an offline parcel list (Bid4Assets)

County-published parcel lists for tax-defaulted sales are public. Many
counties post them as PDF/CSV on their treasurer's website. Once you've
downloaded an authorized list, normalize it to the schema below and point
the env var at the file:

```
APN,address,city,state,zip,use_code,total_sqft,lot_sqft,min_bid,sale_id
```

```bash
BID4ASSETS_PARCEL_LIST_PATH=./data/riverside_apr2026.csv python -m retail_scraper
```

Only rows whose `use_code` matches a retail pattern (store/strip/restaurant/
service-station/single-tenant/etc.) are accepted. The full pattern lives in
`retail_scraper/adapters/bid4assets_county.py`.

## Tests

```bash
python tests/test_pipeline.py
```

## Confidence scoring

Off-market signals are weighted from highest to lowest:

| signal                       | weight |
| ---------------------------- | ------ |
| `tax_defaulted`              | 0.95   |
| `fdic_oreo`                  | 0.90   |
| `federal_surplus`            | 0.85   |
| `government_auction`         | 0.80   |
| `withdrawn`                  | 0.70   |
| `expired`                    | 0.65   |
| `stale_ownership_long_hold`  | 0.65   |
| `owner_held_retail`          | 0.55   |
| `assessor_owner_lead`        | 0.50   |
| `owner_listed`               | 0.50   |

Records are sorted by confidence then completeness; the top `--target`
records are written to the output files.

## Honest notes on this run

* The sandbox this scraper was built in had several remote 503/403
  responses from `realestatesales.gov`, `fdic-ore.com`, `bid4assets.com`,
  and `govdeals.com`. The framework retried with exponential backoff and
  then logged the failure. Those adapters are still useful from a host
  with normal connectivity.
* The 50 records actually produced in this run all come from
  **LA County Assessor PAIS — Sales Parcels** (an open, robots-allowed
  ArcGIS REST endpoint at
  `assessor.gis.lacounty.gov/assessor/rest/services/PAIS/pais_sales_parcels`).
  Each record has a verifiable APN, situs address, building size, year
  built, and last-sale information.
* No property data is fabricated. If a field is unknown the column is
  empty.
* To diversify sources beyond LA County, supply a county tax-sale parcel
  CSV (see above) or run from a host that can reach the federal disposal
  sites.

## Extending

Add a new adapter under `retail_scraper/adapters/`, subclass
`BaseAdapter`, implement `fetch() -> List[PropertyRecord]`, and register
it in `retail_scraper/adapters/__init__.py` and
`retail_scraper/runner.py`. The HTTP client passed in handles retries,
throttling, and robots.txt for free.

## Compliance

* `robots.txt` is fetched per-host and consulted before every request.
* Configurable user-agent identifies the tool and a contact address.
* Per-host throttle is on by default (1 second between requests).
* No source is accessed in a way that requires bypassing authentication
  or paywalls.
