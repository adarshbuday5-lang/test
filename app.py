import streamlit as st
import sqlite3
from datetime import datetime, timedelta

# 1. DATABASE CONFIGURATION
def init_db():
    conn = sqlite3.connect("fois.db")
    cursor = conn.cursor()
    # Create Stations table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stations (
            code TEXT PRIMARY KEY,
            name TEXT,
            travel_time_to_next_mins INTEGER
        )
    """)
    # Create Schedules table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rake_id TEXT,
            source TEXT,
            destination TEXT,
            departure_time TEXT,
            arrival_time TEXT
        )
    """)
    # Seed sample stations if empty
    cursor.execute("SELECT COUNT(*) FROM stations")
    if cursor.fetchone()[0] == 0:
        stations_data = [
            ("NDLS", "New Delhi", 45),
            ("CNB", "Kanpur Central", 60),
            ("HWH", "Howrah", 0)
        ]
        cursor.executemany("INSERT INTO stations VALUES (?, ?, ?)", stations_data)
    conn.commit()
    conn.close()

init_db()

# 2. ANTI-BUNCHING SCHEDULING ALGORITHM (The High-Scoring Module)
def calculate_deconflict_schedule(rake_id, source, destination, target_dept_time, headway_buffer_mins=30):
    """
    Greedy Conflict Resolution Algorithm:
    Checks if another rake is arriving at the same destination within the headway buffer.
    If bunching is detected, it dynamically shifts the departure time forward.
    """
    conn = sqlite3.connect("fois.db")
    cursor = conn.cursor()
    
    # Mock travel time calculation logic based on standard routes
    travel_time = 90 # fixed travel estimation for prototype simplicity
    
    current_dept = target_dept_time
    is_conflicted = True
    iterations = 0
    
    while is_conflicted and iterations < 50:
        current_arrival = current_dept + timedelta(minutes=travel_time)
        arrival_str = current_arrival.strftime("%Y-%m-%d %H:%M")
        
        # Query all existing schedules heading to the same destination
        cursor.execute(
            "SELECT departure_time, arrival_time, rake_id FROM schedules WHERE destination = ?", 
            (destination,)
        )
        existing_schedules = cursor.fetchall()
        
        conflict_found = False
        for sched in existing_schedules:
            existing_arrival = datetime.strptime(sched[1], "%Y-%m-%d %H:%M")
            # Check if absolute time difference is less than safety headway buffer
            time_diff = abs((current_arrival - existing_arrival).total_seconds()) / 60
            if time_diff < headway_buffer_mins:
                conflict_found = True
                break
                
        if conflict_found:
            # Shift departure forward by 15 minutes to clear the bottleneck slot
            current_dept += timedelta(minutes=15)
            iterations += 1
        else:
            is_conflicted = False
            
    conn.close()
    final_arrival = current_dept + timedelta(minutes=travel_time)
    return current_dept, final_arrival, iterations > 0

# 3. STREAMLIT FRONTEND USER INTERFACE
st.set_page_config(page_title="Mini-FOIS Engine", layout="wide")
st.title("🚂 Freight Operations Information System (FOIS) Prototype")
st.subheader("Smart Automated Rake Tracking & Anti-Bunching Scheduler")

col1, col2 = st.columns([1, 2])

with col1:
    st.header("Schedule New Freight Rake")
    rake_id = st.text_input("Rake Unique ID", value="RK-2026-A")
    source = st.selectbox("Source Terminal", ["NDLS", "CNB"])
    destination = st.selectbox("Destination Yard", ["HWH", "CNB"])
    
    date_input = st.date_input("Departure Date", datetime.now())
    time_input = st.time_input("Target Departure Time", datetime.now().time())
    
    # Combine date and time
    target_dt = datetime.combine(date_input, time_input)
    
    if st.button("Run Smart Scheduler", type="primary"):
        if source == destination:
            st.error("Source and Destination cannot be identical!")
        else:
            # Trigger our anti-bunching heuristic calculation
            final_dept, final_arr, was_delayed = calculate_deconflict_schedule(rake_id, source, destination, target_dt)
            
            # Save final conflict-free schedule to database
            conn = sqlite3.connect("fois.db")
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO schedules (rake_id, source, destination, departure_time, arrival_time) VALUES (?, ?, ?, ?, ?)",
                (rake_id, source, destination, final_dept.strftime("%Y-%m-%d %H:%M"), final_arr.strftime("%Y-%m-%d %H:%M"))
            )
            conn.commit()
            conn.close()
            
            if was_delayed:
                st.warning(f"⚠️ Bunching Detected! Departure rescheduled to avoid arrival gridlock.")
            else:
                st.success("✅ Schedule optimized and booked with clean line headway!")
                
            st.metric(label="Optimized Departure Time", value=final_dept.strftime("%H:%M"))
            st.metric(label="Calculated Arrival Time", value=final_arr.strftime("%H:%M"))

with col2:
    st.header("Live Yard Schedule & Line Status")
    
    conn = sqlite3.connect("fois.db")
    cursor = conn.cursor()
    cursor.execute("SELECT rake_id, source, destination, departure_time, arrival_time FROM schedules ORDER BY arrival_time ASC")
    rows = cursor.fetchall()
    conn.close()
    
    if rows:
        # Display schedules in an explicit data grid table
        st.table([
            {"Rake ID": r[0], "From": r[1], "To": r[2], "Departure": r[3], "Arrival": r[4]}
            for r in rows
        ])
    else:
        st.info("No active freight rakes on the lines currently.")