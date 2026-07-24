"""
solve_v2.py
Varian v2: pakai DosenSchedulingProblem dari template dosen, plus modifikasi output
biar 2-SKS praktikum (sks=2, type=praktek) ditampilkan di 2 slot berurutan.

Strategy:
- Pakai representasi (dosen, slot, room) dari template dosen
- Pakai fitness function dari template (DosenSchedulingProblem.getCost)
- Pakai GA sederhana (DEAP) — mirip solve_dosen.py
- Setelah GA selesai, tampilkan assignment per dosen + section khusus 2-SGS praktikum
"""

import sys
import os
import random
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from deap import base, creator, tools

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data_semester_1_3 import dosen_data, time_slots, mk_instances, mk_groups
from dosen_scheduling_v2 import DosenSchedulingProblem, analyze_solution

# ===================== KONFIGURASI =====================
RANDOM_SEED = 42
POPULATION_SIZE = 500  # tested: 1000 ga bantu (same 6.30)
MAX_GENERATIONS = 800  # tested: 1500 ga bantu (same 6.30)
P_CROSSOVER = 0.85
P_MUTATION = 0.30
ELITE_SIZE = 10
EARLY_STOP_GEN = 150  # tested: 400 ga bantu

NUM_DOSEN = len(dosen_data)
NUM_SLOTS = len(time_slots)
NUM_ROOMS = 3  # 0=RK1, 1=RK2, 2=LAB


def random_individual_v2():
    """Individu random: list of (dosen_id, slot_id, room_id). Tested: smart init malah turunkan consecutive."""
    ind = []
    for i in range(len(mk_instances)):
        mk = mk_instances[i]
        qualified_names = mk["dosen_qualified"]
        qualified_ids = []
        for d_id, d_info in dosen_data.items():
            if d_info["name"] in qualified_names:
                qualified_ids.append(d_id)
        if not qualified_ids:
            qualified_ids = list(dosen_data.keys())
        dosen = random.choice(qualified_ids)

        valid_slots = []
        target_room = "LAB" if mk["type"] == "praktek" else None
        for s in time_slots:
            if target_room is None:
                if s["room"] in ("RK1", "RK2"):
                    valid_slots.append(s["id"])
            else:
                if s["room"] == target_room:
                    valid_slots.append(s["id"])
        slot = random.choice(valid_slots) if valid_slots else random.randint(0, NUM_SLOTS - 1)

        room_name = time_slots[slot]["room"]
        room_id = DosenSchedulingProblem.ROOM_ID[room_name]
        ind.append((dosen, slot, room_id))
    return ind


def crossover_tuples_v2(ind1, ind2, indpb=0.5):
    """Crossover uniform."""
    size = len(ind1)
    for i in range(size):
        if random.random() < indpb:
            ind1[i], ind2[i] = ind2[i], ind1[i]
    return ind1, ind2


def mutate_tuples_v2(individual, indpb=0.15):
    """Mutasi: ganti dosen atau slot atau room (original)."""
    for i in range(len(individual)):
        if random.random() < indpb:
            mk = mk_instances[i]
            dosen, slot, room = individual[i]

            r = random.random()
            if r < 0.4:
                # Mutate dosen
                qualified_names = mk["dosen_qualified"]
                qualified_ids = [d_id for d_id, d_info in dosen_data.items()
                                 if d_info["name"] in qualified_names]
                if not qualified_ids:
                    qualified_ids = list(dosen_data.keys())
                new_dosen = random.choice([d for d in qualified_ids if d != dosen] or qualified_ids)
                individual[i] = (new_dosen, slot, room)
            elif r < 0.8:
                # Mutate slot
                valid_slots = []
                target_room = "LAB" if mk["type"] == "praktek" else None
                for s in time_slots:
                    if target_room is None:
                        if s["room"] in ("RK1", "RK2"):
                            valid_slots.append(s["id"])
                    else:
                        if s["room"] == target_room:
                            valid_slots.append(s["id"])
                if valid_slots:
                    new_slot = random.choice([s for s in valid_slots if s != slot] or valid_slots)
                    new_room = DosenSchedulingProblem.ROOM_ID[time_slots[new_slot]["room"]]
                    individual[i] = (dosen, new_slot, new_room)
            else:
                # Mutate room (only for teori di RK, swap RK1<->RK2)
                if mk["type"] == "teori" and room in (0, 1):
                    new_room = 1 - room
                    new_slot = None
                    for s in time_slots:
                        if s["id"] != slot and s["room"] == DosenSchedulingProblem.ROOM_NAME[new_room]:
                            new_slot = s["id"]
                            break
                    if new_slot is not None:
                        individual[i] = (dosen, new_slot, new_room)
    return individual,


