#!/usr/bin/env python3
"""Turn an rAthena item script into description lines a person can read.

The script is run, not pattern-matched: a small interpreter executes it once per
refine level (0..10, or 0..15 for renewal scripts) and at base level 175 and 99,
and each bonus is then described by how its value moves with refine ("ATK +4 per
refine level", "From refine +7: ..."). Conditions it cannot decide (the
character's class, the weapon a card sits in) split the script and label the
lines they guard. Anything it does not know is shown as the script line itself,
so nothing is hidden.

  python3 itemdesc.py --rathena ../../../rathena-level175    # print every converted item and card, before and after

build_iteminfo.py uses it for the client's item descriptions; the level-175 run's status page for
the before and after of each item and card.
"""
import functools
import glob
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
RATHENA = os.environ.get("RATHENA_DIR", os.path.normpath(os.path.join(HERE, "../../../rathena-level175")))   # names of skills and items; set before the first describe()


# ---------------------------------------------------------------- names
@functools.lru_cache(None)
def _db_names(pattern, key):
    names = {}
    for path in glob.glob(os.path.join(RATHENA, pattern)):
        try:
            text = open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for m in re.finditer(r"- Id: (\d+)\s*\n\s+%s: (\S+)\s*\n\s+(?:Name|Description): ([^\n]+)" % key, text):
            names.setdefault(m.group(2), m.group(3).strip())
            names.setdefault(m.group(1), m.group(3).strip())
    return names


def skill_name(s):
    s = str(s).strip('"')
    return _db_names("db/*/skill_db.yml", "Name").get(s) or re.sub(r"^[A-Z]{2,3}_", "", s).replace("_", " ").title()


def item_name(s):
    s = str(s).strip('"')
    return _db_names("db/*/item_db*.yml", "AegisName").get(s) or human(s)


RACES = {"DemiHuman": "Demi-Human", "Demihuman": "Demi-Human", "All": "every race", "Player_Human": "human players",
         "Player_Doram": "Doram players", "Formless": "Formless", "Brute": "Brute"}


def human(c):
    """RC_DemiHuman -> Demi-Human, Ele_Fire -> Fire, W_2HSTAFF -> two-handed staff."""
    c = str(c).strip('"')
    for pre, table in (("RC2_", {}), ("RC_", RACES), ("Ele_", {"All": "every element"}), ("Size_", {"All": "every size"}),
                       ("Class_", {"Normal": "normal monsters", "Boss": "boss monsters", "All": "every monster"}),
                       ("Eff_", {}), ("Job_", {}), ("EAJ_", {}), ("W_", {"2HSTAFF": "two-handed staff", "1HSWORD": "one-handed sword",
                        "2HSWORD": "two-handed sword", "1HSPEAR": "one-handed spear", "2HSPEAR": "two-handed spear",
                        "1HAXE": "one-handed axe", "2HAXE": "two-handed axe", "KNUCKLE": "knuckle"}), ("EF_", {})):
        if c.startswith(pre):
            rest = c[len(pre):]
            if rest in table:
                return table[rest]
            rest = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", rest).replace("_", " ")
            return rest.lower() if pre == "W_" else rest.title() if pre == "EAJ_" else rest
    if re.fullmatch(r"[A-Z]{2,3}_[A-Z0-9_]+", c):
        return skill_name(c)
    return c


# ---------------------------------------------------------------- tokens / parser
TOKEN = re.compile(r'\s*(?:(//[^\n]*|/\*.*?\*/)|("(?:\\.|[^"\\])*")|(\d+)|(\.@\w+|\.?\w+)|(\|\||&&|==|!=|<=|>=|\+=|-=|\*=|/=|[-+*/%<>!?:(){},;=|&]))')


def tokens(text):
    out, pos = [], 0
    while pos < len(text):
        m = TOKEN.match(text, pos)
        if not m or m.end() == pos:
            if text[pos:].strip():
                out.append(("op", text[pos]))
            pos += 1
            continue
        pos = m.end()
        if m.group(1):
            continue
        if m.group(2):
            out.append(("str", bytes(m.group(2)[1:-1], "utf-8").decode("unicode_escape")))
        elif m.group(3):
            out.append(("num", int(m.group(3))))
        elif m.group(4):
            out.append(("id", m.group(4)))
        elif m.group(5):
            out.append(("op", m.group(5)))
    return out


