"""
Script to fix invalid contract type enum values in the database
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, engine
from app.models.contract import Contract, ContractType
from sqlalchemy import text

def fix_contract_types():
    """Fix invalid contract type enum values"""
    db = SessionLocal()
    
    try:
        # Type mapping for invalid values
        # Note: The enum values are lowercase strings, but SQLAlchemy stores them as-is
        type_mapping = {
            'parties': 'other',
            'party': 'other',
            'service': 'other',
            'agreement': 'other',
        }
        
        # First, fix uppercase 'OTHER' to lowercase 'other'
        result = db.execute(
            text("""
                UPDATE contracts 
                SET type = 'other' 
                WHERE type = 'OTHER'
            """)
        )
        print(f"Updated {result.rowcount} contracts from 'OTHER' to 'other'")
        
        # Fix title case 'Other' to lowercase 'other'
        result = db.execute(
            text("""
                UPDATE contracts 
                SET type = 'other' 
                WHERE type = 'Other'
            """)
        )
        print(f"Updated {result.rowcount} contracts from 'Other' to 'other'")
        
        # Get all contracts with invalid types
        # We'll use raw SQL to update since SQLAlchemy enum validation prevents invalid values
        for invalid_type, valid_type in type_mapping.items():
            result = db.execute(
                text("""
                    UPDATE contracts 
                    SET type = :valid_type 
                    WHERE LOWER(type) = :invalid_type
                """),
                {"valid_type": valid_type, "invalid_type": invalid_type}
            )
            print(f"Updated {result.rowcount} contracts from '{invalid_type}' to '{valid_type}'")
        
        # Also fix any other invalid values to 'other'
        # SQLite doesn't support tuple parameters in NOT IN, so we'll check each type
        valid_types = ['supplier', 'customer', 'partnership', 'employment', 'nda', 'other']
        valid_types_str = "', '".join(valid_types)
        result = db.execute(
            text(f"""
                UPDATE contracts 
                SET type = 'other' 
                WHERE LOWER(type) NOT IN ('{valid_types_str}')
            """)
        )
        print(f"Updated {result.rowcount} contracts with other invalid types to 'other'")
        
        # Fix status values - convert enum names to lowercase values
        status_mapping = {
            'DRAFT': 'draft',
            'ACTIVE': 'active',
            'EXPIRED': 'expired',
            'TERMINATED': 'terminated',
            'PENDING_RENEWAL': 'pending_renewal',
        }
        for old_status, new_status in status_mapping.items():
            result = db.execute(
                text(f"""
                    UPDATE contracts 
                    SET status = :new_status 
                    WHERE status = :old_status
                """),
                {"new_status": new_status, "old_status": old_status}
            )
            if result.rowcount > 0:
                print(f"Updated {result.rowcount} contracts from status '{old_status}' to '{new_status}'")
        
        db.commit()
        print("Contract types and statuses fixed successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"Error fixing contract types: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    fix_contract_types()

