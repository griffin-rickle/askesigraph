from collections import defaultdict
from datetime import date
from typing import List, Optional

import matplotlib.pyplot as plt

from askesigraph.model.arboleaf import ArboleafRow
from askesigraph.model.myfitnesspal import MyFitnessPalData


def aggregate_daily_calories(mfp_data: MyFitnessPalData) -> dict[date, float]:
    """Aggregate total calories per day from MyFitnessPal data"""
    daily_calories = defaultdict(float)

    for entry in mfp_data.entries:
        if entry.calories:
            daily_calories[entry.date] += entry.calories

    return dict(daily_calories)


def plot_weight_and_calories(
    arboleaf_data: List[ArboleafRow],
    mfp_data: MyFitnessPalData,
    save_path: Optional[str] = None,
    start_date: Optional[date] = None,
) -> None:
    """Plot weight and calories on dual y-axes

    Args:
        arboleaf_data: List of Arboleaf weight measurements
        mfp_data: MyFitnessPal calorie data
        save_path: Optional path to save the plot
        start_date: Optional start date to filter data (inclusive)
    """
    from datetime import datetime

    # Helper function to convert datetime/date to date
    def to_date(d):
        return d.date() if isinstance(d, datetime) else d

    # Extract weight data
    weight_dates = [row.measure_time for row in arboleaf_data]
    weights = [row.weight for row in arboleaf_data]

    # Filter out None values for weight
    filtered_weight_dates = [d for d, w in zip(weight_dates, weights) if w is not None]
    filtered_weights = [w for w in weights if w is not None]

    # Apply start_date filter to weight data
    if start_date:
        filtered_data = [
            (d, w)
            for d, w in zip(filtered_weight_dates, filtered_weights)
            if to_date(d) >= start_date
        ]
        if filtered_data:
            filtered_weight_dates, filtered_weights = zip(*filtered_data)
            filtered_weight_dates = list(filtered_weight_dates)
            filtered_weights = list(filtered_weights)
        else:
            filtered_weight_dates, filtered_weights = [], []

    # Get daily calorie totals
    daily_calories = aggregate_daily_calories(mfp_data)

    # Apply start_date filter to calorie data
    if start_date:
        daily_calories = {
            d: cal for d, cal in daily_calories.items() if d >= start_date
        }

    calorie_dates = sorted(daily_calories.keys())
    calorie_values = [daily_calories[d] for d in calorie_dates]

    # Create figure and primary axis
    fig, ax1 = plt.subplots(figsize=(14, 6))

    # Plot weight on primary y-axis (left)
    color = "tab:blue"
    ax1.set_xlabel("Date", fontsize=12)
    ax1.set_ylabel("Weight (lb)", color=color, fontsize=12)
    ax1.plot(
        filtered_weight_dates,
        filtered_weights,
        color=color,
        linewidth=2,
        label="Weight",
    )
    ax1.tick_params(axis="y", labelcolor=color)
    ax1.tick_params(axis="x", rotation=45, labelsize=10)
    ax1.grid(True, alpha=0.3)

    # Create secondary y-axis (right) for calories
    ax2 = ax1.twinx()
    color = "tab:orange"
    ax2.set_ylabel("Calories (kcal)", color=color, fontsize=12)
    ax2.plot(
        calorie_dates,
        calorie_values,
        color=color,
        linewidth=2,
        alpha=0.7,
        label="Calories",
    )
    ax2.tick_params(axis="y", labelcolor=color)

    # Add title and legends
    title = "Weight and Calorie Intake Over Time"
    if start_date:
        title += f' (from {start_date.strftime("%Y-%m-%d")})'
    plt.title(title, fontsize=14, fontweight="bold", pad=20)

    # Combine legends from both axes
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")

    plt.show()
