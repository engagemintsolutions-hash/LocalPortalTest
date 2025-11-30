"""
SQLAlchemy ORM models
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from sqlalchemy import (
    Column, Integer, BigInteger, String, Text, Numeric, Boolean,
    DateTime, Date, ForeignKey, Index, JSON, ARRAY, func
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography

Base = declarative_base()


class Property(Base):
    __tablename__ = 'properties'

    property_id = Column(BigInteger, primary_key=True, autoincrement=True)
    uprn = Column(BigInteger, unique=True, nullable=False, index=True)

    # Address
    building_name = Column(String(255))
    building_number = Column(String(50))
    street = Column(String(255))
    locality = Column(String(255))
    town_city = Column(String(255), nullable=False)
    postcode = Column(String(10), nullable=False, index=True)
    address_normalised = Column(Text, nullable=False)

    # Geospatial
    location = Column(Geography('POINT', srid=4326), nullable=False)

    # Characteristics
    property_type = Column(String(50))
    built_form = Column(String(50))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    listings_raw = relationship("ListingRaw", back_populates="property")
    listings_enriched = relationship("ListingEnriched", back_populates="property")


class Agent(Base):
    __tablename__ = 'agents'

    agent_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    branch_name = Column(String(255))

    # Scraper config
    website_url = Column(Text)
    scraper_config = Column(JSONB)

    # Contact
    phone = Column(String(50))
    email = Column(String(255))

    # Status
    is_active = Column(Boolean, default=True, index=True)
    last_scraped_at = Column(DateTime(timezone=True))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    listings_raw = relationship("ListingRaw", back_populates="agent")
    listings_enriched = relationship("ListingEnriched", back_populates="agent")


class ListingRaw(Base):
    __tablename__ = 'listings_raw'

    raw_listing_id = Column(BigInteger, primary_key=True, autoincrement=True)
    agent_id = Column(Integer, ForeignKey('agents.agent_id'), nullable=False, index=True)

    # External identifiers
    external_listing_id = Column(String(255), nullable=False)
    listing_url = Column(Text, nullable=False)

    # Raw data
    title = Column(Text)
    description = Column(Text)
    price_text = Column(String(255))
    price_numeric = Column(Numeric(12, 2))

    bedrooms = Column(Integer)
    bathrooms = Column(Integer)
    receptions = Column(Integer)

    property_type = Column(String(100))
    tenure = Column(String(50))

    # Address
    raw_address = Column(Text, nullable=False)
    postcode = Column(String(10), index=True)

    # Images
    image_urls = Column(JSONB)

    # Listing metadata
    listed_date = Column(Date)
    last_updated_date = Column(Date)
    status = Column(String(50), default='active', index=True)

    # Matching
    matched_property_id = Column(BigInteger, ForeignKey('properties.property_id'), index=True)
    match_confidence = Column(Numeric(3, 2))
    match_method = Column(String(50))

    # Timestamps
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    agent = relationship("Agent", back_populates="listings_raw")
    property = relationship("Property", back_populates="listings_raw")
    enriched = relationship("ListingEnriched", back_populates="raw_listing", uselist=False)

    __table_args__ = (
        Index('idx_listings_raw_agent_external', 'agent_id', 'external_listing_id', unique=True),
    )


class ListingEnriched(Base):
    __tablename__ = 'listings_enriched'

    listing_id = Column(BigInteger, primary_key=True, autoincrement=True)
    raw_listing_id = Column(BigInteger, ForeignKey('listings_raw.raw_listing_id'), unique=True, nullable=False)
    property_id = Column(BigInteger, ForeignKey('properties.property_id'), nullable=False, index=True)
    agent_id = Column(Integer, ForeignKey('agents.agent_id'), nullable=False, index=True)

    # Core listing data
    title = Column(Text, nullable=False)
    description = Column(Text)
    price = Column(Numeric(12, 2), nullable=False, index=True)
    bedrooms = Column(Integer, nullable=False, index=True)
    bathrooms = Column(Integer)
    property_type = Column(String(50), index=True)
    tenure = Column(String(50))

    # Address
    address = Column(Text, nullable=False)
    postcode = Column(String(10), nullable=False, index=True)
    location = Column(Geography('POINT', srid=4326), nullable=False)

    # Status
    status = Column(String(50), default='active', index=True)
    listed_date = Column(Date)

    # EPC
    epc_rating = Column(String(1))
    epc_score = Column(Integer)
    epc_potential_rating = Column(String(1))
    epc_co2_emissions_current = Column(Numeric(8, 2))
    epc_energy_consumption_current = Column(Numeric(8, 2))

    # Conservation & Planning
    in_conservation_area = Column(Boolean, default=False)
    conservation_area_name = Column(String(255))
    planning_constraints = Column(JSONB)
    recent_planning_apps = Column(Integer, default=0)
    planning_refusals = Column(Integer, default=0)

    # Location quality
    school_quality_score = Column(Numeric(3, 2))
    distance_to_nearest_primary_m = Column(Integer)
    distance_to_nearest_secondary_m = Column(Integer)

    # Transport
    distance_to_nearest_station_m = Column(Integer)
    distance_to_nearest_airport_m = Column(Integer)
    nearest_airport_code = Column(String(10))

    # Area quality
    imd_decile = Column(Integer)
    crime_rate_percentile = Column(Integer)
    flood_risk = Column(String(20))
    max_download_speed_mbps = Column(Integer)

    # AVM
    avm_estimate = Column(Numeric(12, 2))
    avm_confidence_interval_lower = Column(Numeric(12, 2))
    avm_confidence_interval_upper = Column(Numeric(12, 2))
    avm_confidence_score = Column(Numeric(3, 2))
    avm_value_delta_pct = Column(Numeric(5, 2))

    # Timestamps
    enriched_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    raw_listing = relationship("ListingRaw", back_populates="enriched")
    property = relationship("Property", back_populates="listings_enriched")
    agent = relationship("Agent", back_populates="listings_enriched")
    reports = relationship("PurchasedReport", back_populates="listing")


class School(Base):
    __tablename__ = 'schools'

    school_id = Column(Integer, primary_key=True, autoincrement=True)
    urn = Column(Integer, unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    school_type = Column(String(100), index=True)
    phase = Column(String(50))

    location = Column(Geography('POINT', srid=4326), nullable=False)
    postcode = Column(String(10))

    ofsted_rating = Column(String(50))
    ofsted_rating_score = Column(Integer)
    ofsted_date = Column(Date)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Airport(Base):
    __tablename__ = 'airports'

    airport_id = Column(Integer, primary_key=True, autoincrement=True)
    iata_code = Column(String(10), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    location = Column(Geography('POINT', srid=4326), nullable=False)


class ConservationArea(Base):
    __tablename__ = 'conservation_areas'

    conservation_area_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    local_authority = Column(String(255))
    boundary = Column(Geography('POLYGON', srid=4326), nullable=False)
    designated_date = Column(Date)


class UserSearch(Base):
    __tablename__ = 'user_searches'

    search_id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(String(255), index=True)

    # Full questionnaire
    questionnaire_data = Column(JSONB, nullable=False)

    # Denormalised filters
    budget_min = Column(Numeric(12, 2))
    budget_max = Column(Numeric(12, 2))
    bedrooms_min = Column(Integer)
    property_types = Column(ARRAY(String(50)))

    # Location
    postcode_areas = Column(ARRAY(String(10)))
    radius_km = Column(Numeric(5, 2))
    max_distance_to_airport_km = Column(Numeric(5, 2))
    target_airports = Column(ARRAY(String(10)))

    # Weights
    weight_schools = Column(Numeric(3, 2), default=0)
    weight_commute = Column(Numeric(3, 2), default=0)
    weight_safety = Column(Numeric(3, 2), default=0)
    weight_energy = Column(Numeric(3, 2), default=0)
    weight_value = Column(Numeric(3, 2), default=0)
    weight_conservation = Column(Numeric(3, 2), default=0)

    results_count = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PurchasedReport(Base):
    __tablename__ = 'purchased_reports'

    report_id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=False, index=True)
    listing_id = Column(BigInteger, ForeignKey('listings_enriched.listing_id'), nullable=False, index=True)

    # Payment
    payment_intent_id = Column(String(255), unique=True, nullable=False, index=True)
    amount_gbp = Column(Numeric(6, 2), nullable=False, default=5.00)
    payment_status = Column(String(50), default='pending')

    # Report
    report_s3_key = Column(Text)
    report_url = Column(Text)

    generated_at = Column(DateTime(timezone=True))
    purchased_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    listing = relationship("ListingEnriched", back_populates="reports")
