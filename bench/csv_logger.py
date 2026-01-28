import csv
import os

class CSVLogger:
    def __init__(self, filename, fieldnames):
        self.filename = filename
        self.fieldnames = fieldnames
        self._exists = os.path.isfile(filename)

    def write_row(self, row):
        with open(self.filename, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)

            if not self._exists:
                writer.writeheader()
                self._exists = True

            writer.writerow(row)
