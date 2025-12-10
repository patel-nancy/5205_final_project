import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import *
from multiprocessing import Pool, cpu_count
from functools import partial

def process_single_ranking(ranking, arrangements, utility_func, n):
  """Process a single ranking and return whether any welfare-maximizing arrangement is stable."""
  profile = generate_utilities(ranking, utility_func, n)

  best_welfare_for_util_profile = -1
  best_arr_for_util_profile = []

  for arr in arrangements:
    welfare = calculate_total_utility(profile, arr)
    if welfare > best_welfare_for_util_profile:
      best_welfare_for_util_profile = welfare
      best_arr_for_util_profile = [arr]
    elif welfare == best_welfare_for_util_profile:
      best_arr_for_util_profile.append(arr)

  # Check if any of the best arrangements is stable
  any_stable = any(is_stable(profile, arr) for arr in best_arr_for_util_profile)

  return any_stable

def analyze_stability_welfare_relationship(n, num_processes, utility_func, utility_name, NUM_RANDOM_SAMPLES=1_000_000):
  """Analyze the relationship between welfare maximization and stability for given n and utility function."""
  people = [excel_label(i) for i in range(n)]
  arrangements = get_circular_arrangements(people)

  print(f"\n{'='*60}")
  print(f"Running analysis for n={n} with {utility_name} utility")
  print(f"{'='*60}")
  print(f"Number of unique circular arrangements: {len(arrangements)}")

  if (n > 5): #too many to generate all ranking profiles possible, so sample instead
    rankings_list = [generate_random_rankings(people) for _ in range(NUM_RANDOM_SAMPLES)]
  else:
    rankings_list = list(generate_all_rankings(people))
  total_profiles = len(rankings_list)
  print(f"Total number of ranking profiles: {total_profiles}")

  # Create partial function with fixed arguments
  process_func = partial(process_single_ranking,
                         arrangements=arrangements,
                         utility_func=utility_func,
                         n=n)

  # Process in parallel
  with Pool(processes=num_processes) as pool:
    results = pool.map(process_func, rankings_list)

  # Count results
  stable_count = sum(results)
  unstable_count = total_profiles - stable_count

  # Print summary table
  print(f"\n{'='*60}")
  print(f"SUMMARY TABLE - {utility_name.upper()} UTILITY (n={n})")
  print(f"{'='*60}")
  print(f"{'Category':<50} {'Count':>8}")
  print(f"{'-'*60}")
  print(f"{'Profiles with >=1 stable welfare-max arrangement':<50} {stable_count:>8}")
  print(f"{'Profiles with NO stable welfare-max arrangement':<50} {unstable_count:>8}")
  print(f"{'-'*60}")
  print(f"{'TOTAL PROFILES':<50} {total_profiles:>8}")
  print(f"{'='*60}")
  print(f"Percentage with stable welfare-max: {100*stable_count/total_profiles:.2f}%")
  print(f"{'='*60}\n")

  return {
    'utility_name': utility_name,
    'n': n,
    'total_profiles': total_profiles,
    'stable_count': stable_count,
    'unstable_count': unstable_count,
    'stable_percentage': 100*stable_count/total_profiles
  }

def main():
    num_processes = cpu_count()
    print(f"Using {num_processes} CPU cores...")

    print("\n" + "="*80)
    print("SEATING ARRANGEMENT STABILITY-WELFARE ANALYSIS")
    print("="*80)

    utility_functions = [
      (ranking_to_normalized_utility, "normalized"),
      (ranking_to_harmonic_utility, "harmonic"),
      (ranking_to_binary_utility, "binary")
    ]

    for n in range(4, 10):    
        results = []
        for utility_func, utility_name in utility_functions:
            result = analyze_stability_welfare_relationship(n, num_processes, utility_func, utility_name)
            results.append(result)

        # Print comparison table
        print("\n" + "="*80)
        print(f"COMPARISON ACROSS UTILITY FUNCTIONS (n={n})")
        print("="*80)
        print(f"{'Utility Function':<20} {'Stable %':>15} {'Stable Count':>15} {'Unstable Count':>15}")
        print("-"*80)
        for r in results:
            print(f"{r['utility_name']:<20} {r['stable_percentage']:>14.2f}% {r['stable_count']:>15} {r['unstable_count']:>15}")
            print("="*80)
        
        print("\n \n \n")

if __name__ == "__main__":
  main()