#!/usr/bin/env python

"""
implemented algorithms for bandit optimization

- Random: random selection of arms
- EpsilonGreedy: epsilon greedy algorithm
- AnnealingEpsilonGreedy: epsilon greedy with annealing (decaying epsilon)
- Boltzmann: softmax algorithm
- AnnealingBoltzmann: softmax with annealing (decaying tau)
- Pursuit
- ReinforcementComparison
"""

import random
import math
import numpy as np


class Random:  # random selection of arms

    def __init__(self, counts, emp_means):
        self.counts = counts
        self.emp_means = emp_means
        return

    def reset(self, n_arms):
        self.counts = [0 for col in range(n_arms)]
        self.emp_means = [0.0 for col in range(n_arms)]
        return

    def select_next_arm(self):
        return random.randrange(len(self.emp_means))

    def update(self, chosen_arm, reward):
        self.counts[chosen_arm] = self.counts[chosen_arm] + 1
        n = self.counts[chosen_arm]
        value = self.emp_means[chosen_arm]
        new_value = ((n - 1) / float(n)) * value + (1 / float(n)) * reward
        self.emp_means[chosen_arm] = new_value
        return


class EpsilonGreedy:

    def __init__(self, epsilon, counts, emp_means):
        self.epsilon = epsilon
        self.counts = counts
        self.emp_means = emp_means  # empirical means of rewards
        return

    def reset(self, n_arms):
        self.counts = [0 for col in range(n_arms)]
        self.emp_means = [0.0 for col in range(n_arms)]
        return

    def select_next_arm(self):
        if random.random() > self.epsilon:
            return np.argmax(self.emp_means)
        else:
            return random.randrange(len(self.emp_means))

    def update(self, chosen_arm, reward):
        self.counts[chosen_arm] = self.counts[chosen_arm] + 1
        n = self.counts[chosen_arm]
        value = self.emp_means[chosen_arm]
        new_value = ((n - 1) / float(n)) * value + (1 / float(n)) * reward
        self.emp_means[chosen_arm] = new_value
        return


class AnnealingEpsilonGreedy:

    def __init__(self, counts, emp_means):
        self.counts = counts
        self.emp_means = emp_means  # reward value (as average)
        return

    def reset(self, n_arms):
        self.counts = [0 for col in range(n_arms)]
        self.emp_means = [0.0 for col in range(n_arms)]
        return

    def select_next_arm(self):
        t = np.sum(self.counts) + 1
        epsilon = 1/math.log(t + 1e-7)

        if random.random() > epsilon:
            return np.argmax(self.emp_means)
        else:
            return random.randrange(len(self.emp_means))

    def update(self, chosen_arm, reward):
        self.counts[chosen_arm] = self.counts[chosen_arm] + 1
        n = self.counts[chosen_arm]
        value = self.emp_means[chosen_arm]
        new_value = ((n - 1) / float(n)) * value + (1 / float(n)) * reward
        self.emp_means[chosen_arm] = new_value
        return


class Boltzmann:  # aka softmax

    def __init__(self, tau, counts, emp_means):
        self.tau = tau
        self.counts = counts
        self.emp_means = emp_means  # reward value (average)
        return

    def reset(self, n_arms):
        self.counts = [0 for col in range(n_arms)]
        self.emp_means = [0.0 for col in range(n_arms)]
        return

    def select_next_arm(self):
        z = sum([math.exp(v / self.tau) for v in self.emp_means])
        probs = [math.exp(v / self.tau) / z for v in self.emp_means]
        return random.choices(np.arange(len(self.emp_means)), weights=probs, k=1)[0]

    def update(self, chosen_arm, reward):
        self.counts[chosen_arm] = self.counts[chosen_arm] + 1
        n = self.counts[chosen_arm]
        value = self.emp_means[chosen_arm]
        new_value = ((n - 1) / float(n)) * value + (1 / float(n)) * reward
        self.emp_means[chosen_arm] = new_value
        return


