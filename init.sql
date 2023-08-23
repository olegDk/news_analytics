-- DROP TABLE IF EXISTS news_securities;
-- DROP TABLE IF EXISTS securities_summaries;
-- DROP TABLE IF EXISTS sector_summary;
-- DROP TABLE IF EXISTS news;
-- DROP TABLE IF EXISTS securities;

CREATE TABLE IF NOT EXISTS securities (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) UNIQUE NOT NULL,
    exchange VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS news (
    id SERIAL PRIMARY KEY,
    title TEXT,
    content TEXT,
    timestamp TIMESTAMP
);

CREATE TABLE IF NOT EXISTS news_securities (
    news_id INT REFERENCES news(id),
    security_id INT REFERENCES securities(id),
    PRIMARY KEY (news_id, security_id)
);

CREATE TABLE IF NOT EXISTS securities_summaries (
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
