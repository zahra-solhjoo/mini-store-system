"""
Shopping Store Simulation Program
A console-based store management system with Manager and Customer roles.
"""

from typing import Optional
import json
import os


# ============================================================================
# CLASS: Product
# ============================================================================

class Product:
    """
    Represents a product in the store.
    
    Attributes:
        name (str): Product name
        price (float): Product price
        stock (int): Available quantity
        category (str): Product category
    """
    
    def __init__(self, name: str, price: float, stock: int, category: str = "General") -> None:
        self.name = name
        self.price = price
        self.stock = stock
        self.category = category
    
    def __repr__(self) -> str:
        return f"Product(name='{self.name}', price={self.price}, stock={self.stock}, category='{self.category}')"
    
    def to_dict(self) -> dict:
        """Convert product to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "price": self.price,
            "stock": self.stock,
            "category": self.category
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Product":
        """Create product from dictionary."""
        return cls(
            name=data["name"],
            price=data["price"],
            stock=data["stock"],
            category=data.get("category", "General")
        )


# ============================================================================
# CLASS: Store
# ============================================================================

class Store:
    """
    Manages the store's product inventory.
    
    Attributes:
        products (list[Product]): List of available products
    """
    
    def __init__(self) -> None:
        self.products: list[Product] = []
    
    def add_product(self, name: str, price: float, stock: int, category: str = "General") -> bool:
        """
        Add a new product to the store.
        
        Args:
            name: Product name
            price: Product price
            stock: Initial stock quantity
            category: Product category
            
        Returns:
            bool: True if added successfully, False if product exists
        """
        if self.find_product(name) is not None:
            print(f"❌ Product '{name}' already exists!")
            return False
        
        product = Product(name, price, stock, category)
        self.products.append(product)
        print(f"✅ Product '{name}' added successfully!")
        return True
    
    def list_products(self) -> None:
        """Display all products in the store."""
        if not self.products:
            print("📦 No products available in the store.")
            return
        
        print("\n" + "=" * 70)
        print(f"{'#':<4} {'Name':<20} {'Price':<12} {'Stock':<8} {'Category':<15}")
        print("=" * 70)
        
        for idx, product in enumerate(self.products, 1):
            print(f"{idx:<4} {product.name:<20} ${product.price:<11.2f} {product.stock:<8} {product.category:<15}")
        
        print("=" * 70)
    
    def find_product(self, name: str) -> Optional[Product]:
        """
        Find a product by name (case-insensitive).
        
        Args:
            name: Product name to search
            
        Returns:
            Product if found, None otherwise
        """
        for product in self.products:
            if product.name.lower() == name.lower():
                return product
        return None
    
    def update_stock(self, name: str, new_stock: int) -> bool:
        """Update the stock of a product."""
        product = self.find_product(name)
        if product:
            product.stock = new_stock
            return True
        return False
    
    def list_by_category(self, category: str) -> list[Product]:
        """List products in a specific category."""
        return [p for p in self.products if p.category.lower() == category.lower()]
    
    def get_categories(self) -> set:
        """Get all unique categories."""
        return {p.category for p in self.products}
    
    def to_dict(self) -> dict:
        """Convert store data to dictionary for JSON serialization."""
        return {
            "products": [p.to_dict() for p in self.products]
        }
    
    def load_from_dict(self, data: dict) -> None:
        """Load store data from dictionary."""
        self.products = [Product.from_dict(p) for p in data.get("products", [])]


# ============================================================================
# CLASS: CartItem
# ============================================================================

class CartItem:
    """
    Represents an item in the shopping cart.
    
    Attributes:
        product (Product): The product object
        quantity (int): Quantity of the product in cart
    """
    
    def __init__(self, product: Product, quantity: int) -> None:
        self.product = product
        self.quantity = quantity
    
    def __repr__(self) -> str:
        return f"CartItem(product={self.product.name}, quantity={self.quantity})"
    
    def subtotal(self) -> float:
        """Calculate subtotal for this item."""
        return self.product.price * self.quantity
    
    def to_dict(self) -> dict:
        """Convert cart item to dictionary."""
        return {
            "product": self.product.to_dict(),
            "quantity": self.quantity
        }


# ============================================================================
# CLASS: Cart
# ============================================================================

class Cart:
    """
    Manages the shopping cart operations.
    
    Attributes:
        items (list[CartItem]): List of items in cart
    """
    
    def __init__(self) -> None:
        self.items: list[CartItem] = []
    
    def add_to_cart(self, product: Product, quantity: int) -> tuple[bool, str]:
        """
        Add a product to the cart.
        
        Args:
            product: Product to add
            quantity: Quantity to add
            
        Returns:
            tuple: (success: bool, message: str)
        """
        # Check stock availability
        if quantity > product.stock:
            return False, f"❌ Not enough stock! Available: {product.stock}"
        
        # Check if product already in cart
        for item in self.items:
            if item.product.name.lower() == product.name.lower():
                new_quantity = item.quantity + quantity
                if new_quantity > product.stock:
                    return False, f"❌ Total quantity exceeds stock! Available: {product.stock}"
                item.quantity = new_quantity
                return True, f"✅ Updated '{product.name}' quantity to {new_quantity}"
        
        # Add new item
        cart_item = CartItem(product, quantity)
        self.items.append(cart_item)
        return True, f"✅ Added '{product.name}' (x{quantity}) to cart"
    
    def remove_from_cart(self, product_name: str) -> bool:
        """
        Remove a product from the cart.
        
        Args:
            product_name: Name of product to remove
            
        Returns:
            bool: True if removed, False if not found
        """
        for i, item in enumerate(self.items):
            if item.product.name.lower() == product_name.lower():
                removed_name = item.product.name
                self.items.pop(i)
                print(f"✅ Removed '{removed_name}' from cart")
                return True
        print(f"❌ Product '{product_name}' not found in cart")
        return False
    
    def update_quantity(self, product_name: str, new_quantity: int) -> bool:
        """Update the quantity of a product in cart."""
        for item in self.items:
            if item.product.name.lower() == product_name.lower():
                if new_quantity > item.product.stock:
                    print(f"❌ Not enough stock! Available: {item.product.stock}")
                    return False
                if new_quantity <= 0:
                    return self.remove_from_cart(product_name)
                item.quantity = new_quantity
                print(f"✅ Updated '{item.product.name}' quantity to {new_quantity}")
                return True
        print(f"❌ Product '{product_name}' not found in cart")
        return False
    
    def view_cart(self) -> None:
        """Display all items in the cart."""
        if not self.items:
            print("🛒 Your cart is empty!")
            return
        
        print("\n" + "=" * 80)
        print(f"{'#':<4} {'Product':<20} {'Unit Price':<12} {'Qty':<6} {'Subtotal':<12}")
        print("=" * 80)
        
        for idx, item in enumerate(self.items, 1):
            subtotal = item.subtotal()
            print(f"{idx:<4} {item.product.name:<20} ${item.product.price:<11.2f} {item.quantity:<6} ${subtotal:<11.2f}")
        
        print("=" * 80)
        print(f"{'TOTAL:':<42} ${self.total_price():<11.2f}")
        print("=" * 80)
    
    def total_price(self) -> float:
        """Calculate total price of all items."""
        return sum(item.subtotal() for item in self.items)
    
    def clear(self) -> None:
        """Clear all items from cart."""
        self.items.clear()
    
    def is_empty(self) -> bool:
        """Check if cart is empty."""
        return len(self.items) == 0


# ============================================================================
# CLASS: User
# ============================================================================

class User:
    """Represents a user (customer) of the store."""
    
    def __init__(self, username: str, password: str) -> None:
        self.username = username
        self.password = password
        self.purchase_history: list[dict] = []
    
    def to_dict(self) -> dict:
        """Convert user to dictionary."""
        return {
            "username": self.username,
            "password": self.password,
            "purchase_history": self.purchase_history
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """Create user from dictionary."""
        user = cls(data["username"], data["password"])
        user.purchase_history = data.get("purchase_history", [])
        return user
    
    def add_purchase(self, cart: Cart) -> None:
        """Add a purchase to history."""
        purchase = {
            "items": [item.to_dict() for item in cart.items],
            "total": cart.total_price()
        }
        self.purchase_history.append(purchase)


# ============================================================================
# CLASS: UserManager
# ============================================================================

class UserManager:
    """Manages user accounts and authentication."""
    
    def __init__(self) -> None:
        self.users: list[User] = []
    
    def register(self, username: str, password: str) -> bool:
        """Register a new user."""
        if self.find_user(username):
            print("❌ Username already exists!")
            return False
        
        user = User(username, password)
        self.users.append(user)
        print("✅ Registration successful!")
        return True
    
    def login(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user."""
        for user in self.users:
            if user.username == username and user.password == password:
                print(f"✅ Welcome back, {username}!")
                return user
        print("❌ Invalid username or password!")
        return None
    
    def find_user(self, username: str) -> Optional[User]:
        """Find a user by username."""
        for user in self.users:
            if user.username == username:
                return user
        return None
    
    def to_dict(self) -> dict:
        """Convert users to dictionary."""
        return {
            "users": [u.to_dict() for u in self.users]
        }
    
    def load_from_dict(self, data: dict) -> None:
        """Load users from dictionary."""
        self.users = [User.from_dict(u) for u in data.get("users", [])]


