from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify, make_response
)
import pdfkit
import pandas as pd
from werkzeug.exceptions import abort
import time
from datetime import datetime, timedelta
from sqlalchemy import func
import requests
import smtplib
from email.message import EmailMessage
from InterfaceSoft.auth import login_required
from InterfaceSoft.app_configs.databases_uri import check_main_db
from InterfaceSoft import db
from InterfaceSoft.models import Reading
from InterfaceSoft.local_configs import get_node, get_outlook_pwd, get_email_address
from InterfaceSoft.data_formating import hourly_formating

NODE = get_node()

NODE_IP = f"{NODE['ip']}:{NODE['port']}"
INTERFACE_NAME = f"{NODE['hostname']}"
MAX_INTERNAL_LIMIT = 6

bp = Blueprint('reading', __name__)

# Create a dictionary of empty lists for different types of nodes
SYSTEM_NODES = {key: [] for key in
                ["master_list", "transmitter_list", "data_server_list", "maintenance_pc_list", "interface_list"]}


@bp.route('/')
# @login_required
def index():
    # Render an HTML template that displays the readings list
    return render_template('reading/index.html')


@bp.route('/pdf')
def html_to_pdf():
    # filter the Reading table by the created_at value in the last 24 hours
    readings = Reading.query.filter(Reading.created_at >= datetime.now() - timedelta(hours=82)).all()
    hourly_readings = hourly_formating(readings)
    # return a JSON response with the hourly readings and the node name
    data = {"readings": hourly_readings, "node": NODE}
    # Render the HTML template with the data
    html = render_template('reading/pdf/index.html', data=data)
    # Use the full path to the wkhtmltopdf executable
    config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
    options = {"enable-local-file-access": "", "load-media-error-handling": "ignore"}
    # Create a PDF file from the HTML template
    pdf = pdfkit.from_string(html, False, configuration=config, options=options)
    # Return the PDF file as a Flask response
    response = make_response(pdf)
    response.mimetype = "application/pdf"
    response.headers["Content-Disposition"] = "attachment; filename=pipeline-soil-temperature-dr.pdf"
    # return jsonify({"readings": hourly_readings, "node": NODE})
    # return render_template('reading/pdf/index.html', data=data)
    return response


@bp.route('/send-email')
def send_email():
    receiver = "bernard.bogos@gmail.com"
    # Get the PDF file as a binary response from the Flask route
    # Specify the proxy settings using the proxies argument
    response = requests.get(f"http://{NODE['ip']}:{NODE['port']}/pdf")
    pdf_file = response.content
    # Create an email message with the PDF file as an attachment
    msg = EmailMessage()
    msg["Subject"] = "Soil Temperature Daily Report - COTCO"
    msg["From"] = get_email_address()
    msg["To"] = receiver
    msg.set_content("Here is Soil Temperature Daily Report.")
    msg.add_attachment(pdf_file, maintype="application", subtype="pdf", filename="pipeline-soil-temperature-dr.pdf")
    # Create a secure SMTP connection to Outlook's server
    # Change the SMTP object from smtplib.SMTP_SSL to smtplib.SMTP
    smtp_server = smtplib.SMTP("smtp-mail.outlook.com", 587)
    # Identify yourself to the server
    smtp_server.ehlo()
    # Start a secure connection using starttls()
    smtp_server.starttls()
    # Login to the SMTP server using your Outlook email and password (or app password)
    smtp_server.login(get_email_address(), get_outlook_pwd())
    # Send the email message using the SMTP server
    smtp_server.send_message(msg)
    # Quit the SMTP server
    smtp_server.quit()
    return jsonify({"status": "Done"})


@bp.route('/system-data-update', methods=["GET", "POST"])
def system_data_update():
    global NODE
    node = get_node()
    if request.method == 'GET':
        return NODE_IP
    # Get the JSON data from the request
    node_list_data = request.json
    SYSTEM_NODES["master_list"] = node_list_data["master_list"]
    SYSTEM_NODES["transmitter_list"] = node_list_data["transmitter_list"]
    SYSTEM_NODES["data_server_list"] = node_list_data["data_server_list"]
    SYSTEM_NODES["maintenance_pc_list"] = node_list_data["maintenance_pc_list"]
    SYSTEM_NODES["interface_list"] = node_list_data["interface_list"]
    for master_node in SYSTEM_NODES["master_list"]:
        if master_node["hostname"] == node["hostname"]:
            NODE = master_node
            g.node = master_node
    return NODE_IP


