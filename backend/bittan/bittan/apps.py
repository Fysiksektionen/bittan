from django.apps import AppConfig

class BittanConfig(AppConfig):
    name = 'bittan'

    def ready(self):
        from bittan.services.swish import Swish, example_callback_handler_function

        url = "https://mss.cpc.getswish.net/swish-cpcapi/"
        callback_url = "https://4c07b97a2f8007.lhr.life/swish/callback/"
        cert_file_paths = ("./test_certificates/testcert.pem", "./test_certificates/testcert.key")

        # Attach the Swish instance to a variable in the app's config for easy access
        self.swish = Swish(url, "1234679304", callback_url, cert_file_paths, example_callback_handler_function)
