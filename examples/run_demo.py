from pprint import pprint

from cpsat_jssp.experiment import run_demo


if __name__ == "__main__":
    pprint(run_demo(time_limit=10.0, workers=1, seed=2026))
