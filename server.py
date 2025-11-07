# server.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from db_init import Base, Product
import os

# Configuración de Flask
app = Flask(__name__)
# Configuración de CORS para permitir peticiones desde cualquier origen (CORRECCIÓN CRUCIAL)
CORS(app, resources={r"/*": {"origins": "*"}})

# --- Configuración de Conexión a DB ---
# Usar la variable de entorno DATABASE_URL proporcionada por Render (por defecto a SQLite local)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///products.db")

# Adaptar la URL de la base de datos si es PostgreSQL para usar el driver psycopg
# CRUCIAL: Reemplazamos 'postgres://' por 'postgresql+psycopg://' para el driver moderno 'psycopg'
if DATABASE_URL.startswith("postgres://"):
    adapted_url = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
else:
    adapted_url = DATABASE_URL

# Configurar motor de SQLAlchemy
engine = create_engine(adapted_url, echo=False, future=True)

@app.route("/")
def index():
    """Ruta de salud simple para verificar que la API está funcionando."""
    return jsonify({"message": "🚀 API del Comparador de Precios (Python ready)"})

def product_to_dict(p):
    """Convierte un objeto Producto de SQLAlchemy a un diccionario amigable para JSON,
       incluyendo el cálculo de pronóstico con manejo de división por cero."""
    precios = [
        {"tienda": "Walmart", "precio": p.precio_walmart},
        {"tienda": "Chedraui", "precio": p.precio_chedraui},
        {"tienda": "Soriana", "precio": p.precio_soriana},
    ]
    
    forecast = None
    if p.predicted_price_next_year is not None:
        # Calcular el promedio actual
        avg_actual = (p.precio_walmart + p.precio_chedraui + p.precio_soriana) / 3.0
        
        # Integración de la lógica para manejar la división por cero (si todos los precios son 0)
        if avg_actual > 0:
            change_abs = p.predicted_price_next_year - avg_actual
            change_pct = (change_abs / avg_actual) * 100
            
            forecast = {
                "predicted_price": round(p.predicted_price_next_year, 2),
                "change_abs": round(change_abs, 2),
                "change_pct": round(change_pct, 2),
            }
        else:
             forecast = {
                 "predicted_price": round(p.predicted_price_next_year, 2),
                 "change_abs": round(p.predicted_price_next_year, 2),
                 "change_pct": "N/A", # No se puede calcular el porcentaje
             }
        
    return {
        "codigo": p.codigo, 
        "nombre": p.nombre, 
        "precios": precios, 
        "forecast": forecast
    }

@app.route("/api/search", methods=["GET"])
def api_search():
    """Busca productos por nombre o código en la base de datos."""
    q = request.args.get("q", "").strip().lower()
    if not q:
        return jsonify({"error": "Parámetro 'q' requerido"}), 400

    try:
        with Session(engine) as session:
            # Buscar productos donde el nombre contiene la query (sin distinción de mayúsculas) 
            # O el código coincide exactamente
            stmt = select(Product).where((Product.nombre.ilike(f"%{q}%")) | (Product.codigo == q))
            res = session.execute(stmt).scalars().all()
            
            if not res:
                return jsonify({"message": "No se encontraron productos"}), 404
                
            # Convertir resultados a formato JSON
            return jsonify([product_to_dict(p) for p in res])
            
    except Exception as e:
        print(f"Error en la búsqueda: {e}")
        # Usamos el formato detallado para el error, como en tu solicitud
        return jsonify({"error": "Error interno del servidor", "details": str(e)}), 500


@app.route("/api/product", methods=["POST"])
def api_add_product():
    """Añade un nuevo producto o actualiza uno existente por código."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON faltante en la solicitud"}), 400

    codigo = data.get("codigo")
    if not codigo:
        return jsonify({"error": "El campo 'codigo' es obligatorio"}), 400
        
    try:
        with Session(engine) as session:
            # Buscar si el producto ya existe
            existing = session.execute(select(Product).where(Product.codigo == codigo)).scalars().first()
            
            if existing:
                # Actualizar producto existente
                for k, v in data.items():
                    if hasattr(existing, k) and v is not None:
                         # Intenta convertir a float si parece ser un precio, para mayor robustez
                        if k.startswith('precio_') or k == 'predicted_price_next_year':
                            try:
                                v = float(v)
                            except (ValueError, TypeError):
                                # Ignorar o registrar error si el valor no es un número válido
                                continue
                        setattr(existing, k, v)
                session.commit()
                return jsonify({"message": f"✅ Producto con código {codigo} actualizado"}), 200
            else:
                # Añadir nuevo producto
                session.add(Product(**data))
                session.commit()
                return jsonify({"message": f"🆕 Producto con código {codigo} añadido"}), 201
                
    except Exception as e:
        print(f"Error al añadir/actualizar producto: {e}")
        # Usamos el formato detallado para el error, como en tu solicitud
        return jsonify({"error": "Error interno del servidor", "details": str(e)}), 500

# Esta sección NO se usa en Render (usa Gunicorn en su lugar)
# Pero se mantiene para pruebas locales.
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)