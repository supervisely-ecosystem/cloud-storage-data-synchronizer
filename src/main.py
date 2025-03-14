import cv2
import numpy as np
import supervisely as sly

import src.functions as f
import src.globals as g

try:
    # * 1. Get project and dataset infos
    g.project = g.api.project.get_info_by_id(g.project_id)
    if g.project is None:
        raise Exception(f"Project with id={g.project_id} not found")
    g.dataset = g.api.dataset.create(g.project.id, "ds0", change_name_if_conflict=True)

    # * 2. Generate 5 sampel images (150x150 with random color circle in random position)
    images = []
    names = []
    for i in range(5):
        img = np.zeros((150, 150, 3), dtype=np.uint8)
        center = (np.random.randint(0, 150), np.random.randint(0, 150))
        radius = np.random.randint(10, 50)
        color = tuple(np.random.randint(0, 256) for _ in range(3))
        cv2.circle(img, center, radius, color, -1)
        img_name = f"sample_{i}.png"
        images.append((img_name, img))
        names.append(img_name)
    infos = g.api.image.upload_nps(g.dataset.id, names, images, conflict_resolution="rename")
    sly.logger.info(f"Uploaded {len(infos)} images to dataset {g.dataset.name}")

except Exception as e:
    f.handle_exception_and_stop(e, "Failed to upload images to dataset")

# * 4. Set output project
output_title = f"{g.project.name}. New dataset:{g.dataset.name}"
g.api.task.set_output_project(g.task_id, g.project.id, output_title)

# * 5. Clean app_data directory
sly.fs.clean_dir(g.app_data)
