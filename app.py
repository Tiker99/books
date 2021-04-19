from flask import Flask, render_template, url_for, jsonify, request, redirect
import json

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
books = []
users = []
nicknames = []
passwords = []
admins = []
adm_nicks = []
user_nicks = []

active_user = None

with open("users.json") as user_list:
  users = json.load(user_list)

with open("admins.json") as admin_list:
    admins = json.load(admin_list)

with open("books.json") as book_list:
  books = json.load(book_list)


for user_aut in users:
  passwords.append(user_aut["password"])
  nicknames.append(user_aut["nickname"])
  user_nicks.append(user_aut["nickname"])

for admin_aut in admins:
  nicknames.append(admin_aut["nickname"])
  adm_nicks.append(admin_aut["nickname"])
  passwords.append(admin_aut["password"])

@app.route('/')
def main():
    return render_template("index.html")


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/login/aces',methods=["POST"])
def aces():
    if request.form['login'] not in nicknames or request.form['password'] not in passwords:
        return render_template('loginfail.html')
    for nick in nicknames:
        if nick == request.form['login']:
            break
    global active_user
    active_user = request.form['login']
    if nick in adm_nicks:
        return redirect('/admin')

    if nick not in adm_nicks:
        return redirect('/library')


@app.route('/change_pass')
def change_pass():
    return render_template('/change_pass.html',mismatch=True)


@app.route('/change_pass/done',methods=["POST"])
def change_pass_done():
    if request.form['password'] != request.form['password1']:
        return render_template('/change_pass.html',mismatched=True)
    for user in users:
        if user["nickname"] == active_user:
            break
    user["password"]=request.form["password"]
    with open('users.json', 'w') as wr:
        json.dump(users, wr, indent=2)
    return redirect('/library')


@app.route('/edit_favorites')
def edit_favorites():
    favs = []
    for user in users:
        if user["nickname"] == active_user:
            break
    for best in user["favorites"]:
        favs.append(best)

    book_titles = [book["title"] for book in books]
    return render_template("/edit_favs.html", books=book_titles, favs=favs)


@app.route('/edit_adm_favorites')
def edit_adm_favorites():
    favs = []
    for admin in admins:
        if admin["nickname"] == active_user:
            break
    for best in admin["favorites"]:
        favs.append(best)

    book_titles = [book["title"] for book in books]
    return render_template("/edit_adm_favs.html", books=book_titles, favs=favs)


@app.route("/library/<string:book>/<string:operation>")
def edit_books(book, operation):
    if operation == "add":
        for user in users:
            if user["nickname"] == active_user:
                break
        user['favorites'].append(book)
        with open("users.json", "w") as wr:
            json.dump(users, wr, indent=2)
        favs = user['favorites']
        book_titles = [book["title"] for book in books]
        return render_template("/edit_favs.html", books=book_titles, favs=favs)
    if operation == "remove":
        for user in users:
            if user["nickname"] == active_user:
                break
        user['favorites'].pop(user['favorites'].index(book))
        with open("users.json", "w") as wr:
            json.dump(users, wr, indent=2)
        favs = user['favorites']
        book_titles = [book["title"] for book in books]
        return render_template("/edit_favs.html", books=book_titles, favs=favs)


@app.route("/admin/<string:book>/<string:operation>")
def edit_adm_books(book, operation):
    if operation == "add":
        for admin in admins:
            if admin["nickname"] == active_user:
                break
        admin['favorites'].append(book)
        with open("admins.json", "w") as wr:
            json.dump(admins, wr, indent=2)
        favs = admin['favorites']
        book_titles = [book["title"] for book in books]
        return render_template("/edit_adm_favs.html", books=book_titles, favs=favs)
    if operation == "remove":
        for admin in admins:
            if admin["nickname"] == active_user:
                break
        admin['favorites'].pop(admin['favorites'].index(book))
        with open("admins.json", "w") as wr:
            json.dump(admins, wr, indent=2)
        favs = admin['favorites']
        book_titles = [book["title"] for book in books]
        return render_template("/edit_favs.html", books=book_titles, favs=favs)


