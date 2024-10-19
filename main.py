import sqlite3
import tkinter as tk
from tkinter import ttk
import math


class RecipeManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Recipe Manager")

        # Set the initial size of the window
        self.root.geometry("1600x600")

        # Create a menu bar
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        # Create a File menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        # Add options to the File menu
        self.file_menu.add_command(label="Add Ingredients", command=self.open_ingredient_manager)
        self.file_menu.add_command(label="Calculate", command=self.open_calculator)
        self.file_menu.add_separator()  # Optional: add a separator line
        self.file_menu.add_command(label="Exit", command=self.root.quit)

        # Existing canvas and scrollbar setup
        self.canvas = tk.Canvas(self.root)
        self.scrollbar = tk.Scrollbar(self.root, orient="horizontal", command=self.canvas.xview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(xscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="top", fill="both", expand=True)
        self.scrollbar.pack(side="bottom", fill="x")

        self.add_recipe_button = tk.Button(self.root, text="Add Recipe", command=self.add_recipe)
        self.add_recipe_button.pack(pady=10)

        self.recipes = []

        self.load_recipes()

    def load_recipes(self):
        cur.execute('SELECT recipe_name, ingredients, servings FROM recipes')
        rows = cur.fetchall()
        for row in rows:
            recipe_name = row[0]
            ingredients = row[1]
            servings = row[2]
            self.add_recipe_from_db(recipe_name, ingredients, servings)

    def add_recipe_from_db(self, dish_name, ingredients, servings):
        recipe_row = tk.Frame(self.scrollable_frame)
        recipe_row.pack(fill=tk.X, pady=5)

        confirm_button = tk.Button(recipe_row, text="Confirm", command=lambda: self.confirm_recipe(recipe_row))
        confirm_button.pack(side=tk.LEFT, padx=5)

        dish_name_entry = tk.Entry(recipe_row, width=20)
        dish_name_entry.insert(0, dish_name)
        dish_name_entry.pack(side=tk.LEFT, padx=5)

        servings_entry = tk.Entry(recipe_row, width=5)
        servings_entry.insert(0, servings)
        servings_entry.pack(side=tk.LEFT, padx=5)

        ingredient_parts = ingredients.split('Ingredient: ')[1:]  # Split by 'Ingredient: ' and skip the first part
        for part in ingredient_parts:
            quantity, measurement, ingredient = part.split()[:3]
            self.create_ingredient_entry_from_db(recipe_row, quantity, measurement, ingredient)

        add_ingredient_button = tk.Button(recipe_row, text="Add Ingredient",
                                          command=lambda: self.add_ingredient(recipe_row, add_ingredient_button))
        add_ingredient_button.pack(side=tk.LEFT, padx=5)

        self.recipes.append(recipe_row)

    def create_ingredient_entry_from_db(self, parent, quantity, measurement, ingredient):
        quantity_entry = tk.Entry(parent, width=5)
        quantity_entry.insert(0, quantity)
        quantity_entry.pack(side=tk.LEFT, padx=5)

        ingredient_combobox = ttk.Combobox(parent, values=ingredient_options, width=10, state='readonly')
        ingredient_combobox.set(ingredient)
        ingredient_combobox.pack(side=tk.LEFT, padx=5)

        measurement_combobox = ttk.Combobox(parent, values=measurement_options, width=10, state='readonly')
        measurement_combobox.set(measurement)
        measurement_combobox.pack(side=tk.LEFT, padx=5)

    def add_recipe(self):
        recipe_row = tk.Frame(self.scrollable_frame)
        recipe_row.pack(fill=tk.X, pady=5)

        confirm_button = tk.Button(recipe_row, text="Confirm", command=lambda: self.confirm_recipe(recipe_row))
        confirm_button.pack(side=tk.LEFT, padx=5)

        dish_name = tk.Entry(recipe_row, width=20)
        dish_name.pack(side=tk.LEFT, padx=5)

        servings_entry = tk.Entry(recipe_row, width=5)
        servings_entry.pack(side=tk.LEFT, padx=5)

        for _ in range(3):  # Create initial 3 sets of ingredients, quantity, and measurement
            self.create_ingredient_entry(recipe_row)

        add_ingredient_button = tk.Button(recipe_row, text="Add Ingredient",
                                          command=lambda: self.add_ingredient(recipe_row, add_ingredient_button))
        add_ingredient_button.pack(side=tk.LEFT, padx=5)

        self.recipes.append(recipe_row)

    def create_ingredient_entry(self, parent):
        quantity = tk.Entry(parent, width=5)
        quantity.pack(side=tk.LEFT, padx=5)

        ingredient = ttk.Combobox(parent, values=ingredient_options, width=10, state='readonly')
        ingredient.pack(side=tk.LEFT, padx=5)

        measurement = ttk.Combobox(parent, values=measurement_options, width=10, state='readonly')
        measurement.pack(side=tk.LEFT, padx=5)

    def add_ingredient(self, parent, add_button):
        self.create_ingredient_entry(parent)
        add_button.pack_forget()  # Remove the button temporarily
        add_button.pack(side=tk.LEFT, padx=5)  # Re-add the button at the end

    def confirm_recipe(self, recipe_row):
        recipe_data = []
        children = recipe_row.winfo_children()
        dish_name = children[1].get()
        servings = children[2].get()
        recipe_data.append(f"Dish Name: {dish_name}")
        recipe_data.append(f"Servings: {servings}")

        i = 3
        while i < len(children):
            if isinstance(children[i], tk.Entry):
                quantity = children[i].get()
                ingredient = children[i + 1].get()
                measurement = children[i + 2].get()
                recipe_data.append(f"Ingredient: {quantity} {measurement} {ingredient}")
                i += 3
            else:
                i += 1

        recipe_string = ' '.join(str(x) for x in recipe_data)
        print(recipe_string)

        cur.execute('''
        INSERT INTO recipes (recipe_name, ingredients, servings)
        VALUES (?, ?, ?)
        ON CONFLICT(recipe_name)
        DO UPDATE SET ingredients=excluded.ingredients, servings=excluded.servings
        ''', (dish_name, recipe_string, servings))

        conn.commit()
        for data in recipe_data:
            print(data)

    def open_ingredient_manager(self):
        ingredient_window = tk.Toplevel(self.root)
        ingredient_window.title("Ingredient Manager")
        ingredient_window.geometry("800x600")

        IngredientManager(ingredient_window)


    def open_calculator(self):
        calculator_window = tk.Toplevel(self.root)
        calculator_window.title("Calculator")
        calculator_window.geometry("800x600")

        CalculatorWindow(calculator_window)


class CalculatorWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculator")

        self.root.geometry("800x600")

        self.canvas = tk.Canvas(self.root)
        self.scrollbar = tk.Scrollbar(self.root, orient="horizontal", command=self.canvas.xview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(xscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="top", fill="both", expand=True)
        self.scrollbar.pack(side="bottom", fill="x")

        self.ingredient_dict = {}  # Class-level dictionary to store ingredient data
        self.recipe_entries = []
        self.calculate_nutrition()

        # Add the calculate shopping list button
        calc_button = tk.Button(self.scrollable_frame, text="Calculate Shopping List", command=self.calculate_shopping_list)
        calc_button.pack(pady=10)

    def calculate_nutrition(self):
        cur.execute('SELECT recipe_name, ingredients, servings FROM recipes')
        recipes = cur.fetchall()

        cur.execute('SELECT ingredient_name, size_int, size_measurement, servings, calories, price, protein FROM ingredients')
        ingredients = cur.fetchall()
        for ing in ingredients:
            self.ingredient_dict[ing[0]] = {
                'size_int': ing[1],
                'size_measurement': ing[2],
                'servings': ing[3],
                'calories': ing[4],
                'price': ing[5],
                'protein': ing[6]
            }

        for recipe in recipes:
            recipe_name = recipe[0]
            ingredients_str = recipe[1]
            servings = recipe[2]

            recipe_frame = tk.Frame(self.scrollable_frame)
            recipe_frame.pack(fill=tk.X, pady=5)

            qty_entry = tk.Entry(recipe_frame, width=5)
            qty_entry.pack(side=tk.LEFT, padx=5)
            self.recipe_entries.append((qty_entry, recipe_name, ingredients_str, servings))

            ingredient_parts = ingredients_str.split('Ingredient: ')[1:]
            total_calories = 0
            total_price = 0
            total_protein = 0

            for part in ingredient_parts:
                qty, measure, ingredient_name = part.split()[:3]
                qty = float(qty)

                if ingredient_name in self.ingredient_dict:
                    ingredient_info = self.ingredient_dict[ingredient_name]
                    ing_size = ingredient_info['size_int']
                    ing_measure = ingredient_info['size_measurement']
                    ing_servings = ingredient_info['servings']
                    ing_calories = ingredient_info['calories']
                    ing_price = ingredient_info['price']
                    ing_protein = ingredient_info['protein']

                    if measure != ing_measure:
                        qty = self.convert_units(qty, measure, ing_measure)

                    size_per_serving = ing_size / ing_servings
                    calories_per_unit = ing_calories / size_per_serving
                    price_per_unit = ing_price / ing_size
                    protein_per_unit = ing_protein / size_per_serving

                    total_calories += qty * calories_per_unit
                    total_price += qty * price_per_unit
                    total_protein += qty * protein_per_unit

            calories_per_serving = total_calories / servings
            price_per_serving = total_price / servings
            protein_per_serving = total_protein / servings

            display_text = f"{recipe_name} ({servings} servings, {calories_per_serving:.2f} calories, ${price_per_serving:.2f}, {protein_per_serving:.2f}g protein)"
            tk.Label(recipe_frame, text=display_text).pack(side=tk.LEFT, padx=5)

    def calculate_shopping_list(self):
        required_ingredients = {}
        total_cost = 0

        for qty_entry, recipe_name, ingredients_str, servings in self.recipe_entries:
            try:
                qty_to_make = int(qty_entry.get())
            except ValueError:
                continue

            ingredient_parts = ingredients_str.split('Ingredient: ')[1:]

            for part in ingredient_parts:
                qty, measure, ingredient_name = part.split()[:3]
                qty = float(qty)

                if ingredient_name in self.ingredient_dict:
                    ingredient_info = self.ingredient_dict[ingredient_name]
                    ing_size = ingredient_info['size_int']
                    ing_measure = ingredient_info['size_measurement']
                    ing_servings = ingredient_info['servings']
                    ing_price = ingredient_info['price']

                    # Convert the measurement units if they don't match
                    if measure != ing_measure:
                        qty = self.convert_units(qty, measure, ing_measure)

                    # Calculate the total quantity needed for the given number of recipes
                    total_qty_needed = qty * qty_to_make

                    # Accumulate the total quantity needed for each ingredient
                    if ingredient_name not in required_ingredients:
                        required_ingredients[ingredient_name] = {
                            'total_qty_needed': 0,
                            'size_per_unit': ing_size,
                            'price_per_unit': ing_price,
                            'measure': ing_measure
                        }
                    required_ingredients[ingredient_name]['total_qty_needed'] += total_qty_needed

        # After accumulating all ingredients, calculate the total cost and number of units needed
        for ingredient_name, data in required_ingredients.items():
            total_qty_needed = data['total_qty_needed']
            size_per_unit = data['size_per_unit']
            price_per_unit = data['price_per_unit']

            # Calculate the number of units needed by taking the ceiling after summing all quantities
            units_to_purchase = math.ceil(total_qty_needed / size_per_unit)
            cost = units_to_purchase * price_per_unit

            # Update the required_ingredients with the calculated values
            required_ingredients[ingredient_name]['units_to_purchase'] = units_to_purchase
            required_ingredients[ingredient_name]['cost'] = cost
            total_cost += cost

        # Display the shopping list
        shopping_list_window = tk.Toplevel(self.root)
        shopping_list_window.title("Shopping List")
        shopping_list_window.geometry("400x400")

        for ingredient_name, data in required_ingredients.items():
            display_text = f"{ingredient_name}: {data['units_to_purchase']} units ({data['total_qty_needed']:.2f} {data['measure']}) - ${data['cost']:.2f}"
            tk.Label(shopping_list_window, text=display_text).pack(pady=2)

        total_cost_text = f"Total Cost: ${total_cost:.2f}"
        tk.Label(shopping_list_window, text=total_cost_text, font=("Arial", 12, "bold")).pack(pady=10)

    def convert_units(self, qty, from_unit, to_unit):
        conversion_factors = {
            ("Cup", "Tablespoon"): 16,
            ("Tablespoon", "Teaspoon"): 3,
            ("Cup", "Ounce"): 8,
            ("Tablespoon", "Cup"): 1/16,
            ("Teaspoon", "Tablespoon"): 1/3,
            ("Ounce", "Cup"): 1/8
        }

        if (from_unit, to_unit) in conversion_factors:
            return qty * conversion_factors[(from_unit, to_unit)]
        elif (to_unit, from_unit) in conversion_factors:
            return qty / conversion_factors[(to_unit, from_unit)]
        else:
            raise ValueError(f"Cannot convert from {from_unit} to {to_unit}")





class IngredientManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Ingredient Manager")

        self.root.geometry("1600x600")

        self.canvas = tk.Canvas(self.root)
        self.scrollbar = tk.Scrollbar(self.root, orient="horizontal", command=self.canvas.xview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(xscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="top", fill="both", expand=True)
        self.scrollbar.pack(side="bottom", fill="x")

        self.add_ingredient_button = tk.Button(self.root, text="Add Ingredient", command=self.add_ingredient)
        self.add_ingredient_button.pack(pady=10)

        self.ingredients = []

        self.load_ingredients()

    def load_ingredients(self):
        cur.execute('SELECT * FROM ingredients')
        rows = cur.fetchall()
        for row in rows:
            self.add_ingredient_from_db(row)

    def add_ingredient_from_db(self, ingredient_data):
        ingredient_row = tk.Frame(self.scrollable_frame)
        ingredient_row.pack(fill=tk.X, pady=5)

        confirm_button = tk.Button(ingredient_row, text="Confirm",
                                   command=lambda: self.confirm_ingredient(ingredient_row))
        confirm_button.pack(side=tk.LEFT, padx=5)

        fields = ["Ingredient Name", "Brand", "Price ($)", "Size", "Measurement", "Servings", "Calories", "Protein (g)",
                  "Carbs (g)"]
        entries = []
        for field, data in zip(fields, ingredient_data[1:]):
            if field == "Measurement":
                tk.Label(ingredient_row, text=field).pack(side=tk.LEFT, padx=5)

                measurement_combobox = ttk.Combobox(ingredient_row, values=measurement_options, width=15,
                                                    state='readonly')
                measurement_combobox.set(data)
                measurement_combobox.pack(side=tk.LEFT, padx=5)
                entries.append(measurement_combobox)
            else:
                tk.Label(ingredient_row, text=field).pack(side=tk.LEFT, padx=5)
                entry = tk.Entry(ingredient_row, width=15)
                entry.insert(0, data)
                entry.pack(side=tk.LEFT, padx=5)
                entries.append(entry)

    def add_ingredient(self):
        ingredient_row = tk.Frame(self.scrollable_frame)
        ingredient_row.pack(fill=tk.X, pady=5)

        confirm_button = tk.Button(ingredient_row, text="Confirm",
                                   command=lambda: self.confirm_ingredient(ingredient_row))
        confirm_button.pack(side=tk.LEFT, padx=5)

        fields = ["Ingredient Name", "Brand", "Price ($)", "Size", "Measurement", "Servings", "Calories", "Protein (g)",
                  "Carbs (g)"]
        entries = []
        for field in fields:
            if field == "Measurement":
                tk.Label(ingredient_row, text=field).pack(side=tk.LEFT, padx=5)

                measurement_combobox = ttk.Combobox(ingredient_row, values=measurement_options, width=15,
                                                    state='readonly')
                measurement_combobox.pack(side=tk.LEFT, padx=5)
                entries.append(measurement_combobox)
            else:
                tk.Label(ingredient_row, text=field).pack(side=tk.LEFT, padx=5)
                entry = tk.Entry(ingredient_row, width=15)
                entry.pack(side=tk.LEFT, padx=5)
                entries.append(entry)

        self.ingredients.append((ingredient_row, entries))

    def add_ingredient_row(self, parent, add_button):
        fields = ["Ingredient Name", "Brand", "Price ($)", "Size", "Measurement", "Servings", "Calories", "Protein (g)",
                  "Carbs (g)"]
        entries = []
        for field in fields:
            if field == "Measurement":

                measurement_combobox = ttk.Combobox(parent, values=measurement_options, width=15, state='readonly')
                measurement_combobox.pack(side=tk.LEFT, padx=5)
                entries.append(measurement_combobox)
            else:
                entry = tk.Entry(parent, width=15)
                entry.pack(side=tk.LEFT, padx=5)
                entries.append(entry)

        add_button.pack_forget()
        add_button.pack(side=tk.LEFT, padx=5)

        self.ingredients.append((parent, entries))

    def confirm_ingredient(self, ingredient_row):
        children = ingredient_row.winfo_children()
        ingredient_data = [child.get() for child in children if isinstance(child, (tk.Entry, ttk.Combobox))]


        cur.execute('''
        INSERT INTO ingredients (ingredient_name, brand, price, size_int, size_measurement, servings, calories, protein, carbs)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(ingredient_name)
        DO UPDATE SET brand=excluded.brand, price=excluded.price, size_int=excluded.size_int, size_measurement=excluded.size_measurement, 
                      servings=excluded.servings, calories=excluded.calories, protein=excluded.protein, carbs=excluded.carbs
        ''', ingredient_data)

        conn.commit()
        print("Ingredient confirmed:", ingredient_data)


if __name__ == "__main__":
    conn = sqlite3.connect("alpha.db")
    cur = conn.cursor()

    cur.execute('''
    CREATE TABLE IF NOT EXISTS recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_name TEXT NOT NULL UNIQUE,
    ingredients TEXT NOT NULL,
    servings INTEGER NOT NULL)''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ingredient_name TEXT NOT NULL UNIQUE,
    brand TEXT NOT NULL,
    price REAL NOT NULL,
    size_int REAL NOT NULL,
    size_measurement TEXT NOT NULL,
    servings REAL NOT NULL,
    calories REAL NOT NULL,
    protein REAL NOT NULL,
    carbs REAL NOT NULL)''')

    conn.commit()

    measurement_options = ['Cup', 'Gram', 'Milliliter', 'Ounce', 'Piece', 'Tablespoon', 'Teaspoon']

    # Query to select all ingredient names
    cur.execute('SELECT ingredient_name FROM ingredients')

    # Fetch all results from the query
    ingredient_options = [row[0] for row in cur.fetchall()]

    root = tk.Tk()
    app = RecipeManager(root)
    root.mainloop()
