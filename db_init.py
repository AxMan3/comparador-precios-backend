# db_init.py
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, Session
import os

DB_FILE = "products.db"
Base = declarative_base()


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    codigo = Column(String, unique=True, nullable=False)  # código de barras
    nombre = Column(String, nullable=False)
    precio_walmart = Column(Float, nullable=False)
    precio_chedraui = Column(Float, nullable=False)
    precio_soriana = Column(Float, nullable=False)
    predicted_price_next_year = Column(Float, nullable=True)  # precio previsto general (opcional)


def populate_sample(session):
    # Lista de productos reales (ejemplos). Agrega/edita según necesites.
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
        prod = Product(
            codigo=p["codigo"],
            nombre=p["nombre"],
            precio_walmart=p["precio_walmart"],
            precio_chedraui=p["precio_chedraui"],
            precio_soriana=p["precio_soriana"],
            predicted_price_next_year=p.get("predicted_price_next_year")
        )
        session.add(prod)
    session.commit()


def main():
    if os.path.exists(DB_FILE):
        print(f"{DB_FILE} ya existe. Si quieres recrearlo, borra el archivo y vuelve a ejecutar.")
        return

    engine = create_engine(f"sqlite:///{DB_FILE}", echo=False, future=True)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        populate_sample(session)

    print("✅ Base de datos creada y poblada con ejemplos en products.db")


if __name__ == "__main__":
    main()
