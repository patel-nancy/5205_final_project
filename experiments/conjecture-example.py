import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import *

def generate_basic_ranking_for_person(person, people):
  others = []
  i = people.index(person)

  for j, o in enumerate(people):
    if(j > i):
        others.append(o)

  for j, o in enumerate(people):
    if(j < i):
        others.append(o)

  return tuple(others)

def main():
    n = 5
    people = [excel_label(i) for i in range(n)]

    rankings = {person: generate_basic_ranking_for_person(person, people) for person in people}
    profile = generate_utilities(rankings, ranking_to_binary_utility, n)

    arrangements = get_circular_arrangements(people)
    max_welfare = -1

    for a in arrangements:
      welfare = calculate_total_utility(profile, a)
      max_welfare = max(max_welfare, welfare)

      if(is_stable(profile, a)):
          print(a, welfare)

    print("Maximum Possible Welfare:", max_welfare)
main()