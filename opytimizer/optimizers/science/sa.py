"""Simulated Annealing.
"""

import copy

import numpy as np
from tqdm import tqdm

import opytimizer.math.random as r
import opytimizer.utils.exception as e
import opytimizer.utils.history as h
import opytimizer.utils.logging as l
from opytimizer.core.optimizer import Optimizer

logger = l.get_logger(__name__)


class SA(Optimizer):
    """A SA class, inherited from Optimizer.

    This is the designed class to define SA-related
    variables and methods.

    References:
        A. Khachaturyan, S. Semenovsovskaya and B. Vainshtein.
        The thermodynamic approach to the structure analysis of crystals.
        Acta Crystallographica (1981).

    """

    def __init__(self, algorithm='SA', params=None):
        """Initialization method.

        Args:
            algorithm (str): Indicates the algorithm name.
            params (dict): Contains key-value parameters to the meta-heuristics.

        """

        logger.info('Overriding class: Optimizer -> SA.')

        # Overrides its parent class with the receiving params
        super(SA, self).__init__()

        # System's temperature
        self.T = 100

        # Temperature decay
        self.beta = 0.999

        # Builds the class
        self.build(params)

        logger.info('Class overrided.')

    @property
    def T(self):
        """float: System's temperature.

        """

        return self._T

    @T.setter
    def T(self, T):
        if not isinstance(T, (float, int)):
            raise e.TypeError('`T` should be a float or integer')
        if T < 0:
            raise e.ValueError('`T` should be >= 0')

        self._T = T

    @property
    def beta(self):
        """float: Temperature decay.

        """

        return self._beta

    @beta.setter
    def beta(self, beta):
        if not isinstance(beta, (float, int)):
            raise e.TypeError('`beta` should be a float or integer')
        if beta < 0:
            raise e.ValueError('`beta` should be >= 0')

        self._beta = beta

    def _update(self, agents, function):
        """Method that wraps Simulated Annealing over all agents and variables.

        Args:
            agents (list): List of agents.
            function (Function): A function object.

        """

        # Iterate through all agents
        for agent in agents:
            # Mimics its position
            a = copy.deepcopy(agent)

            # Generating a random noise from a gaussian distribution
            noise = r.generate_gaussian_random_number(0, 0.1, size=((agent.n_variables, agent.n_dimensions)))

            # Applying the noise
            a.position += noise

            # Check agent limits
            a.clip_by_bound()

            # Calculates the fitness for the temporary position
            a.fit = function(a.position)

            # Generates an uniform random number
            r1 = r.generate_uniform_random_number()

            # If new fitness is better than agent's fitness
            if a.fit < agent.fit:
                # Copy its position and fitness to the agent
                agent.position = copy.deepcopy(a.position)
                agent.fit = copy.deepcopy(a.fit)

            # Checks if state should be updated or not
            elif r1 < np.exp(-(a.fit - agent.fit) / self.T):
                # Copy its position and fitness to the agent
                agent.position = copy.deepcopy(a.position)
                agent.fit = copy.deepcopy(a.fit)

        # Decay the temperature
        self.T *= self.beta

    def run(self, space, function, store_best_only=False, pre_evaluate=None):
        """Runs the optimization pipeline.

        Args:
            space (Space): A Space object that will be evaluated.
            function (Function): A Function object that will be used as the objective function.
            store_best_only (bool): If True, only the best agent of each iteration is stored in History.
            pre_evaluate (callable): This function is executed before evaluating the function being optimized.

        Returns:
            A History object holding all agents' positions and fitness achieved during the task.

        """

        # Initial search space evaluation
        self._evaluate(space, function, hook=pre_evaluate)

        # We will define a History object for further dumping
        history = h.History(store_best_only)

        # Initializing a progress bar
        with tqdm(total=space.n_iterations) as b:
            # These are the number of iterations to converge
            for t in range(space.n_iterations):
                logger.to_file(f'Iteration {t+1}/{space.n_iterations}')

                # Updating agents
                self._update(space.agents, function)

                # Checking if agents meet the bounds limits
                space.clip_by_bound()

                # After the update, we need to re-evaluate the search space
                self._evaluate(space, function, hook=pre_evaluate)

                # Every iteration, we need to dump agents and best agent
                history.dump(agents=space.agents, best_agent=space.best_agent)

                # Updates the `tqdm` status
                b.set_postfix(fitness=space.best_agent.fit)
                b.update()

                logger.to_file(f'Fitness: {space.best_agent.fit}')
                logger.to_file(f'Position: {space.best_agent.position}')

        return history
