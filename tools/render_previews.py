"""Render the project's real Django templates WITHOUT Django, for quick visual previews.

Why: handy for design work or CI screenshots on machines where Django is not installed.
How: Django template syntax is translated to Jinja2 on the fly; data is fictional sample data
built from core/brands.py. Output: docs/screenshots/*.png

Usage:  python tools/render_previews.py
Needs:  jinja2, playwright (with chromium)
For pixel-perfect shots of the real app, run `seed_demo` and screenshot the dev server instead.
"""
import re
import sys
from datetime import date
from pathlib import Path
from types import SimpleNamespace as NS

from jinja2 import DictLoader, Environment

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from core.brands import BRANDS  # noqa: E402  (pure python, no Django needed)

OUT = ROOT / "docs" / "screenshots"
HTML = ROOT / "docs" / "_html"
STATIC = (ROOT / "static").as_uri()


# ------------------------------------------------------------------ django -> jinja
def convert(src):
    src = re.sub(r"{%\s*load [^%]*%}", "", src)
    src = re.sub(r"{%\s*static '([^']+)'\s*%}", lambda m: f"{STATIC}/{m.group(1)}", src)
    src = re.sub(r"{%\s*url [^%]*%}", "#", src)
    src = re.sub(r"{%\s*csrf_token\s*%}", "", src)
    src = re.sub(r'{%\s*now "Y"\s*%}', "2026", src)
    src = re.sub(r"{%\s*endblock \w+\s*%}", "{% endblock %}", src)
    src = re.sub(r"{%\s*empty\s*%}", "{% else %}", src)
    src = re.sub(r'\|default:("[^"]*"|[\w.]+)', r"|default(\1, true)", src)
    src = re.sub(r'\|date:"[^"]*"', "|dj_date", src)
    src = re.sub(r'\|floatformat:"[^"]*"', "|floatformat", src)
    src = re.sub(r"\|truncatechars:(\d+)", r"|truncate(\1)", src)
    src = re.sub(r"\|stringformat:'s'", "|string", src)
    return src


def make_env():
    loader = DictLoader({p.relative_to(ROOT / "templates").as_posix(): convert(p.read_text())
                         for p in (ROOT / "templates").rglob("*.html")})
    env = Environment(loader=loader, autoescape=False)
    env.filters["dj_date"] = lambda d: d.strftime("%b %d, %Y")
    env.filters["floatformat"] = lambda v: f"{float(v):.2f}".rstrip("0").rstrip(".") if float(v) % 1 else str(int(float(v)))
    return env


# ------------------------------------------------------------------ fake data
class FakeForm:
    def __init__(self, fields, errors=None):
        rows = []
        for label, kind, value in fields:
            if kind == "textarea":
                widget = f"<textarea rows='4'>{value}</textarea>"
            else:
                widget = f"<input type='{kind}' value='{value}'>"
            rows.append(f"<div><label>{label}:</label>{widget}</div>")
        self.as_div = "".join(rows)


def user(first, last, username, staff=False, email=""):
    full = f"{first} {last}".strip()
    return {"first_name": first, "last_name": last, "username": username, "is_staff": staff,
            "is_authenticated": True, "get_full_name": full, "email": email}


def sample(brand):
    cats, offers, pk = [], [], 1
    for ci, (cn, cd, items) in enumerate(brand.seed, 1):
        cats.append({"pk": ci, "name": cn, "description": cd, "offering_count": len(items)})
        for n, d, p, m in items:
            offers.append({"pk": pk, "name": n, "description": d, "price": p, "duration_months": m,
                           "is_active": True, "category": {"name": cn}})
            pk += 1
    people = [("Sam", "Example"), ("Alex", "Sample"), ("Jordan", "Demo"), ("Riley", "Test"), ("Casey", "Placeholder")]
    statuses = ["pending", "approved", "pending", "rejected", "approved", "pending"]
    reqs = []
    for i, st in enumerate(statuses):
        f, l = people[i % len(people)]
        reqs.append({"pk": i + 1, "customer": user(f, l, (f + "_" + l).lower()), "offering": offers[i % len(offers)],
                     "status": st, "get_status_display": st.capitalize(), "created_at": date(2026, 10, 28 - i)})
    custs = []
    for i, (f, l) in enumerate(people):
        u = user(f, l, f"{f}.{l}".lower(), email=f"{f}.{l}@example.com".lower())
        u.update({"pk": i + 1, "request_count": (i * 2) % 4 + 1,
                  "profile": {"location": ["Springfield", "Rivertown", "Lakeside", "Hilltop", "Bayview"][i]}})
        custs.append(u)
    tickets = [
        {"pk": 1, "customer": user("Sam", "Example", "sam"), "subject": "Question about billing",
         "message": "When will I be charged for the first period?", "response": "", "status": "open", "get_status_display": "Open"},
        {"pk": 2, "customer": user("Alex", "Sample", "alex"), "subject": "Change of plan",
         "message": "Can I switch to a different option mid-term?", "response": "Yes - send a new request and we will adjust it.",
         "status": "answered", "get_status_display": "Answered"},
    ]
    return cats, offers, reqs, custs, tickets


