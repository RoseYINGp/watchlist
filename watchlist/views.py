from flask import render_template, request, url_for, redirect, flash
from flask_login import login_user, login_required, logout_user, current_user
from jinja2.runtime import new_context

from watchlist import app, db
from watchlist.models import User, Movie, Comment


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if not current_user.is_authenticated:
            return redirect(url_for('index'))

        title = request.form['title']
        year = request.form['year']

        if not title or not year or len(year) != 4 or len(title) > 60:
            flash('Invalid input.')
            return redirect(url_for('index'))

        movie = Movie(title=title, year=year)
        db.session.add(movie)
        db.session.commit()
        flash('Item created.')
        return redirect(url_for('index'))

    movies = Movie.query.all()
    return render_template('index.html', movies=movies)


@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
@login_required
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)

    if request.method == 'POST':
        title = request.form['title']
        year = request.form['year']

        if not title or not year or len(year) != 4 or len(title) > 60:
            flash('Invalid input.')
            return redirect(url_for('edit', movie_id=movie_id))

        movie.title = title
        movie.year = year
        db.session.commit()
        flash('Item updated.')
        return redirect(url_for('index'))

    return render_template('edit.html', movie=movie)


@app.route("/movie/comment/<int:movie_id>", methods=['GET', 'POST'])
def comment(movie_id):
    movie = Movie.query.get_or_404(movie_id)

    if request.method == 'POST':
        # 直接从request.form获取评论内容
        # 获取input name=comment中的值
        comment_text = request.form.get('comment', '').strip()  # 防止空字符串

        # 手动验证：评论内容是否为空
        if not comment_text:
            flash("Please enter a comment.")
            return redirect(url_for('comment', movie_id=movie_id))

        # 创建评论对象并关联电影ID
        new_comment = Comment(
            movie_id=movie_id,
            comment_text=comment_text
        )
        db.session.add(new_comment)
        db.session.commit()

        flash('Comment created successfully!')
        return redirect(url_for('comment', movie_id=movie_id))

    # 渲染模板（无需传递表单对象）
    return render_template('comment.html', movie=movie)


@app.route('/movie/delete/<int:movie_id>', methods=['POST'])
@login_required
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('Item deleted.')
    return redirect(url_for('index'))


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form['name']

        if not name or len(name) > 20:
            flash('Invalid input.')
            return redirect(url_for('settings'))

        user = User.query.first()
        user.name = name
        db.session.commit()
        flash('Settings updated.')
        return redirect(url_for('index'))

    return render_template('settings.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.first()
        if not user:
            if not user:
                flash('请创建第一个用户')
                return redirect(url_for('login'))
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('login'))

        user = User.query.first()

        if username == user.username and user.validate_password(password):
            login_user(user)
            flash('Login success.')
            return redirect(url_for('index'))

        flash('Invalid username or password.')
        return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Goodbye.')
    return redirect(url_for('index'))
