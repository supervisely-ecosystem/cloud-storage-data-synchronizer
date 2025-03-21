from datetime import datetime
from urllib.parse import unquote

import src.functions as f
import src.globals as g
import supervisely as sly

try:
    # * 1. Get project and dataset infos
    g.project = g.api.project.get_info_by_id(g.project_id)
    if g.project is None:
        raise Exception(f"Project with id={g.project_id} not found")
    ds_name = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    g.dataset = g.api.dataset.create(g.project.id, ds_name, change_name_if_conflict=True)

    # * 2. Get existing image names
    # existing_names = set(
    #     [
    #         i.name
    #         for ds in g.api.dataset.get_list(g.project.id, recursive=True)
    #         for i in g.api.image.get_list(ds.id, force_metadata_for_links=False)
    #     ]
    # )
    existing_links = set(
        [
            unquote(i.link)
            for ds in g.api.dataset.get_list(g.project.id, recursive=True)
            for i in g.api.image.get_list(ds.id, force_metadata_for_links=False)
        ]
    )

    # * 3. List remote files
    remote_files = g.api.storage.list(g.team_id, g.folder)
    # remote_names = set(
    #     [
    #         sly.fs.get_file_name(f.name)
    #         for f in remote_files
    #         if sly.fs.get_file_ext(f.name) in sly.image.SUPPORTED_IMG_EXTS
    #     ]
    # )
    remote_links = set(
        [
            f.path
            for f in remote_files
            if sly.fs.get_file_ext(f.name) in sly.image.SUPPORTED_IMG_EXTS
        ]
    )

    new_links = remote_links - existing_links
    # new_names = remote_names - existing_names
    if len(new_links) == 0:
        raise Exception("No new files to upload")
    sly.logger.info(f"Found {len(new_links)} new images to upload: {new_links}")

    # * 4. Prepare files for upload
    import_manager = sly.ImportManager(
        input_data=g.folder,
        project_type=sly.ProjectType.IMAGES,
        upload_as_links=True,
    )
    converter = import_manager.converter

    meta, renamed_classes, renamed_tags = converter.merge_metas_with_conflicts(g.api, g.dataset.id)

    progress, progress_cb = converter.get_progress(len(new_links), "Uploading")

    uploaded_items_count = 0
    with sly.ApiContext(g.api, g.project_id, g.dataset.id, meta):
        names, paths, metas, items = [], [], [], []
        batch_size = 1000

        def _upload_batch(n, l, m, i):
            img_infos = g.api.image.upload_links(
                g.dataset.id, n, l, metas=m, batch_size=len(n), force_metadata_for_links=True
            )
            img_ids = [img_info.id for img_info in img_infos]
            anns = []
            if converter.supports_links:
                for info, item in zip(img_infos, i):
                    item.set_shape((info.height, info.width))
                    anns.append(converter.to_supervisely(item, meta, renamed_classes, renamed_tags))
                g.api.annotation.upload_anns(img_ids, anns, skip_bounds_validation=True)
            return img_ids

        for item in converter.get_items():
            if converter.remote_files_map.get(item.path) in existing_links:
                continue
            # if sly.fs.get_file_name(item.path) not in new_names:
            #     continue
            item.path = converter.validate_image(item.path)
            ext = sly.fs.get_file_ext(item.path)
            item.name = f"{sly.fs.get_file_name(item.path)}{ext.lower()}"
            names.append(item.name)
            paths.append(item.path)
            image_meta = item.meta or {}
            if isinstance(image_meta, str):  # path to file
                image_meta = sly.jsonload_json_file(image_meta)
            metas.append(image_meta)
            items.append(item)

            if len(names) == batch_size:
                img_ids = _upload_batch(names, paths, metas, items)
                uploaded_items_count += len(img_ids)
                progress_cb(len(img_ids))
                items, names, paths, metas = [], [], [], []

        if len(names) > 0:
            img_ids = _upload_batch(names, paths, metas, items)
            uploaded_items_count += len(img_ids)
            progress_cb(len(img_ids))
        if sly.is_development():
            progress.close()

    g.api.task.set_output_project(g.task_id, g.project.id, g.dataset.name)
    sly.logger.info(
        f"Uploaded {uploaded_items_count} images to dataset {g.dataset.name}",
    )

except Exception as e:
    f.handle_exception_and_stop(e, "Failed to upload images to dataset")

# * 4. Set output project
g.api.task.set_output_project(g.task_id, g.project.id, g.dataset.name)

# * 5. Clean app_data directory
sly.fs.clean_dir(g.app_data)
