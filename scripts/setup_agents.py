"""
Setup script to add estate agents to the database
"""
from config.database import SessionLocal
from api.models.database import Agent


def setup_agents():
    """Add estate agents to database"""
    db = SessionLocal()

    agents_to_add = [
        {
            'name': 'Foxtons',
            'branch_name': 'Central London',
            'website_url': 'www.foxtons.co.uk',
            'is_active': True,
            'scraper_config': {
                'base_url': 'https://www.foxtons.co.uk',
                'search_url_template': 'https://www.foxtons.co.uk/properties-for-sale/london?page={page}',
                'max_pages': 20,
                'delay_seconds': 2.0
            }
        },
        {
            'name': 'Chestertons',
            'branch_name': 'London',
            'website_url': 'www.chestertons.co.uk',
            'is_active': True,
            'scraper_config': {
                'base_url': 'https://www.chestertons.co.uk',
                'search_url_template': 'https://www.chestertons.co.uk/property-for-sale?page={page}',
                'max_pages': 20,
                'delay_seconds': 2.0
            }
        },
        {
            'name': 'Kinleigh Folkard & Hayward',
            'branch_name': 'London',
            'website_url': 'www.kfh.co.uk',
            'is_active': True,
            'scraper_config': {
                'base_url': 'https://www.kfh.co.uk',
                'search_url_template': 'https://www.kfh.co.uk/properties/for-sale?page={page}',
                'max_pages': 20,
                'delay_seconds': 2.0
            }
        },
        {
            'name': 'Hamptons',
            'branch_name': 'UK Wide',
            'website_url': 'www.hamptons.co.uk',
            'is_active': True,
            'scraper_config': {
                'base_url': 'https://www.hamptons.co.uk',
                'search_url_template': 'https://www.hamptons.co.uk/sales?page={page}',
                'max_pages': 20,
                'delay_seconds': 2.0
            }
        }
    ]

    for agent_data in agents_to_add:
        # Check if already exists
        existing = db.query(Agent).filter(Agent.name == agent_data['name']).first()

        if existing:
            print(f"Agent '{agent_data['name']}' already exists (ID: {existing.agent_id})")
            continue

        # Create new agent
        agent = Agent(**agent_data)
        db.add(agent)
        db.commit()
        db.refresh(agent)

        print(f"Added agent '{agent.name}' (ID: {agent.agent_id})")

    db.close()
    print("\nAgent setup complete!")


if __name__ == "__main__":
    setup_agents()
