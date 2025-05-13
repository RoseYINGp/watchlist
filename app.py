from flask import Flask, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
import click
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)
# 初始化
login_manager = LoginManager(app)
# 创建用户id回调函数
@login_manager.user_loader
def load_user(user_id):
    user =db.session.get(User,int(user_id))
    return user

username = "root"
password = "dx050513"
host = '127.0.0.1'
port = 3306
database = "my_new_database"

app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://{}:{}@{}:{}/{}'.format(username, password, host, port, database)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# 设置SECRET_KEY
app.config['SECRET_KEY'] = 'your_secret_key'

db = SQLAlchemy(app)

# 创建数据库模型
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    username = db.Column(db.String(20))
    password_hash = db.Column(db.String(256))

    def set_password(self, password):
        # 生成密码字段
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    year = db.Column(db.String(4))


# 登入界面
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not username or not password:
            flash("账号密码错误")
            return redirect(url_for('login'))

        user = User.query.first()
        if username == user.username and user.validate_password(password):
            login_user(user)
            flash("登入成功")
            return redirect(url_for('hello_world'))
        flash('账号密码错误')
        return redirect(url_for('login'))
    return render_template('login.html')


# 登出界面
@app.route('/logout')
# 用于视图保护
@login_required
def logout():
    # 登出用户
    logout_user()
    flash("Goodbye")
    return redirect(url_for('hello_world'))


# 用户设置
@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form['name']

        if not name or len(name) > 20:
            flash('请重新输入')
            return redirect(url_for('settings'))
        # current_user 返回当前数据库记录 --- 相当于查询 再更新
        current_user.name = name
        db.session.commit()
        flash('更新成功')
        return redirect(url_for('settings'))
    return render_template('settings.html')


# 生成点数据
@app.cli.command()
def forge():
    db.create_all()
    name = 'xiao ming'
    movies = [
        {'title': 'My Neighbor Totoro', 'year': '1988'},
        {'title': 'Dead Poets Society', 'year': '1989'},
        {'title': 'A Perfect World', 'year': '1993'},
        {'title': 'Leon', 'year': '1994'},
        {'title': 'Mahjong', 'year': '1996'},
        {'title': 'Swallowtail Butterfly', 'year': '1996'},
        {'title': 'King of Comedy', 'year': '1999'},
        {'title': 'Devils on the Doorstep', 'year': '1999'},
        {'title': 'WALL-E', 'year': '2008'},
        {'title': 'The Pork of Music', 'year': '2012'},
    ]
    user = User(name=name)
    db.session.add(user)
    for m in movies:
        movie = Movie(title=m['title'], year=m['year'])
        db.session.add(movie)
    db.session.commit()
    click.echo('Done')


# 自定义数据库命令 --- 更新数据库结构（会清空数据)
@app.cli.command()
@click.option('--drop', is_flag=True, help='删除后创建.')
def initdb(drop):
    # 如果有数据库
    if drop:
        # 删除
        db.drop_all()
    #     重新创建
    db.create_all()
    click.echo("创建成功.")


# 自定义生成账户
@app.cli.command()
@click.option("--username", prompt=True, help="用于用户登入")
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True, help="用于用户登入密码")
def admin(username, password):
    db.create_all()
    user = User.query.first()
    if user is not None:
        click.echo("更新用户名....")
        user.username = username
        #         设置密码
        user.set_password(password)
    else:
        click.echo("创建用户....")
        user = User(username=username, name='Admin')
        #         设置密码
        user.set_password(password)
        db.session.add(user)

    db.session.commit()
    click.echo("Done")


@app.route('/', methods=['GET', 'POST'])
def hello_world():
    if request.method == 'POST':
        # 如果未进行验证
        if not current_user.is_authenticated:
            return redirect(url_for('hello_world'))
        title = request.form.get('title')
        year = request.form.get('year')
        if not title or not year or len(title) > 60 or len(year) > 4:
            flash("输入不符合!!!")
            # 重定向页面
            return redirect(url_for('hello_world'))
        movie = Movie(title=title, year=year)
        db.session.add(movie)
        db.session.commit()
        flash("添加数据成功!!!")
        #     页面重定向
        return redirect(url_for("hello_world"))
    user = User.query.first()
    movies = Movie.query.all()
    return render_template('index.html', user=user, movies=movies)



@app.errorhandler(404)
def page_not_found_404(e):
    user = User.query.first()
    return render_template("404.html", user=user), 404

@app.errorhandler(500)
def page_not_found_500(e):
    user = User.query.first()
    return render_template("500.html", user=user), 500

@app.errorhandler(400)
def page_not_found_400(e):
    user = User.query.first()
    return render_template("400.html", user=user), 400


# 模板上下文
@app.context_processor
def inject_user():
    user = User.query.first()
    return dict(user=user)


@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
@login_required
def edit(movie_id):
    movie = db.get_or_404(Movie,movie_id)
    if request.method == 'POST':
        title = request.form['title']
        year = request.form['year']
        if not title or not year or len(title) > 60 or len(year) > 4:
            flash('更新失败!!!')
            return redirect(url_for('edit', movie_id=movie_id))
        movie.title = title
        movie.year = year
        db.session.commit()
        flash('更新成功!!!')
        return redirect(url_for('hello_world'))
    return render_template('edit.html', movie=movie)


@app.route("/movie/delete/<int:movie_id>", methods=['POST'])
# 登入保护
@login_required
def delete(movie_id):
    movie = db.get_or_404(Movie,movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash("删除成功")
    # 重定向回主页
    return redirect(url_for('hello_world'))


@app.route("/insert", methods=['GET', 'POST'])
def inster():
    if request.method == 'POST':
        title = request.form.get('title')
        year = request.form.get('year')
        if not title or not year or len(title) > 60 or len(year) > 4:
            flash("输入不符合!!!")
            # 重定向页面
            return redirect(url_for('hello_world'))
        movie = Movie(title=title, year=year)
        db.session.add(movie)
        db.session.commit()
        flash("添加数据成功!!!")
        #     页面重定向
        return redirect(url_for("hello_world"))
    user = User.query.first()
    movie = Movie.query.all()
    return render_template('edit.html', user=user, movie=movie)


if __name__ == '__main__':
    try:
        with app.app_context():
            db.create_all()
        app.run(debug=True)
    except Exception as e:
        print(f"An error occurred: {e}")
