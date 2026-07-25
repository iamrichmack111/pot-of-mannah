#!/bin/bash

# Define the database, table, and CSV file name
database="exercise.db"
table="exercises"
csv_file="gym_exercise_dataset.csv"
cleaned_csv_file="cleaned_gym_exercise_dataset.csv"
log_file="import_errors.log"

# Define the columns and their types
columns="id INTEGER PRIMARY KEY AUTOINCREMENT,
Exercise_Name TEXT,
Equipment TEXT,
Variation TEXT,
Utility TEXT,
Mechanics TEXT,
Force TEXT,
Preparation TEXT,
Execution TEXT,
Target_Muscles TEXT,
Synergist_Muscles TEXT,
Stabilizer_Muscles TEXT,
Antagonist_Muscles TEXT,
Dynamic_Stabilizer_Muscles TEXT,
Main_muscle TEXT,
Difficulty INTEGER,
Secondary_Muscles TEXT,
parent_id TEXT"

# Clean the CSV file to ensure all rows have 18 columns and handle empty columns
awk -F, 'BEGIN {OFS=FS} {
    if (NR == 1) {print; next}
    if (NF < 18) {
        for (i=NF+1; i<=18; i++) {
            $i = "";
        }
    } else if (NF > 18) {
        for (i=19; i<=NF; i++) {
            $(18) = $(18) "," $i
        }
        NF=18
    }
    print $0;
}' $csv_file > $cleaned_csv_file

# Create the SQLite3 database and table
sqlite3 $database <<EOF
DROP TABLE IF EXISTS $table;
CREATE TABLE $table ($columns);
EOF

# Confirm the creation of the database and table
if [ $? -eq 0 ]; then
  echo "SQLite3 database '$database' and table '$table' created successfully."
else
  echo "Failed to create the SQLite3 database and table."
  exit 1
fi

# Import the cleaned CSV data into the table
sqlite3 $database <<EOF 2> $log_file
.mode csv
.import $cleaned_csv_file $table
EOF

# Check for errors during import
if [ -s $log_file ]; then
  echo "Failed to import some data from '$cleaned_csv_file'. Check '$log_file' for details."
else
  echo "Data imported successfully from '$cleaned_csv_file' to '$database'."
  rm $log_file
fi

# Clean up the temporary cleaned CSV file
rm $cleaned_csv_file