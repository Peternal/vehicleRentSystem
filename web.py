from flask import Flask, request, render_template, jsonify, json, url_for
from flaskext.mysql import MySQL
import pymysql
import json
import traceback
import datetime
from flask_bcrypt import Bcrypt
import hashlib

mysql = MySQL()
app = Flask(__name__)
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '123456'
app.config['MYSQL_DATABASE_DB'] = 'test'
app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
mysql.init_app(app)


app = Flask(__name__)

@app.route("/rent_record", methods=['GET', 'POST'])
def rent_record():
    return render_template("rent_record.html")


@app.route("/rent_record_ajax", methods=["POST", "GET"])
def rent_record_ajax():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        if request.method == 'POST':
            draw = request.form['draw']
            row = int(request.form['start'])
            rowperpage = int(request.form['length'])
            searchValue = request.form["search[value]"]
            sortColumn = request.form["columns[" + request.form["order[0][column]"] + "][name]"]
            sortColumnDirection = request.form["order[0][dir]"]
            print(draw)
            print(row)
            print(rowperpage)
            print(searchValue)
            print("sortcol: "+sortColumn)
            print("sortdir: " + sortColumnDirection)

            ## Total number of records without filtering
            cursor.execute(
                "SELECT count(*) AS allrecord "
                +"FROM ltd_rent_record "
                +"INNER JOIN ltd_wow_office ON ltd_wow_office.office_id=ltd_rent_record.pickup_office_id "
                +"INNER JOIN ltd_wow_office AS tmp ON tmp.office_id=ltd_rent_record.dropoff_office_id;")
            rsallrecord = cursor.fetchone()
            totalRecords = rsallrecord['allrecord']
            print(totalRecords)

            ## Total number of records with filtering
            likeString = "%" + searchValue + "%"
            cursor.execute(
                "SELECT count(*) AS allrecord "
                +"FROM ltd_rent_record "
                +"INNER JOIN ltd_wow_office ON ltd_wow_office.office_id=ltd_rent_record.pickup_office_id "
                +"INNER JOIN ltd_wow_office AS tmp ON tmp.office_id=ltd_rent_record.dropoff_office_id "
                +"WHERE ltd_wow_office.office_name LIKE %s OR tmp.office_name LIKE %s OR ltd_rent_record.email LIKE %s OR ltd_rent_record.vin LIKE %s;",
                (likeString, likeString, likeString, likeString))
            rsallrecord = cursor.fetchone()
            totalRecordwithFilter = rsallrecord['allrecord']
            print(totalRecordwithFilter)

            ## Fetch records
            if searchValue == '':
                cursor.execute(
                    "SELECT ltd_rent_record.record_id AS record_id, "
                    +"ltd_wow_office.office_name AS pickup_office_name, "
                    +"tmp.office_name AS dropoff_office_name, "
                    +"ltd_rent_record.pickup_date AS pickup_date, "
                    +"ltd_rent_record.dropoff_date AS dropoff_date, "
                    +"ltd_rent_record.start_meter AS start_meter, "
                    +"ltd_rent_record.end_meter AS end_meter, "
                    +"ltd_rent_record.daliy_meter_limit AS daliy_meter_limit, "
                    +"ltd_rent_record.email AS email, "
                    +"ltd_rent_record.vin AS vin "
                    +"FROM ltd_rent_record "
                    +"INNER JOIN ltd_wow_office ON ltd_wow_office.office_id=ltd_rent_record.pickup_office_id "
                    +"INNER JOIN ltd_wow_office AS tmp ON tmp.office_id=ltd_rent_record.dropoff_office_id "
                    +"ORDER BY "+sortColumn+" "+sortColumnDirection+" limit %s, %s;", (row, rowperpage))
                recordlist = cursor.fetchall()
            else:
                cursor.execute(
                    "SELECT ltd_rent_record.record_id AS record_id, "
                    +"ltd_wow_office.office_name AS pickup_office_name, "
                    +"tmp.office_name AS dropoff_office_name, "
                    +"ltd_rent_record.pickup_date AS pickup_date, "
                    +"ltd_rent_record.dropoff_date AS dropoff_date, "
                    +"ltd_rent_record.start_meter AS start_meter, "
                    +"ltd_rent_record.end_meter AS end_meter, "
                    +"ltd_rent_record.daliy_meter_limit AS daliy_meter_limit, "
                    +"ltd_rent_record.email AS email, "
                    +"ltd_rent_record.vin AS vin "
                    +"FROM ltd_rent_record "
                    +"INNER JOIN ltd_wow_office ON ltd_wow_office.office_id=ltd_rent_record.pickup_office_id "
                    +"INNER JOIN ltd_wow_office AS tmp ON tmp.office_id=ltd_rent_record.dropoff_office_id "
                    +"WHERE ltd_wow_office.office_name LIKE %s OR tmp.office_name LIKE %s OR ltd_rent_record.email LIKE %s OR ltd_rent_record.vin LIKE %s "
                    +"ORDER BY "+sortColumn+" "+sortColumnDirection+" limit %s, %s;",
                    (likeString, likeString, likeString, likeString, row, rowperpage))
                recordlist = cursor.fetchall()

            data = []
            for row in recordlist:
                DMLimit = 'Unlimited' if row['daliy_meter_limit'] == -1 else row['daliy_meter_limit']
                data.append({
                    'record_id': row['record_id'],
                    'pickup_office_name': row['pickup_office_name'],
                    'dropoff_office_name': row['dropoff_office_name'],
                    'pickup_date': row['pickup_date'].strftime("%Y/%m/%d"),
                    'dropoff_date': row['dropoff_date'].strftime("%Y/%m/%d"),
                    'start_meter': row['start_meter'],
                    'end_meter': row['end_meter'],
                    'daliy_meter_limit': DMLimit,
                    'email': row['email'],
                    'vin': row['vin']
                })

            response = {
                'draw': draw,
                'iTotalRecords': totalRecords,
                'iTotalDisplayRecords': totalRecordwithFilter,
                'aaData': data,
            }
            return jsonify(response)

    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()

@app.route("/create_rent_record", methods=['GET', 'POST'])
def create_rent_record():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT office_id, office_name FROM ltd_wow_office")
        officelist = cursor.fetchall()
        return render_template("create_rent_record.html", officelist=officelist)

    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


