# third party extensions 
 
from apifairy import APIFairy
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_mail import Mail

apifairy = APIFairy()
db = SQLAlchemy()
ma = Marshmallow()
mail = Mail()