from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Path, HTTPException
from pydantic import BaseModel, Field, conint
from sqlalchemy.orm import Session
from starlette import status

from .auth import get_current_user
from ..database import SessionLocal
from ..models import Blogs

router = APIRouter(
    prefix='/api/blogs',
    tags=['Blogs']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class BlogsRequest(BaseModel):
    title: str = Field(min_length=3)
    content: str = Field(min_length=1, max_length=1000)
    timestamp: int = conint()

    class Config:
        json_schema_extra = {
            'example': {
                'title': 'A new Blog',
                'content': 'Welcome to Logistics Now',
                'timestamp': 123454323,
            }
        }


@router.get("", status_code=status.HTTP_200_OK)
async def retrieve_a_list_of_all_blog_post(user: user_dependency, db: db_dependency):
    blog_model = db.query(Blogs).filter(Blogs.auther == user.get('id'), Blogs.is_deleted == False).all()
    if blog_model is not None:
        return blog_model
    else:
        raise HTTPException(status_code=404, detail='Blogs not found')


@router.get("/{id}", status_code=status.HTTP_200_OK)
async def retrieve_details_of_a_specific_blog_post(user: user_dependency, db: db_dependency, id: int = Path(gt=0)):
    blog_model = db.query(Blogs).filter(Blogs.id == id, Blogs.auther == user.get('id'),
                                        Blogs.is_deleted == False).first()
    if blog_model is not None:
        return blog_model
    else:
        raise HTTPException(status_code=404, detail='Blog not found')


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_a_new_blog_post(user: user_dependency, db: db_dependency, new_blog: BlogsRequest):
    blog_model = Blogs(
        title=new_blog.title,
        content=new_blog.content,
        timestamp=datetime.utcfromtimestamp(int(new_blog.timestamp / 1000)),
        auther=user.get('id'),
    )
    db.add(blog_model)
    db.commit()


@router.put("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_an_existing_blog_post(user: user_dependency, db: db_dependency, updated_blog: BlogsRequest,
                                       id: int = Path(gt=0)):
    blog_model = db.query(Blogs).filter(Blogs.id == id, Blogs.auther == user.get('id'),
                                        Blogs.is_deleted == False).first()
    if blog_model is None:
        raise HTTPException(status_code=404, detail='Blog not found')
    blog_model.title = updated_blog.title
    blog_model.content = updated_blog.content
    blog_model.timestamp = datetime.utcfromtimestamp(int(updated_blog.timestamp / 1000))
    db.add(blog_model)
    db.commit()


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_a_blog_post(user: user_dependency, db: db_dependency, id: int = Path(gt=0)):
    blog_model = db.query(Blogs).filter(Blogs.id == id, Blogs.auther == user.get('id'),
                                        Blogs.is_deleted == False).first()
    if blog_model is None:
        raise HTTPException(status_code=404, detail='Blog not found')
    blog_model.is_deleted = True
    db.add(blog_model)
    db.commit()
