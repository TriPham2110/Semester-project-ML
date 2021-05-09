"""
Ref: https://aihubprojects.com/svm-from-scratch-python/
     http://cs229.stanford.edu/materials/smo.pdf
     https://ai6034.mit.edu/wiki/images/SVM_and_Boosting.pdf
"""
import pickle
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import random as rn
from sklearn.preprocessing import StandardScaler


class SVM:

    def __init__(self, max_iteration=1000, kernel_type='linear', regularization=1.0, learning_rate=0.001, tol=1e-5):
        self.max_iteration = max_iteration
        self.kernel_type = kernel_type
        self.regularization = regularization
        self.learning_rate = learning_rate
        self.tol = tol

        self.X = None
        self.y = None
        self.alpha = None
        self.w = None
        self.b = None

    def kernel(self, x1, x2, kernel_type='linear', degree=None):
        self.kernel_type = kernel_type
        if self.kernel_type == 'linear':
            return np.dot(x1, x2.T)
        elif self.kernel_type == 'poly':
            if degree >= 2:
                return (np.dot(x1, x2.T) + self.b) ** degree
        elif self.kernel_type == 'rbf':
            pass
        else:
            print('Wrong kernel name')

    def train(self, X, y):
        self.X = SVM.normalize(X)
        self.y = y
        n = len(self.X)
        self.alpha = np.array([0.0] * n)
        self.b = 0.0
        iteration = 0
        while iteration < self.max_iteration:
            num_changed_alphas = 0

            for i in range(n):
                x_i, y_i = self.X[i, :], self.y[i]

                self.w = np.dot(self.alpha * self.y, self.X)
                
                E_i = self.f(x_i, self.w, self.b) - y_i
                res_i = y_i * E_i
                if (res_i.any() < - self.tol and self.alpha[i] < self.regularization) or (res_i.any() > self.tol and self.alpha[i] > 0):
                    j = self.get_rand_j(i, n)

                    x_j, y_j = self.X[j, :], self.y[j]
                    E_j = self.f(x_j, self.w, self.b) - y_j

                    prev_alpha_i, prev_alpha_j = self.alpha[i], self.alpha[j]

                    if y_i != y_j:
                        L, H = max(0, prev_alpha_j - prev_alpha_i), min(self.regularization, self.regularization + prev_alpha_j - prev_alpha_i)
                    else:
                        L, H = max(0, prev_alpha_i + prev_alpha_j - self.regularization), min(self.regularization, prev_alpha_i + prev_alpha_j)

                    if L == H:
                        continue

                    eta = 2 * self.kernel(x_i, x_j) - self.kernel_type(x_i, x_i) - self.kernel_type(x_j, x_j)

                    if eta >= 0:
                        continue

                    self.alpha[j] = prev_alpha_j + float(y_j * (E_i - E_j)) / eta

                    if self.alpha[j] > H:
                        self.alpha[j] = H
                    elif self.alpha[j] < L:
                        self.alpha[j] = L

                    if abs(self.alpha[j] - prev_alpha_j) < self.tol:
                        continue

                    self.alpha[i] = prev_alpha_i + y_i * y_j * (prev_alpha_j - self.alpha[j])

                    b_1 = self.b - E_i - y_i * (self.alpha[i] - prev_alpha_i) * self.kernel(x_i, x_i) - y_j * (self.alpha[j] - prev_alpha_j) * self.kernel(x_i, x_j)
                    b_2 = self.b - E_j - y_i * (self.alpha[i] - prev_alpha_i) * self.kernel(x_i, x_j) - y_j * (self.alpha[j] - prev_alpha_j) * self.kernel(x_j, x_j)

                    if 0 < self.alpha[i] < self.regularization:
                        self.b = b_1
                    elif 0 < self.alpha[j] < self.regularization:
                        self.b = b_2
                    else:
                        self.b = (b_1 + b_2) / 2.0

                    num_changed_alphas += 1

            if num_changed_alphas == 0:
                iteration += 1
            else:
                iteration = 0

    def predict(self, X):
        X = SVM.normalize(X)
        return self.f(X, self.w, self.b)

    def f(self, X, w, b):
        pred = np.array([])
        
        # X = X.reshape(len(X),1)
        f_x = np.dot(w, X.T) + b

        for e in f_x:
            if e.any() >= 0:
                pred = np.append(pred, 1)
            else:
                pred = np.append(pred, -1)
        return pred

    def get_rand_j(self, i, n):
        j = 0
        count = 0
        while j == i and count < 1000:
            j = rn.randint(0, n)
            count += 1
        return j

    @staticmethod
    def normalize(X):
        if isinstance(X, pd.DataFrame):
            X = X.values
        return StandardScaler().fit_transform(X)