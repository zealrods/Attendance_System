import pandas as pd

# Load the attendance data from the CSV file
attendance = pd.read_csv('Attendance_Sheet.csv')

# Calculate the defaulters list
threshold = 2
attendance['Defaulters'] = attendance.iloc[:,2:].sum(axis=1) < threshold
attendance.loc[attendance['Defaulters'], 'Defaulters'] = True

# Save the attendance report to a new CSV file
attendance.to_csv('Attendance_Report.csv', index=False)
