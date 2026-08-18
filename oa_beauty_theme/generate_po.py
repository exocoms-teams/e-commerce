import os

module_dir = r"c:\Users\maram\e-commerce\oa_beauty_theme"

# Exact blocks as they appear in the XML, with normalized whitespace (Odoo compresses inner whitespace)
# We will use exactly what we see in the files.
translations = {
    # Homepage
    "La Beauté Éditoriale": {
        "en": "Editorial Beauty",
        "ar": "الجمال التحريري"
    },
    "Trois Regards,<br/>\n                                <span class=\"oa-editorial-accent\">Une Beauté</span>": {
        "en": "Three Looks,<br/>\n                                <span class=\"oa-editorial-accent\">One Beauty</span>",
        "ar": "ثلاث إطلالات،<br/>\n                                <span class=\"oa-editorial-accent\">جمال واحد</span>"
    },
    "Formules transparentes, textures sensorielles, élégance sans compromis. Célébrez votre essence naturelle.": {
        "en": "Transparent formulas, sensory textures, uncompromising elegance. Celebrate your natural essence.",
        "ar": "تركيبات شفافة، قوام حسي، أناقة لا تقبل المساومة. احتفلي بجوهرك الطبيعي."
    },
    "Découvrir la Collection": {
        "en": "Discover the Collection",
        "ar": "اكتشفي المجموعة"
    },
    "Découvrir la Collection <i class=\"fa fa-long-arrow-right ms-3\"></i>": {
        "en": "Discover the Collection <i class=\"fa fa-long-arrow-right ms-3\"></i>",
        "ar": "اكتشفي المجموعة <i class=\"fa fa-long-arrow-left ms-3\"></i>"
    },
    "La beauté révélée,<br/>\n                                <span class=\"oa-editorial-accent\">jamais déguisée.</span>": {
        "en": "Beauty revealed,<br/>\n                                <span class=\"oa-editorial-accent\">never disguised.</span>",
        "ar": "جمال مكشوف،<br/>\n                                <span class=\"oa-editorial-accent\">لا يتخفى أبداً.</span>"
    },
    "L'histoire de O&amp;A Atelier est née d'une fusion entre créativité, science et narration. <strong>Olesea</strong> sculpte la sensorialité de chaque produit, <strong>Amalia</strong> exige l'excellence des formules actives, et <strong>Irina</strong> tisse l'esthétique visuelle qui donne vie à la marque.": {
        "en": "The story of O&amp;A Atelier was born from a fusion of creativity, science, and storytelling. <strong>Olesea</strong> sculpts the sensoriality of each product, <strong>Amalia</strong> demands excellence in active formulas, and <strong>Irina</strong> weaves the visual aesthetics that bring the brand to life.",
        "ar": "ولدت قصة O&amp;A Atelier من اندماج الإبداع والعلم ورواية القصص. <strong>Olesea</strong> تنحت حسية كل منتج، و<strong>Amalia</strong> تطالب بالتميز في التركيبات الفعالة، و<strong>Irina</strong> تنسج الجماليات البصرية التي تضفي الحيوية على العلامة التجارية."
    },
    "Nous créons des produits qui célèbrent vos imperfections autant que vos atouts, avec une formulation transparente et une touche de luxe.": {
        "en": "We create products that celebrate your imperfections as much as your assets, with transparent formulation and a touch of luxury.",
        "ar": "نحن نبتكر منتجات تحتفي بعيوبك بقدر ما تحتفي بميزاتك، بتركيبة شفافة ولمسة من الفخامة."
    },
    "Notre Manifeste": {
        "en": "Our Manifesto",
        "ar": "بياننا"
    },
    "Explorez nos <span class=\"oa-editorial-accent\">Univers</span>": {
        "en": "Explore our <span class=\"oa-editorial-accent\">Universes</span>",
        "ar": "اكتشفي <span class=\"oa-editorial-accent\">عوالمنا</span>"
    },
    "Des rituels sensoriels pensés pour sublimer chaque instant de votre journée.": {
        "en": "Sensory rituals designed to sublimate every moment of your day.",
        "ar": "طقوس حسية مصممة لتجميل كل لحظة من يومك."
    },
    "Le Soin": {
        "en": "Skincare",
        "ar": "العناية بالبشرة"
    },
    "Le Maquillage": {
        "en": "Makeup",
        "ar": "المكياج"
    },
    "Les Parfums": {
        "en": "Fragrances",
        "ar": "العطور"
    },
    "Science &amp; Nature": {
        "en": "Science &amp; Nature",
        "ar": "العلم والطبيعة"
    },
    "Ingrédients Actifs de <span class=\"oa-editorial-accent\">Haute Performance</span>": {
        "en": "High Performance <span class=\"oa-editorial-accent\">Active Ingredients</span>",
        "ar": "<span class=\"oa-editorial-accent\">مكونات نشطة</span> عالية الأداء"
    },
    "Hydratation Bio-compatible": {
        "en": "Bio-compatible Hydration",
        "ar": "ترطيب متوافق حيوياً"
    },
    "Imite les huiles naturelles de la peau pour retenir l'hydratation sans obstruer les pores.": {
        "en": "Mimics the skin's natural oils to retain moisture without clogging pores.",
        "ar": "يحاكي الزيوت الطبيعية للبشرة للاحتفاظ بالرطوبة دون انسداد المسام."
    },
    "Repulpe &amp; Lisse": {
        "en": "Plumps &amp; Smooths",
        "ar": "يملأ وينعم"
    },
    "Attire l'eau à la surface de la peau pour un aspect radieux, rebondi et rajeuni.": {
        "en": "Draws water to the skin's surface for a radiant, plump, and rejuvenated appearance.",
        "ar": "يجذب الماء إلى سطح البشرة للحصول على مظهر مشرق وممتلئ ومتجدد."
    },
    "Éclat Antioxydant": {
        "en": "Antioxidant Radiance",
        "ar": "إشراقة مضادة للأكسدة"
    },
    "Illumine le teint, estompe les taches sombres et défend la peau contre les agresseurs environnementaux.": {
        "en": "Illuminates the complexion, fades dark spots, and defends the skin against environmental aggressors.",
        "ar": "يضيء البشرة، ويخفي البقع الداكنة، ويدافع عن البشرة ضد المعتدين البيئيين."
    },
    "La Communauté O&amp;A Atelier": {
        "en": "The O&amp;A Atelier Community",
        "ar": "مجتمع O&amp;A Atelier"
    },
    "Rejoignez plus de <span class=\"oa-editorial-accent oa-counter-10k\" style=\"color: var(--oa-lilac);\">10000</span> clientes satisfaites": {
        "en": "Join over <span class=\"oa-editorial-accent oa-counter-10k\" style=\"color: var(--oa-lilac);\">10000</span> satisfied customers",
        "ar": "انضمي إلى أكثر من <span class=\"oa-editorial-accent oa-counter-10k\" style=\"color: var(--oa-lilac);\">10000</span> عميلة راضية"
    },
    "L'Univers des <span style=\"color:var(--oa-lilac);font-style:italic;\">Parfums</span>": {
        "en": "The Universe of <span style=\"color:var(--oa-lilac);font-style:italic;\">Fragrances</span>",
        "ar": "عالم <span style=\"color:var(--oa-lilac);font-style:italic;\">العطور</span>"
    },
    "Six créations olfactives d'exception, nées de l'alliance entre la science des fleurs et l'art de la séduction.": {
        "en": "Six exceptional olfactory creations, born from the alliance between the science of flowers and the art of seduction.",
        "ar": "ستة إبداعات عطرية استثنائية، ولدت من التحالف بين علم الزهور وفن الإغراء."
    },
    "La Confiance,<br/>\n                                <span style=\"color:var(--oa-lilac);font-style:italic;\">au cœur de tout.</span>": {
        "en": "Trust,<br/>\n                                <span style=\"color:var(--oa-lilac);font-style:italic;\">at the heart of everything.</span>",
        "ar": "الثقة،<br/>\n                                <span style=\"color:var(--oa-lilac);font-style:italic;\">في صميم كل شيء.</span>"
    },
    "Get the <span class=\"oa-editorial-accent\">Look</span>": {
        "en": "Get the <span class=\"oa-editorial-accent\">Look</span>",
        "ar": "احصلي على <span class=\"oa-editorial-accent\">الإطلالة</span>"
    },
    "L'essentiel pour un fini naturel et lumineux.": {
        "en": "The essentials for a natural and luminous finish.",
        "ar": "الأساسيات للحصول على لمسة نهائية طبيعية ومشرقة."
    },
    "Voir tout": {
        "en": "View all",
        "ar": "عرض الكل"
    },

    # Core pages
    "Découvrez Votre Rituel": {
        "en": "Discover Your Ritual",
        "ar": "اكتشفي طقوسك"
    },
    "Explorez nos collections de cosmétiques de luxe clean, conçues pour sublimer votre beauté naturelle.": {
        "en": "Explore our collections of clean luxury cosmetics, designed to sublimate your natural beauty.",
        "ar": "استكشفي مجموعاتنا من مستحضرات التجميل الفاخرة والنظيفة، المصممة لإبراز جمالك الطبيعي."
    },
    "Magasiner par Catégorie": {
        "en": "Shop by Category",
        "ar": "تسوق حسب الفئة"
    },
    "Nos Meilleures Ventes": {
        "en": "Our Best Sellers",
        "ar": "الأكثر مبيعاً"
    },
    "Nouveautés": {
        "en": "New Arrivals",
        "ar": "وصل حديثاً"
    },
    "Une Belle Peau Commence Ici": {
        "en": "Beautiful Skin Starts Here",
        "ar": "البشرة الجميلة تبدأ من هنا"
    },
    "Un rituel luxueux adapté aux besoins uniques de votre peau. Découvrez nos nettoyants, sérums, hydratants et traitements conçus par des experts.": {
        "en": "A luxurious ritual tailored to your skin's unique needs. Discover our expertly crafted cleansers, serums, moisturizers, and treatments.",
        "ar": "طقس فاخر مصمم خصيصاً لاحتياجات بشرتك الفريدة. اكتشفي منظفاتنا وأمصالنا ومرطباتنا وعلاجاتنا المصممة بخبرة."
    },
    "La Beauté qui Sublime,<br/>\n                                Sans Jamais Cacher": {
        "en": "Beauty that Sublimates,<br/>\n                                Without Ever Hiding",
        "ar": "جمال يبرز،<br/>\n                                دون أن يخفي أبداً"
    },
    "Élevez votre quotidien avec notre collection de maquillage premium. Des formules clean et longue tenue conçues pour une élégance sans effort.": {
        "en": "Elevate your everyday with our premium makeup collection. Clean, long-wearing formulas designed for effortless elegance.",
        "ar": "ارتقِ بيومياتك مع مجموعة مكياجنا الفاخرة. تركيبات نظيفة تدوم طويلاً مصممة لأناقة بلا مجهود."
    },
    "Les Favoris de Nos Clients": {
        "en": "Our Customers' Favorites",
        "ar": "مفضلات عملائنا"
    },
    "Découvrez les formules emblématiques et les incontournables absolus que notre communauté adore.": {
        "en": "Discover the iconic formulas and absolute must-haves that our community loves.",
        "ar": "اكتشفي التركيبات الأيقونية والأساسيات المطلقة التي يحبها مجتمعنا."
    },

    # Product fields
    "O&amp;A Product Type": {
        "en": "Beauty Product Type",
        "ar": "نوع منتج التجميل"
    },
    "Finish": {
        "en": "Finish",
        "ar": "اللمسة النهائية"
    },
    "Key Ingredients": {
        "en": "Key Ingredients",
        "ar": "المكونات الرئيسية"
    },
    "Skin Type": {
        "en": "Skin Type",
        "ar": "نوع البشرة"
    },
    "Fragrance Family": {
        "en": "Fragrance Family",
        "ar": "العائلة العطرية"
    },
    "Top Notes": {
        "en": "Top Notes",
        "ar": "مقدمة العطر"
    },
    "Heart Notes": {
        "en": "Heart Notes",
        "ar": "قلب العطر"
    },
    "Base Notes": {
        "en": "Base Notes",
        "ar": "قاعدة العطر"
    },
    "Benefits": {
        "en": "Benefits",
        "ar": "الفوائد"
    },
    "How to Use": {
        "en": "How to Use",
        "ar": "طريقة الاستخدام"
    },
    
    # Static UI and JS
    "Add to Cart": {
        "en": "Add to Cart",
        "ar": "أضف إلى السلة"
    },
    "Out of Stock": {
        "en": "Out of Stock",
        "ar": "نفذت الكمية"
    },
    "Coming Soon": {
        "en": "Coming Soon",
        "ar": "قريباً"
    },
    "Customer Reviews": {
        "en": "Customer Reviews",
        "ar": "تقييمات العملاء"
    },
    "Write a Review": {
        "en": "Write a Review",
        "ar": "اكتب تقييماً"
    }
}

