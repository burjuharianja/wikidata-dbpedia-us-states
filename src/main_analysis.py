import pandas as pd
import re
import networkx as nx
from itertools import combinations

# =========================
# 1. Load data
# =========================
wd_raw = pd.read_csv("data_raw/wikidata_us_states.csv")
db_raw = pd.read_csv("data_raw/dbpedia_us_states.csv")

print("Shape Wikidata raw:", wd_raw.shape)
print("Shape DBpedia raw :", db_raw.shape)

# =========================
# 2. Helper functions
# =========================
def norm_text(x):
    if pd.isna(x):
        return ""
    x = str(x).strip().lower()
    x = re.sub(r"[^a-z0-9]+", "", x)
    return x

def first_not_null(series):
    for v in series:
        if pd.notna(v):
            return v
    return None

def combine_unique(series):
    vals = []
    for v in series.dropna():
        parts = [p.strip() for p in str(v).split(",")]
        vals.extend([p for p in parts if p and p.lower() != "nan"])
    vals = sorted(set(vals))
    return ", ".join(vals) if vals else None

def merge_text(a, b):
    vals = []
    for v in [a, b]:
        if pd.notna(v):
            parts = [p.strip() for p in str(v).split(",")]
            vals.extend([p for p in parts if p and p.lower() != "nan"])
    vals = sorted(set(vals))
    return ", ".join(vals) if vals else None

# =========================
# 3. Normalisasi label
# =========================
wd_raw["state_key"] = wd_raw["stateLabel"].apply(norm_text)
db_raw["state_key"] = db_raw["stateLabel"].apply(norm_text)

# =========================
# 4. Siapkan node Wikidata
# =========================
wd_nodes = wd_raw[
    ["state", "stateLabel", "stateQID", "capitalLabel", "population", "area", "state_key"]
].drop_duplicates()

wd_nodes = wd_nodes.groupby("state_key", as_index=False).agg({
    "state": first_not_null,
    "stateLabel": first_not_null,
    "stateQID": first_not_null,
    "capitalLabel": first_not_null,
    "population": first_not_null,
    "area": first_not_null
})

# =========================
# 5. Siapkan edge perbatasan dari Wikidata
# =========================
wd_edges = wd_raw[["stateLabel", "borderStateLabel"]].dropna().copy()
wd_edges["source_key"] = wd_edges["stateLabel"].apply(norm_text)
wd_edges["target_key"] = wd_edges["borderStateLabel"].apply(norm_text)

wd_edges = wd_edges[
    (wd_edges["source_key"] != "") &
    (wd_edges["target_key"] != "") &
    (wd_edges["source_key"] != wd_edges["target_key"])
].copy()

wd_edges["pair"] = wd_edges.apply(
    lambda r: tuple(sorted([r["source_key"], r["target_key"]])),
    axis=1
)
wd_edges = wd_edges.drop_duplicates("pair")

# =========================
# 6. Siapkan DBpedia
# =========================
db = db_raw[
    ["state", "stateLabel", "capitalLabel", "population", "area", "categories", "state_key"]
].drop_duplicates()

db = db.groupby("state_key", as_index=False).agg({
    "state": first_not_null,
    "stateLabel": first_not_null,
    "capitalLabel": first_not_null,
    "population": first_not_null,
    "area": first_not_null,
    "categories": combine_unique
})

db = db.rename(columns={
    "state": "state_dbpedia",
    "stateLabel": "stateLabel_dbpedia",
    "capitalLabel": "capitalLabel_dbpedia",
    "population": "population_dbpedia",
    "area": "area_dbpedia",
    "categories": "categories_dbpedia"
})

# =========================
# 7. Cek overlap
# =========================
common_keys = set(wd_nodes["state_key"]) & set(db["state_key"])
print("Overlap state keys:", len(common_keys))

# =========================
# 8. Left join
# Wikidata = utama
# DBpedia = pelengkap
# =========================
merged = wd_nodes.merge(db, on="state_key", how="left")

matched = merged["state_dbpedia"].notna().sum()
match_rate = matched / len(merged) * 100 if len(merged) > 0 else 0

print("Jumlah state Wikidata :", len(wd_nodes))
print("Jumlah state DBpedia  :", len(db))
print("Matched ke DBpedia    :", matched)
print("Match rate (%)        :", round(match_rate, 2))

# Kolom final
merged["capital_final"] = merged["capitalLabel"].fillna(merged["capitalLabel_dbpedia"])
merged["population_final"] = merged["population"].fillna(merged["population_dbpedia"])
merged["area_final"] = merged["area"].fillna(merged["area_dbpedia"])

