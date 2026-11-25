from flask import Flask, render_template, request, redirect, url_for, session, flash, Blueprint, current_app, make_response, g,jsonify
from functools import wraps
from google.oauth2 import id_token
from google.auth.transport import requests
import json
from src.models import User,Session
from src.utils import init_session
from src.routes.auth.StoreOwnerRoutes import login_required_owner
from src.models.applicationDocuments import ApplicationDocument
from src.forms.StoreOwner.RegisterStore import StoreRegistrationForm
from src.models.StoreOwner import StoreOwner
from src.models.storeApplication import StoreApplication
from src.models.Store import Store

admin_bp = Blueprint('admin',__name__)

@admin_bp.route('/ApprovedList', methods=['GET', 'POST'])
def ApprovedList():
    form = StoreRegistrationForm()
    storeowners = StoreOwner.get_approvedStores()
    return render_template('admin/ApprovedList.html', storeowners=storeowners, form=form)


@admin_bp.route('/adminbase')
def adminbase():
    return render_template('adminbase.html')


@admin_bp.route('/PendingList', methods=['GET' , 'POST'])
def PendingList():
    form = StoreRegistrationForm()
    applicants = StoreOwner.get_pending_store_owner()
    documents = StoreOwner.get_preview_store_owner()

    if request.method == 'POST' and form.validate_on_submit():
        # Assuming form data processing happens here.
        store_owner_id = form.store_owner_id.data
        application_status = form.application_status.data

        # Perform application and store owner verification updates.
        StoreOwner.get_store_owner_verification(store_owner_id)
        StoreOwner.get_store_application_verification(store_owner_id)

        return redirect(url_for('admin.PendingList'))
    return render_template('admin/PendingList.html', applicants=applicants, documents=documents, form=form)

@admin_bp.route('/PreviewDocuments', methods=['GET', 'POST'])
def preview_documents():
    form = StoreRegistrationForm()
    documents = StoreOwner.get_preview_store_owner()

    if request.method == 'POST' and form.validate_on_submit():
        # Assuming form data processing happens here.
        store_owner_id = form.store_owner_id.data
        application_status = form.application_status.data

        # Perform application and store owner verification updates.
        StoreOwner.get_store_owner_verification(store_owner_id)
        StoreOwner.get_store_application_verification(store_owner_id)

        return redirect(url_for('admin.preview_documents'))

    return render_template('admin/PreviewDocuments.html', form=form, documents=documents)

@admin_bp.route('/VerifyStatus/<StoreOwnerId>', methods=["POST"])
def VerifyStatus(StoreOwnerId):
    # Update StoreOwner and StoreApplication statuses
    StoreOwner.get_store_owner_verification(StoreOwnerId)
    StoreOwner.get_store_application_verification(StoreOwnerId)

    #Create Store
    Store_Application = StoreApplication.get_approved_store_application(StoreOwnerId)
        
    Store.create_store(Store_Application['StoreName'], StoreOwnerId, Store_Application['StoreApplicationId'])


    # Redirect back to the preview documents page
    return redirect(url_for('admin.PendingList'))


@admin_bp.route('/RejectApplication/<StoreOwnerId>', methods=["POST"])
def RejectApplication(StoreOwnerId):
    # Update StoreOwner and StoreApplication statuses
    StoreOwner.set_application_rejected(StoreOwnerId)
    StoreOwner.set_application_default(StoreOwnerId)


    # Redirect back to the preview documents page
    return redirect(url_for('admin.PendingList'))


