"""
Seeds the database with Roz Boutique's categories, sample products, shipping
rules, return policy, reviews, and an admin user.

Run with: python3 manage.py seed_data

Safe to run multiple times — it checks for existing data first and won't
create duplicates. To force a full reset, delete db.sqlite3, re-run
migrations, then run this again.
"""
import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from store.models import (
    Category, Product, ProductSize, SizeGuide, SizeGuideRow,
    ShippingRule, ReturnPolicy, Review, InstagramPost,
)


class Command(BaseCommand):
    help = "Seeds the database with sample Roz Boutique data"

    def handle(self, *args, **options):
        self.seed_admin()
        self.seed_categories()
        self.seed_products()
        self.seed_shipping()
        self.seed_return_policy()
        self.seed_reviews()
        self.seed_instagram()
        self.stdout.write(self.style.SUCCESS("Database seeded successfully."))

    def seed_admin(self):
        email = os.environ.get("ADMIN_EMAIL", "admin@roz.com")
        password = os.environ.get("ADMIN_PASSWORD", "roz-admin-2026")
        if not User.objects.filter(username=email).exists():
            User.objects.create_superuser(username=email, email=email, password=password)
            self.stdout.write(f"Created admin user: {email}")
        else:
            self.stdout.write(f"Admin user {email} already exists — skipped.")

    def seed_categories(self):
        if Category.objects.exists():
            self.stdout.write("Categories already exist — skipped.")
            return
        categories = [
            ("New Arrivals", "new-arrivals", "Fresh from the atelier", 1),
            ("Luxury Pret", "luxury-pret", "Ready-to-wear, elevated", 2),
            ("Formals", "formals", "For occasions that matter", 3),
            ("Semi Formals", "semi-formals", "Effortless refinement", 4),
            ("Luxury Formals", "luxury-formals", "Bridal & couture-grade", 5),
            ("Tops", "tops", "Blouses, kurtis & shirts", 6),
            ("Skirts", "skirts", "Flowing silhouettes", 7),
            ("Pants", "pants", "Trousers, shalwars & more", 8),
            ("Kids", "kids", "Little ones, dressed in Roz", 9),
            ("Jewelry", "jewelry", "The finishing touch", 10),
        ]
        for name, slug, tagline, order in categories:
            Category.objects.create(name=name, slug=slug, tagline=tagline, display_order=order)
        self.stdout.write(f"Created {len(categories)} categories.")

    def seed_products(self):
        if Product.objects.exists():
            self.stdout.write("Products already exist — skipped.")
            return

        products = [
            ("Gulnaar Rose Embroidered Kurta Set", "new-arrivals", 148, 175,
             "A soft blush kurta set finished with hand-embroidered rose vines along the neckline and hem, paired with matching cigarette trousers and a dupatta edged in gold gota.",
             "Pure lawn cotton", 0, "Spring", True, True, True),
            ("Zoya Blush Chikankari Suit", "new-arrivals", 162, None,
             "Delicate chikankari hand-embroidery on breathable cotton, in a gentle blush that catches the light like petals at dawn.",
             "Cotton chikankari", 1, "Spring", False, True, True),
            ("Anaya Silk Straight Kurta", "luxury-pret", 128, None,
             "A clean-lined silk kurta in dusty rose, cut for everyday elegance with a subtle floral jacquard woven through the fabric.",
             "Silk jacquard", 2, "", True, False, False),
            ("Ishrat Pastel Kaftan", "luxury-pret", 112, 135,
             "Relaxed, breezy, and romantic — an ankle-length kaftan in whisper-soft pink georgette with butterfly sleeves.",
             "Georgette", 3, "Summer", False, False, False),
            ("Mehak Two-Piece Lawn Set", "luxury-pret", 96, None,
             "A crisp two-piece in cream and rose, printed with a hand-illustrated botanical trail.",
             "Premium lawn", 4, "Summer", True, False, False),
            ("Noorjahan Rose Gold Formal Gown", "formals", 385, 450,
             "An architectural silhouette in rose-gold organza with hand-placed floral appliqué cascading from the shoulder.",
             "Organza silk", 5, "", True, True, False),
            ("Saira Embellished Formal Saree", "formals", 340, None,
             "A blush saree with a hand-embroidered pallu of trailing roses, edged in fine gold zari.",
             "Silk chiffon", 0, "", False, True, False),
            ("Devika Gold-Threaded Anarkali", "formals", 298, None,
             "Floor-length Anarkali in soft rose with gold thread florals winding from bodice to hem.",
             "Silk blend", 1, "", False, False, False),
            ("Rania Rose Garden Semi-Formal Suit", "semi-formals", 210, None,
             "Understated luxury for daytime celebrations: a rose-embroidered bodice with a flowing cream skirt.",
             "Silk cotton blend", 2, "", False, False, False),
            ("Farah Blush Sharara Set", "semi-formals", 235, 260,
             "A three-piece sharara set in blush and gold, with delicate floral resham embroidery.",
             "Raw silk", 3, "", True, False, False),
            ("Meherbano Layered Semi-Formal Gown", "semi-formals", 265, None,
             "Soft layers of blush tulle over a rose silk slip, scattered with hand-sewn petals.",
             "Tulle & silk", 4, "", False, False, False),
            ("Roz Signature Bridal Lehenga", "luxury-formals", 1250, 1450,
             "Our most coveted piece: a hand-embroidered bridal lehenga in blush and antique gold, densely worked with rose motifs and zardozi.",
             "Silk velvet, zardozi", 5, "", True, True, False),
            ("Amara Couture Rose Gharara", "luxury-formals", 890, None,
             "A regal gharara set in rose pink silk, embellished with gold dabka and hand-cut floral appliqué.",
             "Silk, dabka work", 0, "", False, True, False),
            ("Yasmeen Heirloom Formal Set", "luxury-formals", 975, None,
             "Designed to be passed down — dense floral zardozi embroidery on a rose silk base, with a matching dupatta.",
             "Pure silk, zardozi", 1, "", False, False, False),
        ]

        default_sizes = {"XS": 4, "S": 8, "M": 10, "L": 7, "XL": 5, "XXL": 2}
        guide_text = (
            "Measure yourself in undergarments, standing straight. Chest: measure around the fullest "
            "part of your bust, keeping the tape parallel to the ground. Waist: measure around the "
            "narrowest part of your natural waistline. Hips: measure around the fullest part of your "
            "hips. Length: measure from the base of the neck to your desired hemline. If you fall "
            "between two sizes, we recommend sizing up for comfort, especially for heavily embellished pieces."
        )
        guide_rows_data = {
            "XS": (32, 26, 34, 42, 22, 13.5),
            "S": (34, 28, 36, 43, 22.5, 14),
            "M": (36, 30, 38, 44, 23, 14.5),
            "L": (38, 32, 40, 45, 23.5, 15),
            "XL": (40, 34, 42, 46, 24, 15.5),
            "XXL": (42, 36, 44, 47, 24.5, 16),
        }

        for (name, cat_slug, price, compare, desc, fabric, swatch, season, best, feat, new) in products:
            slug = "-".join(name.lower().replace(",", "").replace("'", "").split())
            category = Category.objects.get(slug=cat_slug)
            product = Product.objects.create(
                name=name, slug=slug, category=category, price=price,
                compare_at_price=compare, description=desc, fabric=fabric,
                swatch=swatch, season=season, is_best_seller=best,
                is_featured=feat, is_new_arrival=new, active=True,
            )
            for size_code, qty in default_sizes.items():
                ProductSize.objects.create(product=product, size_code=size_code, quantity=qty)

            guide = SizeGuide.objects.create(product=product, instructions=guide_text, unit="in")
            for size_code, (chest, waist, hips, length, sleeve, shoulder) in guide_rows_data.items():
                SizeGuideRow.objects.create(
                    size_guide=guide, size_code=size_code, chest=chest, waist=waist,
                    hips=hips, length=length, sleeve_length=sleeve, bottom_length=None,
                )

        # make the bridal lehenga sell out in XS/XXL, for realism
        lehenga = Product.objects.get(name="Roz Signature Bridal Lehenga")
        ProductSize.objects.filter(product=lehenga, size_code__in=["XS", "XXL"]).update(quantity=0)

        self.stdout.write(f"Created {len(products)} products with sizes and size guides.")

    def seed_shipping(self):
        if ShippingRule.objects.exists():
            self.stdout.write("Shipping rules already exist — skipped.")
            return
        rules = [
            ("United States", "USD", 9.00, 100),
            ("Canada", "USD", 14.00, 100),
            ("United Kingdom", "USD", 12.00, 100),
            ("Other", "USD", 22.00, 150),
        ]
        for country, currency, price, threshold in rules:
            ShippingRule.objects.create(
                country=country, currency=currency,
                standard_price=price, free_shipping_threshold=threshold,
            )
        self.stdout.write(f"Created {len(rules)} shipping rules.")

    def seed_return_policy(self):
        if ReturnPolicy.objects.exists():
            self.stdout.write("Return policy already exists — skipped.")
            return
        ReturnPolicy.objects.create(
            window_days=7,
            return_fee=12.00,
            eligibility_rules=(
                "Items must be unworn, unwashed, and returned with original tags attached. "
                "Bridal and made-to-order luxury formals are final sale. Customers are responsible "
                "for return shipping costs, deducted from the refund."
            ),
            refund_method="Refunded to original payment method within 5–7 business days of approval.",
        )
        self.stdout.write("Created return policy.")

    def seed_reviews(self):
        if Review.objects.exists():
            self.stdout.write("Reviews already exist — skipped.")
            return
        reviews = [
            ("Roz Signature Bridal Lehenga", "Sana K.", "Toronto, CA", 5,
             "I felt like royalty. The embroidery is even more stunning in person, and it arrived exactly as pictured."),
            ("Gulnaar Rose Embroidered Kurta Set", "Amara H.", "London, UK", 5,
             "The fabric is so soft and the fit is true to size. Roz has become my go-to for Eid outfits."),
            ("Noorjahan Rose Gold Formal Gown", "Priya D.", "New York, US", 5,
             "Wore this to a wedding and got endless compliments. Worth every penny."),
            ("Farah Blush Sharara Set", "Zainab R.", "Houston, US", 4,
             "Beautiful set, the color is more rose than blush in person but I love it even more."),
            ("Anaya Silk Straight Kurta", "Fatima N.", "Manchester, UK", 5,
             "Simple, elegant, and the silk quality is incredible for the price."),
            ("Amara Couture Rose Gharara", "Nadia S.", "Vancouver, CA", 5,
             "The dabka work is exquisite. Customer service was also lovely when I had sizing questions."),
        ]
        for product_name, customer, location, rating, comment in reviews:
            product = Product.objects.get(name=product_name)
            Review.objects.create(
                product=product, customer_name=customer, location=location,
                rating=rating, comment=comment,
            )
        self.stdout.write(f"Created {len(reviews)} reviews.")

    def seed_instagram(self):
        if InstagramPost.objects.exists():
            self.stdout.write("Instagram posts already exist — skipped.")
            return
        captions = [
            "Golden hour in Gulnaar rose \u2728",
            "Bridal season begins \U0001F337",
            "Petals & pret \u2014 new arrivals",
            "Behind the embroidery frame",
            "Styled: blush on blush",
            "From our atelier to your wardrobe",
            "Details that take 40 hours to hand-work",
            "Garden party ready",
        ]
        for i, caption in enumerate(captions):
            InstagramPost.objects.create(caption=caption, swatch=i % 6, sort_order=i)
        self.stdout.write(f"Created {len(captions)} Instagram posts.")
