from __future__ import annotations

# 대세판단에 넣는 심볼은 알트 목록에서 제외한다.
MACRO = [
    {"id": "oil", "label": "유가", "symbol": "CLUSDT", "hint": "WTI"},
    {"id": "soxl", "label": "SOXL", "symbol": "SOXLUSDT", "hint": "반도체 3X"},
    {"id": "nasdaq", "label": "나스닥", "symbol": "QQQUSDT", "hint": "QQQ"},
    {"id": "btc", "label": "비트코인", "symbol": "BTCUSDT", "hint": "BTC"},
    {"id": "eth", "label": "이더리움", "symbol": "ETHUSDT", "hint": "ETH"},
    {"id": "sol", "label": "솔라나", "symbol": "SOLUSDT", "hint": "SOL"},
]

# 사용자 요청 + 커버리지용 추가 분류. 각 알트는 primary 1개.
SECTORS = [
    ("l1", "레이어 1"),
    ("l2", "레이어 2"),
    ("meme", "밈"),
    ("defi", "디파이"),
    ("rwa", "RWA"),
    ("depin", "DePIN"),
    ("ai", "AI"),
    ("game", "게임/메타버스"),
    ("btc_eco", "BTC 생태계"),
    ("infra", "인프라/오라클"),
    ("privacy", "프라이버시"),
    ("tradfi", "TradFi"),
    ("other", "기타"),
]

SECTOR_LABEL = dict(SECTORS)
MACRO_SYMBOLS = {m["symbol"] for m in MACRO}

