from domain.base.entity import AggregateRoot
from domain.partner.value_objects import PartnerId, PartnerCode
from typing import Optional
from datetime import datetime


class Partner(AggregateRoot):
    def __init__(
        self,
        partner_id: PartnerId,
        name: str,
        code: PartnerCode,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        address: Optional[str] = None,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        super().__init__(partner_id.value)
        self.partner_id = partner_id
        self.name = name
        self.code = code
        self.email = email
        self.phone = phone
        self.address = address
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def update_contact_details(self, email: Optional[str] = None, phone: Optional[str] = None, address: Optional[str] = None):
        if email is not None:
            self.email = email
        if phone is not None:
            self.phone = phone
        if address is not None:
            self.address = address
        self.updated_at = datetime.utcnow()
    
    def activate(self):
        self.is_active = True
        self.updated_at = datetime.utcnow()
    
    def deactivate(self):
        self.is_active = False
        self.updated_at = datetime.utcnow()
