"""
Seed script for unicore mock source database.
Generates realistic Serbian bank fixed assets data for development and demo purposes.
"""

import uuid
import random
import psycopg2
from datetime import date, datetime, timedelta
from decimal import Decimal
from faker import Faker

fake = Faker("hr_HR")  # Croatian — closest available Balkan locale
random.seed(42)

DB = dict(host="localhost", port=5433, dbname="unicore", user="unicore", password="unicore")

# ── domain constants ────────────────────────────────────────────────────────

CATEGORIES = [
    ("IT-LAP",  "OS",  Decimal("25.00"), 48),
    ("IT-SRV",  "OS",  Decimal("25.00"), 48),
    ("IT-NET",  "OS",  Decimal("25.00"), 48),
    ("IT-MON",  "OS",  Decimal("33.33"), 36),
    ("IT-TEL",  "OS",  Decimal("25.00"), 48),
    ("FURN",    "OS",  Decimal("10.00"), 120),
    ("VEHI",    "OS",  Decimal("20.00"), 60),
    ("BLDG-OWN","OS",  Decimal("2.50"),  480),
    ("BLDG-IMP","OS",  Decimal("10.00"), 120),
    ("SW-LIC",  "NU",  Decimal("33.33"), 36),
    ("SW-DEV",  "NU",  Decimal("20.00"), 60),
]

ASSET_NAMES = {
    "IT-LAP":   ["Dell Latitude 5540", "Lenovo ThinkPad T14", "HP EliteBook 840", "Apple MacBook Pro"],
    "IT-SRV":   ["Dell PowerEdge R750", "HP ProLiant DL380", "IBM System x3650"],
    "IT-NET":   ["Cisco Catalyst 9300", "Fortinet FortiGate 200F", "Juniper EX3400"],
    "IT-MON":   ["Dell P2422H Monitor", "LG 27UK850 Monitor", "Samsung 27\" Monitor"],
    "IT-TEL":   ["Cisco IP Phone 8841", "Polycom VVX 450", "Yealink T54W"],
    "FURN":     ["Radni sto izvršni", "Kancelarijska stolica ergonomska", "Ormar za dokumentaciju", "Konferencijski sto"],
    "VEHI":     ["Volkswagen Passat", "Škoda Octavia", "Renault Megane", "Ford Focus"],
    "BLDG-OWN": ["Poslovni objekat centrala", "Poslovni objekat filijala NS", "Poslovni objekat filijala NI"],
    "BLDG-IMP": ["Ulaganje u zakupljeni prostor BG PAL", "Ulaganje u zakupljeni prostor BG VOZ", "Ulaganje u zakupljeni prostor NS"],
    "SW-LIC":   ["Microsoft Office 365 licenca", "Adobe Acrobat licenca", "Oracle DB licenca", "SAP licenca"],
    "SW-DEV":   ["CRM sistem interno", "Platni promet modul", "Reporting platforma interna"],
}

LOCATIONS = [
    "LOC-HQ-BG", "LOC-BG-PAL", "LOC-BG-VOZ", "LOC-BG-NOV",
    "LOC-NS-CTR", "LOC-NS-LIM", "LOC-NI-CTR", "LOC-KG-CTR",
    "LOC-DC-BG",
]

COST_CENTERS = [
    "CC-IT-INF", "CC-IT-DEV", "CC-FIN-ACC", "CC-FIN-REP",
    "CC-RE-MGT", "CC-HR-GEN", "CC-OPS-GEN", "CC-RET-BG",
    "CC-RET-NS", "CC-RET-NI",
]

ORG_UNITS = ["OU-IT", "OU-FIN", "OU-RE", "OU-HR", "OU-OPS", "OU-RET"]

SUPPLIERS = ["SUP-001", "SUP-002", "SUP-003", "SUP-004", "SUP-005"]

ACCOUNTING_USERS = [
    ("ACC-01", "Marija Petrović"),
    ("ACC-02", "Nikola Jovanović"),
    ("ACC-03", "Ana Đorđević"),
    ("ACC-04", "Stefan Nikolić"),
]

