import tkinter as tk
from tkinter import ttk
import threading
import time
from enum import Enum
from kaggle_loader import load_kaggle_sensors
from collections import defaultdict


class SensorState(Enum):
    ACTIVE  = 1
    NORMAL  = 2
    WARNING = 3
    ALERT   = 4
    FAULTY  = 5
    OFFLINE = 6


class SensorType(Enum):
    MOISTURE    = "MOISTURE"
    TEMPERATURE = "TEMPERATURE"
    PH          = "PH"


class Sensor:
    """Represents one agricultural field sensor."""

    def __init__(self, sensor_id, zone, sensor_type, reading, unit):
        self.__sensor_id   = sensor_id
        self.__zone        = zone
        self.__sensor_type = sensor_type
        self.__reading     = reading
        self.__unit        = unit
        self.__state       = SensorState.ACTIVE
        self.__assessment  = ""

    def process(self):
        """Validates then classifies the sensor reading."""
        self.__validate()
        if self.__state not in (SensorState.FAULTY,):
            self.__classify()

    def __validate(self):
        if self.__sensor_type == SensorType.MOISTURE:
            if not (0.0 <= self.__reading <= 1.0):
                self.__state      = SensorState.FAULTY
                self.__assessment = f"Moisture {self.__reading} out of range (0.0-1.0)"

        elif self.__sensor_type == SensorType.TEMPERATURE:
            if not (0.0 <= self.__reading <= 60.0):
                self.__state      = SensorState.FAULTY
                self.__assessment = f"Temperature {self.__reading}C out of range (0-60)"

        elif self.__sensor_type == SensorType.PH:
            if not (0.0 <= self.__reading <= 14.0):
                self.__state      = SensorState.FAULTY
                self.__assessment = f"pH {self.__reading} out of range (0-14)"

    def __classify(self):
        if self.__sensor_type == SensorType.MOISTURE:
            m = self.__reading
            if m < 0.20:
                self.__state      = SensorState.ALERT
                self.__assessment = "CRITICAL DRY — irrigate immediately"
            elif m < 0.35:
                self.__state      = SensorState.WARNING
                self.__assessment = "DRY — schedule irrigation within 24hrs"
            elif m < 0.65:
                self.__state      = SensorState.NORMAL
                self.__assessment = "OPTIMAL — soil conditions are good"
            elif m < 0.80:
                self.__state      = SensorState.WARNING
                self.__assessment = "WET — monitor drainage"
            else:
                self.__state      = SensorState.ALERT
                self.__assessment = "WATERLOGGED — activate drainage system"

        elif self.__sensor_type == SensorType.TEMPERATURE:
            t = self.__reading
            if t < 15.0:
                self.__state      = SensorState.ALERT
                self.__assessment = "COLD STRESS — frost damage risk"
            elif t < 20.0:
                self.__state      = SensorState.WARNING
                self.__assessment = "COOL — suboptimal for most Kenyan crops"
            elif t <= 30.0:
                self.__state      = SensorState.NORMAL
                self.__assessment = "OPTIMAL — ideal temperature for crops"
            elif t <= 35.0:
                self.__state      = SensorState.WARNING
                self.__assessment = "WARM — monitor for crop stress"
            else:
                self.__state      = SensorState.ALERT
                self.__assessment = "HEAT STRESS — crops at risk"

        elif self.__sensor_type == SensorType.PH:
            ph = self.__reading
            if ph < 4.5:
                self.__state      = SensorState.ALERT
                self.__assessment = "HIGHLY ACIDIC — lime required urgently"
            elif ph < 5.5:
                self.__state      = SensorState.WARNING
                self.__assessment = "ACIDIC — consider lime treatment"
            elif ph <= 6.8:
                self.__state      = SensorState.NORMAL
                self.__assessment = "OPTIMAL — ideal pH for Kenyan crops"
            elif ph <= 7.5:
                self.__state      = SensorState.WARNING
                self.__assessment = "ALKALINE — nutrient availability reduced"
            else:
                self.__state      = SensorState.ALERT
                self.__assessment = "HIGHLY ALKALINE — soil amendment required"

    def get_sensor_id(self):  return self.__sensor_id
    def get_zone(self):       return self.__zone
    def get_type(self):       return self.__sensor_type.value
    def get_reading(self):    return self.__reading
    def get_unit(self):       return self.__unit
    def get_state(self):      return self.__state
    def get_state_name(self): return self.__state.name
    def get_assessment(self): return self.__assessment


