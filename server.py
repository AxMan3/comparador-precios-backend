# server.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from db_init import Base, Product
import os

app = Flask(__name__)
CORS(app)

# Configurar conexión: usa PostgreSQL si DATABASE_URL está disponible
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///products.db")
engine = create_engine(DATABASE_URL, echo=False, future=True)

@app.route("/")
def index():
    return jsonify({"message": "🚀 API del Comparador de Precios (Python 3.13 ready)"})

def product_to_dict(p):
    precios = [
        {"tienda": "Walmart", "precio": p.precio_walmart},
        {"tienda": "Chedraui", "precio": p.precio_chedraui},
        {"tienda": "Soriana", "precio": p.precio_soriana},
    ]
    forecast = None
    if p.predicted_price_next_year:
        avg_actual = (p.precio_walmart + p.precio_chedraui + p.precio_soriana) / 3.0
        forecast = {
            "predicted_price": p.predicted_price_next_year,
            "change_abs": round(p.predicted_price_next_year - avg_actual, 2),
            "change_pct": round(((p.predicted_price_next_year - avg_actual) / avg_actual) * 100, 2),
        }
    return {"codigo": p.codigo, "nombre": p.nombre, "precios": precios, "forecast": forecast}

@app.route("/api/search", methods=["GET"])
def api_search():
    q = request.args.get("q", "").strip().lower()
    if not q:
        return jsonify({"error": "Parámetro 'q' requerido"}), 400

    with Session(engine) as session:
        stmt = select(Product).where((Product.nombre.ilike(f"%{q}%")) | (Product.codigo == q))
        res = session.execute(stmt).scalars().all()
        if not res:
            return jsonify({"message": "No se encontraron productos"}), 404
        return jsonify([product_to_dict(p) for p in res])

@app.route("/api/product", methods=["POST"])
def api_add_product():
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON faltante"}), 400

    codigo = data.get("codigo")
    try:
        with Session(engine) as session:
            existing = session.execute(select(Product).where(Product.codigo == codigo)).scalars().first()
            if existing:
                for k, v in data.items():
                    if hasattr(existing, k) and v is not None:
                        setattr(existing, k, v)
                session.commit()
                return jsonify({"message": "✅ Producto actualizado"}), 200
            else:
                session.add(Product(**data))
                session.commit()
                return jsonify({"message": "🆕 Producto añadido"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
