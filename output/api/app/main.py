from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import products, customers, orders, dashboard
from app.middleware.error_handler import add_exception_handlers

app = FastAPI(title="Product Inventory and Order Management API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(products.router, prefix="/api/v1/products", tags=["products"])
app.include_router(customers.router, prefix="/api/v1/customers", tags=["customers"])
app.include_router(orders.router, prefix="/api/v1/orders", tags=["orders"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"])

# Add global exception handlers
add_exception_handlers(app)

@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "healthy"}