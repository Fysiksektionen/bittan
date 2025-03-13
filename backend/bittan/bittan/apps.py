import os
import logging

from django.apps import AppConfig

from bittan.settings import ENV_VAR_NAMES, EnvVars


class BittanConfig(AppConfig):
    name = 'bittan'

    def ready(self):
        from bittan.services.swish.swish import Swish 

        swish_url = EnvVars.get(ENV_VAR_NAMES.SWISH_API_URL)
        callback_url = f'{EnvVars.get(ENV_VAR_NAMES.BITTAN_BACKEND_URL)}/swish/callback/'
        logging.info(f'Swish url set to: {swish_url}')
        logging.info(f'Callback url set to: {callback_url}')

        cert_file_paths = (
                EnvVars.get(ENV_VAR_NAMES.SWISH_PEM_FILE_PATH),
                EnvVars.get(ENV_VAR_NAMES.SWISH_KEY_FILE_PATH)
        )

        payee_alias = EnvVars.get(ENV_VAR_NAMES.SWISH_PAYEE_ALIAS)

        # Attach the Swish instance to a variable in the app's config for easy access
        self.swish = Swish(swish_url, payee_alias, callback_url, cert_file_paths)

        from bittan.services.swish.swish import payment_signal
        from bittan.services.swish.example_callback_handler import example_callback_handler_function
        from bittan.services.ticket_processing.payment_request_callback_handler import payment_request_callback_handler
        payment_signal.connect(example_callback_handler_function)
        payment_signal.connect(payment_request_callback_handler)
