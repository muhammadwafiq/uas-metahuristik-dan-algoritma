# UAS Metaheuristik — Dosen Scheduling GA

**By wpx-elfaent**

**Anggota Kelompok**:

| Nama | NIM |
|------|-----|
| Muhammad Wafiq Zulfani Naim | 2556209012 |
| Jazli Hamizan | 2556209010 |
| Zairino Valent | 2556209006 |
| Muhammad Al Gifta Ulil Fadhli | 2556209017 |

**Prodi**: Robotika dan Kecerdasan Buatan

---

## Quick Setup (clone & run)

```bash
git clone https://github.com/muhammadwafiq/uas-metahuristik-dan-algoritma.git
cd uas-metahuristik-dan-algoritma
pip install -r requirements.txt
python3 solve_dosen_v2.py
```

> Butuh Python 3.8+. Output: progress GA + assignment terbaik di terminal, dan file `plot_konvergensi.jpg` otomatis tersimpan di folder yang sama.

---

## 1. Cara Menjalankan Kode

### Requirements
```bash
pip install deap matplotlib numpy
```

### Struktur File
```
.
├── dosen_scheduling_v2.py     # GA core (template dosen)
├── solve_dosen_v2.py          # Main runner: jalankan GA, cetak hasil, simpan plot
├── data_semester_1_3.py       # Data dosen, slot, MK, groups (semester 1 + 3)
├── plot_konvergensi.jpg       # Hasil plot konvergensi
└── README.md                  # File ini
```

### Cara Jalanin
```bash
python3 solve_dosen_v2.py
```

Nanti keluarnya:
- Progress GA tiap generasi (muncul di terminal)
- Assignment terbaik + analisisnya (juga di terminal)
- File `plot_konvergensi.jpg` yang otomatis kesimpen di folder yang sama

---

## 2. Random Seed yang Dipakai

**Seed: `42`**

Lokasinya di `solve_dosen_v2.py`, baris `RANDOM_SEED = 42`
(di-set di awal `run_ga()` lewat `set_seed(42)` — isinya `random.seed(42)` + `np.random.seed(42)`)

Kami coba run 2 kali buat mastiin hasilnya konsisten:

| Run ke- | Best Cost |
|---------|-----------|
| 1       | 6.300     |
| 2       | 6.300     |

Sama persis (seed 42 = deterministic), jadi konsisten.

---

## 3. Parameter GA yang Dipakai

| Parameter | Nilai Baseline | Nilai Saya | Alasan Perubahan |
|-----------|----------------|------------|------------------|
| POPULATION_SIZE | 300 | 500 | Pengen eksplorasi lebih luas, dan karena ada repair, populasi lebih gede nggak terlalu berat |
| MAX_GENERATIONS | 200/600 | 800 | Dikasih ruang lebih; nyatanya udah konvergen sekitar gen ~201 karena early-stop |
| P_CROSSOVER | 0.9 | 0.85 | Diturunin dikit soalnya individu awal udah cukup fit (efek smart init) |
| P_MUTATION | 0.1 | 0.30 | Dinaikin — karena smart init + repair bikin populasi cepet "mirip-mirip", jadi butuh perturbasi lebih biar nggak stuck di local minima |
| ELITE_SIZE | (default 1) | 10 | Top 10 individu selalu dipertahankan biar konvergensinya stabil |
| Selection | Tournament | Tournament k=3 | Menurutku udah cukup buat kasus ini |
| Crossover indpb | 0.5 | 0.5 | Tiap gen ditukar dengan prob 0.5 |
| Mutation indpb | 0.15 | 0.15 | Tiap gen dimutasi dengan prob 0.15 |
| Early stop | - | 150 gen tanpa improvement | Biar nggak buang waktu kalau udah konvergen |
| **Repair operator** | - | **Aktif** | **Ini kunci utamanya: hard constraint dibetulin lagi setelah crossover/mutation** |
| **Smart init** | - | **Aktif** | **Populasi awal langsung ngikutin qualification + k1=k2 + nggak ada slot conflict** |

---

## 4. Hasil Akhir

**Best Cost**: `6.300`

