CREATE TABLE IF NOT EXISTS meals (
    id INTEGER PRIMARY KEY,
    meal_date TEXT NOT NULL,
    food_name TEXT NOT NULL CHECK (length(trim(food_name)) > 0),
    category TEXT NOT NULL CHECK (category IN ('Breakfast','Lunch','Dinner','Snacks')),
    calories_hundredths INTEGER NOT NULL CHECK (typeof(calories_hundredths) = 'integer' AND calories_hundredths >= 0),
    protein_hundredths INTEGER NOT NULL CHECK (typeof(protein_hundredths) = 'integer' AND protein_hundredths >= 0)
);
CREATE INDEX IF NOT EXISTS meals_date ON meals(meal_date);
CREATE TABLE IF NOT EXISTS nutrition_targets (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    calorie_target_hundredths INTEGER CHECK (calorie_target_hundredths IS NULL OR (typeof(calorie_target_hundredths) = 'integer' AND calorie_target_hundredths > 0)),
    protein_target_hundredths INTEGER CHECK (protein_target_hundredths IS NULL OR (typeof(protein_target_hundredths) = 'integer' AND protein_target_hundredths > 0))
);
INSERT INTO nutrition_targets(id) VALUES(1) ON CONFLICT(id) DO NOTHING;
CREATE TABLE IF NOT EXISTS submission_receipts (
    submission_key TEXT PRIMARY KEY NOT NULL,
    operation TEXT NOT NULL,
    resource_id INTEGER,
    payload_json TEXT NOT NULL,
    redirect_path TEXT NOT NULL
);