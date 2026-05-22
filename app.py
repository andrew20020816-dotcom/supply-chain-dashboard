import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import date

st.set_page_config(
    page_title="Supply Chain Dashboard",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 全域樣式 ──────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #1e3a5f, #2d6a9f);
        border-radius: 12px;
        padding: 20px 24px;
        color: white;
        margin-bottom: 8px;
    }
    .metric-card h3 { font-size: 0.85rem; opacity: 0.85; margin: 0 0 6px 0; }
    .metric-card h1 { font-size: 2rem; margin: 0; font-weight: 700; }
    .metric-card p  { font-size: 0.78rem; opacity: 0.75; margin: 4px 0 0 0; }
    .kpi-green  { background: linear-gradient(135deg, #1a5e3a, #27ae60); }
    .kpi-red    { background: linear-gradient(135deg, #6b1a1a, #c0392b); }
    .kpi-purple { background: linear-gradient(135deg, #3b1a5e, #8e44ad); }
    .kpi-amber  { background: linear-gradient(135deg, #5e3d1a, #d68910); }
    .bom-row {
        display: grid;
        grid-template-columns: 2fr 1fr 1.6fr 1fr;
        padding: 11px 16px;
        background: #16202e;
        border-bottom: 1px solid #253245;
        align-items: center;
        font-size: 0.9rem;
    }
    .bom-header {
        display: grid;
        grid-template-columns: 2fr 1fr 1.6fr 1fr;
        padding: 8px 16px;
        background: #1a2540;
        border-radius: 8px 8px 0 0;
        font-size: 0.75rem;
        color: #6b7c99;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.2px;
    }
    .bom-table-wrap { border-radius: 8px; overflow: hidden; margin-bottom: 18px; }
</style>
""", unsafe_allow_html=True)

COLORS = px.colors.qualitative.Set2
ACCENT = "#2d6a9f"


# ── 資料載入 ──────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("kaggle database.csv")
    df.columns = df.columns.str.strip()
    for col in [
        "Revenue generated", "Defect rates", "Price", "Manufacturing costs",
        "Shipping costs", "Costs", "Number of products sold", "Stock levels",
        "Production volumes", "Shipping times", "Manufacturing lead time",
        "Lead times", "Lead time",
    ]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


df = load_data()

# ── 側邊欄導覽 ────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📦 Supply Chain")
    st.markdown("---")
    page = st.radio(
        "選擇頁面",
        ["Executive Dashboard", "Revenue 分析", "Supplier Risk", "Operations", "BOM 追蹤"],
        index=0,
    )
    st.markdown("---")

    if page != "BOM 追蹤":
        st.markdown("### 全域篩選")
        product_filter = st.multiselect(
            "產品類型",
            options=sorted(df["Product type"].dropna().unique()),
            default=sorted(df["Product type"].dropna().unique()),
        )
        supplier_filter = st.multiselect(
            "供應商",
            options=sorted(df["Supplier name"].dropna().unique()),
            default=sorted(df["Supplier name"].dropna().unique()),
        )
        dff = df[
            df["Product type"].isin(product_filter) & df["Supplier name"].isin(supplier_filter)
        ].copy()
    else:
        dff = df.copy()


# ═══════════════════════════════════════════════════════════
# 頁面 1 — Executive Dashboard
# ═══════════════════════════════════════════════════════════
def page_executive():
    st.title("📊 Executive Dashboard")
    st.caption("高階 KPI 總覽 · 即時篩選")

    total_revenue = dff["Revenue generated"].sum()
    total_units = dff["Number of products sold"].sum()
    avg_defect = dff["Defect rates"].mean()
    pass_rate = (dff["Inspection results"] == "Pass").mean() * 100
    avg_shipping = dff["Shipping times"].mean()
    top_supplier = (
        dff.groupby("Supplier name")["Revenue generated"].sum().idxmax()
        if not dff.empty else "N/A"
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>💰 Total Revenue</h3>
            <h1>${total_revenue:,.0f}</h1>
            <p>{len(dff)} SKUs 貢獻</p>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-card kpi-green">
            <h3>📦 Total Units Sold</h3>
            <h1>{total_units:,.0f}</h1>
            <p>平均 {total_units/len(dff):.0f} 件 / SKU</p>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-card kpi-purple">
            <h3>🏆 Top Supplier</h3>
            <h1>{top_supplier}</h1>
            <p>依總營收排名</p>
        </div>""", unsafe_allow_html=True)

    c4, c5, c6 = st.columns(3)
    with c4:
        color = "kpi-red" if avg_defect > 3 else "kpi-amber"
        st.markdown(f"""
        <div class="metric-card {color}">
            <h3>⚠️ Avg Defect Rate</h3>
            <h1>{avg_defect:.2f}%</h1>
            <p>{'高於警戒線 3%' if avg_defect > 3 else '在安全範圍內'}</p>
        </div>""", unsafe_allow_html=True)
    with c5:
        st.markdown(f"""
        <div class="metric-card kpi-green">
            <h3>✅ Inspection Pass Rate</h3>
            <h1>{pass_rate:.1f}%</h1>
            <p>Fail: {(dff['Inspection results']=='Fail').sum()} 筆</p>
        </div>""", unsafe_allow_html=True)
    with c6:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🚚 Avg Shipping Time</h3>
            <h1>{avg_shipping:.1f} days</h1>
            <p>最長: {dff['Shipping times'].max():.0f} 天</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Revenue by Product Type")
        rev_by_type = dff.groupby("Product type")["Revenue generated"].sum().reset_index()
        fig = px.pie(
            rev_by_type, values="Revenue generated", names="Product type",
            color_discrete_sequence=COLORS, hole=0.45,
        )
        fig.update_traces(textposition="outside", textinfo="percent+label")
        fig.update_layout(margin=dict(t=10, b=10), showlegend=False, height=280)
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.subheader("Revenue by Location")
        rev_by_loc = dff.groupby("Location")["Revenue generated"].sum().sort_values(ascending=True).reset_index()
        fig2 = px.bar(
            rev_by_loc, x="Revenue generated", y="Location", orientation="h",
            color="Revenue generated", color_continuous_scale="Blues",
        )
        fig2.update_layout(margin=dict(t=10, b=10), height=280, coloraxis_showscale=False)
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Supplier Revenue Breakdown by Product Type")
    tree_df = dff.groupby(["Supplier name", "Product type"])["Revenue generated"].sum().reset_index()
    fig3 = px.treemap(
        tree_df, path=["Supplier name", "Product type"],
        values="Revenue generated", color="Revenue generated",
        color_continuous_scale="RdBu",
    )
    fig3.update_layout(margin=dict(t=10, b=10), height=340)
    st.plotly_chart(fig3, use_container_width=True)


# ═══════════════════════════════════════════════════════════
# 頁面 2 — Revenue 分析
# ═══════════════════════════════════════════════════════════
def page_revenue():
    st.title("💰 Revenue 分析")
    st.caption("產品、客群、定價三維度深度分析")

    with st.expander("進階篩選", expanded=False):
        demo_opts = sorted(dff["Customer demographics"].dropna().unique())
        demo_sel = st.multiselect("Customer Demographics", demo_opts, default=demo_opts)
        loc_opts = sorted(dff["Location"].dropna().unique())
        loc_sel = st.multiselect("Location", loc_opts, default=loc_opts)
    local = dff[
        dff["Customer demographics"].isin(demo_sel) & dff["Location"].isin(loc_sel)
    ]

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("各產品類型 Revenue 分佈")
        fig = px.box(
            local, x="Product type", y="Revenue generated",
            color="Product type", color_discrete_sequence=COLORS, points="outliers",
        )
        fig.update_layout(showlegend=False, height=350, margin=dict(t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("客群 Revenue 佔比")
        demo_rev = local.groupby("Customer demographics")["Revenue generated"].sum().reset_index()
        fig2 = px.bar(
            demo_rev, x="Customer demographics", y="Revenue generated",
            color="Customer demographics", color_discrete_sequence=COLORS, text_auto=".2s",
        )
        fig2.update_layout(showlegend=False, height=350, margin=dict(t=20, b=20))
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Price vs Revenue（依產品類型著色）")
    fig3 = px.scatter(
        local, x="Price", y="Revenue generated",
        color="Product type", size="Number of products sold",
        hover_data=["SKU", "Supplier name", "Location"],
        color_discrete_sequence=COLORS, trendline="ols",
    )
    fig3.update_layout(height=400, margin=dict(t=20, b=20))
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Top 20 SKU by Revenue")
    top_sku = local.nlargest(20, "Revenue generated")[
        ["SKU", "Product type", "Revenue generated", "Number of products sold", "Price"]
    ]
    fig4 = px.bar(
        top_sku, x="SKU", y="Revenue generated",
        color="Product type", color_discrete_sequence=COLORS,
        hover_data=["Number of products sold", "Price"],
    )
    fig4.update_layout(height=350, margin=dict(t=20, b=20))
    st.plotly_chart(fig4, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.subheader("Revenue by Transportation Mode")
        tm_rev = local.groupby("Transportation modes")["Revenue generated"].sum().reset_index()
        fig5 = px.pie(
            tm_rev, values="Revenue generated", names="Transportation modes",
            color_discrete_sequence=COLORS, hole=0.4,
        )
        fig5.update_layout(height=300, margin=dict(t=10, b=10))
        st.plotly_chart(fig5, use_container_width=True)

    with c4:
        st.subheader("Revenue by Route")
        rt_rev = local.groupby("Routes")["Revenue generated"].sum().reset_index()
        fig6 = px.funnel(
            rt_rev.sort_values("Revenue generated", ascending=False),
            x="Revenue generated", y="Routes", color_discrete_sequence=COLORS,
        )
        fig6.update_layout(height=300, margin=dict(t=10, b=10))
        st.plotly_chart(fig6, use_container_width=True)


# ═══════════════════════════════════════════════════════════
# 頁面 3 — Supplier Risk
# ═══════════════════════════════════════════════════════════
def page_supplier_risk():
    st.title("⚠️ Supplier Risk Analysis")
    st.caption("供應商品質、交期、成本風險全面評估")

    risk_df = (
        dff.groupby("Supplier name")
        .agg(
            avg_defect=("Defect rates", "mean"),
            avg_lead=("Lead time", "mean"),
            avg_mfg_cost=("Manufacturing costs", "mean"),
            fail_count=("Inspection results", lambda x: (x == "Fail").sum()),
            total=("Inspection results", "count"),
        )
        .reset_index()
    )
    risk_df["fail_rate"] = risk_df["fail_count"] / risk_df["total"] * 100

    for col in ["avg_defect", "avg_lead", "fail_rate"]:
        mn, mx = risk_df[col].min(), risk_df[col].max()
        risk_df[f"{col}_norm"] = (risk_df[col] - mn) / (mx - mn + 1e-9) * 100

    risk_df["risk_score"] = (
        risk_df["avg_defect_norm"] * 0.4
        + risk_df["avg_lead_norm"] * 0.3
        + risk_df["fail_rate_norm"] * 0.3
    )

    st.subheader("綜合風險評分（越高越危險）")
    risk_sorted = risk_df.sort_values("risk_score", ascending=False)
    color_map = {
        r: "#c0392b" if s > 65 else ("#d68910" if s > 40 else "#27ae60")
        for r, s in zip(risk_sorted["Supplier name"], risk_sorted["risk_score"])
    }
    fig_risk = px.bar(
        risk_sorted, x="Supplier name", y="risk_score",
        color="Supplier name", color_discrete_map=color_map,
        text=risk_sorted["risk_score"].round(1),
    )
    fig_risk.add_hline(y=65, line_dash="dash", line_color="red", annotation_text="高風險門檻")
    fig_risk.add_hline(y=40, line_dash="dash", line_color="orange", annotation_text="中風險門檻")
    fig_risk.update_layout(showlegend=False, height=320, margin=dict(t=20, b=20))
    st.plotly_chart(fig_risk, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("平均 Defect Rate by Supplier")
        fig_d = px.bar(
            risk_df.sort_values("avg_defect", ascending=False),
            x="Supplier name", y="avg_defect",
            color="avg_defect", color_continuous_scale="Reds",
            text=risk_df.sort_values("avg_defect", ascending=False)["avg_defect"].round(2),
        )
        fig_d.update_layout(coloraxis_showscale=False, height=300, margin=dict(t=10))
        st.plotly_chart(fig_d, use_container_width=True)

    with c2:
        st.subheader("Inspection Results Distribution by Supplier")
        insp_df = (
            dff.groupby(["Supplier name", "Inspection results"])
            .size().reset_index(name="count")
        )
        fig_i = px.bar(
            insp_df, x="Supplier name", y="count",
            color="Inspection results",
            color_discrete_map={"Pass": "#27ae60", "Fail": "#c0392b", "Pending": "#d68910"},
            barmode="stack",
        )
        fig_i.update_layout(height=300, margin=dict(t=10))
        st.plotly_chart(fig_i, use_container_width=True)

    st.subheader("Defect Rate vs Lead Time（泡泡大小 = Manufacturing Cost）")
    fig_sc = px.scatter(
        dff, x="Lead time", y="Defect rates",
        color="Supplier name", size="Manufacturing costs",
        hover_data=["SKU", "Product type", "Inspection results"],
        color_discrete_sequence=COLORS,
    )
    fig_sc.update_layout(height=380, margin=dict(t=10))
    st.plotly_chart(fig_sc, use_container_width=True)

    st.subheader("Supplier 多維風險雷達圖")
    cats = ["avg_defect_norm", "avg_lead_norm", "fail_rate_norm"]
    labels = ["Defect Rate", "Lead Time", "Fail Rate"]
    fig_radar = go.Figure()
    for _, row in risk_df.iterrows():
        vals = [row[c] for c in cats] + [row[cats[0]]]
        fig_radar.add_trace(go.Scatterpolar(
            r=vals, theta=labels + [labels[0]],
            fill="toself", name=row["Supplier name"],
        ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True, height=400, margin=dict(t=20),
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    st.subheader("供應商風險明細表")
    display_cols = {
        "Supplier name": "供應商", "avg_defect": "Avg Defect %",
        "avg_lead": "Avg Lead Time", "fail_rate": "Fail Rate %",
        "avg_mfg_cost": "Avg Mfg Cost", "risk_score": "Risk Score",
    }
    tbl = risk_df[list(display_cols.keys())].rename(columns=display_cols)
    tbl = tbl.sort_values("Risk Score", ascending=False).reset_index(drop=True)
    for col in ["Avg Defect %", "Avg Lead Time", "Fail Rate %", "Avg Mfg Cost", "Risk Score"]:
        tbl[col] = tbl[col].round(2)
    st.dataframe(
        tbl.style.background_gradient(subset=["Risk Score"], cmap="RdYlGn_r"),
        use_container_width=True, hide_index=True,
    )


# ═══════════════════════════════════════════════════════════
# 頁面 4 — Operations
# ═══════════════════════════════════════════════════════════
def page_operations():
    st.title("⚙️ Operations")
    st.caption("庫存、物流、製造效率全面監控")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("庫存水位分佈")
        fig_stk = px.histogram(
            dff, x="Stock levels", color="Product type",
            nbins=20, barmode="overlay",
            color_discrete_sequence=COLORS, opacity=0.75,
        )
        fig_stk.update_layout(height=300, margin=dict(t=10))
        st.plotly_chart(fig_stk, use_container_width=True)

    with c2:
        st.subheader("庫存 vs 銷量 關係")
        fig_sv = px.scatter(
            dff, x="Stock levels", y="Number of products sold",
            color="Product type", size="Order quantities",
            hover_data=["SKU"], color_discrete_sequence=COLORS,
        )
        fig_sv.update_layout(height=300, margin=dict(t=10))
        st.plotly_chart(fig_sv, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.subheader("Shipping Time by Carrier")
        fig_ship = px.violin(
            dff, x="Shipping carriers", y="Shipping times",
            color="Shipping carriers", box=True, points="outliers",
            color_discrete_sequence=COLORS,
        )
        fig_ship.update_layout(showlegend=False, height=320, margin=dict(t=10))
        st.plotly_chart(fig_ship, use_container_width=True)

    with c4:
        st.subheader("Shipping Cost by Transportation Mode")
        fig_sc2 = px.box(
            dff, x="Transportation modes", y="Shipping costs",
            color="Transportation modes", points="outliers",
            color_discrete_sequence=COLORS,
        )
        fig_sc2.update_layout(showlegend=False, height=320, margin=dict(t=10))
        st.plotly_chart(fig_sc2, use_container_width=True)

    st.subheader("Manufacturing Lead Time vs Production Volume（依產品類型）")
    fig_mfg = px.scatter(
        dff, x="Manufacturing lead time", y="Production volumes",
        color="Product type", size="Manufacturing costs",
        facet_col="Product type", color_discrete_sequence=COLORS, trendline="ols",
    )
    fig_mfg.update_layout(height=380, margin=dict(t=30))
    st.plotly_chart(fig_mfg, use_container_width=True)

    st.subheader("成本熱力圖：供應商 × 運輸方式")
    heat_df = (
        dff.groupby(["Supplier name", "Transportation modes"])["Costs"]
        .mean().unstack(fill_value=0)
    )
    fig_heat = px.imshow(
        heat_df, color_continuous_scale="Blues", text_auto=".0f", aspect="auto",
        labels=dict(x="Transportation Mode", y="Supplier", color="Avg Cost"),
    )
    fig_heat.update_layout(height=320, margin=dict(t=10))
    st.plotly_chart(fig_heat, use_container_width=True)

    c5, c6 = st.columns(2)
    with c5:
        st.subheader("Production Volume by Location")
        loc_prod = dff.groupby("Location")["Production volumes"].sum().reset_index()
        fig_lp = px.bar(
            loc_prod.sort_values("Production volumes", ascending=False),
            x="Location", y="Production volumes",
            color="Location", color_discrete_sequence=COLORS, text_auto=".2s",
        )
        fig_lp.update_layout(showlegend=False, height=300, margin=dict(t=10))
        st.plotly_chart(fig_lp, use_container_width=True)

    with c6:
        st.subheader("Order Quantities by Route")
        route_oq = dff.groupby("Routes")["Order quantities"].mean().reset_index()
        fig_ro = px.bar(
            route_oq, x="Routes", y="Order quantities",
            color="Routes", color_discrete_sequence=COLORS, text_auto=".1f",
        )
        fig_ro.update_layout(showlegend=False, height=300, margin=dict(t=10))
        st.plotly_chart(fig_ro, use_container_width=True)


# ═══════════════════════════════════════════════════════════
# 頁面 5 — BOM 物料追蹤
# ═══════════════════════════════════════════════════════════
def page_bom():
    # ── BOM 資料定義 ───────────────────────────────────────
    BOM = {
        "MK2": {
            "total": 32, "ready": 26, "pending": 5, "cancelled": 0,
            "color": "#4fc3f7",
            "pending_items": [
                {"name": "Panel 新板",  "status": "transit",  "eta": "5/22 到貨", "supplier": "—"},
                {"name": "疊板擴孔",    "status": "tbc",      "eta": "TBC",       "supplier": "—"},
            ],
            "ready_items": ["RTX 5090 ×2", "R-DIMM DDR5 ×4", "CPU", "主機板", "電源 1650W", "+ 21 項"],
            "cancelled_items": [],
        },
        "GA2": {
            "total": 14, "ready": 10, "pending": 3, "cancelled": 0,
            "color": "#a5d6a7",
            "pending_items": [
                {"name": "記憶體",   "status": "tbc",     "eta": "TBC",       "supplier": "十銓"},
                {"name": "4K 螢幕", "status": "transit", "eta": "5/15 寄出", "supplier": "百事益"},
                {"name": "PCBA",    "status": "confirm", "eta": "確認數量中", "supplier": "—"},
            ],
            "ready_items": ["水冷排", "顯卡 4070 ×2", "CPU", "電源 1650W", "+ 6 項"],
            "cancelled_items": [],
        },
        "PFA": {
            "total": 13, "ready": 5, "pending": 6, "cancelled": 1,
            "color": "#ffcc80",
            "pending_items": [
                {"name": "純銅+碳基機",      "status": "transit",  "eta": "5/27 寄出", "supplier": "酷科"},
                {"name": "360水冷排+編織管", "status": "transit",  "eta": "5/22",      "supplier": "—"},
                {"name": "DDR5 記憶體",      "status": "exchange", "eta": "5/22 換貨", "supplier": "—"},
            ],
            "ready_items": ["已就緒 5 項"],
            "cancelled_items": ["純鋁"],
        },
    }

    STATUS_META = {
        "transit":   ("在  途", "#bf360c", "#3e1a0a"),
        "tbc":       ("T B C",  "#37474f", "#1a2428"),
        "confirm":   ("確認中", "#0d47a1", "#0a1929"),
        "exchange":  ("換  貨", "#4a148c", "#1c0a33"),
        "cancelled": ("取  消", "#b71c1c", "#2d0d0d"),
    }

    def badge(status: str) -> str:
        label, fg, bg = STATUS_META.get(status, ("未知", "#555", "#222"))
        return (
            f'<span style="background:{bg}; color:{fg}; border:1px solid {fg}55; '
            f'padding:3px 10px; border-radius:6px; font-size:0.77rem; '
            f'font-weight:700; letter-spacing:0.8px; white-space:nowrap;">'
            f'{label}</span>'
        )

    # ── 頁面標題 ───────────────────────────────────────────
    st.title("📋 BOM 物料追蹤 Dashboard")
    st.caption("Computex 2026 備料進度 · 即時監控")

    # ── Computex 倒數計時 ──────────────────────────────────
    today = date.today()
    computex = date(2026, 6, 3)
    days_left = (computex - today).days

    if days_left <= 7:
        urg_border, urg_text, urg_glow = "#ef5350", "#ef5350", "rgba(239,83,80,0.15)"
    elif days_left <= 14:
        urg_border, urg_text, urg_glow = "#ffa726", "#ffa726", "rgba(255,167,38,0.15)"
    else:
        urg_border, urg_text, urg_glow = "#66bb6a", "#66bb6a", "rgba(102,187,106,0.15)"

    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {urg_glow}, rgba(20,30,50,0.8));
        border: 1px solid {urg_border}66;
        border-radius: 16px;
        padding: 22px 36px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 28px;
    ">
        <div>
            <div style="font-size:0.75rem; color:#8899aa; text-transform:uppercase;
                        letter-spacing:2.5px; margin-bottom:4px;">距離 Computex 2026</div>
            <div style="font-size:0.82rem; color:#667788;">開幕日：2026 年 6 月 3 日</div>
            <div style="font-size:0.78rem; color:#556677; margin-top:2px;">展期：06 / 03 — 06 / 06</div>
        </div>
        <div style="text-align:center; padding:0 40px;">
            <span style="font-size:5rem; font-weight:900; color:{urg_text};
                         line-height:1; text-shadow:0 0 30px {urg_border}88;">{days_left}</span>
            <span style="font-size:1.4rem; font-weight:600; color:{urg_text};
                         margin-left:8px; vertical-align:middle;">天</span>
        </div>
        <div style="text-align:right;">
            <div style="font-size:0.88rem; color:#99aabb;">今日 {today.strftime('%Y / %m / %d')}</div>
            <div style="font-size:0.78rem; color:#667788; margin-top:6px;">
                {'🔴 緊急！最後衝刺' if days_left <= 7 else ('🟡 備料倒計時' if days_left <= 14 else '🟢 備料進行中')}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 三個環形進度圖 ─────────────────────────────────────
    st.subheader("各產品備料完成率")
    ring_cols = st.columns(3)

    for i, (product, data) in enumerate(BOM.items()):
        ready = data["ready"]
        total = data["total"]
        not_ready = total - ready
        pct = round(ready / total * 100)
        color = data["color"]

        with ring_cols[i]:
            fig_ring = go.Figure(go.Pie(
                labels=["就緒", "未就緒"],
                values=[ready, not_ready],
                hole=0.72,
                marker=dict(
                    colors=[color, "#1a2535"],
                    line=dict(color=["#0d1b2a"], width=2),
                ),
                textinfo="none",
                hovertemplate="%{label}: %{value} 項<extra></extra>",
                sort=False,
                direction="clockwise",
            ))
            fig_ring.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=10, b=10, l=10, r=10),
                height=200,
                showlegend=False,
                annotations=[dict(
                    text=f"<b>{pct}%</b>",
                    x=0.5, y=0.5,
                    font=dict(size=34, color=color, family="Arial Black"),
                    showarrow=False,
                )],
            )
            st.plotly_chart(fig_ring, use_container_width=True)

            cancelled_html = (
                f'&nbsp;·&nbsp;<span style="color:#ef5350;">{data["cancelled"]} 取消</span>'
                if data["cancelled"] > 0 else ""
            )
            inner_stats = (
                f'<span style="color:#66bb6a;">{ready} 就緒</span>'
                f'&nbsp;/&nbsp;{total} 項&nbsp;·&nbsp;'
                f'<span style="color:#ffa726;">{data["pending"]} 待追蹤</span>'
                + cancelled_html
            )
            stats_html = (
                f'<div style="text-align:center;padding-bottom:8px;">'
                f'<div style="font-size:1.35rem;font-weight:800;color:{color};letter-spacing:1px;">{product}</div>'
                f'<div style="font-size:0.82rem;color:#8899aa;margin-top:5px;">{inner_stats}</div>'
                f'</div>'
            )
            st.markdown(stats_html, unsafe_allow_html=True)

    st.markdown("---")

    # ── 整體橫條進度圖 ─────────────────────────────────────
    st.subheader("整體備料進度對比")

    products = list(BOM.keys())
    ready_v    = [BOM[p]["ready"]     for p in products]
    pending_v  = [BOM[p]["pending"]   for p in products]
    cancel_v   = [BOM[p]["cancelled"] for p in products]
    total_v    = [BOM[p]["total"]     for p in products]
    other_v    = [t - r - p - c for t, r, p, c in zip(total_v, ready_v, pending_v, cancel_v)]

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        name="就緒", y=products, x=ready_v, orientation="h",
        marker_color="#388e3c",
        text=ready_v, textposition="inside", insidetextanchor="middle",
        textfont=dict(color="white", size=12),
    ))
    fig_bar.add_trace(go.Bar(
        name="待追蹤", y=products, x=pending_v, orientation="h",
        marker_color="#e65100",
        text=pending_v, textposition="inside", insidetextanchor="middle",
        textfont=dict(color="white", size=12),
    ))
    if any(c > 0 for c in cancel_v):
        fig_bar.add_trace(go.Bar(
            name="取消", y=products, x=cancel_v, orientation="h",
            marker_color="#b71c1c",
            text=[str(v) if v > 0 else "" for v in cancel_v],
            textposition="inside", insidetextanchor="middle",
            textfont=dict(color="white", size=12),
        ))
    if any(o > 0 for o in other_v):
        fig_bar.add_trace(go.Bar(
            name="未分類", y=products, x=other_v, orientation="h",
            marker_color="#37474f",
            text=[str(v) if v > 0 else "" for v in other_v],
            textposition="inside", insidetextanchor="middle",
            textfont=dict(color="#aaa", size=11),
        ))

    for i, p in enumerate(products):
        pct = round(BOM[p]["ready"] / BOM[p]["total"] * 100)
        fig_bar.add_annotation(
            x=BOM[p]["total"] + 0.5, y=i,
            text=f"<b>{pct}%</b>",
            showarrow=False,
            font=dict(color="#ccd6e0", size=13),
            xanchor="left",
        )

    fig_bar.update_layout(
        barmode="stack",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=230,
        margin=dict(t=8, b=8, l=60, r=80),
        legend=dict(
            orientation="h", x=0.5, xanchor="center", y=-0.18,
            bgcolor="rgba(0,0,0,0)", font=dict(color="#aaa"),
        ),
        xaxis=dict(
            showgrid=True, gridcolor="#253245", zeroline=False,
            tickfont=dict(color="#667788"),
        ),
        yaxis=dict(
            showgrid=False, tickfont=dict(color="#ccd6e0", size=14),
        ),
        font=dict(color="#ccc"),
        bargap=0.35,
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")

    # ── 未到位物料明細（Tabs） ──────────────────────────────
    st.subheader("未到位物料明細")
    tab1, tab2, tab3 = st.tabs(["  MK2  ", "  GA2  ", "  PFA  "])

    for tab, product in zip([tab1, tab2, tab3], ["MK2", "GA2", "PFA"]):
        with tab:
            data = BOM[product]
            color = data["color"]

            # Pending items table — build as one HTML block to avoid orphan tags
            if data["pending_items"]:
                st.markdown("##### 待到位項目")
                rows_html = "".join([
                    f'<div class="bom-row">'
                    f'<span style="color:#dde6f0; font-weight:500;">◈ {item["name"]}</span>'
                    f'<span>{badge(item["status"])}</span>'
                    f'<span style="color:#8fa8c0; font-family:monospace; font-size:0.88rem;">{item["eta"]}</span>'
                    f'<span style="color:#667788; font-size:0.88rem;">{item["supplier"]}</span>'
                    f'</div>'
                    for item in data["pending_items"]
                ])
                st.markdown(
                    f'<div class="bom-table-wrap">'
                    f'<div class="bom-header">'
                    f'<span>物料名稱</span><span>狀態</span><span>預計到位</span><span>供應商</span>'
                    f'</div>{rows_html}</div>',
                    unsafe_allow_html=True,
                )

            # Cancelled items
            if data["cancelled_items"]:
                st.markdown("##### 取消項目")
                for name in data["cancelled_items"]:
                    st.markdown(f"""
                    <div style="padding:10px 16px; background:#1e0f0f;
                                border-left:3px solid #b71c1c; border-radius:4px;
                                margin-bottom:8px; color:#ef9a9a; font-size:0.9rem;
                                text-decoration:line-through; opacity:0.8;">
                        ✕ {name}
                    </div>""", unsafe_allow_html=True)

            # Ready items as tags
            st.markdown("##### 已就緒項目")
            tags_html = "".join([
                f'<span style="background:#0a2218; color:{color}; '
                f'padding:5px 14px; border-radius:20px; font-size:0.83rem; '
                f'margin:3px; display:inline-block; '
                f'border:1px solid {color}44;">{item}</span>'
                for item in data["ready_items"]
            ])
            st.markdown(
                f'<div style="padding:10px 0; line-height:2.4;">{tags_html}</div>',
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # ── 彙總 KPI ──────────────────────────────────────────
    total_items  = sum(d["total"]     for d in BOM.values())
    total_ready  = sum(d["ready"]     for d in BOM.values())
    total_pend   = sum(d["pending"]   for d in BOM.values())
    total_cancel = sum(d["cancelled"] for d in BOM.values())
    overall_pct  = round(total_ready / total_items * 100)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="metric-card">
            <h3>📦 總計物料</h3><h1>{total_items}</h1>
            <p>三個產品合計</p></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card kpi-green">
            <h3>✅ 已就緒</h3><h1>{total_ready}</h1>
            <p>整體完成率 {overall_pct}%</p></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card kpi-amber">
            <h3>⏳ 待追蹤</h3><h1>{total_pend}</h1>
            <p>需持續跟進</p></div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="metric-card kpi-red">
            <h3>❌ 取消項目</h3><h1>{total_cancel}</h1>
            <p>已從計劃移除</p></div>""", unsafe_allow_html=True)


# ── 頁面路由 ──────────────────────────────────────────────
if page == "Executive Dashboard":
    page_executive()
elif page == "Revenue 分析":
    page_revenue()
elif page == "Supplier Risk":
    page_supplier_risk()
elif page == "Operations":
    page_operations()
elif page == "BOM 追蹤":
    page_bom()
