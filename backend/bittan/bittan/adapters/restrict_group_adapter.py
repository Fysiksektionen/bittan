from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialToken
from allauth.core.exceptions import ImmediateHttpResponse
from django.http import HttpResponseForbidden
from bittan.settings import EnvVars, ENV_VAR_NAMES
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build


import logging
import os

def _get_service_credentials() -> Credentials:
    creds: Credentials
    path = EnvVars.get(ENV_VAR_NAMES.SERVICE_ACCOUNT_AUTH_FILE)
    if os.path.exists(path):
        creds = Credentials.from_service_account_file(
            path,
            scopes=['https://www.googleapis.com/auth/admin.directory.group.member.readonly'],
            subject=EnvVars.get(ENV_VAR_NAMES.SUBJECT_EMAIL)
        )
        return creds
    raise FileNotFoundError("Could not find service key file.")

class RestrictGroupAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        email = sociallogin.account.extra_data.get("email").lower()
        allowed_domain = "@fysiksektionen.se"
        if not email.endswith(allowed_domain):
            raise ImmediateHttpResponse(HttpResponseForbidden("You do not have access to this resource."))

        target_group = EnvVars.get(ENV_VAR_NAMES.AUTH_GROUP_KEY)

        user_id = sociallogin.account.uid
        if not self._is_user_in_allowed_group(user_id, target_group):
            raise ImmediateHttpResponse(HttpResponseForbidden("You do not have access to this resource. "))

    def _is_user_in_allowed_group(self, user_id, group_email):
        creds: Credentials
        try:
            creds = _get_service_credentials()
        except Exception as e: 
            logging.error(f"Could not get group checker credentials with exception: \n{e}")
            raise Exception("Could not get credentials")
        
        service = build("admin", "directory_v1", credentials=creds)

        res = service.members().hasMember(
            groupKey=group_email,
            memberKey=user_id
        ).execute()

        return res.get("isMember", False)


            