_L1 = {
    "0G", "ADA", "ALGO", "APT", "ATOM", "AVAX", "BCH", "BERA", "BNB", "BSV",
    "CELO", "CFX", "CKB", "CORE", "DASH", "DOT", "DYM", "EGLD", "ETC", "ETHW",
    "FIL", "FLOW", "FOGO", "HBAR", "HYPE", "ICP", "ICNT", "INJ", "IOTA", "IOTX",
    "KAIA", "KAS", "KAVA", "KSM", "LTC", "MINA", "MON", "NEAR", "NEO", "NEWT",
    "ONE", "ONT", "POL", "QTUM", "ROSE", "RVN", "S", "SEI", "SUI", "TIA", "TRX",
    "VET", "VTHO", "XLM", "XRP", "XTZ", "ZETA", "ZIL", "SONIC", "SAGA", "INIT",
    "KAITO", "KITE", "SOMI", "ASTR", "KAT", "GAS", "HIVE", "STEEM", "LSK",
    "IOST", "WAXP", "ONG", "POWR", "WAN", "G", "SFP", "CTK", "CTSI", "SKL",
    "CELR", "CHR", "HOT", "ANKR", "ARPA", "BAND", "COTI", "PHA", "NKN", "PUNDIX",
    "WIN", "SUN", "JST", "BTTC", "SC", "DGB", "ZEN", "XEM", "WAVES", "ZRX",
    "CHZ", "ENJ", "THETA", "TFUEL", "KLAY", "FTT", "TWT", "WOO", "GMT", "APTO",
    "SEI", "TIA", "SUI", "INJ", "STX", "RONIN", "ROSE", "KAVA", "MINA", "IOTA",
    "KDA", "GLMR", "MOVR", "ASTR", "CFG", "ACA", "SDN", "BIT", "METIS", "AURORA",
    "CQT", "FLR", "SGB", "KAS", "HBAR", "XDC", "IOTA", "HNT", "MOBILE", "IOT",
    "AKT", "JUNO", "SCRT", "OSMO", "SEI", "ARCH", "NIBI", "DYM", "INIT", "BERA",
    "MON", "HYPE", "S", "SONIC", "MOVE", "MEGA", "XPL", "SOMI", "PHAROS", "AZTEC",
    "ALL", "NOM", "NIL", "TAC", "TREE", "CROSS", "MITO", "NXPC", "PARTI", "SIGN",
    "SOON", "SOPH", "STAR", "TA", "THE", "TOWNS", "ZAMA", "ZBT", "ZKC",
}
_L2 = {
    "ARB", "OP", "STRK", "MANTA", "SCR", "LINEA", "TAIKO", "IMX", "METIS", "ZK",
    "ZRO", "LRC", "BOBA", "BLAST", "MODE", "CYBER", "MANTLE", "MNT", "POL",
    "MATIC", "XDAI", "BASE", "SCROLL", "STARK", "ZKSYNC", "MINA", "METIS",
    "MERL", "B2", "MOVE", "MANTA", "ALT", "LAYER", "HEMI", "ERA", " lumia",
    "LUMIA", "CORN", "SWELL", "B3", "WORLD", "WLD", "CELO", "MANTLE",
    "OPN", "OPG", "ORDER", "ZRC", "ZKP", "ZORA",
}
_MEME = {
    "DOGE", "SHIB", "PEPE", "FLOKI", "BONK", "WIF", "BRETT", "POPCAT", "PENGU",
    "NEIRO", "MEME", "TURBO", "MOODENG", "FARTCOIN", "PNUT", "MEW", "BOME",
    "PEOPLE", "CHILLGUY", "TRUMP", "MELANIA", "GIGGLE", "USELESS", "BANANAS31",
    "BROCCOLI714", "BROCCOLIF3B", "KOMA", "DOGS", "CATI", "HMSTR", "MOG", "BOB",
    "CHEEMS", "RATS", "SATS", "SHIB", "XEC", "BABYDOGE", "BANANA", "BAN",
    "BASED", "BIRB", "BULLA", "C", "DOOD", "ELSA", "FIGHT", "GOAT", "GWEI",
    "HAEDAL", "IDOL", "JELLYJELLY", "MARSCOIN", "MEW", "MOCA", "MUBARAK",
    "NEIRO", "NOT", "PIPPIN", "PNUT", "PUMP", "RAVE", "SIREN", "SLERF", "SPX",
    "TOSHI", "TURBO", "TUT", "U", "USTC", "LUNC", "LUNA2", "1000LUNC", "GIGGLE",
    "CHIP", "ACT", "AVA", "B", "BEAT", "BILL", "BSB", "BTR", "BTW", "CAP",
    "CAT", "CC", "COLLECT", "COOKIE", "DEEP", "DOLO", "DOS", "EDEN", "ESP",
    "F", "FF", "FOLKS", "FORM", "GIGGLE", "GRAM", "GRIFFAIN", "GUA", "GUN",
    "H", "HANA", "HEI", "HOME", "HYPER", "INX", "IRYS", "JCT", "KGEN", "KOMA",
    "LAB", "LIGHT", "LIT", "LYN", "M", "MAGMA", "ME", "MERL", "MET", "MIRA",
    "MMT", "MYX", "NAORIS", "NIGHT", "O", "OG", "OGN", "ON", "OPEN", "PENGU",
    "PIEVERSE", "PLAY", "PONS", "POWER", "PRL", "PROM", "PROVE", "PTB", "Q",
    "RARE", "RE", "RECALL", "RED", "RIVER", "ROBO", "SAHARA", "SANTOS", "SAPIEN",
    "SENT", "SHELL", "SKR", "SKY", "SLX", "SPACE", "SPORTFUN", "STABLE", "STBL",
    "STO", "SWARMS", "SXT", "SYN", "T", "TAG", "TAKE", "TST", "TURTLE", "TRUST",
    "TRUTH", "UB", "US", "VELVET", "VVV", "WET", "WLFI", "XAN", "XNY", "XPIN",
    "YB", "ZEREBRO", "ZEST", "哈基米", "币安人生", "我踏马来了", "牛来", "龙虾",
    "ALPINE", "ASR", "ACE", "ALICE", "ANIME", "BANANAS31", "FARTCOIN",
    "MOODENG", "MELANIA", "TRUMP", "CHILLGUY", "NEIRO", "PNUT", "WIF", "POPCAT",
    "BRETT", "BOME", "MEW", "DOGS", "HMSTR", "CATI", "NOT", "PEOPLE", "MEME",
    "TURBO", "FLOKI", "BONK", "PEPE", "SHIB", "DOGE", "GOAT", "ACT", "BAN",
    "SLP", "TLM", "PORTO", "LAZIO", "SANTOS", "BAR", "PSG", "ATM", "JUV",
    "CITY", "INTER", "ACM", "ARG", "POR",
}
_DEFI = {
    "AAVE", "UNI", "CRV", "COMP", "SNX", "SUSHI", "1INCH", "DYDX", "GMX",
    "PENDLE", "LDO", "ENA", "MORPHO", "CAKE", "JOE", "JUP", "RAYSOL", "ORCA",
    "CVX", "YFI", "AERO", "VELODROME", "FLUID", "SYRUP", "LISTA", "EUL", "FRAX",
    "RPL", "BAL", "MKR", "SKY", "FXS", "CRVUSD", "GEAR", "RDNT", "MAV", "JOE",
    "GMX", "GNS", "PERP", "KWENTA", "HPOS", "VELO", "AERO", "THENA", "RAMSES",
    "BNT", "KNC", "ZRX", "BAT", "NMR", "MLN", "AUCTION", "BICO", "BLUR", "ID",
    "MASK", "UMA", "BADGER", "FARM", "ALCX", "SPELL", "MIM", "CURVE", "CONVEX",
    "ETHFI", "REZ", "EIGEN", "PUFFER", "SWELL", "PSTAKE", "RPL", "ANKR",
    "LIDO", "STG", "SYN", "HOP", "ACROSS", "SOCKET", "LI.FI", "KYBER", "DODOX",
    "BANCOR", "QUICK", "CAKE", "BSW", "BABY", "THENA", "EQUAL", "CHRONOS",
    "DRIFT", "JTO", "JUP", "MNDE", "KMNO", "TNSR", "TENSOR", "ORCA", "RAY",
    "SRM", "FIDA", "MAPE", "STEP", "MEDIA", "COPE", "SUN", "JUST", "FLUID",
    "MORPHO", "PENDLE", "EQU", "USUAL", "RESOLV", "SOLV", "LISTA", "RAD",
    "BIFI", "AUTO", "ALPACA", "BISWAP", "BANK", "IQ", "FOX", "OGN", "TRU",
    "FOR", "CREAM", "ALPHA", "SXP", "DEFI", "FIRO", "LQTY", "MAV", "NTRN",
    "OSMO", "ASTRO", "WHITE", "MNTA", "HYPERLIQUID", "HYPER", "GMX", "GNS",
    "MUX", "LEVEL", "JOJO", "APX", "THENA", "SWAP", "VELODROME", "AERO",
    "EXTRA", "WELL", "MOONWELL", "SEAM", "MOON", "GRAVI", "BEND", "PARA",
    "RADIANT", "GEIST", "TROVE", "LODE", "UMAMI", "JONES", "PLUTUS", "GMD",
    "VAULTKA", "CAMELOT", "RAMSES", "SOLIDLY", "EQUALIZER", "FVM", "XVS",
    "VENUS", "ALPACA", "RABBIT", "WOM", "SYNAPSE", "STARGATE", "STG", "HOP",
    "ACROSS", "SOCKET", "BUNGEE", "LI.FI", "RANGO", "THOR", "RUNE", "CHAINFLIP",
    "THORCHAIN", "MAYA", "ASGARDEX", "COW", "COWSWAP", "GNOSIS", "BAL", "AURA",
    "HIDDENHAND", "CONCAVE", "TEMPLE", "OHM", "KLIMA", "FORGE", "VOLT",
    "EUL", "EVAA", "KERNEL", "KGEN", "SAFE", "SSV", "SD", "RPL", "SWISE",
    "OBOL", "LIDO", "WXETH", "SWETH", "RSETH", "EZETH", "WEETH",
}
_RWA = {
    "ONDO", "POLYX", "CFG", "PLUME", "PAXG", "XAUT", "TRU", "GFI", "CTC",
    "RIO", "BACKED", "OUSG", "USDY", "BUIDL", "BENJI", "STBT", "USD0", "USR",
    "USUAL", "CPOOL", "MPL", "CRED", "PROPY", "REAL", "LAND", "PBR", "DUSD",
    "C", "CFG", "POLYX", "ONDO", "PLUME", "GOLD", "SLV", "GLD", "IAU",
    "TRUFI", "CENTRIFUGE", "MAPLE", "GOLDfinch", "CREDIX", "CLEARPOOL",
    "HIFI", "TINLAKE", "MAKERDAO", "SKY", "RWA", "TOKENY", "SECURITIZE",
    "WLFI", "USD1", "USTC", "FRAX", "LUSD", "CRVUSD", "GHO", "DAI", "USDC",
    "TUSD", "FDUSD", "PYUSD", "USDP", "GUSD", "EURC", "EUROC", "GYEN",
    "CADC", "XCHF", "XSGD", "ZUSD", "BIDR", "IDRT", "BRZ", "EURS",
    "STBL", "STABLE", "USDE", "ENA", "ETHENA", "USUAL", "RESOLV",
}
_DEPIN = {
    "FIL", "AR", "RENDER", "IOTX", "GRASS", "BLESS", "AKT", "LPT", "THETA",
    "HNT", "MOBILE", "IOT", "DIMO", "GEOD", "WIFI", "PLANET", "GPS", "W",
    "WAL", "AIOZ", "STORJ", "SC", "BTT", "HOT", "ANKR", "POKT", "NYM",
    "NKN", "CTSI", "IOST", "IOTX", "JASMY", "PHA", "CRU", "OCEAN", "FET",
    "AGIX", "OCEAN", "NUM", "DPR", "HOPR", "NYM", "MASK", "ATLAS", "NAVI",
    "WIFI", "XNET", "WORLDMOBILE", "WMT", "WMTX", "DENT", "HOT", "AMP",
    "TEL", "XYM", "IOTA", "MIOTA", "SMR", "ASMB", "FLUX", "GLMR", "MOVR",
    "PHALA", "ASTR", "CFG", "AKASH", "AKT", "GRASS", "RENDER", "RNDR",
    "LPT", "LIVEPEER", "THETA", "TFUEL", "BTTC", "TRON", "WIN", "JST",
    "BTT", "USDD", "APENFT", "TUSD", "SUN", "HTX", "JUST", "BTTOLD",
    "DRIFT", "DEEP", "ICNT", "IO", "AWE", "EDGE", "DATAIP", "SQD",
    "WAL", "W", "GRASS", "BLESS", "GEODNET", "DIMO", "HIVEMAPPER", "HONEY",
}
_AI = {
    "FET", "AGIX", "OCEAN", "TAO", "WLD", "RENDER", "ARKM", "IO", "VIRTUAL",
    "AIXBT", "CGPT", "FLOCK", "KAITO", "AIGENSYN", "AIN", "AIO", "AIOT",
    "BLUAI", "COAI", "SKYAI", "UAI", "ZEREBRO", "PROMPT", "SWARMS", "AIA",
    "ARC", "ARIA", "AVAAI", "CLANKER", "GRIFFAIN", "RECALL", "SAPIEN",
    "TRUTH", "ZEREBRO", "AI16Z", "GOAT", "FARTCOIN", "ZEREBRO", "OLAS",
    "NMT", "NMR", "CTXC", "AGI", "OCEAN", "FET", "AGIX", "NMR", "CTXC",
    "PHB", "PHA", "RLC", "IEXEC", "GTC", "GITCOIN", "RSS3", "MASK", "LENS",
    "CYBER", "ID", "SPACEID", "SID", "LDO", "SSV", "OBOL", "EIGEN", "ETHFI",
    "REZ", "PUFFER", "KARAK", "ALT", "LAYERZERO", "ZRO", "WORMHOLE", "W",
    "PYTH", "SWITCHBOARD", "API3", "BAND", "TRB", "DIA", "UMA", "UMA",
    "COAI", "AIXBT", "VIRTUAL", "GAME", "PRIME", "PAAL", "SPECTRE", "GRT",
    "THEGRAPH", "KAITO", "COOKIE", "FLOCK", "ARKM", "IO.NET", "IO", "NOSANA",
    "NOS", "RENDER", "RNDR", "LPT", "THETA", "TAO", "BITTENSOR", "SN",
    "CORTEX", "CTXC", "PHB", "RED", "AIOZ", "PHALA", "PHA", "OCEAN",
    "FETCH", "SINGULARITYNET", "AGIX", "NMR", "NUMERAI", "INJECTIVE",
    "INJ", "DYDX", "GMX", "GNS", "VERTEX", "AEVO", "HYPERLIQUID",
    "AEVO", "HYPER", "VERTEX", "DRIFT", "JUP", "ZETA", "ORDERLY", "ORDER",
    "XODEX", "APEX", "MUX", "LEVEL", "GAINS", "GNS", "PREMIA", "LYRA",
    "AEVO", "LYRA", "POLYMARKET", "GNOSIS", "CONDITIONAL",
}
_GAME = {
    "AXS", "SAND", "MANA", "GALA", "PIXEL", "PORTAL", "BIGTIME", "ILV",
    "YGG", "MAGIC", "MAVIA", "ACE", "ALICE", "TLM", "SLP", "BEAMX", "XAI",
    "NOT", "CATI", "ESPORTS", "PLAY", "G", "PIXEL", "PORTAL", "PRIME",
    "GHST", "ATLAS", "POLIS", "STAR", "PYR", "REVU", "UFO", "DAR", "MBOX",
    "MOBOX", "ALPACA", "PET", "HIGH", "MC", "HERO", "CHR", "TOWER", "SKILL",
    "DPET", "FARA", "CAKE", "BETA", "TREASURE", "MAGIC", "BRIDGEWORLD",
    "SMOL", "REALM", "THE", "GODS", "IMX", "OKB", "LOOKS", "BLUR", "X2Y2",
    "SUDO", "NFTX", "FLOOR", "WHALE", "RARE", "SUPERRARE", "FOUNDATION",
    "ENJ", "FLOW", "WAXP", "CHZ", "OG", "PSG", "BAR", "CITY", "JUV", "ATM",
    "ASR", "ACM", "INTER", "PORTO", "LAZIO", "SANTOS", "ALPINE", "SPURS",
    "NAP", "MIL", "NOV", "UCHI", "GAL", "VOXEL", "USTC", "LUNC", "LUNA",
    "ILV", "GDX", "YGG", "MC", "MOC", "MOOV", "FIR", "FCON", "SIDUS",
    "GCOIN", "LOKA", "BICO", "BICONOMY", "IMX", "GODS", "TOWER", "BURGER",
    "BAKE", "EPS", "BELT", "AUTO", "BIFI", "RAMP", "FOR", "UNFI", "BEL",
    "TWT", "SFP", "C98", "ALPHA", "TLM", "ALICE", "DEGO", "AUCTION", "HARD",
    "VIDT", "DATA", "CTK", "CTSI", "CHR", "COS", "KEY", "WAN", "FUN", "COS",
    "DENT", "WIN", "WRX", "LTO", "MBL", "IRIS", "OGN", "NKN", "ARPA", "CTXC",
    "BNT", "COTI", "DATA", "NULS", "STMX", "KMD", "ZEN", "RVN", "DCR", "SC",
    "DGB", "BTS", "STEEM", "HIVE", "LSK", "ARK", "WAVES", "STRAT", "NAV",
    "PIVX", "VTC", "XVG", "SYS", "EMC2", "VIA", "XMR", "ZEC", "DASH",
    "SPORTFUN", "FIGHT", "ESPORTS", "PLAY", "GAME", "GALA", "SAND", "MANA",
    "AXS", "ILV", "YGG", "BIGTIME", "PIXEL", "PORTAL", "XAI", "BEAMX",
    "MAGIC", "MAVIA", "ACE", "ALICE", "TLM", "SLP", "NOT", "CATI", "HMSTR",
    "PIXEL", "PRIME", "GHST", "ATLAS",
}
_BTC_ECO = {
    "ORDI", "STX", "RUNE", "BCH", "BSV", "PUMPBTC", "MERL", "B2", "SATS",
    "RATS", "1000SATS", "1000RATS", "RIF", "SOV", "AKN", "MUBI", "PIPE",
    "FB", "MAPE", "OBTC", "TBTC", "WBTC", "BTCB", "CBBTC", "SOLVBTC",
    "PUMPBTC", "UNIBTC", "BABY", "BABYLON", "BB", "NALS", "RDEX", "TRAC",
    "ATOMICALS", "ATOMICAL", "PIPE", "TRAC", "BITMAP", "BSV", "BCH",
    "XEC", "1000XEC", "BCHA", "BTG", "DGB", "RVN", "LTC", "DOGE",
    "STX", "ALEX", "ALEXLAB", "LEO", "ORDI", "SATS", "RATS", "PIZZA",
    "PUNKS", "NODE", "NODEMONKES", "BITMAP", "RSIC", "FF", "RUNES",
    "RSIC", "PIPE", "TRAC", "NALS", "RDEX", "RAM", "RAMSES",
}
_INFRA = {
    "LINK", "PYTH", "BAND", "API3", "GRT", "TRB", "UMA", "DIA", "PHA",
    "SQD", "W", "AXL", "ZRO", "LAYER", "CC", "TIA", "EIGEN", "ETHFI",
    "SSV", "LDO", "RPL", "ALT", "STG", "SYN", "RUNE", "ENS", "QNT",
    "WCT", "CVC", "ENSO", "ARK", "ARKM",
}
_DEFI |= {
    "RSR", "DEXE", "ALCH", "HUMA", "SPK", "TRADOOR", "CETUS", "ACH",
    "1INCH", "SNX", "COMP", "YFI", "CRV", "CVX", "PENDLE",
}
_AI |= {"VANA", "BIO", "ATH", "CARV", "AIXBT", "CGPT", "ANTHROPIC"}
_GAME |= {"APE", "AGLD", "SUPER", "EDU"}
_DEPIN |= {"GLM", "HOLO", "AR", "FIL", "RENDER", "IOTX", "GRASS"}
_L2 |= {"BAS", "OP", "ARB", "STRK", "LINEA", "TAIKO", "SCR"}
_BTC_ECO |= {"BTCDOM", "ORDI", "STX", "SATS", "RATS"}
_RWA |= {"ONDO", "PLUME", "PAXG", "XAUT", "HUMA", "C"}
_MEME |= {"TST", "NEIRO", "MOG", "BONK", "FLOKI", "PEPE"}
_PRIVACY = {
    "XMR", "ZEC", "DASH", "ROSE", "DUSK", "XVG", "ZEN", "SCRT", "NYM",
    "RAIL", "FIRO", "BEAM", "GRIN", "MWC", "XHV", "OXEN", "LOKI", "PART",
    "PIVX", "NAV", "XZC", "FIRO", "ZENCASH", "KMD", "ARRR", "PIRATE",
    "DERO", "SECRET", "SCRT", "OASIS", "ROSE", "NYM", "HOPR", "RAILGUN",
    "RAIL", "AZTEC", "ZKP", "ZAMA", "FHE", "PRIVACY", "TORN", "TORNADO",
    "NAMADA", "PENUMBRA", "ZEC", "HALO", "ORCHARD", "SAPLING",
}
_TRADFI = {
    "AAPL", "TSLA", "NVDA", "MSFT", "AMZN", "GOOGL", "GOOG", "META", "NFLX",
    "AMD", "INTC", "BABA", "TSM", "SPY", "QQQ", "SOXL", "CL", "BZ", "NATGAS",
    "CRWV", "MRVL", "WMT", "JPM", "V", "BRKB", "HOOD", "COIN", "MSTR",
    "SKHY", "SPCX", "SNDK", "PAXG", "XAUT", "GOLD", "SLV", "GLD",
    "US500", "NDX", "DJI", "NAS100",
}