@app.route('/create_record_request',methods=['GET', 'POST'])
def create_record_request():
    data = request.get_data()
    json_data = json.loads(data)
    pickup_office_id = json_data.get("pickup_office_id")
    dropoff_office_id = json_data.get("dropoff_office_id")
    pickup_date = json_data.get("pickup_date")
    dropoff_date = json_data.get("dropoff_date")
    start_meter = json_data.get("start_meter")
    end_meter = json_data.get("end_meter")
    daliy_meter_limit = json_data.get("daliy_meter_limit")
    email = json_data.get("email")
    vin = json_data.get("vin")

    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    info = dict()
    info['status'] = "success"
    info['content'] = "Successfully submitted"

    try:
        cursor.execute("SELECT count(*) AS allrecord FROM ltd_customer WHERE email='"+email+"';")
        cusCount = cursor.fetchone()
        cusCount = cusCount['allrecord']
        print(cusCount)
        if (cusCount==0):
            info['status'] = "not found"
            info['content'] = "Email not found. No such customer."
            return jsonify(info)

        cursor.execute("SELECT count(*) AS allrecord FROM ltd_vehicle WHERE vin='" + vin + "';")
        vehCount = cursor.fetchone()
        vehCount = vehCount['allrecord']
        print(vehCount)
        if (vehCount==0):
            info['status'] = "not found"
            info['content'] = "VIN not found. No such vehicle."
            return jsonify(info)

        cursor.execute("INSERT INTO ltd_rent_record (pickup_office_id, dropoff_office_id, pickup_date, dropoff_date, start_meter, end_meter, daliy_meter_limit, email, vin) "
                       +"VALUES ( "+pickup_office_id+", "+dropoff_office_id+", '"+pickup_date+"', '"+dropoff_date+"', "+start_meter+", "+end_meter+", "+daliy_meter_limit+", '"+email+"', '"+vin+"');")
        conn.commit()

        return jsonify(info)


    except Exception as e:
        traceback.print_exc()
        print(e)
        conn.rollback()
        info['status'] = "error"
        info['content'] = "Insert error."
        return jsonify(info)

    finally:
        cursor.close()
        conn.close()



@app.route("/email_hint", methods=['GET', 'POST'])
def email_hint():
    data = request.get_data()
    json_data = json.loads(data)
    key = json_data.get("key")
    print(key)

    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:
        cursor.execute("SELECT email FROM ltd_customer WHERE email LIKE '%"+key+"%' LIMIT 5;")
        emaillist = cursor.fetchall()
        if (emaillist):
            code=1
        else: code=0

        info = dict()
        info['code'] = code
        info['content'] = emaillist
        return jsonify(info)

    except Exception as e:
        print(e)
        info = dict()
        info['code'] = 0
        return jsonify(info)

    finally:
        cursor.close()
        conn.close()

@app.route("/vin_hint", methods=['GET', 'POST'])
def vin_hint():
    data = request.get_data()
    json_data = json.loads(data)
    key = json_data.get("key")
    print(key)

    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:
        cursor.execute("SELECT vin FROM ltd_vehicle WHERE vin LIKE '%"+key+"%' LIMIT 5;")
        vinlist = cursor.fetchall()
        if (vinlist):
            code=1
        else: code=0

        info = dict()
        info['code'] = code
        info['content'] = vinlist
        return jsonify(info)

    except Exception as e:
        print(e)
        info = dict()
        info['code'] = 0
        return jsonify(info)

    finally:
        cursor.close()
        conn.close()



@app.route("/vehicle", methods=['GET', 'POST'])
def vehicle():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT office_id, office_name FROM ltd_wow_office")
        officelist = cursor.fetchall()
        cursor.execute("SELECT class_name FROM ltd_vehicle_class")
        classlist = cursor.fetchall()
        return render_template("vehicle.html", officelist=officelist, classlist=classlist)

    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


@app.route("/vehicle_ajax", methods=["POST", "GET"])
def vehicle_ajax():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        if request.method == 'POST':
            draw = request.form['draw']
            row = int(request.form['start'])
            rowperpage = int(request.form['length'])
            searchValue = request.form["search[value]"]
            sortColumn = request.form["columns[" + request.form["order[0][column]"] + "][name]"]
            sortColumnDirection = request.form["order[0][dir]"]
            print(draw)
            print(row)
            print(rowperpage)
            print(searchValue)
            print("sortcol: "+sortColumn)
            print("sortdir: " + sortColumnDirection)

            ## Total number of records without filtering
            cursor.execute(
                "SELECT count(*) AS allrecord "
                +"FROM ltd_vehicle "
                +"INNER JOIN ltd_wow_office ON ltd_wow_office.office_id=ltd_vehicle.office_id;")
            rsallrecord = cursor.fetchone()
            totalRecords = rsallrecord['allrecord']
            print(totalRecords)

            ## Total number of records with filtering
            likeString = "%" + searchValue + "%"
            cursor.execute(
                "SELECT count(*) AS allrecord "
                +"FROM ltd_vehicle "
                +"INNER JOIN ltd_wow_office ON ltd_wow_office.office_id=ltd_vehicle.office_id "
                +"WHERE ltd_wow_office.office_name LIKE %s OR ltd_vehicle.vin LIKE %s OR ltd_vehicle.make LIKE %s OR ltd_vehicle.model LIKE %s OR ltd_vehicle.license_plate_number LIKE %s OR ltd_vehicle.class_name LIKE %s;",
                (likeString, likeString, likeString, likeString, likeString, likeString))
            rsallrecord = cursor.fetchone()
            totalRecordwithFilter = rsallrecord['allrecord']
            print(totalRecordwithFilter)

            ## Fetch records
            if searchValue == '':
                cursor.execute(
                    "SELECT ltd_vehicle.vin AS vin, "
                    +"ltd_vehicle.make AS make, "
                    +"ltd_vehicle.model AS model, "
                    +"ltd_vehicle.year AS year, "
                    +"ltd_vehicle.license_plate_number AS license_plate_number, "
                    +"ltd_vehicle.status AS status, "
                    +"ltd_vehicle.class_name AS class_name, "
                    +"ltd_wow_office.office_name AS office_name "
                    +"FROM ltd_vehicle "
                    +"INNER JOIN ltd_wow_office ON ltd_wow_office.office_id=ltd_vehicle.office_id "
                    +"ORDER BY "+sortColumn+" "+sortColumnDirection+" limit %s, %s;", (row, rowperpage))
                recordlist = cursor.fetchall()
            else:
                cursor.execute(
                    "SELECT ltd_vehicle.vin AS vin, "
                    +"ltd_vehicle.make AS make, "
                    +"ltd_vehicle.model AS model, "
                    +"ltd_vehicle.year AS year, "
                    +"ltd_vehicle.license_plate_number AS license_plate_number, "
                    +"ltd_vehicle.status AS status, "
                    +"ltd_vehicle.class_name AS class_name, "
                    +"ltd_wow_office.office_name AS office_name "
                    +"FROM ltd_vehicle "
                    +"INNER JOIN ltd_wow_office ON ltd_wow_office.office_id=ltd_vehicle.office_id "
                    +"WHERE ltd_wow_office.office_name LIKE %s OR ltd_vehicle.vin LIKE %s OR ltd_vehicle.make LIKE %s OR ltd_vehicle.model LIKE %s OR ltd_vehicle.license_plate_number LIKE %s OR ltd_vehicle.class_name LIKE %s "
                    +"ORDER BY "+sortColumn+" "+sortColumnDirection+" limit %s, %s;",
                    (likeString, likeString, likeString, likeString, likeString, likeString, row, rowperpage))
                recordlist = cursor.fetchall()

            data = []
            for row in recordlist:
                Status = '<div class="badge badge-soft-success">Available</div>' if row['status'] == 1 else '<div class="badge badge-soft-danger">Unavailable</div>'
                data.append({
                    'vin': row['vin'],
                    'make': row['make'],
                    'model': row['model'],
                    'year': row['year'],
                    'license_plate_number': row['license_plate_number'],
                    'status': Status,
                    'class_name': row['class_name'],
                    'office_name': row['office_name']
                })

            response = {
                'draw': draw,
                'iTotalRecords': totalRecords,
                'iTotalDisplayRecords': totalRecordwithFilter,
                'aaData': data,
            }
            return jsonify(response)

    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


