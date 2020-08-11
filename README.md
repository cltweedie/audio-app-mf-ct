# audio-app-mf-ct
Multi-Label Audio Classification Web App using kaggle Freesound 2019 curated dataset

Deplyed on https://render.com/

The guide for production deployment to Render is at https://course.fast.ai/deployment_render.html.

See Render's fast.ai forum thread for questions and support.



## Heroku additions

Taken from: https://github.com/sachinchaturvedi93/PokemonClassifier with additions

1. The starter code taken from for deploying [fast.ai](https://www.fast.ai/) models on [Render](https://github.com/render-examples/fastai-v3). Plus additions for fastai2 and fastai2-audio in this repo.
2. Add the `Procfile` to the repository and put `web: python app/server.py serve` in it.
3. Add a `runtime.txt` file to specify `python` version.
4. In the `server.py` file we need to add :

```
import os 
import requests
Port = int(os.environ.get('PORT', 50000))
```

and replace `uvicorn.run(.....)` by

```
uvicorn.run(app=app, host='0.0.0.0', port=Port, log_level="info")
```

Edit : After upgrading uvicorn version, the app crashed with the following error - [Publish to Heroku is broken: "WARNING: You must pass the application as an import string to enable 'reload' or 'workers"](https://github.com/simonw/datasette/issues/633)

Solution is changing WEB_CONCURRENCY = 1 in app's setting on Heroku dashboard.