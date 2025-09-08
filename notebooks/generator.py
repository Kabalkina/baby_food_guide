import pandas as pd
import random
from itertools import product

# -------------------- Curated recipe bases (realistic) --------------------
# These reflect common baby/toddler recipes seen across NHS/BBC Good Food/parenting sites.
# We DO NOT copy any wording; instructions added below are original and standardized.
STAGES = {
    "stage1_purees": {
        "ages": ["6-8 months", "7-10 months"],
        "texture": "Purée",
        "meals": ["Breakfast", "Lunch", "Snack"],
        "items": [
            ("Sweet Potato Purée", ["sweet potato", "water or breastmilk/formula"]),
            ("Carrot Purée", ["carrot", "water or breastmilk/formula"]),
            ("Pumpkin Purée", ["pumpkin", "water or breastmilk/formula"]),
            ("Pea Purée", ["peas", "water"]),
            ("Zucchini Purée", ["zucchini", "water"]),
            ("Broccoli Purée", ["broccoli", "water"]),
            ("Apple Purée", ["apple", "water"]),
            ("Pear Purée", ["pear", "water"]),
            ("Banana Mash", ["ripe banana"]),
            ("Avocado Mash", ["ripe avocado"]),
            ("Oat Cereal with Breastmilk", ["iron-fortified oats", "breastmilk or formula"]),
        ],
    },
    "stage2_combos": {
        "ages": ["7-10 months", "8-12 months", "9-12 months"],
        "texture": "Purée",
        "meals": ["Lunch", "Dinner"],
        "items": [
            ("Sweet Potato & Carrot Purée", ["sweet potato", "carrot", "water"]),
            ("Apple & Pear Oat Purée", ["apple", "pear", "oats", "water or milk"]),
            ("Pumpkin & Red Lentil Purée", ["pumpkin", "red lentils", "water", "olive oil"]),
            ("Pea & Potato Purée", ["peas", "potato", "water"]),
            ("Chicken & Veggie Purée", ["chicken breast", "carrot", "peas", "water"]),
            ("Salmon & Sweet Potato Purée", ["salmon", "sweet potato", "peas", "water"]),
            ("Turkey & Pumpkin Purée", ["turkey", "pumpkin", "water"]),
            ("Cod & Zucchini Purée", ["cod", "zucchini", "potato", "water"]),
            ("Chickpea & Carrot Purée", ["chickpeas", "carrot", "water", "olive oil"]),
            ("Tofu & Broccoli Purée", ["tofu", "broccoli", "water"]),
        ],
    },
    "stage3_mashes_soft": {
        "ages": ["9-12 months", "10-14 months", "12-18 months"],
        "texture": "Mash",
        "meals": ["Lunch", "Dinner"],
        "items": [
            ("Broccoli & Potato Mash", ["broccoli", "potato", "olive oil"]),
            ("Salmon & Potato Mash", ["salmon", "potato", "broccoli", "olive oil"]),
            ("Lentil & Veggie Mash", ["red lentils", "carrot", "potato", "olive oil"]),
            ("Chicken & Rice Mash", ["chicken breast", "rice", "carrot", "peas"]),
            ("Turkey & Quinoa Mash", ["turkey", "quinoa", "zucchini"]),
            ("Chickpea & Sweet Potato Mash", ["chickpeas", "sweet potato", "spinach"]),
            ("Beef & Veggie Mash", ["beef", "potato", "carrot", "peas"]),
            ("Tofu & Veggie Mash", ["tofu", "pumpkin", "peas"]),
            ("Fish & Veggie Mash", ["white fish", "potato", "peas"]),
        ],
    },
    "finger_foods": {
        "ages": ["10-14 months", "12-18 months", "18-36 months"],
        "texture": "Finger Food",
        "meals": ["Breakfast", "Lunch", "Snack", "Dinner"],
        "items": [
            ("Mini Veggie Omelette Fingers", ["eggs", "spinach", "olive oil"]),
            ("Whole Wheat Banana Pancakes", ["whole wheat flour", "banana", "egg", "milk"]),
            ("Sweetcorn & Spinach Fritters", ["sweetcorn", "spinach", "egg", "flour"]),
            ("Mini Turkey Meatballs", ["ground turkey", "egg", "breadcrumbs", "carrot"]),
            ("Salmon Fishcakes", ["salmon", "potato", "peas", "breadcrumbs"]),
            ("Chicken & Veggie Quesadillas", ["whole wheat tortilla", "cheese", "chicken", "bell pepper"]),
            ("Veggie Muffins", ["flour", "egg", "milk", "zucchini", "carrot"]),
            ("Oat & Banana Fingers", ["oats", "banana", "yogurt"]),
            ("Cheesy Broccoli Bites", ["broccoli", "cheese", "egg", "breadcrumbs"]),
            ("Tofu Nuggets", ["tofu", "breadcrumbs", "olive oil"]),
        ],
    },
    "soft_family_meals": {
        "ages": ["12-18 months", "18-36 months"],
        "texture": "Soft Pieces",
        "meals": ["Lunch", "Dinner"],
        "items": [
            ("Chicken & Veggie Pasta", ["small pasta", "chicken", "zucchini", "tomato sauce", "cheese"]),
            ("Beef & Veggie Bolognese", ["small pasta", "beef", "tomato", "carrot", "onion"]),
            ("Mild Chickpea Curry with Rice", ["chickpeas", "pumpkin", "coconut milk", "mild curry powder", "rice"]),
            ("Turkey & Veggie Fried Rice", ["rice", "turkey", "peas", "egg"]),
            ("Vegetable Risotto", ["arborio rice", "zucchini", "peas", "parmesan"]),
            ("Fish Pie (Toddler Style)", ["white fish", "milk", "potato", "peas"]),
            ("Shepherd’s Pie Minis", ["beef or lamb", "carrot", "peas", "potato"]),
            ("Creamy Broccoli Pasta", ["small pasta", "broccoli", "cheese", "milk"]),
            ("Lentil & Tomato Stew", ["red lentils", "tomato", "carrot", "spinach"]),
            ("Vegetable Couscous Bowl", ["couscous", "zucchini", "carrot", "olive oil"]),
            ("Chicken & Veggie Soup", ["chicken", "carrot", "celery", "potato", "low-sodium stock"]),
            ("Salmon & Veggie Rice Bowl", ["salmon", "rice", "broccoli", "lemon juice"]),
        ],
    },
    "breakfasts_snacks": {
        "ages": ["8-12 months", "9-12 months", "12-18 months", "18-36 months"],
        "texture": "Soft Pieces",
        "meals": ["Breakfast", "Snack"],
        "items": [
            ("Apple Cinnamon Oatmeal", ["oats", "apple", "milk or water", "cinnamon"]),
            ("Berry & Yogurt Bowl", ["plain yogurt", "berries", "banana"]),
            ("Peanut Butter Banana Toast", ["whole wheat bread", "peanut butter", "banana"]),
            ("Chia Pudding with Mango", ["chia seeds", "milk", "mango"]),
            ("Cottage Cheese & Fruit Cup", ["cottage cheese", "pear", "banana"]),
            ("Spinach Banana Smoothie", ["spinach", "banana", "yogurt", "oats"]),
            ("Avocado Toast Fingers", ["whole wheat bread", "avocado", "olive oil"]),
            ("Scrambled Eggs & Toast", ["eggs", "olive oil", "whole wheat bread"]),
            ("Mini Waffles (Hidden Veg)", ["flour", "egg", "milk", "grated carrot"]),
            ("Overnight Oats", ["oats", "milk or yogurt", "berries"]),
        ],
    },
}

