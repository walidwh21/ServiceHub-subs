from dataclasses import dataclass


@dataclass(frozen=True)
class Brand:
    slug: str
    name: str
    tagline: str
    hero_title: str
    hero_text: str
    primary: str
    primary_dark: str
    accent: str
    dark: str
    font: str
    terms: dict
    # ((category, description, ((offering, description, price, months), ...)), ...)
    seed: tuple = ()

    @property
    def initial(self):
        return self.name[:1]


def _terms(offering, offerings, request, requests, action, category="Category", categories="Categories"):
    return {
        "offering": offering,
        "offerings": offerings,
        "request": request,
        "requests": requests,
        "action": action,
        "category": category,
        "categories": categories,
        "customer": "Customer",
        "customers": "Customers",
    }


SANS = "'Helvetica Neue', Helvetica, Arial, sans-serif"

BRANDS = {
    "generic": Brand(
        slug="generic",
        name="ServiceHub",
        tagline="Plans, requests and support in one place.",
        hero_title="Manage every plan and request in one place",
        hero_text="Publish plans, let customers request them, approve in a click and answer questions without leaving the dashboard.",
        primary="#4f46e5", primary_dark="#3730a3", accent="#06b6d4", dark="#111827",
        font=SANS,
        terms=_terms("Plan", "Plans", "Request", "Requests", "Request this plan"),
        seed=(
            ("Starter", "Everything you need to get going.", (
                ("Basic", "Core features for individuals.", 9, 1),
                ("Plus", "More capacity and priority support.", 19, 1),
            )),
            ("Business", "For teams and growing companies.", (
                ("Team", "Shared workspace for up to 25 people.", 79, 12),
                ("Enterprise", "Custom limits, SSO and a dedicated manager.", 249, 12),
            )),
        ),
    ),
    "tesla": Brand(
        slug="tesla",
        name="Tesla Service Center",
        tagline="Keep your vehicle, home energy and charging running at their best.",
        hero_title="Service plans for every mile and every watt",
        hero_text="Reserve maintenance, energy and charging plans online. Approvals and updates appear in your dashboard.",
        primary="#e31937", primary_dark="#b3122b", accent="#393c41", dark="#171a20",
        font="Gotham, 'Helvetica Neue', Helvetica, Arial, sans-serif",
        terms=_terms("Service plan", "Service plans", "Reservation", "Reservations", "Reserve this plan", "Product line", "Product lines"),
        seed=(
            ("Vehicle care", "Maintenance and protection for your car.", (
                ("Annual Maintenance", "Tyre rotation, cabin filter and a full inspection.", 299, 12),
                ("Extended Warranty", "Coverage beyond the factory warranty period.", 1499, 48),
            )),
            ("Home energy", "Solar and storage care.", (
                ("Solar Roof Check-up", "Yearly panel inspection and performance report.", 149, 12),
                ("Powerwall Care", "Remote monitoring and priority repairs.", 199, 12),
            )),
            ("Charging", "Home and on-the-road charging.", (
                ("Home Charger Install", "Wall connector installation by a certified electrician.", 650, 1),
                ("Supercharging Pass", "Discounted fast-charging for a full year.", 399, 12),
            )),
        ),
    ),
    "google": Brand(
        slug="google",
        name="Google Workspace Admin",
        tagline="Subscriptions and licences for your whole organisation.",
        hero_title="Subscriptions that scale with your team",
        hero_text="Request Workspace, Cloud and device subscriptions, then follow approval status from one console.",
        primary="#1a73e8", primary_dark="#1557b0", accent="#34a853", dark="#202124",
        font="'Google Sans', Roboto, 'Helvetica Neue', Arial, sans-serif",
        terms=_terms("Subscription", "Subscriptions", "Subscription request", "Subscription requests", "Subscribe", "Product", "Products"),
        seed=(
            ("Workspace", "Email, meetings, docs and storage.", (
                ("Business Starter", "Custom email, 30 GB storage per user.", 7, 12),
                ("Business Standard", "2 TB storage, recording in meetings.", 14, 12),
                ("Enterprise", "Advanced security and unlimited storage options.", 23, 12),
            )),
            ("Cloud", "Infrastructure and data tools.", (
                ("Compute Credits", "Prepaid credits for virtual machines.", 500, 12),
                ("Storage 2 TB", "Extra object storage for backups.", 40, 12),
            )),
            ("Devices", "Hardware care.", (
                ("Device Care+", "Accidental damage cover for phones and tablets.", 12, 12),
            )),
        ),
    ),
    "microsoft": Brand(
        slug="microsoft",
        name="Microsoft Licensing Portal",
        tagline="Licences, cloud credits and gaming memberships.",
        hero_title="Licences made simple",
        hero_text="Request productivity licences and cloud credits for your people and track every approval.",
        primary="#0078d4", primary_dark="#005a9e", accent="#107c10", dark="#201f1e",
        font="'Segoe UI', 'Helvetica Neue', Arial, sans-serif",
        terms=_terms("Licence", "Licences", "Licence request", "Licence requests", "Request licence", "Suite", "Suites"),
        seed=(
            ("Productivity", "Office apps and collaboration.", (
                ("365 Business Basic", "Web apps, email and Teams.", 6, 12),
                ("365 Business Standard", "Desktop apps plus everything in Basic.", 13, 12),
            )),
            ("Cloud", "Azure usage.", (
                ("Azure Credits", "Prepaid credits for cloud services.", 1000, 12),
            )),
            ("Gaming", "Play on console and PC.", (
                ("Game Pass Ultimate", "Hundreds of games, online play included.", 17, 1),
            )),
        ),
    ),
    "spotify": Brand(
        slug="spotify",
        name="Spotify Membership Desk",
        tagline="Pick a membership, we handle the rest.",
        hero_title="Music for every kind of listener",
        hero_text="Choose individual, duo, family or student memberships and manage requests in one place.",
        primary="#1db954", primary_dark="#158a3e", accent="#b49bc8", dark="#121212",
        font="'Circular', 'Helvetica Neue', Helvetica, Arial, sans-serif",
        terms=_terms("Membership", "Memberships", "Join request", "Join requests", "Join now", "Tier", "Tiers"),
        seed=(
            ("Personal", "For one listener.", (
                ("Individual", "Ad-free music on demand.", 11, 1),
                ("Student", "Discounted plan with verification.", 6, 12),
            )),
            ("Shared", "For households.", (
                ("Duo", "Two accounts for a couple.", 15, 1),
                ("Family", "Up to six accounts, parental controls.", 17, 1),
            )),
        ),
    ),
}


def get_brand(slug):
    return BRANDS.get(slug) or BRANDS["generic"]
