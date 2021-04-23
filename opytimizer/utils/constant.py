"""Constants.
"""

import sys

# Constant value used to avoid division by zero, zero logarithms
# and any possible mathematical errors
EPSILON = 1e-32

# When the agents are initialized, their fitness are defined as
# the maximum float possible
FLOAT_MAX = sys.float_info.max

# If necessary, one can apply custom rules to keys' dumping
# when using the History object
HISTORY_KEYS = ['agents', 'best_agent', 'local_position']

# When working with relativity theories, it is necessary
# to define a constant for the speed of light
LIGHT_SPEED = 3e5

# When using Genetic Programming, each function node needs an unique number of arguments,
# which is defined by this dictionary
FUNCTION_N_ARGS = {
    'SUM': 2,
    'SUB': 2,
    'MUL': 2,
    'DIV': 2,
    'EXP': 1,
    'SQRT': 1,
    'LOG': 1,
    'ABS': 1,
    'SIN': 1,
    'COS': 1
}

# Test passes if the best solution found by the agent in the target function
# is smaller than this value
TEST_EPSILON = 100

# When using the Tournament Selection, one must provide the size of rounds
# where individuals compete among themselves
TOURNAMENT_SIZE = 2
