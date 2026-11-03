"""Независимая проверка daily_by_sku.csv: другой способ расчёта (pandas) + контрольные суммы."""
import pandas as pd

raw = pd.read_csv("sales.csv", dtype=str, keep_default_na=False)
res = pd.read_csv("daily_by_sku.csv")

d = raw.drop_duplicates().copy()
d["status"] = d["status"].str.strip().str.lower().replace({"canceled": "cancelled"})
d["rev"] = pd.to_numeric(d["quantity"], errors="coerce").fillna(0) * d["price"].astype(int)
d.loc[d["status"] != "delivered", "rev"] = 0
exp = d.groupby(["sku", "order_date"]).agg(orders=("order_id", "count"), revenue=("rev", "sum")).reset_index()

assert d["order_id"].is_unique, "после удаления дублей номера заказов должны быть уникальны"
assert exp.equals(res.astype({"orders": "int64", "revenue": "float64"}).astype(exp.dtypes.to_dict())), "расчёты расходятся"
assert res["orders"].sum() == raw["order_id"].nunique(), "сумма orders != число уникальных заказов"
assert res.sort_values(["sku", "order_date"]).equals(res), "неверная сортировка"
assert not res.duplicated(["sku", "order_date"]).any()
print("OK: строк", len(res), "| заказов", res["orders"].sum(), "| выручка", res["revenue"].sum())
