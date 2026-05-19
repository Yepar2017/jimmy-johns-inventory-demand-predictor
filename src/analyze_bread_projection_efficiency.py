from pathlib import Path

import pandas as pd

DAILY_PATH = Path("data/processed/daily_sales_2025.csv")
WEEKLY_PATH = Path("data/processed/bread_weekly_2025.csv")
OUT_PATH = Path("data/processed/bread_projection_efficiency_2025.csv")
FROZEN_TRAY_BREADS = 12


def main():
    daily = pd.read_csv(DAILY_PATH, parse_dates=["date"])
    weekly = pd.read_csv(WEEKLY_PATH)

    start_date = pd.Timestamp("2025-01-01")
    daily = daily[
        (daily["date"] >= start_date)
        & (daily["date"] < start_date + pd.Timedelta(days=7 * 40))
    ].copy()
    daily["week"] = ((daily["date"] - start_date).dt.days // 7) + 1

    projected = (
        daily.groupby("week", as_index=False)
        .agg(
            projected_am=("bread_am_projection", "sum"),
            projected_pm=("bread_pm_projection", "sum"),
            projected_total=("bread_total_projection", "sum"),
            total_sales=("total_sales", "sum"),
        )
    )

    comparison = projected.merge(weekly, on="week", how="inner")
    comparison["projected_breads"] = (
        comparison["projected_total"] * FROZEN_TRAY_BREADS
    )
    comparison["projected_vs_actual_usage"] = (
        comparison["projected_breads"] - comparison["actual_usage"]
    )
    comparison["projected_vs_theoretical_usage"] = (
        comparison["projected_breads"] - comparison["theoretical_usage"]
    )
    comparison["projected_vs_actual_usage_$"] = (
        comparison["projected_vs_actual_usage"]
        * comparison["usage_variance_$"]
        / comparison["usage_variance"]
    )
    comparison["unused_breads_from_usage_variance"] = -comparison["usage_variance"]
    comparison["unused_breads_$"] = -comparison["usage_variance_$"]
    comparison["projected_unused_breads_vs_theoretical"] = (
        comparison["projected_breads"] - comparison["theoretical_usage"]
    )
    comparison["projected_unused_gap"] = (
        comparison["projected_unused_breads_vs_theoretical"]
        - comparison["unused_breads_from_usage_variance"]
    )

    comparison["actual_per_projected_unit"] = (
        comparison["actual_usage"] / comparison["projected_total"]
    )
    comparison["theoretical_per_projected_unit"] = (
        comparison["theoretical_usage"] / comparison["projected_total"]
    )
    comparison["usage_variance_per_projected_unit"] = (
        comparison["usage_variance"] / comparison["projected_total"]
    )

    theoretical_scale = comparison["theoretical_per_projected_unit"].mean()
    comparison["projected_as_theoretical_usage"] = (
        comparison["projected_total"] * theoretical_scale
    )
    comparison["projected_vs_theoretical_error"] = (
        comparison["projected_as_theoretical_usage"] - comparison["theoretical_usage"]
    )
    comparison["projected_vs_actual_error"] = (
        comparison["projected_as_theoretical_usage"] - comparison["actual_usage"]
    )

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    comparison.to_csv(OUT_PATH, index=False)

    print(f"Saved: {OUT_PATH}")
    print(f"Weeks compared: {len(comparison)}")
    print(f"Frozen tray conversion: 1 tray = {FROZEN_TRAY_BREADS} breads")
    print(f"Average projected breads: {comparison['projected_breads'].mean():.2f}")
    print(f"Average actual usage: {comparison['actual_usage'].mean():.2f}")
    print(
        "Average unused breads from usage variance: "
        f"{comparison['unused_breads_from_usage_variance'].mean():.2f}"
    )
    print(f"Average unused breads cost: ${comparison['unused_breads_$'].mean():.2f}")
    print(f"Average projected vs actual usage: {comparison['projected_vs_actual_usage'].mean():.2f}")
    print(
        "Average projected vs theoretical usage: "
        f"{comparison['projected_vs_theoretical_usage'].mean():.2f}"
    )
    print(f"Average actual usage per projected unit: {comparison['actual_per_projected_unit'].mean():.2f}")
    print(
        "Average theoretical usage per projected unit: "
        f"{comparison['theoretical_per_projected_unit'].mean():.2f}"
    )
    print("\nCorrelation matrix:")
    print(
        comparison[
            [
                "projected_total",
                "projected_breads",
                "actual_usage",
                "theoretical_usage",
                "usage_variance",
                "usage_variance_$",
                "unused_breads_from_usage_variance",
                "unused_breads_$",
            ]
        ]
        .corr(numeric_only=True)
        .round(3)
    )
    print("\nFirst 10 rows:")
    print(
        comparison[
            [
                "week",
                "projected_total",
                "projected_breads",
                "actual_usage",
                "theoretical_usage",
                "projected_vs_actual_usage",
                "projected_vs_theoretical_usage",
                "usage_variance",
                "usage_variance_$",
                "unused_breads_from_usage_variance",
                "unused_breads_$",
                "actual_per_projected_unit",
                "theoretical_per_projected_unit",
            ]
        ]
        .head(10)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
