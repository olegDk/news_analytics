CREATE TABLE IF NOT EXISTS securities (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) UNIQUE NOT NULL,
    exchange VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS news (
    id SERIAL PRIMARY KEY,
    kind VARCHAR(50),
    action VARCHAR(50),
    content TEXT,
    timestamp TIMESTAMP
);

CREATE TABLE IF NOT EXISTS news_securities (
    news_id INT REFERENCES news(id),
    security_id INT REFERENCES securities(id),
    PRIMARY KEY (news_id, security_id)
);

CREATE TABLE IF NOT EXISTS daily_summary (
    id SERIAL PRIMARY KEY,
    summary TEXT,
    date DATE,
    security_id INT REFERENCES securities(id)
);

CREATE TABLE IF NOT EXISTS sector_summary (
    id SERIAL PRIMARY KEY,
    summary TEXT,
    date DATE,
    sector VARCHAR(50)
);
