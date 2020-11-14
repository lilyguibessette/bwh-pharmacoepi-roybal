


def write_data(patient_records):
    new_file = str(datetime.now().strftime('%Y_%m_%d'))
    new_file = "PatientTrialData_" + new_file
    out_file = open(new_file, "w")
    out_file.write('variable headings')
    for patient in patient_records:
        out_file.write(patient + '\n')
    out_file.close()