def run_ga(problem, seed=RANDOM_SEED):
    """Run GA menggunakan DEAP + problem.getCost dari v2."""
    random.seed(seed)
    np.random.seed(seed)

    if not hasattr(creator, "FitMin"):
        creator.create("FitMin", base.Fitness, weights=(-1.0,))
    if not hasattr(creator, "Individual"):
        creator.create("Individual", list, fitness=creator.FitMin)

    toolbox = base.Toolbox()
    toolbox.register("individual", tools.initIterate, creator.Individual, random_individual_v2)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("evaluate", problem.getCost)
    toolbox.register("mate", crossover_tuples_v2, indpb=0.5)
    toolbox.register("mutate", mutate_tuples_v2, indpb=0.15)
    toolbox.register("select", tools.selTournament, tournsize=3)

    pop = toolbox.population(n=POPULATION_SIZE)
    fitnesses = list(map(toolbox.evaluate, pop))
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = (fit,)

    hof = tools.HallOfFame(1, similar=np.array_equal)
    hof.update(pop)
    best_cost_history = [hof.items[0].fitness.values[0]]

    stats = tools.Statistics(lambda ind: ind.fitness.values[0])
    stats.register("avg", lambda fits: sum(fits) / len(fits))
    stats.register("min", lambda fits: min(fits))
    stats.register("max", lambda fits: max(fits))

    rec = stats.compile(pop)
    avg_cost_history = [rec["avg"]]

    no_improve = 0
    for gen in range(1, MAX_GENERATIONS + 1):
        offspring = list(map(toolbox.clone, toolbox.select(pop, len(pop) - ELITE_SIZE)))
        elite = list(map(toolbox.clone, tools.selBest(pop, ELITE_SIZE)))
        for c1, c2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < P_CROSSOVER:
                toolbox.mate(c1, c2)
                del c1.fitness.values, c2.fitness.values
        for mutant in offspring:
            if random.random() < P_MUTATION:
                toolbox.mutate(mutant)
                del mutant.fitness.values
        invalid = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = list(map(toolbox.evaluate, invalid))
        for ind, fit in zip(invalid, fitnesses):
            ind.fitness.values = (fit,)
        pop[:] = elite + offspring
        prev_best = hof.items[0].fitness.values[0] if hof.items else float("inf")
        hof.update(pop)
        new_best = hof.items[0].fitness.values[0]
        best_cost_history.append(new_best)
        rec = stats.compile(pop)
        avg_cost_history.append(rec["avg"])
        if gen % 50 == 0 or gen == 1:
            print(f"  gen={gen:>4}  min={new_best:>7.3f}  avg={rec['avg']:>7.3f}  max={rec['max']:>7.3f}")
        if new_best < prev_best - 1e-6:
            no_improve = 0
        else:
            no_improve += 1
        if no_improve >= EARLY_STOP_GEN and gen > 200:
            print(f"  [Early stop at gen {gen}, no improvement for {EARLY_STOP_GEN} gens]")
            break

    return hof.items[0], best_cost_history, avg_cost_history


