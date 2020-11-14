


def import_redcap(filepath):
    print("Importing patient RedCap data")
    redcap = pd.read_csv(filepath)
    return redcap