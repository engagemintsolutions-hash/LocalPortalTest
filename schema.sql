-- UK Property Search Engine - Database Schema
-- PostgreSQL 15+ with PostGIS extension

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pg_trgm; -- Fuzzy text matching
CREATE EXTENSION IF NOT EXISTS btree_gin; -- Composite GIN indexes

-- =====================================================
-- CORE PROPERTY DATA
-- =====================================================

CREATE TABLE properties (
    property_id BIGSERIAL PRIMARY KEY,
    uprn BIGINT UNIQUE NOT NULL, -- Unique Property Reference Number

    -- Address components
    building_name VARCHAR(255),
    building_number VARCHAR(50),
    street VARCHAR(255),
    locality VARCHAR(255),
    town_city VARCHAR(255) NOT NULL,
    postcode VARCHAR(10) NOT NULL,

    -- Normalised full address for matching
    address_normalised TEXT NOT NULL,

    -- Geospatial
    location GEOGRAPHY(POINT, 4326) NOT NULL, -- WGS84 lat/lng

    -- Property characteristics
    property_type VARCHAR(50), -- detached, semi-detached, terraced, flat
    built_form VARCHAR(50), -- house, bungalow, flat, maisonette

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_properties_postcode ON properties(postcode);
CREATE INDEX idx_properties_location ON properties USING GIST(location);
CREATE INDEX idx_properties_address_trgm ON properties USING GIN(address_normalised gin_trgm_ops);
CREATE INDEX idx_properties_uprn ON properties(uprn);

-- =====================================================
-- ESTATE AGENTS
-- =====================================================

CREATE TABLE agents (
    agent_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    branch_name VARCHAR(255),

    -- Scraper config (prototype only)
    website_url TEXT,
    scraper_config JSONB, -- CSS selectors, pagination rules, etc.

    -- Contact
    phone VARCHAR(50),
    email VARCHAR(255),

    -- Status
    is_active BOOLEAN DEFAULT true,
    last_scraped_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_agents_active ON agents(is_active) WHERE is_active = true;

-- =====================================================
-- RAW LISTINGS (from scrapers)
-- =====================================================

CREATE TABLE listings_raw (
    raw_listing_id BIGSERIAL PRIMARY KEY,
    agent_id INTEGER NOT NULL REFERENCES agents(agent_id),

    -- External identifiers
    external_listing_id VARCHAR(255) NOT NULL, -- Agent's own ID
    listing_url TEXT NOT NULL,

    -- Raw scraped data
    title TEXT,
    description TEXT,
    price_text VARCHAR(255), -- e.g. "£450,000", "Offers Over £500k"
    price_numeric NUMERIC(12, 2), -- Parsed price

    bedrooms INTEGER,
    bathrooms INTEGER,
    receptions INTEGER,

    property_type VARCHAR(100),
    tenure VARCHAR(50), -- freehold, leasehold, shared ownership

    -- Address (as scraped - might be incomplete)
    raw_address TEXT NOT NULL,
    postcode VARCHAR(10),

    -- Images
    image_urls JSONB, -- ["url1", "url2", ...]

    -- Listing metadata
    listed_date DATE,
    last_updated_date DATE,
    status VARCHAR(50) DEFAULT 'active', -- active, under_offer, sold, withdrawn

    -- Matching status
    matched_property_id BIGINT REFERENCES properties(property_id),
    match_confidence NUMERIC(3, 2), -- 0.00 to 1.00
    match_method VARCHAR(50), -- uprn_exact, postcode_number, address_fuzzy

    -- Timestamps
    scraped_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(agent_id, external_listing_id)
);

CREATE INDEX idx_listings_raw_agent ON listings_raw(agent_id);
CREATE INDEX idx_listings_raw_status ON listings_raw(status);
CREATE INDEX idx_listings_raw_matched_property ON listings_raw(matched_property_id);
CREATE INDEX idx_listings_raw_postcode ON listings_raw(postcode) WHERE postcode IS NOT NULL;

-- =====================================================
-- ENRICHED LISTINGS (search-optimised)
-- =====================================================

CREATE TABLE listings_enriched (
    listing_id BIGSERIAL PRIMARY KEY,
    raw_listing_id BIGINT NOT NULL REFERENCES listings_raw(raw_listing_id) UNIQUE,
    property_id BIGINT NOT NULL REFERENCES properties(property_id),
    agent_id INTEGER NOT NULL REFERENCES agents(agent_id),

    -- Core listing data (denormalised from raw)
    title TEXT NOT NULL,
    description TEXT,
    price NUMERIC(12, 2) NOT NULL,
    bedrooms INTEGER NOT NULL,
    bathrooms INTEGER,
    property_type VARCHAR(50),
    tenure VARCHAR(50),

    -- Address (from properties table)
    address TEXT NOT NULL,
    postcode VARCHAR(10) NOT NULL,
    location GEOGRAPHY(POINT, 4326) NOT NULL,

    -- Status
    status VARCHAR(50) DEFAULT 'active',
    listed_date DATE,

    -- ==================
    -- ENRICHED FEATURES
    -- ==================

    -- EPC Data
    epc_rating VARCHAR(1), -- A-G
    epc_score INTEGER, -- 1-100
    epc_potential_rating VARCHAR(1),
    epc_co2_emissions_current NUMERIC(8, 2),
    epc_energy_consumption_current NUMERIC(8, 2),

    -- Conservation & Planning
    in_conservation_area BOOLEAN DEFAULT false,
    conservation_area_name VARCHAR(255),
    planning_constraints JSONB, -- {listed_building: true, tpo: false, ...}
    recent_planning_apps INTEGER DEFAULT 0, -- Count in last 5 years
    planning_refusals INTEGER DEFAULT 0,

    -- Location Quality Metrics (0-1 normalised)
    school_quality_score NUMERIC(3, 2), -- Based on nearest primary/secondary Ofsted
    distance_to_nearest_primary_m INTEGER,
    distance_to_nearest_secondary_m INTEGER,

    -- Transport
    distance_to_nearest_station_m INTEGER,
    distance_to_nearest_airport_m INTEGER,
    nearest_airport_code VARCHAR(10),

    -- Area Quality
    imd_decile INTEGER, -- 1 (most deprived) to 10 (least deprived)
    crime_rate_percentile INTEGER, -- 0-100 (lower = less crime)
    flood_risk VARCHAR(20), -- very_low, low, medium, high

    -- Broadband
    max_download_speed_mbps INTEGER,

    -- AVM Valuation
    avm_estimate NUMERIC(12, 2),
    avm_confidence_interval_lower NUMERIC(12, 2),
    avm_confidence_interval_upper NUMERIC(12, 2),
    avm_confidence_score NUMERIC(3, 2), -- 0-1
    avm_value_delta_pct NUMERIC(5, 2), -- (price - avm_estimate) / avm_estimate * 100

    -- Derived flags
    is_undervalued BOOLEAN GENERATED ALWAYS AS (avm_value_delta_pct < -5) STORED,
    is_overvalued BOOLEAN GENERATED ALWAYS AS (avm_value_delta_pct > 5) STORED,

    -- Full-text search
    search_vector tsvector GENERATED ALWAYS AS (
        setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(description, '')), 'B') ||
        setweight(to_tsvector('english', coalesce(address, '')), 'C')
    ) STORED,

    -- Metadata
    enriched_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_listings_enriched_property ON listings_enriched(property_id);
CREATE INDEX idx_listings_enriched_agent ON listings_enriched(agent_id);
CREATE INDEX idx_listings_enriched_status ON listings_enriched(status);
CREATE INDEX idx_listings_enriched_price ON listings_enriched(price);
CREATE INDEX idx_listings_enriched_bedrooms ON listings_enriched(bedrooms);
CREATE INDEX idx_listings_enriched_location ON listings_enriched USING GIST(location);
CREATE INDEX idx_listings_enriched_postcode ON listings_enriched(postcode);
CREATE INDEX idx_listings_enriched_search ON listings_enriched USING GIN(search_vector);

-- Composite index for common filters
CREATE INDEX idx_listings_enriched_search_filters ON listings_enriched(status, price, bedrooms, property_type);

-- =====================================================
-- FEATURE TABLES (reference data from S3)
-- =====================================================

-- Schools (loaded from S3/gov.uk data)
CREATE TABLE schools (
    school_id SERIAL PRIMARY KEY,
    urn INTEGER UNIQUE NOT NULL, -- Unique Reference Number
    name VARCHAR(255) NOT NULL,
    school_type VARCHAR(100), -- primary, secondary
    phase VARCHAR(50),

    location GEOGRAPHY(POINT, 4326) NOT NULL,
    postcode VARCHAR(10),

    ofsted_rating VARCHAR(50), -- outstanding, good, requires_improvement, inadequate
    ofsted_rating_score INTEGER, -- 4=outstanding, 1=inadequate
    ofsted_date DATE,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_schools_location ON schools USING GIST(location);
CREATE INDEX idx_schools_type ON schools(school_type);

-- Airports
CREATE TABLE airports (
    airport_id SERIAL PRIMARY KEY,
    iata_code VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    location GEOGRAPHY(POINT, 4326) NOT NULL
);

CREATE INDEX idx_airports_location ON airports USING GIST(location);

-- Conservation Areas (loaded from local authority data)
CREATE TABLE conservation_areas (
    conservation_area_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    local_authority VARCHAR(255),
    boundary GEOGRAPHY(POLYGON, 4326) NOT NULL,
    designated_date DATE
);

CREATE INDEX idx_conservation_areas_boundary ON conservation_areas USING GIST(boundary);

-- =====================================================
-- USER QUESTIONNAIRES & SEARCHES
-- =====================================================

CREATE TABLE user_searches (
    search_id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(255), -- Future: FK to users table

    -- Questionnaire response (full JSON)
    questionnaire_data JSONB NOT NULL,

    -- Parsed filters (denormalised for quick access)
    budget_min NUMERIC(12, 2),
    budget_max NUMERIC(12, 2),
    bedrooms_min INTEGER,
    property_types VARCHAR(50)[],

    -- Location constraints
    postcode_areas VARCHAR(10)[], -- e.g. ['SW1', 'W1']
    radius_km NUMERIC(5, 2),
    max_distance_to_airport_km NUMERIC(5, 2),
    target_airports VARCHAR(10)[], -- IATA codes

    -- Preference weights (0-1)
    weight_schools NUMERIC(3, 2) DEFAULT 0,
    weight_commute NUMERIC(3, 2) DEFAULT 0,
    weight_safety NUMERIC(3, 2) DEFAULT 0,
    weight_energy NUMERIC(3, 2) DEFAULT 0,
    weight_value NUMERIC(3, 2) DEFAULT 0,
    weight_conservation NUMERIC(3, 2) DEFAULT 0,

    -- Results count
    results_count INTEGER,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_user_searches_user ON user_searches(user_id);

-- =====================================================
-- PURCHASED REPORTS
-- =====================================================

CREATE TABLE purchased_reports (
    report_id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    listing_id BIGINT NOT NULL REFERENCES listings_enriched(listing_id),

    -- Payment
    payment_intent_id VARCHAR(255) UNIQUE NOT NULL, -- Stripe payment intent
    amount_gbp NUMERIC(6, 2) NOT NULL DEFAULT 5.00,
    payment_status VARCHAR(50) DEFAULT 'pending', -- pending, succeeded, failed

    -- Report
    report_s3_key TEXT, -- s3://bucket/reports/{report_id}.pdf
    report_url TEXT, -- CloudFront signed URL

    -- Metadata
    generated_at TIMESTAMPTZ,
    purchased_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_purchased_reports_user ON purchased_reports(user_id);
CREATE INDEX idx_purchased_reports_listing ON purchased_reports(listing_id);
CREATE INDEX idx_purchased_reports_payment ON purchased_reports(payment_intent_id);

-- =====================================================
-- MATERIALIZED VIEW: Search-optimised listing feed
-- =====================================================

-- Refresh this periodically (e.g. every 5 mins) or after enrichment batches
CREATE MATERIALIZED VIEW listings_search AS
SELECT
    listing_id,
    property_id,
    agent_id,
    title,
    price,
    bedrooms,
    bathrooms,
    property_type,
    tenure,
    address,
    postcode,
    ST_Y(location::geometry) AS latitude,
    ST_X(location::geometry) AS longitude,
    location,

    -- Enriched scores (pre-computed)
    epc_rating,
    epc_score,
    in_conservation_area,
    school_quality_score,
    distance_to_nearest_airport_m,
    imd_decile,
    crime_rate_percentile,
    flood_risk,

    avm_estimate,
    avm_value_delta_pct,
    is_undervalued,

    search_vector,
    status,
    listed_date
FROM listings_enriched
WHERE status = 'active';

CREATE UNIQUE INDEX idx_listings_search_listing_id ON listings_search(listing_id);
CREATE INDEX idx_listings_search_location ON listings_search USING GIST(location);
CREATE INDEX idx_listings_search_price ON listings_search(price);
CREATE INDEX idx_listings_search_bedrooms ON listings_search(bedrooms);
CREATE INDEX idx_listings_search_text ON listings_search USING GIN(search_vector);

-- =====================================================
-- TRIGGERS
-- =====================================================

-- Auto-update updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_properties_updated_at BEFORE UPDATE ON properties
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_listings_raw_updated_at BEFORE UPDATE ON listings_raw
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_listings_enriched_updated_at BEFORE UPDATE ON listings_enriched
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
