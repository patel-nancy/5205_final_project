import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import *
from multiprocessing import Pool, cpu_count

def analyze_simulated_annealing_accuracy(n, utility_func, utility_name, NUM_RANDOM_SAMPLES=7_962_624, findMax=True):
  NUM_PARALLEL_RUNS = 10 

  people = [excel_label(i) for i in range(n)]
  rankings = [generate_random_rankings(people) for _ in range(NUM_RANDOM_SAMPLES)]

  #metrics
  num_times_recovered = 0
  num_times_not_recovered_bc_no_stable_solution = 0
  num_times_not_recovered_but_stable_solution = 0

  for ranking in rankings:
    profile = generate_utilities(ranking, utility_func, n)

    num_stable = 0

    #parallelize 10 SA runs
    sa_args = [(n, people, profile, utility_func, utility_name, findMax) for _ in range(NUM_PARALLEL_RUNS)]
    with Pool(processes=min(NUM_PARALLEL_RUNS, cpu_count())) as pool:
      final_arrangements = pool.map(run_single_sa, sa_args)

    #check results from SA runs
    for final_arrangement in final_arrangements:
      #found a stable arrangement
      if(is_stable(profile, final_arrangement)):
        num_stable += 1
        break

    if(num_stable == 0):
      #see if a stable matching exists, for such a profile
      if(does_stable_arr_exist_for_profile(people, profile)):
        num_times_not_recovered_but_stable_solution += 1

      else:
        num_times_not_recovered_bc_no_stable_solution += 1
    else:
      num_times_recovered += 1

  print("Percentage Recovered:", num_times_recovered/NUM_RANDOM_SAMPLES)
  print("Percentage Not Recovered (No Stable Solution Exists):", num_times_not_recovered_bc_no_stable_solution/NUM_RANDOM_SAMPLES)
  print("Percentage Not Recovered (Stable Solution Exists):", num_times_not_recovered_but_stable_solution/NUM_RANDOM_SAMPLES)

def main():
    # #TODO: format!

    NUM_SAMPLES = 100

    utility_functions = [
      (ranking_to_normalized_utility, "normalized"),
      (ranking_to_harmonic_utility, "harmonic"),
      (ranking_to_binary_utility, "binary")
    ]


    for n in range(4, 10):
      print("="*80)
      print(f"n={n}")
      print("\n")

      for utility_func, utility_name in utility_functions:
          print(f"{utility_name}")
          analyze_simulated_annealing_accuracy(n, utility_func, utility_name, NUM_SAMPLES)
          print("-"*80)

      print("="*80)

if __name__ == "__main__":
  main()