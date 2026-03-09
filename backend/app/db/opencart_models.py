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


class OCProductImage(OCBase):
    """OpenCart additional product images"""
    __tablename__ = "oc_product_image"

    product_image_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(Integer)
    image: Mapped[str] = mapped_column(String(255))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    def __repr__(self) -> str:
        return f"<OCProductImage prod={self.product_id} img={self.product_image_id}>"


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


class OCInformation(OCBase):
    """OpenCart information/static pages table"""
    __tablename__ = "oc_information"

    information_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[bool] = mapped_column(Boolean, default=True)
    date_added: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    date_modified: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<OCInformation {self.information_id}>"


class OCInformationDescription(OCBase):
    """OpenCart information descriptions (multi-language)"""
    __tablename__ = "oc_information_description"

    information_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    language_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    meta_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    meta_description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    meta_keyword: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    def __repr__(self) -> str:
        return f"<OCInformationDescription info={self.information_id} lang={self.language_id}>"


class OCAddress(OCBase):
    """OpenCart customer address table"""
    __tablename__ = "oc_address"

    address_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_id: Mapped[int] = mapped_column(Integer, nullable=False)
    firstname: Mapped[str] = mapped_column(String(32), nullable=False)
    lastname: Mapped[str] = mapped_column(String(32), nullable=False)
    company: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)
    address_1: Mapped[str] = mapped_column(String(128), nullable=False)
    address_2: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    city: Mapped[str] = mapped_column(String(128), nullable=False)
    postcode: Mapped[str] = mapped_column(String(10), nullable=False)
    country_id: Mapped[int] = mapped_column(Integer, nullable=False)
    zone_id: Mapped[int] = mapped_column(Integer, nullable=False)
    custom_field: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<OCAddress {self.address_id} customer={self.customer_id}>"


class OCOption(OCBase):
    """OpenCart option table"""
    __tablename__ = "oc_option"

    option_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[str] = mapped_column(String(32), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    def __repr__(self) -> str:
        return f"<OCOption {self.option_id}>"


class OCOptionDescription(OCBase):
    """OpenCart option description table"""
    __tablename__ = "oc_option_description"

    option_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    language_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)

    def __repr__(self) -> str:
        return f"<OCOptionDescription {self.option_id} lang={self.language_id}>"


class OCOptionValue(OCBase):
    """OpenCart option value table"""
    __tablename__ = "oc_option_value"

    option_value_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    option_id: Mapped[int] = mapped_column(Integer, nullable=False)
    image: Mapped[str] = mapped_column(String(255), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    def __repr__(self) -> str:
        return f"<OCOptionValue {self.option_value_id} option={self.option_id}>"


class OCOptionValueDescription(OCBase):
    """OpenCart option value description table"""
    __tablename__ = "oc_option_value_description"

    option_value_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    language_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    option_id: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)

    def __repr__(self) -> str:
        return f"<OCOptionValueDescription {self.option_value_id} lang={self.language_id}>"


class OCProductOption(OCBase):
    """OpenCart product option table"""
    __tablename__ = "oc_product_option"

    product_option_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(Integer, nullable=False)
    option_id: Mapped[int] = mapped_column(Integer, nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=True)
    required: Mapped[bool] = mapped_column(Boolean, default=False)

    def __repr__(self) -> str:
        return f"<OCProductOption {self.product_option_id} prod={self.product_id} opt={self.option_id}>"


class OCProductOptionValue(OCBase):
    """OpenCart product option value table"""
    __tablename__ = "oc_product_option_value"

    product_option_value_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_option_id: Mapped[int] = mapped_column(Integer, nullable=False)
    product_id: Mapped[int] = mapped_column(Integer, nullable=False)
    option_id: Mapped[int] = mapped_column(Integer, nullable=False)
    option_value_id: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    subtract: Mapped[bool] = mapped_column(Boolean, default=True)
    price: Mapped[float] = mapped_column(Numeric(15, 4), default=0)
    price_prefix: Mapped[str] = mapped_column(String(1), nullable=False)
    points: Mapped[int] = mapped_column(Integer, default=0)
    points_prefix: Mapped[str] = mapped_column(String(1), nullable=False)
    weight: Mapped[float] = mapped_column(Numeric(15, 8), default=0)
    weight_prefix: Mapped[str] = mapped_column(String(1), nullable=False)

    def __repr__(self) -> str:
        return f"<OCProductOptionValue {self.product_option_value_id} prod={self.product_id}>"


class OCDevice(OCBase):
    """OpenCart devices table"""
    __tablename__ = "oc_devices"

    device_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_id: Mapped[int] = mapped_column(Integer)
    device_type: Mapped[str] = mapped_column(String(40))
    device_name: Mapped[str] = mapped_column(String(40))
    device_serial: Mapped[str] = mapped_column(String(40))
    register_date: Mapped[datetime] = mapped_column(DateTime)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<OCDevice {self.device_id} customer={self.customer_id}>"


class OCToken(OCBase):
    """OpenCart tokens table"""
    __tablename__ = "oc_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token: Mapped[str] = mapped_column(String(255))
    customer_id: Mapped[int] = mapped_column(Integer)

    def __repr__(self) -> str:
        return f"<OCToken {self.id} customer={self.customer_id}>"


class OCTokenToDevice(OCBase):
    """OpenCart token to device mapping table"""
    __tablename__ = "oc_token_to_device"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token_id: Mapped[int] = mapped_column(Integer)
    serial: Mapped[str] = mapped_column(String(255))
    device_type: Mapped[str] = mapped_column(String(20))
    date_added: Mapped[datetime] = mapped_column(DateTime)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<OCTokenToDevice {self.id} token={self.token_id} serial={self.serial}>"
