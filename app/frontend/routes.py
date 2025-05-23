from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

router = APIRouter()

# Configure templates
templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
templates = Jinja2Templates(directory=templates_dir)

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the index page."""
    return templates.TemplateResponse("index.html", {"request": request})