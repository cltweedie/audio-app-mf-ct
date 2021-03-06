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


export_file_url = 'https://storage.googleapis.com/fastai-export-bucket/export.pkl' # google cloud bucket
#export_file_url = 'https://drive.google.com/uc?export=download&id=1NryOFwHs6T3HlkG_dsSCslWgcviRv4h-' # google drive

export_file_name = 'export.pkl'

with open('app/classes.txt', 'r') as f:
    classes = ast.literal_eval(f.read())

path = Path(__file__).parent

app = Starlette()
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_headers=['X-Requested-With', 'Content-Type'])
app.mount('/static', StaticFiles(directory='app/static'))


async def download_file(url, dest):
    print("Attempting pkl file download")
    print("url:", url)
    print("dest:", dest)
    if dest.exists(): return "dest.exists()"
    async with aiohttp.ClientSession() as session:
        print("async session")
        async with session.get(url) as response:
            print("response", response)
            data = await response.read()
            #print("data response",data)
            with open(dest, 'wb') as f:
                print("writing data")
                f.write(data)
                print("file", f)

def get_file(r): return '../content/train_curated/'+r['fname']
def get_label(r): return r['labels'].split(',') # split labels on ','

async def setup_learner():
    await download_file(export_file_url, path/export_file_name)
    try:
        print("pkl file exists?:", path/export_file_name, os.path.exists(path/export_file_name))
        print("dl pkl file size:", Path(path/export_file_name).stat().st_size)
        print("loading learner...")
        learn = load_learner(path/export_file_name)
        print("learner loaded")
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
    return JSONResponse({'classifications': str(predictions)})


if __name__ == '__main__':
    if 'serve' in sys.argv:
        uvicorn.run(app=app, host='0.0.0.0', port=5000, log_level="info") # render
        #uvicorn.run(app=app, host='0.0.0.0', port=Port, log_level="info") #heroku
