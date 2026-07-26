# 🏭 Supply Chain Dashboard — Computex 2026 BOM Tracking

A real-world supply chain dashboard built with Python and Streamlit,  
tracking BOM material readiness for ENERMAX's Computex 2026 exhibition.

## 🎯 Business Problem

Hardware product launches require precise material coordination  
across multiple suppliers. This dashboard provides real-time visibility  
into BOM completion rates, supplier risk, and operational bottlenecks  
— enabling proactive intervention before critical deadlines.

## 📊 Dashboard Pages

| Page | Description |
|------|-------------|
| Executive Dashboard | High-level KPIs and overall readiness |
| Revenue Analysis | Product revenue breakdown |
| Supplier Risk | Supplier concentration and delay tracking |
| Operations | Operational metrics |
| BOM Tracking | Real-time material completion by product |

## 🔍 Key Insights

- Tracked **59 BOM items** across 3 products (MK2 / GA2 / PFA)
- MK2 achieved **81% completion** (26/32 items)
- Identified **6 at-risk PFA items** requiring supplier follow-up
- Enabled data-driven prioritization in final weeks before Computex

## 🛠 Tech Stack

- **Python** — Data processing and logic
- **Streamlit** — Interactive web dashboard
- **Pandas** — Data manipulation
- **Plotly** — Data visualization

## 🚀 Live Demo

[View Dashboard](https://supply-chain-dashboard-xdg7rzapfgw5fynx2waxwt.streamlit.app)

## 📁 Project Structure

supply-chain-dashboard/
├── app.py              # Main Streamlit application
├── kaggle database.csv # Supply chain dataset
├── requirements.txt    # Python dependencies
└── README.md          # Project documentation

## 👤 Author

**Andrew Chien (簡楨庭)**  
Hardware PM | Warwick WMG SCM (Sep 2026)  
[LinkedIn](https://linkedin.com/in/your-profile)
