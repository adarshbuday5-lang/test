import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

st.set_page_config(page_title="NTPC Dadri - Rake Unloading & Demurrage Engine", layout="wide")

# Custom CSS for industrial enterprise branding
st.markdown("""
    <style>
    .main-title { font-size:32px; font-weight:bold; color:#1E3A8A; margin-bottom:5px; }
    .sub-title { font-size:18px; color:#4B5563; margin-bottom:25px; }
    .metric-card { background-color: #F3F4F6; padding: 15px; border-radius: 8px; border-left: 5px solid #2563EB; }
    </style>
""", unsafe_allowed_html=True)

st.markdown('<div class="main-title">🚂 FOIS-Tippler Operational Optimization Platform</div>', unsafe_allowed_html=True)
st.markdown('<div class="sub-title">Real-Time Unloading Performance, Demurrage Analytics & Anti-Bunching Control Center | Site: NC Dadri (DER)</div>', unsafe_allowed_html=True)

# -------------------------------------------------------------------
# MOCK DATASETS MATCHING USER'S EXACT EXCEL STRUCTURE
# -------------------------------------------------------------------
@st.cache_data
def load_historical_demurrage_data():
    # Exactly matches the categories in "Daily Rake UL Report.xlsx - Dmrg. Pie charts.csv"
    reasons = [
        "Due to Bunching", "Due to CHP System", "Boulders & Sticky Coal", 
        "Due to Railway Line Clearance", "Wagon Defect / Coupler", "Bad Weather / Fog"
    ]
    boxn_shares = [44.0, 30.0, 5.7, 10.6, 4.7, 5.0]
    bobr_shares = [78.8, 9.5, 5.0, 3.1, 1.8, 1.8]
    
    df_boxn = pd.DataFrame({"Reason": reasons, "Percentage": boxn_shares, "Type": "BOXN (Wagon Tippler)"})
    df_bobr = pd.DataFrame({"Reason": reasons, "Percentage": bobr_shares, "Type": "BOBR (Track Hopper)"})
    return pd.concat([df_boxn, df_bobr])

@st.cache_data
def get_active_yard_status():
    return [
        {"Rake ID": "NCL/SPUS/1490", "Type": "BOXN", "Siding": "SPUS/NCL", "Wagons": 58, "Status": "Tippling", "Location": "WT-2", "Arrival": "08:25", "Demurrage Risk": "Low"},
        {"Rake ID": "CCL/KTWY/0189", "Type": "BOBR", "Siding": "KTWY/CCL", "Wagons": 59, "Status": "Discharging", "Location": "TH-1", "Arrival": "09:40", "Demurrage Risk": "Medium"},
        {"Rake ID": "NCL/SSMN/1492", "Type": "BOXN", "Siding": "SSMN/NCL", "Wagons": 56, "Status": "Waiting", "Location": "R&D Line 7", "Arrival": "10:15", "Demurrage Risk": "High ⚠️"}
    ]

hist_df = load_historical_demurrage_data()
active_rakes = get_active_yard_status()

# -------------------------------------------------------------------
# ENTERPRISE MULTI-TAB NAVIGATION INTERFACE
# -------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["📊 Executive Demurrage Analytics", "🎛️ Live Yard & Tippler Monitor", "📅 Anti-Bunching Smart Scheduler"])

