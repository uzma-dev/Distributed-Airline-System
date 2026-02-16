import tkinter as tk
from tkinter import ttk
import requests

# ---------------- CONFIG ----------------
SERVER_URL = "https://chatty-rufflike-mellisa.ngrok-free.dev"
# Replace with your current Ngrok URL

NAME = "Uzma"
REG_NO = "23BIT0284"
SL_NO = "43"

ROLES = [
    "Pilot",
    "Co-Pilot",
    "Sky Marshal",
    "Flight Attendant",
    "Engineer"
]


# ---------------- MAIN WINDOW ----------------
root = tk.Tk()
root.title("Distributed Airline Crew System")
root.geometry("700x750")
root.resizable(False, False)


# ---------------- HEADER ----------------
header = tk.Label(
    root,
    text=f"Distributed Airline Crew Management System\nName: {NAME}\nReg No: {REG_NO}\nSerial No: {SL_NO}",
    font=("Arial", 15, "bold"),
    pady=15
)
header.pack()


# ---------------- STATUS ----------------
status = tk.Label(root, text="", font=("Arial", 11, "bold"))
status.pack(pady=5)


# ---------------- ADD CREW ----------------
add_frame = tk.LabelFrame(root, text=" Add Crew ", font=("Arial", 12, "bold"), padx=15, pady=15)
add_frame.pack(pady=10, fill="x", padx=20)

tk.Label(add_frame, text="Name").grid(row=0, column=0, sticky="w")
name_entry = tk.Entry(add_frame, width=25)
name_entry.grid(row=0, column=1, pady=5)

tk.Label(add_frame, text="Role").grid(row=1, column=0, sticky="w")

role_box = ttk.Combobox(add_frame, values=ROLES, state="readonly", width=22)
role_box.grid(row=1, column=1, pady=5)
role_box.set("Select Role")


def add_crew():

    name = name_entry.get().strip()
    role = role_box.get()

    if len(name) < 2:
        status.config(text="Name must be at least 2 letters", fg="red")
        return

    if role == "Select Role":
        status.config(text="Please select a role", fg="red")
        return

    data = {"name": name, "role": role}

    try:
        res = requests.post(f"{SERVER_URL}/add_crew", json=data)

        if res.status_code == 201:
            status.config(text="Crew Added Successfully", fg="green")
            name_entry.delete(0, tk.END)
            role_box.set("Select Role")
            load_crew()
        else:
            status.config(text="Failed to Add Crew", fg="red")

    except:
        status.config(text="Server Not Reachable", fg="red")


tk.Button(add_frame, text="Add Crew", width=18, command=add_crew)\
    .grid(row=2, column=0, columnspan=2, pady=10)


# ---------------- ASSIGN FLIGHT ----------------
assign_frame = tk.LabelFrame(root, text=" Assign Flight ", font=("Arial", 12, "bold"), padx=15, pady=15)
assign_frame.pack(pady=10, fill="x", padx=20)

tk.Label(assign_frame, text="Crew ID").grid(row=0, column=0, sticky="w")
id_entry = tk.Entry(assign_frame, width=25)
id_entry.grid(row=0, column=1, pady=5)

tk.Label(assign_frame, text="Flight No").grid(row=1, column=0, sticky="w")
flight_entry = tk.Entry(assign_frame, width=25)
flight_entry.grid(row=1, column=1, pady=5)


def assign_flight():

    crew_id = id_entry.get().strip()
    flight = flight_entry.get().strip()

    if not crew_id.isdigit():
        status.config(text="Crew ID must be a number", fg="red")
        return

    if len(flight) == 0:
        status.config(text="Enter flight number", fg="red")
        return

    data = {"id": int(crew_id), "flight": flight}

    try:
        res = requests.post(f"{SERVER_URL}/assign", json=data)
        result = res.json()

        if res.status_code == 200:
            status.config(text=result["message"], fg="green")
        elif res.status_code == 409:
            status.config(text="Crew Already Assigned", fg="red")
        elif res.status_code == 404:
            status.config(text="Crew ID Not Found", fg="red")
        else:
            status.config(text="Error Occurred", fg="red")

        id_entry.delete(0, tk.END)
        flight_entry.delete(0, tk.END)
        load_crew()

    except:
        status.config(text="Server Not Reachable", fg="red")


tk.Button(assign_frame, text="Assign Flight", width=18, command=assign_flight)\
    .grid(row=2, column=0, columnspan=2, pady=10)


# ---------------- DATABASE ----------------
db_frame = tk.LabelFrame(root, text=" Crew Database ", font=("Arial", 12, "bold"), padx=10, pady=10)
db_frame.pack(pady=10, fill="both", expand=True, padx=20)

crew_box = tk.Listbox(db_frame, width=95, height=15)
crew_box.pack(pady=5)


def load_crew():
    try:
        res = requests.get(f"{SERVER_URL}/crew")
        data = res.json()

        crew_box.delete(0, tk.END)

        for c in data:
            line = (
                f"ID:{c['id']} | {c['name']} | {c['role']} | "
                f"Flight:{c['flight']} | "
                f"Created(UTC):{c['created_at_utc']} | "
                f"Assigned(UTC):{c['assigned_at_utc']}"
            )
            crew_box.insert(tk.END, line)

    except:
        status.config(text="Cannot Load Database", fg="red")


tk.Button(root, text="Refresh Database", width=20, command=load_crew).pack(pady=5)


# ---------------- SYSTEM STATE ----------------
def show_system_state():
    try:
        res = requests.get(f"{SERVER_URL}/system_state")
        data = res.json()

        status.config(
            text=f"Total: {data['total_crew']} | Assigned: {data['assigned_crew']}",
            fg="purple"
        )

    except:
        status.config(text="Cannot Fetch System State", fg="red")


tk.Button(root, text="View System State", width=20, command=show_system_state)\
    .pack(pady=10)


load_crew()
root.mainloop()