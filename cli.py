"""
CLI for running common tasks
"""
import click
from config.database import SessionLocal
from ingestion.scrapers.orchestrator import run_scraping_job
from enrichment.enricher import enrich_all_unmatched_listings
from api.models.database import ListingRaw
from matching.matchers.address_matcher import match_listing_to_property


@click.group()
def cli():
    """UK Property Search Engine CLI"""
    pass


@cli.command()
def scrape():
    """Run scraping job for all agents"""
    click.echo("Starting scraping job...")
    db = SessionLocal()
    try:
        stats = run_scraping_job(db)
        click.echo(f"\nScraping completed:")
        click.echo(f"  Total agents: {stats['total_agents']}")
        click.echo(f"  Successful: {stats['successful_agents']}")
        click.echo(f"  Failed: {stats['failed_agents']}")
        click.echo(f"  Total listings scraped: {stats['total_listings_scraped']}")
        click.echo(f"  New: {stats['total_listings_new']}")
        click.echo(f"  Updated: {stats['total_listings_updated']}")
    finally:
        db.close()


@cli.command()
def match():
    """Match unmatched raw listings to properties"""
    click.echo("Matching raw listings to properties...")
    db = SessionLocal()
    try:
        unmatched = db.query(ListingRaw).filter(
            ListingRaw.matched_property_id.is_(None),
            ListingRaw.postcode.isnot(None)
        ).all()

        click.echo(f"Found {len(unmatched)} unmatched listings")

        matched_count = 0
        for raw in unmatched:
            result = match_listing_to_property(db, raw.raw_address, raw.postcode)
            if result:
                raw.matched_property_id = result[0]
                raw.match_confidence = result[1]
                raw.match_method = result[2]
                matched_count += 1

                if matched_count % 100 == 0:
                    click.echo(f"  Matched {matched_count} listings...")

        db.commit()
        click.echo(f"\nMatching completed: {matched_count} / {len(unmatched)} matched")

    finally:
        db.close()


@cli.command()
def enrich():
    """Enrich matched listings"""
    click.echo("Enriching matched listings...")
    db = SessionLocal()
    try:
        count = enrich_all_unmatched_listings(db)
        click.echo(f"Enriched {count} listings")
    finally:
        db.close()


@cli.command()
def pipeline():
    """Run full pipeline: scrape -> match -> enrich"""
    click.echo("Running full ingestion pipeline...\n")

    # Step 1: Scrape
    click.echo("=" * 50)
    click.echo("STEP 1: SCRAPING")
    click.echo("=" * 50)
    ctx = click.get_current_context()
    ctx.invoke(scrape)

    # Step 2: Match
    click.echo("\n" + "=" * 50)
    click.echo("STEP 2: MATCHING")
    click.echo("=" * 50)
    ctx.invoke(match)

    # Step 3: Enrich
    click.echo("\n" + "=" * 50)
    click.echo("STEP 3: ENRICHMENT")
    click.echo("=" * 50)
    ctx.invoke(enrich)

    click.echo("\n" + "=" * 50)
    click.echo("PIPELINE COMPLETED")
    click.echo("=" * 50)


@cli.command()
@click.option('--host', default='0.0.0.0', help='Host to bind')
@click.option('--port', default=8000, help='Port to bind')
@click.option('--reload', is_flag=True, help='Enable auto-reload')
def serve(host, port, reload):
    """Start the API server"""
    import uvicorn
    click.echo(f"Starting API server on {host}:{port}")
    uvicorn.run("api.main:app", host=host, port=port, reload=reload)


@cli.command()
def init_db():
    """Initialize database (create tables)"""
    from api.models.database import Base
    from config.database import engine

    click.echo("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    click.echo("Database initialized successfully")


if __name__ == '__main__':
    cli()
