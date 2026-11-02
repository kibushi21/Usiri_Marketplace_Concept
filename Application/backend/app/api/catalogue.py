from __future__ import annotations

from fastapi import APIRouter, Form, HTTPException, Query, UploadFile, status
from sqlalchemy import or_, select
from sqlalchemy.orm import joinedload, selectinload

from ..deps import Db
from ..errors import NotFound
from ..models import (
    Category,
    Department,
    Product,
    ProductStatus,
    Supplier,
    SupplierStatus,
)
from ..services import visual_search
from .serializers import department_out, product_detail, product_summary

router = APIRouter(prefix="/catalogue", tags=["catalogue"])

IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_IMAGE_BYTES = 5 * 1024 * 1024


def _product_query():
    return (
        select(Product)
        .where(Product.status == ProductStatus.ACTIVE)
        .options(
            selectinload(Product.variants),
            joinedload(Product.supplier),
        )
    )


@router.get("/departments")
def list_departments(db: Db):
    departments = db.scalars(
        select(Department).where(Department.active.is_(True)).order_by(Department.sort_order)
    ).all()
    categories = db.scalars(select(Category).where(Category.active.is_(True))).all()
    grouped: dict[str, list[Category]] = {}
    for category in categories:
        grouped.setdefault(category.department_id, []).append(category)
    counts = {}
    for department_id, in db.execute(
        select(Product.department_id).where(Product.status == ProductStatus.ACTIVE)
    ):
        counts[department_id] = counts.get(department_id, 0) + 1
    result = []
    for department in departments:
        data = department_out(department, grouped.get(department.id, []))
        data["product_count"] = counts.get(department.id, 0)
        result.append(data)
    return result


@router.get("/products")
def list_products(
    db: Db,
    department: str | None = None,
    category: str | None = None,
    q: str | None = None,
    supplier: str | None = None,
    sort: str = Query(default="featured", pattern="^(featured|price_asc|price_desc|name)$"),
    limit: int = Query(default=48, ge=1, le=96),
    offset: int = Query(default=0, ge=0),
):
    query = _product_query().join(Supplier, Supplier.id == Product.supplier_id).where(
        Supplier.status == SupplierStatus.VERIFIED
    )
    if department:
        query = query.join(Department, Department.id == Product.department_id).where(
            Department.slug == department
        )
    if category:
        query = query.join(Category, Category.id == Product.category_id).where(
            Category.slug == category
        )
    if supplier:
        query = query.where(Supplier.id == supplier)
    if q:
        needle = f"%{q.strip()}%"
        query = query.where(
            or_(Product.name.ilike(needle), Product.brand.ilike(needle), Product.description.ilike(needle))
        )

    products = list(db.scalars(query).unique().all())
    departments = {row.id: row for row in db.scalars(select(Department)).all()}
    for product in products:
        department = departments.get(product.department_id)
        product.department_slug = department.slug if department else None
        product.department_name = department.name if department else None

    if sort == "price_asc":
        products.sort(key=lambda p: min((v.price_tzs for v in p.variants), default=0))
    elif sort == "price_desc":
        products.sort(key=lambda p: max((v.price_tzs for v in p.variants), default=0), reverse=True)
    elif sort == "name":
        products.sort(key=lambda p: p.name)
    else:
        products.sort(key=lambda p: p.created_at, reverse=True)

    total = len(products)
    page = products[offset : offset + limit]
    return {"total": total, "limit": limit, "offset": offset, "items": [product_summary(p) for p in page]}


@router.post("/image-search")
async def image_search(
    db: Db,
    file: UploadFile,
    hint: str | None = Form(default=None),
    limit: int = Query(default=24, ge=1, le=48),
):
    if file.content_type not in IMAGE_TYPES:
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            "Upload a JPEG, PNG, WebP or GIF image",
        )
    data = await file.read(MAX_IMAGE_BYTES + 1)
    if not data:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "The uploaded image is empty")
    if len(data) > MAX_IMAGE_BYTES:
        raise HTTPException(status.HTTP_413_CONTENT_TOO_LARGE, "Images must be 5 MB or smaller")

    products, vision = visual_search.search(
        db,
        filename=file.filename or "",
        data=data,
        hint=hint,
        limit=limit,
    )
    return {
        "provider": vision.provider,
        "tags": vision.tags,
        "note": vision.note,
        "total": len(products),
        "items": [product_summary(product) for product in products],
    }


@router.get("/products/{slug}")
def get_product(slug: str, db: Db):
    product = db.scalar(
        _product_query()
        .where(Product.slug == slug)
        .options(joinedload(Product.images))
    )
    if product is None:
        raise NotFound("Product not found")
    department = db.get(Department, product.department_id)
    product.department_slug = department.slug if department else None
    product.department_name = department.name if department else None
    return product_detail(product)


@router.get("/suppliers/{supplier_id}")
def public_supplier(supplier_id: str, db: Db):
    supplier = db.get(Supplier, supplier_id)
    if supplier is None or supplier.status != SupplierStatus.VERIFIED:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Supplier not found")
    products = db.scalars(
        _product_query().where(Product.supplier_id == supplier_id).limit(48)
    ).unique().all()
    return {
        "id": supplier.id,
        "name": supplier.trading_name,
        "region": supplier.region,
        "city": supplier.city,
        "rating": supplier.rating_x10 / 10,
        "products": [product_summary(p) for p in products],
    }
