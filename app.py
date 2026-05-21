import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
    .kpi-green { background: linear-gradient(135deg, #1a5e3a, #27ae60); }
    .kpi-red   { background: linear-gradient(135deg, #6b1a1a, #c0392b); }
    .kpi-purple{ background: linear-gradient(135deg, #3b1a5e, #8e44ad); }
    .kpi-amber { background: linear-gradient(135deg, #5e3d1a, #d68910); }
</style>
""", unsafe_allow_html=True)

COLORS = px.colors.qualitative.Set2
ACCENT = "#2d6a9f"


# ── 資料載入 ──────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("kaggle database.csv")
    df.columns = df.columns.str.strip()
    df["Revenue generated"] = pd.to_numeric(df["Revenue generated"], errors="coerce")
    df["Defect rates"] = pd.to_numeric(df["Defect rates"], errors="coerce")
    df["Price"] = pd.to_numeric(df["Price"], errors="coerce")
    df["Manufacturing costs"] = pd.to_numeric(df["Manufacturing costs"], errors="coerce")
    df["Shipping costs"] = pd.to_numeric(df["Shipping costs"], errors="coerce")
    df["Costs"] = pd.to_numeric(df["Costs"], errors="coerce")
    df["Number of products sold"] = pd.to_numeric(df["Number of products sold"], errors="coerce")
    df["Stock levels"] = pd.to_numeric(df["Stock levels"], errors="coerce")
    df["Production volumes"] = pd.to_numeric(df["Production volumes"], errors="coerce")
    df["Shipping times"] = pd.to_numeric(df["Shipping times"], errors="coerce")
    df["Manufacturing lead time"] = pd.to_numeric(df["Manufacturing lead time"], errors="coerce")
    df["Lead times"] = pd.to_numeric(df["Lead times"], errors="coerce")
    df["Lead time"] = pd.to_numeric(df["Lead time"], errors="coerce")
    return df


df = load_data()

# ── 側邊欄導覽 ────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📦 Supply Chain")
    st.markdown("---")
    page = st.radio(
        "選擇頁面",
        ["Executive Dashboard", "Revenue 分析", "Supplier Risk", "Operations"],
        index=0,
    )
    st.markdown("---")
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


# ═══════════════════════════════════════════════════════════
# 頁面 1 — Executive Dashboard
# ═══════════════════════════════════════════════════════════
def page_executive():
    st.title("📊 Executive Dashboard")
    st.caption("高階 KPI 總覽 · 即時篩選")

    # KPI 計算
    total_revenue = dff["Revenue generated"].sum()
    total_units = dff["Number of products sold"].sum()
    avg_defect = dff["Defect rates"].mean()
    pass_rate = (dff["Inspection results"] == "Pass").mean() * 100
    avg_shipping = dff["Shipping times"].mean()
    top_supplier = (
        dff.groupby("Supplier name")["Revenue generated"].sum().idxmax()
        if not dff.empty else "N/A"
    )

    # KPI Cards
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

    # 兩欄圖表
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

    # 底部寬圖：供應商 Revenue 矩形樹圖
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

    # 子篩選
    with st.expander("進階篩選", expanded=False):
        demo_opts = sorted(dff["Customer demographics"].dropna().unique())
        demo_sel = st.multiselect("Customer Demographics", demo_opts, default=demo_opts)
        loc_opts = sorted(dff["Location"].dropna().unique())
        loc_sel = st.multiselect("Location", loc_opts, default=loc_opts)
    local = dff[
        dff["Customer demographics"].isin(demo_sel) & dff["Location"].isin(loc_sel)
    ]

    # Row 1
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("各產品類型 Revenue 分佈")
        fig = px.box(
            local, x="Product type", y="Revenue generated",
            color="Product type", color_discrete_sequence=COLORS,
            points="outliers",
        )
        fig.update_layout(showlegend=False, height=350, margin=dict(t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("客群 Revenue 佔比")
        demo_rev = local.groupby("Customer demographics")["Revenue generated"].sum().reset_index()
        fig2 = px.bar(
            demo_rev, x="Customer demographics", y="Revenue generated",
            color="Customer demographics", color_discrete_sequence=COLORS,
            text_auto=".2s",
        )
        fig2.update_layout(showlegend=False, height=350, margin=dict(t=20, b=20))
        st.plotly_chart(fig2, use_container_width=True)

    # Row 2 — Price vs Revenue scatter
    st.subheader("Price vs Revenue（依產品類型著色）")
    fig3 = px.scatter(
        local, x="Price", y="Revenue generated",
        color="Product type", size="Number of products sold",
        hover_data=["SKU", "Supplier name", "Location"],
        color_discrete_sequence=COLORS,
        trendline="ols",
    )
    fig3.update_layout(height=400, margin=dict(t=20, b=20))
    st.plotly_chart(fig3, use_container_width=True)

    # Row 3 — Top 10 SKU
    st.subheader("Top 20 SKU by Revenue")
    top_sku = (
        local.nlargest(20, "Revenue generated")
        [["SKU", "Product type", "Revenue generated", "Number of products sold", "Price"]]
    )
    fig4 = px.bar(
        top_sku, x="SKU", y="Revenue generated",
        color="Product type", color_discrete_sequence=COLORS,
        hover_data=["Number of products sold", "Price"],
    )
    fig4.update_layout(height=350, margin=dict(t=20, b=20))
    st.plotly_chart(fig4, use_container_width=True)

    # Row 4 — Revenue by Transportation Mode
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
            x="Revenue generated", y="Routes",
            color_discrete_sequence=COLORS,
        )
        fig6.update_layout(height=300, margin=dict(t=10, b=10))
        st.plotly_chart(fig6, use_container_width=True)


# ═══════════════════════════════════════════════════════════
# 頁面 3 — Supplier Risk
# ═══════════════════════════════════════════════════════════
def page_supplier_risk():
    st.title("⚠️ Supplier Risk Analysis")
    st.caption("供應商品質、交期、成本風險全面評估")

    # Risk Score 計算：標準化 defect rate + lead time 合成分數
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

    # 歸一化 0-100
    for col in ["avg_defect", "avg_lead", "fail_rate"]:
        mn, mx = risk_df[col].min(), risk_df[col].max()
        risk_df[f"{col}_norm"] = (risk_df[col] - mn) / (mx - mn + 1e-9) * 100

    risk_df["risk_score"] = (
        risk_df["avg_defect_norm"] * 0.4
        + risk_df["avg_lead_norm"] * 0.3
        + risk_df["fail_rate_norm"] * 0.3
    )

    # Row 1 — Risk Score Bar
    st.subheader("綜合風險評分（越高越危險）")
    risk_sorted = risk_df.sort_values("risk_score", ascending=False)
    color_map = {
        r: "#c0392b" if s > 65 else ("#d68910" if s > 40 else "#27ae60")
        for r, s in zip(risk_sorted["Supplier name"], risk_sorted["risk_score"])
    }
    fig_risk = px.bar(
        risk_sorted, x="Supplier name", y="risk_score",
        color="Supplier name",
        color_discrete_map=color_map,
        text=risk_sorted["risk_score"].round(1),
    )
    fig_risk.add_hline(y=65, line_dash="dash", line_color="red", annotation_text="高風險門檻")
    fig_risk.add_hline(y=40, line_dash="dash", line_color="orange", annotation_text="中風險門檻")
    fig_risk.update_layout(showlegend=False, height=320, margin=dict(t=20, b=20))
    st.plotly_chart(fig_risk, use_container_width=True)

    # Row 2
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
            .size()
            .reset_index(name="count")
        )
        fig_i = px.bar(
            insp_df, x="Supplier name", y="count",
            color="Inspection results",
            color_discrete_map={"Pass": "#27ae60", "Fail": "#c0392b", "Pending": "#d68910"},
            barmode="stack",
        )
        fig_i.update_layout(height=300, margin=dict(t=10))
        st.plotly_chart(fig_i, use_container_width=True)

    # Row 3 — Scatter defect vs lead time
    st.subheader("Defect Rate vs Lead Time（泡泡大小 = Manufacturing Cost）")
    fig_sc = px.scatter(
        dff, x="Lead time", y="Defect rates",
        color="Supplier name", size="Manufacturing costs",
        hover_data=["SKU", "Product type", "Inspection results"],
        color_discrete_sequence=COLORS,
    )
    fig_sc.update_layout(height=380, margin=dict(t=10))
    st.plotly_chart(fig_sc, use_container_width=True)

    # Row 4 — Radar chart
    st.subheader("Supplier 多維風險雷達圖")
    cats = ["avg_defect_norm", "avg_lead_norm", "fail_rate_norm"]
    labels = ["Defect Rate", "Lead Time", "Fail Rate"]
    fig_radar = go.Figure()
    for _, row in risk_df.iterrows():
        vals = [row[c] for c in cats]
        vals += [vals[0]]  # close loop
        fig_radar.add_trace(go.Scatterpolar(
            r=vals, theta=labels + [labels[0]],
            fill="toself", name=row["Supplier name"],
        ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True, height=400, margin=dict(t=20),
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    # Risk table
    st.subheader("供應商風險明細表")
    display_cols = {
        "Supplier name": "供應商",
        "avg_defect": "Avg Defect %",
        "avg_lead": "Avg Lead Time",
        "fail_rate": "Fail Rate %",
        "avg_mfg_cost": "Avg Mfg Cost",
        "risk_score": "Risk Score",
    }
    tbl = risk_df[list(display_cols.keys())].rename(columns=display_cols)
    tbl = tbl.sort_values("Risk Score", ascending=False).reset_index(drop=True)
    for col in ["Avg Defect %", "Avg Lead Time", "Fail Rate %", "Avg Mfg Cost", "Risk Score"]:
        tbl[col] = tbl[col].round(2)
    st.dataframe(
        tbl.style.background_gradient(subset=["Risk Score"], cmap="RdYlGn_r"),
        use_container_width=True,
        hide_index=True,
    )


# ═══════════════════════════════════════════════════════════
# 頁面 4 — Operations
# ═══════════════════════════════════════════════════════════
def page_operations():
    st.title("⚙️ Operations")
    st.caption("庫存、物流、製造效率全面監控")

    # Row 1 — Stock Levels
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
            hover_data=["SKU"],
            color_discrete_sequence=COLORS,
        )
        fig_sv.update_layout(height=300, margin=dict(t=10))
        st.plotly_chart(fig_sv, use_container_width=True)

    # Row 2 — Shipping
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

    # Row 3 — Manufacturing
    st.subheader("Manufacturing Lead Time vs Production Volume（依產品類型）")
    fig_mfg = px.scatter(
        dff, x="Manufacturing lead time", y="Production volumes",
        color="Product type", size="Manufacturing costs",
        facet_col="Product type", color_discrete_sequence=COLORS,
        trendline="ols",
    )
    fig_mfg.update_layout(height=380, margin=dict(t=30))
    st.plotly_chart(fig_mfg, use_container_width=True)

    # Row 4 — Cost breakdown heatmap
    st.subheader("成本熱力圖：供應商 × 運輸方式")
    heat_df = (
        dff.groupby(["Supplier name", "Transportation modes"])["Costs"]
        .mean()
        .unstack(fill_value=0)
    )
    fig_heat = px.imshow(
        heat_df,
        color_continuous_scale="Blues",
        text_auto=".0f",
        aspect="auto",
        labels=dict(x="Transportation Mode", y="Supplier", color="Avg Cost"),
    )
    fig_heat.update_layout(height=320, margin=dict(t=10))
    st.plotly_chart(fig_heat, use_container_width=True)

    # Row 5 — Production by Location
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


# ── 頁面路由 ──────────────────────────────────────────────
if page == "Executive Dashboard":
    page_executive()
elif page == "Revenue 分析":
    page_revenue()
elif page == "Supplier Risk":
    page_supplier_risk()
elif page == "Operations":
    page_operations()
