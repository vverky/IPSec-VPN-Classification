import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys

# =============================
# Step 1: Custom evaluation function (MAE and RMSE only)
# =============================
def evaluate_model(pred_path, true_path, columns=None):
    try:
        pred_df = pd.read_csv(pred_path)
        true_df = pd.read_csv(true_path, sep='|', engine='python', quotechar='"')
    except FileNotFoundError as e:
        print(f"File reading error: {e}")
        return None

    # Get common column names (case insensitive)
    common_cols = [col for col in pred_df.columns
                   if col.lower() in (c.lower() for c in true_df.columns)]

    if columns is not None:
        valid_cols = [col for col in columns if col in common_cols]
        if not valid_cols:
            print(f"Warning: Specified columns {columns} not found in common columns")
            return None
    else:
        valid_cols = common_cols

    # Extract aligned data
    aligned_true = true_df[valid_cols].reset_index(drop=True)
    aligned_pred = pred_df[valid_cols].reset_index(drop=True)

    # Handle data length mismatch
    if len(aligned_true) != len(aligned_pred):
        print(f"Warning: Data length mismatch (True: {len(aligned_true)}, Pred: {len(aligned_pred)})")
        min_len = min(len(aligned_true), len(aligned_pred))
        aligned_true = aligned_true.iloc[:min_len]
        aligned_pred = aligned_pred.iloc[:min_len]

    metrics = {}
    for col in valid_cols:
        try:
            y_true = pd.to_numeric(aligned_true[col], errors='coerce').dropna()
            y_pred = pd.to_numeric(aligned_pred[col], errors='coerce').dropna()

            # Ensure equal length
            min_len = min(len(y_true), len(y_pred))
            y_true = y_true.iloc[:min_len]
            y_pred = y_pred.iloc[:min_len]

            # Calculate only MAE and RMSE
            metrics[col] = {
                'MAE': mean_absolute_error(y_true, y_pred),
                'RMSE': mean_squared_error(y_true, y_pred, squared=False)
            }
        except Exception as e:
            print(f"Error calculating metrics for column {col}: {e}")
            continue

    return metrics

# =============================
# Step 2: Configuration and evaluation (single model)
# =============================
traffic_types = ['web', 'ftp', 'im']
model = '1'  # Only evaluating one model
columns_to_compare = ['plaintext_header_length', 'padding_length']

all_results = []

for traffic in traffic_types:
    pred_file = f'{traffic}_{model}_pred.csv'
    true_file = f'{traffic}_true.csv'

    if not os.path.exists(pred_file):
        print(f"Warning: Prediction file not found {pred_file}")
        continue
    if not os.path.exists(true_file):
        print(f"Warning: Ground truth file not found {true_file}")
        continue

    scores = evaluate_model(pred_file, true_file, columns_to_compare)
    if scores is None:
        continue

    for col, metrics in scores.items():
        row = {
            'Traffic': traffic,
            'Field': col,
            **metrics
        }
        all_results.append(row)

if not all_results:
    print("Error: No results generated, please check input files")
    sys.exit(1)

results_df = pd.DataFrame(all_results)

# =============================
# Step 3: Visualization and output
# =============================

# Create a summary table
summary_table = results_df.pivot_table(
    index=['Traffic', 'Field'],
    values=['MAE', 'RMSE']
).round(4)

print("\n📊 Model Error Metrics (MAE & RMSE):\n")
print(summary_table)

# Visualization
plt.figure(figsize=(12, 6))

# Create a melted dataframe for easier plotting
melted_df = results_df.melt(
    id_vars=['Traffic', 'Field'],
    value_vars=['MAE', 'RMSE'],
    var_name='Metric',
    value_name='Value'
)

# Create bar plot
ax = sns.barplot(
    data=melted_df,
    x='Traffic',
    y='Value',
    hue='Field',
    palette='viridis',
)

# Add annotations and formatting
plt.title('Model Performance (MAE & RMSE) by Traffic Type and Field')
plt.ylabel('Error Value')
plt.xlabel('Traffic Type')
plt.legend(title='Field', bbox_to_anchor=(1.05, 1), loc='upper left')

# Rotate x-axis labels if needed
plt.xticks(rotation=45)

# Save the plot
os.makedirs('plots', exist_ok=True)
plt.savefig("plots/mae_rmse_comparison.png", dpi=300, bbox_inches='tight')
plt.close()

# Save results
try:
    with pd.ExcelWriter("single_model_results.xlsx", engine='openpyxl') as writer:
        summary_table.to_excel(writer, sheet_name='Summary')
        results_df.to_excel(writer, sheet_name='Raw Data')
    results_df.to_csv("single_model_results.csv", index=False)
    print("\n✅ Results saved to single_model_results.xlsx and single_model_results.csv")
except Exception as e:
    print(f"Error saving results: {e}")
    try:
        results_df.to_csv("single_model_results.csv", index=False)
        print("Partial results saved to single_model_results.csv")
    except Exception as e:
        print(f"Failed to save any results: {e}")