class FarmDashboard:
    """GUI dashboard with grouped, expandable table structure for 3000+ sensors."""

    ROW_COLORS = {
        "NORMAL" : "#d4edda",
        "WARNING": "#fff3cd",
        "ALERT"  : "#f8d7da",
        "FAULTY" : "#e2e3e5",
    }

    GROUP_COLORS = {
        "ALERT"  : "#d32f2f",
        "WARNING": "#f57c00",
        "NORMAL" : "#388e3c",
        "FAULTY" : "#757575",
    }

    def __init__(self, root):
        self.root = root
        self.running = False
        self.expanded_groups = {"ALERT": True, "WARNING": True, "NORMAL": False, "FAULTY": False}
        self.group_data = {"ALERT": [], "WARNING": [], "NORMAL": [], "FAULTY": []}

        self.root.title("SMART FARM MONITORING DASHBOARD - 3000 SENSORS")
        self.root.geometry("1100x700")
        self.root.configure(bg="#f5f5f5")
        self.root.resizable(True, True)

        self.__build_header()
        self.__build_alert_section()
        self.__build_table()
        self.__build_summary()
        add_control_buttons(self)

    def __build_header(self):
        frame = tk.Frame(self.root, bg="#1565c0", pady=15)
        frame.pack(fill="x")

        tk.Label(
            frame,
            text="SMART FARM MONITORING SYSTEM",
            font=("Arial", 18, "bold"),
            fg="white", bg="#1565c0"
        ).pack()

        tk.Label(
            frame,
            text="Decision Support for Agricultural Management",
            font=("Arial", 10),
            fg="#b3e5fc", bg="#1565c0"
        ).pack()

    def __build_alert_section(self):
        """Critical alerts section."""
        frame = tk.Frame(self.root, bg="#fff3e0", relief="solid", bd=1)
        frame.pack(fill="x", padx=15, pady=10)

        tk.Label(
            frame,
            text="CRITICAL ALERTS - NEED IMMEDIATE ACTION REQUIRED",
            font=("Arial", 11, "bold"),
            fg="#d32f2f", bg="#fff3e0"
        ).pack(anchor="w", padx=10, pady=5)

        self.alert_text = tk.Text(
            frame,
            height=3,
            font=("Courier", 9),
            bg="#fff9e6",
            relief="flat",
            state="disabled"
        )
        self.alert_text.pack(fill="both", expand=True, padx=10, pady=5)

    def __build_table(self):
        """Grouped, expandable table by sensor status."""
        frame = tk.Frame(self.root, bg="#f5f5f5")
        frame.pack(fill="both", expand=True, padx=15, pady=(0, 8))

        # Canvas with scrollbar for table
        self.table_frame = tk.Frame(frame, bg="#f5f5f5")
        self.table_frame.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        self.canvas = tk.Canvas(
            self.table_frame,
            bg="#f5f5f5",
            highlightthickness=0,
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.canvas.yview)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.scrollable_frame = tk.Frame(self.canvas, bg="#f5f5f5")
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

    def __build_summary(self):
        """KPI footer with sensor counts."""
        frame = tk.Frame(self.root, bg="#2c3e50", pady=8)
        frame.pack(fill="x")

        self.lbl_total    = self.__summary_label(frame, "Total Sensors : —")
        self.lbl_alerts   = self.__summary_label(frame, "Alerts : —")
        self.lbl_warnings = self.__summary_label(frame, "Warnings : —")
        self.lbl_normal   = self.__summary_label(frame, "Normal : —")
        self.lbl_faulty   = self.__summary_label(frame, "Faulty : —")
        self.lbl_moisture = self.__summary_label(frame, "Avg Moisture : —")

    def __summary_label(self, parent, text):
        lbl = tk.Label(
            parent,
            text=text,
            font=("Helvetica", 10, "bold"),
            fg="white", bg="#2c3e50",
            padx=14
        )
        lbl.pack(side="left")
        return lbl

    def __on_run_clicked(self):
        """Run analysis button handler."""
        if self.running:
            return

        self.running = True
        self.__clear_table()
        self.run_btn.config(state="disabled", text="ANALYZING...")
        self.status_lbl.config(text="Processing 3000 sensors from Kaggle dataset concurrently...")

        t = threading.Thread(target=self.__run_analysis)
        t.daemon = True
        t.start()

    def __on_clear_clicked(self):
        """Clear button handler."""
        self.__clear_table()
        self.__reset_summary()
        self.status_lbl.config(text="Cleared. Press RUN ANALYSIS to start.")
        self.group_data = {"ALERT": [], "WARNING": [], "NORMAL": [], "FAULTY": []}

    def __run_analysis(self):
        """Background thread: Load and process 3000 sensors."""
        # Load 1000 Kaggle records = 3000 sensors (3 types per record)
        kaggle_sensor_data = load_kaggle_sensors(limit=1000)
        
        if not kaggle_sensor_data:
            self.root.after(0, lambda: self.__handle_error("Failed to load Kaggle dataset"))
            return
        
        sensors = [
            Sensor(
                s["sensor_id"],
                s["zone"],
                SensorType[s["sensor_type"]],
                s["reading"],
                s["unit"]
            )
            for s in kaggle_sensor_data
        ]
        
        results = []
        lock = threading.Lock()

        def process_one(sensor):
            sensor.process()
            with lock:
                results.append(sensor)

        threads = []
        for sensor in sensors:
            t = threading.Thread(target=process_one, args=(sensor,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        self.root.after(0, lambda: self.__display_results(results))

    def __handle_error(self, msg):
        """Handle errors."""
        self.status_lbl.config(text=f"ERROR: {msg}")
        self.run_btn.config(state="normal", text="RUN ANALYSIS")
        self.running = False

    def __display_results(self, results):
        """Display results organized by status groups."""
        # Group sensors by status
        self.group_data = {"ALERT": [], "WARNING": [], "NORMAL": [], "FAULTY": []}
        
        for sensor in results:
            state = sensor.get_state_name()
            self.group_data[state].append(sensor)
        
        # Display grouped table
        self.__display_grouped_table()
        
        # Display alerts
        self.__display_alerts()
        
        # Update summary
        self.__update_summary(results)
        
        self.status_lbl.config(text="Analysis complete. 3000 sensors processed.")
        self.run_btn.config(state="normal", text="RUN ANALYSIS")
        self.running = False

    def __display_alerts(self):
        """Show critical alerts at top."""
        self.alert_text.config(state="normal")
        self.alert_text.delete(1.0, tk.END)
        
        alert_count = len(self.group_data["ALERT"])
        if alert_count > 0:
            alert_zones = set()
            for sensor in self.group_data["ALERT"][:10]:  # Show first 10
                alert_zones.add(sensor.get_zone())
            
            zones_str = ", ".join(sorted(alert_zones)[:5])
            self.alert_text.insert(tk.END, f"  {alert_count} sensors in CRITICAL state\n")
            self.alert_text.insert(tk.END, f"  Affected zones: {zones_str}\n")
            self.alert_text.insert(tk.END, f"  ACTION REQUIRED: Review Alert group below for details")
        else:
            self.alert_text.insert(tk.END, "  No critical alerts. All systems operating normally.")
        
        self.alert_text.config(state="disabled")

    def __display_grouped_table(self):
        """Display table with collapsible status groups."""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Display each group in order: ALERT, WARNING, NORMAL, FAULTY
        for status in ["ALERT", "WARNING", "NORMAL", "FAULTY"]:
            sensors = self.group_data[status]
            self.__create_group_header(status, len(sensors))
            
            if self.expanded_groups[status]:
                self.__create_group_table(status, sensors)

    def __create_group_header(self, status, count):
        """Create collapsible group header."""
        color = self.GROUP_COLORS[status]
        is_expanded = self.expanded_groups[status]
        arrow = "▼" if is_expanded else "►"
        
        header = tk.Frame(self.scrollable_frame, bg=color, relief="solid", bd=1)
        header.pack(fill="x", pady=(5, 0), padx=0)
        
        def toggle_group():
            self.expanded_groups[status] = not self.expanded_groups[status]
            self.__display_grouped_table()
        
        tk.Button(
            header,
            text=f"  {arrow}  {status}  ({count} sensors)",
            font=("Arial", 11, "bold"),
            fg="white", bg=color,
            anchor="w",
            relief="flat",
            cursor="hand2",
            command=toggle_group
        ).pack(fill="x", padx=10, pady=8)

    def __create_group_table(self, status, sensors):
        """Create table rows for a status group."""
        # Table header
        header_frame = tk.Frame(self.scrollable_frame, bg="#333", height=30)
        header_frame.pack(fill="x", padx=0)
        
        for col, width in [("Sensor ID", 100), ("Zone", 150), ("Type", 100), 
                           ("Reading", 100), ("State", 80), ("Assessment", 300)]:
            tk.Label(
                header_frame,
                text=col,
                font=("Helvetica", 9, "bold"),
                fg="white", bg="#333",
                width=width//8,
                anchor="w",
                padx=5
            ).pack(side="left", fill="both", expand=True)
        
        # Table rows
        for sensor in sensors[:50]:  # Limit display to 50 rows per group for performance
            row_frame = tk.Frame(self.scrollable_frame, bg=self.ROW_COLORS[status], height=25)
            row_frame.pack(fill="x", padx=0)
            
            tk.Label(row_frame, text=sensor.get_sensor_id(), font=("Courier", 8), 
                    bg=self.ROW_COLORS[status], anchor="w", padx=5).pack(side="left", fill="both", expand=True)
            tk.Label(row_frame, text=sensor.get_zone(), font=("Courier", 8),
                    bg=self.ROW_COLORS[status], anchor="w", padx=5).pack(side="left", fill="both", expand=True)
            tk.Label(row_frame, text=sensor.get_type(), font=("Courier", 8),
                    bg=self.ROW_COLORS[status], anchor="w", padx=5).pack(side="left", fill="both", expand=True)
            tk.Label(row_frame, text=f"{sensor.get_reading():.2f} {sensor.get_unit()}", 
                    font=("Courier", 8), bg=self.ROW_COLORS[status], anchor="w", padx=5).pack(side="left", fill="both", expand=True)
            tk.Label(row_frame, text=sensor.get_state_name(), font=("Courier", 8),
                    bg=self.ROW_COLORS[status], anchor="w", padx=5).pack(side="left", fill="both", expand=True)
            tk.Label(row_frame, text=sensor.get_assessment()[:40], font=("Courier", 8),
                    bg=self.ROW_COLORS[status], anchor="w", padx=5).pack(side="left", fill="both", expand=True)
        
        # "Show more" if truncated
        if len(sensors) > 50:
            more_frame = tk.Frame(self.scrollable_frame, bg="#f0f0f0")
            more_frame.pack(fill="x", padx=0)
            tk.Label(more_frame, text=f"  ... and {len(sensors)-50} more {status} sensors",
                    font=("Helvetica", 9, "italic"), fg="#666", bg="#f0f0f0", anchor="w").pack(fill="x", padx=10, pady=3)

    def __update_summary(self, results):
        """Update KPI footer."""
        alerts = len([s for s in results if s.get_state_name() == "ALERT"])
        warnings = len([s for s in results if s.get_state_name() == "WARNING"])
        normal = len([s for s in results if s.get_state_name() == "NORMAL"])
        faulty = len([s for s in results if s.get_state_name() == "FAULTY"])
        
        moist = [s for s in results if s.get_type() == "MOISTURE" and s.get_state_name() != "FAULTY"]
        avg_m = sum(s.get_reading() for s in moist) / len(moist) if moist else 0
        
        self.lbl_total.config(text=f"Total Sensors : {len(results)}")
        self.lbl_alerts.config(text=f"Alerts : {alerts}")
        self.lbl_warnings.config(text=f"Warnings : {warnings}")
        self.lbl_normal.config(text=f"Normal : {normal}")
        self.lbl_faulty.config(text=f"Faulty : {faulty}")
        self.lbl_moisture.config(text=f"Avg Moisture : {avg_m:.3f} VWC")

    def __clear_table(self):
        """Clear table display."""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

    def __reset_summary(self):
        """Reset summary labels."""
        self.lbl_total.config(text="Total Sensors : —")
        self.lbl_alerts.config(text="Alerts : —")
        self.lbl_warnings.config(text="Warnings : —")
        self.lbl_normal.config(text="Normal : —")
        self.lbl_faulty.config(text="Faulty : —")
        self.lbl_moisture.config(text="Avg Moisture : —")


def add_control_buttons(dashboard):
    """Add control buttons to the dashboard."""
    frame = tk.Frame(dashboard.root, bg="#eceff1", pady=10)
    frame.pack(fill="x", side="bottom")

    dashboard.run_btn = tk.Button(
        frame,
        text="RUN ANALYSIS",
        font=("Helvetica", 11, "bold"),
        bg="#27ae60", fg="white",
        activebackground="#1e8449",
        relief="flat", padx=20, pady=6,
        cursor="hand2",
        command=lambda: dashboard._FarmDashboard__on_run_clicked()
    )
    dashboard.run_btn.pack(side="left", padx=(0, 8))

    tk.Button(
        frame,
        text="CLEAR",
        font=("Helvetica", 11),
        bg="#c0392b", fg="white",
        activebackground="#a93226",
        relief="flat", padx=20, pady=6,
        cursor="hand2",
        command=lambda: dashboard._FarmDashboard__on_clear_clicked()
    ).pack(side="left")

    dashboard.status_lbl = tk.Label(
        frame,
        text="Ready. Press RUN ANALYSIS to start.",
        font=("Helvetica", 10),
        fg="#7f8c8d", bg="#eceff1"
    )
    dashboard.status_lbl.pack(side="left", padx=16)


if __name__ == "__main__":
    # >>> APPLICATION ENTRY: Creates GUI and starts event loop
    root = tk.Tk()
    app  = FarmDashboard(root)
    root.mainloop()
