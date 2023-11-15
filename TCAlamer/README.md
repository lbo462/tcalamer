# TCALAMER

- Léo BONNAIRE
- Léonard PRINCÉ
- Edgar BRUNAUD

# Start the python backend in `PythonFiles/`

```shell
cd PythonFiles
```

Create a python virtual env

```shell
python -m venv venv
source venv/bin/activate
```

Install dependencies

```shell
pip install -r requirements.txt
```

## Start API

To start the API, use the following command within the python virtual env 

```shell
uvicorn main:app --reload
```

Check the swagger at `http://localhost:8000/docs`
