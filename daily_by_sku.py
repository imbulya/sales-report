"""Считает по sales.csv файл daily_by_sku.csv: заказы и выручка по артикулу и дню."""
import csv
import sys
from collections import defaultdict

SRC = sys.argv[1] if len(sys.argv) > 1 else "sales.csv"
DST = sys.argv[2] if len(sys.argv) > 2 else "daily_by_sku.csv"

# В выгрузке встречаются "Delivered", "delivered " и "canceled" - приводим к двум статусам
STATUS_ALIASES = {"canceled": "cancelled"}


def normalize_status(raw):
    status = raw.strip().lower()
    return STATUS_ALIASES.get(status, status)


def main():
    seen = set()  # номера уже учтённых заказов
    orders = defaultdict(int)
    revenue = defaultdict(int)

    with open(SRC, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            order_id = row["order_id"].strip()
            if order_id in seen:  # дубль строки - пропускаем
                continue
            seen.add(order_id)

            status = normalize_status(row["status"])
            if status not in ("delivered", "cancelled"):
                sys.exit(f"Неизвестный статус {row['status']!r} в заказе {order_id}")

            key = (row["sku"].strip(), row["order_date"].strip())
            orders[key] += 1
            if status == "delivered":
                # у delivered пустого quantity нет (проверено); если появится - упадём, а не посчитаем неверно
                revenue[key] += int(row["quantity"]) * int(row["price"])

    with open(DST, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["sku", "order_date", "orders", "revenue"])
        for sku, day in sorted(orders):
            writer.writerow([sku, day, orders[(sku, day)], revenue[(sku, day)]])

    print(f"Заказов: {len(seen)}, строк в {DST}: {len(orders)}")


if __name__ == "__main__":
    main()
