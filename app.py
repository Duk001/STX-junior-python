from flask import Flask, request, jsonify, render_template, redirect, url_for
from pkg.bookcase import bookcase
import dateutil.parser
from wtforms import (
    Form,
    StringField,
    validators,
    DateField,
    IntegerField,
)

bk = bookcase()
app = Flask(__name__)


class AddForm(Form):
    title = StringField(
        "title", [validators.Length(min=1), validators.DataRequired()], default=""
    )
    author = StringField(
        "author", [validators.Length(min=1), validators.DataRequired()], default=""
    )
    language = StringField(
        "language", [validators.Length(min=1), validators.DataRequired()], default=""
    )
    isbn = StringField(
        "isbn", [validators.Length(min=1), validators.DataRequired()], default=""
    )
    pages = IntegerField(
        "pages",
        [validators.NumberRange(min=0, max=10000), validators.DataRequired()],
        default="",
    )
    cover_url = StringField(
        "cover_url", [validators.Length(min=1), validators.DataRequired()], default=""
    )
    date = DateField(
        "date", format="%Y-%m-%d", validators=[validators.DataRequired()], default=""
    )


class AddAPIForm(Form):
    key_words = StringField(
        "key_words", [validators.Length(min=1), validators.DataRequired()], default=""
    )


@app.route("/api/books/", methods=["GET"])
def rest_func():
    args = request.args
    title = args.get("title")
    author = args.get("author")
    language = args.get("language")
    start_date = args.get("start_date")
    if start_date:
        start_date = dateutil.parser.parse(start_date).date()
    end_date = args.get("end_date")
    if end_date:
        end_date = dateutil.parser.parse(end_date).date()

    if not any([title, author, language, start_date, end_date]):
        books = [dict(b) for b in bk.books]
        return jsonify(books)

    books = [
        dict(b)
        for b in bk.find(
            title=title,
            author=author,
            language=language,
            start_date=start_date,
            end_date=end_date,
        )
    ]
    return jsonify(books)


@app.route("/")
def home_page():
    list_of_books = [dict(b) for b in bk.books]
    return render_template("home.html", length=len(list_of_books), books=list_of_books)


@app.route("/add", methods=["GET", "POST"])
def add_book():

    if request.method == "POST":
        form = AddForm(request.form)
        bk.add(
            form.title.data,
            form.author.data,
            form.date.data,
            form.isbn.data,
            form.pages.data,
            form.cover_url.data,
            form.language.data,
        )
        return redirect(url_for("home_page"))
    form = AddForm()
    return render_template(
        "add_form.html", mode="Dodaj", form=form, submit_address="/add"
    )


@app.route("/add_api", methods=["GET", "POST"])
def add_book_api():

    if request.method == "POST":
        form = AddAPIForm(request.form)
        words = form.key_words.data.split(",")
        bk.import_from_api(words)
        return redirect(url_for("home_page"))
    form = AddAPIForm()
    return render_template(
        "add_form_api.html",
        mode="Dodaj poprzez API",
        form=form,
        submit_address="/add_api",
    )


@app.route("/edit", methods=["GET", "POST"])
def edit_book():

    if request.method == "POST":
        args = request.args
        book_id = int(args.get("book_id"))
        form = AddForm(request.form)
        bk.edit(
            book_id,
            form.title.data,
            form.author.data,
            form.date.data,
            form.isbn.data,
            form.pages.data,
            form.cover_url.data,
            form.language.data,
        )
        return redirect(url_for("home_page"))

    args = request.args
    book_id = int(args.get("book_id"))
    b = [dict(elem) for elem in bk.books if elem.id == book_id]
    if b == []:
        return redirect(url_for("home_page"))
    b = b[0]
    form = AddForm()
    form.title.data = b["title"]
    form.author.data = b["author"]
    form.language.data = b["language"]
    form.isbn.data = b["isbn"]
    form.pages.data = b["pages"]
    form.cover_url.data = b["cover url"]
    form.date.data = b["publication date"]

    return render_template(
        "add_form.html",
        mode="Edytuj",
        form=form,
        submit_address=url_for("edit_book", book_id=[book_id]),
    )


if __name__ == "__main__":
    bk = bookcase()
    bk.import_from_api("Harry")
    bk.import_from_api("Hobbit")
    app.run()
