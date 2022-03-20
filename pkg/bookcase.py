import json

try:
    from pkg.book import book
except ImportError:
    from book import book
import requests
import unittest
import dateutil.parser


class bookcase:
    def __init__(self) -> None:
        self.books = []
        self.new_id = 0

    def add(
        self,
        title,
        author,
        publication_date,
        isbn,
        number_of_pages,
        cover_url,
        language,
    ):
        book_id = self.new_id
        self.new_id += 1
        new_book = book(
            title,
            author,
            publication_date,
            isbn,
            number_of_pages,
            cover_url,
            language,
            book_id,
        )

        self.books.append(new_book)
        ...

    def edit(
        self,
        book_id,
        title,
        author,
        publication_date,
        isbn,
        number_of_pages,
        cover_url,
        language,
    ):
        for b in self.books:
            if b.id == book_id:
                b.title = title
                b.author = author
                b.publication_date = publication_date
                b.ISBN = isbn
                b.number_of_pages = number_of_pages
                b.cover_url = cover_url
                b.language = language
                return

    def find(
        self, title=None, author=None, language=None, start_date=None, end_date=None
    ):
        out = []
        for b in self.books:
            flag = True
            if title and title not in b.title:
                flag = False
            if author and author not in b.author:
                flag = False
            if language and language != b.language:
                flag = False
            if start_date and start_date > b.publication_date:
                flag = False
            if end_date and end_date < b.publication_date:
                flag = False
            if flag:
                out.append(b)

        return out

    def import_from_api(self, query):

        if isinstance(query, list):
            query = "+".join(query)

        api_query = "https://www.googleapis.com/books/v1/volumes?q=" + query

        resp = requests.get(api_query)
        if resp.status_code != 200:
            return

        data = json.loads(resp.content)
        for volume in data["items"]:
            book_info = volume["volumeInfo"]

            title = book_info["title"]
            try:
                author = ", ".join(book_info["authors"])
            except KeyError:
                author = None
            # publication_date = book_info["publishedDate"]
            try:
                publication_date = book_info["publishedDate"]
            except KeyError:
                publication_date = None
            # isbn=book_info["industryIdentifiers"]#[0]#["identifier"]
            isbn = [
                elem["identifier"]
                for elem in book_info["industryIdentifiers"]
                if elem["type"] == "ISBN_13"
            ]
            if isbn == []:
                isbn = (
                    book_info["industryIdentifiers"][0]["type"]
                    + " : "
                    + book_info["industryIdentifiers"][0]["identifier"]
                )
            else:
                isbn = isbn[0]

            try:
                number_of_pages = book_info["pageCount"]
            except KeyError:
                number_of_pages = None
            try:
                cover_url = book_info["imageLinks"]["thumbnail"]
            except KeyError:
                cover_url = None

            try:
                language = book_info["language"]
            except KeyError:
                language = None

            self.add(
                title,
                author,
                publication_date,
                isbn,
                number_of_pages,
                cover_url,
                language,
            )

        # print(data)

        ...


class test_bookcase(unittest.TestCase):
    def setUp(self):
        self.bk = bookcase()

    def test_add(self):
        date = "2000-10-30"
        self.bk.add("title", "author", date, 12345, 15, "www.url.com", "en")
        expected = book("title", "author", date, 12345, 15, "www.url.com", "en", 0)
        actual = self.bk.books[0]
        self.assertEqual(dict(actual), dict(expected))

    def test_edit(self):
        expected = book(
            "title", "author", "2000-10-30", 12345, 15, "www.url.com", "en", 0
        )
        self.bk.add("title1", "author1", "2001-10-30", 2, 10, "www.url.pl", "pl")

        date = dateutil.parser.parse("2000-10-30").date()
        self.bk.edit(
            0,
            "title",
            "author",
            date,
            12345,
            15,
            "www.url.com",
            "en",
        )

        actual = self.bk.books[0]
        self.assertEqual(dict(actual), dict(expected))

    def test_find(self):
        book_set = [
            ("title one", "author one", "2001-10-30", 12345, 15, "www.url.com", "en"),
            ("title one", "author two", "2002-10-30", 12345, 15, "www.url.com", "en"),
            ("title one", "author one", "2003-10-30", 12345, 15, "www.url.com", "en"),
            ("title one", "author two", "2004-10-30", 12345, 15, "www.url.com", "en"),
            ("title two", "author one", "2005-10-30", 12345, 15, "www.url.com", "en"),
            ("title two", "author two", "2006-10-30", 12345, 15, "www.url.com", "pl"),
            ("title two", "author one", "2007-10-30", 12345, 15, "www.url.com", "en"),
            ("title two", "author two", "2008-10-30", 12345, 15, "www.url.com", "en"),
        ]
        for b in book_set:
            self.bk.add(*b)
        start_date = dateutil.parser.parse("2004-9-30").date()
        end_date = dateutil.parser.parse("2007-11-30").date()
        actual = self.bk.find("", "two", "en", start_date, end_date)
        expected = [book(*book_set[3], 3)]
        self.assertEqual(
            [dict(elem) for elem in actual], [dict(elem) for elem in expected]
        )


if __name__ == "__main__":
    unittest.main()