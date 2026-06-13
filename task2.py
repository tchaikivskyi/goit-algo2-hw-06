import re
import time
from pathlib import Path

import hyperloglog
import pandas as pd


IP_PATTERN = re.compile(
    r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b"
)


def is_valid_ip(ip: str) -> bool:
    parts = ip.split(".")

    if len(parts) != 4:
        return False

    for part in parts:
        if not part.isdigit():
            return False

        number = int(part)

        if number < 0 or number > 255:
            return False

    return True


def load_ip_addresses(file_path: str) -> list[str]:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Файл не знайдено: {file_path}")

    ip_addresses = []

    with path.open("r", encoding="utf-8", errors="ignore") as file:
        for line in file:
            match = IP_PATTERN.search(line)

            if not match:
                continue

            ip = match.group()

            if is_valid_ip(ip):
                ip_addresses.append(ip)

    return ip_addresses


def count_unique_exact(ip_addresses: list[str]) -> int:
    return len(set(ip_addresses))


def count_unique_hll(ip_addresses: list[str], error_rate: float = 0.01) -> int:
    hll = hyperloglog.HyperLogLog(error_rate)

    for ip in ip_addresses:
        hll.add(ip)

    return int(len(hll))


def measure_time(func, *args):
    start = time.perf_counter()
    result = func(*args)
    end = time.perf_counter()

    return result, end - start


def compare_methods(file_path: str) -> pd.DataFrame:
    ip_addresses = load_ip_addresses(file_path)

    exact_count, exact_time = measure_time(count_unique_exact, ip_addresses)
    hll_count, hll_time = measure_time(count_unique_hll, ip_addresses)

    results = pd.DataFrame(
        {
            "Точний підрахунок": [float(exact_count), round(exact_time, 6)],
            "HyperLogLog": [float(hll_count), round(hll_time, 6)],
        },
        index=["Унікальні елементи", "Час виконання (сек.)"],
    )

    return results


if __name__ == "__main__":
    log_file = "lms-stage-access.log"

    try:
        comparison = compare_methods(log_file)

        print("Результати порівняння:")
        print(comparison)

    except FileNotFoundError as error:
        print(error)
        print("Покладіть файл lms-stage-access.log в одну папку з цим скриптом.")
