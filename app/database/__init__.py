from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


def populate_db(num_users=5):
    """
    Fills the database with fake data. Used for testing.
    """
    from faker import Factory
    from app.user.models import User

    fake = Factory.create()

    admin_email = 'cburmeister@discogs.com'
    admin_password = 'test123'

    users = []
    for _ in range(int(num_users)):
        users.append(
            User(
                fake.email(),
                fake.word() + fake.word(),
                fake.ipv4()
            )
        )

    users.append(
        User(
            admin_email,
            admin_password,
            fake.ipv4(),
            active=True,
            is_admin=True
        )
    )

    for user in users:
        db.session.add(user)

    db.session.commit()


class CRUDMixin(object):
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)

    @classmethod
    def get_by_id(cls, id):
        if any((isinstance(id, (str, bytes)) and id.isdigit(),
                isinstance(id, (int, float))),):
            return cls.query.get(int(id))
        return None

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        return instance.save()

    def update(self, commit=True, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        return commit and self.save() or self

    def save(self, commit=True):
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=True):
        db.session.delete(self)
        return commit and db.session.commit()


class DataTable(object):
    """
    Represents a sortable, filterable, searchable, and paginated set of data,
    generated by arguments in the request values.

    TODO:
    - flask-ext for access to request values?
    - throw some custom errors when getting fields, etc
    - get rid of the 4 helpers that do the same thing
    - should this generate some html to help with visualizing the data?
    """
    def __init__(self, model, columns, sortable, searchable, filterable, limits, request):
        self.model = model
        self.query = self.model.query
        self.columns = columns
        self.sortable = sortable
        self.orders = ['asc', 'desc']
        self.searchable = searchable
        self.filterable = filterable
        self.limits = limits

        self.get_selected(request)

        for f in self.filterable:
            self.selected_filter = request.values.get(f.name, None)
            self.filter(f.name, self.selected_filter)
        self.search(self.selected_query)
        self.sort(self.selected_sort, self.selected_order)
        self.paginate(self.selected_page, self.selected_limit)

    def get_selected(self, request):
        self.selected_sort = request.values.get('sort', self.sortables[0])
        self.selected_order = request.values.get('order', self.orders[0])
        self.selected_query = request.values.get('query', None)
        self.selected_limit = request.values.get('limit', self.limits[1], type=int)
        self.selected_page = request.values.get('page', 1, type=int)

    @property
    def _columns(self):
        return [x.name for x in self.columns]

    @property
    def sortables(self):
        return [x.name for x in self.sortable]

    @property
    def searchables(self):
        return [x.name for x in self.searchable]

    @property
    def filterables(self):
        return [x.name for x in self.filterable]

    @property
    def colspan(self):
        """Length of all columns."""
        return len(self.columns) + len(self.sortable) + len(self.searchable)

    def sort(self, field, order):
        """Sorts the data based on a field & order."""
        if field in self.sortables and order in self.orders:
            field = getattr(getattr(self.model, field), order)
            self.query = self.query.order_by(field())

    def filter(self, field, value):
        """Filters the query based on a field & value."""
        if field and value:
            field = getattr(self.model, field)
            self.query = self.query.filter(field==value)

    def search(self, search_query):
        """Filters the query based on a list of fields & search query."""
        if search_query:
            search_query = '%%%s%%' % search_query
            from sqlalchemy import or_
            fields = [getattr(self.model, x) for x in self.searchables]
            self.query = self.query.filter(or_(*[x.like(search_query) for x in fields]))

    def paginate(self, page, limit):
        """Paginate the query based on a page & limit."""
        self.query = self.query.paginate(page, limit)
