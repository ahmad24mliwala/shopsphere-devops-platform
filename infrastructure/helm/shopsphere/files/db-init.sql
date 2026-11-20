CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE products (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    price NUMERIC(12,2) NOT NULL CHECK (price >= 0),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    product_id BIGINT REFERENCES products(id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    status VARCHAR(30) DEFAULT 'CREATED',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE payments (
    id BIGSERIAL PRIMARY KEY,
    order_id BIGINT UNIQUE REFERENCES orders(id),
    amount NUMERIC(12,2) NOT NULL CHECK (amount >= 0),
    method VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'SIMULATED_SUCCESS',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
