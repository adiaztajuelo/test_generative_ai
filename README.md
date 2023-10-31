# test_generative_ai

## Config
Create a file 'config.py' and add the API_KEY
```
api_key = 'OPENAI_API_KEY'
```

## Run Audio app
Run
```
streamlit run audio/app_audio.py
```

## Run askPDF app
Run
```
cd askPDF
streamlit run app.py
```

## Run chat_db app
Two steps:
```
cd chat_db
python api.py
```
```
cd .\chat_db\chatbot\release\web\
python -m http.server 5050
```

