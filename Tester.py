import sys
import os
import subprocess
import argparse
from math import ceil
from subprocess import check_output
from Lexer import runlexer

TESTER_DIR = "tests/"

stage = None

def run_test(test_set, test):
    lexer = TESTER_DIR + "T{}/".format(stage) + test_set + '/' + test_set + ".lex"
    finput = TESTER_DIR + "T{}/".format(stage) + test_set + "/input/" + test_set + '.' + test + ".in"
    foutput = TESTER_DIR + "T{}/".format(stage) + test_set + "/out/" + test_set + '.' + test + ".out"
    freference = TESTER_DIR + "T{}/".format(stage) + test_set + "/ref/" + test_set + '.' + test + ".ref"

    if not os.path.exists(os.path.dirname(foutput)):
        try:
            os.makedirs(os.path.dirname(foutput))
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise

    runlexer(lexer, finput, foutput)
    val = subprocess.call(["diff","--ignore-all-space", foutput, freference])

    no_dots = 20
    set_no = int(test_set.split('.')[1])
    if set_no > 9:
        no_dots -= 1
    if int(test) > 9:
        no_dots -= 1
    dots = '.' * no_dots

    if val == 1:
        points = 0
        print(test_set + "." + test + dots + "failed [0p]")
    elif val == 0:
        if set_no == 1:
            points = 2.5
        else:
            points = 1
        print(test_set + "." + test + dots + "passed [{}p]".format(points))

    return points

def run_test_set(test_set):
    # stage = int(test_set.split('.')[0][1])
    input_dir = TESTER_DIR + "T{}/".format(stage) + test_set + "/input/"
    # inputs = [os.path.splitext(f)[0] for f in listdir(input_dir)]
    inputs = list(map(lambda f : int(f.split('.')[-2]), os.listdir(input_dir)))
    inputs.sort()
    inputs = map(lambda i : str(i), inputs)

    print("Testset", test_set)
    set_total = 0
    for i in inputs:
        set_total += run_test(test_set, i)
    set_total = ceil(set_total)
    print("Set total" + '.' * 17 + "[{}p]".format(set_total))

    return set_total

def run_all():
    print("Stage {}".format(stage))
    test_sets = os.listdir(TESTER_DIR + "T{}".format(stage))
    test_sets.sort(key=lambda t : int(t[3:]))
    total = 0
    for test_set in test_sets:
        total += run_test_set(test_set)
        if test_set != test_sets[-1]:
            print()
    print("\nTotal" + '.' * 21 + "[{}p]".format(total))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='FLA project checker')
    parser.add_argument('--stage', default='1',
                        help='Project stage')
    parser.add_argument('--set',
                        help='Test set index')
    parser.add_argument('--test',
                        help='Test index')
    args = parser.parse_args()

    if args.test and not args.set:
        sys.exit("Test set must be specified if you want to run a specific test")

    stage = int(args.stage)

    if stage > 3:
        sys.exit("There are only three stages to the project")

    if stage != 1:
        sys.exit("Stage {} checker coming soon".format(stage))

    if args.set:
        if args.test:
            if not args.test.isnumeric():
                sys.exit("Test index must be a number")
            run_test(args.set, args.test)
        else:
            run_test_set(args.set)
    else:
        run_all()

