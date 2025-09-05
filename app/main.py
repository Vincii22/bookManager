from fastapi import FastAPI, Depends, Request, Form 
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session 
from . import models, database, crud, schemas 

models.Base.metadata.create_all(bind = database.engine)

app = FastAPI()

app.mount('/static', StaticFiles(directory='app/static'), name='static')
templates = Jinja2Templates(directory='app/templates')

def get_db():
    db = database.SessionLocal()
    try: 
        yield db 
    finally: 
        db.close()

@app.get('/')
def read_books(request: Request, db: Session = Depends(get_db)):
    books = crud.get_books(db)
    return templates.TemplateResponse('index.html', {"request": request, "books": books})

@app.get('/create')
def create_form(request: Request):
    return templates.TemplateResponse('create.html', {"request": request})

@app.post('/create')
def create_book(title: str = Form(...), author: str = Form(...), year: int = Form(...), db: Session = Depends(get_db)):
    crud.create_book(db, schemas.BookCreate(title=title, author=author, year=year))
    return RedirectResponse("/", status_code = 303)

@app.get('/update/{book_id}')
def update_form(book_id: int, request: Request, db: Session = Depends(get_db)):
    book = crud.get_book(db, book_id)
    return templates.TemplateResponse('update.html', {'request': request, 'book': book})

@app.post('/update/{book_id}')
def update_book(book_id: int, title: str = Form(...), author: str = Form(...), year: int = Form(...), db: Session = Depends(get_db)):
    crud.update_book(db, book_id, schemas.BookUpdate(title=title, author=author, year=year))
    return RedirectResponse('/', status_code = 303)

@app.get('/delete/{book_id}')
def delete_book(book_id: int, db: Session = Depends(get_db)):
    crud.delete_book(db, book_id)
    return RedirectResponse('/', status_code = 303)
