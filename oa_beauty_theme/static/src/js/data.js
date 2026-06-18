/* ============================================================
   LUMIÈRE — data.js
   Static product catalog + categories + review pool.
   Loaded first; everything else reads from window.LM.*
   ============================================================ */
(function () {
  "use strict";
  window.LM = window.LM || {};

  /* ---------- Categories ---------- */
  LM.CATEGORIES = [
    { id: "skincare",  name: "Skincare",   blurb: "Serums, creams & rituals for clear, calm skin." },
    { id: "face",      name: "Face",       blurb: "Tints, blush & glow for a no-makeup makeup look." },
    { id: "lips",      name: "Lips",       blurb: "Colour, gloss & balm that feel as good as they look." },
    { id: "eyes",      name: "Eyes",       blurb: "Mascara, liner & palettes for definition that lasts." },
    { id: "body",      name: "Body Care",  blurb: "Lotions, scrubs & oils for skin beyond the face." },
    { id: "fragrance", name: "Fragrance",  blurb: "Signature scents, worn close to the skin." }
  ];

  LM.getCategoryName = function (id) {
    var c = LM.CATEGORIES.find(function (c) { return c.id === id; });
    return c ? c.name : id;
  };

  /* ---------- Products ---------- */
  LM.PRODUCTS = [
    {
      id: 1, name: "Lumière Radiance Serum", category: "skincare", art: "dropper",
      price: 68, rating: 4.9, reviewCount: 412, badge: "Bestseller",
      type: "Brightening Serum", finish: "Lightweight, fast-absorbing",
      bestFor: "Dullness & uneven tone", keyIngredients: "Vitamin C, Niacinamide, Squalane",
      description: "A weightless vitamin C serum that leaves skin luminous by morning.",
      details: "Our signature serum pairs stabilised vitamin C with niacinamide to brighten, even tone, and soften the look of fine lines, without the sting older formulas are known for. A few drops sink in instantly, leaving skin dewy, never greasy.",
      howToUse: ["Apply 2–3 drops to clean, dry skin morning and night.", "Press gently into face and neck before heavier creams.", "Follow with SPF during the day."],
      sizes: [{ label: "30ml", delta: 0 }, { label: "50ml", delta: 22 }]
    },
    {
      id: 2, name: "Cloud Cream Moisturizer", category: "skincare", art: "jar",
      price: 54, rating: 4.8, reviewCount: 298,
      type: "Whipped Moisturizer", finish: "Satin, plush",
      bestFor: "Dry & dehydrated skin", keyIngredients: "Ceramides, Shea Butter, Hyaluronic Acid",
      description: "A cloud-light whip that floods skin with 24-hour moisture.",
      details: "Whipped to a featherweight texture, this moisturizer melts into skin on contact and settles into a soft, dewy finish. Ceramides and shea butter restore the skin barrier while hyaluronic acid keeps comfort levels high from breakfast to bedtime.",
      howToUse: ["Warm a small amount between palms.", "Press into face and neck as the last step of your routine.", "Reapply midday if skin feels tight."],
      sizes: [{ label: "50ml", delta: 0 }, { label: "100ml", delta: 20 }]
    },
    {
      id: 3, name: "Dew Drop Cleansing Oil", category: "skincare", art: "pump",
      price: 38, rating: 4.7, reviewCount: 201,
      type: "Cleansing Oil", finish: "Silky, rinses clean",
      bestFor: "Removing makeup & SPF", keyIngredients: "Jojoba Oil, Camellia Oil, Vitamin E",
      description: "A botanical oil cleanser that melts away makeup without stripping skin.",
      details: "This first-step cleanser dissolves makeup, SPF and the day itself, while a blend of jojoba and camellia oils keeps the skin barrier soft and calm. It emulsifies into a milk on contact with water and rinses away with no residue.",
      howToUse: ["Massage 2 pumps onto dry skin for 60 seconds.", "Add a splash of water to emulsify into a milk.", "Rinse thoroughly, then follow with your second cleanser."],
      sizes: [{ label: "100ml", delta: 0 }, { label: "200ml", delta: 14 }]
    },
    {
      id: 4, name: "Overnight Recovery Elixir", category: "skincare", art: "dropper",
      price: 72, rating: 4.9, reviewCount: 156, badge: "New",
      type: "Night Treatment", finish: "Rich, balm-like",
      bestFor: "Repair while you sleep", keyIngredients: "Bakuchiol, Peptides, Squalane",
      description: "A nourishing night oil-serum that works while you rest.",
      details: "Formulated for the hours your skin repairs itself, this elixir blends bakuchiol, a gentle plant-based retinol alternative, with peptides and squalane to support firmness and softness by morning. Wake up to skin that looks rested, even when you aren't.",
      howToUse: ["Apply 3–4 drops as the final step of your evening routine.", "Massage upward from neck to forehead.", "Use 3–4 nights per week to start, building up as tolerated."]
    },
    {
      id: 5, name: "Soft Focus Skin Tint", category: "face", art: "pump",
      price: 46, rating: 4.6, reviewCount: 184,
      type: "Sheer Foundation", finish: "Skin-like, second-skin",
      bestFor: "Natural, no-makeup makeup", keyIngredients: "Hyaluronic Acid, SPF 20, Light Reflectors",
      description: "A featherweight tint that evens skin while looking like skin.",
      details: "Part skincare, part coverage, this tint blurs imperfections and evens tone with a soft-focus finish, while hyaluronic acid keeps it from ever looking cakey. Buildable from sheer to light-medium, it never sits in fine lines.",
      howToUse: ["Warm 2–3 drops between fingertips.", "Press onto skin starting from the center of the face.", "Build coverage only where needed; set with powder if desired."],
      shades: [{ name: "Porcelain", hex: "#f3dcc9" }, { name: "Vanille", hex: "#e8c6a0" }, { name: "Miel", hex: "#cf9b6c" }, { name: "Noisette", hex: "#a9714a" }, { name: "Acajou", hex: "#7c4a2c" }]
    },
    {
      id: 6, name: "Petal Flush Blush", category: "face", art: "compact",
      price: 32, compareAtPrice: 38, rating: 4.8, reviewCount: 233, badge: "Sale",
      type: "Cream Blush", finish: "Dewy flush",
      bestFor: "A natural, just-pinched glow", keyIngredients: "Jojoba Oil, Rose Extract",
      description: "A cream blush that blends like a dream and looks like sunshine.",
      details: "One swipe of this featherlight cream melts into skin for a flush that looks like it came from underneath, not on top. Rose extract and jojoba oil keep the formula comfortable enough to forget you're wearing it.",
      howToUse: ["Dab onto cheeks with fingertip.", "Blend outward toward temples in small circles.", "Layer for more intensity."],
      shades: [{ name: "Rose Petal", hex: "#e8a3ad" }, { name: "Berry Kiss", hex: "#c45a6a" }, { name: "Sunset Coral", hex: "#e8825c" }]
    },
    {
      id: 7, name: "Moonlight Highlighter Duo", category: "face", art: "compact",
      price: 36, rating: 4.7, reviewCount: 142,
      type: "Cream Highlighter", finish: "Luminous, glass-like",
      bestFor: "Lit-from-within glow", keyIngredients: "Mica, Squalane, Pearl Powder",
      description: "Two cream highlighters that catch the light from every angle.",
      details: "A duo of complementary cream highlighters, one warm, one cool, for a glow that adapts to any look. Soft pearl pigments melt into skin rather than sitting on top, for a lit-from-within finish that photographs beautifully.",
      howToUse: ["Tap onto cheekbones, brow bone, and cupid's bow.", "Blend with fingertip or damp sponge.", "Layer both shades together for a multidimensional glow."],
      shades: [{ name: "Champagne", hex: "#e8d3a8" }, { name: "Rosé", hex: "#dba8a0" }]
    },
    {
      id: 8, name: "Velvet Veil Setting Powder", category: "face", art: "compact",
      price: 40, rating: 4.6, reviewCount: 97,
      type: "Translucent Powder", finish: "Soft-matte, blurred",
      bestFor: "All-day wear without shine", keyIngredients: "Rice Powder, Silica",
      description: "A whisper-light powder that blurs pores without flattening skin.",
      details: "Milled finer than fine, this translucent powder sets makeup and softens the look of pores without ever looking dry or cakey. Rice powder absorbs shine through the day while keeping that second-skin finish intact.",
      howToUse: ["Dust lightly over the T-zone with a fluffy brush.", "Focus on areas prone to shine.", "Reapply midday with a light hand if needed."]
    },
    {
      id: 9, name: "Velvet Lip Elixir", category: "lips", art: "lipstick",
      price: 28, rating: 4.9, reviewCount: 518, badge: "Bestseller",
      type: "Liquid Lipstick", finish: "Matte velvet",
      bestFor: "Long-lasting, conditioning colour", keyIngredients: "Shea Butter, Vitamin E, Jojoba Oil",
      description: "A velvet-matte liquid lipstick that conditions while it colours.",
      details: "Extraordinary colour payoff meets skincare-grade conditioning. This liquid-to-matte formula glides on weightless, sets to a soft velvet finish, and wears for hours without the dry, cracked feeling matte lipsticks usually leave behind.",
      howToUse: ["Apply from the center of the lips outward.", "Allow 30 seconds to set to a matte finish.", "Layer for a fuller, more opaque finish."],
      shades: [{ name: "Rose Petal", hex: "#c97b8a" }, { name: "Berry Kiss", hex: "#9b3d54" }, { name: "Nude Silk", hex: "#c9967f" }, { name: "Red Muse", hex: "#a1273a" }, { name: "Mauve Dust", hex: "#a9788a" }]
    },
    {
      id: 10, name: "Glass Petal Gloss", category: "lips", art: "gloss",
      price: 24, compareAtPrice: 29, rating: 4.7, reviewCount: 266, badge: "Sale",
      type: "Lip Gloss", finish: "High-shine glass",
      bestFor: "Mirror-like shine, non-sticky", keyIngredients: "Castor Oil, Vitamin E",
      description: "A non-sticky gloss for that just-bitten, glass-skin shine.",
      details: "All shine, no stick. This gloss glides on smooth and dries down to a comfortable, glass-like finish that catches the light without the tacky feeling of traditional glosses. Wear alone or over your favourite lip colour.",
      howToUse: ["Apply directly from the doe-foot applicator.", "Blot lightly for a more subtle sheen.", "Layer over lipstick for added dimension."],
      shades: [{ name: "Clear Quartz", hex: "#f3d9d9" }, { name: "Rose Glass", hex: "#e3a3ad" }, { name: "Cinnamon", hex: "#c98060" }]
    },
    {
      id: 11, name: "Rose Balm Repair", category: "lips", art: "jar",
      price: 18, rating: 4.8, reviewCount: 189,
      type: "Lip Balm", finish: "Sheer tint, glossy",
      bestFor: "Dry, chapped lips", keyIngredients: "Shea Butter, Rosehip Oil, Beeswax",
      description: "An overnight repair balm with the faintest wash of rose.",
      details: "Part treatment, part tint, this balm melts on with a faint rose flush and gets to work softening dry, chapped lips overnight. Rosehip oil and beeswax form a protective layer that locks in moisture until morning.",
      howToUse: ["Apply generously before bed.", "Use throughout the day as needed.", "Pair with a lip scrub once weekly for extra softness."]
    },
    {
      id: 12, name: "Satin Lip Liner", category: "lips", art: "pencil",
      price: 20, rating: 4.6, reviewCount: 88,
      type: "Lip Liner", finish: "Satin-matte",
      bestFor: "Defining & extending wear", keyIngredients: "Vitamin E, Jojoba Esters",
      description: "A creamy liner that defines lips without dragging or feathering.",
      details: "Glides on smooth, sets to a satin-matte finish, and stays put with no feathering and no fading by lunch. Use it to define, fill in fully for a soft matte lip, or layer beneath gloss for longer wear.",
      howToUse: ["Line lips starting at the center of the bow.", "Fill in completely for longer-lasting colour underneath lipstick.", "Sharpen regularly for a precise line."],
      shades: [{ name: "Rose Petal", hex: "#c97b8a" }, { name: "Berry Kiss", hex: "#9b3d54" }, { name: "Nude Silk", hex: "#c9967f" }]
    },
    {
      id: 13, name: "Feather Lash Mascara", category: "eyes", art: "mascara",
      price: 30, rating: 4.7, reviewCount: 312,
      type: "Volumizing Mascara", finish: "Feather-light, buildable",
      bestFor: "Length & volume without clumps", keyIngredients: "Castor Oil, Beeswax, Rice Starch",
      description: "A clump-free mascara that builds from natural to dramatic.",
      details: "A flexible hourglass brush coats every lash, even the small inner-corner ones, for length and volume that builds without clumping or flaking. Wears comfortably from morning meetings to last call.",
      howToUse: ["Wiggle the brush at the root, then sweep upward.", "Apply a second coat to outer lashes for extra drama.", "Remove gently with a water-based makeup remover."],
      shades: [{ name: "Blackest Black", hex: "#1a1a1a" }, { name: "Espresso Brown", hex: "#3b2a22" }]
    },
    {
      id: 14, name: "Twilight Eyeshadow Palette", category: "eyes", art: "palette",
      price: 58, rating: 4.9, reviewCount: 174, badge: "Limited",
      type: "9-Pan Eyeshadow Palette", finish: "Mattes, satins & shimmers",
      bestFor: "Day-to-night eye looks", keyIngredients: "Mica, Talc-free Base",
      description: "Nine blendable shades that move effortlessly from desk to dinner.",
      details: "A considered edit of nine shadows, soft mattes for the crease, satin transitions, and two foiled shimmers for the lid, built to blend into each other with almost no effort. One palette, an entire season of eye looks.",
      howToUse: ["Start with a matte shade in the crease to build dimension.", "Pat shimmer shades onto the lid with a fingertip.", "Blend edges with a clean fluffy brush."]
    },
    {
      id: 15, name: "Precision Ink Eyeliner", category: "eyes", art: "pencil",
      price: 24, rating: 4.6, reviewCount: 121,
      type: "Liquid Eyeliner", finish: "Ultra-matte, smudge-proof",
      bestFor: "Sharp lines & winged looks", keyIngredients: "Carbon Black Pigment, Vitamin E",
      description: "A precision felt-tip liner for lines so sharp they look airbrushed.",
      details: "A fine, flexible tip glides on with total control, perfect for first-timers and wing experts alike. It dries down matte and budge-proof within seconds, holding its line through humidity, tears, and everything in between.",
      howToUse: ["Rest the tip at the lash line and draw in short strokes.", "Build your wing gradually rather than committing to one line.", "Let dry for 10 seconds before opening eyes fully."],
      shades: [{ name: "Noir", hex: "#161616" }, { name: "Cacao", hex: "#3b2a22" }]
    },
    {
      id: 16, name: "Arch Define Brow Pencil", category: "eyes", art: "pencil",
      price: 22, rating: 4.5, reviewCount: 103,
      type: "Brow Pencil", finish: "Natural, hair-like strokes",
      bestFor: "Filling sparse areas", keyIngredients: "Carnauba Wax, Vitamin E",
      description: "An ultra-fine pencil that mimics real brow hairs, strand by strand.",
      details: "A precision tip thin enough to draw individual hair-like strokes, with a built-in spoolie to soften and blend. It fills sparse patches without ever looking drawn-on.",
      howToUse: ["Use short, light strokes following your natural brow shape.", "Fill sparse areas first, then define the arch.", "Brush through with the spoolie to soften."],
      shades: [{ name: "Blonde", hex: "#c9a36a" }, { name: "Taupe", hex: "#8a6a52" }, { name: "Espresso", hex: "#4a3324" }]
    },
    {
      id: 17, name: "Silk Body Lotion", category: "body", art: "pump",
      price: 42, rating: 4.8, reviewCount: 212,
      type: "Whipped Body Lotion", finish: "Silky, fast-absorbing",
      bestFor: "Everyday hydration", keyIngredients: "Shea Butter, Oat Extract, Squalane",
      description: "A whipped lotion that absorbs in seconds, never sticky.",
      details: "Whipped to a cloud-like texture, this lotion sinks into skin in seconds, leaving behind softness without any greasy residue. Oat extract calms while shea butter and squalane keep moisture locked in for hours.",
      howToUse: ["Smooth generously over damp or dry skin.", "Focus on rough patches like elbows and knees.", "Use daily after showering for best results."],
      sizes: [{ label: "200ml", delta: 0 }, { label: "400ml", delta: 16 }]
    },
    {
      id: 18, name: "Sugar Bloom Body Scrub", category: "body", art: "jar",
      price: 34, compareAtPrice: 40, rating: 4.7, reviewCount: 178, badge: "Sale",
      type: "Exfoliating Sugar Scrub", finish: "Polishing, fine-grain",
      bestFor: "Smoothing rough, dry skin", keyIngredients: "Cane Sugar, Coconut Oil, Vanilla",
      description: "A fine cane-sugar scrub that polishes skin to a soft glow.",
      details: "Fine cane sugar buffs away dry, rough patches while coconut oil keeps things from ever feeling stripped. A faint vanilla warmth lingers after rinsing, your skin will feel like satin.",
      howToUse: ["Massage onto damp skin in circular motions.", "Focus on elbows, knees, and heels.", "Rinse thoroughly and follow with body lotion."]
    },
    {
      id: 19, name: "Golden Hour Dry Oil", category: "body", art: "pump",
      price: 44, rating: 4.8, reviewCount: 134,
      type: "Shimmer Body Oil", finish: "Fast-absorbing, golden sheen",
      bestFor: "A subtle, sun-kissed glow", keyIngredients: "Squalane, Jojoba Oil, Mica",
      description: "A weightless dry oil with the faintest golden shimmer.",
      details: "This featherlight oil absorbs in seconds, leaving nothing behind but soft skin and the faintest golden shimmer, like your skin caught the last good light of the day. Wear it alone or over lotion for extra glow.",
      howToUse: ["Smooth over damp or dry skin.", "Focus on collarbones, shoulders, and shins for maximum glow.", "Reapply as desired throughout the evening."]
    },
    {
      id: 20, name: "Vanity Hand Cream Trio", category: "body", art: "jar",
      price: 36, rating: 4.9, reviewCount: 96,
      type: "Hand Cream Set", finish: "Rich, fast-absorbing",
      bestFor: "Dry hands & cuticles", keyIngredients: "Shea Butter, Glycerin, Rosehip Oil",
      description: "Three rich hand creams, dressed for your handbag and your vanity.",
      details: "A trio of fast-absorbing hand creams in three signature scents, each rich enough to soothe the driest hands without ever leaving a greasy film. Beautiful enough to leave out, small enough to carry everywhere.",
      howToUse: ["Massage a small amount into hands and cuticles as needed.", "Reapply after washing hands.", "Keep one in your bag, one by the sink, one on your desk."]
    },
    {
      id: 21, name: "Lumière Eau de Parfum", category: "fragrance", art: "perfume",
      price: 98, rating: 4.9, reviewCount: 387, badge: "Bestseller",
      type: "Eau de Parfum", finish: "Warm, woody floral",
      bestFor: "Signature everyday scent", keyIngredients: "Jasmine, Sandalwood, Amber",
      description: "Our signature scent, warm jasmine and sandalwood worn close to skin.",
      details: "The scent the entire brand is named for: jasmine and white florals open into a warm heart of sandalwood and soft amber. Long-wearing and never overwhelming, it's the kind of fragrance people lean in to ask about.",
      howToUse: ["Spray onto pulse points: wrists, neck, and collarbone.", "Avoid rubbing wrists together to preserve the scent's development.", "Reapply after 6–8 hours for all-day wear."],
      sizes: [{ label: "30ml", delta: 0 }, { label: "50ml", delta: 24 }, { label: "100ml", delta: 46 }]
    },
    {
      id: 22, name: "Pétale Rollerball Set", category: "fragrance", art: "perfume",
      price: 54, rating: 4.7, reviewCount: 142,
      type: "Travel Rollerball Trio", finish: "Three wearable concentrations",
      bestFor: "Travel & layering", keyIngredients: "Rose, Bergamot, Musk",
      description: "Three travel-size rollerballs, perfect for layering or gifting.",
      details: "A trio of rollerball fragrances, rose, bergamot, and soft musk, sized for carry-on bags and bedside tables alike. Wear one alone or layer all three for a scent that's entirely your own.",
      howToUse: ["Roll directly onto pulse points.", "Layer scents for a custom blend.", "Carry in your bag for touch-ups on the go."]
    },
    {
      id: 23, name: "Velvet Bloom Hair Mist", category: "fragrance", art: "pump",
      price: 36, rating: 4.6, reviewCount: 108,
      type: "Hair & Body Mist", finish: "Light, fine veil",
      bestFor: "A soft scent without overwhelming", keyIngredients: "Peony, White Musk, Vitamin E",
      description: "A featherlight mist that perfumes hair without weighing it down.",
      details: "Formulated to be lighter than a traditional perfume, this mist settles into hair as a soft peony-and-musk veil, close enough to notice, never overwhelming. Safe to mist directly over styled hair.",
      howToUse: ["Hold 12 inches from hair and mist lightly.", "Avoid spraying directly onto roots.", "Reapply as desired throughout the day."]
    },
    {
      id: 24, name: "Nuit Blanche Eau de Parfum", category: "fragrance", art: "perfume",
      price: 98, rating: 4.8, reviewCount: 79, badge: "New",
      type: "Eau de Parfum", finish: "Dark, smoky vanilla",
      bestFor: "Evening wear & special occasions", keyIngredients: "Vanilla, Black Pepper, Oud",
      description: "A smoky vanilla parfum built for long nights and longer goodbyes.",
      details: "Built for the hours after sunset: dark vanilla and oud warmed by a flash of black pepper. It sits close to the skin, deepens over time, and tends to linger in the best possible way.",
      howToUse: ["Spray onto pulse points 30 minutes before heading out.", "Layer with the matching body oil for a richer trail.", "One spray is plenty, let it develop before adding more."],
      sizes: [{ label: "30ml", delta: 0 }, { label: "50ml", delta: 24 }]
    }
  ];

  /* ---------- Review pool (sampled per-product, see getReviews) ---------- */
  LM.REVIEW_POOL = [
    { author: "Sophia L.",  location: "Paris",     text: "The texture alone is worth it, it sinks in immediately and never feels heavy. This has fully replaced three other products in my routine." },
    { author: "Amara T.",   location: "London",    text: "I've already repurchased this twice. My skin looks calmer and so much more even after just a few weeks." },
    { author: "Chloé M.",   location: "Tunis",     text: "Packaging this beautiful makes me want to leave it out on my vanity, but the formula is even better than the bottle suggests." },
    { author: "Yasmine B.", location: "Tunis",     text: "Shipping was fast and the product arrived perfectly packaged. It's become a genuine staple, not just a pretty face on the shelf." },
    { author: "Inès D.",    location: "Marseille", text: "A little goes such a long way. I was skeptical about the price at first but I'm now a full convert." },
    { author: "Hana R.",    location: "Dubai",     text: "This is the first product in years that's made my partner ask what I'm wearing. Worth every cent." },
    { author: "Camille F.", location: "Lyon",      text: "Subtle, elegant, and it lasts the whole day without needing a single touch-up. Exactly what I look for." },
    { author: "Leila K.",   location: "Tunis",     text: "I have sensitive skin and reacted to nothing, soft, comfortable, and genuinely effective from the first use." },
    { author: "Marion P.",  location: "Brussels",  text: "Customer service was lovely when I had a question, and the product itself exceeded what I expected." },
    { author: "Nora S.",    location: "Geneva",    text: "Three friends have asked me about this since I started using it. I've basically become an unpaid spokesperson at this point." },
    { author: "Élise V.",   location: "Paris",     text: "The kind of small daily luxury that makes the whole routine feel a little more special. I look forward to using it." },
    { author: "Salma A.",   location: "Tunis",     text: "Refined, understated, and clearly made by people who actually use what they sell. It shows in every detail." }
  ];

  /* ---------- Helpers ---------- */
  LM.formatPrice = function (n) {
    return "$" + Number(n).toFixed(2);
  };

  LM.getProduct = function (id) {
    id = Number(id);
    return LM.PRODUCTS.find(function (p) { return p.id === id; });
  };

  LM.getProductsByCategory = function (catId) {
    return LM.PRODUCTS.filter(function (p) { return p.category === catId; });
  };

  LM.getRelatedProducts = function (product, count) {
    count = count || 4;
    var sameCat = LM.PRODUCTS.filter(function (p) { return p.category === product.category && p.id !== product.id; });
    if (sameCat.length < count) {
      var others = LM.PRODUCTS.filter(function (p) { return p.category !== product.category; });
      sameCat = sameCat.concat(others.slice(0, count - sameCat.length));
    }
    return sameCat.slice(0, count);
  };

  LM.getReviewsForProduct = function (id, count) {
    count = count || 2;
    var pool = LM.REVIEW_POOL;
    var out = [];
    for (var i = 0; i < count; i++) {
      out.push(pool[(id * 3 + i * 5) % pool.length]);
    }
    return out;
  };

  LM.getMinMaxPrice = function () {
    var prices = LM.PRODUCTS.map(function (p) { return p.price; });
    return { min: 0, max: Math.ceil(Math.max.apply(null, prices) / 10) * 10 };
  };
})();