# acquisition amounts by category (min, max)
AMOUNTS = {
    "IT-LAP":   (80_000,  250_000),
    "IT-SRV":   (300_000, 1_500_000),
    "IT-NET":   (150_000, 800_000),
    "IT-MON":   (30_000,  80_000),
    "IT-TEL":   (15_000,  50_000),
    "FURN":     (20_000,  150_000),
    "VEHI":     (1_500_000, 4_000_000),
    "BLDG-OWN": (50_000_000, 200_000_000),
    "BLDG-IMP": (5_000_000, 30_000_000),
    "SW-LIC":   (100_000, 2_000_000),
    "SW-DEV":   (500_000, 5_000_000),
}

START_DATE = date(2023, 1, 1)
END_DATE   = date(2025, 12, 31)


# ── helpers ──────────────────────────────────────────────────────────────────

def uid() -> str:
    return str(uuid.uuid4())


def rand_date(start: date, end: date) -> date:
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


def months_between(d1: date, d2: date) -> int:
    return (d2.year - d1.year) * 12 + d2.month - d1.month


def period_code(y: int, m: int) -> str:
    return f"{y}-{m:02d}"


def maker_checker():
    m, c = random.sample(ACCOUNTING_USERS, 2)
    return m, c


# ── seeders ──────────────────────────────────────────────────────────────────

