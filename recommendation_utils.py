import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def get_product_recommendation(user_query):
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")

        system_instruction = """You are TACX Product Recommendation AI, an expert assistant for The Ayurveda Co. (TACX) WhatsApp bot. Your job is to intelligently suggest product links, combo options, and offers — but only when a product is actually recommended during the chat, not randomly or repetitively.

🧠 Core Responsibilities:

🔗 Product URL Recommendation:
When a product is mentioned or suggested in chat (e.g., “Kumkumadi oil”, “Hair Growth Serum”), respond with the correct product URL from the provided urldata.
🧴 Combo Suggestion (Only when applicable):
If the recommended product has a combo or is part of a bundle, suggest that combo's URL along with a short benefit summary.
🎁 Offer Notification (Only at time of recommendation):
Show any available offers/discounts related to the product or combo only when that product is being recommended.
🚫 Do Not Repeat:
Avoid suggesting products, combos, or offers again in the same session unless the user asks again explicitly.

Input Data: urldata-{
    "Upto 20% Off!": {
        "url": "https://theayurvedaco.com/collections/all-products-onsite"
    },
    "Additional 7% Off on All Prepaid Orders!": {
        "url": "https://theayurvedaco.com/collections/all-products-onsite"
    },
    "Combos": {
        "url": "https://theayurvedaco.com/collections/combo"
    },
    "Eladi Sunscreen SPF 50 (Pack of 2)Hot Movers": {
        "url": "https://theayurvedaco.com/products/sunscreen-spf-50-pa-for-uva-uvb-sun-protection-with-eladi-neem-pack-of-2-100g"
    },
    "Eladi Sunscreen SPF 50 (Pack of 2)": {
        "url": "https://theayurvedaco.com/products/sunscreen-spf-50-pa-for-uva-uvb-sun-protection-with-eladi-neem-pack-of-2-100g"
    },
    "Eladi Sunscreen SPF 50 MiniSale": {
        "url": "https://theayurvedaco.com/products/eladi-sunscreen-spf-50-mini-retail"
    },
    "Eladi Triple Action RegimeSale": {
        "url": "https://theayurvedaco.com/products/eladi-triple-action-regime"
    },
    "Festive Shringaar SetSale": {
        "url": "https://theayurvedaco.com/products/festive-shringaar-set-5"
    },
    "Firming & Repairing Face SerumSale": {
        "url": "https://theayurvedaco.com/products/firm-repair-face-serum-ashwagandha-bakuchiol"
    },
    "Glow Together BundleSale": {
        "url": "https://theayurvedaco.com/products/glow-together-bundle"
    },
    "Hair Care Combo with Mighty BhringrajSale": {
        "url": "https://theayurvedaco.com/products/hair-care-combo-with-mighty-bhringraj"
    },
    "Harmony DeodorantSale": {
        "url": "https://theayurvedaco.com/products/harmony-deodorant-1-diy"
    },
    "HER - Elemental Luxury Perfume SetHot Movers": {
        "url": "https://theayurvedaco.com/products/her-elemental-luxury-perfume-set"
    },
    "Hibiscus Hair SerumSold out": {
        "url": "https://theayurvedaco.com/products/hibiscus-hair-serum-retail"
    },
    "HIM - Elemental Luxury Perfume SetSale": {
        "url": "https://theayurvedaco.com/products/him-elemental-luxury-perfume-set"
    },
    "Hot Pink Pie Lip, Cheek & Eye TintSale": {
        "url": "https://theayurvedaco.com/products/hot-pink-pie-lip-cheek-tint"
    },
    "Indian Rose Body Lotion (Pack of 2)Winter Essentials": {
        "url": "https://theayurvedaco.com/products/indian-rose-body-lotion-pack-of-2"
    },
    "Indian Rose Body Lotion (Pack of 2)": {
        "url": "https://theayurvedaco.com/products/indian-rose-body-lotion-pack-of-2"
    },
    "Intense Hydration Face SerumSale": {
        "url": "https://theayurvedaco.com/products/hydration-quench-face-serum-honey-aloe-vera"
    },
    "Intimate Brightening SerumSale": {
        "url": "https://theayurvedaco.com/products/intimate-brightening-serum"
    },
    "Kumkumadi Cleansing MilkSale": {
        "url": "https://theayurvedaco.com/products/kumkumadi-cleansing-milk"
    },
    "Kumkumadi Complete Care RegimeSale": {
        "url": "https://theayurvedaco.com/products/kumkumadi-complete-care-regime"
    },
    "Kumkumadi Daily Glow ComboSold out": {
        "url": "https://theayurvedaco.com/products/combo-of-kumkumadi-sunscreen-spf-50-pa-and-kumkumadi-face-wash-with-24k-gold-dust"
    },
    "Kumkumadi Daily Glow Combo": {
        "url": "https://theayurvedaco.com/products/combo-of-kumkumadi-sunscreen-spf-50-pa-and-kumkumadi-face-wash-with-24k-gold-dust"
    },
    "Kumkumadi Day Cream and Night Gel ComboSold out": {
        "url": "https://theayurvedaco.com/products/combo-of-10-kumkumadi-day-cream-with-spf-20-and-10-kumkumadi-night-gel"
    },
    "Kumkumadi Day Cream and Night Gel Combo": {
        "url": "https://theayurvedaco.com/products/combo-of-10-kumkumadi-day-cream-with-spf-20-and-10-kumkumadi-night-gel"
    },
    "10% Kumkumadi Day Cream with SPF 20 and Night Gel for Glowing Skin": {
        "url": "https://theayurvedaco.com/products/combo-of-10-kumkumadi-day-cream-with-spf-20-and-10-kumkumadi-night-gel"
    },
    "Kumkumadi Festive Glow KitSale": {
        "url": "https://theayurvedaco.com/products/kumkumadi-face-wash-kumkumadi-face-scrub-kumkumadi-sheet-mask"
    },
    "Kumkumadi Festive Glow Kit": {
        "url": "https://theayurvedaco.com/products/kumkumadi-face-wash-kumkumadi-face-scrub-kumkumadi-sheet-mask"
    },
  "Kumkumadi Gold Glow ComboSale": {
    "url": "https://theayurvedaco.com/products/combo-of-kumkumadi-face-wash-and-kumkumadi-face-scrub"
  },
  "Kumkumadi Gold Glow Combo": {
    "url": "https://theayurvedaco.com/products/combo-of-kumkumadi-face-wash-and-kumkumadi-face-scrub"
  },
  "Kumkumadi Gold Glow Facial KitWinter Essentials": {
    "url": "https://theayurvedaco.com/products/kumkumadi-gold-glow-facial-kit"
  },
  "Kumkumadi Gold Glow Facial Kit": {
    "url": "https://theayurvedaco.com/products/kumkumadi-gold-glow-facial-kit-retail"
  },
  "Kumkumadi Gold Glow Facial KitSale": {
    "url": "https://theayurvedaco.com/products/kumkumadi-gold-glow-facial-kit-retail"
  },
  "Kumkumadi Gold Glow Facial Kit (Set of 4)Sale": {
    "url": "https://theayurvedaco.com/products/kumkumadi-gold-glow-facial-kit-set-of-4-diy"
  },
  "Kumkumadi Gold Glow Facial Kit (Set of 4)": {
    "url": "https://theayurvedaco.com/products/kumkumadi-gold-glow-facial-kit-set-of-4-diy"
  },
  "Kumkumadi Radiance KitSale": {
    "url": "https://theayurvedaco.com/products/kumkumadi-radiance-kit"
  },
  "Kumkumadi Radiance Kit": {
    "url": "https://theayurvedaco.com/products/kumkumadi-radiance-kit"
  },
  "Kumkumadi Radiant Glow DuoSold out": {
    "url": "https://theayurvedaco.com/products/radiant-glow-duo"
  },
  "Kumkumadi Radiant Glow Duo": {
    "url": "https://theayurvedaco.com/products/radiant-glow-duo"
  },
  "Kumkumadi Sunscreen With SPF 50 (Pack of 2)Hot Movers": {
    "url": "https://theayurvedaco.com/products/kumkumadi-sunscreen-with-spf-50-pack-of-2"
  },
  "Kumkumadi Sunscreen With SPF 50 (Pack of 2)": {
    "url": "https://theayurvedaco.com/products/kumkumadi-sunscreen-with-spf-50-pack-of-2"
  },
  "Lady Lilac Liquid Lipstick (Pack of 2)Sold out": {
    "url": "https://theayurvedaco.com/products/lady-lilac-liquid-lipstick-5ml-pack-of-2-diy"
  },
  "Lady Lilac Liquid Lipstick (Pack of 2)": {
    "url": "https://theayurvedaco.com/products/lady-lilac-liquid-lipstick-5ml-pack-of-2-diy"
  },
  "Luxury Perfume Set of 2- Spicy Truth & Forbidden RomanceHot Movers": {
    "url": "https://theayurvedaco.com/products/luxury-perfume-set-of-2-spicy-truth-forbidden-romance-sls"
  },
  "Luxury Perfume Set of 2- Spicy Truth & Forbidden Romance": {
    "url": "https://theayurvedaco.com/products/luxury-perfume-set-of-2-spicy-truth-forbidden-romance-diy"
  },
  "Luxury Perfume Set of 2- Spicy Truth & Forbidden RomanceSold out": {
    "url": "https://theayurvedaco.com/products/luxury-perfume-set-of-2-spicy-truth-forbidden-romance-diy"
  },
  "Maroon Fantasy Liquid Lipstick (Pack of 2)Sold out": {
    "url": "https://theayurvedaco.com/products/maroon-fantasy-liquid-lipstick-5ml-pack-of-2-diy"
  },
  "Maroon Fantasy Liquid Lipstick (Pack of 2)": {
    "url": "https://theayurvedaco.com/products/maroon-fantasy-liquid-lipstick-5ml-pack-of-2-diy"
  },
  "Methi Anti-dandruff KitSold out": {
    "url": "https://theayurvedaco.com/products/miraculous-haircare-treatment-for-damaged-hair"
  },
  "Methi Anti-dandruff Kit": {
    "url": "https://theayurvedaco.com/products/miraculous-haircare-treatment-for-damaged-hair"
  },
  "Methi Hair Care Kit: Shampoo, Oil and Mask": {
    "url": "https://theayurvedaco.com/products/miraculous-haircare-treatment-for-damaged-hair"
  },
  "Methi Anti-Dandruff RegimeSale": {
    "url": "https://theayurvedaco.com/products/methi-hair-oil-shampoo-anti-dandruff-combo"
  },
  "Methi Anti-Dandruff Regime": {
    "url": "https://theayurvedaco.com/products/methi-hair-oil-shampoo-anti-dandruff-combo"
  },
  "Miss Red Liquid Lipstick (Pack of 2)Sold out": {
    "url": "https://theayurvedaco.com/products/miss-red-liquid-lipstick-5ml-pack-of-2-diy"
  },
  "Miss Red Liquid Lipstick (Pack of 2)": {
    "url": "https://theayurvedaco.com/products/miss-red-liquid-lipstick-5ml-pack-of-2-diy"
  },
  "Nude Elude Liquid Lipstick (Pack of 2)Sale": {
    "url": "https://theayurvedaco.com/products/nude-elude-liquid-lipstick-pack-of-2"
  },
  "Nude Elude Liquid Lipstick (Pack of 2)": {
    "url": "https://theayurvedaco.com/products/nude-elude-liquid-lipstick-pack-of-2"
  },
    "Onion Hair Regrowth ComboSale": {
        "url": "https://theayurvedaco.com/products/onion-shampoo-hair-oil-combo-hair-fall-control"
    },
    "Onion Hair Regrowth Combo": {
        "url": "https://theayurvedaco.com/products/onion-shampoo-hair-oil-combo-hair-fall-control"
    },
    "Ayurvedic Hair Oil and Shampoo for Hair Fall Control": {
        "url": "https://theayurvedaco.com/products/onion-shampoo-hair-oil-combo-hair-fall-control"
    },
    "Oudh Roll-On Deo (Pack of 2)Sale": {
        "url": "https://theayurvedaco.com/products/oudh-roll-on-deo-pack-of-3"
    },
    "Oudh Roll-On Deo (Pack of 2)": {
        "url": "https://theayurvedaco.com/products/oudh-roll-on-deo-pack-of-3"
    },
    "Oudh Roll-On Deo and Whitening Underarm SerumSale": {
        "url": "https://theayurvedaco.com/products/oudh-roll-on-deo-and-whitening-underarm-serum"
    },
    "Oudh Roll-On Deo and Whitening Underarm Serum": {
        "url": "https://theayurvedaco.com/products/oudh-roll-on-deo-and-whitening-underarm-serum"
    },
    "Long Lasting Freshness Roll-On Deo": {
        "url": "https://theayurvedaco.com/products/oudh-roll-on-deo-and-whitening-underarm-serum"
    },
    "Peach Nude Lip, Cheek & Eye Tint (Pack of 2)Sold out": {
        "url": "https://theayurvedaco.com/products/peach-nude-lip-cheek-eye-tint-pack-of-2"
    },
    "Peach Nude Lip, Cheek & Eye Tint (Pack of 2)": {
        "url": "https://theayurvedaco.com/products/peach-nude-lip-cheek-eye-tint-pack-of-2"
    },
    "Pink Flatter Liquid Lipstick (Pack of 2)Sale": {
        "url": "https://theayurvedaco.com/products/pink-flatter-liquid-lipstick-5ml-pack-of-2-diy"
    },
    "Pink Flatter Liquid Lipstick (Pack of 2)": {
        "url": "https://theayurvedaco.com/products/pink-flatter-liquid-lipstick-5ml-pack-of-2-diy"
    },
    "Purify & Nourish ComboSold out": {
        "url": "https://theayurvedaco.com/products/purify-nourish-combo"
    },
    "Purify & Nourish Combo": {
        "url": "https://theayurvedaco.com/products/purify-nourish-combo"
    },
    "Kumkumadi Face Wash & Gold Glow Face Oil | Reduces Dullness & Pigmentation": {
        "url": "https://theayurvedaco.com/products/purify-nourish-combo"
    },
    "Radiant Shield ComboSold out": {
        "url": "https://theayurvedaco.com/products/radiant-shield-combo"
    },
    "Radiant Shield Combo": {
        "url": "https://theayurvedaco.com/products/radiant-shield-combo"
    },
    "Kumkumadi Sunscreen & Glow Boosting Face Serum | Fights Dullness & Tanning": {
        "url": "https://theayurvedaco.com/products/radiant-shield-combo"
    },
    "TAC Essentials Gift Box: A Treasure of Ayurveda for Radiant SkinSale": {
        "url": "https://theayurvedaco.com/products/tac-essentials-gift-box-a-treasure-of-ayurveda-for-radiant-skin"
    },
    "TAC Essentials Gift Box: A Treasure of Ayurveda for Radiant Skin": {
        "url": "https://theayurvedaco.com/products/tac-essentials-gift-box-a-treasure-of-ayurveda-for-radiant-skin"
    },
    "Ubtan Soap (Pack of 3)Sold out": {
        "url": "https://theayurvedaco.com/products/ubtan-soap-pack-of-3"
    },
    "Ubtan Soap (Pack of 3)": {
        "url": "https://theayurvedaco.com/products/ubtan-soap-pack-of-3"
    },
    "Velvet Mauve Liquid Lipstick (Pack of 2)Sale": {
        "url": "https://theayurvedaco.com/products/velvet-mauve-liquid-lipstick-5ml-diy"
    },
    "Velvet Mauve Liquid Lipstick (Pack of 2)": {
        "url": "https://theayurvedaco.com/products/velvet-mauve-liquid-lipstick-5ml-diy"
    },
    "Vitamin C Brightening ComboSold out": {
        "url": "https://theayurvedaco.com/products/vitamin-c-brightening-combo"
    },
    "Vitamin C Brightening Combo": {
        "url": "https://theayurvedaco.com/products/vitamin-c-brightening-combo"
    },
    "Vitamin C Serum Sheet Mask (Pack of 3)Sale": {
        "url": "https://theayurvedaco.com/products/vitamin-c-serum-sheet-mask"
    },
    "Vitamin C Serum Sheet Mask (Pack of 3)": {
        "url": "https://theayurvedaco.com/products/vitamin-c-serum-sheet-mask"
    },
  "10% Vitamin C Face Serum (Pack of 2)Sale": {
    "url": "https://theayurvedaco.com/products/10-natural-vitamin-c-face-serum-for-glowing-skin-with-1-hyaluronic-acid-for-anti-aging-pack-2-x-30ml"
  },
  "10% Vitamin C Face Serum (Pack of 2)": {
    "url": "https://theayurvedaco.com/products/10-natural-vitamin-c-face-serum-for-glowing-skin-with-1-hyaluronic-acid-for-anti-aging-pack-2-x-30ml"
  },
  "AyurJosh Shilajit Resin (Pack of 2)Sale": {
    "url": "https://theayurvedaco.com/products/100-natural-pure-shilajit-resin-for-improving-immunity-metabolism-stamina-pack-of-2"
  },
  "AyurJosh Shilajit Resin (Pack of 2)": {
    "url": "https://theayurvedaco.com/products/100-natural-pure-shilajit-resin-for-improving-immunity-metabolism-stamina-pack-of-2"
  },
  "Beautif-Eye Ayurvedic Black Kajal (Pack of 2)Sale": {
    "url": "https://theayurvedaco.com/products/beautif-eye-ayurvedic-black-kajal-pack-of-2-diy"
  },
  "Beautif-Eye Ayurvedic Black Kajal (Pack of 2)": {
    "url": "https://theayurvedaco.com/products/beautif-eye-ayurvedic-black-kajal-pack-of-2-diy"
  },
  "Beautif-Eye Ayurvedic Black Kajal (Pack of 3)Sale": {
    "url": "https://theayurvedaco.com/products/beautif-eye-ayurvedic-black-kajal-pack-of-3"
  },
  "Beautif-Eye Ayurvedic Black Kajal (Pack of 3)": {
    "url": "https://theayurvedaco.com/products/beautif-eye-ayurvedic-black-kajal-pack-of-3"
  },
  "Anti Acne Day Cream (Pack of 2)Sale": {
    "url": "https://theayurvedaco.com/products/anti-acne-day-cream-pack-of-2"
  },
  "Anti Acne Day Cream (Pack of 2)": {
    "url": "https://theayurvedaco.com/products/anti-acne-day-cream-pack-of-2"
  },
  "Ayurglow Brightening Cream 50gm (Pack of 2)Sale": {
    "url": "https://theayurvedaco.com/products/ayurglow-brightening-cream-50gm-1-diy"
  },
  "Ayurglow Brightening Cream 50gm (Pack of 2)": {
    "url": "https://theayurvedaco.com/products/ayurglow-brightening-cream-50gm-1-diy"
  },
  "Beetroot Lip Butter & Lip Scrub ComboSale": {
    "url": "https://theayurvedaco.com/products/beetroot-lip-butter-balm-lip-scrub-combo"
  },
  "Beetroot Lip Butter & Lip Scrub Combo": {
    "url": "https://theayurvedaco.com/products/beetroot-lip-butter-balm-lip-scrub-combo"
  },
  "Bright & Beautiful Lips Combo": {
    "url": "https://theayurvedaco.com/products/beetroot-lip-butter-balm-lip-scrub-combo"
  },
  "Pigmentation & Dullness": {
        "url": "https://theayurvedaco.com/collections/pigmentation-and-dullness"
    },
    "Acne & Spots": {
        "url": "https://theayurvedaco.com/collections/acne-and-spots"
    },
    "Sun Protection": {
        "url": "https://theayurvedaco.com/collections/sun-protection"
    },
    "Hair Fall": {
        "url": "https://theayurvedaco.com/collections/hair-fall"
    },
    "Dandruff & Flakiness": {
        "url": "https://theayurvedaco.com/collections/dandruff-and-flakiness"
    },
    "Hair Growth": {
        "url": "https://theayurvedaco.com/collections/hair-growth"
    },
    "Dullness": {
        "url": "https://theayurvedaco.com/collections/dullness"
    },
    "Dark Underarms & Odour": {
        "url": "https://theayurvedaco.com/collections/dark-underarms-and-odour"
    },
    "Fatigue & Low Vitality": {
        "url": "https://theayurvedaco.com/collections/fatigue-and-low-vitality"
    },
    "Personal Health": {
        "url": "https://theayurvedaco.com/collections/personal-health"
    },
    "Face Wash": {
        "url": "https://theayurvedaco.com/collections/face-wash"
    },
    "Face Serum": {
        "url": "https://theayurvedaco.com/collections/face-serum"
    },
    "Moisturisers and Face Creams": {
        "url": "https://theayurvedaco.com/collections/moisturisers-and-face-creams"
    },
    "Sheet Masks": {
        "url": "https://theayurvedaco.com/collections/sheet-masks"
    },
    "Face Polishers": {
        "url": "https://theayurvedaco.com/collections/face-polishers"
    },
    "Hair Oils": {
        "url": "https://theayurvedaco.com/collections/hair-oils"
    },
    "Shampoo": {
        "url": "https://theayurvedaco.com/collections/shampoo"
    },
    "Conditioner": {
        "url": "https://theayurvedaco.com/collections/conditioner"
    },
    "Lip Balms and Butters": {
        "url": "https://theayurvedaco.com/collections/lip-balms-and-butters"
    },
    "Lip Scrub": {
        "url": "https://theayurvedaco.com/collections/lip-scrubs"
    },
    "Body Lotions": {
        "url": "https://theayurvedaco.com/collections/body-lotions"
    },
    "Underarm Roll Ons": {
        "url": "https://theayurvedaco.com/collections/dark-underarms-and-odour"
    },
    "Body Mists": {
        "url": "https://theayurvedaco.com/collections/body-mists"
    },
    "Fragrances": {
        "url": "https://theayurvedaco.com/collections/fragrances"
    },
    "Wellness": {
        "url": "https://theayurvedaco.com/collections/wellness"
    },
    "Lip & Cheek Tint": {
        "url": "https://theayurvedaco.com/collections/lip-cheek-tint"
    },
    "Liquid Lipstick": {
        "url": "https://theayurvedaco.com/collections/liquid-lipsticks"
    },
    "Kajal": {
        "url": "https://theayurvedaco.com/products/beautif-eye-ayurvedic-black-kajal"
    },
    "Face": {
        "url": "https://theayurvedaco.com/collections/face-care"
    },
    "Hair": {
        "url": "https://theayurvedaco.com/collections/hair-care"
    },
    "Body": {
        "url": "https://theayurvedaco.com/collections/bath-and-body"
    },
    "Lip Care": {
        "url": "https://theayurvedaco.com/collections/lip-care"
    },
    "Make Up": {
        "url": "https://theayurvedaco.com/collections/natural-makeup"
    },
    "Cart": {
        "url": "https://theayurvedaco.com/cart"
    },
    "With Eladi & Neem | Reduces Tan & Combats Acne": {
        "url": "https://theayurvedaco.com/products/sunscreen-spf-50-pa-for-uva-uvb-sun-protection-with-eladi-neem-pack-of-2-100g"
    },
    "Eladi Sunscreen SPF 50 Mini": {
        "url": "https://theayurvedaco.com/products/eladi-sunscreen-spf-50-mini-retail"
    },
    "Sunscreen SPF 50 with Neem for Protection from UVA UVB Ray": {
        "url": "https://theayurvedaco.com/products/eladi-sunscreen-spf-50-mini-retail"
    },
    "Eladi Triple Action Regime": {
        "url": "https://theayurvedaco.com/products/eladi-triple-action-regime"
    },
    "Eladi Face Wash, Acne & Spot Correction Face Serum & Sunscreen | Combats Acne & Spots": {
        "url": "https://theayurvedaco.com/products/eladi-triple-action-regime"
    },
    "Festive Shringaar Set": {
        "url": "https://theayurvedaco.com/products/festive-shringaar-set-5"
    },
    "Firming & Repairing Face Serum": {
        "url": "https://theayurvedaco.com/products/firm-repair-face-serum-ashwagandha-bakuchiol"
    },
    "with Ashwagandha & Bakuchiol | Fights Signs of Ageing": {
        "url": "https://theayurvedaco.com/products/firm-repair-face-serum-ashwagandha-bakuchiol"
    },
    "Glow Together Bundle": {
        "url": "https://theayurvedaco.com/products/glow-together-bundle"
    },
    "Hair Care Combo with Mighty Bhringraj": {
        "url": "https://theayurvedaco.com/products/hair-care-combo-with-mighty-bhringraj"
    },
    "Harmony Deodorant": {
        "url": "https://theayurvedaco.com/products/harmony-deodorant-1-diy"
    },
    "HER - Elemental Luxury Perfume Set": {
        "url": "https://theayurvedaco.com/products/her-elemental-luxury-perfume-set"
    },
    "Mystical Fragrances to Make a Statement": {
        "url": "https://theayurvedaco.com/products/him-elemental-luxury-perfume-set"
    },
    "Hibiscus Hair Serum": {
        "url": "https://theayurvedaco.com/products/hibiscus-hair-serum-retail"
    },
    "With Moringa & Brahmi For Dry & Rough Hair": {
        "url": "https://theayurvedaco.com/products/hibiscus-hair-serum-retail"
    },
    "HIM - Elemental Luxury Perfume Set": {
        "url": "https://theayurvedaco.com/products/him-elemental-luxury-perfume-set"
    },
    "Hot Pink Pie Lip, Cheek & Eye Tint": {
        "url": "https://theayurvedaco.com/products/hot-pink-pie-lip-cheek-tint"
    },
    "Organic Lip and Cheek Tint for Pink Lip and Dry Skin": {
        "url": "https://theayurvedaco.com/products/hot-pink-pie-lip-cheek-tint"
    },
    "Indian Rose Body Lotion": {
        "url": "https://theayurvedaco.com/products/indian-rose-body-lotion-diy"
    },
    "with Milk Protein | For Hydrated & Refreshed Skin": {
        "url": "https://theayurvedaco.com/products/indian-rose-body-lotion-pack-of-2"
    },
    "Indian Rose Body LotionWinter Essentials": {
        "url": "https://theayurvedaco.com/products/indian-rose-body-lotion-diy"
    },
    "Indian Rose Body Lotion Mini": {
        "url": "https://theayurvedaco.com/products/indian-rose-body-lotion-mini-30ml"
    },
    "with Milk for Hydrating & Refreshing SKin": {
        "url": "https://theayurvedaco.com/products/indian-rose-body-lotion-mini-30ml"
    },
    "Indian Rose Lip Balm": {
        "url": "https://theayurvedaco.com/products/indian-rose-lip-balm-butter-dry-dark-lips-chapped-lips"
    },
    "Lip Balm for Dry, Dark & Chapped Lips": {
        "url": "https://theayurvedaco.com/products/indian-rose-lip-balm-butter-dry-dark-lips-chapped-lips"
    },
    "Intense Hydration Body Lotion with Aloe and Almond OilWinter Essentials": {
        "url": "https://theayurvedaco.com/products/intense-hydration-body-lotion-with-aloe-and-almond-oil-diy"
    },
    "Intense Hydration Body Lotion with Aloe and Almond Oil": {
        "url": "https://theayurvedaco.com/products/intense-hydration-body-lotion-with-aloe-and-almond-oil-diy"
    },
    "with Aloe & Almond Oil | For Long Lasting Hydration": {
        "url": "https://theayurvedaco.com/products/intense-hydration-body-lotion-with-aloe-and-almond-oil-250ml-diy"
    },
    "Intense Hydration Body Lotion with Aloe and Almond Oil, 100mlWinter Essentials": {
        "url": "https://theayurvedaco.com/products/intense-hydration-body-lotion-with-aloe-and-almond-oil-100ml-diy"
    },
    "Intense Hydration Body Lotion with Aloe and Almond Oil, 100ml": {
        "url": "https://theayurvedaco.com/products/intense-hydration-body-lotion-with-aloe-and-almond-oil-100ml-diy"
    },
    "Intense Hydration Body Lotion with Aloe and Almond Oil, 250mlWinter Essentials": {
        "url": "https://theayurvedaco.com/products/intense-hydration-body-lotion-with-aloe-and-almond-oil-250ml-diy"
    },
    "Intense Hydration Body Lotion with Aloe and Almond Oil, 250ml": {
        "url": "https://theayurvedaco.com/products/intense-hydration-body-lotion-with-aloe-and-almond-oil-250ml-diy"
    },
    "Intense Hydration Face Serum": {
        "url": "https://theayurvedaco.com/products/hydration-quench-face-serum-honey-aloe-vera"
    },
    "with Honey & Aloe Vera | Hydrates Skin & Retains Moisture": {
        "url": "https://theayurvedaco.com/products/hydration-quench-face-serum-honey-aloe-vera"
    },
    "Intimate Brightening Serum": {
        "url": "https://theayurvedaco.com/products/intimate-brightening-serum"
    },
    "Kumkumadi Aloevera GelHot Movers": {
        "url": "https://theayurvedaco.com/products/kumkumadi-aloevera-gel-glowinng-skin"
    },
    "Kumkumadi Aloevera Gel": {
        "url": "https://theayurvedaco.com/products/kumkumadi-aloevera-gel-glowinng-skin"
    },
    "with Saffron & 24K Gold | Moisturises & Nourishes Skin": {
        "url": "https://theayurvedaco.com/products/kumkumadi-aloevera-gel-glowinng-skin"
    },
    "Kumkumadi Body ButterWinter Essentials": {
        "url": "https://theayurvedaco.com/products/kumkumadi-body-butter"
    },
    "Kumkumadi Body Butter": {
        "url": "https://theayurvedaco.com/products/kumkumadi-body-butter"
    },
    "with Saffron & Shea Butter | Nourishes Skin & Locks in Moisture": {
        "url": "https://theayurvedaco.com/products/kumkumadi-body-butter"
    },
    "Kumkumadi Body Lotion": {
        "url": "https://theayurvedaco.com/products/kumkumadi-body-lotion-diy"
    },
    "with Saffron & Turmeric | For Radiant & Youthful Skin": {
        "url": "https://theayurvedaco.com/products/kumkumadi-body-lotion-diy"
    },
    "Kumkumadi Body LotionWinter Essentials": {
        "url": "https://theayurvedaco.com/products/kumkumadi-body-lotion-diy"
    },
    "Kumkumadi Cleansing Milk": {
        "url": "https://theayurvedaco.com/products/kumkumadi-cleansing-milk"
    },
    "Cleanses dirt, impurities & makeup Residues": {
        "url": "https://theayurvedaco.com/products/kumkumadi-cleansing-milk"
    },
    "Kumkumadi Complete Care Regime": {
        "url": "https://theayurvedaco.com/products/kumkumadi-complete-care-regime"
    },
    "Kumkumadi Face Wash, Face Serum, Moisturiser & Sunscreen | Reduce Dull Skin & Imparts Glow": {
        "url": "https://theayurvedaco.com/products/kumkumadi-complete-care-regime"
    },
    "Kumkumadi Day CreamBestseller": {
        "url": "https://theayurvedaco.com/products/kumkumadi-day-cream-spf-20-radiant-youthful-skin"
    },
    "Kumkumadi Day Cream": {
        "url": "https://theayurvedaco.com/products/kumkumadi-day-cream-spf-20-radiant-youthful-skin"
    },
    "with Saffron & 24K Gold | Moisturises & Hydrates Skin": {
        "url": "https://theayurvedaco.com/products/kumkumadi-day-cream-spf-20-radiant-youthful-skin"
    },
    "Kumkumadi Face MoisturiserWinter Essentials": {
        "url": "https://theayurvedaco.com/products/kumkumadi-face-moisturiser"
    },
    "Kumkumadi Face Moisturiser": {
        "url": "https://theayurvedaco.com/products/kumkumadi-face-moisturiser"
    },
    "Saffron & 24K Gold | Hydrates & Nourishes Skin": {
        "url": "https://theayurvedaco.com/products/kumkumadi-face-moisturiser-20g-pack-of-3"
    },
    "Kumkumadi Face Moisturiser 20gSale": {
        "url": "https://theayurvedaco.com/products/kumkumadi-face-moisturiser-20g-diy"
    },
    "Kumkumadi Face Moisturiser 20g": {
        "url": "https://theayurvedaco.com/products/kumkumadi-face-moisturiser-20g-diy"
    },
    "Kumkumadi Face Moisturiser 20g (Pack of 2)Sale": {
        "url": "https://theayurvedaco.com/products/kumkumadi-face-moisturiser-20g-pack-of-2"
    },
    "Kumkumadi Face Moisturiser 20g (Pack of 2)": {
        "url": "https://theayurvedaco.com/products/kumkumadi-face-moisturiser-20g-pack-of-2"
    },
    "Kumkumadi Face Moisturiser 20g (Pack of 3)Sale": {
        "url": "https://theayurvedaco.com/products/kumkumadi-face-moisturiser-20g-pack-of-3"
    },
    "Kumkumadi Face Moisturiser 20g (Pack of 3)": {
        "url": "https://theayurvedaco.com/products/kumkumadi-face-moisturiser-20g-pack-of-3"
    },
    "Kumkumadi Face OilBestseller": {
        "url": "https://theayurvedaco.com/products/kumkumadi-face-oil-glowing-skin"
    },
    "Kumkumadi Face Oil": {
        "url": "https://theayurvedaco.com/products/kumkumadi-face-oil-glowing-skin"
    },
    "With Saffron & Sandalwood | Fades Pigmentation & Spots": {
        "url": "https://theayurvedaco.com/products/kumkumadi-face-oil-glowing-skin"
    },
    "Kumkumadi Face ScrubSale": {
        "url": "https://theayurvedaco.com/products/kumkumadi-face-scrub-diy"
    },
    "Kumkumadi Face Scrub": {
        "url": "https://theayurvedaco.com/products/kumkumadi-face-scrub-diy"
    },
    "with Saffron & 24K Gold | Exfoliates Skin & Imparts Glow": {
        "url": "https://theayurvedaco.com/products/kumkumadi-face-scrub-10gm"
    },
    "Kumkumadi Face Scrub 10gmSold out": {
        "url": "https://theayurvedaco.com/products/kumkumadi-face-scrub-10gm"
    },
    "Kumkumadi Face Scrub 10gm": {
        "url": "https://theayurvedaco.com/products/kumkumadi-face-scrub-10gm"
    },
    "Kumkumadi Face WashHot Movers": {
        "url": "https://theayurvedaco.com/products/kumkumadi-face-wash-radiant-youthful-oily-skin"
    },
    "Kumkumadi Face Wash": {
        "url": "https://theayurvedaco.com/products/kumkumadi-face-wash-radiant-youthful-oily-skin"
    },
    "Saffron & 24K Gold | Deeply Cleanses Skin": {
        "url": "https://theayurvedaco.com/products/kumkumadi-face-wash-radiant-youthful-oily-skin"
    },
    "Kumkumadi Face Wash, 50mlHot Movers": {
        "url": "https://theayurvedaco.com/products/kumkumadi-face-wash-50ml"
    },
    "Kumkumadi Face Wash, 50ml": {
        "url": "https://theayurvedaco.com/products/kumkumadi-face-wash-50ml"
    },
    "Face Wash for Radiant and Youthful Skin Brightening": {
        "url": "https://theayurvedaco.com/products/kumkumadi-face-wash-50ml"
    },
    "Kumkumadi Glow Boosting Face Serum": {
        "url": "https://theayurvedaco.com/products/glow-booster-face-serum-kumkumadi-with-saffron"
    },
    "Saffron & 24K Gold | Reduces Dullness & Pigmentation": {
        "url": "https://theayurvedaco.com/products/glow-booster-face-serum-kumkumadi-with-saffron"
    },
  "with Saffron & 24K Gold | Reduces Pigmentation & Dark Spots": {
    "url": "https://theayurvedaco.com/products/combo-of-kumkumadi-face-wash-and-kumkumadi-face-scrub"
  },
  "Kumkumadi Lip ScrubSold out": {
    "url": "https://theayurvedaco.com/products/kumkumadi-lip-scrub-15gm"
  },
  "Kumkumadi Lip Scrub": {
    "url": "https://theayurvedaco.com/products/kumkumadi-lip-scrub-15gm"
  },
  "Helps to Lightens & Smoothens Lips": {
    "url": "https://theayurvedaco.com/products/kumkumadi-lip-scrub-15gm"
  },
  "Kumkumadi Lip SerumSold out": {
    "url": "https://theayurvedaco.com/products/kumkumadi-lip-serum"
  },
  "Kumkumadi Lip Serum": {
    "url": "https://theayurvedaco.com/products/kumkumadi-lip-serum"
  },
  "with Saffron Softens & Lightens": {
    "url": "https://theayurvedaco.com/products/kumkumadi-lip-serum"
  },
  "Kumkumadi Night Gel MiniSold out": {
    "url": "https://theayurvedaco.com/products/kumkumadi-night-gel-5g"
  },
  "Kumkumadi Night Gel Mini": {
    "url": "https://theayurvedaco.com/products/kumkumadi-night-gel-5g"
  },
  "with Saffron & 24K Gold | Overnight Skin Replenishment": {
    "url": "https://theayurvedaco.com/products/kumkumadi-night-gel-5g"
  },
  "Kumkumadi Face Wash & Glow Boosting Face Serum": {
    "url": "https://theayurvedaco.com/products/kumkumadi-radiance-kit"
  },
  "Kumkumadi Face Moisturiser & Glow Boosting Face Serum": {
    "url": "https://theayurvedaco.com/products/radiant-glow-duo"
  },
  "Kumkumadi Serum Sheet Mask (Pack of 3)Sale": {
    "url": "https://theayurvedaco.com/products/kumkumadi-serum-sheet-mask"
  },
  "Kumkumadi Serum Sheet Mask (Pack of 3)": {
    "url": "https://theayurvedaco.com/products/kumkumadi-serum-sheet-mask"
  },
  "with Saffron & Manjistha | Hydrates Skin & Enhances Glow": {
    "url": "https://theayurvedaco.com/products/kumkumadi-serum-sheet-mask"
  },
  "Kumkumadi Soap (Pack of 3)Hot Movers": {
    "url": "https://theayurvedaco.com/products/kumkumadi-soap-pack-of-3"
  },
  "Kumkumadi Soap (Pack of 3)": {
    "url": "https://theayurvedaco.com/products/kumkumadi-soap-pack-of-3"
  },
  "for Radiant & Youthful Skin": {
    "url": "https://theayurvedaco.com/products/kumkumadi-soap-pack-of-3"
  },
  "Kumkumadi Sunscreen SPF 50Hot Movers": {
    "url": "https://theayurvedaco.com/products/kumkumadi-sunscreen-moisturizing-spf-50-uva-uvb-pa"
  },
  "Kumkumadi Sunscreen SPF 50": {
    "url": "https://theayurvedaco.com/products/kumkumadi-sunscreen-moisturizing-spf-50-uva-uvb-pa"
  },
  "With Saffron & Manjistha | Reduces Tan & Dullness": {
    "url": "https://theayurvedaco.com/products/kumkumadi-sunscreen-with-spf-50-pack-of-2"
  },
  "Kumkumadi Under Eye SerumSale": {
    "url": "https://theayurvedaco.com/products/kumkumadi-under-eye-serum-10ml"
  },
  "Kumkumadi Under Eye Serum": {
    "url": "https://theayurvedaco.com/products/kumkumadi-under-eye-serum-10ml"
  },
  "With Saffron Oil & Gotu Kola | Reduces Dark Circles & Puffy Eyes": {
    "url": "https://theayurvedaco.com/products/kumkumadi-under-eye-serum-10ml"
  },
  "Kumukumadi Gold Glow MoisturiserSold out": {
    "url": "https://theayurvedaco.com/products/kumukumadi-gold-glow-moisturiser"
  },
  "Kumukumadi Gold Glow Moisturiser": {
    "url": "https://theayurvedaco.com/products/kumukumadi-gold-glow-moisturiser"
  },
  "Lady Lilac Liquid LipstickSold out": {
    "url": "https://theayurvedaco.com/products/lady-lilac-liquid-lipstick"
  },
  "Lady Lilac Liquid Lipstick": {
    "url": "https://theayurvedaco.com/products/lady-lilac-liquid-lipstick"
  },
  "Matte Finish & Long-Lasting Impact": {
    "url": "https://theayurvedaco.com/products/nude-elude-liquid-lipstick-5ml-diy"
  },
  "Limitless DeodorantSale": {
    "url": "https://theayurvedaco.com/products/limitless-deodorant-1-diy"
  },
  "Limitless Deodorant": {
    "url": "https://theayurvedaco.com/products/limitless-deodorant-1-diy"
  },
  "Lip, Cheek & Eye Tint - MinisSale": {
    "url": "https://theayurvedaco.com/products/lip-cheek-eye-tint-minis"
  },
  "Lip, Cheek & Eye Tint - Minis": {
    "url": "https://theayurvedaco.com/products/lip-cheek-eye-tint-minis"
  },
  "Ayurvedic & Natural Lip Cheek Tint Shades for Healthy Skin Tone": {
    "url": "https://theayurvedaco.com/products/lip-cheek-eye-tint-minis"
  },
  "Liquid Lipsticks- Bold & Beautiful (Essential Browns & Reds)Sold out": {
    "url": "https://theayurvedaco.com/products/liquid-lipsticks-bold-beautiful-essential-browns-reds"
  },
    "Onion Hair ShampooSold out": {
        "url": "https://theayurvedaco.com/products/onion-hair-shampoo-for-hair-fall-control"
    },
    "Onion Hair Shampoo": {
        "url": "https://theayurvedaco.com/products/onion-hair-shampoo-for-hair-fall-control"
    },
    "Hair Fall Control Shampoo with Ginger for Healthy Hair & Scalp": {
        "url": "https://theayurvedaco.com/products/onion-hair-shampoo-for-hair-fall-control"
    },
    "Oudh & Green Tea Body MistSale": {
        "url": "https://theayurvedaco.com/products/oud-green-tea-body-mist"
    },
    "Oudh & Green Tea Body Mist": {
        "url": "https://theayurvedaco.com/products/oud-green-tea-body-mist"
    },
    "Oudh Roll-On DeoHot Movers": {
        "url": "https://theayurvedaco.com/products/roll-on-deo-men-oudh-aloe"
    },
    "Oudh Roll-On Deo": {
        "url": "https://theayurvedaco.com/products/roll-on-deo-men-oudh-aloe"
    },
    "Long Lasting Freshness Roll-On for Men": {
        "url": "https://theayurvedaco.com/products/oudh-roll-on-deo-pack-of-3"
    },
    "Passion DeodorantSale": {
        "url": "https://theayurvedaco.com/products/passion-deodorant-1-diy"
    },
    "Passion Deodorant": {
        "url": "https://theayurvedaco.com/products/passion-deodorant-1-diy"
    },
    "Peach Nude Lip, Cheek & Eye TintSale": {
        "url": "https://theayurvedaco.com/products/peach-nude-pink-lip-and-cheek-tint"
    },
    "Peach Nude Lip, Cheek & Eye Tint": {
        "url": "https://theayurvedaco.com/products/peach-nude-pink-lip-and-cheek-tint"
    },
    "Natural Lip and Cheek Tint for Bright, Moisturisation, and Soft Shade of Pink": {
        "url": "https://theayurvedaco.com/products/peach-nude-lip-cheek-eye-tint-pack-of-2"
    },
    "Pink Flatter Liquid LipstickSale": {
        "url": "https://theayurvedaco.com/products/pink-flatter-liquid-lipstick-5ml"
    },
    "Pink Flatter Liquid Lipstick": {
        "url": "https://theayurvedaco.com/products/pink-flatter-liquid-lipstick-5ml"
    },
    "Matte Finish & Long-Lasting Impact": {
        "url": "https://theayurvedaco.com/products/velvet-mauve-liquid-lipstick-5ml-diy"
    },
    "Pure Indian Rose WaterSale": {
        "url": "https://theayurvedaco.com/products/hydrating-rose-water-face-toning-natural-glowing-skin"
    },
    "Pure Indian Rose Water": {
        "url": "https://theayurvedaco.com/products/hydrating-rose-water-face-toning-natural-glowing-skin"
    },
    "Pure Indian Rose Water Toning & Hydrating": {
        "url": "https://theayurvedaco.com/products/hydrating-rose-water-face-toning-natural-glowing-skin"
    },
    "Retro Charmer PerfumeSale": {
        "url": "https://theayurvedaco.com/products/retro-charmer-perfume-20ml"
    },
    "Retro Charmer Perfume": {
        "url": "https://theayurvedaco.com/products/retro-charmer-perfume-20ml"
    },
    "EDP | Eau De Parfum | Citrusy & Earthy Hints": {
        "url": "https://theayurvedaco.com/products/retro-charmer-perfume-20ml"
    },
    "Retro Red Plum Lip, Cheek & Eye TintSale": {
        "url": "https://theayurvedaco.com/products/retro-red-plum-lip-cheek-tint"
    },
    "Retro Red Plum Lip, Cheek & Eye Tint": {
        "url": "https://theayurvedaco.com/products/retro-red-plum-lip-cheek-tint"
    },
    "Best Lip and Cheek Tint for Moisturising and Maintains a Healthy Texture": {
        "url": "https://theayurvedaco.com/products/retro-red-plum-lip-cheek-tint"
    },
    "Rose Roll-On Deo (Pack of 2)Sale": {
        "url": "https://theayurvedaco.com/products/rose-roll-on-deo-pack-of-2"
    },
    "Rose Roll-On Deo (Pack of 2)": {
        "url": "https://theayurvedaco.com/products/rose-roll-on-deo-pack-of-2"
    },
    "Long Lasting Freshness Roll-On for Women": {
        "url": "https://theayurvedaco.com/products/rose-roll-on-deo-pack-of-2"
    },
    "Rosemary Anti-Hair Fall ConditionerSale": {
        "url": "https://theayurvedaco.com/products/rosemary-anti-hair-fall-conditioner"
    },
    "Rosemary Anti-Hair Fall Conditioner": {
        "url": "https://theayurvedaco.com/products/rosemary-anti-hair-fall-conditioner"
    },
    "with Mint & Clove Oil | Combats Hair Fall": {
        "url": "https://theayurvedaco.com/products/rosemary-anti-hair-fall-conditioner"
    },
    "Rosemary Anti-Hair Fall Hair MaskSale": {
        "url": "https://theayurvedaco.com/products/rosemary-anti-hair-fall-hair-mask"
    },
    "Rosemary Anti-Hair Fall Hair Mask": {
        "url": "https://theayurvedaco.com/products/rosemary-anti-hair-fall-hair-mask"
    },
    "with Mint & Clove Oil | Nourishes Hair Strands": {
        "url": "https://theayurvedaco.com/products/rosemary-anti-hair-fall-hair-mask"
    },
    "Rosemary Anti-Hair Fall Hair OilSold out": {
        "url": "https://theayurvedaco.com/products/10-rosemary-anti-hair-fall-hair-oil"
    },
    "Rosemary Anti-Hair Fall Hair Oil": {
        "url": "https://theayurvedaco.com/products/10-rosemary-anti-hair-fall-hair-oil"
    },
    "Rosemary & Clove Oil | Controls Hair Fall | Strengthens Hair Roots": {
        "url": "https://theayurvedaco.com/products/10-rosemary-anti-hair-fall-hair-oil"
    },
    "Rosemary Anti-Hair Fall Hair ShampooSold out": {
        "url": "https://theayurvedaco.com/products/rosemary-anti-hair-fall-shampoo"
    },
    "Rosemary Anti-Hair Fall Hair Shampoo": {
        "url": "https://theayurvedaco.com/products/rosemary-anti-hair-fall-shampoo"
    },
    "Rosemary & Clove Oil | Reduces Hair Fall": {
        "url": "https://theayurvedaco.com/products/rosemary-anti-hair-fall-shampoo"
    },
    "Rosemary Anti-Hair Fall Scalp SerumSale": {
        "url": "https://theayurvedaco.com/products/rosemary-anti-hair-fall-scalp-serum"
    },
    "Rosemary Anti-Hair Fall Scalp Serum": {
        "url": "https://theayurvedaco.com/products/rosemary-anti-hair-fall-scalp-serum"
    },
    "with Mint & Clove Oil | Treats & Nourishes Scalp": {
        "url": "https://theayurvedaco.com/products/rosemary-anti-hair-fall-scalp-serum"
    },
    "Rust Desire Liquid LipstickSale": {
        "url": "https://theayurvedaco.com/products/rust-desire-liquid-lipstick-retail"
    },
    "Rust Desire Liquid Lipstick": {
        "url": "https://theayurvedaco.com/products/rust-desire-liquid-lipstick-retail"
    },
    "Satsuma Orange Lip, Cheek & TintSale": {
        "url": "https://theayurvedaco.com/products/satsuma-orange-lip-cheek-tint-5gm"
    },
    "Satsuma Orange Lip, Cheek & Tint": {
        "url": "https://theayurvedaco.com/products/satsuma-orange-lip-cheek-tint-5gm"
    },
    
    "Rosemary & Clove Oil | Reduces Hair Fall": {
        "url": "https://theayurvedaco.com/products/rosemary-anti-hair-fall-shampoo"
    },
    "Rosemary Anti-Hair Fall Scalp SerumSale": {
        "url": "https://theayurvedaco.com/products/rosemary-anti-hair-fall-scalp-serum"
    },
    "Rosemary Anti-Hair Fall Scalp Serum": {
        "url": "https://theayurvedaco.com/products/rosemary-anti-hair-fall-scalp-serum"
    },
    "with Mint & Clove Oil | Treats & Nourishes Scalp": {
        "url": "https://theayurvedaco.com/products/rosemary-anti-hair-fall-scalp-serum"
    },
    "Rust Desire Liquid LipstickSale": {
        "url": "https://theayurvedaco.com/products/rust-desire-liquid-lipstick-retail"
    },
    "Rust Desire Liquid Lipstick": {
        "url": "https://theayurvedaco.com/products/rust-desire-liquid-lipstick-retail"
    },
    "Satsuma Orange Lip, Cheek & TintSale": {
        "url": "https://theayurvedaco.com/products/satsuma-orange-lip-cheek-tint-5gm"
    },
    "Satsuma Orange Lip, Cheek & Tint": {
        "url": "https://theayurvedaco.com/products/satsuma-orange-lip-cheek-tint-5gm"
    },
    "Ayurvedic Lip, Cheek & Eye Tint for Natural Makeup look": {
        "url": "https://theayurvedaco.com/products/satsuma-orange-lip-cheek-tint-5gm"
    },
    "Shringaar Maroon SindoorSold out": {
        "url": "https://theayurvedaco.com/products/shringaar-maroon-sindoor-retail"
    },
    "Shringaar Maroon Sindoor": {
        "url": "https://theayurvedaco.com/products/shringaar-maroon-sindoor-retail"
    },
    "Your beauty with the auspicious & symbolic Shringaar Sindoor": {
        "url": "https://theayurvedaco.com/products/shringaar-red-sindoor-retail"
    },
    "Shringaar Red SindoorSale": {
        "url": "https://theayurvedaco.com/products/shringaar-red-sindoor-retail"
    },
    "Shringaar Red Sindoor": {
        "url": "https://theayurvedaco.com/products/shringaar-red-sindoor-retail"
    },
    "Smokey Affair PerfumeSale": {
        "url": "https://theayurvedaco.com/products/smokey-affair-perfume-20ml"
    },
    "Smokey Affair Perfume": {
        "url": "https://theayurvedaco.com/products/smokey-affair-perfume-20ml"
    },
    "EDP | Eau De Parfum | Smokey & Woody Hints": {
        "url": "https://theayurvedaco.com/products/smokey-affair-perfume-20ml"
    },
    "Spicy Truth PerfumeSold out": {
        "url": "https://theayurvedaco.com/products/spicy-truth-perfume-20ml"
    },
    "Spicy Truth Perfume": {
        "url": "https://theayurvedaco.com/products/spicy-truth-perfume-20ml"
    },
    "EDP | Eau De Parfum | Citrusy with Fruity Hints": {
        "url": "https://theayurvedaco.com/products/spicy-truth-perfume-20ml"
    },
    "Thrive DeodorantSale": {
        "url": "https://theayurvedaco.com/products/thrive-deodorant-1-diy"
    },
    "Thrive Deodorant": {
        "url": "https://theayurvedaco.com/products/thrive-deodorant-1-diy"
    },
    "Ubtan Face Wash with Haldi & Chandan, 50mlSold out": {
        "url": "https://theayurvedaco.com/products/ubtan-face-wash-with-haldi-chandan"
    },
    "Ubtan Face Wash with Haldi & Chandan, 50ml": {
        "url": "https://theayurvedaco.com/products/ubtan-face-wash-with-haldi-chandan"
    },
    "Ubtan Foaming Face WashSold out": {
        "url": "https://theayurvedaco.com/products/ubtan-foaming-face-wash-retail"
    },
    "Ubtan Foaming Face Wash": {
        "url": "https://theayurvedaco.com/products/ubtan-foaming-face-wash-retail"
    },
    "Foaming Face Wash Glow & Brightening Skin": {
        "url": "https://theayurvedaco.com/products/ubtan-foaming-face-wash-retail"
    },
    "Ubtan Serum Sheet MaskSold out": {
        "url": "https://theayurvedaco.com/products/ubtan-serum-sheet-mask"
    },
    "Ubtan Serum Sheet Mask": {
        "url": "https://theayurvedaco.com/products/ubtan-serum-sheet-mask"
    },
    "with Sandalwood for Anti-Tan & Detox": {
        "url": "https://theayurvedaco.com/products/ubtan-serum-sheet-mask"
    },
    "Urban Blush Lip, Cheek & Eye TintSale": {
        "url": "https://theayurvedaco.com/products/urban-blush-lip-cheek-tint-5gm"
    },
  "with Grapefruit & Aloe Vera | For Toning & Brightening Skin": {
    "url": "https://theayurvedaco.com/products/10-natural-vitamin-c-face-serum-for-glowing-skin-with-1-hyaluronic-acid-for-anti-aging-pack-2-x-30ml"
  },
  "100% Natural Neem CombSale": {
    "url": "https://theayurvedaco.com/products/100-natural-neem-comb"
  },
  "100% Natural Neem Comb": {
    "url": "https://theayurvedaco.com/products/100-natural-neem-comb"
  },
  "7% Kumkumadi Face Wash with 24K Gold DustHot Movers": {
    "url": "https://theayurvedaco.com/products/7-kumkumadi-face-wash-with-24k-gold-dust-diy"
  },
  "7% Kumkumadi Face Wash with 24K Gold Dust": {
    "url": "https://theayurvedaco.com/products/7-kumkumadi-face-wash-with-24k-gold-dust-diy"
  },
  "Saffron & 24K Gold | Deeply Cleanses Skin": {
    "url": "https://theayurvedaco.com/products/7-kumkumadi-face-wash-with-24k-gold-dust-diy"
  },
  "Acne & Spot Correction Face SerumBestseller": {
    "url": "https://theayurvedaco.com/products/acne-oil-control-face-serum-eladi-neem"
  },
  "Acne & Spot Correction Face Serum": {
    "url": "https://theayurvedaco.com/products/acne-oil-control-face-serum-eladi-neem"
  },
  "With Eladi & Neem | Reduces Acne & Spots": {
    "url": "https://theayurvedaco.com/products/acne-oil-control-face-serum-eladi-neem"
  },
  "Ananda Fruit & Spice Deodorant SpraySale": {
    "url": "https://theayurvedaco.com/products/ananda-fruit-spice-deodorant-spray-150ml"
  },
  "Ananda Fruit & Spice Deodorant Spray": {
    "url": "https://theayurvedaco.com/products/ananda-fruit-spice-deodorant-spray-150ml"
  },
  "for Refreshing & Long Lasting Fragrance": {
    "url": "https://theayurvedaco.com/products/ananda-fruit-spice-deodorant-spray-150ml"
  },
  "Ananda Sandalwood & Cinnamon Deodorant SpraySold out": {
    "url": "https://theayurvedaco.com/products/ananda-sandalwood-cinnamon-deodorant-spray-150ml"
  },
  "Ananda Sandalwood & Cinnamon Deodorant Spray": {
    "url": "https://theayurvedaco.com/products/ananda-sandalwood-cinnamon-deodorant-spray-150ml"
  },
  "with Sandalwood & Cinnamon for Refreshing & Long Lasting Fragrance": {
    "url": "https://theayurvedaco.com/products/ananda-sandalwood-cinnamon-deodorant-spray-150ml"
  },
  "Anti Acne Day CreamSale": {
    "url": "https://theayurvedaco.com/products/anti-acne-day-cream"
  },
  "Anti Acne Day Cream": {
    "url": "https://theayurvedaco.com/products/anti-acne-day-cream"
  },
  "Anti-ageing RegimeSold out": {
    "url": "https://theayurvedaco.com/products/anti-ageing-regime"
  },
  "Anti-ageing Regime": {
    "url": "https://theayurvedaco.com/products/anti-ageing-regime"
  },
  "Ashwagandha Face Wash and Face Serum": {
    "url": "https://theayurvedaco.com/products/anti-ageing-regime"
  },
  "Anti-Pigmentation Face SerumSale": {
    "url": "https://theayurvedaco.com/products/anti-pigmentation-face-serum-gotu-kola-rosehip"
  },
  "Anti-Pigmentation Face Serum": {
    "url": "https://theayurvedaco.com/products/anti-pigmentation-face-serum-gotu-kola-rosehip"
  },
  "with Gotu Kola & Rosehip | Reduces Pigmentation & Dullness": {
    "url": "https://theayurvedaco.com/products/anti-pigmentation-face-serum-gotu-kola-rosehip"
  },
  "Ashwagandha Face Wash with Bakuchiol, 50mlSale": {
    "url": "https://theayurvedaco.com/products/ashwagandha-face-wash-with-bakuchiol"
  },
  "Ashwagandha Face Wash with Bakuchiol, 50ml": {
    "url": "https://theayurvedaco.com/products/ashwagandha-face-wash-with-bakuchiol"
  },
  "for Soft and Supple Skin": {
    "url": "https://theayurvedaco.com/products/ashwagandha-face-wash-with-bakuchiol-50ml-pack-of-2"
  },
  "Ashwagandha Face Wash with Bakuchiol, 50ml (Pack of 2)Sold out": {
    "url": "https://theayurvedaco.com/products/ashwagandha-face-wash-with-bakuchiol-50ml-pack-of-2"
  },
  "Ashwagandha Face Wash with Bakuchiol, 50ml (Pack of 2)": {
    "url": "https://theayurvedaco.com/products/ashwagandha-face-wash-with-bakuchiol-50ml-pack-of-2"
  },
  "Ayurglow Brightening Cream 50gmSale": {
    "url": "https://theayurvedaco.com/products/ayurglow-brightening-cream-50gm"
  },
  "Ayurglow Brightening Cream 50gm": {
    "url": "https://theayurvedaco.com/products/ayurglow-brightening-cream-50gm"
  },
  "AyurJosh Shilajit ResinSale": {
    "url": "https://theayurvedaco.com/products/ayurjosh-shilajit-resin-retail"
  },
  "AyurJosh Shilajit Resin": {
    "url": "https://theayurvedaco.com/products/ayurjosh-shilajit-resin-retail"
  },
  "With Fulvic Acid & 84 Minerals | Boosts Immunity & Metabolism": {
    "url": "https://theayurvedaco.com/products/100-natural-pure-shilajit-resin-for-improving-immunity-metabolism-stamina-pack-of-2"
  },
  "Bakuchiol Under Eye GelHot Movers": {
    "url": "https://theayurvedaco.com/products/under-eye-gel-cream-remove-dark-circles"
  },
  "Bakuchiol Under Eye Gel": {
    "url": "https://theayurvedaco.com/products/under-eye-gel-cream-remove-dark-circles"
  },
  "for Removing Dark Circles and Collagen Boosting with Potato Starch": {
    "url": "https://theayurvedaco.com/products/under-eye-gel-cream-remove-dark-circles"
  },
  "with Vitamin E & Almond Oil | Smudge-proof & Matte Finish": {
    "url": "https://theayurvedaco.com/products/beautif-eye-kajal-intense-black-kajal-retail"
  },
  "Beautif-eye Kajal - Intense Black KajalSale": {
    "url": "https://theayurvedaco.com/products/beautif-eye-kajal-intense-black-kajal-retail"
  },
  "Beautif-eye Kajal - Intense Black Kajal": {
    "url": "https://theayurvedaco.com/products/beautif-eye-kajal-intense-black-kajal-retail"
  },
  "Beet Mighty Pink Lip, Cheek and Eye TintSale": {
    "url": "https://theayurvedaco.com/products/beetroot-lip-and-cheek-tint"
  },
  "Beet Mighty Pink Lip, Cheek and Eye Tint": {
    "url": "https://theayurvedaco.com/products/beetroot-lip-and-cheek-tint"
  },
  "Organic Beetroot Lip and Cheek Tint for Dry Skin and Glow": {
    "url": "https://theayurvedaco.com/products/beetroot-lip-and-cheek-tint"
  },
  "Beetroot Lip Balm with SPF 20Sale": {
    "url": "https://theayurvedaco.com/products/beetroot-lip-balm-dry-dark-lip-lightening"
  },
  "Beetroot Lip Balm with SPF 20": {
    "url": "https://theayurvedaco.com/products/beetroot-lip-balm-dry-dark-lip-lightening"
  },
  "Moisturising Lip Balm for Dry & Pigmented Lips": {
    "url": "https://theayurvedaco.com/products/beetroot-lip-balm-dry-dark-lip-lightening"
  },
  "Beetroot Lip ScrubSale": {
    "url": "https://theayurvedaco.com/products/beetroot-lip-scrub-dark-dry-lips-chapped-lips"
  },
  "Beetroot Lip Scrub": {
    "url": "https://theayurvedaco.com/products/beetroot-lip-scrub-dark-dry-lips-chapped-lips"
  },
  "Lip Scrub for Dry, Dark & Chapped Lips": {
    "url": "https://theayurvedaco.com/products/beetroot-lip-scrub-dark-dry-lips-chapped-lips"
  },
  "BhringaBali Hair ConditionerSold out": {
    "url": "https://theayurvedaco.com/products/bhringabali-hair-conditioner-diy"
  },
  "BhringaBali Hair Conditioner": {
    "url": "https://theayurvedaco.com/products/bhringabali-hair-conditioner-diy"
  },
  "with Mighty Bhringraj | For Hair Growth": {
    "url": "https://theayurvedaco.com/products/bhringabali-hair-shampoo-diy"
  },
  "BhringaBali Hair Growth CapsulesSold out": {
    "url": "https://theayurvedaco.com/products/bhringabali-hair-growth-30-veg-capsules"
  }
}"""  

        response = model.generate_content(
            contents=[{
                "role": "user",
                "parts": [user_query]
            }],
            generation_config={
                "system_instruction": system_instruction
            }
        )

        return response.text

    except Exception as e:
        print(f"❌ Recommendation Error: {str(e)}")
        return "I'm having trouble accessing product recommendations right now. Please try again later."
