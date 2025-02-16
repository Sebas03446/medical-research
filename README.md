# medical-research

## Running the Backend App

1. Navigate to the `backend` directory:
   ```sh
   cd backend
   ```

2. Create a virtual environment:
   ```sh
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```sh
     venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```sh
     source venv/bin/activate
     ```

4. Install the dependencies from `requirements.txt`:
   ```sh
   pip install -r requirements.txt
   ```

5. Run the FastAPI app using `uvicorn`:
   ```sh
   uvicorn app.main:app --reload
   ```