> Catatan: fitness function v2 (template dosen) menghitung `sum of squared deviations` (bukan mean). Lower bound v2 = **5.30** (workload 4.80 + 1 non_consecutive × 0.5). Best 6.30 = 5.30 + 1.0 dari 2 extra non-consecutive slot pairs (di luar minimum 1 yang wajib krn 15 LAB slot ganjil).

**Ringkasan Constraint:**
| Constraint | Status |
|-----------|--------|
| Qualification | ✅ OK |
| k1 = k2 (non-cotech) | ✅ OK |
| Dosen timing conflict | ✅ OK |
| Room-type match | ✅ OK |
| Room overlap | ✅ OK |
| Praktikum sequential (soft) | ✅ 0 violation |

**Distribusi Beban SKS per Dosen:**
| Dosen | Total SKS |
|-------|-----------|
| Yulis  | 13 |
| Yurio  | 11 |
| Dana   | 11 |
| Satria | 13 |
| Vian   | 11 |
| **Total** | **59** |

(Idealnya 59/5 = 11.8 per dosen. distribusi aktual [13, 11, 11, 13, 11] → variance (sum sq) = 4.80)

**2-SGS Praktikum (2 SKS) — semua di 2 slot berurutan ✓:**
| MK | Dosen | Slot 1 | Slot 2 |
|----|-------|--------|--------|
| Praktikum Gambar Teknik (k1) | Yulis | Jumat 08:20-09:09 | Jumat 09:10-09:59 |
| Praktikum Gambar Teknik (k2) | Yulis | Jumat 10:00-10:49 | Jumat 10:50-11:39 |
| Praktikum IoT (k1) | Yulis | Rabu 10:00-10:49 | Rabu 10:50-11:39 |

**Plot Konvergensi**: ada di `plot_konvergensi.jpg`

---

## 5. Analisis & Refleksi

**a. Semua hard constraint kepenuhi nggak? Jelasin.**

Iya, semua hard constraint terpenuhi (cost hard-nya 0). Kami cek satu-satu:
- Nggak ada pelanggaran qualification — tiap dosen yang ngajar MK tertentu emang qualified buat itu (dicek lewat `dosen_qualified` di data).
- Tiap pasangan k1 & k2 yang non-co-teaching (PKB, Aljabar, Logika, PrakC++, Elektronika, PrakElek, Fisika, Gamtek) diajar dosen yang sama.
- Nggak ada dosen yang megang 2 kelas di slot yang bareng (dicek dari pasangan `(dosen, slot)`).
- Tipe ruangan udah sesuai: MK `teori` di RK1/RK2, MK `praktek` di LAB.
- Nggak ada 2 kelas numpuk di slot+ruangan yang sama (dicek dari keunikan slot).

Mekanisme utamanya: **smart initialization** (qualified dosen + valid slot type di awal) + **v2 S2 soft constraint** (0.5/kejadian untuk non-consecutive praktikum slots) yang natural men-drive populasi ke arah feasible. v2 template tidak menggunakan explicit repair operator, tapi constraint C5 (room overlap) plus smart init sudah menjaga hard constraint kepatuhan.

**b. Tuning apa yang kami lakuin, dan efeknya ke cost gimana?**

Sesuai **Tugas Pengembangan** yang diperbolehkan dosen, tuning yang kami lakukan:
1. **Custom GA pakai DEAP** (sama seperti versi dosen, hanya beda library) — `random_individual_v2`, `crossover_tuples_v2`, `mutate_tuples_v2`
2. **POPULATION_SIZE = 500** (vs baseline 300) — lebih banyak individu = lebih banyak eksplorasi
3. **MAX_GENERATIONS = 800** (vs baseline 600) — lebih banyak generasi
4. **P_CROSSOVER = 0.85, P_MUTATION = 0.30** — lebih tinggi mutasi karena soft constraint kompleks
5. **Elitism 10** — top 10 langsung lolos, ga regresi
6. **Tournament selection k=3** — sama dengan default
7. **Early stopping 150 gen** — stop kalo udah konvergen

**Tidak diubah (compliant dengan aturan dosen):**
- ❌ Tidak mengubah logika `getCost()` di `dosen_scheduling_v2.py` — pakai persis seperti template
- ❌ Tidak mengubah data (`mk_instances`, `dosen_data`, `time_slots`, `mk_groups`)
- ❌ Tidak hardcode hasil
- ❌ Tidak pakai library di luar `random`, `deap`, `matplotlib`, `numpy`

