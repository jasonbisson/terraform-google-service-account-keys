#!/usr/bin/env python3

# Copyright 2018 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import base64
import argparse
import googleapiclient.discovery
import google.auth
import datetime

# [START iam_create_key]
def create_key(service_account_email):
    """Creates a key for a service account."""

    credentials, project_id = google.auth.default()
    #project_id = service_account_email.split('.')[0].split('@')[1]
    service = googleapiclient.discovery.build(
        'iam', 'v1', credentials=credentials)

    key = service.projects().serviceAccounts().keys().create(
        name='projects/-/serviceAccounts/' + service_account_email, body={}
        ).execute()

    json_key_file = base64.b64decode(key['privateKeyData']).decode('utf-8')

# [END iam_create_key]

# [START iam_list_keys]
def list_keys(service_account_email):
    """Lists all keys for a service account."""

    credentials, project_id = google.auth.default()

    service = googleapiclient.discovery.build(
        'iam', 'v1', credentials=credentials)

    keys = service.projects().serviceAccounts().keys().list(
    name='projects/-/serviceAccounts/' + service_account_email, keyTypes="USER_MANAGED").execute()

    for key in keys['keys']:
        print(key['name'])
# [END iam_list_keys]

# [START delete_expired_keys]
def delete_expired_keys(service_account_email):
    """Delete expired keys for a service account."""
    credentials, project_id = google.auth.default()
    service = googleapiclient.discovery.build(
        'iam', 'v1', credentials=credentials)

    keys = service.projects().serviceAccounts().keys().list(
    name='projects/-/serviceAccounts/' + service_account_email, keyTypes="USER_MANAGED").execute()

    for key in keys['keys']:
        keyname = key['name']
        expiration_date = key['validBeforeTime']
        expiration_datetime = datetime.datetime.strptime(expiration_date, '%Y-%m-%dT%H:%M:%SZ')
        now = datetime.datetime.now()
        days_until_expiration = (expiration_datetime - now).days
        if days_until_expiration < 0:
            service.projects().serviceAccounts().keys().delete(
            name=keyname).execute()

# [START iam_delete_key]
def delete_key(full_key_name):
    """Deletes a service account key."""

    credentials, project_id = google.auth.default()

    service = googleapiclient.discovery.build(
        'iam', 'v1', credentials=credentials)

    service.projects().serviceAccounts().keys().delete(
        name=full_key_name).execute()

    print('Deleted key: ' + full_key_name)
# [END iam_delete_key]

def main(request):
    request_json = request.get_json(silent=True)
    request_args = request.args

    method = request_json['method']
    service_account_email = request_json['service_account_email']

    if method == 'list':
        list_keys(service_account_email)
    elif method == 'create':
        create_key(service_account_email)
    elif method == 'delete':
        delete_key(full_key_name)
    elif method == 'delete_expired_keys':
        delete_expired_keys(service_account_email)
if __name__ == '__main__':
    main()