@app.route('/signup')
def signup():
     return render_template('/signup.html')


@app.route('/signup/add_user',methods=['POST'])
def signuser():
    if request.form['password'] != request.form['password1']:
        return render_template('/signup.html', full_name=request.form['full_name'], nick=request.form['nickname'], mismatch=True)
    new_user = {
        "nickname": request.form['nickname'],
        "password": request.form['password'],
        "full_name": request.form['full_name'],
        "favorites": []
    }
    users.append(new_user)
    file = open("users.json", "w")
    file.write(json.dumps(users, indent=2))
    file.close()
    return redirect('/library')


@app.route('/library')
def library():
    favs = []
    for fav in users:
        if fav["nickname"] == active_user:
            break
    for best in fav["favorites"]:
        favs.append(best)
    book_titles = [book["title"] for book in books]
    return render_template("library.html", books=book_titles,favs=favs)


@app.route('/admin')
def admlib():
    favs = []
    for fav in admins:
        if fav["nickname"] == active_user:
            break
    for best in fav["favorites"]:
        favs.append(best)
    book_titles = [book['title'] for book in books]
    return render_template("admin.html", books=book_titles,favs=favs)
#<img src="" style="width:100%;height:100%;position:absolute;top:0;left:0;z-index:-5000;">


@app.route('/admindel')
def admindel():
    book_titles = [book['title'] for book in books]
    return render_template("admindel.html", user_nicks = user_nicks, books=book_titles)


@app.route('/admin')
def admin():
    return render_template('admin.html')


@app.route('/admin/<string:name>')
def bookadm(name):
    for book in books:
        if name == book["title"]:
            break
    return render_template('view_book.html',book=book)


@app.route('/library/<string:name>')
def book(name):
    for book in books:
        if name == book["title"]:
            break
    return render_template('view_book.html',book=book)


@app.route('/admindel/deluser/<string:name>')
def deluser(name):
     for i in range(len(users)):
         if users[i]["nickname"] == name:
            users.pop(i)
            break
     open("users.json", "w").write(
         json.dumps(users, sort_keys=True, indent=2, separators=(',', ': '))
     )
     return redirect('/admin')


@app.route('/admindel/delbook/<string:name>')
def delbook(name):
     for i in range(len(books)):
         if books[i]["title"] == name:
            books.pop(i)
            break
     open("books.json", "w").write(
         json.dumps(books, sort_keys=True, indent=2, separators=(',', ': '))
     )
     return redirect('/admin')


@app.route('/new_book')
def display():
    return render_template("new.html")


@app.route('/new_book/add_book', methods=["POST"])
def add_book():
    if request.method == "POST":
        new_title = request.form['title']
        new_author = request.form['author']
        new_genre = request.form['genre'].split(' ')
        new_pages = int(request.form['pages'])
        new_chapters = int(request.form['chapters'])
        new_release = int(request.form['release'])
        books.append({
            "title": new_title,
            "author": new_author,
            "genre": new_genre,
            "pages": new_pages,
            "chapters": new_chapters,
            "release": new_release
        })
        with open('books.json', 'w') as wr:
            json.dump(books, wr, indent=2)
        return redirect('/library')
    return render_template('/new_book')


@app.route('/addbookadm')
def displayadm():
    return render_template("addbookadm.html")


@app.route('/addbookadm/add_book', methods=["POST"])
def add_bookadm():
    if request.method == "POST":
        new_title = request.form['title']
        new_author = request.form['author']
        new_genre = request.form['genre'].split(' ')
        new_pages = int(request.form['pages'])
        new_chapters = int(request.form['chapters'])
        new_release = int(request.form['release'])
        books.append({
            "title": new_title,
            "author": new_author,
            "genre": new_genre,
            "pages": new_pages,
            "chapters": new_chapters,
            "release": new_release
        })
        with open('books.json', 'w') as wr:
            json.dump(books, wr, indent=2)
        return redirect('/admin')
    return render_template('/new_book')



if __name__ == "__main__":
    app.run(debug=True)
