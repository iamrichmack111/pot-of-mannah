# Food Data and Measurements

## Canonical unit

Food nutrient values are normalized to **per 100 grams**. Logged portions are calculated as:

```text
portion nutrient = nutrient per 100 g × grams eaten ÷ 100
```

Example:

```text
291 kcal / 100 g × 700 g = 2,037 kcal
```

The app stores the exact grams eaten and a nutrient snapshot for the logged portion. Historical logs therefore do not silently change if a source food record is updated later.

## Food sources

- Pot of Mannah local food database
- User-created custom foods
- USDA FoodData Central search
- Open Food Facts packaged-food search

Remote foods can be imported into the local user library.
