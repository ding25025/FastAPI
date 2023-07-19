import uvicorn
import json
import secrets
import jwt
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from pydantic import BaseModel, BaseSettings
from typing import Union, Optional, List
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy import Boolean, Column, Float, String, Integer, text
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from common import getTime, checkJWT


app = FastAPI()

engine = create_engine(
    'mysql+mysqlconnector://compal:0000@localhost:3306/mpd_sales')
# Establish a connection
# connection = engine.connect()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class JWTSettings(BaseSettings):
    authjwt_secret_key = "compal-secret-key"
    authjwt_algorithm = "HS256"
    # 30 minutes * 60 seconds = 1800 seconds
    authjwt_access_token_expires = 30 * 60


class Account(Base):
    __tablename__ = 'Account'

    id = Column(Integer, primary_key=True)
    email = Column(String)
    password = Column(String)
    firstname = Column(String, nullable=True)
    lastname = Column(String, nullable=True)
    createtime = Column(Float, nullable=True)
    updatetime = Column(Float, nullable=True)
    deletetime = Column(Float, default=0.0)


class AccountResponse(BaseModel):
    id: int
    email: str
    password: str
    firstname: Optional[str]
    lastname: Optional[str]
    createtime: Optional[float]
    updatetime: Optional[float]
    deletetime: float = 0.0


class Customer(Base):
    __tablename__ = 'Customer'

    id = Column(Integer, primary_key=True)
    email = Column(String)
    firstname = Column(String, nullable=True)
    lastname = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    company = Column(String, nullable=True)
    position = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    content = Column(String, nullable=True)
    createtime = Column(Float, default=getTime())
    updatetime = Column(Float, default=getTime())
    deletetime = Column(Float, default=0.0)


class CustomerResponse(BaseModel):
    id: int
    email: str
    firstname: Optional[str]
    lastname: Optional[str]
    gender: Optional[str]
    company: Optional[str]
    position: Optional[str]
    phone: Optional[str]
    content: Optional[str]
    createtime: Optional[float]
    updatetime: Optional[float]
    deletetime: float = 0.0


@AuthJWT.load_config
def get_auth_jwt_config():
    return JWTSettings()


@app.get("/")
def read_root():
    return {"Hello": "World"}


def create_api(app: FastAPI):
    @app.get(app.root_path + "/openapi.json")
    def custom_swagger_ui_html():
        return app.openapi()


@app.get("/Account")
def read_all_accounts(auth: AuthJWT = Depends()):
    try:
        # Validate the JWT token and retrieve the user ID
        auth.jwt_required()
        db = SessionLocal()
        # Return all accounts
        result = db.query(Account).all()
        if result is None:
            return {"status": False, "msg": "Empty Result"}
        db.close()
        # Convert each account object to a dictionary
        json_result = []
        for account in result:
            account_dict = account.__dict__
            account_dict.pop('_sa_instance_state', None)
            json_result.append(account_dict)

        return {"status": True, "msg": "Success", "result": json_result}
    except AuthJWTException:
        return {"status": False, "msg": "Invalid token"}
    except Exception as e:
        # Handle the exception gracefully
        # You can log the error, return an error response, or perform any other appropriate actions
        print("Error:", str(e))
        return {"status": False, "msg": str(e)}


@app.get("/Account/{account_id}")
def read_account(account_id: Optional[int] = None, auth: AuthJWT = Depends()):
    try:
        # Validate the JWT token and retrieve the user ID
        auth.jwt_required()
        db = SessionLocal()
        if account_id is None:
            # Return all accounts
            result = db.query(Account).all()
        else:
            # Filter by account_id
            result = db.query(Account).filter(Account.id == account_id).first()

        if result is None:
            return {"status": False, "msg": "Empty Result"}
        db.close()

        # Convert the query result to JSON
        json_result = result.__dict__
        json_result.pop('_sa_instance_state', None)
        return {"status": True, "msg": "Success", "result": json_result}
    except AuthJWTException:
        return {"status": False, "msg": "Invalid token"}
    except Exception as e:
        # Handle the exception gracefully
        # You can log the error, return an error response, or perform any other appropriate actions
        print("Error:", str(e))
        return {"status": False, "msg": str(e)}


