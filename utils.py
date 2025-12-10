import itertools
import random
import math

SEED = 5 #global for reproducibility

def excel_label(i):
  #A, B, ..., Z, AA, ...
  s = ""
  while True:
    i, r = divmod(i, 26)
    s = chr(65 + r) + s
    if i == 0:
      break
    i -= 1
  return s

# NOTE: there (n-1)!/2 arrangements
# (n-1)! for sliding (explanation: https://www.youtube.com/watch?v=TgJMVLSjpOc)
# divide by 2 for cw/ccw
def get_circular_arrangements(people):
    arrangements = set()
    for p in itertools.permutations(people):
      # only add topologically different arrangements
      # e.g. ('A', 'C', 'B') == ('B', 'A', 'C') if you slide to the left or right enough
      # e.g. ('A', 'C', 'B') == ('A', 'B', 'C'). one is clockwise, the other counterclockwise
      rotations = [p[i:] + p[:i] for i in range(len(p))]

      p_reversed = p[::-1]
      reversed_rotations = [p_reversed[i:] + p_reversed[:i] for i in range(len(p))]

      #lexographically smallest
      #we get every rotation of both the original (clockwise) and reversed (ccw) permutation.
      #min = pick the permutation rotation that starts with 'A'
      arrangements.add(min(rotations + reversed_rotations))

    return list(arrangements)

def generate_random_arrangement(people):
  # random.seed(SEED)
  random.shuffle(people)
  return tuple(people)

# for n people, generate possible rankings
# NOTE: generator functions have better memory usage
# NOTE: since yielding, every time you iterate through rankings, you have to reinitialize it
def generate_all_rankings_for_person(person, people):
  others = [o for o in people if o != person]

  for ranking in itertools.permutations(others):
    yield (person, ranking)

def generate_all_rankings(people):
  rankings_per_person = [generate_all_rankings_for_person(p, people) for p in people]

  for combination in itertools.product(*rankings_per_person):
    yield {person: ranking for person, ranking in combination}
    #output: {'A': ('B', 'C'), 'B': ('A', 'C'), 'C': ('A', 'B')}
    #s.t. A: B > C, B: A > C, C: A > B

def generate_random_ranking_for_person(person, people):
  others = [o for o in people if o != person]
  # random.seed(SEED)
  random.shuffle(others)
  return tuple(others)

def generate_random_rankings(people):
  return {person: generate_random_ranking_for_person(person, people) for person in people}

# rankings -> utility
def ranking_to_normalized_utility(ordering, n):
  n_others = n-1
  score = [n_others-i for i in range(n_others)]
  total = sum(score)
  return {person: score[i]/total for i, person in enumerate(ordering)}

def ranking_to_harmonic_utility(ordering, n):
  n_others = n-1
  score = [1/(i+1) for i in range(n_others)]
  total = sum(score)
  return {person: score[i]/total for i, person in enumerate(ordering)}

def ranking_to_binary_utility(ordering, n):
  n_others = n-1
  # First person gets 1, everyone else gets 0
  return {person: (1.0 if i == 0 else 0.0) for i, person in enumerate(ordering)}

def generate_utilities(rankings, utility_func, n):
  return {person: utility_func(ranking, n) for person, ranking in rankings.items()}

def get_neighbors(arrangement, seat, idx=-1):
  #if you have the seat index already, pass it in the 'idx' parameter.
  #otherwise, we'll find the seat index using the 'seat' parameter.

  if(idx != -1):
    i = idx
  else:
    i = arrangement.index(seat)
  return [arrangement[i-1], arrangement[(i+1)%len(arrangement)]]

def calculate_total_utility(profile, arrangement):
  sum = 0

  for seat in arrangement:
    #check two neighbors
    neighbors = get_neighbors(arrangement, seat)
    sum += profile[seat][neighbors[0]] + profile[seat][neighbors[1]]

  return sum

