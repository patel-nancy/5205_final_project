import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import *

def analyze_naive_sit_as_you_come(n, utility_func, utility_name, NUM_RANDOM_SAMPLES=7_962_624):
    people = [excel_label(i) for i in range(n)]
   
    rankings = [generate_random_rankings(people) for _ in range(NUM_RANDOM_SAMPLES)]

    num_times_recovered = 0
    for ranking in rankings:
        profile = generate_utilities(ranking, utility_func, n)

        final_arr = run_naive_sit_as_you_come(n, people, ranking, utility_func)

        if(is_stable(profile, final_arr)):
            num_times_recovered += 1
    
    print("Percentage Recovered:", num_times_recovered/NUM_RANDOM_SAMPLES)

def main():
    random.seed(GLOBAL_SEED)
    
    NUM_SAMPLES = 100

    utility_functions = [
        (ranking_to_normalized_negative_utility, "negative normalized"),
        (ranking_to_binary_negative_utility, "negative binary"),
        (ranking_to_skewed_utility, "skewed at n/3")
    ]

    for n in range(3, 21):
        for utility_func, utility_name in utility_functions:
            print(f"n={n}, {utility_name}")
            analyze_naive_sit_as_you_come(n, utility_func, utility_name, NUM_SAMPLES)

if __name__ == "__main__":
  main()