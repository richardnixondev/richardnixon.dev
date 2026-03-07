from ninja import NinjaAPI
from .routes import blog_router, portfolio_router, contact_router, home_router

api = NinjaAPI(
    title="richardnixon.dev API",
    version="1.0.0",
    urls_namespace="api",
)

api.add_router("/home", home_router)
api.add_router("/blog", blog_router)
api.add_router("/portfolio", portfolio_router)
api.add_router("/contact", contact_router)
