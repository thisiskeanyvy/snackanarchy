class Ingredient:
    def __init__(self, name, type, is_dirty=False, effect=None):
        self.name = name
        self.type = type # base, dirty
        self.is_dirty = is_dirty
        self.effect = effect # Dictionary of impacts e.g., {'reputation': -10}

class Dish:
    def __init__(self, name, base_ingredients):
        self.name = name
        self.base_ingredients = base_ingredients
        self.added_ingredients = []
        
    def add_ingredient(self, ingredient):
        self.added_ingredients.append(ingredient)
        
    def is_valid(self):
        # Check if all base ingredients are present
        base_names = [i.name for i in self.base_ingredients]
        added_names = [i.name for i in self.added_ingredients]
        return all(name in added_names for name in base_names)
        
    def get_quality_score(self):
        score = 100
        for ing in self.added_ingredients:
            if ing.is_dirty:
                score -= 20
        return max(0, score)

# Predefined Dishes
def create_tacos_xxl():
    base = [
        Ingredient("Galette de blé", "base"),
        Ingredient("Viande", "base"),
        Ingredient("Sauce fromagère", "base"),
        Ingredient("Frites", "base"),
        Ingredient("Sel", "base")
    ]
    return Dish("Tacos XXL", base)

def create_kebab():
    base = [
        Ingredient("Pain pita", "base"),
        Ingredient("Viande kebab", "base"),
        Ingredient("Salade", "base"),
        Ingredient("Tomates", "base"),
        Ingredient("Oignons", "base")
    ]
    return Dish("Kebab", base)

# Dirty Ingredients
DIRTY_INGREDIENTS = [
    Ingredient("Sauce périmée", "dirty", True, {'symptoms': 0.8, 'reputation': -10}),
    Ingredient("Trop de fromage", "dirty", True, {'eating_time': 1.5}),
    Ingredient("Frites brûlées", "dirty", True, {'reputation': -5}),
    Ingredient("Hygiène douteuse", "dirty", True, {'inspection_risk': 0.5}),
    Ingredient("Viande trop cuite", "dirty", True, {'quality': -20}),
    Ingredient("Sauce coupée à l'eau", "dirty", True, {'quality': -10, 'money': 2}), # Saves money?
    Ingredient("Salade flétrie", "dirty", True, {'quality': -5}),
]