def find_blocking_pair(profile, arrangement):
  for seat in arrangement:
    neighbors = get_neighbors(arrangement, seat)
    curr_utility = profile[seat][neighbors[0]] + profile[seat][neighbors[1]]

    for other in arrangement:
      if(other != seat):
        other_neighbors = get_neighbors(arrangement, other)

        #swapping two neighbors
        if(seat == other_neighbors[0]):
          other_utility = profile[seat][other_neighbors[1]] + profile[seat][other]
        elif(seat == other_neighbors[1]):
          other_utility = profile[seat][other_neighbors[0]] + profile[seat][other]
        else:
          other_utility = profile[seat][other_neighbors[0]] + profile[seat][other_neighbors[1]]

        #player 1 would benefit from swapping
        if(other_utility > curr_utility):
          #check if player 2 would benefit from swapping
          curr_utility2 = profile[other][other_neighbors[0]] + profile[other][other_neighbors[1]]

          if(other == neighbors[0]):
            other_utility2 = profile[other][neighbors[1]] + profile[other][seat]
          elif(other == neighbors[1]):
            other_utility2 = profile[other][neighbors[0]] + profile[other][seat]
          else:
            other_utility2 = profile[other][neighbors[0]] + profile[other][neighbors[1]]

          if(other_utility2 > curr_utility2):
            return [seat, other]
  return None

def is_stable(profile, arrangement):
  blocking_pair = find_blocking_pair(profile, arrangement)
  return blocking_pair == None

def swap_seats(prev_arrangement):
  """ Returns: an arrangement with two (distinct) seats swapped"""
  # random.seed(SEED)
  i = random.randrange(0, len(prev_arrangement))
  j = random.randrange(0, len(prev_arrangement))

  while i == j:
    j = random.randrange(0, len(prev_arrangement))

  next_arrangement = list(prev_arrangement)
  next_arrangement[i] = prev_arrangement[j]
  next_arrangement[j] = prev_arrangement[i]

  return tuple(next_arrangement)


def run_round(profile, prev_arrangement, T, findMax=True):
  """ Returns: next arrangement, based on utility increasing/decreasing total utility"""
  T_min = 0.001 #NOTE: could be lower?
  # random.seed(SEED)

  prev_utility = calculate_total_utility(profile, prev_arrangement)

  next_arrangement = swap_seats(prev_arrangement)
  next_utility = calculate_total_utility(profile, next_arrangement)

  #looking for global MAX
  if findMax:
    if next_utility >= prev_utility:
      return next_arrangement
    else:
      #next_utility < prev_utility
      x = random.random()

      if(T < T_min):
        prob = 0
      else:
        prob = math.exp((next_utility-prev_utility)/T)

      if(x <= prob):
        return prev_arrangement
      else:
        return next_arrangement
    
  #global MIN
  else:
    if next_utility <= prev_utility:
      return next_arrangement
    else:
      #next_utility > prev_utility
      x = random.random()

      if(T < T_min):
        prob = 0
      else:
        prob = math.exp((prev_utility-next_utility)/T)
      
      if(x <= prob):
        return prev_arrangement
      else:
        return next_arrangement

def run_simulated_annealing(n, profile, utility_func, utility_name, findMax=True):
  NUM_TIMES_TO_BE_CONVERGENT = 15
  people = [excel_label(i) for i in range(n)]

  #initial parameters
  curr_arrangement = generate_random_arrangement(people) #technically this is more than the reduced number of arrangements...
  T = 2*n #NOTE: typically upper bound of total utility. normalized/binary/harmonic UB = 1*2*n=2n
  MAX_ROUNDS = 10000
  gamma = 0.99
  prev_and_curr_same = 0

  for k in range(MAX_ROUNDS):
    prev_arrangement = curr_arrangement
    curr_arrangement = run_round(profile, curr_arrangement, T, findMax)
    T *= gamma

    if(prev_arrangement == curr_arrangement):
      prev_and_curr_same += 1
    else:
      prev_and_curr_same = 0

    #converged (previous and current arrangement have been the same X times)
    if(prev_and_curr_same > NUM_TIMES_TO_BE_CONVERGENT):
      break

  return curr_arrangement
  