@app.route('/change_status_request',methods=['GET', 'POST'])
def change_status_request():
    data = request.get_data()
    json_data = json.loads(data)
    vin = json_data.get("vin")
    status = json_data.get("status")

    print(vin)
    print(status)

    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    info = dict()

    try:
        cursor.execute("SELECT status FROM ltd_vehicle WHERE vin='"+vin+"';")
        currStatus = cursor.fetchone()
        print(currStatus)
        currStatus = currStatus['status']
        print(currStatus)

        if (currStatus == status):
            newStatus = '0' if currStatus == 1 else '1'
            cursor.execute("UPDATE ltd_vehicle SET status="+newStatus+" WHERE vin='"+vin+"';")
            conn.commit()
            info['status'] = "success"
            info['content'] = "Successfully rent the vehicle" if currStatus == 1 else "Successfully return the vehicle"
            return jsonify(info)
        else :
            info['status'] = "error"
            info['content'] = "Vehicle has already been rent" if currStatus == 0 else "Vehicle has already been returned"
            return jsonify(info)


    except Exception as e:
        traceback.print_exc()
        print(e)
        conn.rollback()
        info['status'] = "error"
        info['content'] = "Update error."
        return jsonify(info)

    finally:
        cursor.close()
        conn.close()


@app.route('/add_vehicle_request',methods=['GET', 'POST'])
def add_vehicle_request():
    data = request.get_data()
    json_data = json.loads(data)
    vin = json_data.get("vin")
    make = json_data.get("make")
    model = json_data.get("model")
    year = json_data.get("year")
    license_plate_number = json_data.get("license_plate_number")
    class_name = json_data.get("class_name")
    office_id = json_data.get("office_id")

    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    info = dict()
    info['status'] = "success"
    info['content'] = "Successfully submitted"

    try:
        cursor.execute("SELECT count(*) AS allrecord FROM ltd_vehicle WHERE vin='"+vin+"';")
        vinCount = cursor.fetchone()
        vinCount = vinCount['allrecord']
        print(vinCount)
        if (vinCount!=0):
            info['status'] = "duplicate"
            info['content'] = "Duplicated VIN. Vehicle already exists."
            return jsonify(info)

        cursor.execute("SELECT count(*) AS allrecord FROM ltd_vehicle WHERE license_plate_number='" + license_plate_number + "';")
        licCount = cursor.fetchone()
        licCount = licCount['allrecord']
        print(licCount)
        if (licCount!=0):
            info['status'] = "duplicate"
            info['content'] = "Duplicated license plate number. Vehicle already exists."
            return jsonify(info)

        cursor.execute("INSERT INTO ltd_vehicle (vin, make, model, year, license_plate_number, status, class_name, office_id) "+
                       "VALUES ('"+vin+"', '"+make+"', '"+model+"', "+year+", '"+license_plate_number+"', 1, '"+class_name+"', "+office_id+");")
        conn.commit()

        return jsonify(info)


    except Exception as e:
        traceback.print_exc()
        print(e)
        conn.rollback()
        info['status'] = "error"
        info['content'] = "Insert error."
        return jsonify(info)

    finally:
        cursor.close()
        conn.close()


@app.route('/edit_vehicle_request',methods=['GET', 'POST'])
def edit_vehicle_request():
    data = request.get_data()
    json_data = json.loads(data)
    vin = json_data.get("vin")
    make = json_data.get("make")
    model = json_data.get("model")
    year = json_data.get("year")
    license_plate_number = json_data.get("license_plate_number")
    class_name = json_data.get("class_name")
    office_id = json_data.get("office_id")

    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    info = dict()
    info['status'] = "success"
    info['content'] = "Successfully submitted"

    try:
        cursor.execute("SELECT count(*) AS allrecord FROM ltd_vehicle WHERE vin<>'"+vin+"' and license_plate_number='" + license_plate_number + "';")
        licCount = cursor.fetchone()
        licCount = licCount['allrecord']
        print(licCount)
        if (licCount!=0):
            info['status'] = "duplicate"
            info['content'] = "Duplicated license plate number."
            return jsonify(info)

        cursor.execute("UPDATE ltd_vehicle SET make='"+make+"', model='"+model+"', year="+year+", license_plate_number='"+license_plate_number+
                       "', class_name='"+class_name+"', office_id="+office_id+" WHERE vin='"+vin+"';")
        conn.commit()

        return jsonify(info)


    except Exception as e:
        traceback.print_exc()
        print(e)
        conn.rollback()
        info['status'] = "error"
        info['content'] = "Update error."
        return jsonify(info)

    finally:
        cursor.close()
        conn.close()


@app.route('/delete_vehicle_request',methods=['GET', 'POST'])
def delete_vehicle_request():
    data = request.get_data()
    json_data = json.loads(data)
    vin = json_data.get("vin")

    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    info = dict()
    info['status'] = "success"
    info['content'] = "Successfully deleted"

    try:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        cursor.execute("DELETE FROM ltd_vehicle WHERE vin='"+vin+"';")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        conn.commit()

        return jsonify(info)


    except Exception as e:
        traceback.print_exc()
        print(e)
        conn.rollback()
        info['status'] = "error"
        info['content'] = "Delete error."
        return jsonify(info)

    finally:
        cursor.close()
        conn.close()



@app.route("/vehicle_class", methods=['GET', 'POST'])
def vehicle_class():
    return render_template("vehicle_class.html")




