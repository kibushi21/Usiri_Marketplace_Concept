from __future__ import annotations

import json
import random
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import (
    Address,
    Category,
    Department,
    PlatformConfig,
    Product,
    ProductVariant,
    Role,
    Supplier,
    SupplierDocument,
    User,
)
from .security import hash_password
from .services import ledger
from .services.platform_config import DEFAULTS

DEMO_PASSWORD = "Usiri#2026"

DEPARTMENTS = [
    (
        "homeware-storage",
        "Homeware & Storage",
        "Nyumbani na Hifadhi",
        "Everyday home organisation, storage and tableware.",
        ["storage", "tableware", "textiles"],
    ),
    (
        "small-appliances",
        "Small Kitchen & Home Appliances",
        "Vifaa Vidogo vya Jikoni",
        "Bench-top appliances for cooking, blending and food preparation.",
        ["cooking", "preparation", "cooling"],
    ),
    (
        "fashion-footwear",
        "Fashion & Footwear",
        "Mavazi na Viatu",
        "Locally made and imported clothing, sandals, shoes and accessories.",
        ["womenswear", "menswear", "footwear"],
    ),
    (
        "beauty-personal-care",
        "Beauty & Personal Care",
        "Urembo na Utunzaji",
        "Skincare, haircare and grooming essentials.",
        ["skincare", "haircare", "grooming"],
    ),
    (
        "baby-maternity",
        "Baby & Maternity",
        "Watoto na Uzazi",
        "Baby care, feeding and maternity essentials.",
        ["baby-care", "feeding", "maternity"],
    ),
    (
        "bundles",
        "Home & Kitchen Bundles",
        "Seti za Nyumbani na Jikoni",
        "Curated starter sets for new homes and gifting.",
        ["starter-kits", "gift-sets"],
    ),
]

