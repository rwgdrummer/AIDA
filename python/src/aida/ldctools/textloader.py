# =============================================================================
# Authors: PAR Government
# Organization: DARPA
#
# Copyright (c) 2016 PAR Government
# All rights reserved.
#==============================================================================

from sqlalchemy.sql.sqltypes import DateTime, Integer, Float
from logging import ERROR, _levelToName, WARNING
import datetime

def processDateTime(value):
    if len(value) == 25:
        value = value[0:22] + value[23:]
    if len(value) == 10:
        return datetime.datetime.strptime(value, "%Y-%m-%d")
    return datetime.datetime.strptime(value,"%Y-%m-%dT%H:%M:%S%z")

def format_value(attribute_metadata, value):
    """
    String to Attribute
    :param attribute_metadata:
    :param value: string value
    :return:
    @type value: str
    """
    if (type(value) == str and len(value) == 0 or value == 'n/a') or value is None:
        return None
    if isinstance(attribute_metadata.expression.type, DateTime):
        return  processDateTime(value)
    elif isinstance(attribute_metadata.expression.type, Integer):
        return int(value)
    elif isinstance(attribute_metadata.expression.type, Float):
        return float(value)
    else:
        return value

def format_attribute(attribute_metadata, attribute):
    """
    Attribute to String
    :param attribute_metadata:
    :param attribute: instance attribute
    :return:
    """
    if attribute is None:
        return ''
    if isinstance(attribute_metadata.expression.type, DateTime):
        return attribute.strftime("%Y-%m-%dT%H:%M:%S%z")
    return str(attribute)

def format_value_by_name(model_class_instance, column_name, value):
    return format_value(model_class_instance.__dict__[column_name], value)

def map_column_values(column_values, column_names, model_class_instance):
    """
    column text to attribute
    :param column_values:  values from text file
    :param column_names: name to order in column list
    :param class_instance: destination model class
    :return:
    """
    values = {}
    for column_no in range(len(column_values)):
        column_value = column_values[column_no]
        column_name = column_names[column_no]
        if column_name not in model_class_instance.__dict__:
            continue
        try:
            values[column_name] = format_value(model_class_instance.__dict__[column_name],column_value)
        except Exception as e:
            log (ERROR,'%s: entity %s column %s value %s' %(str(e),model_class_instance.__name__,column_name,column_value))
            raise e
    return values

def map_attribute_values(column_names, model_instance):
    """
    attribute value to column
    :param column_values:  values from text file
    :param column_names: name to order in column list
    :param class_instance: destination model class
    :return:
    """
    values = []
    for column_no in range(len(column_names)):
        column_name = column_names[column_no]
        if column_name not in model_instance.__class__.__dict__:
            continue
        try:
            values.append(format_attribute(model_instance.__class__.__dict__[column_name],model_instance.__dict__[column_name]))
        except Exception as e:
            log (ERROR,'%s: entity %s column %s ' %(str(e),model_instance.__class__.__name__,column_name))
            raise e
    return values

def log(code, msg):
    print ("%s %s" % (_levelToName[code],msg))


class FileReader:

    def __init__(self, filename, sep='\t', skip_first_line=True):
        self.filename = filename
        self.sep = sep
        self.skip_first_line = skip_first_line

    def read(self, session, processor):
        first = True
        if self.filename is None:
            raise ValueError("user file not provided")
        with open(self.filename,'r', encoding='utf-8') as fp:
            lineno = 0
            while True:
                line = fp.readline()
                lineno+=1
                if first and self.skip_first_line:
                    first = False
                    continue
                if line is None or len(line) == 0:
                    break
                columns = line.split(self.sep)
                columns = [c.strip() for c in columns]
                try:
                    processor(session, columns)
                except Exception as e:
                    log (ERROR, 'Error on line %d: %s in filel %s' % (lineno,line,self.filename))
                    raise e

class FileWriter:

    def __init__(self, filename, sep='\t', skip_first_line=True):
        self.filename = filename
        self.sep = sep
        self.skip_first_line = skip_first_line

    def write(self, column_names, instances):
        if self.filename is None:
            raise ValueError("user file not provided")
        with open(self.filename,'w', encoding='utf-8') as fp:
            lines = []
            for instance in instances:
                lines.append(self.sep.join(map_attribute_values(column_names,instance)))
            fp.writelines(lines)