@app.route("/vehicle_class_ajax", methods=["POST", "GET"])
def vehicle_class_ajax():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        if request.method == 'POST':
            draw = request.form['draw']
            row = int(request.form['start'])
            rowperpage = int(request.form['length'])
            searchValue = request.form["search[value]"]
            sortColumn = request.form["columns[" + request.form["order[0][column]"] + "][name]"]
            sortColumnDirection = request.form["order[0][dir]"]
            print(draw)
            print(row)
            print(rowperpage)
            print(searchValue)
            print("sortcol: "+sortColumn)
            print("sortdir: " + sortColumnDirection)

            ## Total number of records without filtering
            cursor.execute(
                "SELECT count(*) AS allrecord "
                +"FROM (SELECT ltd_vehicle_class.*, IFNULL(COUNT(ltd_vehicle.class_name), 0) AS vehicle_number "
                +"FROM ltd_vehicle_class "
                +"LEFT JOIN ltd_vehicle ON ltd_vehicle.class_name=ltd_vehicle_class.class_name "
                +"GROUP BY ltd_vehicle_class.class_name) a;")
            rsallrecord = cursor.fetchone()
            totalRecords = rsallrecord['allrecord']
            print(totalRecords)

            ## Total number of records with filtering
            likeString = "%" + searchValue + "%"
            cursor.execute(
                "SELECT count(*) AS allrecord "
                +"FROM (SELECT ltd_vehicle_class.*, IFNULL(COUNT(ltd_vehicle.class_name), 0) AS vehicle_number "
                +"FROM ltd_vehicle_class "
                +"LEFT JOIN ltd_vehicle ON ltd_vehicle.class_name=ltd_vehicle_class.class_name "
                +"GROUP BY ltd_vehicle_class.class_name) a "
                +"WHERE class_name LIKE %s OR rental_rate LIKE %s OR over_millage_fee LIKE %s OR vehicle_number LIKE %s;",
                (likeString, likeString, likeString, likeString))
            rsallrecord = cursor.fetchone()
            totalRecordwithFilter = rsallrecord['allrecord']
            print(totalRecordwithFilter)

            ## Fetch records
            if searchValue == '':
                cursor.execute(
                    "SELECT * "
                    +"FROM (SELECT ltd_vehicle_class.*, IFNULL(COUNT(ltd_vehicle.class_name), 0) AS vehicle_number "
                    +"FROM ltd_vehicle_class "
                    +"LEFT JOIN ltd_vehicle ON ltd_vehicle.class_name=ltd_vehicle_class.class_name "
                    +"GROUP BY ltd_vehicle_class.class_name) a "
                    +"ORDER BY "+sortColumn+" "+sortColumnDirection+" limit %s, %s;", (row, rowperpage))
                recordlist = cursor.fetchall()
            else:
                cursor.execute(
                    "SELECT * "
                    +"FROM (SELECT ltd_vehicle_class.*, IFNULL(COUNT(ltd_vehicle.class_name), 0) AS vehicle_number "
                    +"FROM ltd_vehicle_class "
                    +"LEFT JOIN ltd_vehicle ON ltd_vehicle.class_name=ltd_vehicle_class.class_name "
                    +"GROUP BY ltd_vehicle_class.class_name) a "
                    +"WHERE class_name LIKE %s OR rental_rate LIKE %s OR over_millage_fee LIKE %s OR vehicle_number LIKE %s "
                    +"ORDER BY "+sortColumn+" "+sortColumnDirection+" limit %s, %s;",
                    (likeString, likeString, likeString, likeString, row, rowperpage))
                recordlist = cursor.fetchall()

            data = []
            for row in recordlist:
                data.append({
                    'class_name': row['class_name'],
                    'rental_rate': row['rental_rate'],
                    'over_millage_fee': row['over_millage_fee'],
                    'vehicle_number': row['vehicle_number']
                })

            response = {
                'draw': draw,
                'iTotalRecords': totalRecords,
                'iTotalDisplayRecords': totalRecordwithFilter,
                'aaData': data,
            }
            return jsonify(response)

    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()



@app.route('/add_class_request',methods=['GET', 'POST'])
def add_class_request():
    data = request.get_data()
    json_data = json.loads(data)
    class_name = json_data.get("class_name")
    rental_rate = json_data.get("rental_rate")
    over_millage_fee = json_data.get("over_millage_fee")


    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    info = dict()
    info['status'] = "success"
    info['content'] = "Successfully submitted"

    try:
        cursor.execute("SELECT count(*) AS allrecord FROM ltd_vehicle_class WHERE class_name='"+class_name+"';")
        nameCount = cursor.fetchone()
        nameCount = nameCount['allrecord']
        print(nameCount)
        if (nameCount!=0):
            info['status'] = "duplicate"
            info['content'] = "Duplicated class name."
            return jsonify(info)

        cursor.execute("INSERT INTO ltd_vehicle_class (class_name, rental_rate, over_millage_fee) "+
                       "VALUES ('"+class_name+"', "+rental_rate+", "+over_millage_fee+");")
        conn.commit()

        return jsonify(info)


    except Exception as e:
        traceback.print_exc()
        print(e)
        conn.rollback()
        info['status'] = "error"
        info['content'] = "Insert error."
        return jsonify(info)

    finally:
        cursor.close()
        conn.close()

# "/edit_class_request"
@app.route('/edit_class_request',methods=['GET', 'POST'])
def edit_class_request():
    data = request.get_data()
    json_data = json.loads(data)
    class_name = json_data.get("class_name")
    rental_rate = json_data.get("rental_rate")
    over_millage_fee = json_data.get("over_millage_fee")
    old_class_name = json_data.get("old_class_name")

    print(class_name)

    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    info = dict()
    info['status'] = "success"
    info['content'] = "Successfully submitted"

    try:
        cursor.execute("SELECT count(*) AS allrecord FROM ltd_vehicle_class WHERE class_name='" + class_name + "';")
        nameCount = cursor.fetchone()
        nameCount = nameCount['allrecord']
        print(nameCount)
        if (old_class_name!=class_name and nameCount!=0):
            info['status'] = "duplicate"
            info['content'] = "Duplicated class name."
            return jsonify(info)

        cursor.execute("UPDATE ltd_vehicle_class SET class_name='"+class_name+"' , rental_rate="+rental_rate+" , over_millage_fee="+over_millage_fee+" WHERE class_name='"+old_class_name+"';")
        conn.commit()

        return jsonify(info)


    except Exception as e:
        traceback.print_exc()
        print(e)
        conn.rollback()
        info['status'] = "error"
        info['content'] = "Update error."
        return jsonify(info)

    finally:
        cursor.close()
        conn.close()



@app.route('/delete_class_request',methods=['GET', 'POST'])
def delete_class_request():
    data = request.get_data()
    json_data = json.loads(data)
    class_name = json_data.get("class_name")

    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    info = dict()
    info['status'] = "success"
    info['content'] = "Successfully deleted"

    try:
        cursor.execute("SELECT count(*) AS allrecord FROM ltd_vehicle WHERE class_name='"+class_name+"';")
        nameCount = cursor.fetchone()
        nameCount = nameCount['allrecord']

        if(nameCount!=0):
            info['status'] = "error"
            info['content'] = "There are still "+nameCount+" vehicles in this class!"
            return jsonify(info)

        cursor.execute("DELETE FROM ltd_vehicle_class WHERE class_name='"+class_name+"';")
        conn.commit()

        return jsonify(info)


    except Exception as e:
        traceback.print_exc()
        print(e)
        conn.rollback()
        info['status'] = "error"
        info['content'] = "Delete error."
        return jsonify(info)

    finally:
        cursor.close()
        conn.close()


