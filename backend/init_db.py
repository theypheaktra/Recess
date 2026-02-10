"""
Database initialization script
Creates tables and seeds initial data
"""
import sys
import os
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine, SessionLocal, Base
from app.core.security import get_password_hash
from app.models import (
    User, UserStatus,
    Organization, OrgType,
    Vendor, VendorType, TaxType
)


def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created successfully")


def seed_data():
    """Seed initial data"""
    db = SessionLocal()
    
    try:
        print("\nSeeding initial data...")
        
        # 1. Create Organizations
        print("Creating organizations...")
        
        # Tier 0: Production Committee
        committee = Organization(
            name="Tokyo Broadcasting Committee",
            name_jp="東京放送制作委員会",
            type=OrgType.committee,
            tier=0,
            phone="03-1234-5678",
            email="contact@tbc-committee.jp"
        )
        db.add(committee)
        
        # Tier 1: Prime Contractor
        prime_studio = Organization(
            name="RECESS Animation Studio",
            name_jp="リセス・アニメーションスタジオ",
            type=OrgType.prime,
            tier=1,
            business_no="123-45-67890",
            bank_name="Tokyo Mitsubishi Bank",
            bank_account="1234567890",
            phone="03-9876-5432",
            email="info@recess-studio.jp"
        )
        db.add(prime_studio)
        
        # Tier 2: Subcontractor Studio
        sub_studio = Organization(
            name="Seoul Animation Works",
            name_jp="ソウルアニメーション",
            type=OrgType.sub,
            tier=2,
            business_no="987-65-43210",
            bank_name="Shinhan Bank",
            bank_account="9876543210",
            phone="02-1111-2222",
            email="contact@seoul-anim.kr"
        )
        db.add(sub_studio)
        
        db.commit()
        print("✓ Organizations created")
        
        # 2. Create Users
        print("Creating users...")
        
        # Tier 0: Committee Chairman
        chairman = User(
            email="chairman@tbc-committee.jp",
            password_hash=get_password_hash("password123"),
            name="Tanaka Ichiro",
            name_jp="田中一郎",
            role_level=0,
            tier=0,
            org_id=committee.id,
            status=UserStatus.active
        )
        db.add(chairman)
        
        # Tier 1: Prime PD
        pd = User(
            email="pd@recess-studio.jp",
            password_hash=get_password_hash("password123"),
            name="Yamamoto Kenji",
            name_jp="山本健二",
            role_level=3,
            tier=1,
            org_id=prime_studio.id,
            status=UserStatus.active,
            is_superuser=True
        )
        db.add(pd)
        
        # Tier 1: Desk
        desk = User(
            email="desk@recess-studio.jp",
            password_hash=get_password_hash("password123"),
            name="Suzuki Yuki",
            name_jp="鈴木由紀",
            role_level=4,
            tier=1,
            org_id=prime_studio.id,
            status=UserStatus.active
        )
        db.add(desk)
        
        # Tier 2: Subcontractor PM
        sub_pm = User(
            email="pm@seoul-anim.kr",
            password_hash=get_password_hash("password123"),
            name="Kim Minho",
            name_jp="キム・ミンホ",
            role_level=5,
            tier=2,
            org_id=sub_studio.id,
            status=UserStatus.active
        )
        db.add(sub_pm)
        
        # Tier 2: Team Lead
        team_lead = User(
            email="lead@seoul-anim.kr",
            password_hash=get_password_hash("password123"),
            name="Lee Jihyun",
            name_jp="イ・ジヒョン",
            role_level=6,
            tier=2,
            org_id=sub_studio.id,
            status=UserStatus.active
        )
        db.add(team_lead)
        
        # Tier 2: Worker (Freelancer)
        worker = User(
            email="worker@example.com",
            password_hash=get_password_hash("password123"),
            name="Park Sora",
            name_jp="パク・ソラ",
            role_level=7,
            tier=2,
            org_id=sub_studio.id,
            status=UserStatus.active
        )
        db.add(worker)
        
        db.commit()
        print("✓ Users created")
        
        # 3. Create Vendors
        print("Creating vendors...")
        
        # Studio vendor
        vendor_studio = Vendor(
            name="Seoul Animation Works",
            name_jp="ソウルアニメーション",
            type=VendorType.studio,
            tier=2,
            org_id=sub_studio.id,
            tax_type=TaxType.corporate,
            bank_name="Shinhan Bank",
            bank_account="9876543210",
            account_holder="Seoul Animation Works Co., Ltd.",
            default_rate=Decimal("12000.00"),
            is_active=True
        )
        db.add(vendor_studio)
        
        # Freelancer vendor
        vendor_freelancer = Vendor(
            name="Park Sora (Freelancer)",
            name_jp="パク・ソラ（フリーランサー）",
            type=VendorType.freelancer,
            tier=2,
            tax_type=TaxType.individual,
            email="worker@example.com",
            phone="010-1234-5678",
            bank_name="Kookmin Bank",
            bank_account="1111222233334444",
            account_holder="Park Sora",
            default_rate=Decimal("15000.00"),
            is_active=True
        )
        db.add(vendor_freelancer)
        
        db.commit()
        print("✓ Vendors created")
        
        print("\n" + "="*50)
        print("✓ Database initialization completed successfully!")
        print("="*50)
        
        print("\nTest Accounts:")
        print("-" * 50)
        print(f"1. Committee Chairman (Tier 0, L0)")
        print(f"   Email: chairman@tbc-committee.jp")
        print(f"   Password: password123")
        print()
        print(f"2. Producer/PD (Tier 1, L3) [SUPERUSER]")
        print(f"   Email: pd@recess-studio.jp")
        print(f"   Password: password123")
        print()
        print(f"3. Desk (Tier 1, L4)")
        print(f"   Email: desk@recess-studio.jp")
        print(f"   Password: password123")
        print()
        print(f"4. Subcontractor PM (Tier 2, L5)")
        print(f"   Email: pm@seoul-anim.kr")
        print(f"   Password: password123")
        print()
        print(f"5. Team Lead (Tier 2, L6)")
        print(f"   Email: lead@seoul-anim.kr")
        print(f"   Password: password123")
        print()
        print(f"6. Worker (Tier 2, L7)")
        print(f"   Email: worker@example.com")
        print(f"   Password: password123")
        print("-" * 50)
        
    except Exception as e:
        print(f"\n✗ Error seeding data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("="*50)
    print("RECESS IMS Database Initialization")
    print("="*50)
    
    create_tables()
    seed_data()
    
    print("\nNext steps:")
    print("1. Start the API server: cd backend && python -m uvicorn app.main:app --reload")
    print("2. Access API docs: http://localhost:8000/docs")
    print("3. Login with test accounts above")