# ============================================================================
# CLASS: StoreManager (Main Application)
# ============================================================================

class StoreManager:
    """
    Main application class that manages the store operations.
    """
    
    DATA_FILE = "store_data.json"
    
    def __init__(self) -> None:
        self.store = Store()
        self.cart = Cart()
        self.user_manager = UserManager()
        self.current_user: Optional[User] = None
        self.is_manager_mode = False
        self.load_data()
    
    # ==================== Data Persistence ====================
    
    def save_data(self) -> None:
        """Save all data to JSON file."""
        data = {
            "store": self.store.to_dict(),
            "users": self.user_manager.to_dict()
        }
        with open(self.DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print("💾 Data saved successfully!")
    
    def load_data(self) -> None:
        """Load data from JSON file."""
        if os.path.exists(self.DATA_FILE):
            try:
                with open(self.DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.store.load_from_dict(data.get("store", {}))
                self.user_manager.load_from_dict(data.get("users", {}))
                print("📂 Data loaded successfully!")
            except (json.JSONDecodeError, KeyError):
                print("⚠️ Error loading data, starting fresh!")
    
    # ==================== Authentication ====================
    
    def show_auth_menu(self) -> None:
        """Display authentication menu."""
        while True:
            print("\n" + "=" * 50)
            print("         🏪 WELCOME TO THE STORE 🏪")
            print("=" * 50)
            print("  1. 👤 Customer Login")
            print("  2. 📝 Customer Register")
            print("  3. 🔐 Manager Mode")
            print("  4. 🚪 Exit")
            print("=" * 50)
            
            choice = input("\nEnter your choice: ").strip()
            
            if choice == "1":
                self.customer_login()
            elif choice == "2":
                self.customer_register()
            elif choice == "3":
                self.manager_login()
            elif choice == "4":
                self.save_data()
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice!")
    
    def customer_login(self) -> None:
        """Handle customer login."""
        print("\n--- Customer Login ---")
        username = input("Username: ").strip()
        password = input("Password: ").strip()
        
        user = self.user_manager.login(username, password)
        if user:
            self.current_user = user
            self.customer_menu()
    
    def customer_register(self) -> None:
        """Handle customer registration."""
        print("\n--- Customer Registration ---")
        username = input("Username: ").strip()
        password = input("Password: ").strip()
        self.user_manager.register(username, password)
    
    def manager_login(self) -> None:
        """Handle manager login (simple password check)."""
        print("\n--- Manager Login ---")
        password = input("Enter manager password: ").strip()
        
        if password == "admin123":  # Simple password for demo
            self.is_manager_mode = True
            print("✅ Welcome, Manager!")
            self.manager_menu()
        else:
            print("❌ Invalid password!")
    
    # ==================== Manager Menu ====================
    
    def manager_menu(self) -> None:
        """Display manager menu."""
        while True:
            print("\n" + "=" * 50)
            print("         👨‍💼 MANAGER MENU 👨‍💼")
            print("=" * 50)
            print("  1. ➕ Add Product")
            print("  2. 📦 List Products")
            print("  3. 🔄 Update Stock")
            print("  4. 🗂️  List by Category")
            print("  5. 📊 View Categories")
            print("  6. 💾 Save Data")
            print("  7. 🚪 Logout")
            print("=" * 50)
            
            choice = input("\nEnter your choice: ").strip()
            
            if choice == "1":
                self.add_product_flow()
            elif choice == "2":
                self.store.list_products()
            elif choice == "3":
                self.update_stock_flow()
            elif choice == "4":
                self.list_by_category_flow()
            elif choice == "5":
                self.show_categories()
            elif choice == "6":
                self.save_data()
            elif choice == "7":
                self.is_manager_mode = False
                print("👋 Logged out!")
                break
            else:
                print("❌ Invalid choice!")
    
    def add_product_flow(self) -> None:
        """Flow for adding a new product."""
        print("\n--- Add New Product ---")
        name = input("Product name: ").strip()
        
        if not name:
            print("❌ Name cannot be empty!")
            return
        
        try:
            price = float(input("Price: $"))
            stock = int(input("Initial stock: "))
            category = input("Category (default: General): ").strip() or "General"
            
            if price < 0 or stock < 0:
                print("❌ Price and stock must be positive!")
                return
            
            self.store.add_product(name, price, stock, category)
        except ValueError:
            print("❌ Invalid input! Please enter valid numbers.")
    
    def update_stock_flow(self) -> None:
        """Flow for updating product stock."""
        self.store.list_products()
        name = input("\nEnter product name to update: ").strip()
        
        product = self.store.find_product(name)
        if product:
            try:
                new_stock = int(input(f"New stock (current: {product.stock}): "))
                if new_stock < 0:
                    print("❌ Stock cannot be negative!")
                    return
                self.store.update_stock(name, new_stock)
                print(f"✅ Stock updated to {new_stock}")
            except ValueError:
                print("❌ Invalid input!")
        else:
            print(f"❌ Product '{name}' not found!")
    
    def list_by_category_flow(self) -> None:
        """Flow for listing products by category."""
        category = input("Enter category name: ").strip()
        products = self.store.list_by_category(category)
        
        if products:
            print(f"\n📂 Products in '{category}':")
            print("-" * 50)
            for p in products:
                print(f"  • {p.name}: ${p.price:.2f} (Stock: {p.stock})")
        else:
            print(f"❌ No products found in category '{category}'")
    
    def show_categories(self) -> None:
        """Show all available categories."""
        categories = self.store.get_categories()
        if categories:
            print("\n📂 Available Categories:")
            print("-" * 30)
            for cat in sorted(categories):
                count = len(self.store.list_by_category(cat))
                print(f"  • {cat} ({count} products)")
        else:
            print("❌ No categories available!")
    
    # ==================== Customer Menu ====================
    
    def customer_menu(self) -> None:
        """Display customer menu."""
        self.cart = Cart()  # New cart for this session
        
        while True:
            print("\n" + "=" * 50)
            print(f"         🛒 CUSTOMER MENU 🛒")
            print(f"         Welcome, {self.current_user.username}!")
            print("=" * 50)
            print("  1. 🛍️  Browse Products")
            print("  2. ➕ Add to Cart")
            print("  3. 🗑️  Remove from Cart")
            print("  4. ✏️  Update Quantity")
            print("  5. 👁️  View Cart")
            print("  6. 💳 Checkout")
            print("  7. 📜 Purchase History")
            print("  8. 🚪 Logout")
            print("=" * 50)
            
            choice = input("\nEnter your choice: ").strip()
            
            if choice == "1":
                self.store.list_products()
            elif choice == "2":
                self.add_to_cart_flow()
            elif choice == "3":
                self.remove_from_cart_flow()
            elif choice == "4":
                self.update_cart_flow()
            elif choice == "5":
                self.cart.view_cart()
            elif choice == "6":
                self.checkout()
            elif choice == "7":
                self.show_purchase_history()
            elif choice == "8":
                print("👋 Logged out!")
                self.current_user = None
                break
            else:
                print("❌ Invalid choice!")
    
    def add_to_cart_flow(self) -> None:
        """Flow for adding product to cart."""
        self.store.list_products()
        name = input("\nEnter product name: ").strip()
        
        product = self.store.find_product(name)
        if not product:
            print(f"❌ Product '{name}' not found!")
            return
        
        if product.stock == 0:
            print("❌ Product is out of stock!")
            return
        
        try:
            quantity = int(input(f"Quantity (available: {product.stock}): "))
            if quantity <= 0:
                print("❌ Quantity must be positive!")
                return
            
            success, message = self.cart.add_to_cart(product, quantity)
            print(message)
        except ValueError:
            print("❌ Invalid quantity!")
    
    def remove_from_cart_flow(self) -> None:
        """Flow for removing product from cart."""
        self.cart.view_cart()
        if self.cart.is_empty():
            return
        
        name = input("\nEnter product name to remove: ").strip()
        self.cart.remove_from_cart(name)
    
    def update_cart_flow(self) -> None:
        """Flow for updating cart item quantity."""
        self.cart.view_cart()
        if self.cart.is_empty():
            return
        
        name = input("\nEnter product name: ").strip()
        try:
            quantity = int(input("New quantity: "))
            self.cart.update_quantity(name, quantity)
        except ValueError:
            print("❌ Invalid quantity!")
    
    def checkout(self) -> None:
        """Process checkout and generate invoice."""
        if self.cart.is_empty():
            print("❌ Your cart is empty!")
            return
        
        print("\n" + "=" * 70)
        print("                    🧾 FINAL INVOICE 🧾")
        print("=" * 70)
        
        self.cart.view_cart()
        
        total = self.cart.total_price()
        print(f"\n{'SUBTOTAL:':<42} ${total:.2f}")
        print(f"{'TOTAL:':<42} ${total * 1.00:.2f}")
        print("=" * 70)
        
        # Update stock
        for item in self.cart.items:
            item.product.stock -= item.quantity
        
        # Save purchase to history
        self.current_user.add_purchase(self.cart)
        
        print("\n🎉 Thank you for your purchase!")
        print("✅ Order confirmed! Stock updated.")
        
        self.cart.clear()
    
    def show_purchase_history(self) -> None:
        """Display user's purchase history."""
        if not self.current_user.purchase_history:
            print("📜 No purchase history found!")
            return
        
        print("\n" + "=" * 60)
        print("              📜 PURCHASE HISTORY 📜")
        print("=" * 60)
        
        for idx, purchase in enumerate(self.current_user.purchase_history, 1):
            print(f"\n📦 Order #{idx} - Total: ${purchase['total']:.2f}")
            print("-" * 40)
            for item in purchase['items']:
                print(f"  • {item['product']['name']} x{item['quantity']} = ${item['product']['price'] * item['quantity']:.2f}")
        
        print("=" * 60)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main() -> None:
    """Main entry point of the application."""
    app = StoreManager()
    app.show_auth_menu()


if __name__ == "__main__":
    main()