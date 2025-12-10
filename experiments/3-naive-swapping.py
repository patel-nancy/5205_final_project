import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import *

def analyze_naive_swapping(n, utility_func, utility_name, NUM_RANDOM_SAMPLES=7_962_624):
    people = [excel_label(i) for i in range(n)]

    #TODO: should change this based on n so a gajillion rankings for n=3 aren't generated
    rankings = [generate_random_rankings(people) for _ in range(NUM_RANDOM_SAMPLES)]

    num_times_recovered = 0
    for ranking in rankings:
        profile = generate_utilities(ranking, utility_func, n)
        
        final_arr = run_naive_swapping(people, profile, utility_func, utility_name)
        
        if(final_arr != None and is_stable(profile, final_arr)):
            num_times_recovered += 1

    print("Percentage Recovered:", num_times_recovered/NUM_RANDOM_SAMPLES)

def main():
    NUM_SAMPLES = 100

    utility_functions = [
        (ranking_to_normalized_utility, "normalized"),
        (ranking_to_harmonic_utility, "harmonic"),
        (ranking_to_binary_utility, "binary")
    ]

    for n in range(3, 21):
        for utility_func, utility_name in utility_functions:
            print(f"n={n}, {utility_name}")
            analyze_naive_swapping(n, utility_func, utility_name, NUM_SAMPLES)
    

if __name__ == "__main__":
    main()