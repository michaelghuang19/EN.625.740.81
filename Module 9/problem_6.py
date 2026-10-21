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

# Create 200 x 2 matrix of samples + class labels
x = np.vstack((class_1_samples, class_2_samples))
y = np.hstack((np.ones(100), np.zeros(100)))

# Train linear classifier using the Perceptron algorithm
linear_classifier = Perceptron(max_iter=1000, tol=1e-5)
linear_classifier.fit(x, y)

plt.figure(figsize=(8, 6))

# Create meshgrid for plotting decision boundary
x_min, x_max = x[:, 0].min() - 1, x[:, 0].max() + 1
y_min, y_max = x[:, 1].min() - 1, x[:, 1].max() + 1
xx, yy = np.meshgrid(np.arange(x_min, x_max, 0.05),
                     np.arange(y_min, y_max, 0.05))

# Predict across the meshgrid
z_linear = linear_classifier.predict(np.c_[xx.ravel(), yy.ravel()])
z_linear = z_linear.reshape(xx.shape)

# Plot points with decision boundary regions
plt.scatter(class_1_samples[:, 0], class_1_samples[:, 1], color='blue', label="Class 1", alpha=0.5)
plt.scatter(class_2_samples[:, 0], class_2_samples[:, 1], color='red', label="Class 2", alpha=0.5)

plt.contourf(xx, yy, z_linear, alpha=0.25)
plt.contour(xx, yy, z_linear, colors="black", linewidths=1)

plt.title("6. Perceptron Algorithm Decision Boundary")
plt.xlabel("$x_1$")
plt.ylabel("$x_2$")
plt.legend()
plt.savefig("problem_6_perceptron_plot.png", bbox_inches="tight")
plt.show()
plt.close()