import numpy as np
from sklearn.svm import SVC

training_data = np.loadtxt("hw_11_data.txt", delimiter=",")
x_1 = training_data[:, 0]
x_2 = training_data[:, 1]
X = np.column_stack([x_1, x_2])
c = training_data[:, 2]
# Translate labels to {-1, 1}
y = np.where(c == 1, 1, -1)

rbf_svm = SVC(kernel="rbf").fit(X, y)
rbf_svm_accuracy = rbf_svm.score(X, y)
print(f"Radial Basis Function Accuracy: {(rbf_svm_accuracy * 100):.2f}%")
print("Number of support vectors:", len(rbf_svm.support_))