def run_single_sa(args):
  """Helper function to run a single SA run - used for parallelization."""
  n, profile, utility_func, utility_name, findMax = args
  return run_simulated_annealing(n, profile, utility_func, utility_name, findMax)

def swap_blocking_pair_seats(prev_arrangement, seat, other):
  i = prev_arrangement.index(seat)
  j = prev_arrangement.index(other)

  next_arrangement = list(prev_arrangement)
  next_arrangement[i] = prev_arrangement[j]
  next_arrangement[j] = prev_arrangement[i]

  return tuple(next_arrangement)


def run_swap_blocking_pairs(profile, arr, init_blocking_pair):
  #swaps pairs MAX_ROUNDS times
  #returns stable arrangement, if found. otherwise, returns None
  n = len(arr)
  MAX_ROUNDS = 100*n

  blocking_pair = init_blocking_pair
  prev_arrangement = arr
  for _ in range(MAX_ROUNDS):
    next_arrangement = swap_blocking_pair_seats(prev_arrangement, blocking_pair[0], blocking_pair[1])

    blocking_pair = find_blocking_pair(profile, next_arrangement)
    #now stable
    if(blocking_pair == None):
      return next_arrangement
    else:
      prev_arrangement = next_arrangement
  return None

def simulated_annealing_swapping_blocking_pairs(n, utility_func, utility_name, NUM_RANDOM_SAMPLES=7_962_624, debug=False, findMax=True):
  NUM_PARALLEL_RUNS = 10 

  people = [excel_label(i) for i in range(n)]
  rankings = [generate_random_rankings(people) for _ in range(NUM_RANDOM_SAMPLES)]

  num_times_recovered = 0
  num_times_not_recovered_but_stable_solution = 0
  num_times_not_recovered_bc_no_stable_solution = 0

  num_times_found_after_initial_SA = 0
  num_times_found_after_swapping_pairs = 0

  for ranking in rankings:
    profile = generate_utilities(ranking, utility_func, n)

    num_stable = 0
    final_nonstable_arrangments = {}

    # Parallelize the 10 SA runs
    sa_args = [(n, profile, utility_func, utility_name, findMax) for _ in range(NUM_PARALLEL_RUNS)]
    with Pool(processes=min(NUM_PARALLEL_RUNS, cpu_count())) as pool:
      final_arrangements = pool.map(run_single_sa, sa_args)

    # Check results from SA runs
    for final_arr in final_arrangements:
      #found stable arrangement
      blocking_pair = find_blocking_pair(profile, final_arr)
      if(blocking_pair == None):
        num_stable += 1
        num_times_found_after_initial_SA += 1
        break
      else:
        final_nonstable_arrangments[final_arr] = blocking_pair

    if(num_stable == 0):
      #we collect the final arrangements from SA.
      #these are w.h.p local or global optima
      #swap blocking pairs and see if we can find a stable pair "nearby"
      for final_arr, blocking_pair in final_nonstable_arrangments.items():
        final = run_swap_blocking_pairs(profile, final_arr, blocking_pair)
        if(final != None):
          num_stable += 1
          num_times_found_after_swapping_pairs += 1
          break

      #POST SWAPPING blocking pairs and still not stable
      if(num_stable == 0):
        if(debug):
          print("After SA + swapping blocking pairs, no stable arrangement found.")

        #check all arrangements to see if a stable one exists
        #only do so if there's less than a trillion arrangements
        if(n < 13):
          all_arrangements = get_circular_arrangements(people)

          stable_exists = False
          for arr in all_arrangements:
            if(is_stable(profile, arr)):
              stable_exists = True

          if(stable_exists):
            num_times_not_recovered_but_stable_solution += 1
          else:
            num_times_not_recovered_bc_no_stable_solution += 1

      #POST SWAPPING blocking pairs, found a stable arrangement
      else:
        if(debug):
          print("Found a stable arrangement after swapping blocking pairs.")
        num_times_recovered += 1

    #recovered stable match from simply running SA
    else:
      if(debug):
          print("Found a stable arrangement after initial SA. Max welfare arrangement is stable.")
      num_times_recovered += 1

  print("Percentage Recovered:", num_times_recovered/NUM_RANDOM_SAMPLES)
  #how many recovered arrangements were from SA versus SA + swapping
  if(num_times_recovered > 0):
    print("Percentage of Recovered Found After Initial SA:", num_times_found_after_initial_SA/num_times_recovered)
    print("Percentage of Recovered Found After Swapping Blocking Pairs:", num_times_found_after_swapping_pairs/num_times_recovered)

  print("Percentage Not Recovered (No Stable Solution Exists):", num_times_not_recovered_bc_no_stable_solution/NUM_RANDOM_SAMPLES)
  print("Percentage Not Recovered (Stable Solution Exists):", num_times_not_recovered_but_stable_solution/NUM_RANDOM_SAMPLES)