@app.route("/indi_coupon", methods=['GET', 'POST'])
def indi_coupon():
    return render_template("indi_coupon.html")



@app.route("/indi_coupon_ajax", methods=["POST", "GET"])
def indi_coupon_ajax():


    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        if request.method == 'POST':
            draw = request.form['draw']
            row = int(request.form['start'])
            rowperpage = int(request.form['length'])
            searchValue = request.form["search[value]"]
            sortColumn = request.form["columns[" + request.form["order[0][column]"] + "][name]"]
            sortColumnDirection = request.form["order[0][dir]"]
            print(draw)
            print(row)
            print(rowperpage)
            print(searchValue)
            print("sortcol: "+sortColumn)
            print("sortdir: " + sortColumnDirection)

            showFlag = request.form['showFlag']
            print(showFlag)

            if showFlag == 'inactive' :
                timeCheck = ' WHERE start_date > sysdate() '
                timeCheckFilter = ' AND start_date > sysdate() '
            elif showFlag == 'expired' :
                timeCheck = ' WHERE end_date < sysdate() '
                timeCheckFilter = ' AND end_date < sysdate() '
            elif showFlag == 'active' :
                timeCheck = ' WHERE (end_date >= sysdate() AND start_date <= sysdate()) '
                timeCheckFilter = ' AND (end_date >= sysdate() AND start_date <= sysdate()) '
            else :
                timeCheck = ''
                timeCheckFilter = ''

            ## Total number of records without filtering
            cursor.execute("SELECT count(*) AS allrecord FROM ltd_indi_coupon "+timeCheck+" ;")
            rsallrecord = cursor.fetchone()
            totalRecords = rsallrecord['allrecord']
            print(totalRecords)

            ## Total number of records with filtering
            likeString = "%" + searchValue + "%"
            cursor.execute(
                "SELECT count(*) AS allrecord FROM ltd_indi_coupon "
                +"WHERE indi_coupon_id LIKE %s OR indi_discount_rate LIKE %s OR start_date LIKE %s OR end_date LIKE %s OR license_id LIKE %s "+timeCheckFilter+" ;",
                (likeString, likeString, likeString, likeString, likeString))
            rsallrecord = cursor.fetchone()
            totalRecordwithFilter = rsallrecord['allrecord']
            print(totalRecordwithFilter)

            ## Fetch records
            if searchValue == '':
                cursor.execute(
                    "SELECT * FROM ltd_indi_coupon "+timeCheck
                    +"ORDER BY "+sortColumn+" "+sortColumnDirection+" limit %s, %s;", (row, rowperpage))
                recordlist = cursor.fetchall()
            else:
                cursor.execute(
                    "SELECT * FROM ltd_indi_coupon "
                    +"WHERE indi_coupon_id LIKE %s OR indi_discount_rate LIKE %s OR start_date LIKE %s OR end_date LIKE %s OR license_id LIKE %s "+timeCheckFilter
                    +"ORDER BY "+sortColumn+" "+sortColumnDirection+" limit %s, %s;",
                    (likeString, likeString, likeString, likeString, likeString, row, rowperpage))
                recordlist = cursor.fetchall()

            data = []
            for row in recordlist:
                if datetime.datetime.now() < row['start_date'] :
                    status = '<div class="badge badge-soft-warning">Inactive</div>'
                elif datetime.datetime.now() > row['end_date'] :
                    status = '<div class="badge badge-soft-danger">Expired</div>'
                else :
                    status = '<div class="badge badge-soft-success">Active</div>'
                data.append({
                    'indi_coupon_id': row['indi_coupon_id'],
                    'indi_discount_rate': row['indi_discount_rate'],
                    'start_date': row['start_date'].strftime("%Y/%m/%d"),
                    'end_date': row['end_date'].strftime("%Y/%m/%d"),
                    'license_id': row['license_id'],
                    'status': status
                })

            response = {
                'draw': draw,
                'iTotalRecords': totalRecords,
                'iTotalDisplayRecords': totalRecordwithFilter,
                'aaData': data,
            }
            return jsonify(response)

    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


@app.route("/new_license_hint", methods=['GET', 'POST'])
def new_license_hint():
    data = request.get_data()
    json_data = json.loads(data)
    key = json_data.get("key")
    print(key)

    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:
        cursor.execute("SELECT license_id FROM ltd_indi_cus WHERE license_id LIKE '%"+key+"%' LIMIT 5;")
        liclist = cursor.fetchall()
        if (liclist):
            code=1
        else: code=0

        info = dict()
        info['code'] = code
        info['content'] = liclist
        return jsonify(info)

    except Exception as e:
        print(e)
        info = dict()
        info['code'] = 0
        return jsonify(info)

    finally:
        cursor.close()
        conn.close()

@app.route('/add_indi_coupon_request',methods=['GET', 'POST'])
def add_indi_coupon_request():
    data = request.get_data()
    json_data = json.loads(data)
    indi_coupon_id = json_data.get("indi_coupon_id")
    indi_discount_rate = json_data.get("indi_discount_rate")
    start_date = json_data.get("start_date")
    end_date = json_data.get("end_date")
    license_id = json_data.get("license_id")

    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    info = dict()
    info['status'] = "success"
    info['content'] = "Successfully submitted"

    try:
        cursor.execute("SELECT count(*) AS allrecord FROM ltd_indi_coupon WHERE indi_coupon_id='"+indi_coupon_id+"';")
        idCount = cursor.fetchone()
        idCount = idCount['allrecord']
        print(idCount)
        if (idCount!=0):
            info['status'] = "duplicate"
            info['content'] = "Duplicated individual coupon ID. Individual coupon already exists."
            return jsonify(info)

        cursor.execute("SELECT count(*) AS allrecord FROM ltd_indi_cus WHERE license_id='" + license_id + "';")
        cusCount = cursor.fetchone()
        cusCount = cusCount['allrecord']
        print(cusCount)
        if (cusCount == 0):
            info['status'] = "not found"
            info['content'] = "License ID not found. No such customer."
            return jsonify(info)


        cursor.execute("INSERT INTO ltd_indi_coupon (indi_coupon_id, indi_discount_rate, start_date, end_date, license_id) "+
                       "VALUES ("+indi_coupon_id+", "+indi_discount_rate+", '"+start_date+"', '"+end_date+"', '"+license_id+"');")
        conn.commit()

        return jsonify(info)


    except Exception as e:
        traceback.print_exc()
        print(e)
        conn.rollback()
        info['status'] = "error"
        info['content'] = "Insert error."
        return jsonify(info)

    finally:
        cursor.close()
        conn.close()



