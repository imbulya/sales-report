"""Ищет в sales.csv дубли, опечатки и пропуски по заданным критериям. Файл ничего не меняет, только печатает."""
import sys

import pandas as pd

SRC = sys.argv[1] if len(sys.argv) > 1 else "sales.csv"
SHOW = 5  # сколько примеров строк показывать для каждой проблемы

# dtype=str и keep_default_na=False: читаем всё как текст, чтобы пустые ячейки и пробелы не потерялись
d = pd.read_csv(SRC, dtype=str, keep_default_na=False)

dates = pd.to_datetime(d["order_date"], format="%Y-%m-%d", errors="coerce")
checks = {
    "полные дубли строк": d.duplicated(keep="first"),
    "повтор order_id": d["order_id"].duplicated(keep="first"),
    "order_id не из цифр": ~d["order_id"].str.fullmatch(r"\d+"),
    "order_date пустая или не ГГГГ-ММ-ДД": dates.isna(),
    "sku не вида UYT-0000": ~d["sku"].str.fullmatch(r"UYT-\d{4}"),
    "quantity пустое или не целое > 0": ~d["quantity"].str.fullmatch(r"[1-9]\d*"),
    "price пустая или не целая > 0": ~d["price"].str.fullmatch(r"[1-9]\d*"),
    "status не ровно delivered/cancelled": ~d["status"].isin(["delivered", "cancelled"]),
}

print(f"Всего строк: {len(d)}")
for name, mask in checks.items():
    print(f"\n{name}: {mask.sum()}")
    if mask.any():
        print(d[mask].head(SHOW).to_string())

print("\nВарианты статуса:")
print(d["status"].map(repr).value_counts().to_string())
