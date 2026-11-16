"""Regenerate the themed timeseries images used in docs/timeseries/getting-started.md."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

from pyfake import Timeseries

OUT = Path(__file__).resolve().parent.parent / "docs" / "assets"
ACCENT = "#ff6d00"

THEMES = {
    "light": {"bg": "#ffffff", "fg": "#1f2328", "muted": "#6b7280", "grid": "#e5e7eb"},
    "dark": {"bg": "#1e2129", "fg": "#e6e8eb", "muted": "#9aa0aa", "grid": "#2e323c"},
}

ts = Timeseries(
    start="2024-01-01",
    periods=180,
    freq="day",
    baseline=100.0,
    trend={"type": "upward", "slope": 0.4},
    noise=2.0,
    seasonality={"type": "week", "amplitude": 6},
    anomalies={"type": "spike", "count": 3, "magnitude": 0.25},
    seed=7,
)
data = ts.generate()
x = [d for d, _ in data]
y = [float(v) for _, v in data]

for name, c in THEMES.items():
    fig, ax = plt.subplots(figsize=(10, 3.8), dpi=200)
    fig.patch.set_facecolor(c["bg"])
    ax.set_facecolor(c["bg"])

    ax.plot(x, y, color=ACCENT, linewidth=1.8, solid_capstyle="round")
    ax.fill_between(x, y, min(y) - 5, color=ACCENT, alpha=0.12, linewidth=0)

    ax.set_ylim(min(y) - 5, max(y) + 5)
    ax.set_xlim(x[0], x[-1])
    ax.grid(axis="y", color=c["grid"], linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(c["grid"])
    ax.tick_params(colors=c["muted"], length=0, labelsize=9)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.set_title(
        "pyfake Timeseries",
        loc="left",
        color=c["fg"],
        fontsize=12,
        fontweight="bold",
        pad=12,
    )

    fig.tight_layout()
    fig.savefig(OUT / f"timeseries-{name}.png", facecolor=c["bg"])
    plt.close(fig)
