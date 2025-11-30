"""
Property report generation.

Generates detailed PDF reports for purchased properties using:
- Jinja2 for HTML templating
- WeasyPrint for PDF conversion
- S3 for storage
- CloudFront for delivery
"""
import os
import logging
from datetime import datetime
from typing import Dict, Any
from decimal import Decimal
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import boto3

from config.database import SessionLocal
from api.models.database import PurchasedReport, ListingEnriched, Property

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generates property reports"""

    def __init__(self):
        self.template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(self.template_dir))

        # S3 client
        self.s3_client = boto3.client('s3')
        self.bucket = os.getenv('REPORTS_S3_BUCKET', 'uk-property-reports')
        self.cloudfront_domain = os.getenv('CLOUDFRONT_DOMAIN', 'd1234567890.cloudfront.net')

    def generate(self, report_id: int, listing_id: int) -> str:
        """
        Generate report and upload to S3.

        Args:
            report_id: PurchasedReport ID
            listing_id: ListingEnriched ID

        Returns:
            CloudFront URL of generated report
        """
        logger.info(f"Generating report {report_id} for listing {listing_id}")

        # Gather data
        db = SessionLocal()
        try:
            report_data = self._gather_report_data(db, listing_id)

            # Render HTML
            html_content = self._render_html(report_data)

            # Convert to PDF
            pdf_bytes = self._html_to_pdf(html_content)

            # Upload to S3
            s3_key = f"reports/{report_id}.pdf"
            self._upload_to_s3(pdf_bytes, s3_key)

            # Generate CloudFront URL
            report_url = f"https://{self.cloudfront_domain}/{s3_key}"

            # Update database
            purchase = db.query(PurchasedReport).filter(
                PurchasedReport.report_id == report_id
            ).first()
            purchase.report_s3_key = s3_key
            purchase.report_url = report_url
            purchase.generated_at = datetime.utcnow()
            db.commit()

            logger.info(f"Report {report_id} generated: {report_url}")
            return report_url

        finally:
            db.close()

    def _gather_report_data(self, db, listing_id: int) -> Dict[str, Any]:
        """Gather all data needed for report"""

        # Fetch listing
        listing = db.query(ListingEnriched).filter(
            ListingEnriched.listing_id == listing_id
        ).first()

        if not listing:
            raise ValueError(f"Listing {listing_id} not found")

        # Fetch property
        prop = db.query(Property).filter(
            Property.property_id == listing.property_id
        ).first()

        # Compile data
        data = {
            # Metadata
            'generated_at': datetime.utcnow().strftime('%d %B %Y'),
            'report_id': listing_id,

            # Listing basics
            'title': listing.title,
            'address': listing.address,
            'postcode': listing.postcode,
            'price': f"£{listing.price:,.0f}",
            'bedrooms': listing.bedrooms,
            'bathrooms': listing.bathrooms,
            'property_type': listing.property_type,
            'tenure': listing.tenure,
            'description': listing.description,

            # EPC
            'epc_rating': listing.epc_rating,
            'epc_score': listing.epc_score,
            'epc_potential': listing.epc_potential_rating,
            'epc_co2': listing.epc_co2_emissions_current,

            # Conservation
            'in_conservation_area': listing.in_conservation_area,
            'conservation_area_name': listing.conservation_area_name,

            # Planning
            'planning_constraints': listing.planning_constraints or {},
            'recent_planning_apps': listing.recent_planning_apps,
            'planning_refusals': listing.planning_refusals,

            # Schools
            'school_quality_score': float(listing.school_quality_score) if listing.school_quality_score else None,
            'nearest_primary_m': listing.distance_to_nearest_primary_m,
            'nearest_secondary_m': listing.distance_to_nearest_secondary_m,

            # Transport
            'nearest_station_m': listing.distance_to_nearest_station_m,
            'nearest_airport_m': listing.distance_to_nearest_airport_m,
            'nearest_airport_code': listing.nearest_airport_code,

            # Area quality
            'imd_decile': listing.imd_decile,
            'crime_percentile': listing.crime_rate_percentile,
            'flood_risk': listing.flood_risk,
            'broadband_mbps': listing.max_download_speed_mbps,

            # AVM
            'avm_estimate': f"£{listing.avm_estimate:,.0f}" if listing.avm_estimate else "N/A",
            'avm_lower': f"£{listing.avm_confidence_interval_lower:,.0f}" if listing.avm_confidence_interval_lower else "N/A",
            'avm_upper': f"£{listing.avm_confidence_interval_upper:,.0f}" if listing.avm_confidence_interval_upper else "N/A",
            'avm_confidence': f"{listing.avm_confidence_score * 100:.0f}%" if listing.avm_confidence_score else "N/A",
            'avm_delta_pct': listing.avm_value_delta_pct,
            'is_undervalued': listing.is_undervalued,

            # Placeholder for additional sections
            'restrictive_covenants': self._get_restrictive_covenants(prop.uprn),
            'planning_applications': self._get_planning_applications(prop.uprn),
        }

        return data

    def _render_html(self, data: Dict[str, Any]) -> str:
        """Render HTML from template"""
        template = self.jinja_env.get_template('property_report.html')
        return template.render(**data)

    def _html_to_pdf(self, html_content: str) -> bytes:
        """Convert HTML to PDF using WeasyPrint"""
        pdf = HTML(string=html_content).write_pdf()
        return pdf

    def _upload_to_s3(self, pdf_bytes: bytes, s3_key: str):
        """Upload PDF to S3"""
        self.s3_client.put_object(
            Bucket=self.bucket,
            Key=s3_key,
            Body=pdf_bytes,
            ContentType='application/pdf',
            ServerSideEncryption='AES256'
        )

    def _get_restrictive_covenants(self, uprn: int) -> list:
        """
        Fetch restrictive covenants for property.

        PLACEHOLDER: In production, query HM Land Registry API or internal dataset.
        """
        # Mock data
        return [
            {
                'description': 'No commercial use permitted',
                'date_imposed': '1985-03-15'
            }
        ]

    def _get_planning_applications(self, uprn: int) -> list:
        """
        Fetch detailed planning applications.

        PLACEHOLDER: In production, query from S3 or planning API.
        """
        # Mock data
        return [
            {
                'reference': '2022/12345/FULL',
                'description': 'Single storey rear extension',
                'decision': 'Approved',
                'decision_date': '2022-06-15',
                'status': 'Completed'
            }
        ]


def generate_report_task(report_id: int, listing_id: int):
    """
    Background task to generate report.

    Called from FastAPI BackgroundTasks or Celery.
    """
    generator = ReportGenerator()
    try:
        generator.generate(report_id, listing_id)
    except Exception as e:
        logger.error(f"Failed to generate report {report_id}: {e}", exc_info=True)
        # In production, update PurchasedReport with error status