SUPPLIERS = [
    {
        "code": "SUP-0001",
        "legal_name": "Kariakoo Homeware Company Limited",
        "trading_name": "Kariakoo Homeware",
        "tin": "102-456-789",
        "brela_number": "BR-2019-45678",
        "region": "Dar es Salaam",
        "city": "Dar es Salaam",
        "contact_name": "Halima Said",
        "contact_email": "halima@kariahoo.co.tz",
        "contact_phone": "+255 712 456 789",
        "status": "verified",
        "payout_provider": "M-Pesa (Vodacom)",
        "rating_x10": 47,
    },
    {
        "code": "SUP-0002",
        "legal_name": "Mwanga Appliances Limited",
        "trading_name": "Mwanga Appliances",
        "tin": "110-221-334",
        "brela_number": "BR-2020-11223",
        "region": "Dar es Salaam",
        "city": "Dar es Salaam",
        "contact_name": "Peter Mwanga",
        "contact_email": "peter@mwanga.co.tz",
        "contact_phone": "+255 754 221 334",
        "status": "verified",
        "payout_provider": "Tigo Pesa",
        "rating_x10": 45,
    },
    {
        "code": "SUP-0003",
        "legal_name": "Sanaa Fashion House Limited",
        "trading_name": "Sanaa Fashion House",
        "tin": "118-556-901",
        "brela_number": "BR-2018-55690",
        "region": "Dar es Salaam",
        "city": "Dar es Salaam",
        "contact_name": "Grace Mwaikambo",
        "contact_email": "grace@sanaafashion.co.tz",
        "contact_phone": "+255 786 556 901",
        "status": "verified",
        "payout_provider": "Airtel Money",
        "rating_x10": 46,
    },
    {
        "code": "SUP-0004",
        "legal_name": "Zanzibar Beauty Supplies Limited",
        "trading_name": "Zanzibar Beauty Supplies",
        "tin": "121-334-778",
        "brela_number": "BR-2021-33477",
        "region": "Zanzibar Urban/West",
        "city": "Zanzibar City",
        "contact_name": "Fatma Ali",
        "contact_email": "fatma@znzbeauty.co.tz",
        "contact_phone": "+255 777 334 778",
        "status": "verified",
        "payout_provider": "M-Pesa (Vodacom)",
        "rating_x10": 44,
    },
    {
        "code": "SUP-0005",
        "legal_name": "Tumaini Baby Store Limited",
        "trading_name": "Tumaini Baby Store",
        "tin": "130-990-112",
        "brela_number": "BR-2019-99011",
        "region": "Arusha",
        "city": "Arusha",
        "contact_name": "Esther Mollel",
        "contact_email": "esther@tumaini.co.tz",
        "contact_phone": "+255 713 990 112",
        "status": "verified",
        "payout_provider": "CRDB Bank",
        "rating_x10": 48,
    },
    {
        "code": "SUP-0006",
        "legal_name": "Dodoma Kitchen Bundle Works",
        "trading_name": "Dodoma Kitchen Works",
        "tin": "133-447-889",
        "brela_number": "BR-2022-44788",
        "region": "Dodoma",
        "city": "Dodoma",
        "contact_name": "Martha Chusi",
        "contact_email": "martha@dodomakitchen.co.tz",
        "contact_phone": "+255 768 447 889",
        "status": "verified",
        "payout_provider": "M-Pesa (Vodacom)",
        "rating_x10": 43,
    },
    {
        "code": "SUP-0007",
        "legal_name": "Lake Zone Essentials Limited",
        "trading_name": "Lake Zone Essentials",
        "tin": "141-228-663",
        "brela_number": "BR-2021-22866",
        "region": "Mwanza",
        "city": "Mwanza",
        "contact_name": "John Nyambari",
        "contact_email": "john@lakezone.co.tz",
        "contact_phone": "+255 755 228 663",
        "status": "verified",
        "payout_provider": "NMB Bank",
        "rating_x10": 42,
    },
    {
        "code": "SUP-0008",
        "legal_name": "Arusha Craft and Home Limited",
        "trading_name": "Arusha Craft & Home",
        "tin": "149-771-220",
        "brela_number": "BR-2023-77122",
        "region": "Arusha",
        "city": "Arusha",
        "contact_name": "Naserian Lema",
        "contact_email": "naserian@arushacraft.co.tz",
        "contact_phone": "+255 787 771 220",
        "status": "pending_verification",
        "payout_provider": "M-Pesa (Vodacom)",
        "rating_x10": 0,
    },
    {
        "code": "SUP-0009",
        "legal_name": "Mwanza Textile Mills Limited",
        "trading_name": "Mwanza Textiles",
        "tin": "152-889-443",
        "brela_number": "BR-2017-88944",
        "region": "Mwanza",
        "city": "Mwanza",
        "contact_name": "Rehema Kileo",
        "contact_email": "rehema@mzatextiles.co.tz",
        "contact_phone": "+255 715 889 443",
        "status": "verified",
        "payout_provider": "Tigo Pesa",
        "rating_x10": 41,
    },
]

