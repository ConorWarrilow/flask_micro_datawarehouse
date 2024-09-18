from flask import render_template, request, url_for, Blueprint
from powerpy.models import Post, Database
from flask_login import current_user, login_required

# similar to app = Flask(__name__)
main = Blueprint('main', __name__)


@main.context_processor
def inject_total_databases():
    total_databases = Database.query.count()  # Get the total number of databases
    return {'total_databases': total_databases}








@main.route("/")
@main.route("/home")
def home():

    total_databases = Database.query.count()


    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', posts=posts, total_databases=total_databases)


@main.route("/about")
def about():
    return render_template('about.html', title='About')


@main.route("/base")
def base():

    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)

    return render_template('/layouts/base_secondary.html', title='base', image_file=image_file)


















#
#
#    <h1 class="mb-3">No databases. Create one below!</h1>
#    <form method="POST" action="" novalidate>
#        {{ form.hidden_tag() }}
#        <fieldset class="form-group">
#            <legend class="border-bottom mb-4">{{ legend }}</legend> <!-- legend variable-->
#            <div class="form-group">
#                {{form.database_name.label(class="form-control-label") }}
#                {% if form.database_name.errors %}
#                {{form.database_name(class="form-control form-control-lg is-invalid") }}
#                <div class="invalid-feedback">
#                    {% for error in form.database_name.errors %}
#                        <span>{{ error }}</span>
#                    {% endfor %}
#                </div>
#                {% else %}
#                    {{form.database_name(class="form-control form-control-lg") }}
#                {% endif %}
#            </div>
#            <div class="form-group">
#                {{form.database_description.label(class="form-control-label") }}
#                {% if form.database_description.errors %}
#                {{form.database_description(class="form-control form-control-lg is-invalid") }}
#                <div class="invalid-feedback">
#                    {% for error in form.database_description.errors %}
#                        <span>{{ error }}</span>
#                    {% endfor %}
#                </div>
#                {% else %}
#                    {{form.database_description(class="form-control form-control-lg") }}
#                {% endif %}
#            </div>
#            <div class="form-group">
#                {{form.default_schema.label(class="form-control-label") }}
#                {% if form.default_schema.errors %}
#                {{form.default_schema(class="form-control form-control-lg is-invalid") }}
#                <div class="invalid-feedback">
#                    {% for error in form.default_schema.errors %}
#                        <span>{{ error }}</span>
#                    {% endfor %}
#                </div>
#                {% else %}
#                    {{form.default_schema(class="form-control form-control-lg") }}
#                {% endif %}
#            </div>
#            <div class="form-group">
#                {{form.schema_description.label(class="form-control-label") }}
#                {% if form.schema_description.errors %}
#                {{form.schema_description(class="form-control form-control-lg is-invalid") }}
#                <div class="invalid-feedback">
#                    {% for error in form.schema_description.errors %}
#                        <span>{{ error }}</span>
#                    {% endfor %}
#                </div>
#                {% else %}
#                    {{form.schema_description(class="form-control form-control-lg") }}
#                {% endif %}
#            </div>
#        </fieldset>
#        <div class="form-group">
#            {{ form.submit(class="modal-submit-button") }}
#        </div>
#    </form>





#
#
#    <div class="modal fade" id="createDatabaseModal" tabindex="-1" role="dialog" aria-labelledby="createDatabaseModalLabel" aria-hidden="true">
#        <div class="modal-dialog" role="document">
#            <div class="modal-content">
#                <div class="modal-header">
#                    <h5 class="modal-title" id="createDatabaseModalLabel">Create New Database</h5>
#                    <button type="button" class="close" data-dismiss="modal" aria-label="Close">
#                        <span aria-hidden="true">&times;</span>
#                    </button>
#                </div>
#                <div class="modal-body">
#                    <form method="POST" action="" novalidate>
#                        {{ form.hidden_tag() }}
#                        <div class="form-group">
#                            {{form.database_name.label(class="form-control-label") }}
#                            {% if form.database_name.errors %}
#                            {{form.database_name(class="form-control form-control-lg is-invalid") }}
#                            <div class="invalid-feedback">
#                                {% for error in form.database_name.errors %}
#                                    <span>{{ error }}</span>
#                                {% endfor %}
#                            </div>
#                            {% else %}
#                                {{form.database_name(class="form-control form-control-lg") }}
#                            {% endif %}
#                        </div>
#                        <div class="form-group">
#                            {{form.database_description.label(class="form-control-label") }}
#                            {% if form.database_description.errors %}
#                            {{form.database_description(class="form-control form-control-lg is-invalid") }}
#                            <div class="invalid-feedback">
#                                {% for error in form.database_description.errors %}
#                                    <span>{{ error }}</span>
#                                {% endfor %}
#                            </div>
#                            {% else %}
#                                {{form.database_description(class="form-control form-control-lg") }}
#                            {% endif %}
#                        </div>
#                        <div class="form-group">
#                            {{form.default_schema.label(class="form-control-label") }}
#                            {% if form.default_schema.errors %}
#                            {{form.default_schema(class="form-control form-control-lg is-invalid") }}
#                            <div class="invalid-feedback">
#                                {% for error in form.default_schema.errors %}
#                                    <span>{{ error }}</span>
#                                {% endfor %}
#                            </div>
#                            {% else %}
#                                {{form.default_schema(class="form-control form-control-lg") }}
#                            {% endif %}
#                        </div>
#                        <div class="form-group">
#                            {{form.schema_description.label(class="form-control-label") }}
#                            {% if form.schema_description.errors %}
#                            {{form.schema_description(class="form-control form-control-lg is-invalid") }}
#                            <div class="invalid-feedback">
#                                {% for error in form.schema_description.errors %}
#                                    <span>{{ error }}</span>
#                                {% endfor %}
#                            </div>
#                            {% else %}
#                                {{form.schema_description(class="form-control form-control-lg") }}
#                            {% endif %}
#                        </div>
#                        <div class="form-group position-right">
#                            {{ form.submit(class="modal-submit-button") }}
#                        </div>
#                    </form>
#                </div>
#            </div>
#        </div>
#    </div>
#
#
#