# ------------------------------------------------------------------ pages
def pages(brand):
    cats, offers, reqs, custs, tickets = sample(brand)
    staff = user("Morgan", "Admin", "morgan", staff=True)
    cust = user("Sam", "Example", "sam")
    anon = {"is_authenticated": False, "is_staff": False}
    return {
        "home": ("core/home.html", "home", anon, {"featured": offers[:3]}),
        "login": ("accounts/login.html", "login", anon, {"form": FakeForm([("Username", "text", ""), ("Password", "password", "")])}),
        "staff-dashboard": ("catalog/dashboard_staff.html", "dashboard", staff, {
            "customers": 128, "categories": len(cats), "offerings": len(offers), "total_requests": 342,
            "counts": {"pending": 41, "approved": 276, "rejected": 25}, "open_tickets": 7, "recent": reqs[:5]}),
        "staff-requests": ("catalog/request_list.html", "request-list", staff, {"object_list": reqs, "current_status": ""}),
        "staff-catalog": ("catalog/offering_list.html", "offering-list", staff, {"object_list": offers}),
        "staff-customers": ("catalog/customer_list.html", "customer-list", staff, {"customers": custs}),
        "staff-tickets": ("catalog/ticket_list_staff.html", "ticket-list", staff, {"object_list": tickets}),
        "customer-dashboard": ("catalog/dashboard_customer.html", "dashboard", cust, {
            "available": len(offers), "my_requests": 3, "my_approved": 1, "my_tickets": 2, "recent": reqs[:3]}),
        "customer-browse": ("catalog/browse.html", "browse", cust, {"offerings": offers, "categories": cats, "current_category": ""}),
        "customer-requests": ("catalog/my_requests.html", "my-requests", cust, {"requests_list": reqs[:4]}),
        "form-new-item": ("catalog/form.html", "offering-create", staff, {"title": "New item", "form": FakeForm([
            ("Category", "text", cats[0]["name"]), ("Name", "text", ""), ("Description", "textarea", ""),
            ("Price", "number", ""), ("Duration months", "number", "12")])}),
    }


PLAN = [  # (brand, page, viewport width)
    ("generic", "home"), ("tesla", "home"), ("google", "home"), ("microsoft", "home"), ("spotify", "home"),
    ("generic", "login"),
    ("tesla", "staff-dashboard"), ("tesla", "staff-requests"), ("tesla", "staff-catalog"),
    ("google", "staff-dashboard"), ("google", "staff-requests"), ("google", "staff-customers"),
    ("google", "staff-tickets"), ("google", "form-new-item"),
    ("microsoft", "customer-dashboard"), ("microsoft", "customer-requests"),
    ("spotify", "customer-browse"), ("tesla", "customer-browse"), ("google", "customer-browse"),
]


def main():
    from playwright.sync_api import sync_playwright

    OUT.mkdir(parents=True, exist_ok=True)
    HTML.mkdir(parents=True, exist_ok=True)
    env = make_env()
    shots = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1366, "height": 800})
        for slug, name in PLAN:
            brand = BRANDS[slug]
            tpl, url_name, usr, ctx = pages(brand)[name]
            ctx = dict(ctx, brand=brand, t=brand.terms, currency="$", all_brands=[], messages=[], user=usr,
                       request=NS(resolver_match=NS(url_name=url_name)), object=None)
            html = env.get_template(tpl).render(**ctx)
            f = HTML / f"{slug}-{name}.html"
            f.write_text(html)
            page.goto(f.as_uri())
            target = OUT / f"{slug}-{name}.png"
            page.screenshot(path=str(target), full_page=(name in ("home",)))
            shots.append(target)
            print("wrote", target.relative_to(ROOT))
        browser.close()


if __name__ == "__main__":
    main()