@app.route('/edit_indi_coupon_request',methods=['GET', 'POST'])
def edit_indi_coupon_request():
    data = request.get_data()
    json_data = json.loads(data)
    indi_coupon_id = json_data.get("indi_coupon_id")
    indi_discount_rate = json_data.get("indi_discount_rate")
    start_date = json_data.get("start_date")
    end_date = json_data.get("end_date")


    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    info = dict()
    info['status'] = "success"
    info['content'] = "Successfully submitted"

    try:
        cursor.execute("SELECT count(*) AS allrecord FROM ltd_indi_coupon WHERE indi_coupon_id="+str(indi_coupon_id)+" ;")
        licCount = cursor.fetchone()
        licCount = licCount['allrecord']
        print(licCount)
        if (licCount==0):
            info['status'] = "error"
            info['content'] = "Coupon ID not found."
            return jsonify(info)

        cursor.execute("UPDATE ltd_indi_coupon SET indi_discount_rate="+indi_discount_rate+", start_date='"+start_date+"', end_date='"+end_date+"' WHERE indi_coupon_id="+str(indi_coupon_id)+" ;")
        conn.commit()

        return jsonify(info)


    except Exception as e:
        traceback.print_exc()
        print(e)
        conn.rollback()
        info['status'] = "error"
        info['content'] = "Update error."
        return jsonify(info)

    finally:
        cursor.close()
        conn.close()



@app.route('/delete_indi_coupon_request',methods=['GET', 'POST'])
def delete_indi_coupon_request():
    data = request.get_data()
    json_data = json.loads(data)
    indi_coupon_id = json_data.get("indi_coupon_id")

    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    info = dict()
    info['status'] = "success"
    info['content'] = "Successfully deleted"

    try:
        cursor.execute("DELETE FROM ltd_indi_coupon WHERE indi_coupon_id="+str(indi_coupon_id)+";")
        conn.commit()

        return jsonify(info)


    except Exception as e:
        traceback.print_exc()
        print(e)
        conn.rollback()
        info['status'] = "error"
        info['content'] = "Delete error."
        return jsonify(info)

    finally:
        cursor.close()
        conn.close()

@app.route("/corp_coupon", methods=['GET', 'POST'])
def corp_coupon():
    return render_template("corp_coupon.html")


@app.route("/corp_coupon_ajax", methods=["POST", "GET"])
def corp_coupon_ajax():

    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        if request.method == 'POST':
            draw = request.form['draw']
            row = int(request.form['start'])
            rowperpage = int(request.form['length'])
            searchValue = request.form["search[value]"]
            sortColumn = request.form["columns[" + request.form["order[0][column]"] + "][name]"]
            sortColumnDirection = request.form["order[0][dir]"]
            print(draw)
            print(row)
            print(rowperpage)
            print(searchValue)
            print("sortcol: "+sortColumn)
            print("sortdir: " + sortColumnDirection)

            ## Total number of records without filtering
            cursor.execute("SELECT count(*) AS allrecord FROM "
                           +"(SELECT ltd_corp_coupon.*, GROUP_CONCAT(DISTINCT corp_name SEPARATOR '<br/>') corp_name "
                           +"FROM ltd_corp_coupon "
                           +"LEFT JOIN ltd_corp_cus ON ltd_corp_cus.corp_coupon_id=ltd_corp_coupon.corp_coupon_id "
                           +"GROUP BY ltd_corp_coupon.corp_coupon_id) a;")
            rsallrecord = cursor.fetchone()
            totalRecords = rsallrecord['allrecord']
            print(totalRecords)

            ## Total number of records with filtering
            likeString = "%" + searchValue + "%"
            cursor.execute(
                "SELECT count(*) AS allrecord FROM "
                +"(SELECT ltd_corp_coupon.*, GROUP_CONCAT(DISTINCT corp_name SEPARATOR '<br/>') corp_name "
                +"FROM ltd_corp_coupon "
                +"LEFT JOIN ltd_corp_cus ON ltd_corp_cus.corp_coupon_id=ltd_corp_coupon.corp_coupon_id "
                +"GROUP BY ltd_corp_coupon.corp_coupon_id) a "
                +"WHERE a.c_discount_rate LIKE %s OR a.corp_coupon_id LIKE %s OR a.corp_name LIKE %s ;",
                (likeString, likeString, likeString))
            rsallrecord = cursor.fetchone()
            totalRecordwithFilter = rsallrecord['allrecord']
            print(totalRecordwithFilter)

            ## Fetch records
            if searchValue == '':
                cursor.execute(
                    "SELECT ltd_corp_coupon.*, GROUP_CONCAT(DISTINCT corp_name SEPARATOR '<br/>') corp_name "
                    +"FROM ltd_corp_coupon "
                    +"LEFT JOIN ltd_corp_cus ON ltd_corp_cus.corp_coupon_id=ltd_corp_coupon.corp_coupon_id "
                    +"GROUP BY ltd_corp_coupon.corp_coupon_id "
                    +"ORDER BY "+sortColumn+" "+sortColumnDirection+" limit %s, %s;", (row, rowperpage))
                recordlist = cursor.fetchall()
            else:
                cursor.execute(
                    "SELECT ltd_corp_coupon. *, GROUP_CONCAT(DISTINCT corp_name SEPARATOR '<br/>') corp_name "
                    +"FROM ltd_corp_coupon "
                    +"LEFT JOIN ltd_corp_cus ON ltd_corp_cus.corp_coupon_id=ltd_corp_coupon.corp_coupon_id "
                    +"WHERE ltd_corp_coupon.c_discount_rate LIKE %s OR ltd_corp_coupon.corp_coupon_id LIKE %s OR corp_name LIKE %s "
                    +"GROUP BY ltd_corp_coupon.corp_coupon_id "
                    +"ORDER BY "+sortColumn+" "+sortColumnDirection+" limit %s, %s;",
                    (likeString, likeString, likeString, row, rowperpage))
                recordlist = cursor.fetchall()

            data = []
            for row in recordlist:
                corp_name = row['corp_name'] if row['corp_name'] else ''
                data.append({
                    'corp_coupon_id': row['corp_coupon_id'],
                    'c_discount_rate': row['c_discount_rate'],
                    'corp_name': corp_name
                })

            response = {
                'draw': draw,
                'iTotalRecords': totalRecords,
                'iTotalDisplayRecords': totalRecordwithFilter,
                'aaData': data,
            }
            return jsonify(response)

    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


