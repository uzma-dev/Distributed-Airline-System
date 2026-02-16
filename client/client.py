import tkinter as tk
import requests

# ---------------- CONFIG ----------------
SERVER_URL = "https://chatty-rufflike-mellisa.ngrok-free.dev"
# Replace with your active Ngrok URL

NAME = "Uzma"
REG_NO = "23BIT0284"


# ---------------- MAIN WINDOW ----------------
root = tk.Tk()
root.title("Distributed Airline Crew System")
root.geometry("550x650")


# ---------------- HEADER ----------------
header = tk.Label(
    root,
    text=f"Distributed Airline Crew Management System\nName: {NAME}\nReg No: {REG_NO}",
    font=("Arial", 14, "bold"),
    pady=10
)
header.pack()


# ---------------- STATUS ----------------
status = tk.Label(root, text="", fg="blue", font=("Arial", 10))
status.pack(pady=5)


# ---------------- ADD CREW ----------------
tk.Label(root, text="Add Crew", font=("Arial", 12, "bold")).pack(pady=5)

tk.Label(root, text="Name").pack()
name_entry = tk.Entry(root, width=30)
name_entry.pack()

tk.Label(root, text="Role").pack()
role_entry = tk.Entry(root, width=30)
role_entry.pack()


def add_crew():
    name = name_entry.get()
    role = role_entry.get()

    if name == "" or role == "":
        status.config(text="Enter Name and Role", fg="red")
        return

    data = {
        "name": name,
        "role": role
    }

    try:
        res = requests.post(f"{SERVER_URL}/add_crew", json=data)

        if res.status_code == 201:
            status.config(text="Crew Added Successfully", fg="green")
            name_entry.delete(0, tk.END)
            role_entry.delete(0, tk.END)
            load_crew()
        else:
            status.config(text=res.json().get("error", "Error"), fg="red")

    except:
        status.config(text="Server Not Reachable", fg="red")


tk.Button(root, text="Add Crew", command=add_crew, width=20).pack(pady=5)


# ---------------- ASSIGN FLIGHT ----------------
tk.Label(root, text="Assign Flight", font=("Arial", 12, "bold")).pack(pady=10)

tk.Label(root, text="Crew ID").pack()
id_entry = tk.Entry(root, width=30)
id_entry.pack()

tk.Label(root, text="Flight No").pack()
flight_entry = tk.Entry(root, width=30)
flight_entry.pack()


def assign_flight():
    crew_id = id_entry.get()
    flight = flight_entry.get()

    if crew_id == "" or flight == "":
        status.config(text="Enter ID and Flight", fg="red")
        return

    try:
        data = {
            "id": int(crew_id),
            "flight": flight
        }

        res = requests.post(f"{SERVER_URL}/assign", json=data)
        result = res.json()

        if res.status_code == 200:
            status.config(
                text=f"{result['message']} | Logical Time: {result['logical_time']}",
                fg="green"
            )

        elif res.status_code == 409:
            status.config(text="Conflict: Already Assigned", fg="red")

        elif res.status_code == 404:
            status.config(text="Crew ID Not Found", fg="red")

        else:
            status.config(text=result.get("error", "Error"), fg="red")

        id_entry.delete(0, tk.END)
        flight_entry.delete(0, tk.END)

        load_crew()

    except:
        status.config(text="Server Not Reachable", fg="red")


tk.Button(root, text="Assign Flight", command=assign_flight, width=20).pack(pady=5)


# ---------------- CREW LIST ----------------
tk.Label(root, text="Crew Database", font=("Arial", 12, "bold")).pack(pady=10)

crew_box = tk.Listbox(root, width=70, height=12)
crew_box.pack(pady=5)


def load_crew():

    try:
        res = requests.get(f"{SERVER_URL}/crew")

        if res.status_code != 200:
            status.config(text="Failed to Load Data", fg="red")
            return

        data = res.json()

        crew_box.delete(0, tk.END)

        for c in data:
            line = (
                f"ID: {c['id']} | {c['name']} | {c['role']} | "
                f"Flight: {c['flight']} | Logical Time: {c['logical_time']}"
            )
            crew_box.insert(tk.END, line)

    except:
        status.config(text="Cannot Load Data", fg="red")


tk.Button(root, text="Refresh Data", command=load_crew).pack(pady=5)


# ---------------- GLOBAL STATE BUTTON ----------------
def show_system_state():
    try:
        res = requests.get(f"{SERVER_URL}/system_state")
        data = res.json()

        status.config(
            text=f"Total Crew: {data['total_crew']} | "
                 f"Assigned: {data['assigned_crew']} | "
                 f"Logical Clock: {data['logical_clock']}",
            fg="purple"
        )

    except:
        status.config(text="Cannot Fetch System State", fg="red")


tk.Button(root, text="View System State", command=show_system_state).pack(pady=10)


# ---------------- START ----------------
load_crew()

root.mainloop()