class AnnealingBoltzmann:
    def __init__(self, counts, emp_means):
        self.counts = counts
        self.emp_means = emp_means  # reward value (average)
        return

    def reset(self, n_arms):
        self.counts = [0 for col in range(n_arms)]
        self.emp_means = [0.0 for col in range(n_arms)]
        return

    def select_next_arm(self):
        t = np.sum(self.counts) + 1
        tau = 1/math.log(t + 1e-7)

        z = sum([math.exp(v / tau) for v in self.emp_means])
        probs = [math.exp(v / tau) / z for v in self.emp_means]
        return random.choices(np.arange(len(self.emp_means)), weights=probs, k=1)[0]

    def update(self, chosen_arm, reward):
        self.counts[chosen_arm] = self.counts[chosen_arm] + 1
        n = self.counts[chosen_arm]
        value = self.emp_means[chosen_arm]
        new_value = ((n - 1) / float(n)) * value + (1 / float(n)) * reward
        self.emp_means[chosen_arm] = new_value
        return


class Pursuit:

    def __init__(self, lr, counts, emp_means, probs):
        self.lr = lr  # learning rate
        self.counts = counts
        self.emp_means = emp_means  # reward value (average)
        self.probs = probs
        return

    def reset(self, n_arms):
        self.counts = [0 for col in range(n_arms)]
        self.emp_means = [0.0 for col in range(n_arms)]
        self.probs = [float(1/n_arms) for col in range(n_arms)]
        return

    def select_next_arm(self):
        return random.choices(np.arange(len(self.emp_means)), weights=self.probs, k=1)[0]

    def update(self, chosen_arm, reward):

        # update counts
        self.counts[chosen_arm] = self.counts[chosen_arm] + 1
        n = self.counts[chosen_arm]

        # update reward
        value = self.emp_means[chosen_arm]
        new_value = ((n - 1) / float(n)) * value + (1 / float(n)) * reward
        self.emp_means[chosen_arm] = new_value

        # update probs
        if np.sum(self.emp_means) == 0:  # np.argmax returns the first arm when all reward emp_means are 0, so make sure we don't update probs in that case
            pass
        else:
            for ii in range(len(self.counts)):
                current_prob = self.probs[ii]
                if ii == np.argmax(self.emp_means):
                    self.probs[ii] = current_prob + self.lr*(1-current_prob)
                else:
                    self.probs[ii] = current_prob + self.lr*(0-current_prob)

        return


class ReinforcementComparison:  # need more test, doesn't seem to work
    
    def __init__(self, alpha, beta, counts, emp_means, preferences, exp_rewards, probs):
        self.alpha = alpha  # learning rate for expected reward
        self.beta = beta  # learning rate for preference 
        self.counts = counts  # num data points for each arm
        self.emp_means = emp_means  # empirical means of rewards for each arm
        self.preferences = preferences
        self.exp_rewards = exp_rewards
        self.probs = probs
        return

    def reset(self, n_arms):
        self.counts = [0 for col in range(n_arms)]
        self.emp_means = [0.0 for col in range(n_arms)]
        self.preferences = [0.0 for col in range(n_arms)]  # how to initialize?
        self.exp_rewards = [0.0 for col in range(n_arms)]  # how to initialize?
        self.probs = [float(1/n_arms) for col in range(n_arms)]
        return

    def select_next_arm(self):
        return random.choices(np.arange(len(self.emp_means)), weights=self.probs, k=1)[0]

    def update(self, chosen_arm, reward):
        # update counts
        self.counts[chosen_arm] = self.counts[chosen_arm] + 1
        n = self.counts[chosen_arm]

        # update empirical means
        value = self.emp_means[chosen_arm]
        new_mean = ((n - 1) / float(n)) * value + (1 / float(n)) * reward
        self.emp_means[chosen_arm] = new_mean

        # update preference
        self.preferences[chosen_arm] = self.preferences[chosen_arm] + self.beta * (reward - self.exp_rewards[chosen_arm])
        print(self.preferences)

        # update expected reward
        self.exp_rewards[chosen_arm] = (1-self.alpha) * self.exp_rewards[chosen_arm] + self.alpha * reward
        #print(self.exp_rewards)

        # update probs
        exp_preference = [math.exp(p) for p in self.preferences]
        s = np.sum(exp_preference)
        self.probs = [e / s for e in exp_preference]
        #print(self.probs)

        return


