import matplotlib.pyplot as plt
from .analyze import kpis
from .config import CHART_DIR

def build_charts():
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    k = kpis()

    # APR by lender (bar)
    if not k["apr_by_lender"].empty:
        ax = k["apr_by_lender"].plot(kind="bar")
        ax.set_title("Average APR by Lender")
        ax.set_ylabel("APR (%)")
        fig = ax.get_figure()
        fig.tight_layout(); fig.savefig(CHART_DIR / "apr_by_lender.png"); plt.close(fig)

    # Approval by FICO (bar)
    ax = k["approval_by_fico"].plot(kind="bar")
    ax.set_title("Approval Rate by FICO Band")
    ax.set_ylabel("Approval Rate")
    fig = ax.get_figure()
    fig.tight_layout(); fig.savefig(CHART_DIR / "approval_by_fico.png"); plt.close(fig)

    # Risk trend (line)
    ax = k["risky_by_month"].plot()
    ax.set_title("Risky Deals Over Time (DTI>0.4 or LTV>1.1)")
    ax.set_ylabel("Share of Deals")
    fig = ax.get_figure()
    fig.tight_layout(); fig.savefig(CHART_DIR / "risk_trend.png"); plt.close(fig)