def print_dual_slot_praktikum(best):
    """
    Cari 2-SKS praktikum (sks=2, type=praktek) yang punya 2 slot berurutan.
    Tampilkan dalam section khusus.
    """
    print("\n" + "=" * 90)
    print("2-SKS PRAKTIKUM (each occupies 2 slots)")
    print("=" * 90)

    # Cari 2-SKS praktikum
    dual_slot_mks = [(i, mk) for i, mk in enumerate(mk_instances)
                     if mk["sks"] == 2 and mk["type"] == "praktek"]

    if not dual_slot_mks:
        print("  (No 2-SKS praktikum in dataset)")
        return

    print(f"\n  Total 2-SKS praktikum: {len(dual_slot_mks)}")
    print(f"  {'='*80}\n")

    # Cek mana yg slot-nya consecutive dengan praktek lain di slot+1
    found_any_consecutive = False
    for i, mk in dual_slot_mks:
        dosen, slot, room = best[i]
        slot_info = time_slots[slot]
        next_slot_id = slot + 1

        # Cek apakah slot+1 ada, sama hari, sama room, dan dipakai praktek lain
        consecutive_partner = None
        if next_slot_id < NUM_SLOTS:
            next_slot_info = time_slots[next_slot_id]
            if (next_slot_info["hari"] == slot_info["hari"] and
                next_slot_info["room"] == slot_info["room"]):
                # Cari MK di slot+1
                for j, other_mk in enumerate(mk_instances):
                    if j == i:
                        continue
                    if other_mk["type"] == "praktek":
                        if best[j][1] == next_slot_id:
                            consecutive_partner = (j, other_mk)
                            break

        dosen_name = dosen_data[dosen]["name"]
        room_name = DosenSchedulingProblem.ROOM_NAME[room]
        print(f"  [{i}] {mk['name']} ({mk['kelas']}{mk['semester']}) - {dosen_name} - {mk['sks']} SKS")
        print(f"      Slot 1: {slot_info['hari']} {slot_info['jam']} @ {room_name}")
        if consecutive_partner:
            j, partner_mk = consecutive_partner
            partner_slot = time_slots[best[j][1]]
            partner_room = DosenSchedulingProblem.ROOM_NAME[best[j][2]]
            partner_dosen = dosen_data[best[j][0]]["name"]
            print(f"      Slot 2: {partner_slot['hari']} {partner_slot['jam']} @ {partner_room} ({partner_dosen}: {partner_mk['name']})")
            print(f"      ✅ CONSECUTIVE PAIR (2 slots, same day & room)")
            found_any_consecutive = True
        else:
            print(f"      Slot 2: (no consecutive partner found)")
            print(f"      ⚠️  Not in 2 consecutive slots")
        print()

    if not found_any_consecutive:
        print("  ⚠️  Tidak ada 2-SKS praktikum yang berada di 2 slot berurutan.")
        print("  💡 S2 soft constraint dari template belum cukup kuat untuk enforce ini.")
        print("     Bisa ditambah penalty lebih besar untuk memaksa consecutive slots.")


def save_plot(best_history, avg_history, filename="plot_konvergensi.jpg"):
    """Simpan plot konvergensi."""
    plt.figure(figsize=(10, 6))
    plt.plot(best_history, label="Best Fitness", color="blue", linewidth=2)
    plt.plot(avg_history, label="Average Fitness", color="red", linestyle="--", linewidth=1.5, alpha=0.7)
    plt.xlabel("Generation")
    plt.ylabel("Cost (lower = better)")
    plt.title(f"GA Convergence (Dosen Scheduling v2) - Best: {best_history[-1]:.3f}")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(filename, dpi=100, format="jpg")
    print(f"\n📊 Plot saved to: {filename}")
    plt.close()  # Tutup figure biar ga numpuk memory


def main():
    print("=" * 90)
    print("DOSEN SCHEDULING v2 - GENETIC ALGORITHM (Template Dosen + Custom GA)")
    print("=" * 90)
    print(f"\nProblem Size:")
    print(f"  - MK Instances: {len(mk_instances)}")
    print(f"  - Dosen: {NUM_DOSEN}")
    print(f"  - Time Slots: {NUM_SLOTS}")
    print(f"  - Population Size: {POPULATION_SIZE}")
    print(f"  - Generations: {MAX_GENERATIONS}")
    print(f"  - Random Seed: {RANDOM_SEED}\n")

    problem = DosenSchedulingProblem(mk_instances, dosen_data, time_slots, mk_groups)

    print("Running GA (v2 fitness)...")
    print("-" * 90)
    print(f"{'gen':>6}  {'min':>8}  {'avg':>8}  {'max':>8}")

    best, best_history, avg_history = run_ga(problem)

    print("-" * 90)
    print(f"\n✅ GA Finished! Best cost: {best.fitness.values[0]:.3f}\n")

    # Pakai analyze_solution dari template v2
    analyze_solution(best, mk_instances, dosen_data, time_slots, mk_groups)

    # Section tambahan: 2-SKS praktikum di 2 slot
    print_dual_slot_praktikum(best)

    # Generate plot
    save_plot(best_history, avg_history)

    return best


if __name__ == "__main__":
    main()
