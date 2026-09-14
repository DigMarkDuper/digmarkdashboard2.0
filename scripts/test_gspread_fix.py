"""
Regression test for the Google Sheets integration fix in digmarkdashboard2.0.

Root cause being guarded: the audit commit removed the `auth/drive` scope from
init_connection(). gspread `client.open(<title>)` searches the Drive API and
requires that scope, so every data loader silently returned empty -> dashboard
showed no Google Sheets data. Fix routes all opens through
`client.open_by_key(<spreadsheet_key>)`, which only needs the `spreadsheets`
scope (present) and reads the key from st.secrets (never hardcoded).

This harness runs WITHOUT production secrets/network:
  - Fake `open_by_key` records the key it is given.
  - Fake `open(title)` raises AssertionError, so any leftover title-based open
    makes the test fail immediately (the exact regression we removed).

Run:  cd ~/digmarkdashboard2.0 && python scripts/test_gspread_fix.py
"""
import sys, types, os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
sys.setrecursionlimit(2000)

# ---------------------------------------------------------------------------
# 1. Stub `streamlit` (heavy / interactive) with just what utils.py touches.
# ---------------------------------------------------------------------------
errors = []

class _Secrets(dict):
    pass

class _SessionState(dict):
    clear = None

streamlit = types.ModuleType("streamlit")
streamlit.secrets = _Secrets()
streamlit.session_state = _SessionState()
streamlit.errors = errors

def _cache_resource(*a, **k):
    if a and callable(a[0]):          # bare @st.cache_resource
        return a[0]
    def deco(fn):                      # @st.cache_resource(...)
        return fn
    return deco

def _cache_data(*a, **k):              # always used with parens: @st.cache_data(ttl=N)
    def deco(fn):
        return fn
    return deco

streamlit.cache_resource = _cache_resource
streamlit.cache_data = _cache_data
streamlit.error = staticmethod(lambda msg: errors.append(str(msg)))

sys.modules["streamlit"] = streamlit  # register stub so `import streamlit` resolves

# ---------------------------------------------------------------------------
# 2. Fake gspread + oauth2client: prove open_by_key is used, never open(title).
# ---------------------------------------------------------------------------
class FakeWorksheet:
    def __init__(self, records=None):
        self._records = records or [{"ColA": 1, "ColB": "x"}]
    def get_all_records(self):
        return self._records
    def get_all_values(self):
        return [list(r.keys()) for r in self._records]
    def append_rows(self, rows, value_input_option=None):
        return {"updates": []}
    def row_values(self, n):
        return list(self._records[0].keys()) if self._records else []
    def update_cell(self, r, c, v):
        return self
    def append_row(self, values):
        return self
    def clear(self):
        return self

class FakeWorkbook:
    def __init__(self, n_sheets=10):
        self._sheets = {i: FakeWorksheet() for i in range(n_sheets)}
    def get_worksheet(self, idx):
        return self._sheets.get(idx, FakeWorksheet())

class FakeClient:
    def __init__(self):
        self.opened_keys = []
        self.opened_titles = []
    def open_by_key(self, key):
        self.opened_keys.append(key)
        return FakeWorkbook()
    def open(self, title):
        self.opened_titles.append(title)
        raise AssertionError(
            "REGRESSION: client.open(title) must not be used - it requires the "
            "Drive scope that was removed by the audit. Use open_by_key()."
        )

# Patch gspread.authorize + oauth2client credential builder.
gspread = types.ModuleType("gspread")
client = FakeClient()
gspread.authorize = staticmethod(lambda creds: client)
sys.modules["gspread"] = gspread

oauth2client = types.ModuleType("oauth2client")
oauth2client.service_account = types.ModuleType("oauth2client.service_account")
oauth2client.service_account.ServiceAccountCredentials = type(
    "ServiceAccountCredentials", (), {"from_json_keyfile_dict": staticmethod(
        lambda data, scope: ("FAKE-CREDS", scope))})
sys.modules["oauth2client"] = oauth2client
sys.modules["oauth2client.service_account"] = oauth2client.service_account

# ---------------------------------------------------------------------------
# 3. Configure secrets and import the real module under test.
# ---------------------------------------------------------------------------
streamlit.secrets["gcp_service_account"] = {
    "type": "service_account",
    "client_email": "fake@example.iam.gserviceaccount.com",
    "private_key": "-----BEGIN PRIVATE KEY-----\\nfake\\n-----END PRIVATE KEY-----\\n",
}
streamlit.secrets["spreadsheet_key"] = "FAKE_SPREADSHEET_KEY_123"

from components import utils as U
U.time.sleep = lambda s: None   # keep the parallel-fetch fast in tests

FAILURES = []

def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        FAILURES.append(name)

# --- Test A: open_master resolves by key from secrets, not by title ------
client.opened_keys.clear(); client.opened_titles.clear()
wb = U.open_master()
check("A1 open_master returns workbook", wb is not None)
check("A2 uses open_by_key with the secrets key",
      client.opened_keys == ["FAKE_SPREADSHEET_KEY_123"])
check("A3 never calls open(title)",
      U.time.sleep is not None and client.opened_titles == [])

# --- Test B: main data path returns a full bundle of DataFrames ----------
client.opened_keys.clear()
bundle = U.fetch_all_master_data()
check("B1 fetch_all_master_data returns bundle", isinstance(bundle, dict) and bundle is not None)
expected_keys = {0,1,2,3,4,6,7,8,9}
check("B2 bundle has all expected tab keys", expected_keys <= set(bundle.keys()))
check("B3 every tab resolves to a DataFrame",
      all(isinstance(bundle[i], __import__("pandas").DataFrame) for i in bundle))

# --- Test C: page-level loaders surface data -----------------------------
streamlit.session_state.bundle = bundle
df = U.load_sosmed()
check("C1 load_sosmed returns non-empty DataFrame",
      isinstance(df, __import__("pandas").DataFrame) and not df.empty)
dfwa = U.load_wa_admin()
check("C2 load_wa_admin works", isinstance(dfwa, __import__("pandas").DataFrame))

# --- Test D: write path (append) still works through open_by_key ---------
client.opened_keys.clear()
ok = U.append_sheet_rows(U.TAB['CRM'], [["6281", "Nama Test", "", "2026-01-01"]])
check("D1 append_sheet_rows returns True", ok is True)
check("D2 append used open_by_key (not title)",
      client.opened_keys == ["FAKE_SPREADSHEET_KEY_123"])

# --- Test E: update path works -------------------------------------------
client.opened_keys.clear()
ok = U.update_sheet_cell(U.TAB['CRM'], 0, "ColA", "99")
check("E1 update_sheet_cell returns True", ok is True)
check("E2 update used open_by_key", client.opened_keys == ["FAKE_SPREADSHEET_KEY_123"])

print()
if FAILURES:
    print("RESULT: %d FAILURE(S): %s" % (len(FAILURES), FAILURES))
    sys.exit(1)
print("RESULT: ALL CHECKS PASSED - Google Sheets path restored (open_by_key)")