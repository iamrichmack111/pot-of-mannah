#!/bin/bash

# Define the SQLite database file and CSV file
DB_FILE="food.db"
CSV_FILE="food.csv"

# Define the table creation SQL statement
SQL_SCRIPT=$(cat <<EOF
DROP TABLE IF EXISTS food_data;

CREATE TABLE food_data (
    Category TEXT,
    Description TEXT,
    Nutrient_Data_Bank_Number TEXT,
    Data_Alpha_Carotene TEXT,
    Data_Ash TEXT,
    Data_Beta_Carotene TEXT,
    Data_Beta_Cryptoxanthin TEXT,
    Data_Carbohydrate TEXT,
    Data_Cholesterol TEXT,
    Data_Choline TEXT,
    Data_Fiber TEXT,
    Data_Kilocalories TEXT,
    Data_Lutein_and_Zeaxanthin TEXT,
    Data_Lycopene TEXT,
    Data_Manganese TEXT,
    Data_Niacin TEXT,
    Data_Pantothenic_Acid TEXT,
    Data_Protein TEXT,
    Data_Refuse_Percentage TEXT,
    Data_Retinol TEXT,
    Data_Riboflavin TEXT,
    Data_Selenium TEXT,
    Data_Sugar_Total TEXT,
    Data_Thiamin TEXT,
    Data_Water TEXT,
    Data_Fat_Monosaturated_Fat TEXT,
    Data_Fat_Polysaturated_Fat TEXT,
    Data_Fat_Saturated_Fat TEXT,
    Data_Fat_Total_Lipid TEXT,
    Data_Household_Weights_1st_Household_Weight TEXT,
    Data_Household_Weights_1st_Household_Weight_Description TEXT,
    Data_Household_Weights_2nd_Household_Weight TEXT,
    Data_Household_Weights_2nd_Household_Weight_Description TEXT,
    Data_Major_Minerals_Calcium TEXT,
    Data_Major_Minerals_Copper TEXT,
    Data_Major_Minerals_Iron TEXT,
    Data_Major_Minerals_Magnesium TEXT,
    Data_Major_Minerals_Phosphorus TEXT,
    Data_Major_Minerals_Potassium TEXT,
    Data_Major_Minerals_Sodium TEXT,
    Data_Major_Minerals_Zinc TEXT,
    Data_Vitamins_Vitamin_A_IU TEXT,
    Data_Vitamins_Vitamin_A_RAE TEXT,
    Data_Vitamins_Vitamin_B12 TEXT,
    Data_Vitamins_Vitamin_B6 TEXT,
    Data_Vitamins_Vitamin_C TEXT,
    Data_Vitamins_Vitamin_E TEXT,
    Data_Vitamins_Vitamin_K TEXT
);
EOF
)

# Create the SQLite database and table
sqlite3 "$DB_FILE" "$SQL_SCRIPT"

# Import the CSV data into the SQLite table
sqlite3 "$DB_FILE" <<EOF
.mode csv
.separator ","
.import $CSV_FILE food_data
EOF

echo "Database created and CSV data imported successfully."