def seed_period_calendar(cur):
    print("  seeding period_calendar …")
    rows = []
    for year in (2023, 2024, 2025):
        for month in range(1, 13):
            first = date(year, month, 1)
            if month == 12:
                last = date(year, 12, 31)
            else:
                last = date(year, month + 1, 1) - timedelta(days=1)
            locked = "true" if (year, month) < (2026, 1) else "false"
            rows.append((uid(), period_code(year, month), year, month, first, last, locked, None))

    cur.executemany(
        """INSERT INTO finance_svc.period_calendar
           (id, period_code, fiscal_year, fiscal_period, starts_on, ends_on, locked_flag, lock_reason)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
        rows,
    )
    print(f"    inserted {len(rows)} periods")


def seed_assets(cur, n: int = 150):
    print(f"  seeding {n} assets …")
    assets = []
    preparations = []
    book_states = []
    assignments = []
    operation_requests = []

    prep_counter = 1
    asset_counter = 1
    req_counter = 1

    # a small set are disposed (10%) or in preparation (5%)
    disposed_indices = set(random.sample(range(n), k=int(n * 0.10)))
    prep_only_indices = set(random.sample(range(n - int(n * 0.10)), k=int(n * 0.05)))

    for i in range(n):
        cat_code, asset_type, dep_rate, useful_life = random.choice(CATEGORIES)
        asset_name = random.choice(ASSET_NAMES[cat_code])
        low, high = AMOUNTS[cat_code]
        acq = Decimal(str(round(random.uniform(low, high), 2)))

        activation_dt = rand_date(START_DATE, date(2025, 6, 30))
        prep_dt = activation_dt - timedelta(days=random.randint(5, 30))

        prep_id = uid()
        prep_number = f"PREP-{prep_counter:05d}"
        prep_counter += 1

        is_prep_only = i in prep_only_indices
        is_disposed  = i in disposed_indices

        prep_status = "ACTIVATED" if not is_prep_only else "PENDING"
        preparations.append((
            prep_id, prep_number, asset_type, cat_code,
            random.choice(SUPPLIERS), acq, "RSD", prep_status,
            None, f"{asset_name} — nabavka",
            datetime.combine(prep_dt, datetime.min.time()),
            random.choice(ACCOUNTING_USERS)[0], None, None,
        ))

        if is_prep_only:
            continue

        asset_id = uid()
        asset_number = f"OS-{asset_counter:06d}"
        asset_counter += 1

        lifecycle_status = "DISPOSED" if is_disposed else "ACTIVE"
        disposal_date = rand_date(activation_dt + timedelta(days=180), END_DATE) if is_disposed else None

        # calculate book value
        months_active = months_between(activation_dt, disposal_date or END_DATE)
        monthly_dep = acq * dep_rate / Decimal("100") / Decimal("12")
        max_dep_months = int(Decimal(str(useful_life)))
        dep_months = min(months_active, max_dep_months)
        acc_dep = min(monthly_dep * dep_months, acq).quantize(Decimal("0.01"))
        book_val = (acq - acc_dep).quantize(Decimal("0.01"))

        assets.append((
            asset_id, asset_number, asset_type, cat_code, asset_name,
            lifecycle_status, activation_dt, activation_dt, "RSD", acq, book_val,
            datetime.combine(activation_dt, datetime.min.time()),
            random.choice(ACCOUNTING_USERS)[0], None, None,
        ))

        # book state (one current record)
        book_states.append((
            uid(), asset_id, acq, acc_dep, book_val,
            dep_rate, "PROPORTIONAL", activation_dt, None,
        ))

        # assignment
        loc = random.choice(LOCATIONS)
        cc  = random.choice(COST_CENTERS)
        ou  = random.choice(ORG_UNITS)
        person_id = f"EMP-{random.randint(100,999)}"
        person_name = fake.name()
        assignments.append((
            uid(), asset_id, ou, cc, loc,
            person_id, person_name, activation_dt, None,
            datetime.combine(activation_dt, datetime.min.time()),
        ))

        # activation operation request
        maker, checker = maker_checker()
        verified_dt = datetime.combine(activation_dt + timedelta(days=random.randint(0, 2)), datetime.min.time())
        operation_requests.append((
            uid(), asset_id, prep_id,
            f"REQ-{req_counter:06d}", "ACTIVATION", "VERIFIED",
            activation_dt, None,
            datetime.combine(prep_dt + timedelta(days=1), datetime.min.time()),
            maker[0], verified_dt, checker[0],
        ))
        req_counter += 1

        # disposal operation request
        if is_disposed and disposal_date:
            maker2, checker2 = maker_checker()
            verified_disp = datetime.combine(disposal_date + timedelta(days=1), datetime.min.time())
            operation_requests.append((
                uid(), asset_id, None,
                f"REQ-{req_counter:06d}", "DISPOSAL", "VERIFIED",
                disposal_date, None,
                datetime.combine(disposal_date, datetime.min.time()),
                maker2[0], verified_disp, checker2[0],
            ))
            req_counter += 1

    cur.executemany(
        """INSERT INTO asset_svc.asset_preparation
           (id, preparation_number, asset_type, category_code, supplier_code,
            acquisition_amount, currency_code, preparation_status, source_document_id,
            description, created_at, created_by, updated_at, updated_by)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        preparations,
    )

    cur.executemany(
        """INSERT INTO asset_svc.asset
           (id, asset_number, asset_type, category_code, asset_name,
            lifecycle_status, activation_date, depreciation_start_date,
            currency_code, acquisition_amount, book_amount,
            created_at, created_by, updated_at, updated_by)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        assets,
    )

    cur.executemany(
        """INSERT INTO asset_svc.asset_book_state
           (id, asset_id, gross_amount, accumulated_depreciation, net_amount,
            depreciation_rate, accounting_method, effective_from, effective_to)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        book_states,
    )

    cur.executemany(
        """INSERT INTO asset_svc.asset_assignment
           (id, asset_id, organization_unit_code, cost_center_code, location_code,
            accountable_person_id, accountable_person_name,
            effective_from, effective_to, created_at)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        assignments,
    )

    cur.executemany(
        """INSERT INTO asset_svc.asset_operation_request
           (id, asset_id, preparation_id, request_number, operation_type,
            workflow_status, requested_effective_date, requested_payload,
            created_at, created_by, verified_at, verified_by)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        operation_requests,
    )

    asset_ids = [row[0] for row in assets]
    print(f"    inserted {len(assets)} assets, {len(book_states)} book states, "
          f"{len(assignments)} assignments, {len(operation_requests)} operation requests")
    return asset_ids


