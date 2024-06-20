# Erotic Palace

Before you can use the these apps, make sure you have the requirements installed:  
Windows: `py -m pip install -r requirements.txt`  
Linux: `python3 -m pip install -r requirements.txt`

Also, you have to run "create_db.py" once before running any of the apps.
This will create the database and populate it with some example data.

So, as a checklist, the first time you should:
1. Unzip the .ZIP-archive to an empty directory
2. Go to the directory on the commandline (`cd <dir-name>`)
3. Install a Python Virtual Environment:  
   Windows: `py -m venv .venv`  
   Linux: `python3 -m venv .venv`
4. Activate the VEnv:  
   Windows: `.\.venv\Scripts\activate`  
   Linux: `./.venv/Scripts/activate`
5. Install requirements in the VEnv:  
   Windows: `py -m pip install -r requirements.txt`  
   Linux: `python3 -m pip install -r requirements.txt`
6. Run the create_db script:  
   Windows: `py .\girlsdb.py`  
   Linux: `python3 ./girlsdb.py`
   
The steps above only need to be executed once.
After that, you can start the students api server by doing the following:

1. Go to the directory on the commandline (`cd <dir-name>`)
2. Activate the VEnv:  
   Windows: `.\.venv\Scripts\activate`  
   Linux: `./.venv/Scripts/activate`
3. Start the API server:  
   Windows: `py .\girls_api.py`  
   Linux: `python3 ./girls_api.py`
4. Start the admin frontend:
   Windows: `py .\admin_frontend.py`  
   Linux: `python3 ./admin_frontend.py`

Now, independently from the admin part, you can access the user side using:
   Windows: `py .\user_frontend.py`  
   Linux: `python3 ./user_frontend.py`


Have fun!