@bp.route('/save-reading', methods=["POST"])
def save_reading():
    reading_to_save = request.json
    # Create a new Reading object with the sensor data and the requestor data
    new_reading = Reading(
        trans_id=reading_to_save["trans_id"],
        created_at=reading_to_save["created_at"],
        order_num=reading_to_save["order_num"],
        requestor_id=reading_to_save["requestor_id"],
        temp_1=reading_to_save["temp_1"],
        temp_2=reading_to_save["temp_2"],
        rtd_1=reading_to_save["rtd_1"],
        rtd_2=reading_to_save["rtd_2"],
        is_data_transmitted=reading_to_save["is_data_transmitted"]
    )
    # Add the new Reading object to the database session
    db.session.add(new_reading)
    # Commit the changes to the database
    db.session.commit()
    # Get the latest reading from the database or None if no row is found
    reading = Reading.query.order_by(Reading.created_at.desc()).first()
    reading_dict = reading.as_dict()  # convert the Reading object to a dictionary
    json_object = jsonify(reading_dict)  # convert the dictionary to a JSON object
    # print(reading_dict['id'])
    # print(json_object.get_json())
    return json_object


@bp.route('/save-unsaved-readings', methods=["POST"])
def save_unsaved_readings():
    unsaved_readings = request.json
    print(f"Unsaved Readings | {unsaved_readings}")
    return jsonify(unsaved_readings)


@bp.route('/internal-reading-list', methods=['GET'])
def internal_reading_list():
    # create a subquery to get the maximum created_at value for each trans_id
    subquery = db.session.query(Reading.trans_id, db.func.max(Reading.created_at).label('max_created_at')).group_by(
        Reading.trans_id).subquery()
    # join the Reading table with the subquery and filter by the matching trans_id and created_at values
    readings = Reading.query.join(subquery, (Reading.trans_id == subquery.c.trans_id) & (
            Reading.created_at == subquery.c.max_created_at)).all()
    # convert the readings list to a list of dictionaries using the as_dict method
    local_readings_dict = [reading.as_dict() for reading in readings]
    # format the created_at attribute as an ISO string for each reading dictionary
    local_readings = [{**reading, "created_at": reading["created_at"].isoformat(timespec="seconds")} for reading in
                      local_readings_dict]
    # return a JSON response with the readings list and the node name
    return jsonify({"readings": local_readings, "node": NODE})


@bp.route('/handle-non-transmitted-readings/<int:time_range>', methods=['GET'])
def hdl_non_transmitted_readings(time_range):
    # # get the current time
    # now = datetime.now()
    # # get the time 10 minutes ago
    # ten_minutes_ago = now - timedelta(minutes=time_range)
    # # Create an empty list to store the reading dictionaries
    data = []
    # # query the Reading table and filter by created_at and is_data_transmitted columns
    # non_transmitted_readings = db.session.query(Reading) \
    #     .filter(Reading.created_at >= ten_minutes_ago, Reading.is_data_transmitted == False).all()
    # # Loop through each reading object
    # for reading in non_transmitted_readings:
    #     # Convert the row to a dictionary using the as_dict method
    #     reading_dict = reading.as_dict()
    #     # Convert the datetime object to a string using isoformat method with timespec argument
    #     reading_dict["created_at"] = reading_dict["created_at"].isoformat(timespec="microseconds")
    #     # Append the reading dictionary to the data list
    #     data.append(reading_dict)
    #     # Return a JSON response with the data list
    return jsonify(data)


@bp.route('/get-latest-reading-saved', methods=['GET'])
def latest_reading_saved():
    # reading = Reading.query.order_by(Reading.created_at.desc()).first()
    # if reading is None:
    #     # Return a 404 Not Found error with a message
    #     return jsonify({"error": "No reading found"}), 404
    # reading_dict = reading.as_dict()
    # # Convert the datetime object to a string using isoformat method
    # reading_dict["created_at"] = reading_dict["created_at"].isoformat(timespec="microseconds")
    return jsonify({})
    # return jsonify(reading_dict)


@bp.route('/get-nodes-list', methods=["GET", "POST"])
def get_nodes_list():
    for key in SYSTEM_NODES:
        if SYSTEM_NODES[key] == []:
            return None
        else:
            return g.system_nodes


@bp.before_app_request
def load_system_nodes():
    g.system_nodes = SYSTEM_NODES