IRON_SOURCES = {
    "meat_fish": ["chicken", "turkey", "beef", "lamb", "salmon", "cod", "white fish"],
    "plant": ["red lentils", "lentils", "chickpeas", "beans", "tofu", "spinach"],
    "fortified": ["iron-fortified oats"]
}
ALLERGEN_WORDS = {
    "Dairy": ["milk", "yogurt", "cheese", "butter", "parmesan", "cottage cheese"],
    "Egg": ["egg", "eggs"],
    "Gluten": ["wheat", "flour", "pasta", "bread", "breadcrumbs", "couscous", "arborio", "oats"],
    "Fish": ["salmon", "cod", "white fish", "fish"],
    "Nuts": ["peanut", "almond", "cashew", "nut butter", "peanut butter", "almond butter"],
    "Soy": ["soy", "soy sauce", "tofu"],
}

def get_allergens(ingredients):
    ing = " ".join(ingredients).lower()
    tags = []
    for tag, keywords in ALLERGEN_WORDS.items():
        if any(k in ing for k in keywords):
            tags.append(tag)
    return "None" if not tags else ",".join(sorted(set(tags)))

def iron_rich(ingredients):
    ing = " ".join(ingredients).lower()
    for k in IRON_SOURCES:
        if any(s in ing for s in IRON_SOURCES[k]):
            return "Yes"
    return "No"

