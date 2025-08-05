from imutils.video import VideoStream
import imutils
import cv2
import pytesseract
from PIL import Image
import re
import pymysql
import datetime
from datetime import datetime as dt
import time
from PIL import ImageFile
import LIGHT_SOUND as alarm
import easyocr
reader = easyocr.Reader(['en'])

ImageFile.LOAD_TRUNCATED_IMAGES = True


def Main(CAMARA_IP, DEFAULT_IMAGE_PATH, IMAGE_FOUND_PATH, IMAGE_FOUND_PATH_EXTENSION, IMAGE_NOT_FOUND_PATH,
         TEXT_FILE_PATH, TITLE_NAME, CAM_ID):
    while True:

        try:
            weights = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512]

            def getSparcsn4Connection():
                """Establishes a connection to the sparcsn4 database."""
                conn = pymysql.connect(host='127.0.0.1',
                                       user='root',
                                       password='root',
                                       db='sparcsn4',
                                       charset='utf8mb4',
                                       cursorclass=pymysql.cursors.DictCursor)
                return conn

            def getCtmsmisConnection():
                """Establishes a connection to the ctmsmis database."""
                conn = pymysql.connect(host='127.0.0.1',
                                       user='root',
                                       password='root',
                                       db='ctmsmis',
                                       charset='utf8mb4',
                                       cursorclass=pymysql.cursors.DictCursor)
                return conn


            def logWrite(logText):
                Today = dt.now().strftime('%Y-%m-%d %H:%M:%S')
                # print(Today + "    " + "LOG FILE INSIDE")
                text_file = open(TEXT_FILE_PATH, "a")
                text_file.write("{0} | {1} \n".format(Today, logText))
                text_file.close()

            def getContainerLastDegit(containerNumber):
                chcksum = 0
                aN = 0
                containerFinal = ""

                for c in containerNumber:
                    s1 = containerNumber[aN: aN + 1]

                    if aN < 4:
                        chcksum = chcksum + getDegitWeight(s1) * weights[aN]

                    else:
                        chcksum = chcksum + int(s1) * weights[aN]

                    aN = aN + 1

                containerFinal = containerNumber + str((0 if (chcksum % 11 == 10) else (chcksum % 11)))

                return str(containerFinal)

            def getDegitWeight(contValue):
                j = 0
                s = contValue.strip()
                if s == "A":
                    j = 10
                elif s == "B":
                    j = 12
                elif s == "C":
                    j = 13
                elif s == "D":
                    j = 14
                elif s == "E":
                    j = 15
                elif s == "F":
                    j = 16
                elif s == "G":
                    j = 17
                elif s == "H":
                    j = 18
                elif s == "I":
                    j = 19
                elif s == "J":
                    j = 20
                elif s == "K":
                    j = 21
                elif s == "L":
                    j = 23
                elif s == "M":
                    j = 24
                elif s == "N":
                    j = 25
                elif s == "O":
                    j = 26
                elif s == "P":
                    j = 27
                elif s == "Q":
                    j = 28
                elif s == "R":
                    j = 29
                elif s == "S":
                    j = 30
                elif s == "T":
                    j = 31
                elif s == "U":
                    j = 32
                elif s == "V":
                    j = 34
                elif s == "W":
                    j = 35
                elif s == "X":
                    j = 36
                elif s == "Y":
                    j = 37
                elif s == "Z":
                    j = 38

                return int(j)

            def get_string(img_path):
                img = cv2.imread(img_path)

                # Perform OCR
                results = reader.readtext(img)

                # Visualize results
                for (bbox, text, prob) in results:
                    (top_left, top_right, bottom_right, bottom_left) = bbox
                    top_left = tuple(map(int, top_left))
                    bottom_right = tuple(map(int, bottom_right))

                    # Draw bounding box
                    cv2.rectangle(img, top_left, bottom_right, (0, 255, 0), 2)

                    # Put text
                    cv2.putText(img, text, (top_left[0], top_left[1] - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                for result in results:
                    print(f"Text: {result[1]}, Confidence: {result[2]:.2f}")

            def contInsertStatus(contId, todayDateTime, dlvSt, CAM_ID, track_by):
                conn = getCtmsmisConnection()
                curInsert = conn.cursor()
                sql_insert_query = """INSERT INTO ctmsmis.mis_ocr_cont_track(cont_number,entry_dt_time,legal_delivery_st,cam,track_by) VALUES(%s,%s,%s,%s,%s)"""
                insert_tuple = (contId, todayDateTime, dlvSt, CAM_ID, track_by)
                curInsert.execute(sql_insert_query, insert_tuple)
                conn.commit()
                curInsert.close()
                conn.close()

            def checkConatinerAlreadyInserted(unit_gkey):
                sql = "SELECT unit_gkey,legal_delivery_st FROM ctmsmis.mis_ocr_info WHERE unit_gkey = '" + unit_gkey + "'"
                conn = getCtmsmisConnection()
                curAssign = conn.cursor()
                curAssign.execute(sql)
                statusresult = 0

                for rowAssign in curAssign:
                    legalStatuss = rowAssign["legal_delivery_st"]
                    if int(legalStatuss) == 1:
                        statusresult = 1
                    else:
                        statusresult = 2

                curAssign.close()
                conn.close()
                return int(statusresult)

            def deleteContinerFromTempTable(contId):
                print("deleted")
                conn = getCtmsmisConnection()
                curDelete = conn.cursor()
                sql_insert_query = """DELETE FROM ctmsmis.mis_ocr_temp_info WHERE ctmsmis.mis_ocr_temp_info.cont_no = %s"""
                cotnumber = str(contId)
                curDelete.execute(sql_insert_query,cotnumber)
                conn.commit()
                # logWrite(fCont)
                curDelete.close()
                conn.close()

            def containerReplace(unit_gkey, contId, contType, assignmentType, assignementDt, destination, dlvSt,
                                 CnFName,
                                 CAM_ID,track_by):

                todayDateTime = datetime.datetime.today().strftime("%Y-%m-%d, %H:%M:%S")
                todayDate = datetime.datetime.today().strftime("%Y-%m-%d")

                iscontainerInserted = checkConatinerAlreadyInserted(str(unit_gkey))

                print(iscontainerInserted)

                if iscontainerInserted == 0:
                    isfaulty = 0
                    if dlvSt != 1:
                        isfaulty = 1

                    conn = getCtmsmisConnection()
                    curInsert = conn.cursor()
                    sql_insert_query = """INSERT INTO ctmsmis.mis_ocr_info(unit_gkey,cont_number,freight_kind,assign_type,assign_dt,off_dock_code,off_dock_name,entry_dt,entry_dt_time,legal_delivery_st,cf_name,cam,is_faulty,is_faulty_dt_time) VALUES(%s,%s, %s, %s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s)"""
                    insert_tuple = (
                        unit_gkey, contId, contType, assignmentType, assignementDt, destination, '', todayDate,
                        todayDateTime,
                        dlvSt, CnFName, CAM_ID, isfaulty, todayDateTime)

                    curInsert.execute(sql_insert_query, insert_tuple)
                    conn.commit()
                    # logWrite(fCont)
                    curInsert.close()
                    conn.close()
                    if dlvSt == 1:
                        deleteContinerFromTempTable(contId)

                elif iscontainerInserted == 2:
                    if dlvSt == 1:
                        conn = getCtmsmisConnection()
                        curInsert = conn.cursor()
                        sql_insert_query = "UPDATE ctmsmis.mis_ocr_info SET legal_delivery_st = '" + str(
                            dlvSt) + "',is_re_enter = '" + str(1) + "',entry_dt_time =  '" + todayDateTime + "' WHERE unit_gkey = '" + str(unit_gkey) + "'"
                        curInsert.execute(sql_insert_query)
                        conn.commit()
                        # logWrite(fCont)
                        curInsert.close()
                        conn.close()

                        deleteContinerFromTempTable(contId)

                contInsertStatus(contId, todayDateTime, dlvSt, CAM_ID, track_by)

            def getContainerProcess(fCont, frame2,track_by):

                IMG_PATH = "%s%s%s" % (IMAGE_FOUND_PATH, fCont, IMAGE_FOUND_PATH_EXTENSION)
                cv2.imwrite(IMG_PATH, frame2)

                Today = dt.now().strftime('%Y-%m-%d %H:%M:%S')
                print(Today + "    FINAL CONT NUMBER:=  " + Today)

                contId = ""
                contType = ""
                assignmentCode = ""
                assignmentType = ""
                assignementDt = ""
                destination = ""
                CnFName = ""
                gate_id = ""
                unit_gkey = 0

                sql = "SELECT unit_gkey,cont_no AS id,cont_status AS freight_kind,IFNULL(mfdch_value, '') AS mfdch_value, IFNULL(mfdch_desc, '') AS mfdch_desc,CAST(IFNULL(DATE(assignment_dt), '') AS CHAR) AS flex_date01, IFNULL(destination, '') AS destination,IFNULL(cf_name,'') AS CnFName,gate_id FROM ctmsmis.mis_ocr_temp_info WHERE cont_no = '" + fCont + "' ORDER BY unit_gkey DESC LIMIT 1"
                print(Today + "    QUERY FINAL := " + sql)
                conn = getCtmsmisConnection()
                curAssign = conn.cursor()
                curAssign.execute(sql)
                for rowAssign in curAssign:
                    unit_gkey = rowAssign["unit_gkey"]
                    contId = rowAssign["id"]
                    contType = rowAssign["freight_kind"]
                    assignmentCode = rowAssign["mfdch_value"]
                    assignmentType = rowAssign["mfdch_desc"]
                    assignementDt = rowAssign["flex_date01"]
                    destination = rowAssign["destination"]
                    CnFName = rowAssign["CnFName"]
                    gate_id = rowAssign["gate_id"]

                curAssign.close()
                conn.close()
                print(Today + "    UNIT GKEY : " + repr(unit_gkey))
                CheckStrEIR = "SELECT doctype_gkey FROM sparcsn4.road_truck_transactions rtt INNER JOIN sparcsn4.road_documents rd ON rd.tran_gkey=rtt.gkey WHERE rtt.unit_gkey=" + str(
                    unit_gkey) + " ORDER BY rd.gkey DESC LIMIT 1"
                print(Today + "    QUERY EIR CHECK :=  " + CheckStrEIR)
                conn = getSparcsn4Connection()
                curCheckStrEIR = conn.cursor()
                # ASIF UPDATED AT 31-03-2019 START
                curCheckStrEIR.execute(CheckStrEIR)
                dlvSt = 2
                for rowCheckStrEIR in curCheckStrEIR:
                    doctype_gkey = rowCheckStrEIR["doctype_gkey"]
                    if doctype_gkey == 7:
                        dlvSt = 1
                    else:
                        dlvSt = 0
                curCheckStrEIR.close()
                conn.close()
                # ASIF UPDATED AT 31-03-2019 END
                if contType == "FCL":
                    if destination == "2591":
                        if assignmentCode == "OCD":
                            dlvSt = 1
                        else:
                            dlvSt = 0
                # if gate_id != "CPAR":
                #     dlvSt = 0
                # ASIF Replace Query START
                if assignementDt == "":
                    assignementDt = "0000-00-00"
                if destination == "":
                    destination = 0

                if int(dlvSt) != 2:
                    alarm(int(dlvSt))

                containerReplace(unit_gkey, contId, contType, assignmentType, assignementDt, destination, dlvSt,
                                 CnFName,
                                 CAM_ID,track_by)

                # ASIF Replace Query END

            def getContStatusWithDigit(ContNumber, frame2):
                Contlength = len(str(ContNumber))
                Today = dt.now().strftime('%Y-%m-%d %H:%M:%S')
                if Contlength > 5:
                    suffix = ContNumber[0:6]
                    strchk = "SELECT cont_no AS id FROM ctmsmis.mis_ocr_temp_info WHERE SUBSTRING(cont_no,5,6) ='" + suffix + "' AND (DATE(assignment_dt) = DATE(NOW()) OR DATE(assignment_dt) = DATE_ADD(DATE(NOW()),INTERVAL -1 DAY) OR DATE(pickup_taken)=DATE(NOW()) OR DATE(pickup_taken) = DATE_ADD(DATE(NOW()),INTERVAL -1 DAY))"
                else:
                    strchk = "SELECT cont_no AS id FROM ctmsmis.mis_ocr_temp_info WHERE cont_no LIKE '%" + ContNumber + "%'  AND (DATE(assignment_dt) = DATE(NOW()) OR DATE(assignment_dt) = DATE_ADD(DATE(NOW()),INTERVAL -1 DAY) OR DATE(pickup_taken)=DATE(NOW()) OR DATE(pickup_taken) = DATE_ADD(DATE(NOW()),INTERVAL -1 DAY)) LIMIT 1"

                print(Today + "    QUERY CONT CHECK WITH DIGIT := " + strchk)
                fCont = ""
                if ContNumber != "":
                    conn = getCtmsmisConnection()
                    curChkInDb = conn.cursor()
                    curChkInDb.execute(strchk)
                    for rowChkInDb in curChkInDb:
                        fCont = rowChkInDb["id"]
                    curChkInDb.close()
                    conn.close()
                    if (fCont != ""):
                        getContainerProcess(fCont, frame2, "NUMBER")

            def onlyDigitContainerSearch(containrNumer, frame2):
                Today = dt.now().strftime('%Y-%m-%d %H:%M:%S')
                stringValue = containrNumer
                if len(stringValue) >= 6:
                    matches = re.findall("(\d+)", stringValue)
                    for e in matches:
                        thisPart = len(e)
                        if thisPart >= 6:
                            try:
                                getContStatusWithDigit(e, frame2)
                            except BaseException as e:
                                if hasattr(e, 'message'):
                                    print(Today + "    EXCEPTION INSIDE ELSE onlyDigitContainerSearch() : {}".format(
                                        e.message))
                                else:
                                    print(Today + "    EXCEPTION INSIDE ELSE onlyDigitContainerSearch() : {}".format(e))

                if stringValue != "":
                    print(Today + "    CONT= " + stringValue)

            def isContainerExist(ContNumber):
                contFindQuery = "SELECT cont_no AS id FROM ctmsmis.mis_ocr_temp_info WHERE cont_no='" + ContNumber + "'"
                print(contFindQuery)
                finalCont = ""
                conn = getCtmsmisConnection()
                cursor = conn.cursor()
                rows_count = cursor.execute(contFindQuery)

                if rows_count > 0:
                    cursor.close()
                    return int(1)
                else:
                    cursor.close()
                    return int(0)

            def isContainerExist_10_digit(ContNumber10_digt):

                ContNumber = ContNumber10_digt[0:10]
                contFindQuery = "SELECT cont_no AS id FROM ctmsmis.mis_ocr_temp_info WHERE cont_no LIKE '"+ContNumber+"%' LIMIT 1 "
                print(contFindQuery)
                finalCont = ""
                conn = getCtmsmisConnection()
                cursor = conn.cursor()
                cursor.execute(contFindQuery)

                for finalCont in cursor:
                    finalCont = finalCont["id"]
                cursor.close()
                return str(finalCont)

            def getDataProcessing(stringValue, frame2):
                Today = dt.now().strftime('%Y-%m-%d %H:%M:%S')
                if "U" in stringValue:
                    if len(stringValue) >= 10:
                        u = 0
                        for c in stringValue:
                            if ("U" in c):
                                try:
                                    index = u
                                    p1 = stringValue[index - 1]
                                    n1 = stringValue[index + 1]
                                    if p1.isalpha() and n1.isdigit():
                                        uIndex = index
                                        finalCont = stringValue[uIndex - 3: uIndex + 7]
                                        stringPart = stringValue[uIndex - 3: uIndex + 1]
                                        numberPart = stringValue[uIndex + 1: uIndex + 7]
                                        firstStringPart = str(stringPart).isalpha()
                                        lastNumberPArt = numberPart.isdigit()
                                        print(Today + "    FOUND STRING:  " + stringValue)
                                        firstSize = len(str(stringPart))
                                        numbSize = len(str(numberPart))
                                        if (firstStringPart and lastNumberPArt and int(firstSize) >= 4 and int(
                                                numbSize) >= 6):
                                            # ContainerFinal = getContainerLastDegit(finalCont)


                                            if (finalCont != ""):
                                                ContainerFinal = isContainerExist_10_digit(finalCont)
                                                print(Today + "    FULL CONT= " + ContainerFinal)
                                                if ContainerFinal != "":
                                                    getContainerProcess(ContainerFinal, frame2, "FULL")
                                                else:
                                                    getContStatusWithDigit(numberPart, frame2)
                                        else:
                                            onlyDigitContainerSearch(stringValue, frame2)
                                    else:
                                        onlyDigitContainerSearch(stringValue, frame2)

                                except BaseException as e:
                                    if hasattr(e, 'message'):
                                        print(Today + "    EXCEPTION INSIDE IF getDataProcessing() : {}".format(
                                            e.message))
                                        logWrite(e.message)
                                    else:
                                        logWrite(e)
                                        print(Today + "    EXCEPTION INSIDE ELSE getDataProcessing() :  {}".format(e))
                            u = u + 1
                        print(Today + "    CONT= " + stringValue)
                    else:
                        print(Today + "    CONT= " + stringValue)
                        onlyDigitContainerSearch(stringValue, frame2)
                else:
                    print(Today + "    CONT= " + stringValue)
                    onlyDigitContainerSearch(stringValue, frame2)

            def cpa_ocr_main(CAMARA_IP, DEFAULT_IMAGE_PATH, IMAGE_FOUND_PATH, IMAGE_FOUND_PATH_EXTENSION,
                             IMAGE_NOT_FOUND_PATH, TEXT_FILE_PATH, TITLE_NAME, CAM_ID):
                # --- Debugging Start ---
                # logWrite(f"[{CAM_ID}] Attempting to open camera: {CAMARA_IP}")
                # print(f"[{CAM_ID}] Attempting to open camera: {CAMARA_IP}")
                # --- Debugging End ---

                vs = VideoStream(src=CAMARA_IP).start()  # Uses imutils.video.VideoStream
                time.sleep(5.0)  # Give it a moment to connect

                # --- Debugging Start ---
                is_opened_status = vs.stream.isOpened()  # Access isOpened() from the underlying cv2.VideoCapture object
                # logWrite(f"[{CAM_ID}] Camera opened status after 5s: {is_opened_status}")
                # print(f"[{CAM_ID}] Camera opened status after 5s: {is_opened_status}")
                if not is_opened_status:
                    # logWrite(f"[{CAM_ID}] CRITICAL: Camera stream did not open. Exiting cpa_ocr_main for {CAM_ID}.")
                    # print(f"[{CAM_ID}] CRITICAL: Camera stream did not open. Exiting cpa_ocr_main for {CAM_ID}.")
                    vs.stop()  # Ensure the VideoStream is properly stopped
                    return  # Exit the function if camera didn't open
                # --- Debugging End ---

                firstFrame = None
                frame_count = 0
                capture_index = 0

                # loop over the frames of the video
                # while True:
                #     frame_count += 1
                #     # grab the current frame and initialize the occupied/unoccupied text
                #     frame = vs.read()
                #
                #     # --- Debugging Start ---
                #     if frame is None:  # vs.read() returns None if no frame is grabbed
                #         logWrite(
                #             f"[{CAM_ID}] Frame {frame_count}: No frame grabbed. Stream might have ended or failed. Breaking loop.")
                #         print(
                #             f"[{CAM_ID}] Frame {frame_count}: No frame grabbed. Stream might have ended or failed. Breaking loop.")
                #         break  # Exit the loop if no frame is grabbed
                #     # --- Debugging End ---
                #
                #     text = "Unoccupied"
                #
                #     # resize the frame, convert it to grayscale, and blur it
                #     # frame = imutils.resize(frame, width=500) # This line was commented out in your original code
                #     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                #     # gray = cv2.GaussianBlur(gray, (21, 21), 0) # This line was commented out in your original code
                #
                #     # if the first frame is None, initialize it
                #     if firstFrame is None:
                #         firstFrame = gray
                #         # --- Debugging Start ---
                #         # logWrite(f"[{CAM_ID}] Frame {frame_count}: Initializing firstFrame for motion detection.")
                #         # print(f"[{CAM_ID}] Frame {frame_count}: Initializing firstFrame for motion detection.")
                #         # --- Debugging End ---
                #         continue  # Skip processing this first frame, wait for next for diff
                #
                #     # compute the absolute difference between the current frame and first frame
                #     frameDelta = cv2.absdiff(firstFrame, gray)
                #     thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
                #
                #     # dilate the thresholded image to fill in holes, then find contours
                #     thresh = cv2.dilate(thresh, None, iterations=2)
                #     cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                #     cnts = imutils.grab_contours(cnts)  # Use imutils for cross-version compatibility
                #
                #     i = 0  # Flag to process only the first detected large object per frame
                #
                #     # --- Debugging Start ---
                #     if frame_count % 30 == 0:  # Print contour info every 30 frames to avoid log spam
                #         logWrite(f"[{CAM_ID}] Frame {frame_count}: Contours found: {len(cnts)}")
                #         print(f"[{CAM_ID}] Frame {frame_count}: Contours found: {len(cnts)}")
                #     # --- Debugging End ---
                #
                #     # loop over the contours
                #     for c in cnts:
                #         # if the contour is too small, ignore it
                #         cntArea = cv2.contourArea(c)
                #         if cntArea < 500:  # Your existing area threshold
                #             continue
                #
                #         # compute the bounding box for the contour, draw it on the frame
                #         (x, y, w, h) = cv2.boundingRect(c)
                #
                #         if (w > 100 and h > 100 and i == 0):  # Your existing width/height and i==0 filter
                #             cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                #             text = "Occupied"
                #             frame2 = frame[y:y + h, x:x + w]
                #
                #             # To save multiple images, append capture_index to filename
                #             capture_index += 1
                #             # Construct path for default image
                #             base_name_default = DEFAULT_IMAGE_PATH.rsplit('.', 1)[0]
                #             extension_default = DEFAULT_IMAGE_PATH.rsplit('.', 1)[1]
                #             current_default_image_path = f"{base_name_default}_{capture_index}.{extension_default}"
                #
                #             # Construct path for not found image (using its base path from Main.py)
                #             base_name_notfound = IMAGE_NOT_FOUND_PATH.rstrip('/')  # Remove trailing slash if any
                #             current_not_found_image_path = f"{base_name_notfound}/ocr_result_{capture_index}{IMAGE_FOUND_PATH_EXTENSION}"
                #
                #             # --- Debugging Start ---
                #             # logWrite(
                #             #     f"[{CAM_ID}] Frame {frame_count}: Saving detected object image to {current_default_image_path}")
                #             # print(
                #             #     f"[{CAM_ID}] Frame {frame_count}: Saving detected object image to {current_default_image_path}")
                #             # --- Debugging End ---
                #             cv2.imwrite(current_default_image_path, frame2)
                #
                #             # --- Debugging Start ---
                #             # logWrite(f"[{CAM_ID}] Frame {frame_count}: Performing OCR on {current_default_image_path}")
                #             # print(f"[{CAM_ID}] Frame {frame_count}: Performing OCR on {current_default_image_path}")
                #             # --- Debugging End ---
                #             stringValue = get_string(current_default_image_path)
                #
                #             # Ensure stringValue is bytes before decoding based on your get_string function's return type
                #             if isinstance(stringValue, bytes):
                #                 stringValue = stringValue.decode('utf-8', 'ignore')
                #             stringValue = re.sub(r'[^a-zA-Z0-9]', '', stringValue).upper()
                #
                #             # --- Debugging Start ---
                #             logWrite(f"=============================[{CAM_ID}] Frame {frame_count}: OCR Result: '{stringValue}'=============================")
                #             print(f"=============================[{CAM_ID}] Frame {frame_count}: OCR Result: '{stringValue}'=============================")
                #             # --- Debugging End ---
                #
                #             if stringValue != "":
                #                 # For DB Communication
                #                 getDataProcessing(stringValue, frame2)
                #
                #                 # --- Debugging Start ---
                #                 logWrite(
                #                     f"=============================[{CAM_ID}] Frame {frame_count}: Saving image with OCR result to {current_not_found_image_path}=============================")
                #                 print(
                #                     f"=============================[{CAM_ID}] Frame {frame_count}: Saving image with OCR result to {current_not_found_image_path}=============================")
                #                 # --- Debugging End ---
                #                 cv2.imwrite(current_default_image_path, frame2)
                #
                #             # i = 1  # Set i to 1 to ensure only one object is processed per frame based on your original logic
                #             # If you want to process ALL detected objects in a frame, remove this line.
                #
                #     key = cv2.waitKey(1) & 0xFF
                #
                #     # if the `q` key is pressed, break from the loop
                #     if key == ord("q"):
                #         logWrite(f"[{CAM_ID}] 'q' pressed. Exiting loop.")
                #         print(f"[{CAM_ID}] 'q' pressed. Exiting loop.")
                #         break

                # loop over the frames of the video
                while True:
                    frame_count += 1
                    frame = vs.read()

                    if frame is None:
                        # logWrite(
                        #     f"[{CAM_ID}] Frame {frame_count}: No frame grabbed. Stream might have ended or failed. Breaking loop.")
                        # print(
                        #     f"[{CAM_ID}] Frame {frame_count}: No frame grabbed. Stream might have ended or failed. Breaking loop.")
                        break

                    text = "Unoccupied"
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                    if firstFrame is None:
                        firstFrame = gray
                        continue

                    frameDelta = cv2.absdiff(firstFrame, gray)
                    thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
                    thresh = cv2.dilate(thresh, None, iterations=2)
                    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    cnts = imutils.grab_contours(cnts)

                    # Removed 'i = 0' here. You had 'i=0' inside the loop, which means only the first detected contour was processed.
                    # If you truly want *every* large object in a frame to be saved, remove the 'i=1' line later.
                    # If you want only *one* per frame, keep 'i=0' here and 'i=1' inside the contour loop.
                    # Assuming you want to save every image captured where motion is detected, we'll keep `capture_index` incrementing.

                    for c in cnts:
                        cntArea = cv2.contourArea(c)
                        if cntArea < 500:
                            continue

                        (x, y, w, h) = cv2.boundingRect(c)

                        # Process if the detected object meets size criteria
                        # Removed 'and i == 0' from here. If you want to save all detected containers, this condition needs to be adjusted
                        # If you want to save ONLY the first valid contour per frame, then uncomment 'i=0' above and keep 'and i==0'
                        if (w > 100 and h > 100):
                            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                            text = "Occupied"
                            frame2 = frame[y:y + h, x:x + w]

                            # Generate a unique filename using timestamp and incrementing index
                            # Ensure a clean base name without extension for _default_ image
                            base_name_default_no_ext = DEFAULT_IMAGE_PATH.rsplit('.', 1)[0]
                            extension_default = DEFAULT_IMAGE_PATH.rsplit('.', 1)[1]

                            # Get current timestamp for better uniqueness
                            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")[
                                        :-3]  # microseconds to milliseconds
                            unique_filename_prefix = f"{timestamp}_{capture_index}"

                            # Path for the initial detected image (before OCR result is known)
                            current_default_image_path = f"{base_name_default_no_ext}_{unique_filename_prefix}.{extension_default}"
                            cv2.imwrite(current_default_image_path, frame2)

                            # logWrite(
                            #     f"[{CAM_ID}] Frame {frame_count}: Saving detected object image to {current_default_image_path}")
                            # print(
                            #     f"[{CAM_ID}] Frame {frame_count}: Saving detected object image to {current_default_image_path}")

                            stringValue = get_string(current_default_image_path)
                            print(f"string value {stringValue}")
                            if isinstance(stringValue, bytes):
                                stringValue = stringValue.decode('utf-8', 'ignore')
                            stringValue = re.sub(r'[^a-zA-Z0-9]', '', stringValue).upper()

                            # logWrite(
                            #     f"=============================[{CAM_ID}] Frame {frame_count}: OCR Result: '{stringValue}'=============================")
                            # print(
                            #     f"=============================[{CAM_ID}] Frame {frame_count}: OCR Result: '{stringValue}'=============================")

                            if stringValue != "":
                                getDataProcessing(stringValue, frame2)

                                # Now, save the image again but with a name indicating OCR was successful.
                                # This path should reflect the IMAGE_FOUND_PATH structure.
                                # Ensure IMAGE_FOUND_PATH doesn't have a file extension in its variable name,
                                # as you're appending IMAGE_FOUND_PATH_EXTENSION.
                                # Assuming IMAGE_FOUND_PATH is a directory and IMAGE_FOUND_PATH_EXTENSION is like '.jpg'
                                found_image_name = f"ocr_found_{stringValue}_{unique_filename_prefix}{IMAGE_FOUND_PATH_EXTENSION}"
                                current_found_image_path = f"{IMAGE_FOUND_PATH.rstrip('/')}/{found_image_name}"  # Ensure no double slashes

                                logWrite(
                                    # f"=============================[{CAM_ID}] Frame {frame_count}: Saving FOUND image with OCR result to {current_found_image_path}============================= result {stringValue}"
                                    f"ocr result {stringValue}")

                                print(
                                    # f"=============================[{CAM_ID}] Frame {frame_count}: Saving FOUND image with OCR result to {current_found_image_path}============================= result {stringValue}"
                                    f"ocr result {stringValue}"
                                )
                                cv2.imwrite(current_found_image_path, frame2)  # Save to the "found" directory

                            else:  # stringValue is empty, meaning OCR didn't find anything usable
                                # Save to the "not found" directory
                                not_found_image_name = f"ocr_not_found_{unique_filename_prefix}{IMAGE_FOUND_PATH_EXTENSION}"  # Re-using IMAGE_FOUND_PATH_EXTENSION for consistency
                                current_not_found_image_path = f"{IMAGE_NOT_FOUND_PATH.rstrip('/')}/{not_found_image_name}"

                                # logWrite(
                                #     f"=============================[{CAM_ID}] Frame {frame_count}: Saving NOT FOUND image to {current_not_found_image_path}=============================")
                                # print(
                                #     f"=============================[{CAM_ID}] Frame {frame_count}: Saving NOT FOUND image to {current_not_found_image_path}=============================")
                                cv2.imwrite(current_not_found_image_path, frame2)

                            capture_index += 1  # Increment only after processing a successful capture
                            # i = 1 # Keep this if you only want to process the first large contour per frame.
                            # Remove if you want to process all large contours in a single frame

                # cleanup the camera and close any open windows
                vs.stop()  # This stops the imutils.video.VideoStream
                cv2.destroyAllWindows()
                # logWrite(f"[{CAM_ID}] Camera released and windows closed.")
                # print(f"[{CAM_ID}] Camera released and windows closed.")
            cpa_ocr_main(CAMARA_IP, DEFAULT_IMAGE_PATH, IMAGE_FOUND_PATH, IMAGE_FOUND_PATH_EXTENSION, IMAGE_NOT_FOUND_PATH, TEXT_FILE_PATH, TITLE_NAME, CAM_ID)

        except BaseException as e:
            if hasattr(e, 'message'):
                Today = dt.now().strftime('%Y-%m-%d %H:%M:%S')
                print(Today + "    EXCEPTION HOME IF : {}".format(e.message))
            else:
                Today = dt.now().strftime('%Y-%m-%d %H:%M:%S')
                print(Today + " EXCEPTION HOME ELSE : {}".format(e.message))