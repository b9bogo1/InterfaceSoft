from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify, make_response
)
import pdfkit
from datetime import datetime, timedelta
import requests
import smtplib
from email.message import EmailMessage
from InterfaceSoft.auth import login_required
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
@login_required
def index():
    # Render an HTML template that displays the readings list
    return render_template('reading/index.html')


@bp.route('/pdf')
def html_to_pdf():
    # filter the Reading table by the created_at value in the last 24 hours
    readings = Reading.query.filter(Reading.created_at >= datetime.now() - timedelta(hours=24)).all()
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


@bp.route('/send-email', methods=["POST"])
def send_email():
    user = request.json  # or data = request.get_json()
    receiver = user['email']
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
