# Integrasi Data Negara Bagian di Amerika Serikat dari Wikidata dan DBpedia

## Ringkasan
Proyek ini mengintegrasikan data negara bagian di Amerika Serikat dari **Wikidata** sebagai sumber utama dan **DBpedia** sebagai sumber pelengkap. Data hasil integrasi kemudian direpresentasikan sebagai graf wilayah, dengan node berupa state dan edge berupa hubungan perbatasan antarstate.

## Tujuan
- Mengambil data state dari Wikidata
- Mengambil atribut pelengkap dari DBpedia
- Menggabungkan kedua sumber ke dalam satu dataset terintegrasi
- Melakukan analisis graf menggunakan centrality, community detection, dan similarity

## Sumber Data
### Wikidata (sumber utama)
Digunakan untuk:
- identitas entitas (`QID`)
- label state
- ibu kota
- populasi
- luas wilayah
- relasi state yang berbatasan

### DBpedia (sumber pelengkap)
Digunakan untuk:
- ibu kota tambahan
- populasi tambahan
- luas wilayah tambahan
- kategori deskriptif

## Query
File query tersedia di folder `queries/`:
- `queries/wikidata_query.rq`
- `queries/dbpedia_query.rq`

## Struktur Folder
```text
wikidata-dbpedia-us-states/
│
├── data_raw/
│   ├── wikidata_us_states.csv
│   └── dbpedia_us_states.csv
│
├── data_processed/
│   ├── merged_final.csv
│   ├── nodes.csv
│   ├── edges.csv
│   ├── centrality_result.csv
│   ├── community_result.csv
│   └── similarity_result.csv
│
├── queries/
│   ├── wikidata_query.rq
│   └── dbpedia_query.rq
│
├── src/
│   └── main_analysis.py
│
└── README.md
```

## Cara Menjalankan
1. Jalankan query Wikidata dan simpan hasil CSV ke `data_raw/wikidata_us_states.csv`
2. Jalankan query DBpedia dan simpan hasil CSV ke `data_raw/dbpedia_us_states.csv`
3. Jalankan script Python:

```bash
python src/main_analysis.py
```

## Hasil Utama
- Jumlah state dari Wikidata: **50**
- Jumlah state dari DBpedia: **47**
- Overlap key: **46**
- Match rate: **92.0%**
- Jumlah node graf: **50**
- Jumlah edge graf: **109**

## Temuan Utama
### Betweenness Centrality tertinggi
1. Missouri - 0.297533
2. Pennsylvania - 0.275134
3. Kentucky - 0.217696
4. New York - 0.209609
5. Tennessee - 0.200002

Interpretasi: state-state tersebut berperan sebagai penghubung struktural penting dalam jaringan perbatasan.

### Community Detection (Louvain)
Louvain menghasilkan **7 komunitas**:
- **Komunitas 0**: Iowa, Kansas, Minnesota, Missouri, Montana, Nebraska, North Dakota, South Dakota, Wyoming
- **Komunitas 1**: Alaska
- **Komunitas 2**: Hawaii
- **Komunitas 3**: Alabama, Arkansas, Florida, Georgia, Louisiana, Mississippi, North Carolina, Oklahoma, South Carolina, Tennessee, Texas
- **Komunitas 4**: Arizona, California, Colorado, Idaho, Nevada, New Mexico, Oregon, Utah, Washington
- **Komunitas 5**: Connecticut, Maine, Massachusetts, New Hampshire, New York, Rhode Island, Vermont
- **Komunitas 6**: Delaware, Illinois, Indiana, Kentucky, Maryland, Michigan, New Jersey, Ohio, Pennsylvania, Virginia, West Virginia, Wisconsin

Interpretasi: komunitas yang terbentuk sangat selaras dengan kawasan geografis besar di Amerika Serikat, seperti Great Plains, South, West, Northeast, dan Mid-Atlantic/Midwest timur.

### Jaccard Similarity tertinggi
1. Connecticut - New Hampshire (0.600000)
2. Idaho - Wyoming (0.538462)
3. Connecticut - Massachusetts (0.500000)
4. North Dakota - South Dakota (0.500000)
5. Massachusetts - New Hampshire (0.500000)

Interpretasi: pasangan-pasangan ini memiliki kemiripan atribut wilayah yang relatif tinggi.

## Output
Script akan menghasilkan file berikut di folder `data_processed/`:
- `merged_final.csv`
- `nodes.csv`
- `edges.csv`
- `centrality_result.csv`
- `community_result.csv`
- `similarity_result.csv`

## Keterbatasan
- Tidak semua state pada Wikidata memiliki padanan lengkap di DBpedia
- Sebagian nilai numerik dapat berbeda antar sumber karena perbedaan waktu pembaruan data
- Hasil similarity dipengaruhi oleh pemilihan fitur yang digunakan

## Tautan
- Halaman Wikidata: **[ISI URL HALAMAN WIKIDATA DI SINI]**
- Repository GitHub: **[ISI URL REPOSITORY GITHUB DI SINI]**