def simulated_annealing_maxima_and_minima_swapping_blocking_pairs(n, utility_func, utility_name, NUM_RANDOM_SAMPLES=7_962_624, debug=False):
  NUM_PARALLEL_RUNS = 10 # PARALLELIZED

  people = [excel_label(i) for i in range(n)]
  rankings = [generate_random_rankings(people) for _ in range(NUM_RANDOM_SAMPLES)]


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

    # Parallelize the 10 SA runs
    sa_args = [(n, profile, utility_func, utility_name, True) for _ in range(NUM_PARALLEL_RUNS)]
    with Pool(processes=min(NUM_PARALLEL_RUNS, cpu_count())) as pool:
      final_arrangements = pool.map(run_single_sa, sa_args)

    # Check results from SA runs
    for final_arr in final_arrangements:
      #found stable arrangement
      blocking_pair = find_blocking_pair(profile, final_arr)
      if(blocking_pair == None):
        num_stable += 1
        num_times_found_after_initial_SA += 1
        break
      else:
        final_nonstable_arrangments[final_arr] = blocking_pair

    if(num_stable == 0):
      #we collect the final arrangements from SA.
      #these are w.h.p local or global optima
      #swap blocking pairs and see if we can find a stable pair "nearby"
      for final_arr, blocking_pair in final_nonstable_arrangments.items():
        final = run_swap_blocking_pairs(profile, final_arr, blocking_pair)
        if(final != None):
          num_stable += 1
          num_times_found_after_initial_swapping_pairs += 1
          break

      #POST SWAPPING blocking pairs and still not stable
      if(num_stable == 0):
        if(debug):
          print("After SA + swapping blocking pairs, no stable arrangement found.")

        #try 2: SA + swapping pairs with global MINIMA
        final_nonstable_arrangments = {}

        sa_args = [(n, profile, utility_func, utility_name, False) for _ in range(NUM_PARALLEL_RUNS)]
        with Pool(processes=min(NUM_PARALLEL_RUNS, cpu_count())) as pool:
          final_arrangements = pool.map(run_single_sa, sa_args)

        for final_arr in final_arrangements:
          #found stable arrangement
          blocking_pair = find_blocking_pair(profile, final_arr)
          if(blocking_pair == None):
            num_stable += 1
            num_times_found_after_second_SA += 1
            break
          else:
            final_nonstable_arrangments[final_arr] = blocking_pair

        #none of the global MINIMA are stable
        if(num_stable == 0):
          for final_arr, blocking_pair in final_nonstable_arrangments.items():
            final = run_swap_blocking_pairs(profile, final_arr, blocking_pair)
            if(final != None):
              num_stable += 1
              num_times_found_after_second_swapping_pairs += 1
              break 
          
          if(num_stable == 0):
            #tried both global MAXIMA and MINIMUM + swapping block pairs and didn't find stable arrangement

            #check all arrangements to see if a stable one exists
            #only do so if there's less than a trillion arrangements
            if(n < 13):
              all_arrangements = get_circular_arrangements(people)

              stable_exists = False
              for arr in all_arrangements:
                if(is_stable(profile, arr)):
                  stable_exists = True

              if(stable_exists):
                num_times_not_recovered_but_stable_solution += 1
              else:
                num_times_not_recovered_bc_no_stable_solution += 1
          else:
            if(debug):
              print("Found a stable arrangement after swapping blocking pairs for minima.")
            num_times_recovered += 1

        #one of the global MINIMA is stable
        else:
          if(debug):
            print("Found a stable arrangement after second (minima) SA. Min welfare arrangement is stable.")
          num_times_recovered += 1

      #POST SWAPPING blocking pairs, found a stable arrangement
      else:
        if(debug):
          print("Found a stable arrangement after swapping blocking pairs for maxima.")
        num_times_recovered += 1

    #recovered stable match from simply running SA
    else:
      if(debug):
          print("Found a stable arrangement after initial (maxima) SA. Max welfare arrangement is stable.")
      num_times_recovered += 1

  print("Percentage Recovered:", num_times_recovered/NUM_RANDOM_SAMPLES)
  #how many recovered arrangements were from SA versus SA + swapping
  if(num_times_recovered > 0):
    print("Percentage of Recovered Found After Initial SA:", num_times_found_after_initial_SA/num_times_recovered)
    print("Percentage of Recovered Found After Initial (Maxima) Swapping Blocking Pairs:", num_times_found_after_swapping_pairs/num_times_recovered)
    print("Percentage of Recovered Found After Second SA:", num_times_found_after_second_SA/num_times_recovered)
    print("Percentage of Recovered Found After Second (Minima) Swapping Blocking Pairs:", num_times_found_after_second_swapping_pairs/num_times_recovered)

  print("Percentage Not Recovered (No Stable Solution Exists):", num_times_not_recovered_bc_no_stable_solution/NUM_RANDOM_SAMPLES)
  print("Percentage Not Recovered (Stable Solution Exists):", num_times_not_recovered_but_stable_solution/NUM_RANDOM_SAMPLES)