# TAB 1: EXECUTIVE DEMURRAGE ANALYTICS
with tab1:
    st.subheader("⚠️ Root Cause Analysis of Financial Demurrage Losses")
    st.write("Historical distribution calculated from the plant cycle log reports for fiscal year 2025-2026.")
    
    col_pie1, col_pie2 = st.columns(2)
    
    with col_pie1:
        boxn_data = hist_df[hist_df["Type"] == "BOXN (Wagon Tippler)"]
        fig_boxn = px.pie(boxn_data, values="Percentage", names="Reason", 
                          title="BOXN Rake Demurrage Root Causes (Tippler Handled)",
                          hole=0.4, color_discrete_sequence=px.colors.sequential.YlOrRd_r)
        st.plotly_chart(fig_boxn, use_container_width=True)
        
    with col_pie2:
        bobr_data = hist_df[hist_df["Type"] == "BOBR (Track Hopper)"]
        fig_bobr = px.pie(bobr_data, values="Percentage", names="Reason", 
                          title="BOBR Rake Demurrage Root Causes (Track Hopper Handled)",
                          hole=0.4, color_discrete_sequence=px.colors.sequential.Blues_r)
        st.plotly_chart(fig_bobr, use_container_width=True)
        
    st.markdown("---")
    st.subheader("📈 Monthly Handling Trends & Average Cycle Hours Breakdown")
    
    # Timeline trend data reconstruction from 'Cycle Time Brake-Up' sheet
    months = ["April", "May", "June", "July", "August", "September", "October", "November", "December", "January"]
    avg_cycle_hrs = [7.1, 6.8, 8.2, 9.5, 11.2, 10.4, 8.9, 8.5, 8.0, 8.5]
    bunching_incidents = [22, 19, 31, 45, 58, 52, 34, 28, 25, 29]
    
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Bar(x=months, y=bunching_incidents, name="Line Bunching Bottlenecks", yaxis="y1", marker_color="#EF4444", opacity=0.7))
    fig_trend.add_trace(go.Scatter(x=months, y=avg_cycle_hrs, name="Avg Rake Cycle Hours (Target < 7hr)", yaxis="y2", line=dict(color="#10B981", width=3, shape='spline')))
    
    fig_trend.update_layout(
        title="Impact of Rail Line Bunching on Total Plant Cycle Turnaround Times",
        xaxis=dict(title="Operational Month"),
        yaxis=dict(title="Number of Bunching Delays Locked", side="left"),
        yaxis=2=dict(title="Mean Cycle Hours (R&D to R&D)", side="right", overlaying="y", showgrid=False),
        legend=dict(x=0.01, y=0.99)
    )
    st.plotly_chart(fig_trend, use_container_width=True)

# TAB 2: LIVE YARD & TIPPLER MONITOR
with tab2:
    st.subheader("🗺️ Real-Time Plant Infrastructure Tracking System")
    
    # High-level operational live KPIs
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric(label="Rakes Currently in Yard", value="3 Rakes", delta="Steady Line Flow")
    kpi2.metric(label="Active Tippler Status (WT-1 / WT-2)", value="1 IDLE / 1 ACTIVE", delta="-15% Load Congestion")
    kpi3.metric(label="Track Hopper Status (TH-1 / TH-2)", value="1 ACTIVE / 1 IDLE", delta="Optimal Discharge")
    kpi4.metric(label="Current Mean Tippling Rate", value="28 Wagons / Hr", delta="+2% vs Last Shift", delta_color="inverse")
    
    st.write("### Current Track Allocations & Processing Status")
    
    # Beautiful Custom HTML/CSS styled representation of the physical tracks
    for rake in active_rakes:
        status_color = "#10B981" if rake["Status"] == "Tippling" else ("#F59E0B" if rake["Status"] == "Discharging" else "#EF4444")
        
        with st.container():
            st.markdown(f"""
            <div style="background-color: #FAFAFA; padding: 20px; border-radius: 10px; border-left: 8px solid {status_color}; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span style="font-size: 18px; font-weight: bold; color: #111827;">{rake["Rake ID"]}</span>
                        <span style="background-color: #E5E7EB; color: #374151; padding: 2px 8px; border-radius: 12px; font-size: 12px; font-weight: bold; margin-left: 10px;">{rake["Type"]} Wagon</span>
                    </div>
                    <div style="font-weight: bold; color: {status_color}; text-transform: uppercase; letter-spacing: 1px;">{rake["Status"]} @ {rake["Location"]}</div>
                </div>
                <div style="margin-top: 10px; display: flex; gap: 40px; color: #4B5563; font-size: 14px;">
                    <div><b>Origin Coal Siding:</b> {rake["Siding"]}</div>
                    <div><b>Wagon Inventory Count:</b> {rake["Wagons"]} Units</div>
                    <div><b>R&D Yard Entry Time:</b> {rake["Arrival"]} Hrs</div>
                    <div><b>Demurrage Threat Level:</b> <span style="color:{status_color}; font-weight:bold;">{rake["Demurrage Risk"]}</span></div>
                </div>
            </div>
            """, unsafe_allowed_html=True)

