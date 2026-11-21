import numpy as np
from sklearn.svm import SVC

training_data = np.loadtxt("hw_11_data.txt", delimiter=",")
x_1 = training_data[:, 0]
x_2 = training_data[:, 1]
X = np.column_stack([x_1, x_2])
c = training_data[:, 2]
# Translate labels to {-1, 1}
y = np.where(c == 1, 1, -1)

# To fit K(x, x') = (1 + <x, x'>)^d
poly_svm = SVC(kernel="poly", degree=2, gamma=1, coef0=1).fit(X, y)
poly_svm_accuracy = poly_svm.score(X, y)
print(f"Polynomial Kernel SVM Accuracy: {(poly_svm_accuracy * 100):.2f}%")
print("Number of support vectors:", len(poly_svm.support_))
