class ReadMixin(object):
    @classmethod
    def read_all(cls, user=None, is_gm=False):
        return [row.read(user=user, is_gm=is_gm) for row in cls.query() if row.visible(user) or is_gm]

    def visible(self, user=None):
        raise NotImplementedError(
            'Subclasses of ReadMixin must implement an is-visible method.'
        )


class WriteMixin(object):
    def write(self, **kwargs):
        try:
            for column, value in kwargs.iteritems():
                prop = getattr(self, column)
                if isinstance(prop, ndb.IntegerProperty):
                    if isinstance(value, list):
                        value = map(int, value)
                    else:
                        value = int(value)
                setattr(self, column, value)
            self.put()
            return True
        except ValueError:
            return False