@app.route('/add_corp_coupon_request',methods=['GET', 'POST'])
def add_corp_coupon_request():
    data = request.get_data()
    json_data = json.loads(data)
    corp_coupon_id = json_data.get("corp_coupon_id")
    c_discount_rate = json_data.get("c_discount_rate")

    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    info = dict()
    info['status'] = "success"
    info['content'] = "Successfully submitted"

    try:
        cursor.execute("SELECT count(*) AS allrecord FROM ltd_corp_coupon WHERE corp_coupon_id='"+corp_coupon_id+"';")
        cpCount = cursor.fetchone()
        cpCount = cpCount['allrecord']
        print(cpCount)
        if (cpCount!=0):
            info['status'] = "duplicate"
            info['content'] = "Duplicated corporation coupon ID. Corporation coupon already exists."
            return jsonify(info)


        cursor.execute("INSERT INTO ltd_corp_coupon (corp_coupon_id, c_discount_rate) "+
                       "VALUES ("+corp_coupon_id+", "+c_discount_rate+");")
        conn.commit()

        return jsonify(info)


    except Exception as e:
        traceback.print_exc()
        print(e)
        conn.rollback()
        info['status'] = "error"
        info['content'] = "Insert error."
        return jsonify(info)

    finally:
        cursor.close()
        conn.close()


@app.route('/edit_corp_coupon_request',methods=['GET', 'POST'])
def edit_corp_coupon_request():
    data = request.get_data()
    json_data = json.loads(data)
    corp_coupon_id = json_data.get("corp_coupon_id")
    c_discount_rate = json_data.get("c_discount_rate")


    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    info = dict()
    info['status'] = "success"
    info['content'] = "Successfully submitted"

    try:
        cursor.execute("SELECT count(*) AS allrecord FROM ltd_corp_coupon WHERE corp_coupon_id="+str(corp_coupon_id)+" ;")
        cpCount = cursor.fetchone()
        cpCount = cpCount['allrecord']
        print(cpCount)
        if (cpCount==0):
            info['status'] = "error"
            info['content'] = "Coupon ID not found."
            return jsonify(info)

        cursor.execute("UPDATE ltd_corp_coupon SET c_discount_rate="+c_discount_rate+" WHERE corp_coupon_id="+str(corp_coupon_id)+" ;")
        conn.commit()

        return jsonify(info)


    except Exception as e:
        traceback.print_exc()
        print(e)
        conn.rollback()
        info['status'] = "error"
        info['content'] = "Update error."
        return jsonify(info)

    finally:
        cursor.close()
        conn.close()


@app.route('/delete_corp_coupon_request',methods=['GET', 'POST'])
def delete_corp_coupon_request():
    data = request.get_data()
    json_data = json.loads(data)
    corp_coupon_id = json_data.get("corp_coupon_id")

    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    info = dict()
    info['status'] = "success"
    info['content'] = "Successfully deleted"

    try:
        cursor.execute("DELETE FROM ltd_corp_coupon WHERE corp_coupon_id="+str(corp_coupon_id)+";")
        conn.commit()

        return jsonify(info)


    except Exception as e:
        traceback.print_exc()
        print(e)
        conn.rollback()
        info['status'] = "error"
        info['content'] = "Delete error."
        return jsonify(info)

    finally:
        cursor.close()
        conn.close()


GlobalEmail = "solujicifrou-1777@yopmail.com"



@app.route("/cus_invoice", methods=['GET', 'POST'])
def cus_invoices():
    return render_template("cus_invoice.html")





@app.route("/invoice_ajax", methods=["POST", "GET"])
def invoice_ajax():


    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        if request.method == 'POST':
            draw = request.form['draw']
            row = int(request.form['start'])
            rowperpage = int(request.form['length'])
            searchValue = request.form["search[value]"]
            sortColumn = request.form["columns[" + request.form["order[0][column]"] + "][name]"]
            sortColumnDirection = request.form["order[0][dir]"]
            print(draw)
            print(row)
            print(rowperpage)
            print(searchValue)
            print("sortcol: "+sortColumn)
            print("sortdir: " + sortColumnDirection)

            showFlag = request.form['showFlag']
            print(showFlag)

            if showFlag == 'unpaid' :
                payCheck = " WHERE paid='no' "
                payCheckFilter = " AND paid='no' "
            elif showFlag == 'paid' :
                payCheck = " WHERE paid='yes' "
                payCheckFilter = " AND paid='yes' "
            else :
                payCheck = ''
                payCheckFilter = ''

            ## Total number of records without filtering
            cursor.execute(
                "SELECT count(*) AS allrecord FROM "
                +"(SELECT ltd_invoice.* , IF(ltd_invoice.invoice_id IN (SELECT invoice_id FROM ltd_payment), 'yes','no') paid "
                +"FROM ltd_invoice, "
                +"(SELECT record_id FROM ltd_rent_record WHERE email='"+GlobalEmail+"') a "
                +"WHERE ltd_invoice.record_id = a.record_id ) t "+payCheck+" ;"
            )
            rsallrecord = cursor.fetchone()
            totalRecords = rsallrecord['allrecord']
            print(totalRecords)

            ## Total number of records with filtering
            likeString = "%" + searchValue + "%"
            cursor.execute(
                "SELECT count(*) AS allrecord FROM "
                +"(SELECT ltd_invoice.* , IF(ltd_invoice.invoice_id IN (SELECT invoice_id FROM ltd_payment), 'yes','no') paid "
                +"FROM ltd_invoice, "
                +"(SELECT record_id FROM ltd_rent_record WHERE email='"+GlobalEmail+"') a "
                +"WHERE ltd_invoice.record_id = a.record_id ) t "
                +"WHERE invoice_id LIKE %s OR date LIKE %s OR amount LIKE %s OR record_id LIKE %s OR paid LIKE %s "+payCheckFilter+" ;",
                (likeString, likeString, likeString, likeString, likeString))
            rsallrecord = cursor.fetchone()
            totalRecordwithFilter = rsallrecord['allrecord']
            print(totalRecordwithFilter)

            ## Fetch records
            if searchValue == '':
                cursor.execute(
                    "SELECT * FROM "
                    +"(SELECT ltd_invoice.* , IF(ltd_invoice.invoice_id IN (SELECT invoice_id FROM ltd_payment), 'yes','no') paid "
                    +"FROM ltd_invoice, "
                    +"(SELECT record_id FROM ltd_rent_record WHERE email='"+GlobalEmail+"') a "
                    +"WHERE ltd_invoice.record_id = a.record_id ) t "+payCheck
                    +"ORDER BY "+sortColumn+" "+sortColumnDirection+" limit %s, %s;", (row, rowperpage))
                recordlist = cursor.fetchall()
            else:
                cursor.execute(
                    "SELECT * FROM "
                    +"(SELECT ltd_invoice.* , IF(ltd_invoice.invoice_id IN (SELECT invoice_id FROM ltd_payment), 'yes','no') paid "
                    +"FROM ltd_invoice, "
                    +"(SELECT record_id FROM ltd_rent_record WHERE email='"+GlobalEmail+"') a "
                    +"WHERE ltd_invoice.record_id = a.record_id ) t "
                    +"WHERE invoice_id LIKE %s OR date LIKE %s OR amount LIKE %s OR record_id LIKE %s OR paid LIKE %s "+payCheckFilter
                    +"ORDER BY "+sortColumn+" "+sortColumnDirection+" limit %s, %s;",
                    (likeString, likeString, likeString, likeString, likeString, row, rowperpage))
                recordlist = cursor.fetchall()

            data = []
            for row in recordlist:
                data.append({
                    'invoice_id': row['invoice_id'],
                    'date': row['date'].strftime("%Y/%m/%d"),
                    'amount': row['amount'],
                    'record_id': row['record_id'],
                    'paid': row['paid']
                })

            response = {
                'draw': draw,
                'iTotalRecords': totalRecords,
                'iTotalDisplayRecords': totalRecordwithFilter,
                'aaData': data,
            }
            return jsonify(response)

    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


