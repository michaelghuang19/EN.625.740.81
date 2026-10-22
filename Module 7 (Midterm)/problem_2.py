import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm

data = np.loadtxt("midterm_exam_data.txt")

x_data = data[:, 0]
y_data = data[:, 1]

def cos_function(x_data, n):
  """BUild the corresponding matrix by stacking 1, cos(x), etc."""
  return np.column_stack(
    [np.ones_like(x_data)] + 
    [np.cos(k * x_data) for k in range(1, n + 1)]
  )

# Try for n-values up to 10
fit_results = []
result_summaries = []
for n in range(0, 11):
  fit_result = sm.OLS(y_data, cos_function(x_data, n)).fit()
  fit_results.append(fit_result)

  result_summaries.append({
    "n": n,
    "rss": fit_result.ssr,
    "rse": np.sqrt(fit_result.scale),
    "adj_r_2": fit_result.rsquared_adj,
  })

result_summary_df = pd.DataFrame(result_summaries).set_index("n").round(5)
print(result_summary_df)

# n = 5 seems reasonable, so plot and see
plt.scatter(x_data, y_data)
x_series = np.linspace(0, 3.5, 100)
plt.plot(x_series, fit_results[5].predict(cos_function(x_series, 5)), color="red")
plt.xlabel("x")
plt.ylabel("y")
plt.title("Residual plot for n = 5")
plt.show()

# Print RSE as noise estimation 
sigma = np.sqrt(fit_results[5].scale)
print(f"Estimated noise standard deviation: {sigma}")
print(f"Estimated noise variance: {sigma**2}")