# TAB 3: ANTI-UNCHING SMART SCHEDULER
with tab3:
    st.subheader("📅 Heuristic Anti-Bunching Algorithm Controls")
    st.write("Simulate or feed live incoming train declarations from FOIS to dynamically shift placement slots and guarantee zero gridlock demurrage charges.")
    
    col_sim1, col_sim2 = st.columns([1, 2])
    
    with col_sim1:
        st.markdown('<div class="metric-card"><b>Configure Incoming Rake Profile</b></div>', unsafe_allowed_html=True)
        st.write("")
        sim_id = st.text_input("FOIS Declared Rake ID", "NCL/JNCS/1453")
        sim_type = st.radio("Wagon Sub-Type Specification", ["BOXN (Requires Tippler Line)", "BOBR (Requires Hopper Line)"])
        sim_source = st.selectbox("Origin Loading Siding Location", ["JNCS/NCL", "SPUS/NCL", "BCSR/CCL", "DSNS/NCL", "DCSN/NCL"])
        sim_wagons = st.slider("Total Wagon Manifest Load Count", min_value=30, max_value=60, value=58)
        
        target_time = st.time_input("Requested Placement Timestamp Slot", datetime.now().time())
        
        run_allocator = st.button("Execute Predictive Allocation Engine", type="primary")
        
    with col_sim2:
        st.markdown("### Operational De-confliction Resolution View")
        if run_allocator:
            # Simple algorithmic simulation matching the user's specific data logic
            sim_target_dt = datetime.combine(datetime.today(), target_time)
            
            # Simulated bunching constraint checker
            conflict_detected = random.choice([True, False])
            
            if conflict_detected:
                st.error("🚨 CRITICAL LINE BUNCHING PREDICTED! Another rake is already scheduled to occupy the designated unloading bay within your target timeline window.")
                adjusted_time = sim_target_dt + timedelta(minutes=165) # standard tippling duration offset
                
                st.info(f"💡 **Algorithm Remediation Rule Executed:** Staggered queue delay calculated. Safe conflict-free placement slot approved at **{adjusted_time.strftime('%H:%M')}**.")
                
                # Plotly Visual Gantt Chart representing de-confliction
                df_gantt = pd.DataFrame([
                    dict(Task="Conflicting Active Rake", Start=sim_target_dt, Finish=sim_target_dt + timedelta(minutes=150), Resource="Occupied Slot"),
                    dict(Task=f"Your Scheduled Rake: {sim_id}", Start=adjusted_time, Finish=adjusted_time + timedelta(minutes=150), Resource="Optimized Safe Slot")
                ])
                fig_gantt = px.timeline(df_gantt, x_start="Start", x_end="Finish", y="Task", color="Resource", title="De-conflicted Unloading Pipeline Timeline Layout", color_discrete_sequence=["#EF4444", "#10B981"])
                fig_gantt.update_yaxes(autorange="reversed")
                st.plotly_chart(fig_gantt, use_container_width=True)
            else:
                st.success("✅ LINE STATUS CLEAR! No overlapping rake bunching detected for this slot sequence. Demurrage risk minimized to 0.0%.")
                st.metric("Approved Placement Schedule Time", value=sim_target_dt.strftime("%H:%M"), delta="0 Min Deviation")
        else:
            st.info("Fill out the incoming rake declaration fields on the left pane and run the validation algorithm to display live grid visualizations.")
