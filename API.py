import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

TARGET_AMOUNT = 500
OUTPUT_FILE = "tenders.json"
PROGRESS_STEP = 100

BASE_URL = "https://public-api.prozorro.gov.ua/api/2.5/tenders"
EXCLUDED_IDS = {"", "99999999", "88888888"}
MAX_WORKERS = 8


def update_database(target_amount: int = TARGET_AMOUNT, output_path: str = OUTPUT_FILE) -> float:
    def create_session() -> requests.Session:
        session = requests.Session()
        session.headers.update({"User-Agent": "ProzorroHackathonClient/1.0"})
        retry = Retry(
            total=5,
            backoff_factor=1.0,
            status_forcelist=(429, 500, 502, 503, 504),
        )
        adapter = HTTPAdapter(max_retries=retry, pool_connections=MAX_WORKERS, pool_maxsize=MAX_WORKERS)
        session.mount("https://", adapter)
        return session

    def is_valid_numeric(value) -> bool:
        if value is None:
            return False
        try:
            num = float(value)
        except (TypeError, ValueError):
            return False
        if num <= 0:
            return False
        str_val = str(int(num)) if num.is_integer() else str(num)
        return str_val not in EXCLUDED_IDS and str(value).strip() not in EXCLUDED_IDS

    def parse_tender(session: requests.Session, tender_uuid: str) -> dict | None:
        try:
            resp = session.get(f"{BASE_URL}/{tender_uuid}", timeout=15)
            if resp.status_code != 200:
                return None
            data = resp.json().get("data") or {}
        except (requests.RequestException, ValueError):
            return None

        if data.get("status") != "complete":
            return None

        items = data.get("items") or []
        if len(items) != 1:
            return None

        item = items[0] or {}
        qty = item.get("quantity")
        procuring_entity = data.get("procuringEntity") or {}
        buyer_id = str((procuring_entity.get("identifier") or {}).get("id") or "").strip()

        awards = data.get("awards") or []
        active_award = next((a for a in awards if a.get("status") == "active"), awards[-1] if awards else None)

        supplier_id = ""
        supplier_name = ""
        value_obj = data.get("value") or {}

        if active_award:
            suppliers = active_award.get("suppliers") or []
            if suppliers:
                supplier_id = str((suppliers[0].get("identifier") or {}).get("id") or "").strip()
                supplier_name = (suppliers[0].get("name") or "").strip()
            if active_award.get("value"):
                value_obj = active_award["value"]

        if not supplier_id:
            contracts = data.get("contracts") or []
            if contracts:
                suppliers = contracts[-1].get("suppliers") or []
                if suppliers:
                    supplier_id = str((suppliers[0].get("identifier") or {}).get("id") or "").strip()
                    supplier_name = (suppliers[0].get("name") or "").strip()

        amount = value_obj.get("amount")
        currency = value_obj.get("currency") or "UAH"

        if not is_valid_numeric(amount) or not is_valid_numeric(qty):
            return None
        if buyer_id in EXCLUDED_IDS or supplier_id in EXCLUDED_IDS:
            return None

        tender_id = data.get("tenderID") or tender_uuid
        return {
            "id": tender_id,
            "title": data.get("title") or "",
            "status": "complete",
            "date": data.get("date") or data.get("dateModified") or "",
            "buyer_id": buyer_id,
            "buyer_name": procuring_entity.get("name") or "",
            "supplier_id": supplier_id,
            "supplier_name": supplier_name,
            "amount": float(amount),
            "currency": currency,
            "desc": item.get("description") or "",
            "qty": float(qty),
            "unit": (item.get("unit") or {}).get("code") or "",
            "cpv": (item.get("classification") or {}).get("id") or "",
            "url": f"https://prozorro.gov.ua/tender/{tender_id}",
        }

    def save_to_file(records: list[dict]) -> None:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)

    start_time = time.perf_counter()
    session = create_session()
    collected: list[dict] = []
    lock = threading.Lock()
    last_reported = 0

    next_url = f"{BASE_URL}?descending=1&limit=100&opt_fields=status"
    print(f"Розпочато пошук інформації про {target_amount} найновіших тендерів.\n")
    print(f"Знайдено: 0/{target_amount}")

    try:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            while len(collected) < target_amount and next_url:
                try:
                    feed_resp = session.get(next_url, timeout=15)
                    feed_resp.raise_for_status()
                    feed_json = feed_resp.json()
                except (requests.RequestException, ValueError) as e:
                    print(f"[Помилка стрічки Prozorro]: {e}. Повтор через 2 сек...")
                    time.sleep(2)
                    continue

                entries = feed_json.get("data") or []
                raw_next = (feed_json.get("next_page") or {}).get("uri")
                next_url = raw_next.replace("http://", "https://", 1) if raw_next else None

                if not entries:
                    break

                candidate_uuids = [
                    entry["id"]
                    for entry in entries
                    if entry.get("status") in (None, "complete")
                ]

                futures = [executor.submit(parse_tender, session, uuid) for uuid in candidate_uuids]
                for future in as_completed(futures):
                    tender = future.result()
                    if tender is None:
                        continue

                    with lock:
                        if len(collected) >= target_amount:
                            break
                        collected.append(tender)
                        current = len(collected)
                        if current - last_reported >= PROGRESS_STEP or current == target_amount:
                            last_reported = (current // PROGRESS_STEP) * PROGRESS_STEP
                            save_to_file(list(collected[:target_amount]))
                            print(f"Знайдено: {current}/{target_amount}")
    except KeyboardInterrupt:
        print("\nЗупинено користувачем. Зберігаю зібрані дані...")

    save_to_file(collected[:target_amount])
    elapsed = round(time.perf_counter() - start_time, 2)
    print(f"\nІнформацію про тендери ({len(collected)} шт.) успішно завантажено у файл {output_path}.")
    print(f"Операція тривала {elapsed} секунд.")
    return elapsed


if __name__ == "__main__":
    update_database()