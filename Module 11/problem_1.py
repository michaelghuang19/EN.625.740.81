import numpy as np 

training_data = np.loadtxt("hw_11_data.txt", delimiter=",")
x_1 = training_data[:, 0]
x_2 = training_data[:, 1]
c = training_data[:, 2]
# Translate lables to {-1, +1}
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

w = np.zeros(Z.shape[1])
eta = 0.01

for _ in range(1000):
  error_count = 0
  for i in range(len(y)):
    if y[i] * np.dot(w, Z[i]) <= 0:
      w += eta * y[i] * Z[i]
      error_count +=1
  if error_count == 0:
    break

accuracy = np.mean(np.where(np.dot(Z, w) >= 0, 1, -1) == y)
print("Learned weights [w0, w1, w2, w3, w4, w5]:", np.round(w, 2))
print(f"Training accuracy: {(accuracy * 100):.2f}%")