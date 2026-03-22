"""Geographic reference database for TKK videos.

All coordinates are (latitude, longitude) from verified sources.
Latitudes: positive = North, negative = South
Longitudes: positive = East, negative = West
"""

from geo_utils import MapRegion

# ============================================================
# KNOWN LOCATIONS — (lat, lon)
# ============================================================
LOCATIONS = {
    # --- Bronze Age civilizations ---
    "hattusa":        (40.02, 34.62),   # Hittite capital, central Anatolia
    "mycenae":        (37.73, 22.76),   # Mycenaean citadel, Peloponnese Greece
    "memphis_egypt":  (29.87, 31.25),   # Old Kingdom capital, Nile delta
    "thebes_egypt":   (25.72, 32.65),   # New Kingdom capital (modern Luxor)
    "babylon":        (32.54, 44.42),   # Mesopotamia, modern Iraq
    "ugarit":         (35.60, 35.78),   # Syrian coast, key Bronze Age port
    "troy":           (39.96, 26.24),   # Northwest Turkey
    "knossos":        (35.30, 25.16),   # Minoan palace, Crete
    "cyprus":         (35.13, 33.43),   # Cyprus island center

    # --- Classical / Roman ---
    "rome":           (41.90, 12.50),
    "carthage":       (36.85, 10.33),   # Near modern Tunis
    "athens":         (37.97, 23.73),
    "alexandria":     (31.20, 29.92),
    "constantinople": (41.01, 28.98),   # Modern Istanbul
    "sparta":         (37.07, 22.43),

    # --- Americas ---
    "cusco":          (-13.53, -71.97), # Inca capital
    "machu_picchu":   (-13.16, -72.55),
    "tenochtitlan":   (19.43, -99.13),  # Aztec capital (modern Mexico City)
    "tikal":          (17.22, -89.62),  # Maya, Guatemala
    "chichen_itza":   (20.68, -88.57),  # Maya, Yucatan
    "palenque":       (17.48, -92.05),  # Maya, Chiapas

    # --- Southeast Asia ---
    "angkor_wat":     (13.41, 103.87),  # Khmer Empire, Cambodia

    # --- Norse / North Atlantic ---
    "brattahlid":     (61.15, -45.52),  # Erik the Red's farm, Greenland
    "lanse_aux_meadows": (51.59, -55.53), # Viking settlement, Newfoundland
    "bergen":         (60.39, 5.32),    # Norway, departure point

    # --- Near East ---
    "gobekli_tepe":   (37.22, 38.92),   # Southeastern Turkey
    "jericho":        (31.87, 35.44),
    "ur":             (30.96, 46.10),    # Sumer
    "persepolis":     (29.93, 52.89),

    # --- Easter Island ---
    "easter_island":  (-27.12, -109.37),
    "rano_raraku":    (-27.12, -109.30), # Moai quarry

    # --- Modern reference points (for sanity checking) ---
    "london":         (51.51, -0.13),
    "paris":          (48.86, 2.35),
    "istanbul":       (41.01, 28.98),
    "cairo":          (30.04, 31.24),
    "new_york":       (40.71, -74.01),
    "tokyo":          (35.68, 139.69),
    "mumbai":         (19.08, 72.88),
    "cape_town":      (-33.93, 18.42),

    # --- Trade route nodes (Bronze Age) ---
    "afghanistan_tin": (34.5, 69.0),    # Approximate tin source region
    "cyprus_copper":   (35.0, 33.0),    # Copper mines
    "egypt_grain":     (30.0, 31.0),    # Nile delta grain
}


# ============================================================
# MAP REGIONS — bounding boxes for common video topics
# ============================================================
MAP_REGIONS = {
    "eastern_med":    MapRegion("eastern_med",    10, 55, 20, 45),
    "full_med":       MapRegion("full_med",       -10, 45, 25, 50),
    "europe_med":     MapRegion("europe_med",     -5, 50, 25, 55),
    "south_america":  MapRegion("south_america",  -85, -30, -40, 15),
    "southeast_asia": MapRegion("southeast_asia", 90, 120, 0, 25),
    "north_atlantic": MapRegion("north_atlantic", -70, 10, 45, 70),
    "central_america": MapRegion("central_america", -100, -80, 12, 25),
    "turkey":         MapRegion("turkey",         25, 45, 35, 42),
    "east_pacific":   MapRegion("east_pacific",   -115, -105, -30, -24),
    "world":          MapRegion("world",          -180, 180, -60, 75),
}
