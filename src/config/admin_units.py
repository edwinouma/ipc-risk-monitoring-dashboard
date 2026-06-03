# ==========================================================
# STANDARD ADMINISTRATIVE UNITS
# ==========================================================

STANDARD_ADM1 = {

    "South Sudan": [
        "Abyei", "Juba", "Kajo-keji", "Lainya", "Morobo", "Terekeka", "Yei",
        "Budi", "Ikotos", "Kapoeta East", "Kapoeta North", "Kapoeta South",
        "Lafon", "Magwi", "Torit", "Akobo", "Ayod", "Bor South", "Canal/Pigi",
        "Duk", "Fangak", "Nyirol", "Pibor", "Pochalla", "Twic East", "Uror",
        "Awerial", "Cueibet", "Rumbek Centre", "Rumbek East", "Rumbek North",
        "Wulu", "Yirol East", "Yirol West", "Aweil Centre", "Aweil East",
        "Aweil North", "Aweil South", "Aweil West", "Abiemnhom", "Guit",
        "Koch", "Leer", "Mayendit", "Mayom", "Panyijiar", "Pariang",
        "Rubkona", "Baliet", "Fashoda", "Longochuk", "Luakpiny/Nasir",
        "Maban", "Maiwut", "Malakal", "Manyo", "Melut", "Panyikang",
        "Renk", "Ulang", "Gogrial East", "Gogrial West", "Tonj East",
        "Tonj North", "Tonj South", "Twic", "Jur River", "Raja", "Wau",
        "Ezo", "Ibba", "Maridi", "Mundri East", "Mundri West", "Mvolo",
        "Nagero", "Nzara", "Tambura", "Yambio", "Akoka"
    ],

    "Kenya": [
        "Baringo", "Embu", "Garissa", "Isiolo", "Kajiado", "Kilifi", "Kitui",
        "Kwale", "Laikipia", "Lamu", "Makueni", "Mandera", "Marsabit",
        "Meru", "Narok", "Nyeri", "Samburu", "Taita Taveta", "Tana River",
        "Tharaka Nithi", "Turkana", "Wajir", "West Pokot"
    ],

    "Afghanistan": [
        "Badakhshan", "Badghis", "Baghlan", "Balkh", "Bamyan", "Daykundi",
        "Farah", "Faryab", "Ghazni", "Ghor", "Hilmand", "Hirat",
        "Jawzjan", "Kabul", "Kandahar", "Kapisa", "Khost", "Kunar",
        "Kunduz", "Laghman", "Logar", "Maidan Wardak", "Nangarhar",
        "Nimroz", "Nuristan", "Paktika", "Paktya", "Panjsher",
        "Parwan", "Samangan", "Sar-e-Pul", "Takhar", "Uruzgan", "Zabul"
    ]
}


# ==========================================================
# ADMIN NAME REPLACEMENTS
# ==========================================================

ADMIN_REPLACEMENTS = {

    "Kenya": {
        "Nairob": "Nairobi",
        "Mombassa": "Mombasa",
        "Kisum": "Kisumu"
    },

    "Afghanistan": {
        "Wardak": "Maidan Wardak",
        "Sar-e-pul": "Sar-e-Pul",
        "Sar-E Pol": "Sar-e-Pul"
    }
}


# ==========================================================
# ADMINISTRATIVE GROUPINGS
# ==========================================================

ADM1_GROUP_MAPPING = {

    "South Sudan": {

        "Abyei": "Abyei Region",

        # Central Equatoria
        "Juba": "Central Equatoria",
        "Kajo-keji": "Central Equatoria",
        "Lainya": "Central Equatoria",
        "Morobo": "Central Equatoria",
        "Terekeka": "Central Equatoria",
        "Yei": "Central Equatoria",

        # Eastern Equatoria
        "Budi": "Eastern Equatoria",
        "Ikotos": "Eastern Equatoria",
        "Kapoeta East": "Eastern Equatoria",
        "Kapoeta North": "Eastern Equatoria",
        "Kapoeta South": "Eastern Equatoria",
        "Lafon": "Eastern Equatoria",
        "Magwi": "Eastern Equatoria",
        "Torit": "Eastern Equatoria",

        # Jonglei
        "Akobo": "Jonglei",
        "Ayod": "Jonglei",
        "Bor South": "Jonglei",
        "Canal/Pigi": "Jonglei",
        "Duk": "Jonglei",
        "Fangak": "Jonglei",
        "Nyirol": "Jonglei",
        "Pibor": "Jonglei",
        "Pochalla": "Jonglei",
        "Twic East": "Jonglei",
        "Uror": "Jonglei",

        # Lakes
        "Awerial": "Lakes",
        "Cueibet": "Lakes",
        "Rumbek Centre": "Lakes",
        "Rumbek East": "Lakes",
        "Rumbek North": "Lakes",
        "Wulu": "Lakes",
        "Yirol East": "Lakes",
        "Yirol West": "Lakes",

        # Northern Bahr el Ghazal
        "Aweil Centre": "Northern Bahr el Ghazal",
        "Aweil East": "Northern Bahr el Ghazal",
        "Aweil North": "Northern Bahr el Ghazal",
        "Aweil South": "Northern Bahr el Ghazal",
        "Aweil West": "Northern Bahr el Ghazal",

        # Unity
        "Abiemnhom": "Unity",
        "Guit": "Unity",
        "Koch": "Unity",
        "Leer": "Unity",
        "Mayendit": "Unity",
        "Mayom": "Unity",
        "Panyijiar": "Unity",
        "Pariang": "Unity",
        "Rubkona": "Unity",

        # Upper Nile
        "Baliet": "Upper Nile",
        "Fashoda": "Upper Nile",
        "Longochuk": "Upper Nile",
        "Luakpiny/Nasir": "Upper Nile",
        "Maban": "Upper Nile",
        "Maiwut": "Upper Nile",
        "Malakal": "Upper Nile",
        "Manyo": "Upper Nile",
        "Melut": "Upper Nile",
        "Panyikang": "Upper Nile",
        "Renk": "Upper Nile",
        "Ulang": "Upper Nile",
        "Akoka": "Upper Nile",

        # Warrap
        "Gogrial East": "Warrap",
        "Gogrial West": "Warrap",
        "Tonj East": "Warrap",
        "Tonj North": "Warrap",
        "Tonj South": "Warrap",
        "Twic": "Warrap",

        # Western Bahr el Ghazal
        "Jur River": "Western Bahr el Ghazal",
        "Raja": "Western Bahr el Ghazal",
        "Wau": "Western Bahr el Ghazal",

        # Western Equatoria
        "Ezo": "Western Equatoria",
        "Ibba": "Western Equatoria",
        "Maridi": "Western Equatoria",
        "Mundri East": "Western Equatoria",
        "Mundri West": "Western Equatoria",
        "Mvolo": "Western Equatoria",
        "Nagero": "Western Equatoria",
        "Nzara": "Western Equatoria",
        "Tambura": "Western Equatoria",
        "Yambio": "Western Equatoria",
    }
}


# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def get_standard_adm1(country):
    return STANDARD_ADM1.get(country, [])


def get_admin_replacements(country):
    return ADMIN_REPLACEMENTS.get(country, {})


def get_group_mapping(country):
    return ADM1_GROUP_MAPPING.get(country, {})