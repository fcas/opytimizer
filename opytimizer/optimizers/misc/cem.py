"""Cross-Entropy Method.
"""

import numpy as np
from tqdm import tqdm

import opytimizer.math.random as r
import opytimizer.utils.exception as e
import opytimizer.utils.history as h
import opytimizer.utils.logging as l
from opytimizer.core.optimizer import Optimizer

logger = l.get_logger(__name__)


class CEM(Optimizer):
    """A CEM class, inherited from Optimizer.

    This is the designed class to define CEM-related
    variables and methods.

    References:
        R. Y. Rubinstein. Optimization of Computer simulation Models with Rare Events.
        European Journal of Operations Research (1997).

    """

    def __init__(self, algorithm='CEM', params=None):
        """Initialization method.

        Args:
            algorithm (str): Indicates the algorithm name.
            params (dict): Contains key-value parameters to the meta-heuristics.

        """

        # Overrides its parent class with the receiving params
        super(CEM, self).__init__()

        # Amount of positions to employ in mean and std updates
        self.n_updates = 5

        # Learning rate
        self.alpha = 0.7

        # Builds the class
        self.build(params)

        logger.info('Class overrided.')

    @property
    def n_updates(self):
        """int: Number of positions to employ in update formulae.

        """

        return self._n_updates

    @n_updates.setter
    def n_updates(self, n_updates):
        if not isinstance(n_updates, int):
            raise e.TypeError('`n_updates` should be an integer')
        if n_updates <= 0:
            raise e.ValueError('`n_updates` should be > 0')

        self._n_updates = n_updates

    @property
    def alpha(self):
        """float: Learning rate.

        """

        return self._alpha

    @alpha.setter
    def alpha(self, alpha):
        if not isinstance(alpha, (float, int)):
            raise e.TypeError('`alpha` should be a float or integer')
        if alpha < 0:
            raise e.ValueError('`alpha` should be >= 0')

        self._alpha = alpha

    def _create_new_samples(self, agents, function, mean, std):
        """Creates new agents based on current mean and standard deviation.

        Args:
            agents (list): List of agents.
            function (Function): A Function object that will be used as the objective function.
            mean (np.array): An array of means.
            std (np.array): An array of standard deviations.

        """

        # Iterate through all agents
        for agent in agents:
            # Iterate through all decision variables
            for j, (m, s) in enumerate(zip(mean, std)):
                # For each decision variable, we generate gaussian numbers based on mean and std
                agent.position[j] = r.generate_gaussian_random_number(m, s, agent.n_dimensions)

            # Clips the agent limits
            agent.clip_by_bound()

            # Calculates its new fitness
            agent.fit = function(agent.position)

    def _update_mean(self, updates, mean):
        """Calculates and updates mean.

        Args:
            updates (np.array): An array of updates' positions.
            mean (np.array): An array of means.

        Returns:
            The new mean values.

        """

        # Calculates the new mean based on update formula
        new_mean = self.alpha * mean + (1 - self.alpha) * np.mean(updates)

        return new_mean

    def _update_std(self, updates, mean, std):
        """Calculates and updates standard deviation.

        Args:
            updates (np.array): An array of updates' positions.
            mean (np.array): An array of means.
            std (np.array): An array of standard deviations.

        Returns:
            The new standard deviation values.

        """

        # Calculates the new standard deviation based on update formula
        new_std = self.alpha * std + (1 - self.alpha) * np.sqrt(np.mean((updates - mean) ** 2))

        return new_std

    def _update(self, agents, function, mean, std):
        """Method that wraps sampling, mean, and standard deviation updates over all agents and variables.

        Args:
            agents (list): List of agents.
            function (Function): A Function object that will be used as the objective function.
            mean (np.array): An array of means.
            std (np.array): An array of standard deviations.

        """

        # Creates new agents based on current mean and standard deviation
        self._create_new_samples(agents, function, mean, std)

        # Sorts the agents
        agents.sort(key=lambda x: x.fit)

        # Gathering the update positions
        update_position = np.array([agent.position for agent in agents[:self.n_updates]])

        # For every decision variable
        for j in range(mean.shape[0]):
            # Update its mean and standard deviation
            mean[j] = self._update_mean(update_position[:, j, :], mean[j])
            std[j] = self._update_std(update_position[:, j, :], mean[j], std[j])

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

        # Instantiating an array of means and standard deviations
        mean = np.zeros(space.n_variables)
        std = np.zeros(space.n_variables)

        # Iterates through all decision variables
        for j, (lb, ub) in enumerate(zip(space.lb, space.ub)):
            # Calculates the initial mean and standard deviation
            mean[j] = r.generate_uniform_random_number(lb, ub)
            std[j] = ub - lb

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
                self._update(space.agents, function, mean, std)

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
