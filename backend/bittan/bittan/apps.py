import os

from django.apps import AppConfig

from bittan.settings import ENV_VAR_NAMES, EnvVars


class BittanConfig(AppConfig):
    name = 'bittan'

    def ready(self):
        from bittan.services.swish import Swish, example_callback_handler_function

        swish_url = EnvVars.get(ENV_VAR_NAMES.SWISH_API_URL)
        callback_url = f'{EnvVars.get(ENV_VAR_NAMES.APPLICATION_URL)}swish/callback/'

        cert_file_paths = (
                EnvVars.get(ENV_VAR_NAMES.SWISH_PEM_FILE_PATH),
                EnvVars.get(ENV_VAR_NAMES.SWISH_KEY_FILE_PATH)
        )

        payee_alias = EnvVars.get(ENV_VAR_NAMES.SWISH_PAYEE_ALIAS)

        # Attach the Swish instance to a variable in the app's config for easy access
        self.swish = Swish(swish_url, payee_alias, callback_url, cert_file_paths, example_callback_handler_function)
