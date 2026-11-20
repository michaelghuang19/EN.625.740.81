import matplotlib.pyplot as plt
import numpy as np
from sklearn.svm import SVC

training_data = np.loadtxt("hw_11_data.txt", delimiter=",")
x_1 = training_data[:, 0]
x_2 = training_data[:, 1]
X = np.column_stack([x_1, x_2])
c = training_data[:, 2]
# Translate labels to {-1, 1}
y = np.where(c == 1, 1, -1)

# z + 0 = 1, z_1 = x_1, z_2 = x_2, z_3 = x_1^2, z_4 = x_2^2, z_5 = x_1 x_2
Z = np.column_stack([
  np.ones_like(x_1),
  x_1,
  x_2,
  x_1 ** 2,
  x_2 ** 2,
  x_1 * x_2,
])

z_svm = SVC(kernel="linear").fit(Z, y)
z_svm_accuracy = z_svm.score(Z, y)
print(f"Linear SVM for Z Accuracy: {(z_svm_accuracy * 100):.2f}%")
w = z_svm.coef_[0]
w_0 = z_svm.intercept_[0]
print("Weights ([w_1, w_2, w_3, w_4, w_5]):", np.round(w, 2))
print("Intercept (w_0):", np.round(w_0, 2))

# Grid for plotting the boundary 
x_1_grid = np.linspace(x_1.min() - 2.5, x_1.max() + 2.5, 100)
x_2_grid = np.linspace(x_2.min() - 2.5, x_2.max() + 2.5, 100)
X_1, X_2 = np.meshgrid(x_1_grid, x_2_grid)

# Map back into {x1, x2} space
f = (
  w_0
  + w[0] * X_1
  + w[1] * X_2
  + w[2] * (X_1 ** 2)
  + w[3] * (X_2 ** 2)
  + w[4] * (X_1 * X_2)
)

plt.scatter(x_1[c == 0], x_2[c == 0], label="Cluster 0 (y=-1)", s=25)
plt.scatter(x_1[c == 1], x_2[c == 1], label="Cluster 1 (y=1)", s=25)
plt.contour(X_1, X_2, f, levels=[0])
plt.xlabel("$x_1$")
plt.ylabel("$x_2$")
plt.title("Linear SVM in Z-Space Mapped Back to {$x_1$, $x_2$}")
plt.legend()
plt.show()
