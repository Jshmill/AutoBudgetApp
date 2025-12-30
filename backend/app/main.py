from fastapi import FastAPI, UploadFile, File, Depends
from sqlalchemy.orm import Session
import shutil
from . import database, crud, models, schemas, utils
from .config import PLAID_CLIENT_ID, PLAID_SECRET, PLAID_ENV, PLAID_PRODUCTS, PLAID_COUNTRY_CODES
from sqlalchemy import text
import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
import datetime

# Plaid Configuration
configuration = plaid.Configuration(
    host=plaid.Environment.Sandbox,
    api_key={
        'clientId': PLAID_CLIENT_ID,
        'secret': PLAID_SECRET,
    }
)

if PLAID_ENV == 'sandbox':
    configuration.host = plaid.Environment.Sandbox
elif PLAID_ENV == 'development':
    configuration.host = plaid.Environment.Development
elif PLAID_ENV == 'production':
    configuration.host = plaid.Environment.Production

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)


models.Base.metadata.create_all(bind=database.engine)

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/transactions/upload")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_location = f"temp_{file.filename}"
    try:
        with open(file_location, "wb") as f:
            shutil.copyfileobj(file.file, f)
        utils.parse_csv_and_merge(db, file_location)
        return {"status": "success"}
    except Exception as e:
        print(f"Error processing text: {e}")
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        import os
        if os.path.exists(file_location):
            os.remove(file_location)

@app.post("/create_link_token")
def create_link_token():
    try:
        request = LinkTokenCreateRequest(
            products=[Products(product) for product in PLAID_PRODUCTS],
            client_name="Auto Budget App",
            country_codes=[CountryCode(code) for code in PLAID_COUNTRY_CODES],
            language='en',
            user=LinkTokenCreateRequestUser(
                client_user_id='user-id'
            )
        )
        response = client.link_token_create(request)
        return response.to_dict()
    except plaid.ApiException as e:
        return {"error": e.body}

@app.post("/exchange_public_token")
def exchange_public_token(public_token: str, db: Session = Depends(get_db)):
    try:
        exchange_request = ItemPublicTokenExchangeRequest(
            public_token=public_token
        )
        exchange_response = client.item_public_token_exchange(exchange_request)
        access_token = exchange_response['access_token']
        item_id = exchange_response['item_id']
        
        # Save fit to DB
        db_item = models.PlaidItem(access_token=access_token, item_id=item_id)
        db.add(db_item)
        db.commit()
        
        # Sync transactions immediately
        sync_transactions(access_token, db)
        
        return {"public_token_exchange": "complete"}
    except plaid.ApiException as e:
        return {"error": e.body}

def sync_transactions(access_token, db):
    # Set cursor to empty to receive all historical updates
    cursor = ''

    # New transaction updates since "cursor"
    added = []
    modified = []
    removed = [] # Removed transaction ids
    has_more = True

    try:
        # Iterate through each page of new transaction updates for item
        while has_more:
            request = TransactionsSyncRequest(
                access_token=access_token,
                cursor=cursor,
            )
            response = client.transactions_sync(request)
            
            # Add this page of results
            added.extend(response['added'])
            modified.extend(response['modified'])
            removed.extend(response['removed'])
            
            has_more = response['has_more']
            cursor = response['next_cursor']

        # Save to DB
        for transaction in added:
            if not crud.transaction_exists(db, transaction['date'], transaction['name'], transaction['amount']):
                trans = schemas.TransactionCreate(
                   date=str(transaction['date']),
                   description=transaction['name'],
                   amount=transaction['amount'],
                   category=transaction['category'][0] if transaction['category'] else "Uncategorized"
                )
                crud.create_transaction(db, trans)
                
    except plaid.ApiException as e:
        print(f"Error syncing transactions: {e}")






@app.get("/transactions")
def list_transactions(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT * FROM transactions ORDER BY date DESC"))
    return result.mappings().all()

@app.get("/transactions/totalcost")
def get_total_cost(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT SUM(amount) FROM transactions"))
    return result.scalar()

@app.get("/transactions/weeklycost")
def get_weekly_cost(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT SUM(amount) FROM transactions WHERE date >= date('now', '-7 days')"))
    return result.scalar()

@app.get("/transactions/dailycost")
def get_daily_cost(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT SUM(amount) FROM transactions WHERE date = date('now')"))
    return result.scalar()
@app.get("/balances")
def get_balances(db: Session = Depends(get_db)):
    # Get the latest access token (assuming single user/session for now)
    item = db.query(models.PlaidItem).first()
    if not item:
        return {"error": "No linked account found"}
    
    try:
        request = AccountsBalanceGetRequest(
            access_token=item.access_token
        )
        response = client.accounts_balance_get(request)
        
        # Return simplified balance info for all accounts
        accounts_data = []
        for account in response['accounts']:
            accounts_data.append({
                "name": account['name'],
                "current_balance": account['balances']['current'],
                "available_balance": account['balances']['available'],
                "currency": account['balances']['iso_currency_code'],
                "type": str(account['type']),
                "subtype": str(account['subtype'])
            })
            
        return accounts_data
    except plaid.ApiException as e:
        return {"error": e.body}
