import upstudy.settings as settings

class Model(object):
    def __init__(self):
        if settings.backend == "postgres":
            from upstudy.data.backends.postgres import PostgresBackend
            self.backend = PostgresBackend(settings.postgres)

