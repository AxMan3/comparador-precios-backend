# server.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from db_init import Base, Product
import os

# Inicializar Flask y habilitar CORS
app = Flask(__name__)
CORS(app)

# Configurar la base de datos
DB_FILE = "products.db"
engine = create_engine(f"sqlite:///{DB_FILE}", echo=False, future=True)


@app.route("/")
def index():
    return jsonify({
        "message": "🚀 API del Comparador de Precios funcionando correctamente."
    })


def product_to_dict(p):
    """Convierte un objeto Product en un diccionario JSON listo para devolver."""
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
            "change_pct": round(((p.predicted_price_next_year - avg_actual) / avg_actual) * 100, 2)
        }
    return {
        "codigo": p.codigo,
        "nombre": p.nombre,
        "precios": precios,
        "forecast": forecast
    }


@app.route("/api/search", methods=["GET"])
def api_search():
    """Buscar un producto por nombre o código."""
    q = request.args.get("q", "").strip().lower()
    if q == "":
        return jsonify({"error": "Parámetro 'q' requerido"}), 400

    with Session(engine) as session:
        stmt = select(Product).where(
            (Product.nombre.ilike(f"%{q}%")) | (Product.codigo == q)
        )
        res = session.execute(stmt).scalars().all()

        if not res:
            return jsonify({"message": "No se encontraron productos"}), 404

        response = [product_to_dict(p) for p in res]
        return jsonify(response), 200


@app.route("/api/product", methods=["POST"])
def api_add_product():
    """Añadir o actualizar un producto desde JSON."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON faltante"}), 400

    codigo = data.get("codigo")
    nombre = data.get("nombre")

    try:
        with Session(engine) as session:
            stmt = select(Product).where(Product.codigo == codigo)
            existing = session.execute(stmt).scalars().first()

            if existing:
                # Actualizar producto existente
                existing.nombre = nombre or existing.nombre
                existing.precio_walmart = float(data.get("precio_walmart", existing.precio_walmart))
                existing.precio_chedraui = float(data.get("precio_chedraui", existing.precio_chedraui))
                existing.precio_soriana = float(data.get("precio_soriana", existing.precio_soriana))
                existing.predicted_price_next_year = data.get("predicted_price_next_year", existing.predicted_price_next_year)
                session.commit()
                return jsonify({"message": "✅ Producto actualizado"}), 200
            else:
                # Crear nuevo producto
                newp = Product(
                    codigo=codigo,
                    nombre=nombre,
                    precio_walmart=float(data.get("precio_walmart", 0)),
                    precio_chedraui=float(data.get("precio_chedraui", 0)),
                    precio_soriana=float(data.get("precio_soriana", 0)),
                    predicted_price_next_year=data.get("predicted_price_next_year")
                )
                session.add(newp)
                session.commit()
                return jsonify({"message": "🆕 Producto añadido"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    if not os.path.exists(DB_FILE):
        print("⚠️ Base de datos no encontrada. Ejecuta db_init.py primero para crear products.db")
    app.run(host="0.0.0.0", port=5000, debug=True)