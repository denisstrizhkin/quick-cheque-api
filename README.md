# quick-cheque-api

## run containers
```console
docker compose up --build
```

## initialize database
```console
python init-db.py
```
this command works inside `quick-cheque-api-container-back-1` with
```
docker exec -it quick-cheque-api-container-back-1 bash
```
