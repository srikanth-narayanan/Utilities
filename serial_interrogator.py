#!/usr/bin/env python
'''
This is a small snippet to poll dat from  optical interrogator system and
extract wavelength measurement. This will also update the database with the
wavelength information to specific mysql table.

This will connect to the device using Serial protocol.

The function will transfer the data in to the MYSQL Database
Database Server : mysqld@XX.XX.XX.XX
Database port : 3306
Database schema : YY_YY
Database Table : NEW_TABLE

:date: Nov 26, 2012
'''

__author__ = "Srikanth Narayanan"
__version__ = "0.3.1"
__email__ = "srikanth.n.narayanan@gmail.com"

import MySQLdb
from multiprocessing import process, Queue
import binascii
import serial
from datetime import datetime
import sys


class interogateSensor(object):
    '''
    This class contains method to interogate with optical interogator using a
    serial protocol and extract data with the given baud rate.
    '''
    def __init__(self, port, flush_key, poll_key, baud_rt=9600, tout=0.01):
        '''
        Constructor to initiate a serial port connection when initialised

        :param port: A string description of the port.
        :param flush_key: A hex string to flush the serial port i/o.
        :param poll_key: A hex string to poll data from device.
        :param baud_rt: Optional argument to serial port baud rate.
        :param tout: Optional argument to the serial port timeout in seconds.
        '''
        self.port = port
        self.flush_key = flush_key
        self.poll_key = poll_key
        self.baud_rate = baud_rt
        self.time_out = tout
        try:
            # Initiate a Serial connection to the Interrogator
            self.serCon = serial.Serial(self.port,
                                        self.baud_rate,
                                        timeout=self.time_out)
            print "connected to: " + self.ser.portstr
            # stop any existing flow of data
            self.serCon.write(self.flush_key)
            # flushes any serial i/o serial buffer
            self.serCon.flushInput()
            self.serCon.flushOutput()
        except Exception, err:
            print str(err)

    # Define the Function
    def serialread(self, serial_que):
        '''
        Method to send the appropriate serial word to retrieve the wavelength
        data

        :param serial_que: a python queue object to which the data is pushed.
        '''
        while self.serCon.isOpen():
            # send the PollSensorsRequest
            self.serCon.write(self.poll_key)
            # read serial data in to list - Total Length 36 byte
            line = self.serCon.read(20)
            # generate timestamp
            time_stamp = datetime.now().strftime("%d:%m:%Y:%H:%M:%S:%f")
            # convert ASCII to Hex
            hexline = binascii.hexlify(line)
            # add timestamp to the list
            sensor_list = self._calc_strain(hexline)
            sensor_list.insert(0, time_stamp)
            serial_que.put(tuple(sensor_list))

    def _calc_strain(self, hexdata):
        '''
        Helper method to calculate strain data from the hexdata.

        :param hexdata: The hexadecimal data from the serial interogator
        '''
        # calcuate Strain values
        sensor1 = 1544 + (float(((int((hexdata[22:24]), 16))*256) +
                                 (int((hexdata[20:22]), 16)))/1000)
        sensor2 = 1544 + (float(((int((hexdata[26:28]), 16))*256) +
                                 (int((hexdata[24:26]), 16)))/1000)
        sensor3 = 1544 + (float(((int((hexdata[30:32]), 16))*256) +
                                 (int((hexdata[28:30]), 16)))/1000)
        sensor4 = 1544 + (float(((int((hexdata[34:36]), 16))*256) +
                                 (int((hexdata[32:34]), 16)))/1000)
        return [sensor1, sensor2, sensor3, sensor4]


def main(sql_host, sqlport, uname, token, sensorDb, sqltable, ser_port,
         srl_flush_key, srl_poll_key, brate, time_out):
    '''
    Main method to make a sql connection, serial connection and lauch
    multiprocessing worker to poll sensor data and push to database.

    :param sql_host: host ip address of the mysql server
    :param sqlport: port number of the mysql database in integer
    :param uname: user name to access mysql database
    :param token: user password to access mysql database
    :param sensorDb: name of the database in the mysql server
    :param sqltable: name of the sql table in the database
    :param ser_port: serial port to which the device is connected
    :param srl_flush_key: hexkey to flush the serial port i/o
    :param srl_poll_key: hexkey to poll data from the serial port
    :param brate: baud rate of the serial comminication depending on protocol
    :param time_out: serial connection time out in seconds
    '''
    # make SQl connections
    dbCon = MySQLdb.connect(host=sql_host,
                            port=sqlport, user=uname,
                            passwd=token, db=sensorDb)
    # create serial object
    serialObj = interogateSensor(ser_port, srl_flush_key, srl_poll_key,
                                 baud_rt=brate, tout=time_out)
    if serialObj.serCon.isOpen():
        # Create a que to pass data
        daqQue = Queue()
        daqProcess = process.Process(target=serialObj.serialread,
                                     args=(daqQue,))
        daqProcess.daemon = True
        daqProcess.start()
        try:
            while True:
                queData = daqQue.get()
                dbCon.autocommit(True)
                # Create a Cursor object
                cursor = dbCon.cursor()
                try:
                    # Execute the SQL command
                    SQL_STRG = "INSERT INTO "+sqltable+"(timestamp,strain1,\
strain2,strain3,strain4) values(%f, %f, %f, %f, %f)" % (queData)
                    cursor.execute(SQL_STRG)
                    sys.stdout.flush()
                except Exception, err:
                    print str(err)
                    # Rollback in case there is any error
                    dbCon.rollback()
                    # close connection
                    dbCon.close()
                    break
        except KeyboardInterrupt:
            print "\nUser termination initiated"
            daqProcess.join()
            if serialObj.serCon.isOpen():
                serialObj.serCon.close()
                print "\nSerial Connection Closed"
            dbCon.close()
            print "\nDatabase Connection Closed"
    else:
        print "\nSerial Port Connection unsucessfull. Please check connections"

if __name__ == '__main__':
    # user defined SQL and SERIAL port settings
    my_sql_host = "10.10.10.10"
    my_sql_port = 3306
    my_sql_uname = "monkey"
    my_sql_token = "try, me!"
    my_sql_db = "sensordb"
    my_sql_table = "Sensor_Test"
    my_ser_port = "COM5"
    my_ser_brate = 38400
    my_ser_flush_key = "\xA5\xFD\x02\x52\x00\x3C\xD0"
    my_ser_poll_key = "\xA5\xFD\x02\x5C\x01\xF9\x70"
    my_ser_tout = 0.001  # seconds
    # Call main method to start the data acuquistion process.
    main(my_sql_host, my_sql_port, my_sql_uname, my_sql_token, my_sql_db,
         my_sql_table, my_ser_port, my_ser_flush_key, my_ser_poll_key,
         my_ser_brate, my_ser_tout)
