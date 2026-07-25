#!/bin/bash

# Define the JSON and database file names
json_file="gym_exercise_dataset.json"
database="exercise.db"
table="exercises"
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

# Read the JSON file and insert data into SQLite
jq -c '.[]' $json_file | while read -r row; do
  Exercise_Name=$(echo $row | jq -r '.Exercise_Name // "" | gsub("'"'"'"; "''")')
  Equipment=$(echo $row | jq -r '.Equipment // "" | gsub("'"'"'"; "''")')
  Variation=$(echo $row | jq -r '.Variation // "" | gsub("'"'"'"; "''")')
  Utility=$(echo $row | jq -r '.Utility // "" | gsub("'"'"'"; "''")')
  Mechanics=$(echo $row | jq -r '.Mechanics // "" | gsub("'"'"'"; "''")')
  Force=$(echo $row | jq -r '.Force // "" | gsub("'"'"'"; "''")')
  Preparation=$(echo $row | jq -r '.Preparation // "" | gsub("'"'"'"; "''")')
  Execution=$(echo $row | jq -r '.Execution // "" | gsub("'"'"'"; "''")')
  Target_Muscles=$(echo $row | jq -r '.Target_Muscles // "" | gsub("'"'"'"; "''")')
  Synergist_Muscles=$(echo $row | jq -r '.Synergist_Muscles // "" | gsub("'"'"'"; "''")')
  Stabilizer_Muscles=$(echo $row | jq -r '.Stabilizer_Muscles // "" | gsub("'"'"'"; "''")')
  Antagonist_Muscles=$(echo $row | jq -r '.Antagonist_Muscles // "" | gsub("'"'"'"; "''")')
  Dynamic_Stabilizer_Muscles=$(echo $row | jq -r '.Dynamic_Stabilizer_Muscles // "" | gsub("'"'"'"; "''")')
  Main_muscle=$(echo $row | jq -r '.Main_muscle // "" | gsub("'"'"'"; "''")')
  Difficulty=$(echo $row | jq -r '.Difficulty // "" | gsub("'"'"'"; "''")')
  Secondary_Muscles=$(echo $row | jq -r '.Secondary_Muscles // "" | gsub("'"'"'"; "''")')
  parent_id=$(echo $row | jq -r '.parent_id // "" | gsub("'"'"'"; "''")')

  sqlite3 $database <<EOF
  INSERT INTO $table (Exercise_Name, Equipment, Variation, Utility, Mechanics, Force, Preparation, Execution, Target_Muscles, Synergist_Muscles, Stabilizer_Muscles, Antagonist_Muscles, Dynamic_Stabilizer_Muscles, Main_muscle, Difficulty, Secondary_Muscles, parent_id)
  VALUES ('$Exercise_Name', '$Equipment', '$Variation', '$Utility', '$Mechanics', '$Force', '$Preparation', '$Execution', '$Target_Muscles', '$Synergist_Muscles', '$Stabilizer_Muscles', '$Antagonist_Muscles', '$Dynamic_Stabilizer_Muscles', '$Main_muscle', '$Difficulty', '$Secondary_Muscles', '$parent_id');
EOF
done

# Check for errors during the insertion process
if [ $? -eq 0 ]; then
  echo "Data imported successfully from '$json_file' to '$database'."
else
  echo "Failed to import data from '$json_file' to '$database'. Check '$log_file' for details."
fi