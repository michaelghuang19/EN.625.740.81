import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import multivariate_normal
from sklearn.model_selection import train_test_split
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

FILE_DATASET_NAME_MAP = {
  "supervised_learning_data_3.txt" : "Dataset 3",
  "supervised_learning_data_5.txt" : "Dataset 5",
  "supervised_learning_data_7.txt" : "Dataset 7",
}

FILE_MEAN_MAP = {
  "supervised_learning_data_3.txt" : [
    np.array([5, 10]),
    np.array([6, 4]),
  ],
  "supervised_learning_data_5.txt" : [
    np.array([2, 2]),
    np.array([0, 0]),
  ],
  "supervised_learning_data_7.txt" : [
    np.array([2, 0]),
    np.array([-5, 5]),
    np.array([-3, -3]),
  ],
}

P1 = np.array([
  [np.cos(np.pi/6), np.sin(np.pi/6)], 
  [-np.sin(np.pi/6), np.cos(np.pi/6)],
])
P2 = np.array([
  [np.cos(2*np.pi/3), np.sin(2*np.pi/3)], 
  [-np.sin(2*np.pi/3), np.cos(2*np.pi/3)],
])
Q = np.array([[4, 0], [0, 9]])
P = np.array([
  [np.cos(5*np.pi/6), np.sin(5*np.pi/6)], 
  [-np.sin(5*np.pi/6), np.cos(5*np.pi/6)],
])

FILE_COVARIANCE_MAP = {
  "supervised_learning_data_3.txt" : [
    P1 @ Q @ P1.T,
    P2 @ Q @ P2.T,
  ],
  "supervised_learning_data_5.txt" : [
    P @ np.array([[4, 0], [0, 1]]) @ P.T,
    P @ np.array([[4, 0], [0, 9]]) @ P.T,
  ],
  "supervised_learning_data_7.txt" : [
    np.eye(2), 
    4 * np.eye(2), 
    9 * np.eye(2),
  ]
}



def analyze_dataset(filepath):
  df = pd.read_csv(filepath, header=None)
  x = df.iloc[:, :-1].values
  y = df.iloc[:, -1].values
  classes = np.unique(y)
  print(f"{FILE_DATASET_NAME_MAP[filepath]} Results")
  
  # Generate color values along the rainbow spectrum for the number of classes
  colors = [plt.cm.jet(i / (len(classes) - 1)) for i in range(len(classes))]

  # (a) i. Plot the data using a different color for each class.
  plt.figure(figsize=(8, 6))
  for idx, class_label in enumerate(classes):
    plt.scatter(
      x[y == class_label, 0],
      x[y == class_label, 1],
      color=colors[idx], label=f"Class {int(class_label)}", alpha=0.5
    )

  # (a) ii. Using the known distributions, plot the Bayes decision boundaries.

  mean_list = FILE_MEAN_MAP[filepath]
  covariance_list = FILE_COVARIANCE_MAP[filepath]

  # Set up numpy meshgrid which is used for shaping the decision boundaries

  x_min, x_max = x[:, 0].min() - 1, x[:, 0].max() + 1
  y_min, y_max = x[:, 1].min() - 1, x[:, 1].max() + 1
  xx, yy = np.meshgrid(np.arange(x_min, x_max, 0.05), np.arange(y_min, y_max, 0.05))
  pos = np.dstack((xx, yy))

  probabilities = [multivariate_normal(mean=mu, cov=cov).pdf(pos) for mu, cov in zip(mean_list, covariance_list)]
  Z_bayes = np.argmax(probabilities, axis=0)

  plt.contourf(xx, yy, Z_bayes, alpha=0.25)
  plt.contour(xx, yy, Z_bayes, colors="black", linewidths=1)
    
  plt.title(f"{FILE_DATASET_NAME_MAP[filepath]}: 6(a) True Bayes Boundaries")
  plt.legend()
  plt.savefig(f"dataset_{FILE_DATASET_NAME_MAP[filepath][-1]}_true_bayes.png", bbox_inches="tight")
  plt.show()
  plt.close()

  # (b) Split each dataset into 50% training data and 50% testing data. 
  x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.5, stratify=y)

  # (b) i. Plot the testing data using a different color for each class.
  plt.figure(figsize=(8, 6))
  for idx, class_label in enumerate(classes):
    plt.scatter(
      x_test[y_test == class_label, 0],
      x_test[y_test == class_label, 1],
      color=colors[idx], label=f"Test Class {int(class_label)}", alpha=0.5
    )

  # (b) ii. Compute estimates for the parameters (mean and covariance) of each class.
  for c in classes:
    x_class = x_train[y_train == c]
    print(f"Class {int(c)} Mean: {np.mean(x_class, axis=0)}")
    print(f"Class {int(c)} Covariance: {np.cov(x_class, rowvar=False)}")

  lda = LinearDiscriminantAnalysis()
  lda.fit(x_train, y_train)
  
  y_pred = lda.predict(x_test)
  misclassified = x_test[y_pred != y_test]

  Z_linear = lda.predict(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)

  plt.contourf(xx, yy, Z_linear, alpha=0.25)
  plt.contour(xx, yy, Z_linear, colors="black", linewidths=1)

  for idx, class_label in enumerate(classes):
    plt.scatter(
      x_test[(y_test == class_label) & (y_pred == y_test), 0],
      x_test[(y_test == class_label) & (y_pred == y_test), 1],
      color=colors[idx], marker="o", edgecolor="k", s=50, label=f"Correct Class {int(class_label)}", alpha=0.5
    )

  if len(misclassified) > 0:
    print(f"Percentage misclassified: {len(misclassified) / len(y_pred) * 100}%")
    plt.scatter(
      misclassified[:, 0],
      misclassified[:, 1],
      color="red", marker="X", s=100, edgecolor="black", label="Misclassified", linewidths=1, alpha=0.5
    )
 
  plt.title(f"{FILE_DATASET_NAME_MAP[filepath]}: 6(b) Testing Data Results")
  plt.legend()
  plt.savefig(f"dataset_{FILE_DATASET_NAME_MAP[filepath][-1]}_testing_data.png", bbox_inches="tight")
  plt.show()
  plt.close()

analyze_dataset("supervised_learning_data_3.txt")
analyze_dataset("supervised_learning_data_5.txt")
analyze_dataset("supervised_learning_data_7.txt")