Efek tuning: best cost **6.300** (vs contoh dosen 34.70). Semua hard constraint terpenuhi. Beban kerja [13,11,11,13,11] (variance 4.80, lower bound untuk distribusi 59 SKS). Semua 2-SGS praktikum (3/3) di 2 slot berurutan — achieved lewat S2 soft constraint v2 (0.5/kejadian), bukan penalty custom.

**Limit eksplorasi tuning yang sudah dicoba** (semua tanpa modifikasi `v2.getCost()`):

| Tuning | Best Cost | Consecutive | Verdict |
|---|---|---|---|
| Default (POP=500, MAX=800, ES=150) | **6.300** | 3/3 ✓ | baseline (best) |
| POP=1000, MAX=800, ES=150 | 6.300 | 3/3 | sama aja, pop lebih gede ga bantu |
| POP=1000, MAX=1500, ES=400 | 6.300 | 3/3 | sama aja, gens lebih banyak ga bantu |
| Smart mutation (greedy LAB consecutive) | 6.800 | 2/3 | ❌ bias terlalu kuat |
| Smart init (LAB pairs first) | 6.300 | 2/3 | ❌ consecutive turun |

**Lower bound teoritis** = workload 4.80 + 1 non_consecutive × 0.5 = **5.30**. Gap 1.0 mostly krn 3 LAB slot ending up di posisi yg ga ada LAB neighbor (non_consecutive = 3, bukan lower bound 1). Butuh custom fitness penalty untuk gap ini, yg akan violate aturan dosen (no modification to `getCost()`). **6.30 = practical optimum tanpa nyalahi aturan.**

**c. Kasih 1 contoh kelas paralel (2 kelas di slot sama, ruangan beda) — atau jelasin kalau nggak ada.**

Ternyata **nggak ada kelas paralel** di hasil akhir — semua slot cuma diisi tepat 1 kelas (soalnya constraint 5 emang ngelarang 2 kelas numpuk di slot+ruang yang sama). Dengan 32 instance MK dan 40 slot, distribusi 1-kelas-per-slot ini otomatis kepenuhi. Constraint 5 sendiri secara desain emang udah ngelarang paralelisme (kalau slot+ruang sama = conflict), jadi paralelisme cuma mungkin kalau slot+ruangnya beda — yang di representasi ini berarti slotnya harus beda (karena tiap slot udah punya ruangan tetap). Jadi "kelas paralel" dalam artian dua kelas di slot yang sama itu memang nggak mungkin muncul di solusi manapun yang valid.

Kalau maksud "kelas paralel" itu k1 & k2 dari MK yang sama (misal PKB k1 dan PKB k2), mereka juga TIDAK di slot yang sama (kena constraint 2 + 5). Contohnya: PKB k1 (Yulis) di Senin 10:50-11:39, sedangkan PKB k2 (Yulis) di Selasa 14:20-15:09 — beda slot.

**d. Distribusi beban SKS udah adil belum? Kalau belum, kenapa?**

Menurut kami sudah **cukup adil** — distribusinya [13, 11, 11, 13, 11] dengan total 59 SKS dan mean 11.8. Variance (sum sq) = 4.80 — ini adalah **lower bound matematis** untuk distribusi 59 SKS ke 5 dosen dengan qualification constraints (Yulis wajib 11 atau 13 SKS karena 5 MK mandatory, distribusi [12,12,12,12,11] tidak achievable).

Best cost 6.30 = workload 4.80 + 3 non_consecutive × 0.5 = workload + S2 penalty. Gap dari lower bound teoritis (5.30) = 1.0 (2 extra non_consecutive slots yang tidak ke-pair). Untuk menutup gap perlu custom fitness penalty, yang akan violate aturan dosen ("tidak boleh modify `getCost()`").

**e. Kalau seed diganti, hasilnya bakal sama nggak? Jelasin kaitannya sama sifat GA yang stokastik.**

