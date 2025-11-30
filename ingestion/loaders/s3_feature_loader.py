"""
Load feature data from S3 Parquet files into DuckDB for fast querying.

This module creates an in-memory (or persistent) DuckDB database that can
directly query S3 Parquet files and join them with property data.
"""
import os
from typing import Optional, Dict, Any, List
import duckdb
from decimal import Decimal


class S3FeatureStore:
    """
    DuckDB-based feature store that reads from S3 Parquet files.

    Features stored:
    - EPC data (energy performance certificates)
    - Planning applications and decisions
    - IMD (Index of Multiple Deprivation)
    - Crime statistics
    - Flood risk zones
    - Broadband availability
    """

    def __init__(self, db_path: str = ":memory:", s3_bucket: str = None):
        """
        Initialize the feature store.

        Args:
            db_path: Path to DuckDB database file (":memory:" for in-memory)
            s3_bucket: S3 bucket name containing feature parquet files
        """
        self.db_path = db_path
        self.s3_bucket = s3_bucket or os.getenv("FEATURE_S3_BUCKET", "uk-property-features")
        self.conn = duckdb.connect(db_path)

        # Configure S3 access (uses AWS credentials from environment)
        self.conn.execute("INSTALL httpfs;")
        self.conn.execute("LOAD httpfs;")

        # Optional: configure S3 region
        region = os.getenv("AWS_REGION", "eu-west-2")
        self.conn.execute(f"SET s3_region='{region}';")

        # Create views over S3 data
        self._create_views()

    def _create_views(self):
        """Create views/tables from S3 Parquet files"""

        # EPC Data
        self.conn.execute(f"""
            CREATE OR REPLACE VIEW epc_data AS
            SELECT
                uprn,
                current_energy_rating AS epc_rating,
                current_energy_efficiency AS epc_score,
                potential_energy_rating AS epc_potential_rating,
                co2_emissions_current AS epc_co2_emissions_current,
                energy_consumption_current AS epc_energy_consumption_current,
                postcode
            FROM read_parquet('s3://{self.s3_bucket}/epc/*.parquet')
        """)

        # IMD (deprivation index) - postcode level
        self.conn.execute(f"""
            CREATE OR REPLACE VIEW imd_data AS
            SELECT
                postcode,
                imd_decile,
                crime_score,
                crime_percentile AS crime_rate_percentile
            FROM read_parquet('s3://{self.s3_bucket}/imd/*.parquet')
        """)

        # Flood risk - by UPRN or postcode
        self.conn.execute(f"""
            CREATE OR REPLACE VIEW flood_data AS
            SELECT
                uprn,
                postcode,
                flood_risk_level AS flood_risk
            FROM read_parquet('s3://{self.s3_bucket}/flood/*.parquet')
        """)

        # Broadband availability
        self.conn.execute(f"""
            CREATE OR REPLACE VIEW broadband_data AS
            SELECT
                postcode,
                max_download_speed_mbps
            FROM read_parquet('s3://{self.s3_bucket}/broadband/*.parquet')
        """)

        # Planning applications (aggregated by UPRN)
        self.conn.execute(f"""
            CREATE OR REPLACE VIEW planning_data AS
            SELECT
                uprn,
                COUNT(*) AS total_planning_apps,
                SUM(CASE WHEN decision = 'Refused' THEN 1 ELSE 0 END) AS planning_refusals,
                SUM(CASE WHEN application_date >= CURRENT_DATE - INTERVAL '5 years' THEN 1 ELSE 0 END) AS recent_planning_apps
            FROM read_parquet('s3://{self.s3_bucket}/planning/*.parquet')
            GROUP BY uprn
        """)

    def get_property_features(self, uprn: int, postcode: str) -> Dict[str, Any]:
        """
        Get all feature data for a property.

        Args:
            uprn: Unique Property Reference Number
            postcode: Property postcode

        Returns:
            Dictionary of feature values
        """
        query = f"""
            SELECT
                -- EPC
                epc.epc_rating,
                epc.epc_score,
                epc.epc_potential_rating,
                epc.epc_co2_emissions_current,
                epc.epc_energy_consumption_current,

                -- Area quality
                imd.imd_decile,
                imd.crime_rate_percentile,

                -- Flood
                flood.flood_risk,

                -- Broadband
                bb.max_download_speed_mbps,

                -- Planning
                COALESCE(planning.recent_planning_apps, 0) AS recent_planning_apps,
                COALESCE(planning.planning_refusals, 0) AS planning_refusals

            FROM (SELECT '{postcode}' AS postcode, {uprn} AS uprn) AS prop
            LEFT JOIN epc_data epc ON epc.uprn = prop.uprn
            LEFT JOIN imd_data imd ON imd.postcode = prop.postcode
            LEFT JOIN flood_data flood ON flood.uprn = prop.uprn OR flood.postcode = prop.postcode
            LEFT JOIN broadband_data bb ON bb.postcode = prop.postcode
            LEFT JOIN planning_data planning ON planning.uprn = prop.uprn
        """

        result = self.conn.execute(query).fetchone()

        if not result:
            return {}

        columns = [desc[0] for desc in self.conn.description]
        return dict(zip(columns, result))

    def get_batch_features(self, properties: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Get features for multiple properties in batch.

        Args:
            properties: List of dicts with 'uprn' and 'postcode' keys

        Returns:
            List of feature dictionaries
        """
        if not properties:
            return []

        # Create temp table with properties
        self.conn.execute("DROP TABLE IF EXISTS temp_properties")
        self.conn.execute("""
            CREATE TEMP TABLE temp_properties (
                property_id BIGINT,
                uprn BIGINT,
                postcode VARCHAR(10)
            )
        """)

        # Insert properties
        for prop in properties:
            self.conn.execute("""
                INSERT INTO temp_properties VALUES (?, ?, ?)
            """, [prop['property_id'], prop['uprn'], prop['postcode']])

        # Batch query
        query = """
            SELECT
                prop.property_id,
                prop.uprn,
                epc.epc_rating,
                epc.epc_score,
                epc.epc_potential_rating,
                epc.epc_co2_emissions_current,
                epc.epc_energy_consumption_current,
                imd.imd_decile,
                imd.crime_rate_percentile,
                flood.flood_risk,
                bb.max_download_speed_mbps,
                COALESCE(planning.recent_planning_apps, 0) AS recent_planning_apps,
                COALESCE(planning.planning_refusals, 0) AS planning_refusals
            FROM temp_properties prop
            LEFT JOIN epc_data epc ON epc.uprn = prop.uprn
            LEFT JOIN imd_data imd ON imd.postcode = prop.postcode
            LEFT JOIN flood_data flood ON flood.uprn = prop.uprn OR flood.postcode = prop.postcode
            LEFT JOIN broadband_data bb ON bb.postcode = prop.postcode
            LEFT JOIN planning_data planning ON planning.uprn = prop.uprn
        """

        results = self.conn.execute(query).fetchall()
        columns = [desc[0] for desc in self.conn.description]

        return [dict(zip(columns, row)) for row in results]

    def close(self):
        """Close the DuckDB connection"""
        self.conn.close()


# Singleton instance
_feature_store: Optional[S3FeatureStore] = None


def get_feature_store() -> S3FeatureStore:
    """Get or create the global feature store instance"""
    global _feature_store
    if _feature_store is None:
        _feature_store = S3FeatureStore()
    return _feature_store