class UCB1:

    def __init__(self, counts, emp_means, ucbs):
        self.counts = counts
        self.emp_means = emp_means
        self.ucbs = ucbs  # ucb values calculated with means and counts
        return

    def reset(self, n_arms):
        self.counts = [0 for col in range(n_arms)]
        self.emp_means = [0.0 for col in range(n_arms)]
        self.ucbs = [0.0 for col in range(n_arms)]
        return

    def _update_ucbs(self):
        bonuses = [math.sqrt((2 * math.log(sum(self.counts) + 1)) / float(self.counts[arm] + 1e-7)) for arm in range(len(self.counts))]
        self.ucbs = [e + b for e, b in zip(self.emp_means, bonuses)]
        return

    def select_next_arm(self):
        if sum(self.counts) < len(self.counts):  # run a first pass through all arms
            for arm in range(len(self.counts)):
                if self.counts[arm] == 0:
                    return arm
        else:  # now select arm based on ucb value
            return np.argmax(self.ucbs)

    def update(self, chosen_arm, reward):
        self.counts[chosen_arm] = self.counts[chosen_arm] + 1
        n = self.counts[chosen_arm]
        value = self.emp_means[chosen_arm]
        new_value = ((n - 1) / float(n)) * value + (1 / float(n)) * reward
        self.emp_means[chosen_arm] = new_value
        self._update_ucbs()
        return


class UCB1Tuned:  # seems like V value are a lot bigger than 1/4, but should be normal behavior with small t

    def __init__(self, counts, emp_means, M2, ucbs):
        self.counts = counts
        self.emp_means = emp_means
        self.M2 = M2  # M2(n) = var(n) * n, used to update variance (a more stable Welford's algo)
        self.ucbs = ucbs  # ucb values calculated with means and counts
        return

    def reset(self, n_arms):
        self.counts = [0 for col in range(n_arms)]
        self.emp_means = [0.0 for col in range(n_arms)]
        self.M2 = [0.0 for col in range(n_arms)]
        self.ucbs = [0.0 for col in range(n_arms)]
        return

    def _update_ucbs(self):
        Vs = [self.M2[arm] / (self.counts[arm]+1e-7) + math.sqrt(2 * math.log(sum(self.counts)+1) / float(self.counts[arm] + 1e-7)) for arm in range(len(self.counts))]
        mins = [min(1/4, v) for v in Vs]
        bonuses = [math.sqrt((math.log(sum(self.counts)+1)) / float(self.counts[arm] + 1e-7) * mins[arm]) for arm in range(len(self.counts))]
        self.ucbs = [e + b for e, b in zip(self.emp_means, bonuses)]
        return

    def select_next_arm(self):
        if sum(self.counts) < len(self.counts):  # run a first pass through all arms
            for arm in range(len(self.counts)):
                if self.counts[arm] == 0:
                    return arm
        else:  # now select arm based on ucb value
            return np.argmax(self.ucbs)

    def update(self, chosen_arm, reward):
        # update counts
        self.counts[chosen_arm] = self.counts[chosen_arm] + 1
        n = self.counts[chosen_arm]
        # update emp. means
        old_mean = self.emp_means[chosen_arm]
        new_mean = ((n - 1) / float(n)) * old_mean + (1 / float(n)) * reward
        self.emp_means[chosen_arm] = new_mean
        # update M2 values (n*variance)
        self.M2[chosen_arm] = self.M2[chosen_arm] + (reward - old_mean) * (reward - new_mean)
        # update UCB value
        self._update_ucbs()
        return


if __name__ == '__main__':
    a = EpsilonGreedy(epsilon=0, counts=[], emp_means=[])
    a.reset(5)