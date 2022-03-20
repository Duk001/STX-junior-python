import dateutil.parser


class book:
    def __init__(
        self,
        title,
        author,
        publication_date,
        isbn,
        number_of_pages,
        cover_url,
        language,
        book_id,
    ):
        self.title = title
        self.author = author
        if isinstance(publication_date, str):
            self.publication_date = dateutil.parser.parse(publication_date).date()
        else:
            self.publication_date = publication_date
        self.ISBN = isbn
        self.number_of_pages = number_of_pages
        self.cover_url = cover_url
        self.language = language
        self.id = book_id

    def __iter__(self):
        yield "title", self.title
        yield "author", self.author
        yield "publication date", self.publication_date
        yield "isbn", self.ISBN
        yield "pages", self.number_of_pages
        yield "cover url", self.cover_url
        yield "language", self.language
        yield "id", self.id
