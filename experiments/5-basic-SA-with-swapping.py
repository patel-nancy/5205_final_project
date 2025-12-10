import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import *
from multiprocessing import Pool, cpu_count

def analyze_simulated_annealing_swapping_blocking_pairs_accuracy(n, utility_func, utility_name, NUM_RANDOM_SAMPLES=7_962_624, debug=False):
  NUM_PARALLEL_RUNS = 10 
  MAX_N_TO_BRUTE_FORCE_CHECK = 12

  people = [excel_label(i) for i in range(n)]
  rankings = [generate_random_rankings(people) for _ in range(NUM_RANDOM_SAMPLES)]

  #metrics
  num_times_recovered = 0
  num_times_not_recovered_but_stable_solution = 0
  num_times_not_recovered_bc_no_stable_solution = 0

  num_times_found_after_initial_SA = 0
  num_times_found_after_swapping_pairs = 0

  for ranking in rankings:
    profile = generate_utilities(ranking, utility_func, n)

    num_stable = 0

    final_nonstable_arrangments = {}

    #parallelize 10 SA runs
    sa_args = [(n, people, profile, utility_func, utility_name, True) for _ in range(NUM_PARALLEL_RUNS)]
    with Pool(processes=min(NUM_PARALLEL_RUNS, cpu_count())) as pool:
      final_arrangements = pool.map(run_single_sa, sa_args)

    #check results from SA runs
    for final_arr in final_arrangements:
      blocking_pair = find_blocking_pair(profile, final_arr)

      #found stable arrangement
      if(blocking_pair == None):
        num_stable += 1
        num_times_found_after_initial_SA += 1
        break
      else:
        final_nonstable_arrangments[final_arr] = blocking_pair

    #if none of the max welfare arrangements are stable, 
    #then try swapping blocking pairs and see if we can find a stable pair "nearby"
    if(num_stable == 0):
      for final_arr, blocking_pair in final_nonstable_arrangments.items():
        final = run_swap_blocking_pairs(profile, final_arr, blocking_pair)
        if(final != None):
          num_stable += 1
          num_times_found_after_swapping_pairs += 1
          break

      #after swapping blocking pairs, did not find a stable arrangement
      if(num_stable == 0):
        if(debug):
          print("No stable arrangement found after SA + blocking pairs.")

        #check all arrangements to see if a stable one exists
        #only do so if there's less than a trillion arrangements
        if(n < MAX_N_TO_BRUTE_FORCE_CHECK):
          if(does_stable_arr_exist_for_profile(people, profile)):
            num_times_not_recovered_but_stable_solution += 1

          else:
            num_times_not_recovered_bc_no_stable_solution += 1

      #after swapping blocking pairs, found a stable arrangement
      else:
        if(debug):
          print("Found a stable arrangement after initial swapping blocking pairs.")
        num_times_recovered += 1

    #recovered stable match from simply running SA
    else:
      if(debug):
          print("Found a stable arrangement after initial SA. Max welfare arrangement is stable.")
      num_times_recovered += 1

  print("Percentage Recovered:", num_times_recovered/NUM_RANDOM_SAMPLES)
  if(num_times_recovered > 0):
    print("Percentage of Recovered Found After Initial SA:", num_times_found_after_initial_SA/num_times_recovered)
    print("Percentage of Recovered Found After Swapping Blocking Pairs:", num_times_found_after_swapping_pairs/num_times_recovered)

  if(n < MAX_N_TO_BRUTE_FORCE_CHECK):
    print("Percentage Not Recovered (No Stable Solution Exists):", num_times_not_recovered_bc_no_stable_solution/NUM_RANDOM_SAMPLES)
    print("Percentage Not Recovered (Stable Solution Exists):", num_times_not_recovered_but_stable_solution/NUM_RANDOM_SAMPLES)

def main():
    #TODO: format!
    
    NUM_SAMPLES = 100
  
    utility_functions = [
        (ranking_to_normalized_utility, "normalized"),
        (ranking_to_harmonic_utility, "harmonic"),
        (ranking_to_binary_utility, "binary")
    ]

    for n in range(3, 21):
        for utility_func, utility_name in utility_functions:
            print(f"n={n}, {utility_name}")
            analyze_simulated_annealing_swapping_blocking_pairs_accuracy(n, utility_func, utility_name, NUM_SAMPLES)

if __name__ == "__main__":
    main()