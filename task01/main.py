from collections import deque, defaultdict

def build_logistic_graph():
    # Вузли: super → Terminals (T1, T2) → Warehouses (S1–S4) → Shops (M1–M14) → sink
    graph = defaultdict(list)
    cap = {}

    def add_edge(u, v, c):
        graph[u].append(v)
        graph[v].append(u)
        cap[(u, v)] = c
        cap[(v, u)] = 0

    # 1) super → Terminals
    add_edge('super', 'T1', 25+20+15)  # 60
    add_edge('super', 'T2', 15+30+10)  # 55

    # 2) Terminals → Warehouses
    add_edge('T1', 'S1', 25)
    add_edge('T1', 'S2', 20)
    add_edge('T1', 'S3', 15)
    add_edge('T2', 'S3', 15)
    add_edge('T2', 'S4', 30)
    add_edge('T2', 'S2', 10)

    # 3) Warehouses → Shops
    add_edge('S1', 'M1', 15)
    add_edge('S1', 'M2', 10)
    add_edge('S1', 'M3', 20)
    add_edge('S2', 'M4', 15)
    add_edge('S2', 'M5', 10)
    add_edge('S2', 'M6', 25)
    add_edge('S3', 'M7', 20)
    add_edge('S3', 'M8', 15)
    add_edge('S3', 'M9', 10)
    add_edge('S4', 'M10', 20)
    add_edge('S4', 'M11', 10)
    add_edge('S4', 'M12', 15)
    add_edge('S4', 'M13', 5)
    add_edge('S4', 'M14', 10)

    # 4) Shops → sink
    shop_caps = [15,10,20,15,10,25,20,15,10,20,10,15,5,10]  # M1..M14
    for i, c in enumerate(shop_caps, start=1):
        add_edge(f'M{i}', 'sink', c)

    return graph, cap

def edmonds_karp(graph, cap, source='super', sink='sink'):
    flow = defaultdict(int)
    max_flow = 0

    while True:
        # BFS пошук шляху з позитивною пропускною здатністю
        parent = {source: None}
        queue = deque([source])
        while queue and sink not in parent:
            u = queue.popleft()
            for v in graph[u]:
                if v not in parent and cap[(u, v)] - flow[(u, v)] > 0:
                    parent[v] = u
                    queue.append(v)
        if sink not in parent:
            break  # більше немає шляху

        # Знаходимо bottleneck
        v = sink
        bottleneck = float('inf')
        while v != source:
            u = parent[v]
            bottleneck = min(bottleneck, cap[(u, v)] - flow[(u, v)])
            v = u

        # Оновлюємо потоки
        v = sink
        while v != source:
            u = parent[v]
            flow[(u, v)] += bottleneck
            flow[(v, u)] -= bottleneck
            v = u

        max_flow += bottleneck

    return max_flow, flow

def decompose_flow(graph, flow):
    # Розкладаємо мережевий потік на s-t шляхи
    def dfs(u, t, visited):
        if u == t:
            return []
        visited.add(u)
        for v in graph[u]:
            if (u, v) in flow and flow[(u, v)] > 0 and v not in visited:
                rest = dfs(v, t, visited)
                if rest is not None:
                    return [(u, v)] + rest
        return None

    residual = flow.copy()
    paths = []
    while True:
        path = dfs('super', 'sink', set())
        if not path:
            break
        f = min(residual[e] for e in path)
        paths.append((path, f))
        for e in path:
            residual[e] -= f

    return paths

# --- Виконання ---
graph, cap = build_logistic_graph()
max_flow, flow = edmonds_karp(graph, cap)
paths = decompose_flow(graph, flow)

# Зведення потоку Terminal→Shop
terminal_map = {'T1': 'Термінал 1', 'T2': 'Термінал 2'}
shop_map = {f'M{i}': f'Магазин {i}' for i in range(1, 15)}
agg = defaultdict(int)
for path, f in paths:
    t = path[0][1]          # другий вузол у шляху: T1 або T2
    shop = path[-2][1]      # вузол перед sink: M?
    agg[(terminal_map[t], shop_map[shop])] += f

# Вивід
print(f"Максимальний потік мережі: {max_flow} одиниць\n")
print("| Термінал    | Магазин    | Фактичний Потік (одиниць) |")
print("|-------------|------------|---------------------------|")
for (t, s), v in sorted(agg.items()):
    print(f"| {t:<11} | {s:<10} | {v:>25} |")
