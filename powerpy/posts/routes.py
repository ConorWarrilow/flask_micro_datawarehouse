from flask import Blueprint

from flask import render_template, url_for, flash, redirect, request, abort
from powerpy.posts.forms import PostForm
from powerpy import db
from powerpy.models import User, Post
from flask_login import current_user, login_required


# similar to app = Flask(__name__)
posts = Blueprint('posts', __name__)



@posts.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user) # can use user id instead of author, here we're just using the backreference
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('main.home'))

    return render_template('posts/create_post.html', title='New Post', form=form,
                           legend='New Post')


# Allows us to look at individual posts. we use a variable in our route i.e. the id of a post is in the route. We can also specify the dtype of a variable.
@posts.route("/post/<int:post_id>", methods=['GET', 'POST'])
def post(post_id):
    post = Post.query.get_or_404(post_id) # If it doesn't exist, return a 404
    return render_template('post.html', title=post.title, post=post)



# update or delete a post
@posts.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    # This line obtains the data for the specific post
    post = Post.query.get_or_404(post_id) # If it doesn't exist, return a 404
    if post.author != current_user:
        abort(403) # http response for a forbidden route
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated.', 'success')
        return redirect(url_for('posts.post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content

    return render_template('posts/create_post.html', title='Update Post',
                           form=form, legend='Update Post')


@posts.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('main.home'))