class Parser:
    def __init__(self, text):
        self.t, self.i = tokens(text), 0

    def peek(self, k=0):
        return self.t[self.i + k] if self.i + k < len(self.t) else ("eof", None)

    def take(self, val=None):
        tok = self.peek()
        if val is not None and tok[1] != val:
            raise SyntaxError("expected %r, got %r" % (val, tok[1]))
        self.i += 1
        return tok

    def block(self):
        stmts = []
        while self.peek()[0] != "eof" and self.peek()[1] != "}":
            stmts.append(self.stmt())
        return stmts

    def stmt(self):
        start = self.i
        kind, val = self.peek()
        if val == "{":
            self.take()
            body = self.block()
            self.take("}")
            return ("block", body)
        if val == ";":
            self.take()
            return ("block", [])
        if val == "if":
            self.take()
            self.take("(")
            cond = self.expr()
            self.take(")")
            then = self.stmt()
            other = None
            if self.peek()[1] == "else":
                self.take()
                other = self.stmt()
            return ("if", cond, then, other)
        if kind == "id" and val.startswith(".@") and self.peek(1)[1] in ("=", "+=", "-=", "*=", "/="):
            self.take()
            op = self.take()[1]
            e = self.expr()
            self.take(";")
            return ("set", val, op, e)
        if kind == "id":
            self.take()
            args = []
            while self.peek()[1] not in (";", "eof"):
                args.append(self.expr())
                if self.peek()[1] == ",":
                    self.take()
                elif self.peek()[1] != ";":
                    break
            self.take(";")
            return ("cmd", val, args, self.raw(start))
        self.take()
        return ("block", [])

    def raw(self, start):
        return " ".join(str(v) for _, v in self.t[start:self.i])

    # precedence climbing
    BIN = [("||",), ("&&",), ("|",), ("&",), ("==", "!="), ("<", "<=", ">", ">="), ("+", "-"), ("*", "/", "%")]

    def expr(self):
        c = self.binary(0)
        if self.peek()[1] == "?":
            self.take()
            a = self.expr()
            self.take(":")
            b = self.expr()
            return ("?", c, a, b)
        return c

    def binary(self, level):
        if level == len(self.BIN):
            return self.unary()
        left = self.binary(level + 1)
        while self.peek()[0] == "op" and self.peek()[1] in self.BIN[level]:
            op = self.take()[1]
            left = ("bin", op, left, self.binary(level + 1))
        return left

    def unary(self):
        if self.peek()[1] in ("-", "!", "+"):
            op = self.take()[1]
            return ("un", op, self.unary())
        return self.primary()

    def primary(self):
        kind, val = self.take()
        if val == "(":
            e = self.expr()
            self.take(")")
            return e
        if kind in ("num", "str"):
            return (kind, val)
        if kind == "id" and self.peek()[1] == "(":
            self.take()
            args = []
            while self.peek()[1] != ")":
                args.append(self.expr())
                if self.peek()[1] == ",":
                    self.take()
            self.take(")")
            return ("call", val, args)
        return ("id", val)


# ---------------------------------------------------------------- evaluation
class Unk:
    """A value the description cannot fix: the character's stats, class or other gear.
    per = (amount, every, what) when it is a plain "amount per every what" (5 per 20 DEX)."""
    def __init__(self, text, per=None):
        self.per = per
        self.text = text if per is None else per_text(per)

    def __repr__(self):
        return self.text

    def __eq__(self, other):
        return isinstance(other, Unk) and other.text == self.text

    def __hash__(self):
        return hash(self.text)


def per_text(per, unit=""):
    n, d, what = per
    return "%s%s per %s%s" % (n, unit, "%d " % d if d != 1 else "", what)


STAT = {"bStr": "STR", "bAgi": "AGI", "bVit": "VIT", "bInt": "INT", "bDex": "DEX", "bLuk": "LUK"}


def cdiv(a, b):
    if b == 0:
        return 0
    q = abs(a) // abs(b)
    return q if (a >= 0) == (b > 0) else -q


def utext(v):
    return v.text if isinstance(v, Unk) else str(v)


