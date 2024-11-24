import random
import datetime

class PatientGenerator:
    def __init__(self):
        # Sample data for generating random names
        self.first_names = ["John", "Jane", "Alex", "Emily", "Chris", "Pat", "Taylor", "Jordan"]
        self.last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]

    def generate_patient_profile(self, arrival_time, patient_type):
        """Generate a patient profile based on the patient type."""
        # Determine acuity level and hours left based on the patient type
        if patient_type == "A":
            acuity_level = "High"
            hours_left = 4
        elif patient_type == "B":
            acuity_level = "Medium"
            hours_left = 3
        elif patient_type == "C":
            acuity_level = "Low"
            hours_left = 2
        else:
            raise ValueError(f"Invalid patient type: {patient_type}")

        # Generate a random name
        first_name = random.choice(self.first_names)
        last_name = random.choice(self.last_names)

        # Create the patient profile as a dictionary
        patient_profile = {
            "acuity_level": acuity_level,
            "arrival_time": arrival_time,
            "being_served": False,
            "hours_left": hours_left,
            "patient_type": patient_type
        }

        return patient_profile

# Example usage
if __name__ == "__main__":
    patient_generator = PatientGenerator()
    # Generate 5 sample patient profiles with the current time as the arrival time
    for _ in range(5):
        arrival_time = datetime.datetime.now().strftime("%H:%M:%S")
        patient = patient_generator.generate_patient_profile(arrival_time)
        print(patient)
