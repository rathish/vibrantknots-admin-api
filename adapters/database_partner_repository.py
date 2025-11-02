from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from domain.partner.entities import Partner
from domain.partner.value_objects import PartnerId, PartnerCode
from datetime import datetime
import uuid


class DatabasePartnerRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def save(self, partner: Partner) -> Partner:
        # Check if partner exists
        result = self.db.execute(
            text("SELECT id FROM partners WHERE id = :id"),
            {"id": partner.partner_id.value}
        )
        exists = result.fetchone()
        
        if exists:
            # Update existing
            self.db.execute(
                text("""
                    UPDATE partners 
                    SET name = :name, code = :code, email = :email, 
                        phone = :phone, address = :address, updated_at = NOW()
                    WHERE id = :id
                """),
                {
                    "id": partner.partner_id.value,
                    "name": partner.name,
                    "code": partner.code.value,
                    "email": partner.email,
                    "phone": partner.phone,
                    "address": partner.address
                }
            )
        else:
            # Create new
            partner_id = str(uuid.uuid4()) if not hasattr(partner, 'partner_id') else partner.partner_id.value
            self.db.execute(
                text("""
                    INSERT INTO partners (id, name, code, email, phone, address, is_active, created_at, updated_at)
                    VALUES (:id, :name, :code, :email, :phone, :address, :is_active, NOW(), NOW())
                """),
                {
                    "id": partner_id,
                    "name": partner.name,
                    "code": partner.code.value,
                    "email": partner.email,
                    "phone": partner.phone,
                    "address": partner.address,
                    "is_active": partner.is_active
                }
            )
            partner.partner_id = PartnerId(partner_id)
        
        self.db.commit()
        return partner
    
    def find_by_id(self, partner_id: PartnerId) -> Optional[Partner]:
        result = self.db.execute(
            text("""
                SELECT id, name, code, email, phone, address, is_active, created_at, updated_at
                FROM partners WHERE id = :id
            """),
            {"id": partner_id.value}
        )
        row = result.fetchone()
        if not row:
            return None
        
        return Partner(
            partner_id=PartnerId(str(row.id)),
            name=row.name,
            code=PartnerCode(row.code),
            email=row.email,
            phone=row.phone,
            address=row.address,
            is_active=row.is_active,
            created_at=row.created_at,
            updated_at=row.updated_at
        )
    
    def find_all(self) -> List[Partner]:
        result = self.db.execute(
            text("""
                SELECT id, name, code, email, phone, address, is_active, created_at, updated_at
                FROM partners ORDER BY name
            """)
        )
        
        partners = []
        for row in result:
            partners.append(Partner(
                partner_id=PartnerId(str(row.id)),
                name=row.name,
                code=PartnerCode(row.code),
                email=row.email,
                phone=row.phone,
                address=row.address,
                is_active=row.is_active,
                created_at=row.created_at,
                updated_at=row.updated_at
            ))
        
        return partners
    
    def find_by_code(self, code: str) -> Optional[Partner]:
        result = self.db.execute(
            text("""
                SELECT id, name, code, email, phone, address, is_active, created_at, updated_at
                FROM partners WHERE code = :code
            """),
            {"code": code.upper()}
        )
        row = result.fetchone()
        if not row:
            return None
        
        return Partner(
            partner_id=PartnerId(str(row.id)),
            name=row.name,
            code=PartnerCode(row.code),
            email=row.email,
            phone=row.phone,
            address=row.address,
            is_active=row.is_active,
            created_at=row.created_at,
            updated_at=row.updated_at
        )
