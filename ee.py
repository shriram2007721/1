import threading


class InventoryManagement:

    def __init__(self):
        self.warehouses = {
            "Warehouse A": {},
            "Warehouse B": {},
            "Warehouse C": {}
        }

        self.suppliers = {}
        self.reorder_threshold = 10
        self.lock = threading.Lock()

    # Add Product
    def add_product(self, warehouse, product, quantity):

        if warehouse not in self.warehouses:
            return "Invalid warehouse"

        if quantity < 0:
            return "Invalid quantity"

        if product not in self.warehouses[warehouse]:
            self.warehouses[warehouse][product] = 0

        self.warehouses[warehouse][product] += quantity

        return "Product added successfully"

    # Remove Product
    def remove_product(self, warehouse, product, quantity):

        if warehouse not in self.warehouses:
            return "Invalid warehouse"

        if product not in self.warehouses[warehouse]:
            return "Invalid product"

        if quantity < 0:
            return "Invalid quantity"

        if self.warehouses[warehouse][product] < quantity:
            return "Insufficient inventory"

        self.warehouses[warehouse][product] -= quantity

        return "Product removed successfully"

    # Check Stock
    def check_stock(self, warehouse, product):

        if warehouse not in self.warehouses:
            return -1

        if product not in self.warehouses[warehouse]:
            return -1

        return self.warehouses[warehouse][product]

    # Automatically Select Warehouse
    def select_warehouse(self, product, quantity):

        for warehouse in self.warehouses:

            if product in self.warehouses[warehouse]:

                if self.warehouses[warehouse][product] >= quantity:
                    return warehouse

        return None

    # Fulfill Order
    def fulfill_order(self, product, quantity):

        if quantity <= 0:
            return "Invalid quantity"

        warehouse = self.select_warehouse(product, quantity)

        if warehouse is None:
            return "Insufficient inventory"

        with self.lock:

            if self.warehouses[warehouse][product] < quantity:
                return "Insufficient inventory"

            self.warehouses[warehouse][product] -= quantity

        return "Order fulfilled from " + warehouse

    # Transfer Stock
    def transfer_stock(self, source, destination,
                       product, quantity):

        if source not in self.warehouses:
            return "Invalid source warehouse"

        if destination not in self.warehouses:
            return "Invalid destination warehouse"

        if source == destination:
            return "Source and destination cannot be same"

        if product not in self.warehouses[source]:
            return "Invalid product"

        if quantity <= 0:
            return "Invalid quantity"

        if self.warehouses[source][product] < quantity:
            return "Insufficient inventory"

        with self.lock:

            self.warehouses[source][product] -= quantity

            if product not in self.warehouses[destination]:
                self.warehouses[destination][product] = 0

            self.warehouses[destination][product] += quantity

        return "Stock transferred successfully"

    # Reorder
    def reorder(self, warehouse, product, quantity):

        if warehouse not in self.warehouses:
            return "Invalid warehouse"

        if product not in self.warehouses[warehouse]:
            return "Invalid product"

        if self.warehouses[warehouse][product] <= self.reorder_threshold:

            self.warehouses[warehouse][product] += quantity

            return "Reorder completed"

        return "Reorder not required"

    # Supplier Management
    def add_supplier(self, supplier_id, supplier_name):

        if supplier_id in self.suppliers:
            return "Supplier already exists"

        self.suppliers[supplier_id] = supplier_name

        return "Supplier added successfully"

    def remove_supplier(self, supplier_id):

        if supplier_id not in self.suppliers:
            return "Supplier not found"

        del self.suppliers[supplier_id]

        return "Supplier removed successfully"

    # Low Stock Detection
    def low_stock(self):

        result = []

        for warehouse in self.warehouses:

            for product in self.warehouses[warehouse]:

                quantity = self.warehouses[warehouse][product]

                if quantity <= self.reorder_threshold:

                    result.append(
                        (warehouse, product, quantity)
                    )

        return result


if __name__ == "__main__":

    inventory = InventoryManagement()

    # Add products
    print(
        inventory.add_product(
            "Warehouse A",
            "Laptop",
            50
        )
    )

    print(
        inventory.add_product(
            "Warehouse B",
            "Laptop",
            30
        )
    )

    print(
        inventory.add_product(
            "Warehouse C",
            "Phone",
            20
        )
    )

    # Supplier
    print(
        inventory.add_supplier(
            "S001",
            "ABC Suppliers"
        )
    )

    # Check stock
    print(
        "Warehouse A Laptop:",
        inventory.check_stock(
            "Warehouse A",
            "Laptop"
        )
    )

    # Automatic warehouse selection
    print(
        inventory.fulfill_order(
            "Laptop",
            20
        )
    )

    # Transfer stock
    print(
        inventory.transfer_stock(
            "Warehouse A",
            "Warehouse B",
            "Laptop",
            10
        )
    )

    # Low stock
    print(
        "Low Stock:",
        inventory.low_stock()
    )
