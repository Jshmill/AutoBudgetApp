import pandas as pd
from . import crud, schemas

def parse_csv_and_merge(db, file_path):
    df = pd.read_csv(file_path)
    # Normalize column names: strip whitespace
    df.columns = df.columns.str.strip()
    
    # Handle Debit/Credit split if Amount is missing
    if 'Amount' not in df.columns and 'Debit' in df.columns and 'Credit' in df.columns:
        # Ensure they are numeric, treating invalid parsing as NaN then 0
        df['Credit'] = pd.to_numeric(df['Credit'], errors='coerce').fillna(0)
        df['Debit'] = pd.to_numeric(df['Debit'], errors='coerce').fillna(0)
        df['Amount'] = df['Credit'] - df['Debit']

    required_columns = ['Date', 'Description', 'Amount']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        raise ValueError(f"Missing columns: {missing_columns}. Found columns: {list(df.columns)}")
        
    df = df[required_columns]
    for _, row in df.iterrows():
        if not crud.transaction_exists(db, row['Date'], row['Description'], row['Amount']):
            trans = schemas.TransactionCreate(
                date=row['Date'],
                description=row['Description'],
                amount=row['Amount'],
                category="Uncategorized"
            )
            crud.create_transaction(db, trans)
