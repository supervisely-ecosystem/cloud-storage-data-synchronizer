import os
import json
from dotenv import load_dotenv

import supervisely as sly

if sly.is_development():
    load_dotenv("local.env")
    load_dotenv(os.path.expanduser("~/supervisely.env"))

# os.environ["APP_CATEGORIES"] = json.dumps(["import"])

api = sly.Api()

app_data = sly.app.get_data_dir()
sly.fs.clean_dir(app_data)

task_id = sly.env.task_id()
team_id = sly.env.team_id()
workspace_id = sly.env.workspace_id()
project_id = sly.env.project_id()
folder = sly.env.folder(raise_not_found=False)


def validate_bucket_name(bucket_name):
    import re

    if bucket_name == "" or bucket_name is None:
        raise ValueError("Bucket name is undefined")

    # Regex: one or more non-slash, then (slash and one or more non-slash) repeated, no leading/trailing/consecutive slashes
    pattern = r"^[^/]+(?:/[^/]+)+$"
    if not re.match(pattern, bucket_name):
        raise ValueError(
            "Bucket name must be in the format 'bucket/folder' or 'bucket/folder/subfolder', with no leading, trailing, or consecutive slashes"
        )
    return bucket_name

if folder is None:
    provider = os.environ.get("modal.state.provider")
    bucket = validate_bucket_name(os.environ.get("modal.state.bucketName"))
    folder = f"{provider}://{bucket.lstrip('/')}"

project = None
dataset = None
