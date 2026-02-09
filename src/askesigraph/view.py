from typing import List, Optional

import matplotlib.pyplot as plt

from askesigraph.ingest import ArboleafRow


def plot_body_metrics(data: List[ArboleafRow], save_path: Optional[str] = None) -> None:
    dates = [row.measure_time for row in data]

    # Define metrics to plot (excluding non-numeric and device info)
    metrics = [
        ("weight", "Weight (lb)", "Weight Over Time"),
        ("body_fat", "Body Fat (%)", "Body Fat Percentage"),
        ("bmi", "BMI", "BMI"),
        ("skeletal_muscle", "Skeletal Muscle (%)", "Skeletal Muscle Percentage"),
        ("muscle_mass", "Muscle Mass (lb)", "Muscle Mass"),
        ("protein", "Protein (%)", "Protein Percentage"),
        ("bmr", "BMR (kcal)", "Basal Metabolic Rate"),
        ("fat_free_body_weight", "Fat-free Weight (lb)", "Fat-free Body Weight"),
        ("subcutaneous_fat", "Subcutaneous Fat (%)", "Subcutaneous Fat"),
        ("visceral_fat", "Visceral Fat Level", "Visceral Fat"),
        ("body_water", "Body Water (%)", "Body Water Percentage"),
        ("bone_mass", "Bone Mass (lb)", "Bone Mass"),
        ("metabolic_age", "Metabolic Age", "Metabolic Age"),
    ]

    # Create a grid of subplots
    fig, axes = plt.subplots(5, 3, figsize=(15, 18))
    axes = axes.flatten()

    for idx, (field, ylabel, title) in enumerate(metrics):
        values = [getattr(row, field) for row in data]

        # Filter out None values
        filtered_dates = [d for d, v in zip(dates, values) if v is not None]
        filtered_values = [v for v in values if v is not None]

        if filtered_values:  # Only plot if there's data
            axes[idx].plot(filtered_dates, filtered_values, linewidth=1)
            axes[idx].set_title(title, fontsize=10, fontweight="bold")
            axes[idx].set_ylabel(ylabel, fontsize=9)
            axes[idx].tick_params(axis="x", rotation=45, labelsize=8)
            axes[idx].tick_params(axis="y", labelsize=8)
            axes[idx].grid(True, alpha=0.3)

    # Hide unused subplots
    for idx in range(len(metrics), len(axes)):
        axes[idx].set_visible(False)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")

    plt.show()