merged["population_final"] = pd.to_numeric(merged["population_final"], errors="coerce")
merged["area_final"] = pd.to_numeric(merged["area_final"], errors="coerce")

merged.to_csv("data_processed/merged_final.csv", index=False)

# =========================
# 9. Siapkan nodes dan edges final
# =========================
valid_keys = set(merged["state_key"])
label_map = dict(zip(merged["state_key"], merged["stateLabel"]))

edges = wd_edges[
    wd_edges["source_key"].isin(valid_keys) &
    wd_edges["target_key"].isin(valid_keys)
].copy()

edges["source"] = edges["source_key"].map(label_map)
edges["target"] = edges["target_key"].map(label_map)
edges = edges[["source", "target"]].drop_duplicates()
edges.to_csv("data_processed/edges.csv", index=False)

nodes = merged[[
    "stateLabel", "stateQID", "capital_final",
    "population_final", "area_final", "categories_dbpedia"
]].copy()
nodes = nodes.rename(columns={"stateLabel": "node"})
nodes.to_csv("data_processed/nodes.csv", index=False)

print("Jumlah node final:", len(nodes))
print("Jumlah edge final:", len(edges))

# =========================
# 10. Bangun graph
# =========================
G = nx.Graph()

for _, row in merged.iterrows():
    G.add_node(
        row["stateLabel"],
        qid=row["stateQID"],
        capital=row["capital_final"],
        population=row["population_final"],
        area=row["area_final"],
        categories=row["categories_dbpedia"]
    )

for _, row in edges.iterrows():
    if row["source"] != row["target"]:
        G.add_edge(row["source"], row["target"], relation="shares_border_with")

# =========================
# 11. Centrality
# =========================
bet = nx.betweenness_centrality(G, normalized=True)
pr = nx.pagerank(G)

centrality_df = pd.DataFrame({
    "state": list(bet.keys()),
    "betweenness": [bet[n] for n in bet],
    "pagerank": [pr[n] for n in bet]
}).sort_values("betweenness", ascending=False)

centrality_df.to_csv("data_processed/centrality_result.csv", index=False)

print("\nTop 10 Betweenness")
print(centrality_df.head(10))

# =========================
# 12. Louvain Community Detection
# =========================
try:
    import community as community_louvain
    partition = community_louvain.best_partition(G)

    community_df = pd.DataFrame(
        partition.items(),
        columns=["state", "community"]
    ).sort_values(["community", "state"])

    community_df.to_csv("data_processed/community_result.csv", index=False)
    print("\nCommunity detection selesai.")
except Exception as e:
    print("\nLouvain tidak dijalankan:", e)

# =========================
# 13. Jaccard Similarity
# =========================
if len(merged) >= 4:
    merged["pop_bin"] = pd.qcut(merged["population_final"], q=4, duplicates="drop").astype(str)
    merged["area_bin"] = pd.qcut(merged["area_final"], q=4, duplicates="drop").astype(str)
else:
    merged["pop_bin"] = None
    merged["area_bin"] = None

def add_multi_feature(features, prefix, value):
    if pd.notna(value):
        for item in str(value).split(","):
            item = item.strip()
            if item:
                features.add(f"{prefix}:{item}")

state_features = {}

for _, row in merged.iterrows():
    s = row["stateLabel"]
    features = set()

    add_multi_feature(features, "capital", row.get("capital_final"))
    add_multi_feature(features, "cat", row.get("categories_dbpedia"))

    if pd.notna(row.get("pop_bin")):
        features.add(f"pop:{row['pop_bin']}")
    if pd.notna(row.get("area_bin")):
        features.add(f"area:{row['area_bin']}")

    degree_bucket = G.degree(s)
    features.add(f"degree:{degree_bucket}")

    state_features[s] = features

results = []
states = list(state_features.keys())

for s1, s2 in combinations(states, 2):
    a = state_features[s1]
    b = state_features[s2]

    if len(a.union(b)) == 0:
        sim = 0
    else:
        sim = len(a.intersection(b)) / len(a.union(b))

    if sim > 0:
        results.append([s1, s2, sim])

similarity_df = pd.DataFrame(results, columns=["state1", "state2", "jaccard"])
similarity_df = similarity_df.sort_values("jaccard", ascending=False)

similarity_df.to_csv("data_processed/similarity_result.csv", index=False)

print("\nTop 10 Jaccard Similarity")
print(similarity_df.head(10))