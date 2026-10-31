from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, Field, create_engine, Session, select

#Modelos
class CategoriaProducto(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nombre: str
    descripcion: str | None = None


class Producto(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nombre: str
    descripcion: str | None = None
    precio: float
    stock: int = 0
    img: str | None = None
    categoria_id: int = Field(foreign_key="categoriaproducto.id", index=True)

#Schema
class CategoriaCreate(SQLModel):
    nombre: str
    descripcion: str | None = None

class ProductoCreate(SQLModel):
    categoria_id: int
    nombre: str
    img: str | None = None
    descripcion: str | None = None
    precio: float
    stock: int = 0

class ProductoRead(SQLModel):
    id: int
    categoria_id: int
    nombre: str
    img: str | None = None
    precio: float
    stock: int = 0

sqlite_url = "sqlite:///tecnologia.db"

engine = create_engine(
    sqlite_url,
    echo=True,
)

def create_tables():
    SQLModel.metadata.create_all(engine)

create_tables()

app = FastAPI(title="Catálogo de tecnología")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/categorias", status_code=status.HTTP_201_CREATED, response_model=CategoriaProducto)
def crear_categoria(datos: CategoriaCreate):
    categoria = CategoriaProducto(
        nombre = datos.nombre,
        descripcion = datos.descripcion
    )
    with Session(engine) as session:
        session.add(categoria)
        session.commit()
        session.refresh(categoria)
        return categoria


@app.get("/categorias", response_model=list[CategoriaProducto])
def obtener_categorias():
    with Session(engine) as session:
        return session.exec(select(CategoriaProducto)).all()


@app.post("/productos", status_code=status.HTTP_201_CREATED, response_model=ProductoRead)
def crear_producto_con_categoria(datos: ProductoCreate):
    producto = Producto(
        nombre = datos.nombre,
        descripcion = datos.descripcion,
        img = datos.img,
        precio = datos.precio,
        stock = datos.stock,
        categoria_id = datos.categoria_id
    )
    with Session(engine) as session:
        if session.get(CategoriaProducto, datos.categoria_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada")
        session.add(producto)
        session.commit()
        session.refresh(producto)
        return producto

@app.get("/productos")
def obtener_productos():
    with Session(engine) as session:
        return session.exec(select(Producto)).all()

@app.get("/productos/{producto_id}")
def obtener_producto(producto_id: int):
    """
    Obtener producto por ID
    """
    with Session(engine) as session:
        producto = session.get(Producto, producto_id)
        if producto is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
        return producto

@app.delete("/productos/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_producto(producto_id: int):
    """
    Eliminar producto por ID
    """
    with Session(engine) as session:
        producto = session.get(Producto, producto_id)
        if not producto:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
        session.delete(producto)
        session.commit()