# (department slug, category slug, supplier index, name, brand, description, [(variant, price, stock, weight_g)])
PRODUCTS = [
    ("homeware-storage", "storage", 0, "Three-Tier Bamboo Shoe Rack", "Kariakoo Living", "Foldable bamboo rack that holds up to twelve pairs without tools.", [("Natural", 68000, 24, 3200), ("Dark stain", 72000, 12, 3200)]),
    ("homeware-storage", "storage", 0, "Stackable Cotton Storage Basket", "Kariakoo Living", "Soft-sided basket with reinforced handles for shelves and wardrobes.", [("Small", 24000, 40, 600), ("Large", 38000, 30, 900), ("Set of 3", 86000, 15, 2400)]),
    ("homeware-storage", "storage", 8, "Kanga Print Underbed Storage Bag", "Mwanza Textiles", "Dust-proof bag in kanga-inspired print with a full-length zip.", [("Blue", 32000, 26, 800), ("Terracotta", 32000, 18, 800)]),
    ("homeware-storage", "tableware", 6, "Stoneware Dinner Plate Set of 6", "Lake Zone Table", "Chip-resistant stoneware plates, dishwasher safe and stackable.", [("White", 96000, 14, 4200), ("Sage", 104000, 8, 4200)]),
    ("homeware-storage", "tableware", 0, "Glass Water Jug 1.5L", "Kariakoo Living", "Heat-resistant borosilicate jug with a drip-free spout.", [("Clear", 28000, 35, 900)]),
    ("homeware-storage", "textiles", 8, "Cotton Bath Towel Pair", "Mwanza Textiles", "Two 500gsm cotton towels that stay soft after repeated washing.", [("White", 46000, 22, 1200), ("Navy", 46000, 20, 1200), ("Sand", 46000, 16, 1200)]),
    ("homeware-storage", "textiles", 8, "Kitenge Table Runner", "Mwanza Textiles", "Hand-finished table runner in a bold kitenge print.", [("2 seater", 26000, 30, 400), ("6 seater", 42000, 20, 700)]),
    ("small-appliances", "preparation", 1, "700W Blender with Grinder Jar", "Mwanga", "Two-jar blender for smoothies, spices and sauces, with overload protection.", [("1.5L", 148000, 16, 3800)]),
    ("small-appliances", "preparation", 1, "Electric Kettle 1.8L", "Mwanga", "Stainless steel kettle with auto shut-off and boil-dry protection.", [("Silver", 62000, 28, 1400), ("Black", 64000, 20, 1400)]),
    ("small-appliances", "cooking", 1, "Two-Burner Gas Cooker", "Mwanga", "Table-top gas cooker with cast-iron supports and a hose kit.", [("Standard", 235000, 9, 7200)]),
    ("small-appliances", "cooking", 1, "Non-Stick Frying Pan 28cm", "Mwanga", "Forged aluminium pan with a stay-cool handle, gas and electric safe.", [("28cm", 54000, 25, 1100), ("32cm", 68000, 17, 1500)]),
    ("small-appliances", "preparation", 6, "Manual Food Processor", "Lake Zone Kitchen", "Pull-cord chopper for onions, garlic and herbs; no electricity needed.", [("500ml", 42000, 32, 700)]),
    ("small-appliances", "cooling", 1, "Rechargeable Table Fan", "Mwanga", "Three-speed fan with a built-in battery for power cuts.", [("White", 118000, 12, 2600)]),
    ("fashion-footwear", "womenswear", 2, "Cotton Wrap Dress", "Sanaa", "Breathable wrap dress cut for everyday wear and office days.", [("S", 88000, 12, 500), ("M", 88000, 18, 520), ("L", 88000, 14, 540), ("XL", 92000, 8, 560)]),
    ("fashion-footwear", "menswear", 2, "Linen Blend Shirt", "Sanaa", "Lightweight short-sleeve shirt with a relaxed collar.", [("M", 76000, 16, 420), ("L", 76000, 20, 440), ("XL", 80000, 10, 460)]),
    ("fashion-footwear", "footwear", 2, "Leather Sandals", "Sanaa", "Hand-stitched leather sandals from a Tanzanian workshop.", [("38", 96000, 8, 800), ("39", 96000, 10, 810), ("40", 96000, 12, 820), ("41", 98000, 9, 830), ("42", 98000, 7, 840)]),
    ("fashion-footwear", "footwear", 6, "Canvas Slip-On Shoes", "Lake Zone Wear", "Everyday canvas shoes with a cushioned insole.", [("40", 58000, 14, 900), ("41", 58000, 16, 910), ("42", 58000, 12, 920), ("43", 58000, 10, 930)]),
    ("fashion-footwear", "womenswear", 2, "Kitenge Tote Bag", "Sanaa", "Structured tote in kitenge fabric with a cotton lining.", [("Standard", 46000, 24, 500)]),
    ("beauty-personal-care", "skincare", 3, "Baobab Body Butter 250ml", "Zanzibar Botanicals", "Rich body butter with baobab oil and shea for dry skin.", [("250ml", 34000, 40, 300), ("500ml", 56000, 22, 560)]),
    ("beauty-personal-care", "skincare", 3, "Black Soap Face Cleanser", "Zanzibar Botanicals", "Gentle charcoal cleanser for oily and combination skin.", [("150ml", 26000, 45, 220)]),
    ("beauty-personal-care", "haircare", 3, "Coconut Hair Oil 200ml", "Zanzibar Botanicals", "Cold-pressed coconut oil blended with rosemary.", [("200ml", 22000, 36, 240), ("400ml", 36000, 20, 440)]),
    ("beauty-personal-care", "grooming", 6, "Shea Lip Balm Trio", "Lake Zone Care", "Three tinted balms in a gift-ready tin.", [("Trio", 18000, 50, 120)]),
    ("baby-maternity", "baby-care", 4, "Cotton Baby Blanket", "Tumaini", "Soft double-layer blanket sized for cots and prams.", [("Yellow", 36000, 18, 700), ("Grey", 36000, 15, 700)]),
    ("baby-maternity", "feeding", 4, "BPA-Free Feeding Set", "Tumaini", "Bowl, plate, cup and spoon set with suction bases.", [("Mint", 48000, 22, 500)]),
    ("baby-maternity", "maternity", 4, "Maternity Support Pillow", "Tumaini", "C-shaped pillow with a removable washable cover.", [("Grey", 112000, 9, 2200)]),
    ("baby-maternity", "baby-care", 4, "Cotton Baby Onesie Pack", "Tumaini", "Three short-sleeve onesies with press studs.", [("0-3m", 34000, 20, 350), ("3-6m", 34000, 18, 370), ("6-9m", 36000, 12, 390)]),
    ("bundles", "starter-kits", 5, "New Home Kitchen Starter Set", "Dodoma Kitchen Works", "Plates, cups, cutlery, cooking pot and serving bowls for two.", [("For 2", 178000, 10, 6500), ("For 4", 245000, 6, 9200)]),
    ("bundles", "starter-kits", 5, "Student Room Essentials Kit", "Dodoma Kitchen Works", "Kettle, storage baskets, bedding set and desk lamp alternative.", [("Standard", 162000, 8, 4800)]),
    ("bundles", "gift-sets", 3, "Zanzibar Spa Gift Hamper", "Zanzibar Botanicals", "Body butter, scrub, soap and hair oil in a woven basket.", [("Classic", 96000, 14, 1800), ("Deluxe", 138000, 7, 2600)]),
    ("bundles", "starter-kits", 0, "Housewarming Hostess Set", "Kariakoo Living", "Serving tray, jug, tea towels and storage jars.", [("Standard", 84000, 12, 2600)]),
]