def place_in_arrangement(n, person, arrangement, profile, utility_func, utility_name):
  max_individual_welfare = -1
  max_seat_idx = -1

  if utility_name == "normalized":
    median_individual_welfare = (n-1)/2
  elif utility_name == "harmonic":
    median_individual_welfare = 2 * 1/(n-1)
  elif utility_name == "binary":
    median_individual_welfare = 1/(n-1) #P[sitting next to your favorite person] = 1/(n-1)

  #look for a "good" enough seat (sitting next to at least one person in your top half rankings)
  for seat_idx, seat in enumerate(arrangement):
    #only check empty seats
    if seat == '':
      neighbors = get_neighbors(arrangement, seat, seat_idx)

      individual_welfare = 0

      # not an empty neighbor
      if neighbors[0] != '':
        individual_welfare += profile[person][neighbors[0]]
      if neighbors[1] != '':
        individual_welfare += profile[person][neighbors[1]]

      if (individual_welfare >= (median_individual_welfare)):
        max_individual_welfare = individual_welfare
        max_seat_idx = seat_idx

  #didn't find a "good" enough seat
  if(max_seat_idx == -1):
    possible_seat_idxs = []

    #find all empty seats
    for seat_idx, seat in enumerate(arrangement):
      if seat == '':
        possible_seat_idxs.append(seat_idx)

    # random.seed(SEED)
    max_seat_idx = random.choice(possible_seat_idxs)

  arrangement[max_seat_idx] = person
  return arrangement

def run_naive_sit_as_you_come(people, profile, utility_func, utility_name):
  starting_order = generate_random_arrangement(people)
  final_arrangement = ['' for i in range(n)]  #['', '', ...]

  for p in starting_order:
    final_arrangement = place_in_arrangement(n, p, final_arrangement, profile, utility_func, utility_name)

  return final_arrangement

def run_naive_swapping(people, profile, utility_func, utility_name):
  starting_arrangement = generate_random_arrangement(people)
  init_blocking_pair = find_blocking_pair(profile, starting_arrangement)

  if(init_blocking_pair != None):
    final_arrangement = run_swap_blocking_pairs(profile, starting_arrangement, init_blocking_pair)
    return final_arrangement
  else:
    return starting_arrangement