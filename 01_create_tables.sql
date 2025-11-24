-- WebShop Database Schema
-- Create all tables according to the ER model

-- Customer Table
CREATE TABLE customer (
    customer_id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    strasse VARCHAR(255),
    ort VARCHAR(100),
    plz VARCHAR(10)
);

-- Category Table
CREATE TABLE category (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE
);

-- Product Table
CREATE TABLE product (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL CHECK (price >= 0),
    stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
    category_id INTEGER NOT NULL,
    FOREIGN KEY (category_id) REFERENCES category (category_id) ON DELETE RESTRICT
);

-- Order Table
CREATE TABLE "order" (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    order_date DATE NOT NULL DEFAULT CURRENT_DATE,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    total_amount DECIMAL(10, 2) NOT NULL CHECK (total_amount >= 0),
    FOREIGN KEY (customer_id) REFERENCES customer (customer_id) ON DELETE CASCADE
);

-- Order_Item Table (Junction table between Order and Product)
CREATE TABLE order_item (
    order_item_id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    price_per_unit DECIMAL(10, 2) NOT NULL CHECK (price_per_unit >= 0),
    FOREIGN KEY (order_id) REFERENCES "order" (order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES product (product_id) ON DELETE RESTRICT
);

-- Cart Table
CREATE TABLE cart (
    cart_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL UNIQUE,
    last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customer (customer_id) ON DELETE CASCADE
);

-- Cart_Item Table (Junction table between Cart and Product)
CREATE TABLE cart_item (
    cart_item_id SERIAL PRIMARY KEY,
    cart_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    FOREIGN KEY (cart_id) REFERENCES cart (cart_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES product (product_id) ON DELETE CASCADE,
    UNIQUE (cart_id, product_id)
);

-- Create indexes for better query performance
CREATE INDEX idx_product_category ON product (category_id);

CREATE INDEX idx_order_customer ON "order" (customer_id);

CREATE INDEX idx_order_item_order ON order_item (order_id);

CREATE INDEX idx_order_item_product ON order_item (product_id);

CREATE INDEX idx_cart_customer ON cart (customer_id);

CREATE INDEX idx_cart_item_cart ON cart_item (cart_id);

CREATE INDEX idx_cart_item_product ON cart_item (product_id);

CREATE INDEX idx_customer_email ON customer (email);