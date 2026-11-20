import numpy as np
from sklearn.svm import SVC

training_data = np.loadtxt("hw_11_data.txt", delimiter=",")
x_1 = training_data[:, 0]
x_2 = training_data[:, 1]
X = np.column_stack([x_1, x_2])
c = training_data[:, 2]
# Translate labels to {-1, 1}
y = np.where(c == 1, 1, -1)

linear_svm = SVC(kernel="linear").fit(X, y)
linear_svm_accuracy = linear_svm.score(X, y)
print(f"Linear SVM Accuracy: {(linear_svm_accuracy * 100):.2f}%")
print("Weights ([w1, w2]):", np.round(linear_svm.coef_[0], 2), "Intercept (w0):", np.round(linear_svm.intercept_[0], 2))