def time_and_calories(ingredients, texture, meal_type):
    ing = " ".join(ingredients).lower()
    # Time baseline
    t = {"Purée": 15, "Mash": 20, "Finger Food": 25, "Soft Pieces": 20}[texture]
    if any(p in ing for p in IRON_SOURCES["meat_fish"]):
        t += 5
    if any(g in ing for g in ["rice", "pasta", "quinoa", "couscous", "arborio"]):
        t += 5
    t = max(5, min(60, t))
    # Calories baseline
    cals = 90 if meal_type in ["Breakfast", "Snack"] else 150
    if any(p in ing for p in IRON_SOURCES["meat_fish"] + ["tofu"]):
        cals += 40
    if any(d in ing for d in ["cheese", "milk", "yogurt", "butter", "coconut milk"]):
        cals += 40
    if any(c in ing for c in ["rice", "pasta", "oats", "quinoa", "couscous", "potato", "sweet potato", "bread", "waffles", "pancakes"]):
        cals += 30
    return t, min(300, cals)

def build_instructions(ingredients, texture):
    ing_list = ", ".join(ingredients)
    steps = []
    steps.append(f"Wash and prep ingredients: {ing_list}.")
    lower = " ".join(ingredients).lower()
    if any(x in lower for x in ["rice", "pasta", "arborio", "couscous", "oats"]):
        steps.append("Cook grains in plenty of water or milk (no added salt) until very soft.")
    if any(x in lower for x in ["lentils", "chickpeas", "beans"]):
        steps.append("Rinse pulses; simmer until tender and skins split easily.")
    if any(x in lower for x in ["chicken", "turkey", "beef", "lamb"]):
        steps.append("Dice meat small and simmer/steam until fully cooked through (juices run clear).")
    if any(x in lower for x in ["salmon", "cod", "white fish", "fish"]):
        steps.append("Steam fish until it flakes; carefully remove any bones.")
    steps.append("Steam or gently simmer vegetables/fruit until fork-tender.")
    if texture == "Purée":
        steps.append("Blend with a splash of cooking water or breastmilk/formula until smooth.")
    elif texture == "Mash":
        steps.append("Drain and mash to a soft, lumpy texture that holds together.")
    elif texture == "Finger Food":
        steps.append("Shape into small patties/strips and cook on low heat or bake until set and soft inside.")
    elif texture == "Soft Pieces":
        steps.append("Chop into pea-sized pieces and cook until very tender; pieces should squash between fingers.")
    steps.append("Cool before serving. Store in the fridge up to 2 days or freeze portions up to 1 month.")
    return " ".join(steps)

def difficulty_by_time(t):
    return "Easy" if t <= 20 else "Medium"

# Add a single row per named dish to avoid duplicates
def add_named_recipe(rows, seen_names, name, age, texture, meal_type, ingredients):
    if name in seen_names:
        return
    allergens = get_allergens(ingredients)
    iron = iron_rich(ingredients)
    t, cal = time_and_calories(ingredients, texture, meal_type)
    instr = build_instructions(ingredients, texture)
    rows.append([
        name, age, iron, allergens, ", ".join(ingredients),
        t, instr, texture, meal_type, cal, difficulty_by_time(t)
    ])
    seen_names.add(name)

