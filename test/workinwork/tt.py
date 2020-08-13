#!/usr/bin/python
# -*- coding: UTF-8 -*-
import datetime
from pprint import pprint

from bs4 import BeautifulSoup

from utils.fiddler import RawToPython

PLANNED_START_CITY_NAME = 'COOLANGATTA'
UNPLANNED_START_CITY_NAME = 'RICHMOND'
START_ID = 39


def write_file(sql):
    with open('./sql.sql', 'ab') as fw:
        fw.write(sql)


def get_all_citys():
    rtp = RawToPython('./tt.head')
    web = rtp.requests(timeout=10)
    soups = BeautifulSoup(web.text, "lxml")
    all_options = soups.find_all('option')
    all_citys = []
    for option in all_options:
        if hasattr(option, 'text') and option.text:
            all_citys.append(option.text)
    return all_citys


def get_plan_info(city_name):
    print "-- > requesting city name:", city_name
    rtp = RawToPython('./tt.head')
    rtp.set_param(req_param={'form1:suburbDropDown': city_name})
    web = rtp.requests(timeout=10)
    # print web.text
    soups = BeautifulSoup(web.text, "lxml")
    last_update_on = soups.find_all(id="form1:tabSet1:tab1:lastUpdatedTime")
    if last_update_on:
        last_update_on = last_update_on[0].text
        last_update_on_str = 'last_update_on: ' + last_update_on
        print '-- >', last_update_on_str
    else:
        last_update_on = ''
    datails_str = soups.find_all(
        id="form1:tabSet1:tab1:plannedOutagesTable:tableRowGroupPlanned:_emptyDataColumn")
    if datails_str:
        datails_str = datails_str[0]
        print '-- > detail:', datails_str.text
    else:
        datails_soup = soups.find_all(id="form1:tabSet1:tab1:plannedOutagesTable")
        if datails_soup:
            datails_soup = datails_soup[0]
            excel_titles = datails_soup.find_all(
                id='form1:tabSet1:tab1:plannedOutagesTable:tableRowGroupPlanned:_columnHeaderBar:0')[0]
            excel_titles = [x.strip() for x in excel_titles.text.split('\n') if x.strip()]
            line_templ = "form1:tabSet1:tab1:plannedOutagesTable:tableRowGroupPlanned:{}"
            all_details = []
            for i in range(99999):
                line_id = line_templ.format(i)
                line_data = datails_soup.find_all(id=line_id)
                if not line_data:
                    break
                line_data = line_data[0]
                line_data = [x for x in line_data.text.split('\n') if x.strip()]
                all_details.append(dict(zip(excel_titles, line_data)))
            if all_details:
                sql1 = get_insert_sql1(
                    post_code='', city=city_name,
                    interruptions=last_update_on_str,
                    type='planned')
                print sql1
                write_file(sql1)
                for each in all_details:
                    sql2 = get_insert_sql2(
                        post_code=each['Postcode'],
                        city=each['Suburb'],
                        street=each['Street'],
                        start_time=datetime.datetime.strptime(
                            each['Planned Start'], '%d/%m/%Y %H:%M'),
                        finish_time=datetime.datetime.strptime(
                            each['Planned Finish'], '%d/%m/%Y %H:%M'),
                        cause='', status='', estimated_restoration_time='',
                        number_of_customers_affected='',
                    )
                    print sql2
                    write_file(sql2)
                print '--', '-' * 50
            print '-- > detail:', all_details


def get_unplan_info(city_name):
    print "-- > requesting city name:", city_name
    rtp = RawToPython('./tt2.head')
    rtp.set_param(req_param={'form1:suburbDropDown': city_name})
    web = rtp.requests(timeout=100)
    # print web.text
    soups = BeautifulSoup(web.text, "lxml")
    total_customers_affected = soups.find_all(id="form1:tabSet1:tab2:totalCustomersAffected")
    if total_customers_affected:
        total_customers_affected = total_customers_affected[0].text
        total_customers_affected_str = 'total_customers_affected: ' + total_customers_affected
        print '-- >', total_customers_affected_str
    empty_datails_str = soups.find_all(
        id="form1:tabSet1:tab2:unplannedOutagesTable:tableRowGroupUnPlanned:_emptyDataColumn:_emptyDataText")
    if empty_datails_str:
        datails_str = empty_datails_str[0]
        print '-- > detail:', datails_str.text
    else:
        datails_soup = soups.find_all(id="form1:tabSet1:tab2:unplannedOutagesTable")
        if datails_soup:
            datails_soup = datails_soup[0]
            excel_titles = datails_soup.find_all(
                id='form1:tabSet1:tab2:unplannedOutagesTable:tableRowGroupUnPlanned:_columnHeaderBar:0')[
                0]
            excel_titles = [x.strip() for x in excel_titles.text.split('\n') if
                            x.strip()]
            excel_titles = ["{} {}".format(excel_titles[0], excel_titles[1])] + excel_titles[2:]
            line_templ = "form1:tabSet1:tab2:unplannedOutagesTable:tableRowGroupUnPlanned:{}"
            all_details = []
            for i in range(99999):
                line_id = line_templ.format(i)
                line_data = datails_soup.find_all(id=line_id)
                if not line_data:
                    break
                line_data = line_data[0]
                line_data = [x for x in line_data.text.split('\n') if x.strip()]
                all_details.append(dict(zip(excel_titles, line_data)))
            if all_details:
                sql1 = get_insert_sql1(
                    post_code='', city=city_name,
                    interruptions=total_customers_affected_str,
                    type='unplanned')
                print sql1
                write_file(sql1)
                for each in all_details:
                    sql2 = get_insert_sql2(
                        post_code=each['Post Code'],
                        city=each['Suburb'],
                        street=each['Street'],
                        start_time='',
                        finish_time='',
                        cause=each['Cause'], status=each['Status'],
                        estimated_restoration_time=each['Estimated Restoration Time'],
                        number_of_customers_affected=each['Number of Customers Affected'],
                    )
                    print sql2
                    write_file(sql2)
                print '--', '-' * 50
            print '-- > detail:', all_details


def get_insert_sql1(**kwargs):
    global START_ID
    sql = """
INSERT INTO `outage_infos` (`id`, `post_code`, `suburb`, `type`, `interruptions`)
VALUES
    ({id}, '{post_code}', '{city}', '{type}', '{interruptions}');
    """.format(id=START_ID, **kwargs)
    START_ID += 1
    return sql

def get_insert_sql2(**kwargs):
    sql2 = """
INSERT INTO `outage_info_details` (`post_code`, `suburb`, `street`, `cause`, `status`, `estimated_restoration_time`, `number_of_customers_affected`, `start_time`, `finish_time`, `outage_info_id`)
VALUES
	('{post_code}', '{city}', '{street}', '{cause}', '{status}', '{estimated_restoration_time}', '{number_of_customers_affected}', '{start_time}', '{finish_time}', {outage_info_id});
""".format(outage_info_id=START_ID-1, **kwargs)
    return sql2


if __name__ == '__main__':
    all_citys = get_all_citys()
    planned_citys = all_citys
    if PLANNED_START_CITY_NAME:
        planned_citys = all_citys[all_citys.index(PLANNED_START_CITY_NAME):]
    for planned_city_name in planned_citys:
        get_plan_info(planned_city_name)
    unplanned_citys = all_citys
    if UNPLANNED_START_CITY_NAME:
        unplanned_citys = all_citys[all_citys.index(UNPLANNED_START_CITY_NAME):]
    for unplanned_city_name in unplanned_citys:
        get_unplan_info(unplanned_city_name)
