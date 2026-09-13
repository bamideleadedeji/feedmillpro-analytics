import io
import streamlit as st
import pandas as pd
import numpy as np
from weasyprint import HTML

# ---------------------------------------------------------
# Page Configuration & Header
# ---------------------------------------------------------
st.set_page_config(
    page_title="FeedMillPro Analytics | Feed Manufacturing SaaS",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🏭 FeedMillPro Enterprise SaaS")
st.caption("Commercial Feed Formulation, Milling Unit Economics & Profitability Engine")
st.markdown("---")

# ---------------------------------------------------------
# Sidebar Inputs
# ---------------------------------------------------------
st.sidebar.header("📋 Production Batch Setup")

feed_type = st.sidebar.selectbox(
    "Select Feed Formulation Type",
    ["Broiler Starter", "Broiler Finisher", "Layer Mash", "Grower Mash", "Aquafeed / Fish Feed"]
)

currency = st.sidebar.selectbox("Currency", ["₦ (NGN)", "$ (USD)", "£ (GBP)", "€ (EUR)"])
target_tonnage = st.sidebar.number_input("Target Production Batch (Metric Tons)", min_value=1.0, max_value=500.0, value=25.0, step=5.0)
bag_size_kg = st.sidebar.selectbox("Bag Packaging Size (kg)", [25, 50, 100], index=0)
shrinkage_loss_pct = st.sidebar.slider("Processing Shrinkage & Moisture Loss (%)", min_value=0.5, max_value=5.0, value=1.5, step=0.1)

st.sidebar.markdown("---")
st.sidebar.header("🌽 Raw Material Input Prices (per Metric Ton)")

# Default Formulation Inclusions & Raw Material Pricing Defaults
if "Broiler Starter" in feed_type:
    def_maize_pct, def_soya_pct, def_offal_pct, def_premix_pct, def_other_pct = 50.0, 32.0, 10.0, 3.0, 5.0
elif "Broiler Finisher" in feed_type:
    def_maize_pct, def_soya_pct, def_offal_pct, def_premix_pct, def_other_pct = 55.0, 25.0, 12.0, 3.0, 5.0
elif "Layer Mash" in feed_type:
    def_maize_pct, def_soya_pct, def_offal_pct, def_premix_pct, def_other_pct = 48.0, 18.0, 18.0, 4.0, 12.0 # Higher limestone/bone meal
else:
    def_maize_pct, def_soya_pct, def_offal_pct, def_premix_pct, def_other_pct = 52.0, 20.0, 20.0, 3.0, 5.0

maize_price_ton = st.sidebar.number_input(f"Maize Price / Ton ({currency})", min_value=0.0, value=450000.0, step=5000.0)
soya_price_ton = st.sidebar.number_input(f"Soya Meal Price / Ton ({currency})", min_value=0.0, value=780000.0, step=5000.0)
offal_price_ton = st.sidebar.number_input(f"Wheat Offal Price / Ton ({currency})", min_value=0.0, value=220000.0, step=2500.0)
premix_price_ton = st.sidebar.number_input(f"Premix & Additives Price / Ton ({currency})", min_value=0.0, value=1800000.0, step=25000.0)
other_price_ton = st.sidebar.number_input(f"Limestone / Bone Meal Price / Ton ({currency})", min_value=0.0, value=150000.0, step=2500.0)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Milling, Packaging & Operational Overhead")

empty_bag_unit_cost = st.sidebar.number_input(f"Empty Printed Woven Bag Cost ({currency})", min_value=0.0, value=250.0, step=10.0)
power_diesel_cost = st.sidebar.number_input(f"Generator Diesel & Power Total ({currency})", min_value=0.0, value=180000.0, step=5000.0)
mill_labor_wages = st.sidebar.number_input(f"Milling & Loading Labor Total ({currency})", min_value=0.0, value=120000.0, step=5000.0)
maintenance_wear = st.sidebar.number_input(f"Machine Wear & Facility Rent ({currency})", min_value=0.0, value=75000.0, step=2500.0)

st.sidebar.markdown("---")
st.sidebar.header("💰 Commercial Selling Prices")

wholesale_price_per_bag = st.sidebar.number_input(f"Wholesale Selling Price per Bag ({currency})", min_value=0.0, value=18500.0, step=250.0)

# ---------------------------------------------------------
# Core Analytical Engine
# ---------------------------------------------------------
# Inclusion ratios check
total_inclusion_pct = def_maize_pct + def_soya_pct + def_offal_pct + def_premix_pct + def_other_pct

raw_cost_per_ton = (
    (def_maize_pct / 100.0 * maize_price_ton) +
    (def_soya_pct / 100.0 * soya_price_ton) +
    (def_offal_pct / 100.0 * offal_price_ton) +
    (def_premix_pct / 100.0 * premix_price_ton) +
    (def_other_pct / 100.0 * other_price_ton)
)

total_raw_material_cost = raw_cost_per_ton * target_tonnage
theoretical_bags = (target_tonnage * 1000) / bag_size_kg
actual_bags_produced = theoretical_bags * (1.0 - (shrinkage_loss_pct / 100.0))
total_packaging_cost = actual_bags_produced * empty_bag_unit_cost

total_milling_overhead = power_diesel_cost + mill_labor_wages + maintenance_wear
total_production_cost = total_raw_material_cost + total_packaging_cost + total_milling_overhead

production_cost_per_ton = total_production_cost / target_tonnage
production_cost_per_bag = total_production_cost / actual_bags_produced if actual_bags_produced > 0 else 0

gross_revenue = actual_bags_produced * wholesale_price_per_bag
net_profit = gross_revenue - total_production_cost
net_margin_pct = (net_profit / gross_revenue * 100) if gross_revenue > 0 else 0
breakeven_bag_price = production_cost_per_bag

# Cost Breakdown Table Data
df_feed_costs = pd.DataFrame({
    "Expense Category": [
        "Raw Materials (Grains & Concentrates)", 
        "Packaging (Printed Bags)", 
        "Energy & Milling Power (Diesel/Elec)", 
        "Labor & Mill Operations", 
        "Machine Wear & Facility Rent"
    ],
    "Total Batch Cost": [
        total_raw_material_cost, 
        total_packaging_cost, 
        power_diesel_cost, 
        mill_labor_wages, 
        maintenance_wear
    ],
    "Cost per Bag": [
        total_raw_material_cost / actual_bags_produced,
        total_packaging_cost / actual_bags_produced,
        power_diesel_cost / actual_bags_produced,
        mill_labor_wages / actual_bags_produced,
        maintenance_wear / actual_bags_produced
    ]
})
df_feed_costs["Share of Budget"] = (df_feed_costs["Total Batch Cost"] / total_production_cost) * 100

# ---------------------------------------------------------
# PDF Generator Function for Feedmillers
# ---------------------------------------------------------
def generate_feedmill_pdf(feed_type, target_tonnage, actual_bags_produced, bag_size_kg,
                          total_production_cost, gross_revenue, net_profit, 
                          production_cost_per_bag, breakeven_bag_price, currency, df_costs):
    table_rows = ""
    for _, row in df_costs.iterrows():
        table_rows += f"""
        <tr>
            <td>{row['Expense Category']}</td>
            <td class="text-right">{currency} {row['Total Batch Cost']:,.2f}</td>
            <td class="text-right">{currency} {row['Cost per Bag']:,.2f}</td>
            <td class="text-right">{row['Share of Budget']:.1f}%</td>
        </tr>
        """

    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            @page {{ size: A4; margin: 15mm 12mm; }}
            body {{ font-family: 'Helvetica Neue', Arial, sans-serif; color: #1a202c; font-size: 10pt; }}
            .header {{ background-color: #065f46; color: white; padding: 20px; border-radius: 6px; margin-bottom: 20px; }}
            .header h1 {{ margin: 0 0 5px 0; font-size: 18pt; }}
            .header p {{ margin: 0; opacity: 0.85; font-size: 9.5pt; }}
            .kpi-table {{ width: 100%; border-collapse: separate; border-spacing: 8px; margin-bottom: 15px; }}
            .kpi-card {{ background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 6px; padding: 10px; text-align: center; }}
            .kpi-value {{ font-size: 13pt; font-weight: bold; color: #065f46; margin-top: 4px; }}
            .kpi-label {{ font-size: 8pt; color: #475569; text-transform: uppercase; }}
            table.data-table {{ width: 100%; border-collapse: collapse; margin-top: 15px; margin-bottom: 20px; }}
            table.data-table th, table.data-table td {{ padding: 8px 10px; text-align: left; border-bottom: 1px solid #e2e8f0; }}
            table.data-table th {{ background-color: #f1f5f9; color: #334155; font-size: 9pt; font-weight: bold; }}
            .text-right {{ text-align: right; }}
            .summary-box {{ background-color: #f0fdf4; border-left: 4px solid #16a34a; padding: 12px 15px; margin-top: 20px; }}
            .summary-box h3 {{ margin: 0 0 5px 0; color: #15803d; font-size: 11pt; }}
            .summary-box p {{ margin: 0; color: #166534; font-size: 9.5pt; line-height: 1.4; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🏭 FeedMillPro Batch Feasibility Report</h1>
            <p>Feed Milling Unit Economics & Formulation Audit | Enterprise SaaS Summary</p>
        </div>
        <table class="kpi-table">
            <tr>
                <td class="kpi-card" width="25%"><div class="kpi-label">Formulation Profile</div><div class="kpi-value">{feed_type}</div></td>
                <td class="kpi-card" width="25%"><div class="kpi-label">Bags Produced</div><div class="kpi-value">{int(actual_bags_produced):,} ({bag_size_kg}kg)</div></td>
                <td class="kpi-card" width="25%"><div class="kpi-label">Total Production Cost</div><div class="kpi-value">{currency} {total_production_cost:,.2f}</div></td>
                <td class="kpi-card" width="25%"><div class="kpi-label">Projected Net Profit</div><div class="kpi-value">{currency} {net_profit:,.2f}</div></td>
            </tr>
        </table>
        <h3 style="color: #065f46; border-bottom: 2px solid #e2e8f0;">Itemized Feed Milling Budget</h3>
        <table class="data-table">
            <thead>
                <tr><th>Expense Category</th><th class="text-right">Total Amount ({currency})</th><th class="text-right">Cost / Bag ({currency})</th><th class="text-right">Share of Budget</th></tr>
            </thead>
            <tbody>{table_rows}</tbody>
        </table>
        <div class="summary-box">
            <h3>Key Milling Indicators</h3>
            <p>
                • <strong>Production Batch Volume:</strong> {target_tonnage} Metric Tons ({int(actual_bags_produced):,} sellable bags)<br>
                • <strong>Production Cost per Bag:</strong> {currency} {production_cost_per_bag:,.2f}<br>
                • <strong>Break-Even Selling Price:</strong> {currency} {breakeven_bag_price:,.2f}<br>
                • <strong>Shrinkage & Processing Loss Allowance:</strong> {shrinkage_loss_pct:.1f}%
            </p>
        </div>
    </body>
    </html>
    """
    return HTML(string=html_template).write_pdf()

# ---------------------------------------------------------
# Dashboard Layout
# ---------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Batch Yield", f"{int(actual_bags_produced):,} Bags", f"{target_tonnage} Tons ({bag_size_kg}kg)")
col2.metric("Total Milling Cost", f"{currency} {total_production_cost:,.2f}")
col3.metric("Gross Revenue", f"{currency} {gross_revenue:,.2f}")
col4.metric("Net Profit", f"{currency} {net_profit:,.2f}", f"{net_margin_pct:.1f}% Margin")

st.markdown("---")

tab1, tab2, tab3 = st.tabs(["📊 Formulation KPIs", "📑 Budget Breakdown & Exports", "📉 Raw Material Sensitivity Matrix"])

with tab1:
    st.subheader("Key Milling Performance Indicators")
    kpi1, kpi2, kpi3 = st.columns(3)
    with kpi1:
        st.metric("Production Cost / Metric Ton", f"{currency} {production_cost_per_ton:,.2f}")
        st.caption("Combined cost of raw ingredients, energy, packaging, and labor.")
    with kpi2:
        st.metric(f"Production Cost / {bag_size_kg}kg Bag", f"{currency} {production_cost_per_bag:,.2f}")
        st.caption("Net cost to manufacture one finished, sellable bag.")
    with kpi3:
        st.metric("Break-Even Selling Price", f"{currency} {breakeven_bag_price:,.2f}")
        st.caption("Minimum wholesale price required to avoid a financial loss.")

with tab2:
    st.subheader("Itemized Feed Milling Budget Distribution")
    c1, c2 = st.columns([2, 1])
    with c1:
        st.dataframe(df_feed_costs.style.format({
            "Total Batch Cost": f"{currency} {{:,.2f}}",
            "Cost per Bag": f"{currency} {{:,.2f}}",
            "Share of Budget": "{:.1f}%"
        }), use_container_width=True)
    with c2:
        st.write("**Milling Cost Structure Summary:**")
        st.write(f"- Raw Material Share: **{(total_raw_material_cost/total_production_cost)*100:.1f}%**")
        st.write(f"- Packaging Share: **{(total_packaging_cost/total_production_cost)*100:.1f}%**")
        st.write(f"- Power & Labor Share: **{((power_diesel_cost + mill_labor_wages)/total_production_cost)*100:.1f}%**")

    st.markdown("---")
    st.subheader("📥 Export Feedmill Batch Audit Reports")
    exp1, exp2 = st.columns(2)
    
    with exp1:
        csv_feed_bytes = df_feed_costs.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📄 Download Feed Cost Breakdown (CSV)",
            data=csv_feed_bytes,
            file_name=f"feedmill_cost_breakdown_{feed_type.split()[0].lower()}.csv",
            mime="text/csv",
            use_container_width=True
        )

    with exp2:
        pdf_feed_bytes = generate_feedmill_pdf(
            feed_type=feed_type,
            target_tonnage=target_tonnage,
            actual_bags_produced=actual_bags_produced,
            bag_size_kg=bag_size_kg,
            total_production_cost=total_production_cost,
            gross_revenue=gross_revenue,
            net_profit=net_profit,
            production_cost_per_bag=production_cost_per_bag,
            breakeven_bag_price=breakeven_bag_price,
            currency=currency,
            df_costs=df_feed_costs
        )
        st.download_button(
            label="📕 Download Executive Feedmill Audit (PDF)",
            data=pdf_feed_bytes,
            file_name=f"feedmillpro_audit_{feed_type.split()[0].lower()}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

with tab3:
    st.subheader("Profit Sensitivity Matrix (Maize Price Shock vs. Soya Price Shock)")
    maize_variations = [maize_price_ton * factor for factor in [0.90, 0.95, 1.00, 1.05, 1.10]]
    soya_variations = [soya_price_ton * factor for factor in [0.90, 0.95, 1.00, 1.05, 1.10]]
    
    feed_matrix_data = []
    for s_price in soya_variations:
        row = []
        for m_price in maize_variations:
            r_cost_ton = (
                (def_maize_pct / 100.0 * m_price) +
                (def_soya_pct / 100.0 * s_price) +
                (def_offal_pct / 100.0 * offal_price_ton) +
                (def_premix_pct / 100.0 * premix_price_ton) +
                (def_other_pct / 100.0 * other_price_ton)
            )
            t_r_cost = r_cost_ton * target_tonnage
            t_prod_cost = t_r_cost + total_packaging_cost + total_milling_overhead
            sim_profit = gross_revenue - t_prod_cost
            row.append(sim_profit)
        feed_matrix_data.append(row)
        
    df_feed_matrix = pd.DataFrame(
        feed_matrix_data,
        index=[f"Soya @ {currency}{p:,.0f}/ton" for p in soya_variations],
        columns=[f"Maize @ {currency}{p:,.0f}/ton" for p in maize_variations]
    )
    
    st.dataframe(df_feed_matrix.style.format(f"{currency} {{:,.0f}}"), use_container_width=True)
    st.caption("Matrix models batch net profit against fluctuating grain market shocks.")