@app.route('/invoice_pay_request',methods=['GET', 'POST'])
def invoice_pay_request():
    data = request.get_data()
    json_data = json.loads(data)
    invoice_id = str(json_data.get("invoice_id"))
    payment_type = json_data.get("payment_type")
    card_no = json_data.get("card_no")

    payment_status = "approved"

    payment_date = datetime.datetime.now().strftime('%Y-%m-%d')

    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    info = dict()
    info['status'] = "success"
    info['content'] = "Successfully paid"

    try:
        cursor.execute("SELECT count(*) AS allrecord FROM ltd_payment WHERE invoice_id=" + invoice_id + ";")
        idCount = cursor.fetchone()
        idCount = idCount['allrecord']
        print(idCount)
        if (idCount != 0):
            info['status'] = "duplicate"
            info['content'] = "Duplicated invoice ID. Invoice has already been paid."
            return jsonify(info)

        cursor.execute("SELECT count(*) AS allrecord FROM ltd_invoice WHERE invoice_id=" + invoice_id + ";")
        invCount = cursor.fetchone()
        invCount = invCount['allrecord']
        print(invCount)
        if (invCount == 0):
            info['status'] = "not found"
            info['content'] = "Invoice ID not found. No such invoice."
            return jsonify(info)

        cursor.execute("INSERT INTO ltd_payment ( payment_date, payment_status, payment_type, card_no, invoice_id) VALUES "+
                       "('"+payment_date+"', '"+payment_status+"', '"+payment_type+"', '"+card_no+"', "+invoice_id+");")
        conn.commit()

        return jsonify(info)


    except Exception as e:
        traceback.print_exc()
        print(e)
        conn.rollback()
        info['status'] = "error"
        info['content'] = "Insert error."
        return jsonify(info)

    finally:
        cursor.close()
        conn.close()

@app.route("/cus_payment", methods=['GET', 'POST'])
def cus_payment():
    return render_template("cus_payment.html")


@app.route("/payment_ajax", methods=["POST", "GET"])
def payment_ajax():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        if request.method == 'POST':
            draw = request.form['draw']
            row = int(request.form['start'])
            rowperpage = int(request.form['length'])
            searchValue = request.form["search[value]"]
            sortColumn = request.form["columns[" + request.form["order[0][column]"] + "][name]"]
            sortColumnDirection = request.form["order[0][dir]"]
            print(draw)
            print(row)
            print(rowperpage)
            print(searchValue)
            print("sortcol: "+sortColumn)
            print("sortdir: " + sortColumnDirection)

            ## Total number of records without filtering
            cursor.execute(
                "SELECT count(*) AS allrecord FROM "
                +"(SELECT ltd_payment.* FROM ltd_payment, "
                +"(SELECT ltd_invoice.invoice_id "
                +"FROM ltd_invoice, "
                +"(SELECT record_id FROM ltd_rent_record WHERE email='solujicifrou-1777@yopmail.com') a "
                +"WHERE ltd_invoice.record_id = a.record_id) b "
                +"WHERE ltd_payment.invoice_id = b.invoice_id) t;")
            rsallrecord = cursor.fetchone()
            totalRecords = rsallrecord['allrecord']
            print(totalRecords)

            ## Total number of records with filtering
            likeString = "%" + searchValue + "%"
            cursor.execute(
                "SELECT count(*) AS allrecord FROM "
                +"(SELECT ltd_payment.* FROM ltd_payment, "
                +"(SELECT ltd_invoice.invoice_id "
                +"FROM ltd_invoice, "
                +"(SELECT record_id FROM ltd_rent_record WHERE email='solujicifrou-1777@yopmail.com') a "
                +"WHERE ltd_invoice.record_id = a.record_id) b "
                +"WHERE ltd_payment.invoice_id = b.invoice_id) t "
                +"WHERE payment_id LIKE %s OR payment_date LIKE %s OR payment_status LIKE %s OR payment_type LIKE %s OR card_no LIKE %s OR invoice_id LIKE %s;",
                (likeString, likeString, likeString, likeString, likeString, likeString))
            rsallrecord = cursor.fetchone()
            totalRecordwithFilter = rsallrecord['allrecord']
            print(totalRecordwithFilter)

            ## Fetch records
            if searchValue == '':
                cursor.execute(
                    "SELECT * FROM "
                    +"(SELECT ltd_payment.* FROM ltd_payment, "
                    +"(SELECT ltd_invoice.invoice_id "
                    +"FROM ltd_invoice, "
                    +"(SELECT record_id FROM ltd_rent_record WHERE email='solujicifrou-1777@yopmail.com') a "
                    +"WHERE ltd_invoice.record_id = a.record_id) b "
                    +"WHERE ltd_payment.invoice_id = b.invoice_id) t "
                    +"ORDER BY "+sortColumn+" "+sortColumnDirection+" limit %s, %s;", (row, rowperpage))
                recordlist = cursor.fetchall()
            else:
                cursor.execute(
                    "SELECT * FROM "
                    +"(SELECT ltd_payment.* FROM ltd_payment, "
                    +"(SELECT ltd_invoice.invoice_id "
                    +"FROM ltd_invoice, "
                    +"(SELECT record_id FROM ltd_rent_record WHERE email='solujicifrou-1777@yopmail.com') a "
                    +"WHERE ltd_invoice.record_id = a.record_id) b "
                    +"WHERE ltd_payment.invoice_id = b.invoice_id) t "
                    +"WHERE payment_id LIKE %s OR payment_date LIKE %s OR payment_status LIKE %s OR payment_type LIKE %s OR card_no LIKE %s OR invoice_id LIKE %s "
                    +"ORDER BY "+sortColumn+" "+sortColumnDirection+" limit %s, %s;",
                    (likeString, likeString, likeString, likeString, likeString, likeString, row, rowperpage))
                recordlist = cursor.fetchall()

            data = []
            for row in recordlist:
                data.append({
                    'payment_id': row['payment_id'],
                    'payment_date': row['payment_date'].strftime("%Y/%m/%d"),
                    'payment_status': row['payment_status'],
                    'payment_type': row['payment_type'],
                    'card_no': row['card_no'],
                    'invoice_id': row['invoice_id']
                })

            response = {
                'draw': draw,
                'iTotalRecords': totalRecords,
                'iTotalDisplayRecords': totalRecordwithFilter,
                'aaData': data,
            }
            return jsonify(response)

    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    app.run()

