import tkinter as tk
import random
import datetime
import numpy as np  # Import numpy for Poisson distribution
from roomgenerator import *
from patientgenerator import PatientGenerator
import tkinter.messagebox as messagebox  # Add this import at the top of main.py

class RoomPlanner(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hospital Room Planner")
        self.geometry("800x600")
        self.rooms = {}
        self.room_widgets = []
        self.grid_size = 4
        self.patient_generator = PatientGenerator()

        self.input_frame = tk.Frame(self)
        self.input_frame.pack(pady=10)
        self.create_input_fields()

        self.current_time = datetime.datetime.strptime("06:00", "%H:%M")
        # Create a persistent time label
        # self.time_label = tk.Label(self, text=self.format_time_label(), font=("Helvetica", 16))
        # self.time_label.pack(pady=10)

        self.canvas = tk.Canvas(self, width=800, height=600, bg="white")
        self.canvas.pack(fill="both", expand=True)

        self.grid_cells = []  # Keep track of grid cell coordinates
        self.initialize_grid()

        self.distribution_type = None
        self.distribution_parameters = {}
        self.dragging_patient = None

    def create_input_fields(self):
        tk.Label(self.input_frame, text="Number of A Rooms:").grid(row=0, column=0)
        self.a_count_entry = tk.Entry(self.input_frame)
        self.a_count_entry.grid(row=0, column=1)

        tk.Label(self.input_frame, text="Number of B Rooms:").grid(row=1, column=0)
        self.b_count_entry = tk.Entry(self.input_frame)
        self.b_count_entry.grid(row=1, column=1)

        tk.Label(self.input_frame, text="Number of C Rooms:").grid(row=2, column=0)
        self.c_count_entry = tk.Entry(self.input_frame)
        self.c_count_entry.grid(row=2, column=1)

        self.generate_button = tk.Button(self.input_frame, text="Generate Rooms", command=self.generate_rooms)
        self.generate_button.grid(row=3, columnspan=2)

    def initialize_grid(self):
        """Initialize the grid cells for snapping."""
        cell_width = 800 // self.grid_size
        cell_height = (600 - 100) // self.grid_size  # Reduced height to accommodate the waiting room
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                x = i * cell_width
                y = 100 + j * cell_height  # Start below the waiting room
                self.grid_cells.append((x, y, x + cell_width, y + cell_height))


    def calculate_total_cost_and_rooms(self):
        """Calculate the total cost and total number of rooms."""
        total_cost = 0
        total_rooms = 0

        for room_name, characteristics in self.rooms.items():
            if room_name != "WaitingRoom":  # Exclude the waiting room
                total_cost += characteristics.get("cost_per_day", 0)
                total_rooms += 1

        return total_cost, total_rooms

    def confirm_room_selection(self):
        """Display a confirmation dialog for the total cost and rooms."""
        total_cost, total_rooms = self.calculate_total_cost_and_rooms()

        if total_cost > 42000:
            messagebox.showerror(
                "Error",
                f"Total cost ({total_cost}) exceeds the allowed limit of 42000. Please reselect the number of rooms."
            )
            return False
        if total_rooms > 16:
            messagebox.showerror(
                "Error",
                f"Total number of rooms ({total_rooms}) exceeds the limit of 16. Please reselect the number of rooms."
            )
            return False

        # Show confirmation and proceed
        proceed = messagebox.askyesno(
            "Confirmation",
            f"Total Cost: {total_cost}\nTotal Rooms: {total_rooms}\n\nDo you want to proceed?"
        )
        return proceed

    def generate_rooms(self):
        """Generate rooms and validate selection before proceeding."""
        a_count = int(self.a_count_entry.get())
        b_count = int(self.b_count_entry.get())
        c_count = int(self.c_count_entry.get())

        room_manager = RoomManager()
        self.rooms = room_manager.generate_rooms(a_count, b_count, c_count)

    # Validate and confirm before proceeding
        if not self.confirm_room_selection():
            return

        self.canvas.delete("all")
        self.room_widgets.clear()
        self.create_waiting_room()
        self.create_grid()
        self.snap_rooms_to_grid()
        self.show_distribution_options()


    def create_waiting_room(self):
        """Create the waiting room above the 16-cell grid."""
        self.canvas.create_rectangle(0, 0, 800, 100, fill="lightgray", tags="WaitingRoom")
        self.canvas.create_text(400, 50, text="Waiting Room", font=("Helvetica", 16), tags="WaitingRoom")

    def create_grid(self):
        """Draw the 4x4 grid on the canvas below the waiting room."""
        cell_width = 800 // self.grid_size
        cell_height = (600 - 100) // self.grid_size
        for i in range(self.grid_size + 1):
            self.canvas.create_line(i * cell_width, 100, i * cell_width, 600, fill="gray")
            self.canvas.create_line(0, 100 + i * cell_height, 800, 100 + i * cell_height, fill="gray")

    def snap_rooms_to_grid(self):
        """Snap each room into a grid cell."""
        room_colors = {"A": "red", "B": "blue", "C": "yellow"}
        index = 0

        for room_name, characteristics in self.rooms.items():
            if index >= len(self.grid_cells):
                break  # Ensure we don't exceed the number of grid cells
            
            if room_name == 'WaitingRoom':
                continue
            x1, y1, x2, y2 = self.grid_cells[index]
            room_type = room_name[0]  # Get the room type (A, B, or C)
            color = room_colors.get(room_type, "lightblue")

            # Draw the room as a rectangle in the grid cell
            room_rect = self.canvas.create_rectangle(
                x1, y1, x2, y2, fill=color, tags=room_name
            )
            label = self.canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2, text=room_name)

            self.room_widgets.append((room_rect, label))
            index += 1


    def show_distribution_options(self):
        """Show a drop-down menu for selecting the distribution type and create input fields dynamically."""
        for widget in self.input_frame.winfo_children():
            widget.destroy()

        tk.Label(self.input_frame, text="Select Distribution Type:").pack()
        self.distribution_var = tk.StringVar(self)
        self.distribution_var.set("Poisson")
        distribution_menu = tk.OptionMenu(
            self.input_frame, self.distribution_var, "Poisson", "Uniform", "Normal", command=self.update_distribution_fields
        )
        distribution_menu.pack()
        self.parameter_frame = tk.Frame(self.input_frame)
        self.parameter_frame.pack()

        confirm_button = tk.Button(self.input_frame, text="Confirm", command=self.confirm_distribution)
        confirm_button.pack()
        self.update_distribution_fields("Poisson")

    def update_distribution_fields(self, distribution_type):
        """Update input fields based on the selected distribution type for patient types A, B, and C."""
        for widget in self.parameter_frame.winfo_children():
            widget.destroy()

        tk.Label(self.parameter_frame, text=f"{distribution_type} Parameters for Type A:").pack()
        self.a_param_entries = self.create_distribution_fields(self.parameter_frame, distribution_type)

        tk.Label(self.parameter_frame, text=f"{distribution_type} Parameters for Type B:").pack()
        self.b_param_entries = self.create_distribution_fields(self.parameter_frame, distribution_type)

        tk.Label(self.parameter_frame, text=f"{distribution_type} Parameters for Type C:").pack()
        self.c_param_entries = self.create_distribution_fields(self.parameter_frame, distribution_type)

    def create_distribution_fields(self, frame, distribution_type):
        """Helper to create parameter fields for a given distribution type."""
        entries = {}
        if distribution_type == "Poisson":
            tk.Label(frame, text="Lambda (λ):").pack()
            entries["lambda"] = tk.Entry(frame)
            entries["lambda"].pack()
        elif distribution_type == "Uniform":
            tk.Label(frame, text="Lower Bound:").pack()
            entries["lower_bound"] = tk.Entry(frame)
            entries["lower_bound"].pack()
            tk.Label(frame, text="Upper Bound:").pack()
            entries["upper_bound"] = tk.Entry(frame)
            entries["upper_bound"].pack()
        elif distribution_type == "Normal":
            tk.Label(frame, text="Mean (μ):").pack()
            entries["mean"] = tk.Entry(frame)
            entries["mean"].pack()
            tk.Label(frame, text="Standard Deviation (σ):").pack()
            entries["std_dev"] = tk.Entry(frame)
            entries["std_dev"].pack()
        return entries

    def confirm_distribution(self):
        """Store the selected distribution and parameters for each patient type, confirm, then start simulation."""
        self.distribution_type = self.distribution_var.get()
        self.distribution_parameters = {
            "A": self.get_distribution_parameters(self.a_param_entries),
            "B": self.get_distribution_parameters(self.b_param_entries),
            "C": self.get_distribution_parameters(self.c_param_entries),
        }

        # Ask for confirmation
        proceed = messagebox.askyesno(
            "Confirm Distribution",
            f"You've selected {self.distribution_type} distribution with parameters:\n"
            f"Type A: {self.distribution_parameters['A']}\n"
            f"Type B: {self.distribution_parameters['B']}\n"
            f"Type C: {self.distribution_parameters['C']}\n\n"
            "Proceed to generate patients?"
        )

        if proceed:
            self.start_simulation()


    def get_distribution_parameters(self, entries):
        """Extract parameters from entry fields."""
        if self.distribution_type == "Poisson":
            return {"lambda": float(entries["lambda"].get())}
        elif self.distribution_type == "Uniform":
            return {
                "lower_bound": float(entries["lower_bound"].get()),
                "upper_bound": float(entries["upper_bound"].get())
            }
        elif self.distribution_type == "Normal":
            return {
                "mean": float(entries["mean"].get()),
                "std_dev": float(entries["std_dev"].get())
            }


    def start_simulation(self):
        """Start the simulation and generate patients for the first hour."""
        for widget in self.input_frame.winfo_children():
            widget.destroy()
        if not hasattr(self, "time_label"):
            self.time_label = tk.Label(self.input_frame, text=self.format_time_label(), font=("Helvetica", 16))
            self.time_label.pack(pady=10)
        # Update the time label instead of creating a new one
        self.time_label.config(text=self.format_time_label())

        # Generate patients for each type (A, B, C)
        self.patient_widgets = []
        for patient_type in ["A", "B", "C"]:
            num_patients = self.determine_patient_count(patient_type)
            for _ in range(num_patients):
                arrival_time = self.current_time.strftime("%H:%M:%S")
                patient_profile = self.patient_generator.generate_patient_profile(arrival_time, patient_type)
                self.create_patient_widget(patient_profile)

        # Add a "Confirm Choices" button after generating patients
        self.confirm_button = tk.Button(
            self.input_frame,
            text="Confirm Choices",
            font=("Helvetica", 14, "bold"),
            bg="green",
            fg="white",
            command=self.confirm_choices
        )
        self.confirm_button.pack(pady=10)

    def confirm_choices(self):
        """Confirm the current hour's choices, increment time, and update patients."""
        # Increment the simulated time
        if self.current_time.strftime("%H:%M") == "05:00":
            messagebox.showinfo("End of Cycle", "You have reached 5:00 AM. The simulation will restart.")
            self.current_time = datetime.datetime.strptime("06:00", "%H:%M")  # Reset to 6:00 AM
        else:
            self.current_time += datetime.timedelta(hours=1)  # Increment time by one hour

        # Update the time label dynamically
        self.time_label.config(text=self.format_time_label())

        # Update hours_left for all patients
        patients_to_remove = []  # Track patients that need to be removed
        healed_patients = []  # Track details of healed patients

        for patient_icon in self.patient_widgets:
            tags = self.canvas.gettags(patient_icon)

            # Find and update the hours_left tag
            for tag in tags:
                if tag.startswith("hours_left_"):
                    hours_left = int(tag.split("_")[2]) - 1  # Decrement hours_left by 1

                    if hours_left <= 0:
                        patients_to_remove.append(patient_icon)  # Mark for removal
                        # Extract patient type and other details for the summary
                        patient_type = next((t for t in tags if t in ["A", "B", "C"]), "Unknown")
                        healed_patients.append(f"Type: {patient_type}")
                    else:
                        # Update the tag with the new hours_left
                        new_tags = tuple(t for t in tags if not t.startswith("hours_left_")) + (f"hours_left_{hours_left}",)
                        self.canvas.itemconfig(patient_icon, tags=new_tags)

        # Remove patients with hours_left <= 0
        for patient_icon in patients_to_remove:
            self.canvas.delete(patient_icon)
            self.patient_widgets.remove(patient_icon)

        # Inform the user
        healed_message = (
            f"The time has been updated to: {self.current_time.strftime("%H:%M")} - {(self.current_time+datetime.timedelta(hours=1)).strftime("%H:%M")}.\n\n"
        )
        if healed_patients:
            healed_message += "Patients healed and removed:\n" + "\n".join(healed_patients)
        else:
            healed_message += "No patients have been healed this hour."

        messagebox.showinfo("Time Updated", healed_message)

        # Add new patients for the next hour
        self.add_new_patients()

    def add_new_patients(self):
        """Add new patients to the waiting room for the current hour."""
        # Generate new patients for each type (A, B, C)
        for patient_type in ["A", "B", "C"]:
            num_patients = self.determine_patient_count(patient_type)
            for _ in range(num_patients):
                arrival_time = self.current_time.strftime("%H:%M:%S")
                patient_profile = self.patient_generator.generate_patient_profile(arrival_time, patient_type)
                self.create_patient_widget(patient_profile)



    def determine_patient_count(self, patient_type):
        """Determine the number of patients for a given type based on the distribution."""
        params = self.distribution_parameters[patient_type]
        if self.distribution_type == "Poisson":
            return np.random.poisson(params["lambda"])
        elif self.distribution_type == "Uniform":
            return random.randint(params["lower_bound"], params["upper_bound"])
        elif self.distribution_type == "Normal":
            return max(1, int(random.gauss(params["mean"], params["std_dev"])))  # Ensure at least 1 patient


    def create_patient_widget(self, patient_profile):
        """Create a draggable patient icon and display it in the waiting room."""
        # Define the Waiting Room boundaries (adjust based on your layout)
        waiting_room_x_start = 10
        waiting_room_x_end = 790  # Slightly less than canvas width to stay inside the room
        waiting_room_y_start = 10
        waiting_room_y_end = 90   # Matches the height of the Waiting Room

        # Calculate the spacing for patient icons
        total_patients = len(self.patient_widgets)
        spacing = 30  # Space between patient icons
        x = waiting_room_x_start + (total_patients % ((waiting_room_x_end - waiting_room_x_start) // spacing)) * spacing
        y = waiting_room_y_start + (total_patients // ((waiting_room_x_end - waiting_room_x_start) // spacing)) * spacing

        # Ensure icons don't go outside the Waiting Room
        if y > waiting_room_y_end - 20:  # 20 is the size of the patient icon
            y = waiting_room_y_start  # Wrap to the next row
            x = waiting_room_x_start + (total_patients % ((waiting_room_x_end - waiting_room_x_start) // spacing)) * spacing

        # Determine the color based on the acuity level
        acuity_level = patient_profile["acuity_level"]
        if acuity_level == "High":
            color = "purple"
        elif acuity_level == "Medium":
            color = "pink"
        else:  # Low
            color = "white"

        # Create the patient icon
        patient_icon = self.canvas.create_oval(
            x, y, x + 20, y + 20, fill=color,
            tags=(f"patient_{len(self.patient_widgets)}", patient_profile["patient_type"], f"hours_left_{patient_profile['hours_left']}")
        )

        # Make the patient draggable
        self.canvas.tag_bind(f"patient_{len(self.patient_widgets)}", "<Button-1>", self.on_drag_start)
        self.canvas.tag_bind(f"patient_{len(self.patient_widgets)}", "<B1-Motion>", self.on_drag_move)
        self.canvas.tag_bind(f"patient_{len(self.patient_widgets)}", "<ButtonRelease-1>", self.on_drag_end)

        self.patient_widgets.append(patient_icon)


    def on_drag_start(self, event):
        """Start dragging a patient."""
        self.dragging_patient = self.canvas.find_withtag("current")[0]

    def on_drag_move(self, event):
        """Move the patient with the mouse."""
        if self.dragging_patient:
            self.canvas.coords(self.dragging_patient, event.x - 10, event.y - 10, event.x + 10, event.y + 10)

    def on_drag_end(self, event):
        """Snap the patient to the nearest room or back to the waiting room with type restrictions."""
        if self.dragging_patient:
            # Get the patient type from the tags
            tags = self.canvas.gettags(self.dragging_patient)
            patient_type = next(tag for tag in tags if tag in ["A", "B", "C"])

            # Iterate through grid cells to find a valid placement
            for x1, y1, x2, y2 in self.grid_cells:
                if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                    # Check if this cell contains a room
                    for room_name, characteristics in self.rooms.items():
                        room_rect = self.canvas.find_withtag(room_name)
                        if room_rect:  # Room exists on the canvas
                            room_coords = self.canvas.coords(room_rect)
                            if (
                                room_coords[0] == x1
                                and room_coords[1] == y1
                                and room_coords[2] == x2
                                and room_coords[3] == y2
                            ):
                                room_type = room_name[0]  # Room type is the first letter of the room name
                                
                                # Apply type-based placement restrictions
                                if (
                                    (patient_type == "A" and room_type != "A") or
                                    (patient_type == "B" and room_type not in ["A", "B"])
                                ):
                                    messagebox.showerror(
                                        "Invalid Placement",
                                        f"Patient of type {patient_type} cannot be placed in room type {room_type}."
                                    )
                                    self.snap_to_waiting_room()
                                    return

                                # Snap to the room if placement is valid
                                self.canvas.coords(self.dragging_patient, x1 + 10, y1 + 10, x1 + 30, y1 + 30)
                                self.dragging_patient = None
                                return

            # If no valid room was found, snap back to the waiting room
            self.snap_to_waiting_room()

    def snap_to_waiting_room(self):
        """Snap the dragged patient back to the waiting room."""
        index = self.patient_widgets.index(self.dragging_patient)
        x = 50 + index * 100
        self.canvas.coords(self.dragging_patient, x, 20, x + 20, 40)
        self.dragging_patient = None

    def format_time_label(self):
        """Format the current simulated time as a string."""
        next_hour = self.current_time + datetime.timedelta(hours=1)
        return f"Time: {self.current_time.strftime('%I:%M %p')} - {next_hour.strftime('%I:%M %p')}"




if __name__ == "__main__":
    app = RoomPlanner()
    app.mainloop()
