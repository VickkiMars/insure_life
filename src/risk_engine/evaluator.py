"""Actuarial evaluation metrics: Gini coefficient, Decile Lift Tables, ROC-AUC, and MAE."""

from typing import Dict, Any, List
import numpy as np

def calculate_gini(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Computes normalized Gini coefficient for actuarial loss models.
    Gini = Area between Lorenz curve of model and 45-degree line / Area of perfect model.
    """
    n = len(y_true)
    if n == 0 or np.sum(y_true) == 0:
        return 0.0

    order = np.argsort(y_pred)
    y_sorted = y_true[order]
    cum_true = np.cumsum(y_sorted) / np.sum(y_sorted)
    cum_pop = np.arange(1, n + 1) / n
    # Approximate trapezoidal area under Lorenz curve
    auc_model = np.trapz(cum_true, cum_pop)
    gini_raw = 1.0 - 2.0 * auc_model

    # Perfect model ordering
    perfect_order = np.sort(y_true)
    cum_perfect = np.cumsum(perfect_order) / np.sum(perfect_order)
    auc_perfect = np.trapz(cum_perfect, cum_pop)
    gini_max = 1.0 - 2.0 * auc_perfect

    return float(gini_raw / gini_max) if gini_max > 0 else 0.0

def calculate_roc_auc(y_true: np.ndarray, y_score: np.ndarray) -> float:
    """Computes Area Under the ROC Curve via the Mann-Whitney U test formula."""
    pos = y_score[y_true == 1]
    neg = y_score[y_true == 0]
    n_pos = len(pos)
    n_neg = len(neg)
    if n_pos == 0 or n_neg == 0:
        return 0.5

    # Efficient rank calculation
    ranks = np.argsort(np.argsort(y_score))
    rank_sum_pos = np.sum(ranks[y_true == 1]) + n_pos # 1-based ranks
    u = rank_sum_pos - (n_pos * (n_pos + 1)) / 2.0
    return float(u / (n_pos * n_neg))

def compute_decile_lift(y_true: np.ndarray, y_pred: np.ndarray) -> List[Dict[str, Any]]:
    """
    Constructs an actuarial 10-decile lift table:
    Decile 1 (Lowest predicted risk) to Decile 10 (Highest predicted risk).
    """
    n = len(y_true)
    order = np.argsort(y_pred)
    y_true_sorted = y_true[order]
    y_pred_sorted = y_pred[order]

    total_actual = float(np.sum(y_true))
    mean_actual = float(np.mean(y_true))
    decile_size = n // 10

    table = []
    cum_actual = 0.0

    for d in range(10):
        start = d * decile_size
        end = (d + 1) * decile_size if d < 9 else n
        sub_true = y_true_sorted[start:end]
        sub_pred = y_pred_sorted[start:end]

        decile_actual_sum = float(np.sum(sub_true))
        decile_actual_mean = float(np.mean(sub_true)) if len(sub_true) > 0 else 0.0
        decile_pred_mean = float(np.mean(sub_pred)) if len(sub_pred) > 0 else 0.0

        cum_actual += decile_actual_sum
        pct_spend = (decile_actual_sum / total_actual) * 100.0 if total_actual > 0 else 0.0
        cum_pct = (cum_actual / total_actual) * 100.0 if total_actual > 0 else 0.0
        lift = (decile_actual_mean / mean_actual) if mean_actual > 0 else 1.0

        table.append({
            "decile": d + 1,
            "enrollee_count": len(sub_true),
            "pred_mean_spend_ngn": round(decile_pred_mean, 2),
            "actual_mean_spend_ngn": round(decile_actual_mean, 2),
            "actual_total_spend_ngn": round(decile_actual_sum, 2),
            "spend_share_pct": round(pct_spend, 2),
            "cumulative_share_pct": round(cum_pct, 2),
            "lift_vs_portfolio": round(lift, 2)
        })

    return table

def evaluate_models(
    y_spend_true: np.ndarray,
    y_spend_pred: np.ndarray,
    y_hr_true: np.ndarray,
    y_hr_prob: np.ndarray
) -> Dict[str, Any]:
    """Generates comprehensive actuarial metrics report."""
    mae = float(np.mean(np.abs(y_spend_true - y_spend_pred)))
    rmse = float(np.sqrt(np.mean((y_spend_true - y_spend_pred) ** 2)))
    gini = calculate_gini(y_spend_true, y_spend_pred)
    roc_auc = calculate_roc_auc(y_hr_true, y_hr_prob)
    lift_table = compute_decile_lift(y_spend_true, y_spend_pred)

    # Top decile concentration
    top_decile_spend_pct = lift_table[-1]["spend_share_pct"]
    top_decile_lift = lift_table[-1]["lift_vs_portfolio"]

    return {
        "mae_ngn": round(mae, 2),
        "rmse_ngn": round(rmse, 2),
        "gini_coefficient": round(gini, 4),
        "catastrophic_roc_auc": round(roc_auc, 4),
        "top_decile_spend_capture_pct": top_decile_spend_pct,
        "top_decile_lift_factor": top_decile_lift,
        "decile_table": lift_table
    }
