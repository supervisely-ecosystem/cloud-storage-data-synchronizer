<div align="center" markdown>

# Synchronize data from Cloud Storage

<p align="center">
  <a href="#Overview">Overview</a> •
  <a href="#How-To-Run">How To Run</a> •
  <a href="#How-it-works">How it works</a>
</p>

[![](https://img.shields.io/badge/supervisely-ecosystem-brightgreen)](../../../../supervisely-ecosystem/cloud-storage-data-synchronizer)
[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervisely.com/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/cloud-storage-data-synchronizer)
[![views](https://app.supervisely.com/img/badges/views/supervisely-ecosystem/cloud-storage-data-synchronizer.png)](https://supervisely.com)
[![runs](https://app.supervisely.com/img/badges/runs/supervisely-ecosystem/cloud-storage-data-synchronizer.png)](https://supervisely.com)

</div>

# Overview

This app is designed to streamline the process of importing images from cloud storage services into Supervisely projects. It efficiently scans a specified folder in your cloud storage, identifies new images that haven't been previously imported, and adds them to a new dataset within your chosen project. This ensures that your project stays up-to-date with the latest data without duplicating existing files, making it perfect for continuous data synchronization workflows.

- Support for popular cloud storage providers (AWS S3, Google Cloud Storage, Azure Blob Storage).
- Duplicate prevention: only imports files that aren't already in the project.
- Batch processing for efficient handling of large datasets.
- Automatic image metadata and annotation support.
- Link-based uploading for optimized storage usage (without duplicating files).
- Headless operation suitable for automation and scheduled runs.

# How to run

The app expects three main parameters:

- **Project**: Target Supervisely project to import data into
- **Provider**: Cloud storage provider (e.g., `s3`, `gcs`, `azure`)
- **Bucket Path**: Full path in format `bucket/folder/subfolder`

You can launch the app on an existing images project:

1. Find the "Synchronize data from Cloud Storage" app in the Supervisely Ecosystem.
2. Right-click on your target images project and select the app from the context menu.
3. Configure the cloud storage connection:
   - Select your cloud storage provider (AWS S3, Google Cloud, Azure, etc.)
   - Specify the bucket name and folder path in the format `bucket/folder/subfolder`
4. Click Run. The app will automatically create a new dataset with timestamp and import only new images.

# How it works

**Storage Scanning**

- The app scans the specified cloud storage folder for image files with valid extensions.
- Compares found files with already imported images in the project to identify new content.

**Smart Import Process**

- Creates a new dataset with the current timestamp for organization.
- Uses Supervisely's ImportManager for efficient annotation detection.
- Uploads images as links to optimize storage usage (without duplicating files).

**Duplicate Prevention**

- Maintains a record of previously imported file links.
- Skips files that have already been imported in any dataset within the project.
- Ensures data consistency across multiple synchronization runs.