def escape(text):
    return text.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')

def generate_po(filepath, lang_code, tgt_dict):
    content = f"""# Translation of Odoo Server.
# This file contains the translation of the following modules:
# 	* oa_beauty_theme
#
msgid ""
msgstr ""
"Project-Id-Version: Odoo Server 19.0\\n"
"Report-Msgid-Bugs-To: \\n"
"POT-Creation-Date: 2026-08-18 12:00+0000\\n"
"PO-Revision-Date: 2026-08-18 12:00+0000\\n"
"Language-Team: {lang_code.upper()}\\n"
"Language: {lang_code}\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: \\n"
"Plural-Forms: nplurals=2; plural=(n != 1);\\n"

"""
    for src, tgts in tgt_dict.items():
        val = tgts.get(lang_code, "")
        if val:
            content += f'#. module: oa_beauty_theme\n'
            # Check if source contains newlines, Odoo multi-line msgid is split
            if '\n' in src:
                lines = src.split('\n')
                content += 'msgid ""\n'
                for i, line in enumerate(lines):
                    newline = "\\n" if i < len(lines)-1 else ""
                    content += f'"{escape(line)}{newline}"\n'
            else:
                content += f'msgid "{escape(src)}"\n'
                
            if '\n' in val:
                lines = val.split('\n')
                content += 'msgstr ""\n'
                for i, line in enumerate(lines):
                    newline = "\\n" if i < len(lines)-1 else ""
                    content += f'"{escape(line)}{newline}"\n'
            else:
                content += f'msgstr "{escape(val)}"\n'
            content += '\n'
            
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

os.makedirs(os.path.join(module_dir, "i18n"), exist_ok=True)
generate_po(os.path.join(module_dir, "i18n", "en.po"), "en", translations)
generate_po(os.path.join(module_dir, "i18n", "ar.po"), "ar", translations)

print("Manual PO files created successfully.")
