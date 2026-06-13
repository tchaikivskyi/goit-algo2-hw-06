import hashlib
from typing import Any


class BloomFilter:
    def __init__(self, size: int, num_hashes: int):
        if not isinstance(size, int) or size <= 0:
            raise ValueError("size має бути додатним цілим числом")

        if not isinstance(num_hashes, int) or num_hashes <= 0:
            raise ValueError("num_hashes має бути додатним цілим числом")

        self.size = size
        self.num_hashes = num_hashes
        self.bit_array = bytearray(size)

    def _hashes(self, item: str):
        for i in range(self.num_hashes):
            value = f"{i}:{item}".encode("utf-8")
            digest = hashlib.sha256(value).hexdigest()
            yield int(digest, 16) % self.size

    def add(self, item: Any) -> bool:
        if not isinstance(item, str) or item == "":
            return False

        for index in self._hashes(item):
            self.bit_array[index] = 1

        return True

    def __contains__(self, item: Any) -> bool:
        if not isinstance(item, str) or item == "":
            return False

        return all(self.bit_array[index] == 1 for index in self._hashes(item))


def check_password_uniqueness(bloom_filter: BloomFilter, passwords: list[Any]) -> dict[Any, str]:
    results = {}

    for password in passwords:
        if not isinstance(password, str) or password == "":
            results[password] = "некоректне значення"
            continue

        if password in bloom_filter:
            results[password] = "вже використаний"
        else:
            results[password] = "унікальний"
            bloom_filter.add(password)

    return results


if __name__ == "__main__":
    bloom = BloomFilter(size=1000, num_hashes=3)

    existing_passwords = ["password123", "admin123", "qwerty123"]

    for password in existing_passwords:
        bloom.add(password)

    new_passwords_to_check = ["password123", "newpassword", "admin123", "guest"]

    results = check_password_uniqueness(bloom, new_passwords_to_check)

    for password, status in results.items():
        print(f"Пароль '{password}' - {status}.")
