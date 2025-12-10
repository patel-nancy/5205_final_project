import itertools
import random

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
  random.seed(SEED)
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
  random.seed(SEED)
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