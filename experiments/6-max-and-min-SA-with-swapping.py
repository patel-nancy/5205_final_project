import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import *
from multiprocessing import Pool, cpu_count

def analyze_simulated_annealing_max_min_swappping_blocking_pairs(n, utility_func, utility_name, NUM_RANDOM_SAMPLES=7_962_624, debug=False):
    NUM_PARALLEL_RUNS = 10 # PARALLELIZED
    MAX_N_TO_BRUTE_FORCE_CHECK = 12

    people = [excel_label(i) for i in range(n)]
    rankings = [generate_random_rankings(people) for _ in range(NUM_RANDOM_SAMPLES)]

    #metrics
    num_times_recovered = 0
    num_times_not_recovered_but_stable_solution = 0
    num_times_not_recovered_bc_no_stable_solution = 0

    num_times_found_after_initial_SA = 0
    num_times_found_after_initial_swapping_pairs = 0
    num_times_found_after_second_SA = 0
    num_times_found_after_second_swapping_pairs = 0

    for ranking in rankings:
        profile = generate_utilities(ranking, utility_func, n)

        num_stable = 0

        final_nonstable_arrangments = {}

        #parallelize 10 SA runs -- looking for global MAX
        sa_args = [(n, people, profile, utility_func, utility_name, True) for _ in range(NUM_PARALLEL_RUNS)]
        with Pool(processes=min(NUM_PARALLEL_RUNS, cpu_count())) as pool:
            final_arrangements = pool.map(run_single_sa, sa_args)

        #check results from (MAX) SA runs
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
                #try 2: MIN SA + swapping pairs
                final_nonstable_arrangments = {}

                #parallelize 10 SA runs -- looking for global MIN
                sa_args = [(n, people, profile, utility_func, utility_name, False) for _ in range(NUM_PARALLEL_RUNS)]
                with Pool(processes=min(NUM_PARALLEL_RUNS, cpu_count())) as pool:
                    final_arrangements = pool.map(run_single_sa, sa_args)

                #check results from (MIN) SA runs
                for final_arr in final_arrangements:
                    blocking_pair = find_blocking_pair(profile, final_arr)

                    #found stable arrangement
                    if(blocking_pair == None):
                        num_stable += 1
                        num_times_found_after_second_SA += 1
                        break
                    else:
                        final_nonstable_arrangments[final_arr] = blocking_pair

                #if none of the min welfare arrangements are stable,
                #then try swapping blocking pairs and see if we can find a stable pair "nearby"
                if(num_stable == 0):
                    for final_arr, blocking_pair in final_nonstable_arrangments.items():
                        final = run_swap_blocking_pairs(profile, final_arr, blocking_pair)
                        if(final != None):
                            num_stable += 1
                            num_times_found_after_second_swapping_pairs += 1
                            break 
                    
                    #after swapping blocking pairs (on global minima), did not find a stable arrangement
                    if(num_stable == 0):
                        if(debug):
                            print("No stable arrangement found after both rounds of SA + blocking pairs.")
                        
                        #check all arrangements to see if a stable one exists
                        #only do so if there's less than a trillion arrangements
                        if(n < MAX_N_TO_BRUTE_FORCE_CHECK):
                            if(does_stable_arr_exist_for_profile(people, profile)):
                                num_times_not_recovered_but_stable_solution += 1

                            else:
                                num_times_not_recovered_bc_no_stable_solution += 1
                    
                    #after second swapping blocking pairs (on global minima), found a stable arrangement
                    else:
                        if(debug):
                            print("Found a stable arrangement after second (MIN) swapping blocking pairs.")
                        num_times_recovered += 1
                
                #after second (MIN) SA, found stable arrangement
                else:
                    if(debug):
                        print("Found a stable arrangement after second SA. Min welfare arrangement is stable.")
                    num_times_recovered += 1

            #after initial swapping blocking pairs (on global maxima), found a stable arrangement
            else:
                if(debug):
                    print("Found a stable arrangement after initial (MAX) swapping blocking pairs.")
                num_times_recovered += 1
        
        #after initial (MAX) SA, found stable arrangmeent 
        else:
            if(debug):
                print("Found a stable arrangement after initial (MAX) SA. Max welfare arrangement is stable.")

    print("Percentage Recovered:", num_times_recovered/NUM_RANDOM_SAMPLES)
    #how many recovered arrangements were from SA versus SA + swapping
    if(num_times_recovered > 0):
        print("Percentage of Recovered Found After Initial SA:", num_times_found_after_initial_SA/num_times_recovered)
        print("Percentage of Recovered Found After Initial (Maxima) Swapping Blocking Pairs:", num_times_found_after_swapping_pairs/num_times_recovered)
        print("Percentage of Recovered Found After Second SA:", num_times_found_after_second_SA/num_times_recovered)
        print("Percentage of Recovered Found After Second (Minima) Swapping Blocking Pairs:", num_times_found_after_second_swapping_pairs/num_times_recovered)

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

    for n in range(20, 27):
        print("="*80)
        print(f"n={n}")
        print("\n")

        for utility_func, utility_name in utility_functions:
            print(f"{utility_name}")
            analyze_simulated_annealing_max_min_swapping_blocking_pairs_accuracy(n, utility_func, utility_name, NUM_SAMPLES)
            print("-"*80)
        
        print("="*80)

if __name__ == "__main__":
    main()