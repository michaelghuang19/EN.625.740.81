import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm

data = np.loadtxt("polynomial_data.txt")

N_VALUES = [3, 4, 5, 6]

x_data = data[:, 0]
y_data = data[:, 1]

def poly_function(x_data, n):
  """Build the corresponding matrix by stacking 1, x, x^2, etc."""
  return np.column_stack(
    [x_data**k for k in range(n + 1)]
  )

fit_results = []
result_summaries = []

for n in N_VALUES:
  fit_result = sm.OLS(y_data, poly_function(x_data, n)).fit()
  fit_results.append(fit_result)

  result_summaries.append({
    "n": n,
    "rss": fit_result.ssr,
    "rse": np.sqrt(fit_result.scale),
    "adj_r_2": fit_result.rsquared_adj,
  })

result_summary_df = pd.DataFrame(result_summaries).set_index("n").round(5)
print(result_summary_df)

# n = 5 seems good enough, so plot and see
plt.scatter(x_data, y_data)
x_series = np.linspace(min(x_data), max(x_data), 100)
# Index 2 in fit_results since n_values = [3, 4, 5, 6]
plt.plot(x_series, fit_results[2].predict(poly_function(x_series, 5)), color="red")
plt.xlabel("x")
plt.ylabel("y")
plt.title("Fit for n = 5")
plt.show()

# Print RSE as noise estimation for n = 5
sigma = np.sqrt(fit_results[2].scale)
print(f"Estimated noise standard deviation: {sigma}")
print(f"Estimated noise variance: {sigma**2}")