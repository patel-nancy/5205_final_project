# Heuristically Recovering Stable Dinner Party Seating Arrangements in NP-Hard Settings

This repository contains the code and experimental results for the paper:

> **"Heuristically Recovering Stable Dinner Party Seating Arrangements in NP-Hard Settings."**

## Repository Structure

### `/experiments`
All experiment code and corresponding results described in the paper are located in the `experiments` directory. Any shared or helper methods are in `utils.py`.

The tables in the paper correspond to the following experiment scripts:

- **Table 1:** `2-naive-first-come-first-serve.py`
- **Table 2:** `3-naive-swapping.py`
- **Table 3:** `1-stability-maxwelfare-relationship.py`
- **Table 4:** `4-basic-SA.py`
- **Tables 5 & 6:** `5-basic-SA-with-swapping.py`
- **Table 7:** `6-max-and-min-SA-with-swapping.py`
- **Table 8:** `7-max-and-min-SA-swapping-with-different-utilities.py`

### `/future`
The `future` directory contains experiments that were not included in the paper but may be explored in subsequent work.