@app.post("/Login")
async def login(info: Request, auth: AuthJWT = Depends()):
    try:

        db = SessionLocal()
        item = await info.json()

        if item['email'] is None or item['password'] is None:
            return {"status": False}
        else:
            result = db.query(Account).filter(
                Account.email == item['email'], Account.password == item['password']).first()

        if result is None:
            return {"status": False, "result": "Empty Result"}
        db.close()

        if result:
            # Create an access token and return it as the response
            access_token = auth.create_access_token(subject=item['email'])
            json_result = result.__dict__
            json_result.pop('_sa_instance_state', None)
            return {"status": True, "msg": "Success", "result": json_result, "token": access_token}
        else:
            return {"status": False, "msg": "Login Faill"}
    except Exception as e:
        # Handle the exception gracefully
        # You can log the error, return an error response, or perform any other appropriate actions
        print("Error:", str(e))
        return {"status": False, "msg": str(e)}


@app.get("/Customer")
def read_all_customers(auth: AuthJWT = Depends()):
    try:
        # Validate the JWT token and retrieve the user ID
        auth.jwt_required()

        db = SessionLocal()
        # Return all customers
        result = db.query(Customer).all()

        if result is None:
            return {"status": False, "msg": "Empty Result"}

        db.close()
        # Convert each customer object to a dictionary
        json_result = []

        for customer in result:
            customer_dict = customer.__dict__
            customer_dict.pop('_sa_instance_state', None)
            json_result.append(customer_dict)

        return {"status": True, "msg": "Success", "result": json_result}

    except AuthJWTException:
        return {"status": False, "msg": "Invalid token"}
    except Exception as e:
        # Handle the exception gracefully
        # You can log the error, return an error response, or perform any other appropriate actions
        print("Error:", str(e))
        return {"status": False, "msg": str(e)}


@app.get("/Customer/{customer_id}")
def read_customer(customer_id: Optional[int] = None, auth: AuthJWT = Depends()):
    try:
        # Validate the JWT token and retrieve the user ID
        auth.jwt_required()

        db = SessionLocal()
        if customer_id is None:
            return {"status": False}
        else:
            # Filter by customer_id
            result = db.query(Customer).filter(
                Customer.id == customer_id).first()

        db.close()

        if result is None:
            return {"status": False, "msg": "Empty Result"}

        # Convert the query result to JSON
        json_result = result.__dict__
        json_result.pop('_sa_instance_state', None)

        return {"status": True, "msg": "Success", "result": json_result}
    except AuthJWTException:
        return {"status": False, "msg": "Invalid token"}
    except Exception as e:
        # Handle the exception gracefully
        # You can log the error, return an error response, or perform any other appropriate actions
        print("Error:", str(e))
        return {"status": False, "msg": str(e)}


@app.post("/Customer")
async def create_customer(info: Request):
    try:
        # Validate the JWT token and retrieve the user ID
        # auth.jwt_required()

        db = SessionLocal()
        item = await info.json()

        # Create a new Customer object
        customer = Customer(
            email=item["email"],
            firstname=item["firstname"] if "firstname" in item else "",
            lastname=item["lastname"],
            gender=item["gender"] if "gender" in item else "unknown",
            company=item["company"] if "company" in item else "",
            position=item["position"] if "position" in item else "",
            phone=item["phone"] if "position" in item else 0,
            content=item["content"] if "content" in item else "",
            createtime=getTime(),
            updatetime=getTime(),
            deletetime=0.0
        )

        # Add the customer to the session
        db.add(customer)
        db.commit()  # Commit the changes to the database
        # Refresh the customer object to get the generated ID
        db.refresh(customer)
        db.close()
        print("Customer added successfully!")
        return {"status": True, "msg": "Success", "result": customer}
    except AuthJWTException:
        return {"status": False, "msg": "Invalid token"}
    except Exception as e:
        # Failed to add customer
        db.rollback()  # If the commit fails, you may want to roll back the transaction to maintain data consistency
        return {"status": False, "msg": str(e)}


if __name__ == '__main__':
    uvicorn.run(app)
