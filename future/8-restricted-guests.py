import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import *
from multiprocessing import Pool, cpu_count

def main():
    n = 8
    k = 4
    people = [excel_label(i) for i in range(n)] #[A,B,...,AA,...]
    classes = [_ for _ in range(k)] #[0,1,...]

    class_assignment = assign_people_to_classes(people, classes)
    class_ranking = generate_random_class_rankings(classes)
    print(class_ranking_to_normalized_utility(people, class_assignment, class_ranking, n, k))

if __name__ == "__main__":
    main()