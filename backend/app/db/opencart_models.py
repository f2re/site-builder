"""
OpenCart database models (read-only access)
These models map to the existing OpenCart database tables
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime, Text, Numeric, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class OCBase(DeclarativeBase):
    pass


class OCCategory(OCBase):
    """OpenCart category table"""
    __tablename__ = "oc_category"

    category_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    image: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    parent_id: Mapped[int] = mapped_column(Integer, default=0)
    top: Mapped[bool] = mapped_column(Boolean, default=False)
    column: Mapped[int] = mapped_column(Integer, default=1)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[bool] = mapped_column(Boolean, default=True)
    date_added: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    date_modified: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<OCCategory {self.category_id}>"


class OCCategoryDescription(OCBase):
    """OpenCart category descriptions (multi-language)"""
    __tablename__ = "oc_category_description"

    category_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    language_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    meta_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    meta_description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    meta_keyword: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    def __repr__(self) -> str:
        return f"<OCCategoryDescription cat={self.category_id} lang={self.language_id}>"


class OCCategoryToStore(OCBase):
    """OpenCart category to store mapping"""
    __tablename__ = "oc_category_to_store"

    category_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    store_id: Mapped[int] = mapped_column(Integer, primary_key=True)

    def __repr__(self) -> str:
        return f"<OCCategoryToStore cat={self.category_id} store={self.store_id}>"


class OCProduct(OCBase):
    """OpenCart product table"""
    __tablename__ = "oc_product"

    product_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    model: Mapped[str] = mapped_column(String(64), nullable=False)
    sku: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    upc: Mapped[Optional[str]] = mapped_column(String(12), nullable=True)
    ean: Mapped[Optional[str]] = mapped_column(String(14), nullable=True)
    jan: Mapped[Optional[str]] = mapped_column(String(13), nullable=True)
    isbn: Mapped[Optional[str]] = mapped_column(String(17), nullable=True)
    mpn: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    stock_status_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    image: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    manufacturer_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    shipping: Mapped[bool] = mapped_column(Boolean, default=True)
    price: Mapped[float] = mapped_column(Numeric(15, 4), nullable=False)
    points: Mapped[int] = mapped_column(Integer, default=0)
    tax_class_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    date_available: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    weight: Mapped[float] = mapped_column(Numeric(15, 8), default=0)
    weight_class_id: Mapped[int] = mapped_column(Integer, default=0)
    length: Mapped[float] = mapped_column(Numeric(15, 8), default=0)
    width: Mapped[float] = mapped_column(Numeric(15, 8), default=0)
    height: Mapped[float] = mapped_column(Numeric(15, 8), default=0)
    length_class_id: Mapped[int] = mapped_column(Integer, default=0)
    subtract: Mapped[bool] = mapped_column(Boolean, default=True)
    minimum: Mapped[int] = mapped_column(Integer, default=1)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[bool] = mapped_column(Boolean, default=False)
    viewed: Mapped[int] = mapped_column(Integer, default=0)
    date_added: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    date_modified: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<OCProduct {self.product_id} ({self.model})>"


class OCProductDescription(OCBase):
    """OpenCart product descriptions (multi-language)"""
    __tablename__ = "oc_product_description"

    product_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    language_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tag: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    meta_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    meta_description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    meta_keyword: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    def __repr__(self) -> str:
        return f"<OCProductDescription prod={self.product_id} lang={self.language_id}>"


class OCProductToCategory(OCBase):
    """OpenCart product to category mapping"""
    __tablename__ = "oc_product_to_category"

    product_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category_id: Mapped[int] = mapped_column(Integer, primary_key=True)

    def __repr__(self) -> str:
        return f"<OCProductToCategory prod={self.product_id} cat={self.category_id}>"


class OCProductToStore(OCBase):
    """OpenCart product to store mapping"""
    __tablename__ = "oc_product_to_store"

    product_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    store_id: Mapped[int] = mapped_column(Integer, primary_key=True)

    def __repr__(self) -> str:
        return f"<OCProductToStore prod={self.product_id} store={self.store_id}>"


class OCCustomer(OCBase):
    """OpenCart customer table"""
    __tablename__ = "oc_customer"

    customer_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_group_id: Mapped[int] = mapped_column(Integer, nullable=False)
    store_id: Mapped[int] = mapped_column(Integer, default=0)
    language_id: Mapped[int] = mapped_column(Integer, nullable=False)
    firstname: Mapped[str] = mapped_column(String(32), nullable=False)
    lastname: Mapped[str] = mapped_column(String(32), nullable=False)
    email: Mapped[str] = mapped_column(String(96), nullable=False)
    telephone: Mapped[str] = mapped_column(String(32), nullable=False)
    fax: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    salt: Mapped[Optional[str]] = mapped_column(String(9), nullable=True)
    cart: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    wishlist: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    newsletter: Mapped[bool] = mapped_column(Boolean, default=False)
    address_id: Mapped[int] = mapped_column(Integer, default=0)
    custom_field: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ip: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    status: Mapped[bool] = mapped_column(Boolean, default=True)
    safe: Mapped[bool] = mapped_column(Boolean, default=False)
    token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    code: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    date_added: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    def __repr__(self) -> str:
        return f"<OCCustomer {self.customer_id} ({self.email})>"


class OCOrder(OCBase):
    """OpenCart order table"""
    __tablename__ = "oc_order"

    order_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    invoice_no: Mapped[int] = mapped_column(Integer, default=0)
    invoice_prefix: Mapped[Optional[str]] = mapped_column(String(26), nullable=True)
    store_id: Mapped[int] = mapped_column(Integer, default=0)
    store_name: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    store_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    customer_id: Mapped[int] = mapped_column(Integer, default=0)
    customer_group_id: Mapped[int] = mapped_column(Integer, default=0)
    firstname: Mapped[str] = mapped_column(String(32), nullable=False)
    lastname: Mapped[str] = mapped_column(String(32), nullable=False)
    email: Mapped[str] = mapped_column(String(96), nullable=False)
    telephone: Mapped[str] = mapped_column(String(32), nullable=False)
    fax: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    custom_field: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    payment_firstname: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    payment_lastname: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    payment_company: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)
    payment_address_1: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    payment_address_2: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    payment_city: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    payment_postcode: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    payment_country: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    payment_country_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    payment_zone: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    payment_zone_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    payment_address_format: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    payment_custom_field: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    payment_method: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    payment_code: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    shipping_firstname: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    shipping_lastname: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    shipping_company: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    shipping_address_1: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    shipping_address_2: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    shipping_city: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    shipping_postcode: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    shipping_country: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    shipping_country_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    shipping_zone: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    shipping_zone_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    shipping_address_format: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    shipping_custom_field: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    shipping_method: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    shipping_code: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    total: Mapped[float] = mapped_column(Numeric(15, 4), default=0)
    order_status_id: Mapped[int] = mapped_column(Integer, default=0)
    affiliate_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    commission: Mapped[Optional[float]] = mapped_column(Numeric(15, 4), nullable=True)
    marketing_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    tracking: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    language_id: Mapped[int] = mapped_column(Integer, nullable=False)
    currency_id: Mapped[int] = mapped_column(Integer, nullable=False)
    currency_code: Mapped[str] = mapped_column(String(3), nullable=False)
    currency_value: Mapped[float] = mapped_column(Numeric(15, 8), default=1)
    ip: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    forwarded_ip: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    accept_language: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    date_added: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    date_modified: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    def __repr__(self) -> str:
        return f"<OCOrder {self.order_id}>"


class OCOrderProduct(OCBase):
    """OpenCart order products"""
    __tablename__ = "oc_order_product"

    order_product_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(Integer, nullable=False)
    product_id: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    model: Mapped[str] = mapped_column(String(64), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[float] = mapped_column(Numeric(15, 4), default=0)
    total: Mapped[float] = mapped_column(Numeric(15, 4), default=0)
    tax: Mapped[float] = mapped_column(Numeric(15, 4), default=0)
    reward: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    def __repr__(self) -> str:
        return f"<OCOrderProduct order={self.order_id} product={self.product_id}>"
