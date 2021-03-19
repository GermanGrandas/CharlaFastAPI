async def upload_file(fs,file_info):
    file_id = await fs.upload_from_stream(
        file_info["filename"],
        file_info["content"],
        metadata=file_info["content_info"])
    return file_id

async def get_filenames(fs):
    results = await fs.find({},{"filename" : 1, "_id" : 1, "uploadDate" : 1}).to_list(None)
    return results

async def download_file_helper(fs,file_id):
    grid_out = await fs.open_download_stream(file_id)
    contents = await grid_out.read()
    return contents

async def get_metadata(fs,file_id):
    result = await fs.find_one({"_id" : file_id},{"_id" : 0,"filename" : 1,"metadata" : 1},no_cursor_timeout=True)
    return result
