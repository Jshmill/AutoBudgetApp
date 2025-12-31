# Auto Budget App

## Setup

### 1. Backend
Navigate to the backend directory, create a virtual environment, and install dependencies.

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..
```

### 2. Frontend
Navigate to the frontend directory and install Node.js dependencies.

```bash
cd frontend
npm install
cd ..
```

### 3. Permissions
Ensure the run script is executable.

```bash
chmod +x run.sh
```

## Running the App

To start both the backend and the frontend, simply run:

```bash
./run.sh
```

## Running in Sandbox Mode

To run the app in sandbox mode, set the `PLAID_ENV` environment variable to `sandbox` before running the app.

When signing into the bank, choose continue as guest, choose the Plaid bank, and use the following credentials:

- Username: `user_good`
- Password: `pass_good`

For your phone number, use `415-555-0011`. The phone number verification code is `123456`.



## Repackaging the app

To repackage the app, run the following command:

```bash
cd frontend
npm run dist
cd ..
```



Built app lives in frontend/release/AutoBudget-0.0.0-arm64.dmge