def seed_depreciation_runs(cur, asset_ids: list[str]):
    print("  seeding depreciation runs …")
    runs = []
    run_items = []
    workflow_cases = []
    workflow_actions = []
    accounting_events = []

    run_counter = 1
    case_counter = 1
    event_counter = 1

    # fetch activation dates so we only depreciate after activation
    cur.execute("SELECT id, activation_date, acquisition_amount, category_code FROM asset_svc.asset WHERE lifecycle_status != 'DISPOSAL'")
    asset_meta = {row[0]: {"activation": row[1], "acq": row[2], "cat": row[3]} for row in cur.fetchall()}

    dep_rates = {c: r for c, _, r, _ in CATEGORIES}

    for year in (2023, 2024, 2025):
        for month in range(1, 13):
            pcode = period_code(year, month)
            period_end = date(year, month, 1)
            # mark future periods as not yet run
            if period_end > date(2025, 12, 1):
                continue

            run_id = uid()
            started = datetime(year, month, 28, 1, 0, 0)
            completed = datetime(year, month, 28, 1, 30, 0)

            runs.append((
                run_id, f"DEP-RUN-{run_counter:05d}", pcode,
                "COMPLETED", started, started, completed, "ACC-01",
            ))
            run_counter += 1

            # workflow case for this run
            maker, checker = maker_checker()
            case_id = uid()
            workflow_cases.append((
                case_id, f"WF-{case_counter:06d}", "DepreciationRun", run_id,
                "DEPRECIATION_APPROVAL", "VERIFIED",
                maker[0], maker[1], checker[0], checker[1],
                started, completed, None, None, None,
            ))
            workflow_actions.append((uid(), case_id, "SUBMIT", maker[0], maker[1], started, None))
            workflow_actions.append((uid(), case_id, "VERIFY", checker[0], checker[1], completed, None))
            case_counter += 1

            # items: one per active asset that was activated before this period
            period_month_start = date(year, month, 1)
            eligible = [
                aid for aid, meta in asset_meta.items()
                if meta["activation"] is not None and meta["activation"] < period_month_start
            ]

            total_amount = Decimal("0")
            for aid in eligible:
                meta = asset_meta[aid]
                rate = dep_rates.get(meta["cat"], Decimal("10.00"))
                monthly = (meta["acq"] * rate / Decimal("100") / Decimal("12")).quantize(Decimal("0.01"))

                run_items.append((
                    uid(), run_id, aid,
                    # asset_number not available here, set None
                    None, monthly, "POSTED", None,
                ))
                total_amount += monthly

            # one accounting event per run
            accounting_events.append((
                uid(), f"ACC-EVT-{event_counter:06d}", case_id,
                "DepreciationRun", run_id,
                completed.date(), "RSD", total_amount,
                "POSTED", None, completed,
            ))
            event_counter += 1

    cur.executemany(
        """INSERT INTO finance_svc.depreciation_run
           (id, run_number, period_code, run_status, scheduled_at, started_at, completed_at, initiated_by)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
        runs,
    )
    cur.executemany(
        """INSERT INTO finance_svc.depreciation_run_item
           (id, depreciation_run_id, asset_id, asset_number, amount, status, note)
           VALUES (%s,%s,%s,%s,%s,%s,%s)""",
        run_items,
    )
    cur.executemany(
        """INSERT INTO finance_svc.workflow_case
           (id, case_number, aggregate_type, aggregate_id, operation_type, workflow_status,
            maker_user_id, maker_username, checker_user_id, checker_username,
            submitted_at, verified_at, returned_at, comment_text, correlation_id)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        workflow_cases,
    )
    cur.executemany(
        """INSERT INTO finance_svc.workflow_action
           (id, workflow_case_id, action_type, actor_user_id, actor_username, action_at, comment_text)
           VALUES (%s,%s,%s,%s,%s,%s,%s)""",
        workflow_actions,
    )
    cur.executemany(
        """INSERT INTO finance_svc.accounting_event
           (id, event_number, workflow_case_id, aggregate_type, aggregate_id,
            accounting_date, currency_code, amount, event_status, payload, created_at)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        accounting_events,
    )

    print(f"    inserted {len(runs)} runs, {len(run_items)} run items, "
          f"{len(workflow_cases)} workflow cases, {len(accounting_events)} accounting events")


def seed_codebooks(cur):
    print("  seeding codebooks …")
    now = datetime.now()
    codebooks = []
    entries = []

    def add_codebook(key, name, domain, items):
        cb_id = uid()
        codebooks.append((cb_id, key, name, domain, "ACTIVE", None, now, "SYSTEM"))
        for i, (ekey, eval_) in enumerate(items):
            entries.append((uid(), cb_id, ekey, eval_, None, "ACTIVE", i + 1, None, None, None))

    add_codebook("ASSET_TYPE", "Tip imovine", "asset", [
        ("OS",   "Osnovno sredstvo"),
        ("NU",   "Nematerijalno ulaganje"),
        ("IN",   "Investiciona nekretnina"),
        ("TUOS", "Ulaganje u tuđa OS"),
    ])

    add_codebook("LIFECYCLE_STATUS", "Status životnog ciklusa", "asset", [
        ("IN_PREPARATION", "U pripremi"),
        ("ACTIVE",         "Aktivno"),
        ("DISPOSED",       "Otpisano"),
        ("SOLD",           "Prodato"),
        ("DONATED",        "Donirano"),
    ])

    add_codebook("OPERATION_TYPE", "Tip operacije", "workflow", [
        ("ACTIVATION",        "Aktivacija"),
        ("DISPOSAL",          "Otpis"),
        ("SALE",              "Prodaja"),
        ("LOCATION_CHANGE",   "Promena lokacije"),
        ("CUSTODIAN_CHANGE",  "Promena računopolagača"),
        ("DEPRECIATION_APPROVAL", "Odobrenje amortizacije"),
        ("VALUE_INCREASE",    "Uvećanje vrednosti"),
        ("COMPONENT_REPLACEMENT", "Zamena rezervnog dela"),
    ])

    add_codebook("WORKFLOW_STATUS", "Status workflow-a", "workflow", [
        ("DRAFT",    "Nacrt"),
        ("SUBMITTED","Podnet"),
        ("VERIFIED", "Verifikovan"),
        ("RETURNED", "Vraćen"),
        ("REJECTED", "Odbijen"),
    ])

    add_codebook("CURRENCY_CODE", "Valuta", "finance", [
        ("RSD", "Srpski dinar"),
        ("EUR", "Euro"),
        ("USD", "Američki dolar"),
        ("CHF", "Švajcarski franak"),
    ])

    add_codebook("DEPRECIATION_METHOD", "Metoda amortizacije", "finance", [
        ("PROPORTIONAL", "Proporcionalna metoda"),
        ("DEGRESSIVE",   "Degresivna metoda"),
    ])

    cur.executemany(
        """INSERT INTO reference_svc.codebook
           (id, codebook_key, codebook_name, owning_domain, status, description, created_at, created_by)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
        codebooks,
    )
    cur.executemany(
        """INSERT INTO reference_svc.codebook_entry
           (id, codebook_id, entry_key, entry_value, description, status, sort_order,
            effective_from, effective_to, parent_entry_id)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        entries,
    )
    print(f"    inserted {len(codebooks)} codebooks, {len(entries)} entries")


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    print("Connecting to unicore mock source …")
    conn = psycopg2.connect(**DB)
    conn.autocommit = False
    cur = conn.cursor()

    try:
        print("Seeding reference data …")
        seed_codebooks(cur)

        print("Seeding period calendar …")
        seed_period_calendar(cur)

        print("Seeding assets …")
        asset_ids = seed_assets(cur)

        print("Seeding depreciation runs …")
        seed_depreciation_runs(cur, asset_ids)

        conn.commit()
        print("\nDone. All data committed.")

    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
