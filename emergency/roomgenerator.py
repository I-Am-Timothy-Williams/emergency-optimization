class RoomManager:
    def generate_rooms(self, a_count, b_count, c_count):
        # Initialize an empty dictionary to store room characteristics
        rooms = {}

        # Generate A type rooms
        for i in range(1, a_count + 1):
            room_name = f"A{i}"
            rooms[room_name] = {"type": "A", "capacity": 1, "priority": "High", "occupied": False, "time_in_room": 0, "cost_per_day": 3900}

        # Generate B type rooms
        for i in range(1, b_count + 1):
            room_name = f"B{i}"
            rooms[room_name] = {"type": "B", "capacity": 1, "priority": "Medium", "occupied": False, "time_in_room": 0, "cost_per_day": 3000}

        # Generate C type rooms
        for i in range(1, c_count + 1):
            room_name = f"C{i}"
            rooms[room_name] = {"type": "C", "capacity": 1, "priority": "Low", "occupied": False, "time_in_room": 0, "cost_per_day": 1600}

        # Create Waiting Room
        room_name = "WaitingRoom"
        rooms[room_name] = {
            "type": "WaitingRoom",
            "capacity": 100,  # Large capacity for many patients
            "patients": []    # List to store patient info dictionaries
        }

        return rooms

    def update_room(self, rooms, room_name, occupied_status=None, time_increment=None, patient_info=None):
        # Check if the room exists in the dictionary
        if room_name not in rooms:
            print(f"Room {room_name} does not exist.")
            return

        # Update the room's 'occupied' status if provided
        if occupied_status is not None:
            rooms[room_name]["occupied"] = occupied_status

        # Increment the 'time_in_room' if a time increment is provided
        if time_increment is not None:
            rooms[room_name]["time_in_room"] += time_increment

        # Add patient info to the room (used for assigning a patient)
        if patient_info is not None and room_name != "WaitingRoom":
            if not rooms[room_name]["occupied"]:
                rooms[room_name]["occupied"] = True
                rooms[room_name]["patient_info"] = patient_info  # Add patient info to the room
                print(f"Patient {patient_info} has been assigned to {room_name}.")
            else:
                print(f"Room {room_name} is already occupied.")

    def add_patient_to_waiting_room(self, rooms, patient_info):
        # Add patient info to the Waiting Room
        rooms["WaitingRoom"]["patients"].append(patient_info)
        print(f"Patient {patient_info} added to the Waiting Room.")

# Example usage
if __name__ == "__main__":
    manager = RoomManager()
    rooms = manager.generate_rooms(2, 2, 2)
    manager.add_patient_to_waiting_room(rooms, {"name": "John Doe", "acuity_level": "High", "arrival_time": "10:00 AM"})
    manager.update_room(rooms, "A1", occupied_status=True, time_increment=30, patient_info={"name": "Jane Smith", "acuity_level": "Medium"})

    # Display the updated rooms
    print("Updated Rooms:")
    for room, characteristics in rooms.items():
        print(f"{room}: {characteristics}")
