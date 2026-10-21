import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import Perceptron

mu_1 = np.array([1, -1])
mu_2 = np.array([0, 0])

cov = np.array([
  [0.2, 0], [0, 0.2]
])

class_1_samples = []
while len(class_1_samples) < 100:
  sample = np.random.multivariate_normal(mu_1, cov)
  # Reject if x_1 - x_2 < 1
  if sample[0] - sample[1] >= 1:
    class_1_samples.append(sample)
class_1_samples = np.array(class_1_samples)

class_2_samples = []
while len(class_2_samples) < 100:
  sample = np.random.multivariate_normal(mu_2, cov)
  # Reject if x_1 - x_2 > 1
  if sample[0] - sample[1] <= 1:
    class_2_samples.append(sample)
class_2_samples = np.array(class_2_samples)

# X = np.vstack((class1_samples, class2_samples))
# y = np.hstack((np.ones(100), np.zeros(100)))

# # Train a linear classifier using the Perceptron algorithm
# clf = Perceptron(max_iter=1000, tol=1e-3)
# clf.fit(X, y)

# # Plotting
# plt.figure(figsize=(8, 6))

# # Create meshgrid for plotting the decision boundary
# x_min, x_max = X[:, 0].min() - 0.5, X[:, 0].max() + 0.5
# y_min, y_max = X[:, 1].min() - 0.5, X[:, 1].max() + 0.5
# xx, yy = np.meshgrid(np.arange(x_min, x_max, 0.02),
#                      np.arange(y_min, y_max, 0.02))

# # Predict across the meshgrid
# Z = clf.predict(np.c_[xx.ravel(), yy.ravel()])
# Z = Z.reshape(xx.shape)

# # Plot decision boundary regions
# plt.contourf(xx, yy, Z, alpha=0.2, cmap='coolwarm')
# plt.contour(xx, yy, Z, colors='k', linewidths=1.5)

# # Plot the generated data points
# plt.scatter(class1_samples[:, 0], class1_samples[:, 1], color='blue', label='Class 1 ($\omega_1$)', alpha=0.7, edgecolor='k')
# plt.scatter(class2_samples[:, 0], class2_samples[:, 1], color='red', label='Class 2 ($\omega_2$)', alpha=0.7, edgecolor='k')

# plt.title('Problem 6: Perceptron Decision Boundary')
# plt.xlabel('$x_1$')
# plt.ylabel('$x_2$')
# plt.legend()
# plt.grid(True, linestyle='--', alpha=0.6)
# plt.show()