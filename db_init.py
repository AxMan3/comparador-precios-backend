# db_init.py
from sqlalchemy import create_engine, Column, Integer, String, Float, text
from sqlalchemy.orm import declarative_base, Session
import os

# Usar PostgreSQL (Render proporcionará la variable DATABASE_URL)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///products.db")

# Base declarativa para los modelos
Base = declarative_base()


class Product(Base):
    """Modelo de datos para almacenar la información de los productos y sus precios."""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    codigo = Column(String, unique=True, nullable=False)
    nombre = Column(String, nullable=False)
    
    # Precios por tienda
    precio_walmart = Column(Float, nullable=False)
    precio_chedraui = Column(Float, nullable=False)
    precio_soriana = Column(Float, nullable=False)
    
    # Precio predicho (para el forecast)
    predicted_price_next_year = Column(Float, nullable=True)

    def __repr__(self):
        return f"Product(codigo='{self.codigo}', nombre='{self.nombre}')"


def populate_sample(session):
    """Inserta datos de ejemplo en la base de datos."""
    # Lista de productos de ejemplo.
    samples = [
        {"codigo": "75007614", "nombre": "Coca-Cola 600ml", "precio_walmart": 20.00, "precio_chedraui": 18.00, "precio_soriana": 19.50, "predicted_price_next_year": 20.00},
        {"codigo": "7501020565935", "nombre": "Leche Lala 1L Entera", "precio_walmart": 37.00, "precio_chedraui": 31.00, "precio_soriana": 32.90, "predicted_price_next_year": 35.00},
        {"codigo": "7500810029183", "nombre": "Pan Blanco Bimbo 620g", "precio_walmart": 55.00, "precio_chedraui": 44.00, "precio_soriana": 49.50, "predicted_price_next_year": 51.50},
        {"codigo": "7501071301698", "nombre": "Arroz Verde Valle 900g", "precio_walmart": 32.00, "precio_chedraui": 37.00, "precio_soriana": 32.90, "predicted_price_next_year": 35.00},
        {"codigo": "7501039120149", "nombre": "Aceite Nutrioli 946ml", "precio_walmart": 45.00, "precio_chedraui": 43.00, "precio_soriana": 40.90, "predicted_price_next_year": 44.50},
        {"codigo": "7501101525025", "nombre": "Huevos blancos Bachoco 12 pzas", "precio_walmart": 45.00, "precio_chedraui": 39.00, "precio_soriana": 46.90, "predicted_price_next_year": 45.00},
        {"codigo": "7501071301049", "nombre": "Frijol peruano Valle Verde 900g", "precio_walmart": 50.00, "precio_chedraui": 52.00, "precio_soriana": 53.20, "predicted_price_next_year": 54.00},
        {"codigo": "7501018314507", "nombre": "Spaghetti La Moderna 220g", "precio_walmart": 10.00, "precio_chedraui": 11.40, "precio_soriana": 12.50, "predicted_price_next_year": 11.50},
        {"codigo": "7501045403144", "nombre": "Atún Dolores En Agua 140g", "precio_walmart": 20.00, "precio_chedraui": 20.50, "precio_soriana": 20.90, "predicted_price_next_year": 21.50},
        {"codigo": "7501045400860", "nombre": "Atún Dolores En Agua 295g", "precio_walmart": 43.00, "precio_chedraui": 42.00, "precio_soriana": 41.90, "predicted_price_next_year": 44.00},
        {"codigo": "7501020510614", "nombre": "Lala Yogurt Natural De 1kg", "precio_walmart": 45.00, "precio_chedraui": 42.00, "precio_soriana": 40.00, "predicted_price_next_year": 44.00},
        {"codigo": "7501008023136", "nombre": "Kellogg's Corn Flakes Original 540g", "precio_walmart": 71.00, "precio_chedraui": 53.50, "precio_soriana": 70.90, "predicted_price_next_year": 67.50},
        {"codigo": "7501040005831", "nombre": "FUD Jamón Virginia De Pavo 290g", "precio_walmart": 52.00, "precio_chedraui": 43.00, "precio_soriana": 64.90, "predicted_price_next_year": 55.50},
        {"codigo": "7501055304745", "nombre": "Coca-Cola Refresco Original 3Lt", "precio_walmart": 43.00, "precio_chedraui": 44.00, "precio_soriana": 47.90, "predicted_price_next_year": 46.50},
        {"codigo": "7501020515350", "nombre": "Lala Leche Light 1Lt", "precio_walmart": 37.00, "precio_chedraui": 37.00, "precio_soriana": 39.50, "predicted_price_next_year": 39.50},
        {"codigo": "7501052474076", "nombre": "Clemente Jacques Mermelada de Fresa 470g", "precio_walmart": 25.00, "precio_chedraui": 35.00, "precio_soriana": 29.90, "predicted_price_next_year": 31.00},
        {"codigo": "7501059224827", "nombre": "Café soluble Nescafé Clásico 200g", "precio_walmart": 150.00, "precio_chedraui": 150.00, "precio_soriana": 149.00, "predicted_price_next_year": 155.50},
        {"codigo": "0034587020021", "nombre": "Sal La Fina refinada 1kg", "precio_walmart": 29.00, "precio_chedraui": 24.00, "precio_soriana": 24.90, "predicted_price_next_year": 27.00},
        {"codigo": "7500810022061", "nombre": "Pan Bimbo integral 620g", "precio_walmart": 51.00, "precio_chedraui": 59.00, "precio_soriana": 57.90, "predicted_price_next_year": 58.00},
        {"codigo": "7501000111800", "nombre": "Pan tostado Bimbo clásico 210g", "precio_walmart": 39.00, "precio_chedraui": 39.00, "precio_soriana": 39.80, "predicted_price_next_year": 41.00},
    ]
    for p in samples:
        # Crea la instancia del producto y la añade a la sesión
        session.add(Product(**p))
    session.commit()
    print("Muestra de productos insertada en la base de datos.")


def main():
    """Función principal para inicializar la base de datos."""
    print("Iniciando la creación y población de la base de datos...")
    
    # 1. Adaptar la URL de la base de datos
    # CRUCIAL: Reemplaza 'postgres://' por 'postgresql+psycopg://' para usar el driver moderno
    if DATABASE_URL.startswith("postgres://"):
        adapted_url = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
    else:
        adapted_url = DATABASE_URL # Si es SQLite (local) o ya está correcta, la deja igual.

    # 2. Crear el motor de la base de datos
    engine = create_engine(adapted_url, echo=False, future=True)
    
    # 3. Crear todas las tablas definidas en Base (si no existen)
    Base.metadata.create_all(engine)
    print("Tablas verificadas o creadas correctamente.")
    
    with Session(engine) as session:
        # 4. Verificar si la tabla ya está poblada de forma robusta
        try:
            # Usar text() y scalar_one() es la forma más robusta de contar en SQLAlchemy
            count = session.execute(text("SELECT COUNT(id) FROM products")).scalar_one()
        except Exception as e:
            # En caso de error (ej. tabla no encontrada, aunque create_all debería evitarlo)
            print(f"Error al contar registros: {e}. Asumiendo 0 para intentar poblar.")
            count = 0 
        
        # 5. Poblar solo si está vacía
        if count == 0:
            print("Base de datos vacía. Iniciando la carga de datos de muestra...")
            populate_sample(session)
            print(f"✅ Inicialización de DB completada. {len(session.query(Product).all())} productos cargados.")
        else:
            print(f"Base de datos ya poblada. Se encontraron {count} productos. No se insertarán duplicados.")

# El comando 'python db_init.py' ejecutará esta función
if __name__ == "__main__":
    main()