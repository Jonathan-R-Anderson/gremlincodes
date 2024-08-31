from flask import Blueprint, render_template, request, redirect, url_for, flash
from shared import sysAdminContract, gremlinDAOContract, gremlinThreadContract, gremlinPostContract, posterContract

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/')
def admin_panel():
    # Load data to display on the admin panel
    sysadmin_owner = sysAdminContract.functions.owner().call()
    dao_reserve = gremlinDAOContract.functions.reserve().call()
    threads_count = gremlinThreadContract.functions.getThreadInfo(0).call()[0]  # Example for thread count
    posts_count = gremlinPostContract.functions.getPostCount().call()
    poster_balance = posterContract.functions.getContributionScore("0xYourAddress").call()  # Example for poster balance

    return render_template('admin_panel.html', sysadmin_owner=sysadmin_owner, dao_reserve=dao_reserve,
                           threads_count=threads_count, posts_count=posts_count, poster_balance=poster_balance)

@admin_bp.route('/create-thread', methods=['POST'])
def create_thread():
    subject = request.form['subject']
    tags = request.form.getlist('tags')
    attachments = request.form.getlist('attachments')

    try:
        gremlinThreadContract.functions.createThread(subject, tags, attachments).transact()
        flash('Thread created successfully!', 'success')
    except Exception as e:
        flash(f'Error creating thread: {e}', 'danger')
    
    return redirect(url_for('admin.admin_panel'))

@admin_bp.route('/create-post', methods=['POST'])
def create_post():
    thread_id = int(request.form['thread_id'])
    name = request.form['name']
    email = request.form['email']
    trip_code = request.form['trip_code']
    magnet_url = request.form['magnet_url']

    try:
        gremlinPostContract.functions.createPost(thread_id, name, email, trip_code, magnet_url, "example.com").transact()
        flash('Post created successfully!', 'success')
    except Exception as e:
        flash(f'Error creating post: {e}', 'danger')
    
    return redirect(url_for('admin.admin_panel'))

@admin_bp.route('/set-reserve', methods=['POST'])
def set_reserve():
    new_reserve = int(request.form['new_reserve'])

    try:
        gremlinDAOContract.functions.setReserve(new_reserve).transact()
        flash('Reserve set successfully!', 'success')
    except Exception as e:
        flash(f'Error setting reserve: {e}', 'danger')
    
    return redirect(url_for('admin.admin_panel'))

@admin_bp.route('/set-sysadmin', methods=['POST'])
def set_sysadmin():
    new_sysadmin = request.form['new_sysadmin']

    try:
        sysAdminContract.functions.setSysAdmin(new_sysadmin).transact()
        flash('SysAdmin set successfully!', 'success')
    except Exception as e:
        flash(f'Error setting SysAdmin: {e}', 'danger')
    
    return redirect(url_for('admin.admin_panel'))