# Seed with one canonical row per base item
rows, seen = [], set()
for g in STAGES.values():
    for (name, ing) in g["items"]:
        # pick the first sensible (age, meal) combo to create a single canonical entry
        add_named_recipe(rows, seen, name, g["ages"][0], g["texture"], g["meals"][0], ing)

# Build realistic variants (ingredient swaps + name update)
def smart_variant(base_name, base_ing, texture, ages, meals, swaps, label=None):
    new_ing = []
    for item in base_ing:
        repl = item
        l = item.lower()
        for old, new in swaps:
            if old in l:
                l = l.replace(old, new)
        new_ing.append(l)
    # craft a name reflecting the key swapped ingredient if present
    new_name = base_name
    for old, new in swaps:
        new_name = new_name.replace(old.title(), new.title()).replace(old, new.title())
    if new_name == base_name and label:
        new_name = f"{base_name} ({label})"
    # choose sensible (age, meal)
    age = ages[min(0, 0)]
    meal = meals[min(0, 0)]
    return new_name, new_ing, age, meal, texture

veg_swaps = [("carrot","parsnip"),("zucchini","courgette"),("pumpkin","butternut squash"),
             ("broccoli","cauliflower"),("spinach","kale"),("peas","sweetcorn")]
protein_swaps = [("chicken","turkey"),("beef","lamb"),("salmon","cod"),("white fish","cod"),("tofu","chickpeas")]
grain_swaps = [("rice","quinoa"),("pasta","small pasta"),("couscous","millet")]

labels = ["Family Style","Toddler Favorite","Hidden Veg","Freezer-Friendly","Mild Curry","One-Pot"]

def expand_from_bases(target_count=500):
    global rows, seen
    # generate variants for each group
    for key, g in STAGES.items():
        for (name, ing) in g["items"]:
            # make a handful of safe variants
            for swaps in [
                [random.choice(veg_swaps)],
                [random.choice(protein_swaps)] if any(p in " ".join(ing).lower() for p in ["chicken","turkey","beef","lamb","salmon","cod","fish","tofu"]) else [],
                [random.choice(grain_swaps)] if any(p in " ".join(ing).lower() for p in ["rice","pasta","couscous"] ) else [],
            ]:
                if not swaps:
                    continue
                new_name, new_ing, age, meal, texture = smart_variant(name, ing, g["texture"], g["ages"], g["meals"], swaps, random.choice(labels))
                add_named_recipe(rows, seen, new_name, g["ages"][0], g["texture"], g["meals"][0], new_ing)
            # labeled variant without ingredient change
            labeled = f"{name} ({random.choice(labels)})"
            add_named_recipe(rows, seen, labeled, g["ages"][-1], g["texture"], g["meals"][-1], ing)

    # If we still need more, create extra descriptive variants safely
    safe_suffixes = ["No-Salt", "Extra Soft", "Olive Oil Drizzle", "Steamed", "Baked", "Slow Simmered"]
    i = 0
    base_list = [(k, item, g) for k, g in STAGES.items() for item in g["items"]]
    while len(rows) < target_count and i < 10000:
        i += 1
        k, (name, ing), g = random.choice(base_list)
        suffix = random.choice(safe_suffixes)
        new_name = f"{name} ({suffix})"
        if new_name in seen:
            continue
        add_named_recipe(rows, seen, new_name, random.choice(g["ages"]), g["texture"], random.choice(g["meals"]), ing)

expand_from_bases(target_count=500)

# Ensure exactly 500 unique dish names
df = pd.DataFrame(rows, columns=[
    "Dish Name","Baby Age","Iron-Rich","Allergen","Ingredients","Cooking Time (mins)",
    "Recipe","Texture","Meal Type","Calories (approx)","Preparation Difficulty"
]).drop_duplicates(subset=["Dish Name"]).head(500)

# Save CSV with semicolon separator
out_path = "../data/baby_recipes_500.csv"
df.to_csv(out_path, sep=";", index=False)
print(f"Created {len(df)} recipes -> {out_path}")