def seed(db: Session, *, reset: bool = False) -> None:
    if reset:
        from .db import Base, engine

        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

    ledger.ensure_accounts(db)
    for key, value in DEFAULTS.items():
        if db.get(PlatformConfig, key) is None:
            db.add(PlatformConfig(key=key, value=json.dumps(value)))
    db.flush()

    if db.scalar(select(Department).limit(1)) is not None:
        db.commit()
        return

    random.seed(7)
    password = hash_password(DEMO_PASSWORD)

    departments: dict[str, Department] = {}
    categories: dict[str, Category] = {}
    for order, (slug, name, name_sw, description, cats) in enumerate(DEPARTMENTS):
        department = Department(
            slug=slug, name=name, name_sw=name_sw, description=description, sort_order=order
        )
        db.add(department)
        db.flush()
        departments[slug] = department
        for cat_slug in cats:
            category = Category(
                department_id=department.id,
                slug=cat_slug,
                name=cat_slug.replace("-", " ").title(),
                name_sw=cat_slug.replace("-", " ").title(),
            )
            db.add(category)
            db.flush()
            categories[f"{slug}:{cat_slug}"] = category

    suppliers: list[Supplier] = []
    for definition in SUPPLIERS:
        supplier = Supplier(
            **definition,
            payout_account_name=definition["trading_name"],
            payout_account_number=f"2557{random.randint(10_000_000, 99_999_999)}",
            kyc_verified_at=datetime.now(UTC) if definition["status"] == "verified" else None,
        )
        db.add(supplier)
        db.flush()
        suppliers.append(supplier)

        db.add(
            SupplierDocument(
                supplier_id=supplier.id,
                doc_type="brela_certificate",
                file_ref=f"seed/{supplier.code}/brela.pdf",
                status="approved" if supplier.status == "verified" else "pending",
            )
        )
        db.add(
            SupplierDocument(
                supplier_id=supplier.id,
                doc_type="tin_certificate",
                file_ref=f"seed/{supplier.code}/tin.pdf",
                status="approved" if supplier.status == "verified" else "pending",
            )
        )
        handle = supplier.trading_name.lower().split()[0]
        db.add(
            User(
                email=f"{handle}@suppliers.usiri.co.tz",
                phone=supplier.contact_phone,
                password_hash=password,
                full_name=supplier.contact_name or supplier.trading_name,
                role=Role.SUPPLIER,
                supplier_id=supplier.id,
                email_verified=True,
            )
        )

    for dept_slug, cat_slug, supplier_index, name, brand, description, variants in PRODUCTS:
        slug = name.lower().replace("&", "and").replace("'", "").replace("/", "-")
        slug = "-".join(part for part in slug.replace(",", "").split())
        product = Product(
            supplier_id=suppliers[supplier_index].id,
            department_id=departments[dept_slug].id,
            category_id=categories[f"{dept_slug}:{cat_slug}"].id,
            slug=slug,
            name=name,
            brand=brand,
            description=description,
            status="active",
            attributes={"origin": "Tanzania"},
        )
        db.add(product)
        db.flush()
        for index, (variant_name, price, stock, weight) in enumerate(variants):
            db.add(
                ProductVariant(
                    product_id=product.id,
                    sku=f"USR-{product.id[:6].upper()}-{index + 1:02d}",
                    name=variant_name,
                    price_tzs=price,
                    on_hand=stock,
                    weight_g=weight,
                )
            )

    staff = [
        ("admin@usiri.co.tz", "Amina Mwinyi", Role.SUPERADMIN),
        ("ops@usiri.co.tz", "Joseph Mrema", Role.OPS_ADMIN),
        ("finance@usiri.co.tz", "Neema Kessy", Role.OPS_FINANCE),
        ("finance2@usiri.co.tz", "Zawadi Mushi", Role.OPS_FINANCE),
        ("support@usiri.co.tz", "Baraka Mushi", Role.OPS_SUPPORT),
    ]
    for email, name, role in staff:
        db.add(
            User(
                email=email,
                phone="+255 700 000 100",
                password_hash=password,
                full_name=name,
                role=role,
                email_verified=True,
            )
        )

    demo = User(
        email="demo@usiri.co.tz",
        phone="+255 712 000 001",
        password_hash=password,
        full_name="Asha Juma",
        role=Role.CUSTOMER,
        email_verified=True,
    )
    db.add(demo)
    db.flush()
    db.add(
        Address(
            user_id=demo.id,
            label="Home",
            recipient_name="Asha Juma",
            phone="+255 712 000 001",
            region="Dar es Salaam",
            district="Kinondoni",
            ward="Mikocheni",
            street="Mikocheni B, Rose Garden Road",
            landmark="Opposite Shoppers Plaza",
            is_default=True,
        )
    )

    second = User(
        email="daniel@example.co.tz",
        phone="+255 754 000 002",
        password_hash=password,
        full_name="Daniel Kimaro",
        role=Role.CUSTOMER,
        email_verified=True,
    )
    db.add(second)
    db.flush()
    db.add(
        Address(
            user_id=second.id,
            label="Home",
            recipient_name="Daniel Kimaro",
            phone="+255 754 000 002",
            region="Arusha",
            district="Arusha City",
            ward="Kaloleni",
            street="Old Moshi Road",
            is_default=True,
        )
    )

    db.commit()