# 짧은 이름 휴리스틱
_AI_KEYS = ("AI", "GPT", "NEURAL", "AGENT", "TAO", "RENDER", "VIRTUAL")
_MEME_KEYS = ("PEPE", "DOGE", "SHIB", "INU", "CAT", "MOON", "BABY", "ELON", "TRUMP", "CHILL", "FART", "PUMP")


def _norm(base: str) -> str:
    b = (base or "").upper()
    for p in ("1000000", "1000", "1M"):
        if b.startswith(p) and len(b) > len(p):
            return b[len(p):]
    return b


def sector_id(base: str, symbol: str | None = None, kind: str | None = None) -> str:
    sym = (symbol or "").upper()
    if sym in MACRO_SYMBOLS:
        return "macro"
    k = (kind or "").upper()
    if k in {"EQUITY", "COMMODITY", "INDEX"}:
        return "tradfi"
    b = _norm(base)
    if b.endswith(("2L", "2S", "3L", "3S")) or b.startswith("CSOP"):
        return "tradfi"
    if b in _TRADFI or (sym.endswith("USDT") and b in _TRADFI):
        return "tradfi"
    if b in _PRIVACY:
        return "privacy"
    if b in _MEME:
        return "meme"
    if any(k in b for k in _MEME_KEYS) and b not in _L1:
        return "meme"
    if b in _AI or any(k in b for k in ("AI", "AIXBT", "CGPT")):
        return "ai"
    if b in _DEPIN:
        return "depin"
    if b in _RWA:
        return "rwa"
    if b in _DEFI:
        return "defi"
    if b in _GAME:
        return "game"
    if b in _BTC_ECO:
        return "btc_eco"
    if b in _L2:
        return "l2"
    if b in _L1:
        return "l1"
    if b in _INFRA:
        return "infra"
    return "other"


