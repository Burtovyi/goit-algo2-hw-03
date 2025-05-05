import csv
import random
import timeit
from BTrees.OOBTree import OOBTree

def load_items(filename: str):
    """Завантажує товари з CSV у список словників."""
    items = []
    with open(filename, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row['Price'] = float(row['Price'])
            items.append(row)
    return items

def build_structures(items):
    """
    Будує:
      – tree: OOBTree, ключ = ціна, значення = список товарів
      – d: стандартний dict, ключ = ID, значення = словник атрибутів
    """
    tree = OOBTree()
    d = {}
    for item in items:
        price = item['Price']
        # додаємо товар у список за ключем price
        lst = tree.get(price)
        if lst is None:
            tree[price] = [item]
        else:
            lst.append(item)
        # паралельно — у dict
        d[item['ID']] = item
    return tree, d

def range_query_tree(tree: OOBTree, low: float, high: float):
    """Швидкий запит по ціні через .items(min, max)."""
    res = []
    for price, bucket in tree.items(min=low, max=high):
        res.extend(bucket)
    return res

def range_query_dict(d: dict, low: float, high: float):
    """Лінійний перебір по всім товарам dict."""
    return [item for item in d.values() if low <= item['Price'] <= high]

def main():
    # Для відтворюваності
    random.seed(0)

    # 1) Завантажуємо дані
    items = load_items('generated_items_data.csv')

    # 2) Будуємо структури
    tree, d = build_structures(items)

    # 3) Готуємо 100 випадкових діапазонів [low, high]
    prices = [it['Price'] for it in items]
    p_min, p_max = min(prices), max(prices)
    queries = []
    for _ in range(100):
        low = random.uniform(p_min, p_max)
        high = random.uniform(low, p_max)
        queries.append((low, high))

    # 4) Замір часу для OOBTree
    start = timeit.default_timer()
    for low, high in queries:
        range_query_tree(tree, low, high)
    tree_time = timeit.default_timer() - start

    # 5) Замір часу для dict
    start = timeit.default_timer()
    for low, high in queries:
        range_query_dict(d, low, high)
    dict_time = timeit.default_timer() - start

    # 6) Вивід результатів
    print(f"Total range_query time for OOBTree: {tree_time:.6f} seconds")
    print(f"Total range_query time for Dict:     {dict_time:.6f} seconds")

if __name__ == '__main__':
    main()
