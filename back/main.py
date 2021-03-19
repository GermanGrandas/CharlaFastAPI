import uvicorn
from fastapi import FastAPI,Request,UploadFile,File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse,FileResponse
from motor.motor_asyncio import AsyncIOMotorClient,AsyncIOMotorGridFSBucket
import os
from bson.objectid import ObjectId

from helpers.data_helpers import upload_file,get_filenames,download_file_helper,get_metadata
"""
    DB Connection
"""
MONGO_URL = os.getenv("MONGO_URL") or "localhost:27017"
client = AsyncIOMotorClient(f"mongodb://{MONGO_URL}/")
database = client.pypereira
# grid fs definition
fs = AsyncIOMotorGridFSBucket(database,bucket_name="attachments")
attachments = database.get_collection("attachments.files")
"""
    FastAPI definition
"""
app = FastAPI(title="GridFS API", #"/api/docs",
              description = "API created to interact with the GridFs functionality")

origins = [
    "http://localhost",
    "localhost",
    "http://localhost:3000",
    "localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
@app.post("/api/image_upload")
async def image_upload(file: UploadFile = File(...)):
    print(f"uploading: {file.filename}")
    contents = await file.read()
    data = {
        "filename" : file.filename,
        "content" : contents,
        "content_info" : {"contentType":file.content_type}
    }
    file_id = await upload_file(fs,data)
    return {"uploaded" : str(file_id)}
# async def ImageUpload(request: Request):
    # form = await request.form()
    # filename = form["file"].filename
    # contents = await form["file"].read()
    # print("hello",filename)
    # print(contents)
@app.get("/api/get_files")
async def get_files():
    results = await get_filenames(attachments)
    results = map(lambda data : {**data , "_id" : str(data["_id"])},results)
    return {"status" : 200, "files" : list(results)}

@app.get("/api/download_file/{file_id}")
async def download_file(file_id : str):
    key = ObjectId(file_id)
    metadata = await get_metadata(attachments,key)
    result = await download_file_helper(fs,key)
    with open(f"temp","wb") as temp_file:
        temp_file.write(result)
    media_type = metadata["metadata"]["contentType"]
    return FileResponse("temp",media_type=media_type,filename=metadata["filename"])
    # print(result)
    # return StreamingResponse(result)
    

@app.get("/")
def home():
    return {"Hello": "FastAPI"}

if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True)