def attach_sector(row: dict) -> dict:
    sid = sector_id(row.get("base") or "", row.get("symbol") or "", row.get("kind"))
    out = dict(row)
    out["sector"] = sid
    out["sector_label"] = "대세판단" if sid == "macro" else SECTOR_LABEL.get(sid, "기타")
    out["is_macro"] = sid == "macro"
    return out


def _strength(rows: list[dict]) -> dict:
    chgs = [float(r["change_pct"]) for r in rows if r.get("change_pct") is not None]
    n = len(chgs)
    if not n:
        return {"median_chg": None, "up_count": 0, "up_pct": None, "n": 0}
    chgs.sort()
    if n % 2:
        mid = chgs[n // 2]
    else:
        mid = (chgs[n // 2 - 1] + chgs[n // 2]) / 2
    up = sum(1 for x in chgs if x > 0)
    return {
        "median_chg": round(mid, 2),
        "up_count": up,
        "up_pct": round(100.0 * up / n, 0),
        "n": n,
    }


def group_rows(rows: list[dict]) -> dict:
    tagged = [attach_sector(r) for r in rows]
    by_sym = {r["symbol"]: r for r in tagged}
    macro = []
    for m in MACRO:
        item = dict(m)
        row = by_sym.get(m["symbol"])
        if row:
            item.update(row)
            item["listed"] = True
        else:
            item.update(
                {
                    "base": m["symbol"].replace("USDT", ""),
                    "price": None,
                    "change_pct": None,
                    "quote_volume": None,
                    "category": "",
                    "memo": "",
                    "listed": False,
                    "sector": "macro",
                    "sector_label": "대세판단",
                    "is_macro": True,
                }
            )
        macro.append(item)

    alts = [r for r in tagged if not r["is_macro"]]
    sectors = []
    for sid, label in SECTORS:
        chunk = [r for r in alts if r["sector"] == sid]
        sectors.append(
            {
                "id": sid,
                "label": label,
                "count": len(chunk),
                "rows": chunk,
                **_strength(chunk),
            }
        )
    return {
        "macro": macro,
        "sectors": sectors,
        "alt_count": len(alts),
        "alt_classified": sum(1 for r in alts if r["sector"] != "other"),
        "alt_strength": _strength(alts),
    }
