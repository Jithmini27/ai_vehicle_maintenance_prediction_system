from ai_engine.predict import predict_maintenance

sample_data = {
    "Vehicle_Model": "SUV",
    "Mileage": 60000,
    "Maintenance_History": "Good",
    "Reported_Issues": 2,
    "Vehicle_Age": 5,
    "Fuel_Type": "Petrol",
    "Transmission_Type": "Automatic",
    "Engine_Size": 2000,
    "Odometer_Reading": 85000,
    "Last_Service_Date": "2023-08-10",
    "Warranty_Expiry_Date": "2026-08-10",
    "Owner_Type": "First",
    "Insurance_Premium": 50000,
    "Service_History": 4,
    "Accident_History": 0,
    "Fuel_Efficiency": 14.5,
    "Tire_Condition": "Good",
    "Brake_Condition": "Good",
    "Battery_Status": "Good"
}

result = predict_maintenance(sample_data)
print(result)