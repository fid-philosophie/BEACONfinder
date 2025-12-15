# BEACONfinder_PRIVATE
A Findbuch using the output of https://github.com/fid-philosophie/BEACONaggregator.


## info

### mongodb

## howto

### run with
```
python -m uvicorn app.main:app --reload
```


### test
```
curl "http://localhost:8000/records/by-authority/1274788412"
```

### test (optional paging)
```
curl "http://localhost:8000/records/by-authority/1274788412?limit=50&skip=0"
```
