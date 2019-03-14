from django.apps import AppConfig

class MemoirConfig(AppConfig):
    name = 'memoir'

    def ready(self):
        import memoir.signals