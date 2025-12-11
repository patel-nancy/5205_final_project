import itertools
import random
import math

SEED = 5 #global for reproducibility
random.seed(SEED)

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

def assign_people_to_classes(people, classes):
  class_assignment = {}
  for p in people:
    class_assignment[p] = random.choice(classes)

  return class_assignment

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
  people_copy = people.copy()
  random.shuffle(people_copy)
  return tuple(people_copy)

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
  random.shuffle(others)
  return tuple(others)

def generate_random_rankings(people):
  return {person: generate_random_ranking_for_person(person, people) for person in people}

def generate_random_class_ranking_for_class(classes):
  #NOTE: every class gets to rank itself as well (e.g. people in class 3 like sitting next to others in class 3 most)
  classes_copy = classes.copy() 
  random.shuffle(classes_copy)
  return tuple(classes_copy)

def generate_random_class_rankings(classes):
  return {c: generate_random_class_ranking_for_class(classes) for c in classes} #{0: (2,3,1,0), 1: (2,0,3,1), ...}

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

def class_ranking_to_normalized_utility(people, class_assignment, class_ranking, n, k):
  total = (k-1)*k/2 #each class ranks the other k-1 classes w utility: k-1, k-2, ..., 1

  profile = {}
  for p in people:
    profile[p] = {}

    p_class = class_assignment[p]
    p_class_ranking = class_ranking[p_class]

    for o in people:
      if(p != o):
        o_class = class_assignment[o]
        rank = p_class_ranking.index(o_class) #ranking index (0 = 1st place, 1 = 2nd place, etc.)
        profile[p][o] = (k-1-rank)/total #utility

  return profile

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

def does_stable_arr_exist_for_profile(people, profile):
  all_arrangements = get_circular_arrangements(people)

  # stable_arrs = []
  for arr in all_arrangements:
    if(is_stable(profile, arr)):
      return True
      # stable_arrs.append(arr)

  return False

def swap_seats(prev_arrangement):
  """ Returns: an arrangement with two (distinct) seats swapped"""
  i = random.randrange(0, len(prev_arrangement))
  j = random.randrange(0, len(prev_arrangement))

  while i == j:
    j = random.randrange(0, len(prev_arrangement))

  next_arrangement = list(prev_arrangement)
  next_arrangement[i] = prev_arrangement[j]
  next_arrangement[j] = prev_arrangement[i]

  return tuple(next_arrangement)

def run_round(profile, prev_arrangement, T, findMax):
  """ Returns: next arrangement, based on utility increasing/decreasing total utility"""
  T_min = 0.001 #NOTE: could be lower?

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

def run_simulated_annealing(n, people, profile, utility_func, utility_name, findMax):
  NUM_TIMES_TO_BE_CONVERGENT = 15

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
  n, people, profile, utility_func, utility_name, findMax = args
  return run_simulated_annealing(n, people, profile, utility_func, utility_name, findMax)

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

def place_in_arrangement(n, person, arrangement, ranking, utility_func):
  best_guest_ranked_idx = n
  best_seat_idx = -1

  #look for a "good" enough seat (sitting next to at least one person in your top half rankings)
  for seat_idx, seat in enumerate(arrangement):
    #only check empty seats
    if seat == '':
      neighbors = get_neighbors(arrangement, seat, seat_idx)
      neighbor_ranking_idxs = [n, n] #starts out of bounds (only n-1 rankings). the lower the index, the higher rated the neighbor is.

      # not an empty neighbor
      if neighbors[0] != '':
        neighbor_ranking_idxs[0] = ranking[person].index(neighbors[0]) 

      if neighbors[1] != '':
        neighbor_ranking_idxs[1] = ranking[person].index(neighbors[1])

      #determine which guest is ranked higher
      higher_ranked_guest = ''
      higher_ranked_guest_idx = n
      if(neighbor_ranking_idxs[0] < neighbor_ranking_idxs[1]):
        higher_ranked_guest = neighbors[0]
        higher_ranked_guest_idx = neighbor_ranking_idxs[0]

      elif(neighbor_ranking_idxs[0] > neighbor_ranking_idxs[1]):
        higher_ranked_guest = neighbors[1]
        higher_ranked_guest_idx = neighbor_ranking_idxs[1]

      #sit next to the guest that is in your top half (closest to the favorite)
      if(higher_ranked_guest_idx < (n-1)/2 and higher_ranked_guest_idx < best_guest_ranked_idx):
        best_seat_idx = seat_idx 
        best_guest_ranked_idx = higher_ranked_guest_idx       

  #didn't find a "good" enough seat
  if(best_seat_idx == -1):
    possible_seat_idxs = []

    #find all empty seats
    for seat_idx, seat in enumerate(arrangement):
      if seat == '':
        possible_seat_idxs.append(seat_idx)

    best_seat_idx = random.choice(possible_seat_idxs)

  arrangement[best_seat_idx] = person
  return arrangement

def run_naive_sit_as_you_come(n, people, ranking, utility_func):
  starting_order = generate_random_arrangement(people)
  final_arrangement = ['' for i in range(n)]  #['', '', ...]

  for p in starting_order:
    final_arrangement = place_in_arrangement(n, p, final_arrangement, ranking, utility_func)

  return final_arrangement

def run_naive_swapping(people, profile):
  starting_arrangement = generate_random_arrangement(people)
  init_blocking_pair = find_blocking_pair(profile, starting_arrangement)

  if(init_blocking_pair != None):
    final_arrangement = run_swap_blocking_pairs(profile, starting_arrangement, init_blocking_pair)
    return final_arrangement
  else:
    return starting_arrangement