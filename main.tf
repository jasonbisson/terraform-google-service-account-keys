/**
 * Copyright 2021 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */


resource "google_project_organization_policy" "project_policy_boolean" {
  project    = var.project_id
  constraint = "iam.disableServiceAccountKeyCreation"
  boolean_policy {
    enforced = false
  }
}

resource "google_project_organization_policy" "project_policy_list_allow_all" {
  project    = var.project_id
  constraint = "iam.serviceAccountKeyExpiryHours"
  list_policy {
    allow {
      values = [{var.key_expire_time}]
    }
  }
}

resource "random_id" "random_suffix" {
  byte_length = 4
}

resource "google_project_service" "project_services" {
  project                    = var.project_id
  count                      = var.enable_apis ? length(var.activate_apis) : 0
  service                    = element(var.activate_apis, count.index)
  disable_on_destroy         = var.disable_services_on_destroy
  disable_dependent_services = var.disable_dependent_services
}

resource "google_service_account" "main" {
  project      = var.project_id
  account_id   = "${var.environment}-${random_id.random_suffix.hex}"
  display_name = "${var.environment}${random_id.random_suffix.hex}"
}

resource "google_project_iam_member" "main" {
  project      = var.project_id
  member   = "serviceAccount:${google_service_account.main.email}"
  role     = "roles/iam.serviceAccountKeyAdmin"
}

resource "google_cloudfunctions_function_iam_member" "invoker" {
  project        = var.project_id
  region         = google_cloudfunctions_function.function.region
  cloud_function = google_cloudfunctions_function.function.name
  role           = "roles/cloudfunctions.invoker"
  member         = "group:${var.identity_running_function}"
}

resource "google_cloudfunctions_function" "function" {
  project               = var.project_id
  region                = var.region
  name                  = var.environment
  entry_point           = var.function_entry_point
  ingress_settings      = "ALLOW_INTERNAL_ONLY"
  trigger_http          = true
  runtime               = var.runtime
  service_account_email = google_service_account.main.email
  source_archive_bucket = google_storage_bucket.gcf_source_bucket.name
  source_archive_object = google_storage_bucket_object.gcf_zip_gcs_object.name
  labels = {
    environment = var.environment
  }
  depends_on = [google_project_service.project_services]
}

resource "google_storage_bucket" "gcf_source_bucket" {
  name                        = "${var.environment}-${random_id.random_suffix.hex}"
  uniform_bucket_level_access = true
  location                    = var.region
  project                     = var.project_id
  depends_on                  = [google_project_service.project_services]
}

resource "google_storage_bucket" "key_bucket" {
  name                        = "${var.environment}-${random_id.random_suffix.hex}-keys"
  uniform_bucket_level_access = true
  location                    = var.region
  project                     = var.project_id
  depends_on                  = [google_project_service.project_services]
}

resource "google_storage_bucket_object" "gcf_zip_gcs_object" {
  name   = var.environment
  bucket = google_storage_bucket.gcf_source_bucket.name
  source = data.archive_file.gcf_zip_file.output_path
}

data "archive_file" "gcf_zip_file" {
  type        = "zip"
  output_path = "${path.module}/files/${var.environment}.zip"

  source {
    content  = file("${path.module}/files/main.py")
    filename = "main.py"
  }

}
