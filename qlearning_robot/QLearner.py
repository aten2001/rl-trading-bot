"""
Template for implementing QLearner  (c) 2015 Tucker Balch
"""

import numpy as np
import random as rand

class QLearner(object):

    def __init__(self, \
        num_states=100, \
        num_actions = 4, \
        alpha = 0.2, \
        gamma = 0.9, \
        rar = 0.5, \
        radr = 0.99, \
        dyna = 0, \
        verbose = False):

        self.verbose = verbose
        self.q = np.zeros((num_states, num_actions))
        self.t = np.ones((num_states, num_actions, num_states)) * 1e-9
        self.r = np.zeros((num_states, num_actions))
        self.alpha = alpha
        self.gamma = gamma
        self.rar = rar
        self.radr = radr
        self.dyna = dyna
        self.last_state = -1
        self.last_action = -1

    def choose_action(self, s):
        if rand.random() < self.rar:
            return rand.randint(0, self.q.shape[1]-1)
        else:
            return np.argmax(self.q[s])

    def querysetstate(self, s):
        """
        @summary: Update the state without updating the Q-table
        @param s: The new state
        @returns: The selected action
        """
        action = self.choose_action(s)
        self.last_state = s
        self.last_action = action
        if self.verbose: print "s =", s,"a =",action
        return action

    def query(self,s_prime,r):
        """
        @summary: Update the Q table and return an action
        @param s_prime: The new state
        @param r: The ne state
        @returns: The selected action
        """
        s = self.last_state
        a = self.last_action
        if self.dyna == 0:
            self.q[s, a] = (1 - self.alpha) * self.q[s, a] + self.alpha * (r + self.gamma * np.max(self.q[s_prime]))
        else:
            self.t[s, a, s_prime] += 1
            self.r[s, a] = (1 - self.alpha) * self.r[s, a] + self.alpha * r
            t = self.t / np.sum(self.t, axis=2, keepdims=True)
            q = np.max(self.q, axis=1)
            q_expected = np.dot(t, q)
            for i in np.random.choice(self.q.shape[0] * self.q.shape[1], self.dyna, replace=False):
                s_i = i % self.q.shape[0]
                a_i = i // self.q.shape[0]
                self.q[s_i, a_i] = self.r[s_i, a_i] + self.gamma * q_expected[s_i, a_i]
        action = self.choose_action(s_prime)
        self.last_state = s_prime
        self.last_action = action
        self.rar *= self.radr
        if self.verbose:
            print "s =", s_prime,"a =",action,"r =",r
        return action

    def author(self):
        return 'hwang404'

if __name__=="__main__":
    print "Remember Q from Star Trek? Well, this isn't him"