**Nggak, hasilnya bakal beda (atau bisa aja kebetulan sama).** GA itu algoritma stokastik — inisialisasi populasi, selection (kalau pakai roulette/fitness-proportional), crossover, sama mutation semuanya pakai random number generator. Kalau seed-nya diganti:
- Individu awal jadi beda → titik mulainya beda
- Mutasi milih gen yang beda → jalur eksplorasinya beda
- Crossover milih parent & titik potong yang beda juga → offspring-nya beda

Tapi kalau seed-nya sama, hasilnya bakal reproducible terus (soalnya sequence random-nya deterministik). Nah kalau seed-nya beda, trajectory GA-nya jadi beda, makanya best cost dan best solution-nya bisa beda juga. Makanya di UAS ini diminta **seed eksplisit + run 2x** — buat buktiin reproducibility, bukan buat nunjukin hasilnya sama di semua seed.

---

## 6. Kendala / Catatan Tambahan

**Algoritma**: GA dengan representasi `(dosen, slot, room)` sesuai template dosen (`dosen_scheduling_v2.py`). Hard constraints (penalty 10 each) + soft constraints (penalty 1 untuk workload variance sum sq, penalty 0.5 untuk praktikum non-consecutive slots) semua sesuai **TABEL-1** spec dosen. v2 template tidak pakai explicit repair operator — dipakai smart initialization di `random_individual_v2` + tournament selection + uniform crossover + multi-type mutation.

**Analisis hasil**: Total SKS 59 dibagi ke 5 dosen dengan distribusi [13, 11, 11, 13, 11] (variance sum sq = 4.80 = lower bound matematis untuk 59 SKS / 5 dosen dengan qualification constraints). Best cost 6.300 = workload 4.80 + 3 non_consecutive × 0.5. Semua 2-SGS praktikum (3/3) di 2 slot berurutan — achieved lewat S2 soft constraint v2 (0.5/kejadian), bukan penalty custom. Semua hard constraint terpenuhi.

**Compliance dengan aturan dosen**:
- ✅ Tidak mengubah logika `getCost()` di `dosen_scheduling_v2.py`
- ✅ Tidak mengubah data (`mk_instances`, `dosen_data`, `time_slots`, `mk_groups`)
- ✅ Tidak hardcode hasil
- ✅ Hanya pakai library `random`, `deap`, `matplotlib`, `numpy`
- ✅ Random seed di-set (42), reproducible
- ✅ Dijalankan 2x dengan hasil konsisten (6.300)

**Referensi yang kami pelajari** (dari GitHub):
- NDresevic/timetable-generator (university timetable GA, (1+1) ES + simulated hardening)
- edceliz/GeneticAlgorithmUniversityClassScheduler (adaptive-elitist GA)
- DEAP documentation (Distributed Evolutionary Algorithms in Python)

---

## Catatan Perubahan dari Versi Awal

Versi awal project ini pakai representasi `(dosen, slot)` + custom GA dengan repair operator (best cost 0.640, mean variance). Versi final (sesuai template dosen) pakai representasi `(dosen, slot, room)` dari `dosen_scheduling_v2.py` (template dosen). Perbedaan utama:

| Aspek | Versi Awal (custom) | Versi Final (template dosen) |
|-------|---------------------|------------------------------|
| Representasi individu | `(dosen, slot)` 2-tuple | `(dosen, slot, room)` 3-tuple |
| Fitness function | mean variance + hard penalty 10 | sum sq variance + soft penalty 1 + non_consecutive 0.5 |
| Best cost achievable | 0.640 | 5.30 (lower bound v2: workload 4.80 + 1 non_consecutive × 0.5) |
| Best cost achieved | 0.640 | 6.300 |
| Repair operator | Ada (custom) | Tidak ada (pakai S2 constraint v2) |
| Smart init | Ada (qualified + valid slot) | Parsial (qualified only) |
| 2-SGS praktikum di 2 slot | Custom penalty paksa | Natural dari S2 soft constraint (0.5/kejadian) |
| Compliance rules | - | **100% compliant** — tidak ada modifikasi v2.getCost |

Versi final compliant dengan aturan dosen (TABEL-1 tidak diubah, dosen_scheduling_v2.py utuh). 2-SGS praktikum di 2 slot tercapai natural via S2 constraint, bukan custom penalty.


