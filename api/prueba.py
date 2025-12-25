from sqlalchemy import create_engine

engine = create_engine("postgresql://postgres:Dimichev3.@localhost:5432/test")

try:
    with engine.connect() as connection:
        print("✅ Conexión exitosa a la base de datos")
except Exception as e:
    print(f"❌ Error al conectar: {e}")