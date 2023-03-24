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

"""Demonstrates how to perform basic operations with Google Cloud IAM
service account keys.

For more information, see the documentation at
https://cloud.google.com/iam/docs/creating-managing-service-account-keys.
"""
import base64
import argparse
# [START iam_create_key]
# [START iam_list_keys]
# [START iam_delete_key]
import os

from google.oauth2 import service_account
import googleapiclient.discovery
import google.auth
import datetime
import time

# [END iam_create_key]
# [END iam_list_keys]
# [END iam_delete_key]


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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    subparsers = parser.add_subparsers(dest='command')

    create_key_parser = subparsers.add_parser(
        'create', help=create_key.__doc__)
    create_key_parser.add_argument('service_account_email')

    list_keys_parser = subparsers.add_parser(
        'list', help=list_keys.__doc__)
    list_keys_parser.add_argument('service_account_email')

    delete_key_parser = subparsers.add_parser(
        'delete', help=delete_key.__doc__)
    delete_key_parser.add_argument('full_key_name')

    delete_keys_parser = subparsers.add_parser(
        'delete_expired_keys', help=delete_key.__doc__)
    delete_keys_parser.add_argument('service_account_email')

    args = parser.parse_args()

    if args.command == 'list':
        list_keys(args.service_account_email)
    elif args.command == 'create':
        create_key(args.service_account_email)
    elif args.command == 'delete':
        delete_key(args.full_key_name)
    elif args.command == 'delete_expired_keys':
        delete_expired_keys(args.service_account_email)