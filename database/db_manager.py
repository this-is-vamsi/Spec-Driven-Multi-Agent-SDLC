import sqlite3
import os


class DatabaseManager:
    """Manages the local SQLite database for development and testing."""

    def __init__(self, db_path: str = "database/sdlc.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._initialize()

    def _initialize(self):
        """Create example tables and seed data."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                category TEXT,
                stock_quantity INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 1,
                total_price REAL NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """)

        # Seed data only if tables are empty
        if cursor.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0:
            products = [
                ("Laptop Pro 15", "High-performance laptop with 16GB RAM and 512GB SSD", 1299.99, "Electronics", 50),
                ("Wireless Mouse", "Ergonomic wireless mouse with USB-C receiver", 49.99, "Accessories", 200),
                ("Mechanical Keyboard", "RGB mechanical keyboard with Cherry MX Blue switches", 129.99, "Accessories", 150),
                ("4K Monitor 27\"", "Ultra HD IPS monitor, 144Hz, HDR600", 449.99, "Electronics", 75),
                ("USB-C Hub", "7-in-1 USB-C docking station with HDMI, Ethernet, SD reader", 79.99, "Accessories", 300),
                ("Noise Cancelling Headphones", "Over-ear ANC headphones, 30hr battery", 299.99, "Audio", 120),
                ("Webcam HD 1080p", "Full HD webcam with auto-focus and ring light", 89.99, "Electronics", 180),
                ("Standing Desk Mat", "Anti-fatigue standing desk mat, 20x36 inches", 59.99, "Furniture", 90),
                ("Cable Management Kit", "Complete cable organizer set with 50 velcro ties", 24.99, "Accessories", 500),
                ("Desk Lamp LED", "Adjustable LED desk lamp, 5 colour modes, USB charging", 39.99, "Furniture", 160),
                ("Laptop Stand", "Aluminium adjustable laptop riser, fits 10-17 inch", 69.99, "Accessories", 220),
                ("Bluetooth Speaker", "Portable waterproof speaker, 12hr battery, IPX7", 79.99, "Audio", 95),
                ("Smartphone Dock", "Wireless charging dock with MagSafe support", 44.99, "Accessories", 180),
                ("External SSD 1TB", "Portable NVMe SSD, 1050MB/s read speed", 109.99, "Electronics", 130),
                ("Office Chair Cushion", "Memory foam seat cushion, ergonomic design", 34.99, "Furniture", 250),
                ("Webcam Light Bar", "LED monitor light bar, auto-dimming sensor", 54.99, "Accessories", 140),
                ("Tablet Stylus Pro", "Pressure-sensitive stylus pen, 4096 levels", 69.99, "Accessories", 85),
                ("Gaming Mousepad XL", "Extended desk mat, 900x400mm, waterproof surface", 29.99, "Accessories", 310),
                ("Smart Power Strip", "WiFi-enabled power strip, 4 outlets, 3 USB ports", 39.99, "Electronics", 175),
                ("Desk Organiser", "Bamboo multi-slot desk organiser with phone holder", 27.99, "Furniture", 200),
            ]
            cursor.executemany(
                "INSERT INTO products (name, description, price, category, stock_quantity) VALUES (?, ?, ?, ?, ?)",
                products,
            )

        if cursor.execute("SELECT COUNT(*) FROM customers").fetchone()[0] == 0:
            customers = [
                ("Alice", "Johnson", "alice.johnson@example.com", "+1-555-0101"),
                ("Bob", "Smith", "bob.smith@example.com", "+1-555-0102"),
                ("Charlie", "Brown", "charlie.brown@example.com", "+1-555-0103"),
                ("Diana", "Prince", "diana.prince@example.com", "+1-555-0104"),
                ("Edward", "Norton", "edward.norton@example.com", "+1-555-0105"),
                ("Fiona", "Green", "fiona.green@example.com", "+1-555-0106"),
                ("George", "Harrison", "george.harrison@example.com", "+1-555-0107"),
                ("Hannah", "Lee", "hannah.lee@example.com", "+1-555-0108"),
                ("Ivan", "Petrov", "ivan.petrov@example.com", "+1-555-0109"),
                ("Julia", "Martinez", "julia.martinez@example.com", "+1-555-0110"),
            ]
            cursor.executemany(
                "INSERT INTO customers (first_name, last_name, email, phone) VALUES (?, ?, ?, ?)",
                customers,
            )

        if cursor.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 0:
            orders = [
                (1, 1, 1, 1299.99, "completed"),
                (1, 3, 2, 259.98, "completed"),
                (2, 2, 1, 49.99, "shipped"),
                (3, 6, 1, 299.99, "pending"),
                (4, 4, 1, 449.99, "processing"),
                (5, 5, 3, 239.97, "completed"),
                (2, 7, 1, 89.99, "pending"),
                (3, 10, 2, 79.98, "shipped"),
                (1, 14, 1, 109.99, "completed"),
                (6, 12, 2, 159.98, "shipped"),
                (7, 1, 1, 1299.99, "processing"),
                (8, 11, 1, 69.99, "completed"),
                (9, 15, 3, 104.97, "pending"),
                (10, 8, 1, 59.99, "shipped"),
                (4, 19, 2, 79.98, "completed"),
                (5, 16, 1, 54.99, "processing"),
                (6, 20, 1, 27.99, "completed"),
                (7, 9, 5, 124.95, "shipped"),
                (8, 18, 1, 29.99, "pending"),
                (2, 13, 1, 44.99, "completed"),
                (9, 4, 1, 449.99, "processing"),
                (10, 17, 2, 139.98, "completed"),
                (3, 11, 1, 69.99, "shipped"),
                (1, 20, 2, 55.98, "completed"),
                (6, 3, 1, 129.99, "pending"),
            ]
            cursor.executemany(
                "INSERT INTO orders (customer_id, product_id, quantity, total_price, status) VALUES (?, ?, ?, ?, ?)",
                orders,
            )

        conn.commit()
        conn.close()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def execute_query(self, query: str, params: tuple = ()) -> list:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            return [dict(row) for row in results]
        finally:
            conn.close()

    def execute_write(self, query: str, params: tuple = ()) -> int:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def get_table_info(self) -> dict:
        """Return schema information for all tables."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tables = [row["name"] for row in cursor.fetchall()]
            info = {}
            for table in tables:
                cursor.execute(f"PRAGMA table_info({table})")
                columns = [
                    {"name": col["name"], "type": col["type"], "notnull": bool(col["notnull"]), "pk": bool(col["pk"])}
                    for col in cursor.fetchall()
                ]
                cursor.execute(f"SELECT COUNT(*) as cnt FROM {table}")
                count = cursor.fetchone()["cnt"]
                info[table] = {"columns": columns, "row_count": count}
            return info
        finally:
            conn.close()

    def get_schema_summary(self) -> str:
        """Return a human-readable schema summary with sample data for LLM context."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tables = [row["name"] for row in cursor.fetchall()]
            parts = ["## Database Schema & Sample Data\n"]
            for table in tables:
                cursor.execute(f"PRAGMA table_info({table})")
                cols = cursor.fetchall()
                cursor.execute(f"SELECT COUNT(*) as cnt FROM {table}")
                count = cursor.fetchone()["cnt"]
                parts.append(f"### Table: `{table}` ({count} rows)")
                parts.append("| Column | Type | Nullable | PK |")
                parts.append("|--------|------|----------|----|")
                col_names = []
                for c in cols:
                    nullable = "YES" if not c["notnull"] else "NO"
                    pk = "✓" if c["pk"] else ""
                    parts.append(f"| {c['name']} | {c['type']} | {nullable} | {pk} |")
                    col_names.append(c["name"])
                cursor.execute(f"SELECT * FROM {table} LIMIT 3")
                rows = cursor.fetchall()
                if rows:
                    parts.append(f"\n**Sample rows ({min(3, count)} of {count}):**")
                    parts.append("| " + " | ".join(col_names) + " |")
                    parts.append("| " + " | ".join("---" for _ in col_names) + " |")
                    for row in rows:
                        vals = [str(row[c]) if row[c] is not None else "NULL" for c in col_names]
                        parts.append("| " + " | ".join(vals) + " |")
                parts.append("")
            return "\n".join(parts)
        finally:
            conn.close()
