# import os # for heroku only
# import requests # for heroku only
# Port = int(os.environ.get('PORT', 50000)) # for heroku only
import aiohttp
import asyncio
import uvicorn
import ast
import numpy as np
from fastai2 import *
from fastai2.vision.all import *
from fastai2_audio.core.all import *
from fastai2_audio.augment.all import *
from io import BytesIO
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse, JSONResponse
from starlette.staticfiles import StaticFiles


export_file_url = 'https://direct.bayyu.net/file/6148523063484d364c79396b636d6c325a53356e6232396e62475575593239744c325a70624755765a4338784c54566e546b78354e457477563056426545303354316c6d65584a704f466c6964476c6d516c4a32646a6376646d6c6c647a39316333413963326868636d6c755a773d3d?dl=1'
#export_file_url = "https://www.googleapis.com/drive/v3/files/1-5gNLy4KpWEAxM7OYfyri8YbtifBRvv7/?key=AIzaSyCMqdjFMjVUCy1VhUznkaJcUy89pSFURFk&alt=media"
export_file_name = 'learner.pkl'

with open('app/classes.txt', 'r') as f:
    classes = ast.literal_eval(f.read())
path = Path(__file__).parent

app = Starlette()
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_headers=['X-Requested-With', 'Content-Type'])
app.mount('/static', StaticFiles(directory='app/static'))


async def download_file(url, dest):
    if dest.exists(): return
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.read()
            print("data response",data)
            with open(dest, 'wb') as f:
                f.write(data)


async def setup_learner():
    await download_file(export_file_url, path/export_file_name)
    try:
        def get_file(r): return '../content/train_curated/'+r['fname'] # to avoid AttributeError
        def get_label(r): return r['labels'].split(',') # to avoid AttributeError
        print("pkl file exists?:", path/export_file_name, os.path.exists(path/export_file_name))
        print("dl pkl file size:", Path(path/export_file_name).stat().st_size)
        learn = load_learner(path/export_file_name)
        return learn
    except RuntimeError as e:
        if len(e.args) > 0 and 'CPU-only machine' in e.args[0]:
            print(e)
            message = "\n\nThis model was trained with an old version of fastai and will not work in a CPU environment.\n\nPlease update the fastai library in your training environment and export your model again.\n\nSee instructions for 'Returning to work' at https://course.fast.ai."
            raise RuntimeError(message)
        else:
            raise


loop = asyncio.get_event_loop()
tasks = [asyncio.ensure_future(setup_learner())]
learn = loop.run_until_complete(asyncio.gather(*tasks))[0]
loop.close()


@app.route('/')
async def homepage(request):
    html_file = path / 'view' / 'index.html'
    return HTMLResponse(html_file.open().read())

# method from https://github.com/aquietlife/whisp/blob/master/app/server.py
@app.route('/analyze', methods=['POST'])
async def analyze(request):
    form = await request.form()
    bytes = await (form["file"].read())
    wav = BytesIO(bytes) 
    utc_time = str(int(time.time()))
    sound_file = "tmp/sound_" + utc_time + ".wav"
    _,_,preds =  learn.predict(sound_file)
    predictions = learn.dls.vocab[np.argwhere(preds > 0.3).squeeze()]
    return JSONResponse({'Classifcations': str(predictions)})


if __name__ == '__main__':
    if 'serve' in sys.argv:
        uvicorn.run(app=app, host='0.0.0.0', port=5000, log_level="info") # render
        #uvicorn.run(app=app, host='0.0.0.0', port=Port, log_level="info") #heroku
