# tap-released

A [Singer](https://www.singer.io/) tap that extracts data from **Released**. It is built with [hotglue-singer-sdk](https://github.com/hotgluexyz/HotglueSingerSDK) and speaks the standard Singer message protocol on stdout, so you can pair it with any compatible target.

## Features

- **REST**-style HTTP streams (see `client.py` / `streams.py`).
- **Bearer token** auth via a long-lived **`access_token`** (no refresh-token flow).

- Configurable **`api_url`** and optional **`start_date`** (see [Configuration](#configuration)).

### Streams

| Stream | Endpoint / notes | Primary key | Replication key |
| ------ | ---------------- | ----------- | ----------------- |
| `companies` | `GET` `/companies` — parent of contacts; records in `Data` | `Id` | — (full table) |
| `contacts` | `GET` `/contacts?companyId=&updatedAfterDate=` — child of companies | `Id` | `UpdatedDateTime` |
| `invoices` | `GET` `/invoices?updatedAfterDate=` | `Id` | `UpdatedDate` |

## Requirements

- Python **3.10+** (see `requires-python` in `pyproject.toml`).

## Installation

1. **Clone** this repository and `cd` into the project directory.
2. **Create `config.json`** in the project root with your credentials and settings (see [Configuration](#configuration) for the fields and an example).
3. **Create a virtual environment** and activate it:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows, use `.venv\Scripts\activate` instead of `source .venv/bin/activate`.

4. **Install the package** in editable mode:

```bash
pip install -e .
```

5. **Run the tap** (with the venv still activated):

```bash
tap-released --help
```

## Configuration

| Setting | Type | Required | Default | Description |
| ------- | ---- | -------- | ------- | ----------- |
| `access_token` | string | yes | — | Long-lived Bearer access token (sensitive). |
| `start_date` | string (datetime) | no | `2000-01-01T00:00:00Z` | Earliest record date to sync. |
| `api_url` | string | no | `https://api.re-leased.com/api` | Base URL for the API. |

Run `tap-released --about` (or `tap-released --about --format=markdown`) for the authoritative schema for your installed version.

### Example `config.json`

```json
{
  "start_date": "2000-01-01T00:00:00Z",
  "api_url": "https://api.re-leased.com/api",
  "access_token": "YOUR_ACCESS_TOKEN"
}
```

Do not commit real credentials. Prefer environment variables or a secrets manager in production.

### Environment-based config

You can load settings from the process environment using `--config=ENV` (the SDK merges env into config). Env names follow the tap’s setting keys (see `tap-released --about`).

## Usage

With your virtual environment **activated** and `config.json` in place:

Discover stream catalog:

```bash
tap-released --config config.json --discover > catalog.json
```

Run a sync (with optional state):

```bash
tap-released --config config.json --catalog catalog.json --state state.json
```

Pipe to any Singer target:

```bash
tap-released --config config.json --catalog catalog.json | target-jsonl
```

Inspect built-in settings and stream metadata:

```bash
tap-released --about
```

## API / documentation

TODO: Add your vendor’s base URLs, auth docs, and links (compare to the “API hosts” section in a finished tap README).


## License
MIT — see `LICENSE` and `pyproject.toml`.