def ev(e, env):
    k = e[0]
    if k in ("num", "str"):
        return e[1]
    if k == "id":
        n = e[1]
        if n.startswith(".@"):
            return env["vars"].get(n, 0)
        if n == "BaseLevel":
            return env["level"]
        if n == "JobLevel":
            return 70
        if n in ("BaseClass", "Class", "BaseJob"):
            return Unk("class")
        if n == "EAJ_UPPERMASK":
            return -1   # (eaclass() & EAJ_UPPERMASK): the class line, whatever the rank
        return n   # a constant: RC_Plant, BF_WEAPON, ...
    if k == "call":
        f, a = e[1], [ev(x, env) for x in e[2]]
        if f == "eaclass":
            return Unk("class")
        if f == "getrefine":
            return env["refine"]
        if f == "getequiprefinerycnt":
            env["labels"].add("weapon refine")
            return env["refine"]
        if f in ("min", "max") and all(isinstance(x, int) for x in a):
            return (min if f == "min" else max)(a)
        if f == "pow" and all(isinstance(x, int) for x in a):
            return a[0] ** a[1]
        if f == "readparam" and a and a[0] in STAT:
            return Unk(None, (1, 1, STAT[a[0]]))
        if f == "getskilllv":
            return Unk(None, (1, 1, "level of %s" % skill_name(a[0])))
        if f == "getiteminfo" and len(a) > 1 and isinstance(a[0], Unk):
            return Unk(a[0].text)
        if f == "getequipid":
            where = {"EQI_COMPOUND_ON": "the item it is slotted in", "EQI_HAND_R": "the weapon"}.get(a[0] if a else "", "the gear")
            return Unk(where)
        return Unk("%s(%s)" % (f, ", ".join(utext(x) for x in a)))
    if k == "un":
        v = ev(e[2], env)
        if isinstance(v, Unk):
            return Unk(("not " if e[1] == "!" else e[1]) + v.text)
        return -v if e[1] == "-" else (int(not v) if e[1] == "!" else v)
    if k == "?":
        c = ev(e[1], env)
        if isinstance(c, Unk):
            return Unk("%s if %s, else %s" % (utext(ev(e[2], env)), c.text, utext(ev(e[3], env))))
        return ev(e[2] if c else e[3], env)
    if k == "bin":
        op, a, b = e[1], ev(e[2], env), ev(e[3], env)
        if isinstance(a, int) and isinstance(b, int):
            return {"+": lambda: a + b, "-": lambda: a - b, "*": lambda: a * b, "/": lambda: cdiv(a, b),
                    "%": lambda: a % b if b else 0, "<": lambda: int(a < b), "<=": lambda: int(a <= b),
                    ">": lambda: int(a > b), ">=": lambda: int(a >= b), "==": lambda: int(a == b),
                    "!=": lambda: int(a != b), "&&": lambda: int(bool(a and b)), "||": lambda: int(bool(a or b)),
                    "|": lambda: a | b, "&": lambda: a & b}[op]()
        if op == "&" and isinstance(a, Unk) and b == -1:
            return a
        if isinstance(a, str) and isinstance(b, str) and op == "|":
            return a + "|" + b
        if isinstance(a, str) and isinstance(b, str) and op in ("==", "!="):
            return int((a == b) == (op == "=="))
        if op in ("==", "!=") and isinstance(a, Unk):
            if a.text == "class":
                return Unk("%s%s class line" % ("not the " if op == "!=" else "the ", human(b)) if op == "!=" else "%s class line" % human(b))
            return Unk("%s is %sa %s" % (a.text, "not " if op == "!=" else "", human(b)))
        if op in ("&&", "||"):
            if isinstance(a, int):
                return (b if a else 0) if op == "&&" else (1 if a else b)
            if isinstance(b, int):
                return (a if b else 0) if op == "&&" else (1 if b else a)
            return Unk("%s %s %s" % (a.text, "and" if op == "&&" else "or", b.text))
        if op == "*" and isinstance(b, Unk) and isinstance(a, int):
            a, b = b, a
        if op == "*" and isinstance(a, Unk) and a.per and isinstance(b, int):
            return Unk(None, (a.per[0] * b, a.per[1], a.per[2]))
        if op == "/" and isinstance(a, Unk) and a.per and isinstance(b, int) and b:
            n, d, what = a.per
            return Unk(None, (n // b, d, what)) if n % b == 0 else Unk(None, (n, d * b, what))
        if op in ("<", "<=", ">", ">="):
            return Unk("%s %s %s" % (utext(a), op, utext(b)))
        return Unk("%s %s %s" % (utext(a), op, utext(b)))
    return Unk("?")


# ---------------------------------------------------------------- execution with forks
def run(stmts, env, ctx, out):
    for s in stmts:
        execute(s, env, ctx, out)


def execute(s, env, ctx, out):
    k = s[0]
    if k == "block":
        run(s[1], env, ctx, out)
    elif k == "set":
        v = ev(s[3], env)
        old = env["vars"].get(s[1], 0)
        if s[2] != "=":
            if isinstance(v, int) and isinstance(old, int):
                v = {"+=": old + v, "-=": old - v, "*=": old * v, "/=": cdiv(old, v)}[s[2]]
            else:
                v = Unk("%s %s %s" % (utext(old), s[2][0], utext(v)))
        env["vars"][s[1]] = v
    elif k == "if":
        c = ev(s[1], env)
        if isinstance(c, Unk):
            # Both ways: each branch's lines carry the condition. Variables set in either
            # are taken from the "yes" side, which is the one the lines describe.
            run_branch(s[2], env, ctx + (c.text,), out)
            if s[3] is not None:
                run_branch(s[3], env, ctx + ("otherwise",), out)
        elif c:
            execute(s[2], env, ctx, out)
        elif s[3] is not None:
            execute(s[3], env, ctx, out)
    elif k == "cmd":
        command(s, env, ctx, out)


def run_branch(stmt, env, ctx, out):
    saved = dict(env["vars"])
    execute(stmt, env, ctx, out)
    if ctx[-1] == "otherwise":
        env["vars"] = saved


def command(s, env, ctx, out):
    name, args, raw = s[1], [ev(a, env) for a in s[2]], s[3]
    if name.startswith("bonus") and name != "bonus_script" and args:
        out.append((ctx, args[0], tuple(args[1:])))
    elif name.startswith("autobonus") and args and isinstance(args[0], str):
        inner = describe_once(args[0], env)
        out.append((ctx, name, (" ".join(inner),) + tuple(a for a in args[1:4] if not (isinstance(a, str) and a.startswith("{")))))
    elif name == "skill":
        out.append((ctx, "skill", tuple(args)))
    elif name in ("specialeffect2", "specialeffect", "end"):
        pass
    else:
        out.append((ctx, "raw", (raw,)))


def describe_once(script, env):
    out = []
    sub = dict(env, vars=dict(env["vars"]))
    run(Parser(script).block(), sub, (), out)
    return ["; ".join([line(n, a, None) for _, n, a in out])]


# ---------------------------------------------------------------- one bonus -> words
def pct(v, scale=1, unit="%"):
    if isinstance(v, Unk):
        return "+" + (per_text(v.per, unit) if v.per else v.text + unit)
    x = v / scale
    s = ("%g" % x)
    return ("+" if x > 0 else "") + s + unit


def flat(v):
    return pct(v, 1, "")


def less(v, scale=1, unit="%"):
    """A reduction written as a positive number in the script (bSubRace 30 -> -30 %)."""
    if isinstance(v, Unk):
        return "-" + (per_text(v.per, unit) if v.per else v.text + unit)
    return pct(-v, scale, unit)


B1 = {"bStr": ("STR", flat), "bAgi": ("AGI", flat), "bVit": ("VIT", flat), "bInt": ("INT", flat), "bDex": ("DEX", flat),
      "bLuk": ("LUK", flat), "bAllStats": ("All stats", flat), "bMaxHP": ("Max HP", flat), "bMaxSP": ("Max SP", flat),
      "bMaxHPrate": ("Max HP", pct), "bMaxSPrate": ("Max SP", pct), "bBaseAtk": ("ATK", flat), "bAtk": ("ATK", flat),
      "bAtkRate": ("ATK", pct), "bMatk": ("MATK", flat), "bMatkRate": ("MATK", pct), "bDef": ("DEF", flat),
      "bMdef": ("MDEF", flat), "bDefRate": ("DEF", pct), "bMdefRate": ("MDEF", pct), "bHit": ("HIT", flat),
      "bFlee": ("FLEE", flat), "bFlee2": ("Perfect dodge", flat), "bCritical": ("CRIT", flat),
      "bCritAtkRate": ("Critical damage", pct), "bAspd": ("ASPD", flat), "bAspdRate": ("ASPD", pct),
      "bLongAtkRate": ("Ranged physical damage", pct), "bShortAtkRate": ("Melee physical damage", pct),
      "bCastrate": ("Cast time", pct), "bVariableCastrate": ("Variable cast time", pct),
      "bFixedCastrate": ("Fixed cast time", pct), "bDelayrate": ("After-cast delay", pct),
      "bHealPower": ("Healing done", pct), "bHealPower2": ("Healing received", pct),
      "bHPrecovRate": ("Natural HP recovery", pct), "bSPrecovRate": ("Natural SP recovery", pct),
      "bUseSPrate": ("SP cost of skills", pct), "bHPGainValue": ("HP regained per monster killed in melee", flat),
      "bSPGainValue": ("SP regained per monster killed in melee", flat), "bSPDrainValue": ("SP regained per physical hit", flat),
      "bHPDrainValue": ("HP regained per physical hit", flat), "bPerfectHitRate": ("Chance to always hit", pct),
      "bSplashRange": ("Normal attacks also hit around the target, range", flat),
      "bBreakArmorRate": ("Chance to break the target's armor", lambda v: pct(v, 100)),
      "bBreakWeaponRate": ("Chance to break the target's weapon", lambda v: pct(v, 100)),
      "bMagicDamageReturn": ("Chance to reflect magic", pct), "bShortWeaponDamageReturn": ("Melee damage reflected", pct),
      "bLongWeaponDamageReturn": ("Ranged damage reflected", pct), "bNoKnockback": None}
B0 = {"bUnbreakableWeapon": "The weapon cannot break", "bUnbreakableArmor": "The armor cannot break",
      "bNoCastCancel": "Casting cannot be interrupted", "bNoKnockback": "Cannot be knocked back",
      "bNoGemStone": "Skills need no gemstones", "bIntravision": "Sees hidden enemies", "bNoSizeFix": "No size penalty"}


def line(name, args, _):
    a = list(args)
    v = a[-1] if a else None
    if name == "raw":
        return "(script: %s)" % a[0]
    if name == "skill":
        lv = a[1] if len(a) > 1 else 1
        if isinstance(lv, Unk) and lv.per:
            return "Can use %s, at the %s" % (skill_name(a[0]), lv.per[2])
        return "Can use %s level %s" % (skill_name(a[0]), utext(lv))
    if name in B0:
        return B0[name]
    if name == "bAtkEle":
        return "Weapon element: %s" % human(a[0])
    if name == "bDefEle":
        return "Armor element: %s" % human(a[0])
    if name in B1 and B1[name]:
        lab, f = B1[name]
        return "%s %s" % (lab, f(v))
    t = a[0] if a else ""
    two = {
        "bAddRace": lambda: "Physical damage against %s %s" % (human(t), pct(v)),
        "bAddRace2": lambda: "Physical damage against %s monsters %s" % (human(t), pct(v)),
        "bAddClass": lambda: "Physical damage against %s %s" % (human(t), pct(v)),
        "bAddEle": lambda: "Physical damage against %s-element targets %s" % (human(t), pct(v)),
        "bAddSize": lambda: "Physical damage against %s targets %s" % (human(t).lower(), pct(v)),
        "bMagicAddRace": lambda: "Magic damage against %s %s" % (human(t), pct(v)),
        "bMagicAddRace2": lambda: "Magic damage against %s monsters %s" % (human(t), pct(v)),
        "bMagicAddClass": lambda: "Magic damage against %s %s" % (human(t), pct(v)),
        "bMagicAddEle": lambda: "Magic damage against %s-element targets %s" % (human(t), pct(v)),
        "bMagicAddSize": lambda: "Magic damage against %s targets %s" % (human(t).lower(), pct(v)),
        "bMagicAtkEle": lambda: "%s magic damage %s" % (human(t), pct(v)),
        "bSubRace": lambda: "Damage taken from %s %s" % (human(t), less(v)),
        "bSubRace2": lambda: "Damage taken from %s monsters %s" % (human(t), less(v)),
        "bSubClass": lambda: "Damage taken from %s %s" % (human(t), less(v)),
        "bSubEle": lambda: "Damage taken from %s attacks %s" % (human(t) if t != "Ele_All" else "all elements'", less(v)),
        "bSubSize": lambda: "Damage taken from %s monsters %s" % (human(t).lower(), less(v)),
        "bResEff": lambda: "Resistance to %s %s" % (human(t), pct(v, 100)),
        "bCriticalAddRace": lambda: "CRIT against %s %s" % (human(t), flat(v)),
        "bIgnoreDefRaceRate": lambda: "Ignores %s%% of %s targets' DEF" % (utext(v), human(t)),
        "bIgnoreMdefRaceRate": lambda: "Ignores %s%% of %s targets' MDEF" % (utext(v), human(t)),
        "bAddItemHealRate": lambda: "Healing from %s %s" % (item_name(t), pct(v)),
        "bAddItemGroupHealRate": lambda: "Healing from %s items %s" % (human(t), pct(v)),
        "bAddMonsterDropItem": lambda: "Monsters killed drop %s (%s chance)" % (item_name(t), pct(v, 100)[1:]),
        "bHPRegenRate": lambda: "Regain %s HP every %g s" % (utext(a[0]), a[1] / 1000),
        "bSPRegenRate": lambda: "Regain %s SP every %g s" % (utext(a[0]), a[1] / 1000),
        "bWeaponDamageRate": lambda: "Damage with a %s %s" % (human(t), pct(v)),
        "bSkillAtk": lambda: "%s damage %s" % (skill_name(t), pct(v)),
        "bSkillHeal": lambda: "Healing by %s %s" % (skill_name(t), pct(v)),
        "bSkillCooldown": lambda: "%s cooldown %s" % (skill_name(t), pct(v, 1000, " s")),
        "bSkillUseSP": lambda: "%s SP cost %s" % (skill_name(t), flat(-v) if isinstance(v, int) else utext(v)),
        "bSkillUseSPrate": lambda: "%s SP cost %s" % (skill_name(t), less(v)),
        "bSkillVariableCast": lambda: "%s variable cast time %s" % (skill_name(t), pct(v, 1000, " s")),
        "bSkillFixedCast": lambda: "%s fixed cast time %s" % (skill_name(t), pct(v, 1000, " s")),
        "bSkillCastrate": lambda: "%s cast time %s" % (skill_name(t), pct(v)),
        "bAddEff": lambda: "%s chance to inflict %s on the target%s" % (pct(a[1], 100)[1:], human(t), "" if len(a) < 3 else flag_txt(a[2])),
        "bAddEff2": lambda: "%s chance to inflict %s on yourself when attacking" % (pct(a[1], 100)[1:], human(t)),
        "bAddEffWhenHit": lambda: "When hit, %s chance to inflict %s on the attacker" % (pct(a[1], 100)[1:], human(t)),
        "bAutoSpell": lambda: "When attacking, %s chance to cast %s level %s" % (pct(a[2], 10)[1:], skill_name(t), utext(a[1])),
        "bAutoSpellWhenHit": lambda: "When hit, %s chance to cast %s level %s" % (pct(a[2], 10)[1:], skill_name(t), utext(a[1])),
        "bAutoSpellOnSkill": lambda: "When using %s, %s chance to cast %s level %s" % (skill_name(t), pct(a[3], 10)[1:], skill_name(a[1]), utext(a[2])),
        "autobonus": lambda: "When attacking%s, %s chance for %g s: %s" % (bf_txt(a[3] if len(a) > 3 else ""), pct(a[1], 10)[1:], a[2] / 1000, t),
        "autobonus2": lambda: "When hit%s, %s chance for %g s: %s" % (bf_txt(a[3] if len(a) > 3 else ""), pct(a[1], 10)[1:], a[2] / 1000, t),
        "autobonus3": lambda: "When using %s, %s chance for %g s: %s" % (skill_name(a[3]) if len(a) > 3 else "a skill", pct(a[1], 10)[1:], a[2] / 1000, t),
    }
    try:
        r = two.get(name, lambda: None)()
    except Exception:
        r = None
    return r or "(script: %s %s)" % (name, ", ".join(utext(x) for x in a))


def flag_txt(f):
    return " (to yourself)" if "ATF_SELF" in str(f) else ""


def bf_txt(f):
    f = str(f)
    kinds = [w for k, w in (("BF_SHORT", "in melee"), ("BF_LONG", "at range"), ("BF_MAGIC", "with magic"),
                            ("BF_NORMAL", "with normal attacks"), ("BF_WEAPON", "with weapons"), ("BF_SKILL", "with skills")) if k in f]
    return (" " + " or ".join(kinds)) if kinds else ""


# ---------------------------------------------------------------- the sweep over refine levels
VALUE_AT = {"bAutoSpell": 2, "bAutoSpellWhenHit": 2, "bAutoSpellOnSkill": 3, "bAddEff": 1, "bAddEff2": 1,
            "bAddEffWhenHit": 1, "bHPRegenRate": 0, "bSPRegenRate": 0, "autobonus": 1, "autobonus2": 1, "autobonus3": 1}
NO_VALUE = set(B0) | {"bAtkEle", "bDefEle", "raw", "skill"}


def collect(script, refine, level):
    env = {"refine": refine, "level": level, "vars": {}, "labels": set()}
    out = []
    run(Parser(script).block(), env, (), out)
    totals = {}
    for ctx, name, args in out:
        if name in NO_VALUE or not args:
            key, val = (ctx, name, args, None), 1
        else:
            i = VALUE_AT.get(name, len(args) - 1)
            i = min(i, len(args) - 1)
            key, val = (ctx, name, args[:i] + ("#",) + args[i + 1:], i), args[i]
        if isinstance(val, int) and isinstance(totals.get(key, 0), int):
            totals[key] = totals.get(key, 0) + val
        else:
            totals[key] = val
    return totals, env["labels"]


def with_value(key, v):
    ctx, name, args, i = key
    if i is None:
        return line(name, args, None)
    a = list(args)
    a[i] = v
    return line(name, tuple(a), None)


def word(rlab, n):
    return ("per %s level" % rlab) if n == 1 else ("per %d %s levels" % (n, rlab))


def amount(key, v):
    """The value as the line writes it, with its unit: '+30%', '-1.5 s'."""
    nums = re.findall(r"[-+][\d.]+(?: s|%)?", with_value(key, v))
    return nums[-1] if nums else signed(v)


def describe_key(key, vals, rlab):
    """vals: the value at refine 0..R (0 where the bonus is absent)."""
    R = len(vals) - 1
    if all(not isinstance(v, int) for v in vals if v != 0) and any(v != 0 for v in vals):
        last = next(v for v in reversed(vals) if v != 0)
        return with_value(key, last)
    if all(v == vals[0] for v in vals):
        return with_value(key, vals[0]) if (vals[0] or key[3] is None) else None
    if not all(isinstance(v, int) for v in vals):
        return with_value(key, vals[-1]) + " (at +%d)" % R
    first = next(r for r in range(R + 1) if vals[r] != vals[0])
    # a steady climb: from refine t on, c, then b more every n levels
    for t in sorted({0, first}):
        for n in range(1, 6):
            if t + n > R:
                continue
            c, b = vals[t], vals[t + n] - vals[t]
            if b and all(vals[r] == (vals[0] if r < t else c + b * ((r - t) // n)) for r in range(R + 1)):
                tail = "%s more %s (%s at +%d)" % (amount(key, b), word(rlab, n), amount(key, vals[R]), R)
                if t == 0:
                    return ("%s, and %s" % (with_value(key, c), tail)) if c else "%s %s (%s at +%d)" % (with_value(key, b), word(rlab, n), amount(key, vals[R]), R)
                start = "From %s +%d: " % (rlab, t)
                if vals[0] and c == vals[0] + b:
                    return "%s; from %s +%d on, %s" % (with_value(key, vals[0]), rlab, t, tail)
                if vals[0]:
                    return "%s; from %s +%d: %s at +%d, then %s" % (with_value(key, vals[0]), rlab, t, amount(key, c), t, tail)
                return start + "%s, and %s" % (with_value(key, c), tail)
    parts, prev = [], vals[0]
    for r in range(1, R + 1):
        if vals[r] != prev:
            parts.append((r, vals[r]))
            prev = vals[r]
    if vals[0] == 0 and len(parts) == 1:
        return "From %s +%d: %s" % (rlab, parts[0][0], with_value(key, parts[0][1]))
    head = with_value(key, vals[0]) if vals[0] else "%s from %s +%d" % (with_value(key, parts[0][1]), rlab, parts[0][0])
    rest = parts if vals[0] else parts[1:]
    if len(rest) > 6:   # a curve: a few points on it are enough to read
        at = dict(parts)
        cur, pts = vals[0], []
        for r in range(R + 1):
            cur = at.get(r, cur)
            if r in (4, 7, 10, 15) and r > (parts[0][0] if not vals[0] else 0):
                pts.append((r, vals[r]))
        rest = pts
    if rest:
        head += "; " + ", ".join("%s at +%d" % (amount(key, v), r) for r, v in rest)
    return head


def signed(v):
    return ("+%s" % v) if isinstance(v, int) and v > 0 else str(v)


@functools.lru_cache(4096)
def describe(script, max_refine=10):
    """Description lines for an item script: [(condition or "", line), ...]."""
    script = script or ""
    if not script.strip():
        return ()
    try:
        runs = [collect(script, r, 175) for r in range(max_refine + 1)]
        low = [collect(script, r, 99)[0] for r in range(max_refine + 1)]
    except Exception as ex:   # an unreadable script is shown as it is
        return tuple(("", "(script: %s)" % l.strip()) for l in script.split("\n") if l.strip()) + (("", "(could not read: %s)" % ex),)
    labels = set().union(*(l for _, l in runs))
    rlab = "weapon refine" if "weapon refine" in labels else "refine"
    keys = []
    for t, _ in runs:
        for k in t:
            if k not in keys:
                keys.append(k)
    lines = []
    for k in keys:
        if k[1] == "#":
            continue
        vals = [t.get(k, 0) for t, _ in runs]
        text = describe_key(k, vals, rlab)
        if not text:
            continue
        lv = [t.get(k, 0) for t in low]
        if lv != vals:
            alt = describe_key(k, lv, rlab)
            if alt and alt != text:
                text += "  [at base level 175; at 99: %s]" % alt
        lines.append((" · ".join(c[0].upper() + c[1:] for c in k[0]), text))
    return tuple(lines)


def describe_text(script, max_refine=10):
    out, last = [], None
    for ctx, text in describe(script, max_refine):
        if ctx != last:
            if ctx:
                out.append(ctx + ":")
            last = ctx
        out.append(("   " if ctx else "") + text)
    return "\n".join(out)


JOBS_ALL = {"Third_Upper": "transcendent third classes", "All_Third": "third classes", "Third": "third classes",
            "Fourth": "fourth classes", "Upper": "transcendent classes", "Normal": "normal classes", "Baby": "baby classes",
            "All_Upper": "transcendent classes", "All": "every class"}


def item_header(v):
    """The stat part of a client description, from an item_db entry."""
    bits = [("Type", (v.get("SubType") or v.get("Type") or "").replace("2h", "Two-handed ").replace("1h", "One-handed "))]
    for k, lab in (("Attack", "ATK"), ("MagicAttack", "MATK"), ("Defense", "DEF"), ("WeaponLevel", "Weapon level"),
                   ("Slots", "Slots"), ("EquipLevelMin", "Required level")):
        if v.get(k):
            bits.append((lab, str(v[k])))
    jobs = ", ".join(v.get("Jobs") or []) or "all jobs"
    cls = ", ".join(JOBS_ALL.get(c, c) for c in (v.get("Classes") or []))
    bits.append(("Jobs", jobs + (" (%s)" % cls if cls else "")))
    return bits


if __name__ == "__main__":
    import argparse, json
    ap = argparse.ArgumentParser()
    ap.add_argument("--rathena", default=RATHENA)
    RATHENA = ap.parse_args().rathena
    T = HERE
    for g in json.load(open(os.path.join(T, "equipment_compare.json"))):
        print("=" * 8, g["after"].get("Name", g["item"]))
        print("-- before\n" + describe_text(g["before"].get("Script"), 15))
        print("-- after\n" + describe_text(g["after"].get("Script")))
    for c in json.load(open(os.path.join(T, "cards_compare.json"))):
        print("=" * 8, c["card"])
        print("-- before\n" + describe_text(c["renewal"], 15))
        print("-- after\n" + describe_text(c["after"]))
